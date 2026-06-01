import json
from datetime import datetime
from typing import Optional

from fastapi import HTTPException
from tortoise.expressions import Q
from tortoise.transactions import atomic

from app.core.crud import CRUDBase
from app.models.admin import InventoryTxn, Product, StoreInventory
from app.schemas.inventories import InventoryInitTxnCreate, InventoryOperateCreate


class InventoryController(CRUDBase[StoreInventory, dict, dict]):
    def __init__(self):
        super().__init__(model=StoreInventory)

    async def get_by_store_product(self, store_id: int, product_id: int) -> Optional[StoreInventory]:
        return await self.model.filter(store_id=store_id, product_id=product_id).first()

    async def create_or_update_inventory(
        self,
        store_id: int,
        product_id: int,
        low_stock_threshold: int,
        operator_id: Optional[int] = None,
    ) -> StoreInventory:
        inventory_obj = await self.get_by_store_product(store_id=store_id, product_id=product_id)
        if inventory_obj:
            inventory_obj.low_stock_threshold = low_stock_threshold
            inventory_obj.updated_by = operator_id
            await inventory_obj.save()
            return inventory_obj
        return await self.model.create(
            store_id=store_id,
            product_id=product_id,
            low_stock_threshold=low_stock_threshold,
            available_qty=0,
            locked_qty=0,
            version=1,
            updated_by=operator_id,
        )

    async def create_init_txn(self, store_id: int, obj_in: InventoryInitTxnCreate):
        await InventoryTxn.create(store_id=store_id, **obj_in.model_dump())

    def build_txn_remark(self, data: dict | None = None) -> str | None:
        if not data:
            return None
        return json.dumps(data, ensure_ascii=False, separators=(",", ":"))

    def parse_txn_remark(self, remark: str | None) -> dict:
        if not remark:
            return {}
        try:
            data = json.loads(remark)
            return data if isinstance(data, dict) else {"text": remark}
        except (TypeError, ValueError):
            return {"text": remark}

    def generate_biz_no(self, prefix: str) -> str:
        return f"{prefix}-{datetime.now().strftime('%Y%m%d%H%M%S%f')}"

    async def _get_inventory_or_raise(self, store_id: int, product_obj: Product, operator_id: int):
        inventory_obj = await self.get_by_store_product(store_id=store_id, product_id=product_obj.id)
        if inventory_obj:
            return inventory_obj
        return await self.create_or_update_inventory(
            store_id=store_id,
            product_id=product_obj.id,
            low_stock_threshold=product_obj.low_stock_threshold,
            operator_id=operator_id,
        )

    async def apply_inventory_change(
        self,
        *,
        store_id: int,
        operator_id: int,
        biz_type: str,
        biz_no: str,
        product_obj: Product,
        qty: int,
        remark_meta: dict | None = None,
    ):
        inventory_obj = await self._get_inventory_or_raise(store_id=store_id, product_obj=product_obj, operator_id=operator_id)
        before_qty = inventory_obj.available_qty
        after_qty = before_qty + qty
        if after_qty < 0:
            raise HTTPException(status_code=400, detail=f"商品 {product_obj.name} 库存不足")

        inventory_obj.available_qty = after_qty
        inventory_obj.updated_by = operator_id
        inventory_obj.version += 1
        await inventory_obj.save()

        product_obj.stock_status = after_qty > 0
        await product_obj.save()

        txn_obj = await InventoryTxn.create(
            store_id=store_id,
            product_id=product_obj.id,
            biz_type=biz_type,
            biz_no=biz_no,
            change_qty=qty,
            before_qty=before_qty,
            after_qty=after_qty,
            remark=self.build_txn_remark(remark_meta),
            operator_id=operator_id,
        )
        return txn_obj

    @atomic("mysql")
    async def create_inventory_operation(self, *, store_id: int, operator_id: int, obj_in: InventoryOperateCreate):
        biz_type = obj_in.biz_type.upper()
        if biz_type not in {"STOCK_IN", "STOCK_OUT"}:
            raise HTTPException(status_code=400, detail="仅支持入库或出库作业")

        biz_no = self.generate_biz_no("IN" if biz_type == "STOCK_IN" else "OUT")
        product_ids = [item.product_id for item in obj_in.items]
        product_objs = await Product.filter(store_id=store_id, id__in=product_ids).all()
        product_map = {item.id: item for item in product_objs}

        total_qty = 0
        for line in obj_in.items:
            product_obj = product_map.get(line.product_id)
            if not product_obj:
                raise HTTPException(status_code=404, detail=f"商品 {line.product_id} 不存在")

            delta_qty = line.qty if biz_type == "STOCK_IN" else -line.qty
            total_qty += line.qty
            await self.apply_inventory_change(
                store_id=store_id,
                operator_id=operator_id,
                biz_type=biz_type,
                biz_no=biz_no,
                product_obj=product_obj,
                qty=delta_qty,
                remark_meta={
                    "remark": obj_in.remark,
                    "qty": line.qty,
                },
            )

        return {"biz_no": biz_no, "biz_type": biz_type, "total_qty": total_qty, "item_count": len(obj_in.items)}

    async def get_balance_data(
        self,
        store_id: int,
        page: int,
        page_size: int,
        name: str = "",
        category_id: int | None = None,
        status: int | None = None,
        stock_status: int | None = None,
    ):
        product_q = Q(store_id=store_id)
        if name:
            product_q &= Q(name__contains=name)
        if category_id is not None:
            product_q &= Q(category_id=category_id)
        if status is not None:
            product_q &= Q(status=bool(status))
        if stock_status is not None:
            product_q &= Q(stock_status=bool(stock_status))
        total = await Product.filter(product_q).count()
        product_objs = (
            await Product.filter(product_q).offset((page - 1) * page_size).limit(page_size).order_by("-updated_at")
        )
        product_ids = [item.id for item in product_objs]
        inventory_objs = await self.model.filter(store_id=store_id, product_id__in=product_ids)
        inventory_map = {item.product_id: item for item in inventory_objs}
        rows = []
        for product in product_objs:
            item = await product.to_dict()
            inventory = inventory_map.get(product.id)
            available_qty = inventory.available_qty if inventory else 0
            threshold = inventory.low_stock_threshold if inventory else product.low_stock_threshold
            item["available_qty"] = available_qty
            item["low_stock_threshold"] = threshold
            item["is_low_stock"] = available_qty <= threshold
            rows.append(item)
        return total, rows

    async def get_warning_data(self, store_id: int, page: int, page_size: int):
        inventory_objs = await self.model.filter(store_id=store_id).order_by("available_qty", "product_id")
        warning_objs = [item for item in inventory_objs if item.available_qty <= item.low_stock_threshold]
        total = len(warning_objs)
        current_rows = warning_objs[(page - 1) * page_size : page * page_size]
        product_ids = [item.product_id for item in current_rows]
        product_objs = await Product.filter(store_id=store_id, id__in=product_ids)
        product_map = {item.id: item for item in product_objs}
        rows = []
        for inventory in current_rows:
            product = product_map.get(inventory.product_id)
            if not product:
                continue
            item = await product.to_dict()
            item["available_qty"] = inventory.available_qty
            item["low_stock_threshold"] = inventory.low_stock_threshold
            item["is_low_stock"] = True
            rows.append(item)
        return total, rows

    async def get_txn_data(
        self,
        store_id: int,
        page: int,
        page_size: int,
        product_id: int | None = None,
        biz_type: str | None = None,
        start_time=None,
        end_time=None,
    ):
        q = Q(store_id=store_id)
        if product_id is not None:
            q &= Q(product_id=product_id)
        if biz_type:
            q &= Q(biz_type=biz_type)
        if start_time and end_time:
            q &= Q(created_at__range=[start_time, end_time])
        elif start_time:
            q &= Q(created_at__gte=start_time)
        elif end_time:
            q &= Q(created_at__lte=end_time)
        total = await InventoryTxn.filter(q).count()
        txn_objs = (
            await InventoryTxn.filter(q).offset((page - 1) * page_size).limit(page_size).order_by("-created_at")
        )
        product_ids = list({item.product_id for item in txn_objs})
        product_objs = await Product.filter(store_id=store_id, id__in=product_ids)
        product_map = {item.id: item for item in product_objs}
        rows = []
        for item in txn_objs:
            row = await item.to_dict()
            product_obj = product_map.get(item.product_id)
            row["product_name"] = product_obj.name if product_obj else ""
            row["product_code"] = product_obj.product_code if product_obj else ""
            row["remark_meta"] = self.parse_txn_remark(item.remark)
            rows.append(row)
        return total, rows


inventory_controller = InventoryController()
