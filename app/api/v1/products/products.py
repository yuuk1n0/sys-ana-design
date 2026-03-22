from fastapi import APIRouter, Query
from fastapi.exceptions import HTTPException

from app.controllers.inventory import inventory_controller
from app.controllers.product import product_controller
from app.controllers.user import user_controller
from app.core.ctx import CTX_USER_ID
from app.models.admin import Dept
from app.schemas import Success, SuccessExtra
from app.schemas.products import ProductCreate, ProductStatusUpdate, ProductUpdate

router = APIRouter()


async def get_current_store_id(store_id: int | None = None):
    user_id = CTX_USER_ID.get()
    current_user = await user_controller.get(id=user_id)
    if store_id is not None:
        exists = await Dept.filter(id=store_id, is_deleted=False).exists()
        if not exists:
            raise HTTPException(status_code=400, detail="门店不存在")
        return current_user.id, store_id
    if current_user.dept_id:
        return current_user.id, current_user.dept_id
    if current_user.is_superuser:
        default_store = await Dept.filter(is_deleted=False).order_by("id").first()
        if default_store:
            current_user.dept_id = default_store.id
            await current_user.save()
            return current_user.id, default_store.id
        raise HTTPException(status_code=400, detail="暂无可用门店，请先创建门店")
    raise HTTPException(status_code=400, detail="当前用户未绑定门店")


@router.get("/list", summary="查看商品列表")
async def list_product(
    page: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量"),
    name: str = Query("", description="商品名称"),
    category_id: int | None = Query(None, description="分类ID"),
    status: int | None = Query(None, description="上架状态"),
    stock_status: int | None = Query(None, description="库存状态"),
    store_id: int | None = Query(None, description="门店ID"),
):
    _, current_store_id = await get_current_store_id(store_id)
    total, data = await inventory_controller.get_balance_data(
        store_id=current_store_id,
        page=page,
        page_size=page_size,
        name=name,
        category_id=category_id,
        status=status,
        stock_status=stock_status,
    )
    return SuccessExtra(data=data, total=total, page=page, page_size=page_size)


@router.get("/get", summary="查看商品详情")
async def get_product(
    id: int = Query(..., description="商品ID"),
    store_id: int | None = Query(None, description="门店ID"),
):
    _, current_store_id = await get_current_store_id(store_id)
    product_obj = await product_controller.get(id=id)
    if product_obj.store_id != current_store_id:
        raise HTTPException(status_code=403, detail="无权限访问该商品")
    item = await product_obj.to_dict()
    inventory_obj = await inventory_controller.get_by_store_product(store_id=current_store_id, product_id=id)
    item["available_qty"] = inventory_obj.available_qty if inventory_obj else 0
    return Success(data=item)


@router.post("/create", summary="创建商品")
async def create_product(
    req_in: ProductCreate,
    store_id: int | None = Query(None, description="门店ID"),
):
    operator_id, current_store_id = await get_current_store_id(store_id)
    await product_controller.create_product(store_id=current_store_id, operator_id=operator_id, obj_in=req_in)
    return Success(msg="Created Successfully")


@router.post("/update", summary="更新商品")
async def update_product(
    req_in: ProductUpdate,
    store_id: int | None = Query(None, description="门店ID"),
):
    operator_id, current_store_id = await get_current_store_id(store_id)
    await product_controller.update_product(store_id=current_store_id, operator_id=operator_id, obj_in=req_in)
    return Success(msg="Updated Successfully")


@router.post("/change_status", summary="更新商品状态")
async def change_product_status(
    req_in: ProductStatusUpdate,
    store_id: int | None = Query(None, description="门店ID"),
):
    _, current_store_id = await get_current_store_id(store_id)
    await product_controller.change_status(store_id=current_store_id, obj_in=req_in)
    return Success(msg="Updated Successfully")
