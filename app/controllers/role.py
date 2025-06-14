from http.client import HTTPException
from typing import List, Optional

from app.core.crud import CRUDBase
from app.models.admin import Api, Menu, Role
from app.schemas.login import CredentialsSchema
from app.schemas.roles import RoleCreate, RoleUpdate


class RoleController(CRUDBase[Role, RoleCreate, RoleUpdate]):
    def __init__(self):
        super().__init__(model=Role)

    async def is_exist(self, name: str) -> bool:
        return await self.model.filter(name=name).exists()

    async def update_roles(self, role: Role, menu_ids: List[int], api_infos: List[dict]) -> None:
        await role.menus.clear()
        for menu_id in menu_ids:
            menu_obj = await Menu.filter(id=menu_id).first()
            await role.menus.add(menu_obj)

        await role.apis.clear()
        for item in api_infos:
            api_obj = await Api.filter(path=item.get("path"), method=item.get("method")).first()
            await role.apis.add(api_obj)

    async def authenticate(self, credentials: CredentialsSchema) -> Optional["User"]:
        # 支持手机号或用户名登录
        if credentials.username.isdigit():  # 如果是纯数字，尝试作为手机号登录
            user = await self.model.filter(phone=credentials.username).first()
        else:  # 否则作为用户名登录
            user = await self.model.filter(username=credentials.username).first()

        if not user:
            raise HTTPException(status_code=400, detail="用户不存在")


role_controller = RoleController()
