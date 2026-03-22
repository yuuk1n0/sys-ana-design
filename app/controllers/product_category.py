from app.core.crud import CRUDBase
from app.models.admin import ProductCategory, Product
from app.schemas.product_categories import ProductCategoryCreate, ProductCategoryUpdate


class ProductCategoryController(CRUDBase[ProductCategory, ProductCategoryCreate, ProductCategoryUpdate]):
    def __init__(self):
        super().__init__(model=ProductCategory)

    async def exists_name(self, store_id: int, name: str, exclude_id: int | None = None) -> bool:
        query = self.model.filter(store_id=store_id, name=name)
        if exclude_id:
            query = query.exclude(id=exclude_id)
        return await query.exists()

    async def has_products(self, store_id: int, category_id: int) -> bool:
        return await Product.filter(store_id=store_id, category_id=category_id).exists()


product_category_controller = ProductCategoryController()
