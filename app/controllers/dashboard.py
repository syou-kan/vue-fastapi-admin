from app.models.admin import User
from app.schemas.dashboard import AdminDashboardData, UserDashboardData, DashboardResponse
from app.controllers.user import user_controller
# 导入获取订单总数的逻辑
from app.controllers.order import order_controller
from app.schemas.orders import OrderQuerySchema

class DashboardController:
    async def get_dashboard_data(self, current_user: User) -> DashboardResponse:
        if current_user.is_superuser:
            user_count = await user_controller.model.all().count()
            
            # 修正：调用 order_controller 的 get_all 方法并获取总数
            # 注意：为 get_all 传递一个默认的 OrderQuerySchema 实例
            orders_data = await order_controller.get_all(params=OrderQuerySchema(), current_user=current_user)
            order_count = orders_data.total

            admin_data = AdminDashboardData(
                user_count=user_count,
                order_count=order_count
            )
            return DashboardResponse(is_admin=True, data=admin_data)
        else:
            user_data = UserDashboardData(
                welcome_message=f"欢迎回来, {current_user.alias or current_user.username}!"
            )
            return DashboardResponse(is_admin=False, data=user_data)

dashboard_controller = DashboardController()