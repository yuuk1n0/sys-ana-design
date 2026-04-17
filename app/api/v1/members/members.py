from fastapi import APIRouter, Query
from fastapi.exceptions import HTTPException
from tortoise.expressions import Q

from app.controllers.member import member_controller
from app.controllers.user import user_controller
from app.core.ctx import CTX_USER_ID
from app.models.admin import Dept
from app.schemas import Success, SuccessExtra
from app.schemas.members import MemberCreate, MemberUpdate

router = APIRouter()


async def get_current_store_id(store_id: int | None = None):
    user_id = CTX_USER_ID.get()
    current_user = await user_controller.get(id=user_id)
    if store_id is not None:
        exists = await Dept.filter(id=store_id, is_deleted=False).exists()
        if not exists:
            raise HTTPException(status_code=400, detail="门店不存在")
        return store_id
    if current_user.dept_id:
        return current_user.dept_id
    if current_user.is_superuser:
        default_store = await Dept.filter(is_deleted=False).order_by("id").first()
        if default_store:
            current_user.dept_id = default_store.id
            await current_user.save()
            return default_store.id
        raise HTTPException(status_code=400, detail="暂无可用门店，请先创建门店")
    raise HTTPException(status_code=400, detail="当前用户未绑定门店")


@router.get("/list", summary="查看会员列表")
async def list_member(
    page: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量"),
    name: str = Query("", description="会员姓名"),
    member_no: str = Query("", description="会员编号"),
    phone: str = Query("", description="手机号"),
    status: int | None = Query(None, description="状态"),
    store_id: int | None = Query(None, description="门店ID"),
):
    current_store_id = await get_current_store_id(store_id)
    q = Q(store_id=current_store_id)
    if name:
        q &= Q(name__contains=name)
    if member_no:
        q &= Q(member_no__contains=member_no)
    if phone:
        q &= Q(phone__contains=phone)
    if status is not None:
        q &= Q(status=bool(status))
    total, rows = await member_controller.list(page=page, page_size=page_size, search=q, order=["-updated_at"])
    data = [await item.to_dict() for item in rows]
    return SuccessExtra(data=data, total=total, page=page, page_size=page_size)


@router.get("/get", summary="查看会员详情")
async def get_member(
    id: int = Query(..., description="会员ID"),
    store_id: int | None = Query(None, description="门店ID"),
):
    current_store_id = await get_current_store_id(store_id)
    member_obj = await member_controller.get(id=id)
    if member_obj.store_id != current_store_id:
        raise HTTPException(status_code=403, detail="无权限访问该会员")
    return Success(data=await member_obj.to_dict())


@router.post("/create", summary="创建会员")
async def create_member(
    req_in: MemberCreate,
    store_id: int | None = Query(None, description="门店ID"),
):
    current_store_id = await get_current_store_id(store_id)
    if await member_controller.exists_member_no(store_id=current_store_id, member_no=req_in.member_no):
        raise HTTPException(status_code=400, detail="会员编号已存在")
    if await member_controller.exists_phone(store_id=current_store_id, phone=req_in.phone):
        raise HTTPException(status_code=400, detail="手机号已存在")
    await member_controller.create(obj_in={"store_id": current_store_id, **req_in.model_dump()})
    return Success(msg="Created Successfully")


@router.post("/update", summary="更新会员")
async def update_member(
    req_in: MemberUpdate,
    store_id: int | None = Query(None, description="门店ID"),
):
    current_store_id = await get_current_store_id(store_id)
    member_obj = await member_controller.get(id=req_in.id)
    if member_obj.store_id != current_store_id:
        raise HTTPException(status_code=403, detail="无权限访问该会员")
    if req_in.member_no and await member_controller.exists_member_no(
        store_id=current_store_id, member_no=req_in.member_no, exclude_id=req_in.id
    ):
        raise HTTPException(status_code=400, detail="会员编号已存在")
    if await member_controller.exists_phone(store_id=current_store_id, phone=req_in.phone, exclude_id=req_in.id):
        raise HTTPException(status_code=400, detail="手机号已存在")
    await member_controller.update(id=req_in.id, obj_in=req_in)
    return Success(msg="Updated Successfully")


@router.delete("/delete", summary="删除会员")
async def delete_member(
    id: int = Query(..., description="会员ID"),
    store_id: int | None = Query(None, description="门店ID"),
):
    current_store_id = await get_current_store_id(store_id)
    member_obj = await member_controller.get(id=id)
    if member_obj.store_id != current_store_id:
        raise HTTPException(status_code=403, detail="无权限访问该会员")
    await member_controller.remove(id=id)
    return Success(msg="Deleted Success")
