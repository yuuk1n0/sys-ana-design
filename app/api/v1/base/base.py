from pathlib import Path
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.controllers.finance import finance_controller
from app.controllers.user import user_controller
from app.core.ctx import CTX_USER_ID
from app.core.dependency import DependAuth
from app.models.admin import (
    Api,
    AuditLog,
    Dept,
    InventoryTxn,
    Member,
    Menu,
    Product,
    ProductCategory,
    Role,
    StoreEmployee,
    StoreInventory,
    Supplier,
    User,
)
from app.schemas.base import Fail, Success
from app.schemas.login import *
from app.schemas.users import UpdatePassword
from app.settings import settings
from app.utils.jwt_utils import create_access_token
from app.utils.password import get_password_hash, verify_password

router = APIRouter()
AVATAR_DIR = Path(settings.BASE_DIR) / "static" / "avatars"
DEFAULT_AVATAR_FILE = "admin.jpg"


@router.post("/access_token", summary="获取token")
async def login_access_token(credentials: CredentialsSchema):
    user: User = await user_controller.authenticate(credentials)
    await user_controller.update_last_login(user.id)
    access_token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.now(timezone.utc) + access_token_expires

    data = JWTOut(
        access_token=create_access_token(
            data=JWTPayload(
                user_id=user.id,
                username=user.username,
                is_superuser=user.is_superuser,
                exp=expire,
            )
        ),
        username=user.username,
    )
    return Success(data=data.model_dump())


@router.get("/userinfo", summary="查看用户信息", dependencies=[DependAuth])
async def get_userinfo():
    user_id = CTX_USER_ID.get()
    user_obj = await user_controller.get(id=user_id)
    data = await user_obj.to_dict(exclude_fields=["password"])
    data["avatar"] = f"/api/v1/base/avatar/{DEFAULT_AVATAR_FILE}"
    return Success(data=data)


@router.get("/avatar/{file_name}", summary="获取本地头像")
async def get_local_avatar(file_name: str):
    safe_name = Path(file_name).name
    if safe_name != file_name:
        raise HTTPException(status_code=400, detail="invalid avatar file name")
    file_path = AVATAR_DIR / safe_name
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="avatar file not found")
    return FileResponse(path=file_path, filename=safe_name)


@router.get("/usermenu", summary="查看用户菜单", dependencies=[DependAuth])
async def get_user_menu():
    user_id = CTX_USER_ID.get()
    user_obj = await User.filter(id=user_id).first()
    menus: list[Menu] = []
    if user_obj.is_superuser:
        menus = await Menu.all()
    else:
        role_objs: list[Role] = await user_obj.roles
        for role_obj in role_objs:
            menu = await role_obj.menus
            menus.extend(menu)
        menus = list(set(menus))
    parent_menus: list[Menu] = []
    for menu in menus:
        if menu.parent_id == 0:
            parent_menus.append(menu)
    res = []
    for parent_menu in parent_menus:
        parent_menu_dict = await parent_menu.to_dict()
        parent_menu_dict["children"] = []
        for menu in menus:
            if menu.parent_id == parent_menu.id:
                parent_menu_dict["children"].append(await menu.to_dict())
        res.append(parent_menu_dict)
    return Success(data=res)


@router.get("/userapi", summary="查看用户API", dependencies=[DependAuth])
async def get_user_api():
    user_id = CTX_USER_ID.get()
    user_obj = await User.filter(id=user_id).first()
    if user_obj.is_superuser:
        api_objs: list[Api] = await Api.all()
        apis = [api.method.lower() + api.path for api in api_objs]
        return Success(data=apis)
    role_objs: list[Role] = await user_obj.roles
    apis = []
    for role_obj in role_objs:
        api_objs: list[Api] = await role_obj.apis
        apis.extend([api.method.lower() + api.path for api in api_objs])
    apis = list(set(apis))
    return Success(data=apis)


async def _resolve_current_store(user_obj: User):
    if user_obj.dept_id:
        return await Dept.filter(id=user_obj.dept_id, is_deleted=False).first()
    if user_obj.is_superuser:
        return await Dept.filter(is_deleted=False).order_by("id").first()
    return None


