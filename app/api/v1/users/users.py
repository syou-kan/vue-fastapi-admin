import logging

from fastapi import APIRouter, Body, Query
from tortoise.expressions import Q

from app.controllers.user import user_controller
from app.schemas.base import Fail, Success, SuccessExtra
from app.schemas.users import *
from app.core.dependency import DependAuth, DependPermisson, DependDataIsolation, DependEnhancedPermission
from app.core.ctx import CTX_USER_ID
from app.models.admin import User

logger = logging.getLogger(__name__)

router = APIRouter()
public_router = APIRouter()


@router.get("/list", summary="查看用户列表")
async def list_user(
    page: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量"),
    username: str = Query("", description="用户名称，用于搜索"),
    phone: str = Query("", description="手机号，用于搜索"),
):
    q = Q()
    if username:
        q &= Q(username__contains=username)
    if phone:
        q &= Q(phone_number__contains=phone)
    total, user_objs = await user_controller.list(page=page, page_size=page_size, search=q)
    data = [await obj.to_dict(m2m=True, exclude_fields=["password"]) for obj in user_objs]
    for item in data:
        item.pop("dept_id", None)
        item["dept"] = {}

    return SuccessExtra(data=data, total=total, page=page, page_size=page_size)


@router.get("/get", summary="查看用户", dependencies=[DependEnhancedPermission])
async def get_user(
    user_id: int = Query(None, description="用户ID"),
):
    """
    查看用户详细信息。
    普通用户只能查看自己的信息，管理员可以查看任何用户的信息。
    如果不提供user_id，则返回当前用户的信息。
    """
    current_user_id = CTX_USER_ID.get()
    current_user = await user_controller.get(id=current_user_id)
    
    # 如果没有提供user_id，返回当前用户信息
    if user_id is None:
        user_id = current_user_id
    
    # 普通用户只能查看自己的信息
    if not current_user.is_superuser and user_id != current_user_id:
        return Fail(msg="Access denied: You can only view your own information")
    
    user_obj = await user_controller.get(id=user_id)
    if not user_obj:
        return Fail(msg="User not found")
        
    user_dict = await user_obj.to_dict(exclude_fields=["password"])
    return Success(data=user_dict)


@router.post("/create", summary="创建用户")
async def create_user(
    user_in: UserCreate,
):
    new_user = await user_controller.create_user(obj_in=user_in)
    if user_in.role_ids:
        await user_controller.update_roles(new_user, user_in.role_ids)
    return Success(msg="Created Successfully")


@router.post("/update", summary="更新用户", dependencies=[DependEnhancedPermission])
async def update_user(
    user_in: UserUpdate,
):
    """
    更新用户信息。
    普通用户只能更新自己的信息，管理员可以更新任何用户的信息。
    """
    current_user_id = CTX_USER_ID.get()
    current_user = await user_controller.get(id=current_user_id)
    
    # 普通用户只能更新自己的信息
    if not current_user.is_superuser and user_in.id != current_user_id:
        return Fail(msg="Access denied: You can only update your own information")
    
    # 普通用户不能修改敏感字段
    if not current_user.is_superuser:
        # 创建一个新的更新对象，排除敏感字段
        update_data = user_in.model_dump(exclude_unset=True)
        # 普通用户不能修改这些字段
        forbidden_fields = ['is_superuser', 'is_active', 'role_ids']
        for field in forbidden_fields:
            if field in update_data:
                return Fail(msg=f"Access denied: You cannot modify the '{field}' field")
        
        # 重新创建UserUpdate对象，只包含允许的字段
        allowed_update = UserUpdate(
            id=user_in.id,
            username=update_data.get('username'),
            alias=update_data.get('alias'),
            phone_number=update_data.get('phone_number'),
            company_name=update_data.get('company_name'),
            credit_code=update_data.get('credit_code')
        )
        user = await user_controller.update(id=user_in.id, obj_in=allowed_update)
    else:
        # 管理员可以更新所有字段
        user = await user_controller.update(id=user_in.id, obj_in=user_in)
        if user_in.role_ids:
            await user_controller.update_roles(user, user_in.role_ids)
    
    return Success(msg="Updated Successfully")


@router.delete("/delete", summary="删除用户")
async def delete_user(
    user_id: int = Query(..., description="用户ID"),
):
    await user_controller.remove(id=user_id)
    return Success(msg="Deleted Successfully")


@router.post("/reset_password", summary="重置密码")
async def reset_password(user_id: int = Body(..., description="用户ID", embed=True)):
    await user_controller.reset_password(user_id)
    return Success(msg="密码已重置为123456")


@public_router.post("/register", summary="用户注册")
async def register_user(
    user_in: UserRegister,
):
    await user_controller.register_user(obj_in=user_in)
    return Success(msg="注册成功")
