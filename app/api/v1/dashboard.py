from fastapi import APIRouter, Depends

from app.controllers.dashboard import dashboard_controller
from app.core.dependency import DependAuth
from app.schemas.base import Success
from app.schemas.users import BaseUser

router = APIRouter()


@router.get(
    "/workbench",
    summary="获取工作台数据",
    tags=["仪表盘"],
)
async def get_workbench_data(
    current_user: BaseUser = DependAuth,
):
    """
    根据用户角色返回不同的工作台数据
    """
    data = await dashboard_controller.get_workbench_data(current_user)
    return Success(data=data.model_dump())