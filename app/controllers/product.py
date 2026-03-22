from fastapi import HTTPException
from tortoise.transactions import atomic

from app.core.crud import CRUDBase
from app.models.admin import Product
from app.schemas.inventories import InventoryInitTxnCreate
from app.schemas.products import ProductCreate, ProductStatusUpdate, ProductUpdate

from .inventory import inventory_controller


class ProductController(CRUDBase[Product, ProductCreate, ProductUpdate]):
    def __init__(self):
        super().__init__(model=Product)

    async def exists_product_code(self, store_id: int, product_code: str, exclude_id: int | None = None) -> bool:
        query = self.model.filter(store_id=store_id, product_code=product_code)
        if exclude_id:
            query = query.exclude(id=exclude_id)
        return await query.exists()

    async def exists_barcode(self, store_id: int, barcode: str | None, exclude_id: int | None = None) -> bool:
        if not barcode:
            return False
        query = self.model.filter(store_id=store_id, barcode=barcode)
        if exclude_id:
            query = query.exclude(id=exclude_id)
        return await query.exists()

    @atomic("mysql")
    async def create_product(self, store_id: int, operator_id: int, obj_in: ProductCreate):
        if await self.exists_product_code(store_id=store_id, product_code=obj_in.product_code):
            raise HTTPException(status_code=400, detail="商品编码已存在")
        if await self.exists_barcode(store_id=store_id, barcode=obj_in.barcode):
            raise HTTPException(status_code=400, detail="商品条码已存在")
        data = obj_in.model_dump()
        data["store_id"] = store_id
        product_obj = await self.create(obj_in=data)
        await inventory_controller.create_or_update_inventory(
            store_id=store_id,
            product_id=product_obj.id,
            low_stock_threshold=product_obj.low_stock_threshold,
            operator_id=operator_id,
        )
        await inventory_controller.create_init_txn(
            store_id=store_id,
            obj_in=InventoryInitTxnCreate(
                product_id=product_obj.id,
                biz_no=f"INIT-{product_obj.id}",
                operator_id=operator_id,
            ),
        )
        return product_obj

    @atomic("mysql")
    async def update_product(self, store_id: int, operator_id: int, obj_in: ProductUpdate):
        product_obj = await self.get(id=obj_in.id)
        if product_obj.store_id != store_id:
            raise HTTPException(status_code=403, detail="无权限访问该商品")
        if obj_in.product_code and await self.exists_product_code(
            store_id=store_id, product_code=obj_in.product_code, exclude_id=product_obj.id
        ):
            raise HTTPException(status_code=400, detail="商品编码已存在")
        if await self.exists_barcode(store_id=store_id, barcode=obj_in.barcode, exclude_id=product_obj.id):
            raise HTTPException(status_code=400, detail="商品条码已存在")
        updated_obj = await self.update(id=product_obj.id, obj_in=obj_in)
        await inventory_controller.create_or_update_inventory(
            store_id=store_id,
            product_id=updated_obj.id,
            low_stock_threshold=updated_obj.low_stock_threshold,
            operator_id=operator_id,
        )
        return updated_obj

    async def change_status(self, store_id: int, obj_in: ProductStatusUpdate):
        product_obj = await self.get(id=obj_in.id)
        if product_obj.store_id != store_id:
            raise HTTPException(status_code=403, detail="无权限访问该商品")
        product_obj.status = obj_in.status
        await product_obj.save()


product_controller = ProductController()
