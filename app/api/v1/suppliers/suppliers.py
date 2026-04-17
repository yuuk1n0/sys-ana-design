from fastapi import APIRouter, Query
from fastapi.exceptions import HTTPException
from tortoise.expressions import Q

from app.controllers.supplier import supplier_controller
from app.controllers.user import user_controller
from app.core.ctx import CTX_USER_ID
from app.models.admin import Dept
from app.schemas import Success, SuccessExtra
from app.schemas.suppliers import SupplierCreate, SupplierUpdate

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


@router.get("/list", summary="查看供应商列表")
async def list_supplier(
    page: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量"),
    supplier_name: str = Query("", description="供应商名称"),
    supplier_code: str = Query("", description="供应商编码"),
    status: int | None = Query(None, description="状态"),
    store_id: int | None = Query(None, description="门店ID"),
):
    current_store_id = await get_current_store_id(store_id)
    q = Q(store_id=current_store_id)
    if supplier_name:
        q &= Q(supplier_name__contains=supplier_name)
    if supplier_code:
        q &= Q(supplier_code__contains=supplier_code)
    if status is not None:
        q &= Q(status=bool(status))
    total, rows = await supplier_controller.list(page=page, page_size=page_size, search=q, order=["-updated_at"])
    data = [await item.to_dict() for item in rows]
    return SuccessExtra(data=data, total=total, page=page, page_size=page_size)


@router.get("/get", summary="查看供应商详情")
async def get_supplier(
    id: int = Query(..., description="供应商ID"),
    store_id: int | None = Query(None, description="门店ID"),
):
    current_store_id = await get_current_store_id(store_id)
    supplier_obj = await supplier_controller.get(id=id)
    if supplier_obj.store_id != current_store_id:
        raise HTTPException(status_code=403, detail="无权限访问该供应商")
    return Success(data=await supplier_obj.to_dict())


@router.post("/create", summary="创建供应商")
async def create_supplier(
    req_in: SupplierCreate,
    store_id: int | None = Query(None, description="门店ID"),
):
    current_store_id = await get_current_store_id(store_id)
    if await supplier_controller.exists_supplier_code(store_id=current_store_id, supplier_code=req_in.supplier_code):
        raise HTTPException(status_code=400, detail="供应商编码已存在")
    await supplier_controller.create(obj_in={"store_id": current_store_id, **req_in.model_dump()})
    return Success(msg="Created Successfully")


@router.post("/update", summary="更新供应商")
async def update_supplier(
    req_in: SupplierUpdate,
    store_id: int | None = Query(None, description="门店ID"),
):
    current_store_id = await get_current_store_id(store_id)
    supplier_obj = await supplier_controller.get(id=req_in.id)
    if supplier_obj.store_id != current_store_id:
        raise HTTPException(status_code=403, detail="无权限访问该供应商")
    if req_in.supplier_code and await supplier_controller.exists_supplier_code(
        store_id=current_store_id, supplier_code=req_in.supplier_code, exclude_id=req_in.id
    ):
        raise HTTPException(status_code=400, detail="供应商编码已存在")
    await supplier_controller.update(id=req_in.id, obj_in=req_in)
    return Success(msg="Updated Successfully")


@router.delete("/delete", summary="删除供应商")
async def delete_supplier(
    id: int = Query(..., description="供应商ID"),
    store_id: int | None = Query(None, description="门店ID"),
):
    current_store_id = await get_current_store_id(store_id)
    supplier_obj = await supplier_controller.get(id=id)
    if supplier_obj.store_id != current_store_id:
        raise HTTPException(status_code=403, detail="无权限访问该供应商")
    await supplier_controller.remove(id=id)
    return Success(msg="Deleted Success")
