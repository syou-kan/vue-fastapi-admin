from fastapi import APIRouter, Depends
from app.core.dependency import DependAuth
from app.models.admin import User
from app.schemas.dashboard import DashboardResponse
from app.controllers.dashboard import dashboard_controller

router = APIRouter()

@router.get(
    "",
    summary="获取仪表盘数据",
    response_model=DashboardResponse
)
async def get_dashboard_data(
    current_user: User = DependAuth
):
    return await dashboard_controller.get_dashboard_data(current_user)