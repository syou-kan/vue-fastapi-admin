from pydantic import BaseModel

class AdminDashboardData(BaseModel):
    user_count: int
    order_count: int

class UserDashboardData(BaseModel):
    welcome_message: str

class DashboardResponse(BaseModel):
    is_admin: bool
    data: AdminDashboardData | UserDashboardData