from app.models.admin import User
from app.models.orders import Order
from app.schemas.dashboard import AdminDashboardData, UserDashboardData, DashboardResponse
from app.controllers.user import user_controller
from app.controllers.order import order_controller
from app.schemas.orders import OrderQuerySchema
from datetime import datetime, timedelta
from tortoise.functions import Sum

class DashboardController:
    async def get_dashboard_data(self, current_user: User) -> DashboardResponse:
        if current_user.is_superuser:
            user_count = await user_controller.model.all().count()
            
            orders_data = await order_controller.get_all(params=OrderQuerySchema(), current_user=current_user)
            order_count = orders_data.total

            # 获取今日订单
            today = datetime.utcnow().date()
            today_orders = await Order.filter(created_at__gte=today).count()

            # 使用数据库聚合计算总销售额
            sales_data = await Order.all().annotate(sum=Sum("item_amount")).values("sum")
            total_sales = sales_data[0].get("sum") if sales_data and sales_data[0].get("sum") is not None else 0.0

            # 模拟近七日订单趋势
            daily_order_trend = []
            for i in range(7):
                start_date = today - timedelta(days=i)
                end_date = start_date + timedelta(days=1)
                daily_count = await Order.filter(created_at__gte=start_date, created_at__lt=end_date).count()
                daily_order_trend.insert(0, daily_count)

            admin_data = AdminDashboardData(
                user_count=user_count,
                order_count=order_count,
                today_orders=today_orders,
                total_sales=total_sales,
                daily_order_trend=daily_order_trend,
            )
            return DashboardResponse(is_admin=True, data=admin_data)
        else:
            user_data = UserDashboardData(
                welcome_message=f"欢迎回来, {current_user.alias or current_user.username}!"
            )
            return DashboardResponse(is_admin=False, data=user_data)

dashboard_controller = DashboardController()