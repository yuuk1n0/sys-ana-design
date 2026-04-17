from app.core.crud import CRUDBase
from app.models.admin import StoreEmployee
from app.schemas.store_employees import StoreEmployeeCreate, StoreEmployeeUpdate


class StoreEmployeeController(CRUDBase[StoreEmployee, StoreEmployeeCreate, StoreEmployeeUpdate]):
    def __init__(self):
        super().__init__(model=StoreEmployee)

    async def exists_employee_no(self, store_id: int, employee_no: str, exclude_id: int | None = None) -> bool:
        query = self.model.filter(store_id=store_id, employee_no=employee_no)
        if exclude_id:
            query = query.exclude(id=exclude_id)
        return await query.exists()

    async def exists_phone(self, store_id: int, phone: str | None, exclude_id: int | None = None) -> bool:
        if not phone:
            return False
        query = self.model.filter(store_id=store_id, phone=phone)
        if exclude_id:
            query = query.exclude(id=exclude_id)
        return await query.exists()


store_employee_controller = StoreEmployeeController()
