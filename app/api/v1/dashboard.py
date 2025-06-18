from fastapi import APIRouter, Depends
from app.core.dependency import DependAuth, DependPermisson
from app.models.admin import User
from app.schemas.dashboard import DashboardResponse
from app.controllers.dashboard import dashboard_controller

router = APIRouter(tags=["仪表盘"])

@router.get(
    "",
    summary="获取仪表盘数据",
    response_model=DashboardResponse,
    dependencies=[DependPermisson]
)
async def get_dashboard_data(
    current_user: User = DependAuth
):
    """
    获取仪表盘数据。
    普通用户只能看到自己相关的数据，管理员可以看到全局数据。
    """
    return await dashboard_controller.get_dashboard_data(current_user)
