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
    """
    初始化超级用户，如果不存在则创建，并确保其拥有'管理员'角色。
    """
    admin_user = await user_controller.get_by_username("admin")
    if not admin_user:
        admin_user_in = UserCreate(
            username="admin",
            password="123456",
            phone_number="18888888888",
            is_active=True,
            is_superuser=True,
            dept_id=0,
        )
        admin_user = await user_controller.create_user(admin_user_in)
        logger.info("超级用户创建成功。")

    # 确保超级用户有关联的'管理员'角色
    admin_role = await Role.get_or_none(name="管理员")
    if admin_user and admin_role:
        # 检查用户是否已有该角色
        has_admin_role = await admin_user.roles.filter(id=admin_role.id).exists()
        if not has_admin_role:
            await admin_user.roles.add(admin_role)
            logger.info("已为超级用户分配'管理员'角色。")
    elif not admin_role:
        logger.warning("初始化警告：'管理员'角色不存在，无法为超级用户分配角色。")


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
            name="订单管理",
            path="/order",
            order=5,
            parent_id=0,
            icon="mdi:cart",
            is_hidden=False,
            component="@/views/order/index.vue",
            keepalive=False,
            redirect="/order/list",
        )


async def init_apis():
    """
    初始化API，刷新API列表确保与代码同步。
    """
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


async def init_order_apis():
    """
    确保订单管理的API被手动注册到数据库中。
    这是一个保障性措施，以防 refresh_api 未能正确扫描到它们。
    """
    order_api_definitions = [
        {"method": "POST", "path": "/api/v1/orders/", "summary": "创建新订单", "tags": "订单管理"},
        {"method": "GET", "path": "/api/v1/orders/", "summary": "查看所有订单", "tags": "订单管理"},
        {"method": "GET", "path": "/api/v1/orders/{order_id}", "summary": "获取指定ID的订单", "tags": "订单管理"},
        {"method": "PUT", "path": "/api/v1/orders/{order_id}", "summary": "更新订单", "tags": "订单管理"},
        {"method": "DELETE", "path": "/api/v1/orders/{order_id}", "summary": "删除订单", "tags": "订单管理"},
    ]

    for api_def in order_api_definitions:
        await Api.get_or_create(
            path=api_def["path"],
            method=api_def["method"],
            defaults={"summary": api_def["summary"], "tags": api_def["tags"]}
        )
    logger.info("已手动确保订单管理API的注册。")


async def init_roles():
    """
    初始化角色。首次运行时创建默认角色和权限。
    后续运行时，确保管理员角色拥有所有API权限。
    """
    # 首次运行时，创建角色、分配菜单和基础API
    if not await Role.exists():
        logger.info("首次初始化角色权限...")
        admin_role = await Role.create(name="管理员", desc="管理员角色")
        user_role = await Role.create(name="普通用户", desc="普通用户角色")

        # 分配菜单
        all_menus = await Menu.all()
        if all_menus:
            await admin_role.menus.add(*all_menus)
            await user_role.menus.add(*all_menus)
            logger.info("已为默认角色分配菜单。")

        # 为普通用户分配基础API
        basic_apis_query = Q(method__in=["GET"]) | Q(tags="基础模块")
        basic_apis = await Api.filter(basic_apis_query)
        if basic_apis:
            await user_role.apis.add(*basic_apis)
            logger.info("已为'普通用户'角色分配基础API权限。")

    # 每次启动时，都为管理员同步所有API权限
    admin_role = await Role.get_or_none(name="管理员")
    if not admin_role:
        admin_role = await Role.create(name="管理员", desc="管理员角色")
        logger.info("已创建'管理员'角色。")

    all_apis = await Api.all()
    if all_apis:
        await admin_role.apis.clear()
        await admin_role.apis.add(*all_apis)
        logger.info("已将所有API权限强制同步至'管理员'角色。")


async def init_data():
    await init_db()
    await init_menus()
    await init_apis()
    await init_order_apis()
    await init_roles()
    await init_superuser()