@router.get("/course_design_overview", summary="查看课程设计总览", dependencies=[DependAuth])
async def get_course_design_overview():
    user_id = CTX_USER_ID.get()
    user_obj = await user_controller.get(id=user_id)
    current_store = await _resolve_current_store(user_obj)

    dept_count = await Dept.filter(is_deleted=False).count()
    user_count = await User.all().count()
    role_count = await Role.all().count()
    menu_count = await Menu.all().count()
    api_count = await Api.all().count()
    audit_count = await AuditLog.all().count()

    store_metrics = {
        "store_id": current_store.id if current_store else None,
        "store_name": current_store.name if current_store else "未绑定门店",
        "category_count": 0,
        "product_count": 0,
        "inventory_sku_count": 0,
        "inventory_qty": 0,
        "inventory_warning_count": 0,
        "sales_order_count": 0,
        "net_sales_amount": 0.0,
        "member_count": 0,
        "member_points": 0,
        "employee_count": 0,
        "supplier_count": 0,
    }

    if current_store:
        store_id = current_store.id
        store_metrics["category_count"] = await ProductCategory.filter(store_id=store_id).count()
        store_metrics["product_count"] = await Product.filter(store_id=store_id).count()
        store_metrics["member_count"] = await Member.filter(store_id=store_id).count()
        store_metrics["employee_count"] = await StoreEmployee.filter(store_id=store_id).count()
        store_metrics["supplier_count"] = await Supplier.filter(store_id=store_id).count()

        inventory_rows = await StoreInventory.filter(store_id=store_id).all()
        store_metrics["inventory_sku_count"] = len(inventory_rows)
        store_metrics["inventory_qty"] = sum(item.available_qty for item in inventory_rows)
        store_metrics["inventory_warning_count"] = sum(
            1 for item in inventory_rows if item.available_qty <= item.low_stock_threshold
        )

        member_rows = await Member.filter(store_id=store_id).all()
        store_metrics["member_points"] = sum(item.points for item in member_rows)

        sales_rows = await InventoryTxn.filter(store_id=store_id, biz_type__in=["SALE", "RETURN"]).all()
        store_metrics["sales_order_count"] = len({item.biz_no for item in sales_rows})
        finance_overview = await finance_controller.get_overview(store_id=store_id)
        store_metrics["net_sales_amount"] = finance_overview["net_sales_amount"]

    phase_plan = [
        {"stage": "阶段 0", "name": "环境准备", "duration": "0.5 天"},
        {"stage": "阶段 1", "name": "基础模块", "duration": "1.5 天"},
        {"stage": "阶段 2", "name": "核心业务", "duration": "2 天"},
        {"stage": "阶段 3", "name": "统计报表", "duration": "1 天"},
        {"stage": "阶段 4", "name": "测试优化", "duration": "0.5 天"},
        {"stage": "阶段 5", "name": "部署上线", "duration": "0.5 天"},
    ]

    phase_one_modules = [
        {
            "name": "注册及登录模块",
            "status": "已实现",
            "route": "/login",
            "features": ["用户账号维护", "登录鉴权与会话管理", "基础权限校验预留接口"],
        },
        {
            "name": "商品管理模块",
            "status": "已实现",
            "route": "/store/product",
            "features": ["商品录入与维护", "分类管理", "库存与价格管理", "促销活动展示区"],
        },
        {
            "name": "仓库管理模块",
            "status": "已实现",
            "route": "/store/warehouse-center",
            "features": ["仓库信息概览", "入库出库管理", "库存盘点提示", "库存报警管理"],
        },
        {
            "name": "财务管理模块",
            "status": "已实现",
            "route": "/store/finance-center",
            "features": ["收银业务汇总", "财务报表", "成本核算看板", "预算与税务占位区"],
        },
    ]

    phase_two_modules = [
        {
            "name": "会员管理模块",
            "status": "已实现",
            "route": "/store/member",
            "features": ["会员档案", "等级管理", "积分政策", "消费记录与兑换能力展示"],
        },
        {
            "name": "员工管理模块",
            "status": "已实现",
            "route": "/store/store-employee",
            "features": ["员工档案", "岗位管理", "排班与考勤", "工资管理展示区"],
        },
        {
            "name": "销售管理模块",
            "status": "已实现",
            "route": "/store/sales",
            "features": ["销售开单", "销售退货", "统计报表", "商品销售排行"],
        },
        {
            "name": "供应商管理模块",
            "status": "已实现",
            "route": "/store/supplier",
            "features": ["供应商档案", "合同管理", "评价管理", "采购订单展示区"],
        },
        {
            "name": "系统管理模块",
            "status": "已实现",
            "route": "/system/ops-center",
            "features": ["用户权限管理", "系统日志", "数据备份恢复", "基础设置与维护"],
        },
    ]

    return Success(
        data={
            "current_store": store_metrics,
            "platform_metrics": {
                "dept_count": dept_count,
                "user_count": user_count,
                "role_count": role_count,
                "menu_count": menu_count,
                "api_count": api_count,
                "audit_count": audit_count,
            },
            "phase_plan": phase_plan,
            "phase_one_modules": phase_one_modules,
            "phase_two_modules": phase_two_modules,
        }
    )


@router.post("/update_password", summary="修改密码", dependencies=[DependAuth])
async def update_user_password(req_in: UpdatePassword):
    user_id = CTX_USER_ID.get()
    user = await user_controller.get(user_id)
    verified = verify_password(req_in.old_password, user.password)
    if not verified:
        return Fail(msg="旧密码验证错误！")
    user.password = get_password_hash(req_in.new_password)
    await user.save()
    return Success(msg="修改成功")
