from pydantic import BaseModel
from typing import List

class AdminDashboardData(BaseModel):
    user_count: int
    order_count: int
    today_orders: int
    total_sales: float
    daily_order_trend: List[int]

class UserDashboardData(BaseModel):
    welcome_message: str

class DashboardResponse(BaseModel):
    is_admin: bool
    data: AdminDashboardData | UserDashboardData