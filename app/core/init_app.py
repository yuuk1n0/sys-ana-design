import shutil

from aerich import Command
from fastapi import FastAPI
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from tortoise.expressions import Q

from app.api import api_router
from app.controllers.api import api_controller
from app.controllers.user import UserCreate, user_controller
from app.core.exceptions import (
    DoesNotExist,
    DoesNotExistHandle,
    HTTPException,
    HttpExcHandle,
    IntegrityError,
    IntegrityHandle,
    RequestValidationError,
    RequestValidationHandle,
    ResponseValidationError,
    ResponseValidationHandle,
)
from app.log import logger
from app.models.admin import Api, Menu, Role
from app.schemas.menus import MenuType
from app.settings.config import settings

from .middlewares import BackGroundTaskMiddleware, HttpAuditLogMiddleware


def make_middlewares():
    middleware = [
        Middleware(
            CORSMiddleware,
            allow_origins=settings.CORS_ORIGINS,
            allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
            allow_methods=settings.CORS_ALLOW_METHODS,
            allow_headers=settings.CORS_ALLOW_HEADERS,
        ),
        Middleware(BackGroundTaskMiddleware),
        Middleware(
            HttpAuditLogMiddleware,
            methods=["GET", "POST", "PUT", "DELETE"],
            exclude_paths=[
                "/api/v1/base/access_token",
                "/docs",
                "/openapi.json",
            ],
        ),
    ]
    return middleware


def register_exceptions(app: FastAPI):
    app.add_exception_handler(DoesNotExist, DoesNotExistHandle)
    app.add_exception_handler(HTTPException, HttpExcHandle)
    app.add_exception_handler(IntegrityError, IntegrityHandle)
    app.add_exception_handler(RequestValidationError, RequestValidationHandle)
    app.add_exception_handler(ResponseValidationError, ResponseValidationHandle)


def register_routers(app: FastAPI, prefix: str = "/api"):
    app.include_router(api_router, prefix=prefix)


async def init_superuser():
    user = await user_controller.model.exists()
    if not user:
        await user_controller.create_user(
            UserCreate(
                username="admin",
                email="admin@admin.com",
                password="123456",
                is_active=True,
                is_superuser=True,
            )
        )


async def init_menus():
    menus = await Menu.exists()
    if not menus:
        parent_menu = await Menu.create(
            menu_type=MenuType.CATALOG,
            name="系统管理",
            path="/system",
            order=1,
            parent_id=0,
            icon="carbon:gui-management",
            is_hidden=False,
            component="Layout",
            keepalive=False,
            redirect="/system/user",
        )
        children_menu = [
            Menu(
                menu_type=MenuType.MENU,
                name="用户管理",
                path="user",
                order=1,
                parent_id=parent_menu.id,
                icon="material-symbols:person-outline-rounded",
                is_hidden=False,
                component="/system/user",
                keepalive=False,
            ),
            Menu(
                menu_type=MenuType.MENU,
                name="角色管理",
                path="role",
                order=2,
                parent_id=parent_menu.id,
                icon="carbon:user-role",
                is_hidden=False,
                component="/system/role",
                keepalive=False,
            ),
            Menu(
                menu_type=MenuType.MENU,
                name="菜单管理",
                path="menu",
                order=3,
                parent_id=parent_menu.id,
                icon="material-symbols:list-alt-outline",
                is_hidden=False,
                component="/system/menu",
                keepalive=False,
            ),
            Menu(
                menu_type=MenuType.MENU,
                name="API管理",
                path="api",
                order=4,
                parent_id=parent_menu.id,
                icon="ant-design:api-outlined",
                is_hidden=False,
                component="/system/api",
                keepalive=False,
            ),
            Menu(
                menu_type=MenuType.MENU,
                name="部门管理",
                path="dept",
                order=5,
                parent_id=parent_menu.id,
                icon="mingcute:department-line",
                is_hidden=False,
                component="/system/dept",
                keepalive=False,
            ),
            Menu(
                menu_type=MenuType.MENU,
                name="审计日志",
                path="auditlog",
                order=6,
                parent_id=parent_menu.id,
                icon="ph:clipboard-text-bold",
                is_hidden=False,
                component="/system/auditlog",
                keepalive=False,
            ),
        ]
        await Menu.bulk_create(children_menu)
        await Menu.create(
            menu_type=MenuType.MENU,
            name="一级菜单",
            path="/top-menu",
            order=2,
            parent_id=0,
            icon="material-symbols:featured-play-list-outline",
            is_hidden=False,
            component="/top-menu",
            keepalive=False,
            redirect="",
        )
    await ensure_store_menus()


