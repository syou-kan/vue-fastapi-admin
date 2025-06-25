import logging
from datetime import datetime
from typing import List, Optional

from fastapi.exceptions import HTTPException
from tortoise.expressions import Q

from app.core.crud import CRUDBase
from app.models.admin import User
from app.schemas.login import CredentialsSchema
from app.schemas.users import UserCreate, UserRegister, UserUpdate
from app.utils.password import get_password_hash, verify_password

from .role import role_controller


class UserController(CRUDBase[User, UserCreate, UserUpdate]):
    def __init__(self):
        super().__init__(model=User)

    async def get_by_username(self, username: str) -> Optional[User]:
        return await self.model.filter(username=username).first()

    async def get_by_phone_number(self, phone_number: str) -> Optional[User]:
        return await self.model.filter(phone_number=phone_number).first()

    async def create_user(self, obj_in: UserCreate) -> User:
        obj_in.password = get_password_hash(password=obj_in.password)
        obj = await self.create(obj_in)
        return obj

    async def register_user(self, obj_in: UserRegister) -> User:
        if await self.get_by_username(obj_in.username):
            raise HTTPException(status_code=400, detail="用户名已存在")
        obj_in_data = obj_in.model_dump()
        obj_in_data["password"] = get_password_hash(password=obj_in.password)
        user = await self.model.create(**obj_in_data)

        # 为新用户分配默认角色
        default_role = await role_controller.get_by_name("普通用户")
        if default_role:
            await user.roles.add(default_role)
        else:
            # 如果默认角色不存在，可以记录一个警告或采取其他措施
            logging.warning("Default role '普通用户' not found, user created without a role.")

        return user

    async def update_last_login(self, id: int) -> None:
        user = await self.model.get(id=id)
        user.last_login = datetime.now()
        await user.save()

    async def authenticate(self, credentials: CredentialsSchema) -> Optional["User"]:
        user = await self.get_by_phone_number(credentials.phone_number)
        if not user:
            raise HTTPException(status_code=400, detail="无效的手机号码")
        verified = verify_password(credentials.password, user.password)
        if not verified:
            raise HTTPException(status_code=400, detail="密码错误!")
        if not user.is_active:
            raise HTTPException(status_code=400, detail="用户已被禁用")
        return user

    async def update_roles(self, user: User, role_ids: List[int]) -> None:
        await user.roles.clear()
        for role_id in role_ids:
            role_obj = await role_controller.get(id=role_id)
            await user.roles.add(role_obj)

    async def search_users_by_id_query(self, query_str: str, limit: int = 10) -> List[User]:
        """
        根据用户ID片段或完整ID搜索用户。
        如果 query_str 可以转换为整数，则尝试精确匹配ID。
        """
        users = []
        try:
            user_id = int(query_str)
            # 使用 get_or_none 避免在找不到时抛出 DoesNotExist 异常
            user = await self.model.get_or_none(id=user_id)
            if user:
                users.append(user)
        except ValueError:
            # 如果 query_str 不能转换为整数，则不进行搜索，因为需求是按ID搜索
            # 如果未来需要支持其他字段的模糊搜索，可以在这里扩展
            # 例如，如果 query_str 不是数字，则搜索用户名或昵称：
            # users = await self.model.filter(
            #     Q(username__icontains=query_str) | Q(alias__icontains=query_str)
            # ).limit(limit)
            pass
        
        # 即使只有一个结果，也返回列表，以便前端统一处理
        return users

    async def reset_password(self, user_id: int):
        user_obj = await self.get(id=user_id)
        if user_obj.is_superuser:
            raise HTTPException(status_code=403, detail="不允许重置超级管理员密码")
        user_obj.password = get_password_hash(password="123456")
        await user_obj.save()

    async def fuzzy_search_by_username(
        self, username: str, limit: int = 3
    ) -> List[User]:
        """
        根据用户名模糊搜索用户
        :param username: 用户名查询字符串
        :param limit: 返回结果最大数量
        :return: 匹配的用户列表
        """
        if not username:
            return []
        return await self.model.filter(
            username__icontains=username
        ).limit(limit)


user_controller = UserController()
