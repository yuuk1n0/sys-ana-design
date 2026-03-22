from fastapi import APIRouter, Query
from fastapi.exceptions import HTTPException
from tortoise.expressions import Q

from app.controllers.product_category import product_category_controller
from app.controllers.user import user_controller
from app.core.ctx import CTX_USER_ID
from app.models.admin import Dept
from app.schemas import Success, SuccessExtra
from app.schemas.product_categories import ProductCategoryCreate, ProductCategoryUpdate

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


@router.get("/list", summary="查看商品分类列表")
async def list_product_category(
    name: str = Query("", description="分类名称"),
    status: int | None = Query(None, description="状态"),
    store_id: int | None = Query(None, description="门店ID"),
):
    current_store_id = await get_current_store_id(store_id)
    q = Q(store_id=current_store_id)
    if name:
        q &= Q(name__contains=name)
    if status is not None:
        q &= Q(status=bool(status))
    data = [await item.to_dict() for item in await product_category_controller.model.filter(q).order_by("sort", "id")]
    return SuccessExtra(data=data, total=len(data), page=1, page_size=len(data))


@router.post("/create", summary="创建商品分类")
async def create_product_category(
    req_in: ProductCategoryCreate,
    store_id: int | None = Query(None, description="门店ID"),
):
    current_store_id = await get_current_store_id(store_id)
    if await product_category_controller.exists_name(store_id=current_store_id, name=req_in.name):
        raise HTTPException(status_code=400, detail="分类名称已存在")
    await product_category_controller.create(obj_in={"store_id": current_store_id, **req_in.model_dump()})
    return Success(msg="Created Successfully")


@router.post("/update", summary="更新商品分类")
async def update_product_category(
    req_in: ProductCategoryUpdate,
    store_id: int | None = Query(None, description="门店ID"),
):
    current_store_id = await get_current_store_id(store_id)
    category_obj = await product_category_controller.get(id=req_in.id)
    if category_obj.store_id != current_store_id:
        raise HTTPException(status_code=403, detail="无权限访问该分类")
    if req_in.name and await product_category_controller.exists_name(
        store_id=current_store_id, name=req_in.name, exclude_id=req_in.id
    ):
        raise HTTPException(status_code=400, detail="分类名称已存在")
    await product_category_controller.update(id=req_in.id, obj_in=req_in)
    return Success(msg="Updated Successfully")


@router.delete("/delete", summary="删除商品分类")
async def delete_product_category(
    id: int = Query(..., description="分类ID"),
    store_id: int | None = Query(None, description="门店ID"),
):
    current_store_id = await get_current_store_id(store_id)
    category_obj = await product_category_controller.get(id=id)
    if category_obj.store_id != current_store_id:
        raise HTTPException(status_code=403, detail="无权限访问该分类")
    if await product_category_controller.has_products(store_id=current_store_id, category_id=id):
        raise HTTPException(status_code=400, detail="分类下存在商品，无法删除")
    await product_category_controller.remove(id=id)
    return Success(msg="Deleted Success")
