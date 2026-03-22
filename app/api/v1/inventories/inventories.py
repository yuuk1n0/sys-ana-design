from datetime import datetime

from fastapi import APIRouter, Query
from fastapi.exceptions import HTTPException

from app.controllers.inventory import inventory_controller
from app.controllers.user import user_controller
from app.core.ctx import CTX_USER_ID
from app.models.admin import Dept
from app.schemas import SuccessExtra

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


@router.get("/balance/list", summary="查看库存余额")
async def get_inventory_balance_list(
    page: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量"),
    name: str = Query("", description="商品名称"),
    category_id: int | None = Query(None, description="分类ID"),
    stock_status: int | None = Query(None, description="库存状态"),
    store_id: int | None = Query(None, description="门店ID"),
):
    current_store_id = await get_current_store_id(store_id)
    total, data = await inventory_controller.get_balance_data(
        store_id=current_store_id,
        page=page,
        page_size=page_size,
        name=name,
        category_id=category_id,
        stock_status=stock_status,
    )
    return SuccessExtra(data=data, total=total, page=page, page_size=page_size)


@router.get("/txn/list", summary="查看库存流水")
async def get_inventory_txn_list(
    page: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量"),
    product_id: int | None = Query(None, description="商品ID"),
    biz_type: str | None = Query(None, description="业务类型"),
    start_time: datetime | None = Query(None, description="开始时间"),
    end_time: datetime | None = Query(None, description="结束时间"),
    store_id: int | None = Query(None, description="门店ID"),
):
    current_store_id = await get_current_store_id(store_id)
    total, data = await inventory_controller.get_txn_data(
        store_id=current_store_id,
        page=page,
        page_size=page_size,
        product_id=product_id,
        biz_type=biz_type,
        start_time=start_time,
        end_time=end_time,
    )
    return SuccessExtra(data=data, total=total, page=page, page_size=page_size)


@router.get("/warning/list", summary="查看低库存预警")
async def get_inventory_warning_list(
    page: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量"),
    store_id: int | None = Query(None, description="门店ID"),
):
    current_store_id = await get_current_store_id(store_id)
    total, data = await inventory_controller.get_warning_data(
        store_id=current_store_id,
        page=page,
        page_size=page_size,
    )
    return SuccessExtra(data=data, total=total, page=page, page_size=page_size)
