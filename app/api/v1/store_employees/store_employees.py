from fastapi import APIRouter, Query
from fastapi.exceptions import HTTPException
from tortoise.expressions import Q

from app.controllers.store_employee import store_employee_controller
from app.controllers.user import user_controller
from app.core.ctx import CTX_USER_ID
from app.models.admin import Dept
from app.schemas import Success, SuccessExtra
from app.schemas.store_employees import StoreEmployeeCreate, StoreEmployeeUpdate

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


@router.get("/list", summary="查看门店员工列表")
async def list_store_employee(
    page: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量"),
    name: str = Query("", description="员工姓名"),
    employee_no: str = Query("", description="员工工号"),
    job_title: str = Query("", description="岗位"),
    status: int | None = Query(None, description="状态"),
    store_id: int | None = Query(None, description="门店ID"),
):
    current_store_id = await get_current_store_id(store_id)
    q = Q(store_id=current_store_id)
    if name:
        q &= Q(name__contains=name)
    if employee_no:
        q &= Q(employee_no__contains=employee_no)
    if job_title:
        q &= Q(job_title__contains=job_title)
    if status is not None:
        q &= Q(status=bool(status))
    total, rows = await store_employee_controller.list(page=page, page_size=page_size, search=q, order=["-updated_at"])
    data = [await item.to_dict() for item in rows]
    return SuccessExtra(data=data, total=total, page=page, page_size=page_size)


@router.get("/get", summary="查看门店员工详情")
async def get_store_employee(
    id: int = Query(..., description="员工ID"),
    store_id: int | None = Query(None, description="门店ID"),
):
    current_store_id = await get_current_store_id(store_id)
    employee_obj = await store_employee_controller.get(id=id)
    if employee_obj.store_id != current_store_id:
        raise HTTPException(status_code=403, detail="无权限访问该员工")
    return Success(data=await employee_obj.to_dict())


@router.post("/create", summary="创建门店员工")
async def create_store_employee(
    req_in: StoreEmployeeCreate,
    store_id: int | None = Query(None, description="门店ID"),
):
    current_store_id = await get_current_store_id(store_id)
    if await store_employee_controller.exists_employee_no(store_id=current_store_id, employee_no=req_in.employee_no):
        raise HTTPException(status_code=400, detail="员工工号已存在")
    if await store_employee_controller.exists_phone(store_id=current_store_id, phone=req_in.phone):
        raise HTTPException(status_code=400, detail="手机号已存在")
    await store_employee_controller.create(obj_in={"store_id": current_store_id, **req_in.model_dump()})
    return Success(msg="Created Successfully")


@router.post("/update", summary="更新门店员工")
async def update_store_employee(
    req_in: StoreEmployeeUpdate,
    store_id: int | None = Query(None, description="门店ID"),
):
    current_store_id = await get_current_store_id(store_id)
    employee_obj = await store_employee_controller.get(id=req_in.id)
    if employee_obj.store_id != current_store_id:
        raise HTTPException(status_code=403, detail="无权限访问该员工")
    if req_in.employee_no and await store_employee_controller.exists_employee_no(
        store_id=current_store_id, employee_no=req_in.employee_no, exclude_id=req_in.id
    ):
        raise HTTPException(status_code=400, detail="员工工号已存在")
    if await store_employee_controller.exists_phone(store_id=current_store_id, phone=req_in.phone, exclude_id=req_in.id):
        raise HTTPException(status_code=400, detail="手机号已存在")
    await store_employee_controller.update(id=req_in.id, obj_in=req_in)
    return Success(msg="Updated Successfully")


@router.delete("/delete", summary="删除门店员工")
async def delete_store_employee(
    id: int = Query(..., description="员工ID"),
    store_id: int | None = Query(None, description="门店ID"),
):
    current_store_id = await get_current_store_id(store_id)
    employee_obj = await store_employee_controller.get(id=id)
    if employee_obj.store_id != current_store_id:
        raise HTTPException(status_code=403, detail="无权限访问该员工")
    await store_employee_controller.remove(id=id)
    return Success(msg="Deleted Success")
