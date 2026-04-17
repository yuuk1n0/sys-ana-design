from app.core.crud import CRUDBase
from app.models.admin import Member
from app.schemas.members import MemberCreate, MemberUpdate


class MemberController(CRUDBase[Member, MemberCreate, MemberUpdate]):
    def __init__(self):
        super().__init__(model=Member)

    async def exists_member_no(self, store_id: int, member_no: str, exclude_id: int | None = None) -> bool:
        query = self.model.filter(store_id=store_id, member_no=member_no)
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


member_controller = MemberController()
