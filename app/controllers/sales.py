from decimal import Decimal

from fastapi import HTTPException
from tortoise.expressions import Q
from tortoise.transactions import atomic

from app.models.admin import InventoryTxn, Member, Product
from app.schemas.sales import SalesOrderCreate

from .inventory import inventory_controller


class SalesController:
    @atomic("mysql")
    async def submit_order(
        self,
        *,
        store_id: int,
        operator_id: int,
        biz_type: str,
        obj_in: SalesOrderCreate,
    ):
        biz_type = biz_type.upper()
        if biz_type not in {"SALE", "RETURN"}:
            raise HTTPException(status_code=400, detail="仅支持销售和退货单")

        member_meta = {}
        if obj_in.member_id is not None:
            member_obj = await Member.filter(id=obj_in.member_id, store_id=store_id).first()
            if not member_obj:
                raise HTTPException(status_code=404, detail="会员不存在")
            member_meta = {
                "member_id": member_obj.id,
                "member_no": member_obj.member_no,
                "member_name": member_obj.name,
            }

        biz_no = inventory_controller.generate_biz_no("SAL" if biz_type == "SALE" else "RET")
        product_ids = [item.product_id for item in obj_in.items]
        product_objs = await Product.filter(store_id=store_id, id__in=product_ids).all()
        product_map = {item.id: item for item in product_objs}

        total_qty = 0
        total_amount = Decimal("0")
        for line in obj_in.items:
            product_obj = product_map.get(line.product_id)
            if not product_obj:
                raise HTTPException(status_code=404, detail=f"商品 {line.product_id} 不存在")

            line_amount = Decimal(str(product_obj.sale_price)) * line.qty
            total_amount += line_amount
            total_qty += line.qty
            delta_qty = -line.qty if biz_type == "SALE" else line.qty
            await inventory_controller.apply_inventory_change(
                store_id=store_id,
                operator_id=operator_id,
                biz_type=biz_type,
                biz_no=biz_no,
                product_obj=product_obj,
                qty=delta_qty,
                remark_meta={
                    **member_meta,
                    "remark": obj_in.remark,
                    "qty": line.qty,
                    "unit_price": float(product_obj.sale_price),
                    "line_amount": float(line_amount),
                },
            )

        return {
            "biz_no": biz_no,
            "biz_type": biz_type,
            "member": member_meta,
            "total_qty": total_qty,
            "total_amount": float(total_amount),
            "item_count": len(obj_in.items),
        }

    async def list_orders(
        self,
        *,
        store_id: int,
        page: int,
        page_size: int,
        biz_type: str | None = None,
        biz_no: str | None = None,
        start_time=None,
        end_time=None,
    ):
        q = Q(store_id=store_id, biz_type__in=["SALE", "RETURN"])
        if biz_type:
            q &= Q(biz_type=biz_type.upper())
        if biz_no:
            q &= Q(biz_no__contains=biz_no)
        if start_time and end_time:
            q &= Q(created_at__range=[start_time, end_time])
        elif start_time:
            q &= Q(created_at__gte=start_time)
        elif end_time:
            q &= Q(created_at__lte=end_time)

        txn_rows = await InventoryTxn.filter(q).order_by("-created_at", "id").all()
        product_ids = list({item.product_id for item in txn_rows})
        product_rows = await Product.filter(store_id=store_id, id__in=product_ids).all() if product_ids else []
        product_map = {item.id: item for item in product_rows}

        grouped = {}
        ordered_biz_nos = []
        for txn in txn_rows:
            if txn.biz_no not in grouped:
                ordered_biz_nos.append(txn.biz_no)
                meta = inventory_controller.parse_txn_remark(txn.remark)
                grouped[txn.biz_no] = {
                    "biz_no": txn.biz_no,
                    "biz_type": txn.biz_type,
                    "created_at": txn.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "operator_id": txn.operator_id,
                    "member_id": meta.get("member_id"),
                    "member_no": meta.get("member_no", ""),
                    "member_name": meta.get("member_name", ""),
                    "remark": meta.get("remark", ""),
                    "item_count": 0,
                    "total_qty": 0,
                    "total_amount": 0.0,
                    "line_summary": [],
                }

            group = grouped[txn.biz_no]
            meta = inventory_controller.parse_txn_remark(txn.remark)
            product_obj = product_map.get(txn.product_id)
            product_name = product_obj.name if product_obj else ""
            product_code = product_obj.product_code if product_obj else ""
            unit_price = meta.get("unit_price")
            if unit_price is None:
                unit_price = float(product_obj.sale_price) if product_obj else 0.0
            abs_qty = abs(txn.change_qty)
            group["item_count"] += 1
            group["total_qty"] += abs_qty
            group["total_amount"] += float(unit_price) * abs_qty
            group["line_summary"].append(f"{product_name or product_code} x{abs_qty}")

        member_ids = {item.get("member_id") for item in grouped.values()}
        member_ids = {member_id for member_id in member_ids if isinstance(member_id, int)}
        member_map = {}
        if member_ids:
            member_rows = await Member.filter(store_id=store_id, id__in=list(member_ids)).all()
            member_map = {item.id: item for item in member_rows}

        rows = []
        for biz_no_item in ordered_biz_nos:
            item = grouped[biz_no_item]
            member_obj = member_map.get(item.get("member_id"))
            if member_obj:
                item["member_no"] = member_obj.member_no
                item["member_name"] = member_obj.name
            item["line_summary"] = "；".join(item["line_summary"][:3])
            rows.append(item)

        total = len(rows)
        paged = rows[(page - 1) * page_size : page * page_size]
        return total, paged

    async def get_order_detail(self, *, store_id: int, biz_no: str):
        txn_rows = await InventoryTxn.filter(
            store_id=store_id,
            biz_no=biz_no,
            biz_type__in=["SALE", "RETURN"],
        ).order_by("id")
        if not txn_rows:
            raise HTTPException(status_code=404, detail="单据不存在")

        product_ids = [item.product_id for item in txn_rows]
        product_rows = await Product.filter(store_id=store_id, id__in=product_ids).all()
        product_map = {item.id: item for item in product_rows}
        first_meta = inventory_controller.parse_txn_remark(txn_rows[0].remark)
        member_id = first_meta.get("member_id")
        member_obj = None
        if isinstance(member_id, int):
            member_obj = await Member.filter(id=member_id, store_id=store_id).first()

        lines = []
        total_amount = Decimal("0")
        total_qty = 0
        for txn in txn_rows:
            meta = inventory_controller.parse_txn_remark(txn.remark)
            product_obj = product_map.get(txn.product_id)
            unit_price = Decimal(str(meta.get("unit_price") or (product_obj.sale_price if product_obj else 0)))
            qty = abs(txn.change_qty)
            amount = unit_price * qty
            total_qty += qty
            total_amount += amount
            lines.append(
                {
                    "product_id": txn.product_id,
                    "product_name": product_obj.name if product_obj else "",
                    "product_code": product_obj.product_code if product_obj else "",
                    "qty": qty,
                    "unit_price": float(unit_price),
                    "amount": float(amount),
                }
            )

        return {
            "biz_no": biz_no,
            "biz_type": txn_rows[0].biz_type,
            "created_at": txn_rows[0].created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "operator_id": txn_rows[0].operator_id,
            "member_id": member_id,
            "member_no": member_obj.member_no if member_obj else first_meta.get("member_no", ""),
            "member_name": member_obj.name if member_obj else first_meta.get("member_name", ""),
            "remark": first_meta.get("remark", ""),
            "total_qty": total_qty,
            "total_amount": float(total_amount),
            "lines": lines,
        }


sales_controller = SalesController()
