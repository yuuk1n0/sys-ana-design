from app.core.crud import CRUDBase
from app.models.admin import Supplier
from app.schemas.suppliers import SupplierCreate, SupplierUpdate


class SupplierController(CRUDBase[Supplier, SupplierCreate, SupplierUpdate]):
    def __init__(self):
        super().__init__(model=Supplier)

    async def exists_supplier_code(self, store_id: int, supplier_code: str, exclude_id: int | None = None) -> bool:
        query = self.model.filter(store_id=store_id, supplier_code=supplier_code)
        if exclude_id:
            query = query.exclude(id=exclude_id)
        return await query.exists()


supplier_controller = SupplierController()