async def ensure_store_menus():
    store_parent = await Menu.filter(path="/store", parent_id=0).first()
    if not store_parent:
        store_parent = await Menu.create(
            menu_type=MenuType.CATALOG,
            name="门店运营",
            path="/store",
            order=3,
            parent_id=0,
            icon="material-symbols:storefront-outline",
            is_hidden=False,
            component="Layout",
            keepalive=False,
            redirect="/store/product",
        )
    children = [
        dict(
            name="商品分类",
            path="product-category",
            order=1,
            icon="material-symbols:category-outline",
            component="/store/product-category",
        ),
        dict(
            name="商品管理",
            path="product",
            order=2,
            icon="material-symbols:inventory-2-outline",
            component="/store/product",
        ),
        dict(
            name="库存余额",
            path="inventory-balance",
            order=3,
            icon="material-symbols:inventory-2",
            component="/store/inventory-balance",
        ),
        dict(
            name="库存流水",
            path="inventory-txn",
            order=4,
            icon="material-symbols:receipt-long-outline",
            component="/store/inventory-txn",
        ),
        dict(
            name="库存预警",
            path="inventory-warning",
            order=5,
            icon="material-symbols:warning-outline",
            component="/store/inventory-warning",
        ),
    ]
    for item in children:
        exists = await Menu.filter(path=item["path"], parent_id=store_parent.id).exists()
        if exists:
            continue
        await Menu.create(
            menu_type=MenuType.MENU,
            name=item["name"],
            path=item["path"],
            order=item["order"],
            parent_id=store_parent.id,
            icon=item["icon"],
            is_hidden=False,
            component=item["component"],
            keepalive=False,
            redirect="",
        )


async def init_apis():
    apis = await api_controller.model.exists()
    if not apis:
        await api_controller.refresh_api()


async def init_db():
    command = Command(tortoise_config=settings.TORTOISE_ORM)
    try:
        await command.init_db(safe=True)
    except FileExistsError:
        pass

    await command.init()
    try:
        await command.migrate()
    except AttributeError:
        logger.warning("unable to retrieve model history from database, model history will be created from scratch")
        shutil.rmtree("migrations")
        await command.init_db(safe=True)

    await command.upgrade(run_in_transaction=True)


async def init_roles():
    roles = await Role.exists()
    if not roles:
        admin_role = await Role.create(
            name="管理员",
            desc="管理员角色",
        )
        user_role = await Role.create(
            name="普通用户",
            desc="普通用户角色",
        )

        # 分配所有API给管理员角色
        all_apis = await Api.all()
        await admin_role.apis.add(*all_apis)
        # 分配所有菜单给管理员和普通用户
        all_menus = await Menu.all()
        await admin_role.menus.add(*all_menus)
        await user_role.menus.add(*all_menus)

        # 为普通用户分配基本API
        basic_apis = await Api.filter(Q(method__in=["GET"]) | Q(tags="基础模块"))
        await user_role.apis.add(*basic_apis)
    await ensure_role_permissions()


async def ensure_role_permissions():
    admin_role = await Role.filter(name="管理员").first()
    if admin_role:
        all_apis = await Api.all()
        existed_apis = await admin_role.apis
        merge_apis = list({api.id: api for api in (list(existed_apis) + list(all_apis))}.values())
        await admin_role.apis.clear()
        await admin_role.apis.add(*merge_apis)
        all_menus = await Menu.all()
        existed_menus = await admin_role.menus
        merge_menus = list({menu.id: menu for menu in (list(existed_menus) + list(all_menus))}.values())
        await admin_role.menus.clear()
        await admin_role.menus.add(*merge_menus)

    user_role = await Role.filter(name="普通用户").first()
    if user_role:
        basic_apis = await Api.filter(Q(method__in=["GET"]) | Q(tags="基础模块"))
        store_apis = await Api.filter(tags__in=["商品模块", "商品分类模块", "库存模块", "财务模块"])
        origin_apis = await user_role.apis
        merge_apis = list({api.id: api for api in (list(origin_apis) + list(basic_apis) + list(store_apis))}.values())
        await user_role.apis.clear()
        await user_role.apis.add(*merge_apis)
        store_menu = await Menu.filter(path="/store", parent_id=0).first()
        if store_menu:
            store_children = await Menu.filter(parent_id=store_menu.id)
            origin_menus = await user_role.menus
            merged_menus = list({m.id: m for m in (origin_menus + [store_menu] + list(store_children))}.values())
            await user_role.menus.clear()
            await user_role.menus.add(*merged_menus)


async def init_data():
    await init_db()
    await init_superuser()
    await init_menus()
    await init_apis()
    await init_roles()
