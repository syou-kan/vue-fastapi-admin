import shutil

from tortoise import Tortoise
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from tortoise.exceptions import DoesNotExist, IntegrityError
from tortoise.expressions import Q

from app.api import api_router
from app.controllers.api import api_controller
from app.controllers.user import UserCreate, user_controller
from app.core.exceptions import (
    DoesNotExistHandle,
    HttpExcHandle,
    IntegrityHandle,
    RequestValidationHandle,
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
        
        # 创建仪表盘菜单（将显示为"首页"）
        await Menu.create(
            menu_type=MenuType.MENU,
            name="仪表盘",
            path="/dashboard",
            order=0,
            parent_id=0,
            icon="mdi:view-dashboard",
            is_hidden=False,
            component="/dashboard",
            keepalive=False,
        )
        
        # 创建订单管理菜单
        await Menu.create(
            menu_type=MenuType.MENU,
            name="订单管理",
            path="/order",
            order=5,
            parent_id=0,
            icon="mdi:cart",
            is_hidden=False,
            component="/order",
            keepalive=False,
        )
        
        # 创建个人中心菜单（隐藏，不在菜单栏显示）
        await Menu.create(
            menu_type=MenuType.MENU,
            name="个人中心",
            path="/profile",
            order=10,
            parent_id=0,
            icon="mdi:account",
            is_hidden=True,
            component="/profile",
            keepalive=False,
        )


async def init_apis():
    """
    初始化API，刷新API列表确保与代码同步。
    """
    await api_controller.refresh_api()


async def init_tortoise():
    """
    初始化 Tortoise ORM 并创建数据库表。
    """
    await Tortoise.init(config=settings.TORTOISE_ORM)
    # 生成数据库模式，如果表不存在则创建
    await Tortoise.generate_schemas()


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


async def init_user_specific_apis():
    """
    确保用户相关的API被正确注册到数据库中。
    """
    user_api_definitions = [
        {"method": "GET", "path": "/api/v1/user/get", "summary": "查看用户详细信息", "tags": "用户管理"},
        {"method": "POST", "path": "/api/v1/user/update", "summary": "更新用户信息", "tags": "用户管理"},
        {"method": "GET", "path": "/api/v1/dashboard", "summary": "访问仪表盘", "tags": "仪表盘"},
    ]

    for api_def in user_api_definitions:
        await Api.get_or_create(
            path=api_def["path"],
            method=api_def["method"],
            defaults={"summary": api_def["summary"], "tags": api_def["tags"]}
        )
    logger.info("已手动确保用户相关API的注册。")


async def init_roles():
    """
    初始化角色。首次运行时创建默认角色和权限。
    后续运行时，确保管理员角色拥有所有API权限，普通用户角色拥有精确的API权限。
    """
    # 首次运行时，创建角色
    if not await Role.exists():
        logger.info("首次初始化角色权限...")
        admin_role = await Role.create(name="管理员", desc="管理员角色")
        user_role = await Role.create(name="普通用户", desc="普通用户角色")
        logger.info("已创建默认角色。")
    else:
        admin_role = await Role.get_or_none(name="管理员")
        user_role = await Role.get_or_none(name="普通用户")
        
        if not admin_role:
            admin_role = await Role.create(name="管理员", desc="管理员角色")
            logger.info("已创建'管理员'角色。")
            
        if not user_role:
            user_role = await Role.create(name="普通用户", desc="普通用户角色")
            logger.info("已创建'普通用户'角色。")

    # 为管理员分配所有菜单
    all_menus = await Menu.all()
    if all_menus and admin_role:
        await admin_role.menus.clear()
        await admin_role.menus.add(*all_menus)
        logger.info("已为'管理员'角色分配所有菜单。")

    # 为普通用户分配特定菜单（仪表盘、订单管理、个人中心）
    # 注意：仪表盘和个人中心设为隐藏，但用户仍可通过直接URL访问
    if user_role:
        user_menus = await Menu.filter(
            Q(name__in=["仪表盘", "订单管理", "个人中心"])
        )
        if user_menus:
            await user_role.menus.clear()
            await user_role.menus.add(*user_menus)
            logger.info(f"已为'普通用户'角色分配 {len(user_menus)} 个菜单（包含隐藏菜单）。")

    # 每次启动时，都为管理员同步所有API权限
    all_apis = await Api.all()
    if all_apis and admin_role:
        await admin_role.apis.clear()
        await admin_role.apis.add(*all_apis)
        logger.info("已将所有API权限强制同步至'管理员'角色。")

    # 为普通用户配置精确的API权限
    if user_role:
        await configure_user_role_permissions(user_role)


async def configure_user_role_permissions(user_role: Role):
    """
    为普通用户角色配置精确的API权限。
    根据权限方案设计，普通用户只能访问特定的API。
    """
    # 定义普通用户允许访问的API权限
    user_api_permissions = [
        # 基础模块 - 个人信息相关
        {"method": "GET", "path": "/api/v1/base/userinfo"},
        {"method": "POST", "path": "/api/v1/base/update_password"},
        {"method": "GET", "path": "/api/v1/base/usermenu"},
        {"method": "GET", "path": "/api/v1/base/userapi"},
        
        # 仪表盘
        {"method": "GET", "path": "/api/v1/dashboard"},
        
        # 用户管理 - 仅限查看和修改自己的信息
        {"method": "GET", "path": "/api/v1/user/get"},
        {"method": "POST", "path": "/api/v1/user/update"},
        
        # 订单管理 - 仅限操作自己的订单
        {"method": "GET", "path": "/api/v1/orders/"},
        {"method": "GET", "path": "/api/v1/orders/{order_id}"},
        {"method": "POST", "path": "/api/v1/orders/"},
        {"method": "PUT", "path": "/api/v1/orders/{order_id}"},
    ]
    
    # 清除现有权限
    await user_role.apis.clear()
    
    # 添加新的权限
    user_apis = []
    for permission in user_api_permissions:
        api = await Api.get_or_none(
            method=permission["method"],
            path=permission["path"]
        )
        if api:
            user_apis.append(api)
        else:
            logger.warning(
                f"API权限配置警告：未找到API {permission['method']} {permission['path']}"
            )
    
    if user_apis:
        await user_role.apis.add(*user_apis)
        logger.info(f"已为'普通用户'角色配置 {len(user_apis)} 个API权限。")
    else:
        logger.warning("警告：未能为'普通用户'角色配置任何API权限。")


async def init_data():
    await init_tortoise()
    await init_menus()
    await init_apis()
    await init_order_apis()
    await init_user_specific_apis()
    await init_roles()
    await init_superuser()
