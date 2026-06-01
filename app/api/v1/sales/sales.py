from datetime import datetime

from fastapi import APIRouter, Query
from fastapi.exceptions import HTTPException

from app.controllers.sales import sales_controller
from app.controllers.user import user_controller
from app.core.ctx import CTX_USER_ID
from app.models.admin import Dept
from app.schemas import Success, SuccessExtra
from app.schemas.sales import SalesOrderCreate

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


@router.post("/submit", summary="提交销售单")
async def submit_sale_order(
    req_in: SalesOrderCreate,
    store_id: int | None = Query(None, description="门店ID"),
):
    operator_id, current_store_id = await get_current_store_id(store_id)
    data = await sales_controller.submit_order(
        store_id=current_store_id,
        operator_id=operator_id,
        biz_type="SALE",
        obj_in=req_in,
    )
    return Success(data=data, msg="Created Successfully")


@router.post("/return", summary="提交退货单")
async def submit_return_order(
    req_in: SalesOrderCreate,
    store_id: int | None = Query(None, description="门店ID"),
):
    operator_id, current_store_id = await get_current_store_id(store_id)
    data = await sales_controller.submit_order(
        store_id=current_store_id,
        operator_id=operator_id,
        biz_type="RETURN",
        obj_in=req_in,
    )
    return Success(data=data, msg="Created Successfully")


@router.get("/order/list", summary="查看销售单据列表")
async def get_sales_order_list(
    page: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量"),
    biz_type: str | None = Query(None, description="业务类型"),
    biz_no: str | None = Query(None, description="业务单号"),
    start_time: datetime | None = Query(None, description="开始时间"),
    end_time: datetime | None = Query(None, description="结束时间"),
    store_id: int | None = Query(None, description="门店ID"),
):
    _, current_store_id = await get_current_store_id(store_id)
    total, data = await sales_controller.list_orders(
        store_id=current_store_id,
        page=page,
        page_size=page_size,
        biz_type=biz_type,
        biz_no=biz_no,
        start_time=start_time,
        end_time=end_time,
    )
    return SuccessExtra(data=data, total=total, page=page, page_size=page_size)


@router.get("/order/get", summary="查看销售单据详情")
async def get_sales_order_detail(
    biz_no: str = Query(..., description="业务单号"),
    store_id: int | None = Query(None, description="门店ID"),
):
    _, current_store_id = await get_current_store_id(store_id)
    data = await sales_controller.get_order_detail(store_id=current_store_id, biz_no=biz_no)
    return Success(data=data)
