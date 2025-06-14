from pydantic import BaseModel


class AdminWorkbenchData(BaseModel):
    """
    Admin workbench data
    """

    user_count: int
    role_count: int
    menu_count: int
    api_count: int


class UserWorkbenchData(BaseModel):
    """
    User workbench data
    """

    task_count: int
    message_count: int