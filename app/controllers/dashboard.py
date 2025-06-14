from app.models.admin import User, Role, Menu, Api
from app.schemas.dashboard import AdminWorkbenchData, UserWorkbenchData
from app.schemas.users import BaseUser


class DashboardController:
    @classmethod
    async def get_workbench_data(
        cls, current_user: BaseUser
    ) -> AdminWorkbenchData | UserWorkbenchData:
        """
        根据用户角色返回不同的工作台数据
        """
        if current_user.is_superuser:
            # 查询管理员所需数据
            user_count = await User.all().count()
            role_count = await Role.all().count()
            menu_count = await Menu.all().count()
            api_count = await Api.all().count()
            return AdminWorkbenchData(
                user_count=user_count,
                role_count=role_count,
                menu_count=menu_count,
                api_count=api_count,
            )
        else:
            # 模拟普通用户数据
            return UserWorkbenchData(task_count=10, message_count=99)


dashboard_controller = DashboardController()