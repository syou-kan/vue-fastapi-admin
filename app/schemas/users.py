from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class BaseUser(BaseModel):
    id: int
    username: Optional[str] = None
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    last_login: Optional[datetime]
    roles: Optional[list] = []
    phone_number: Optional[str] = None


class UserCreate(BaseModel):
    username: str
    password: str
    phone_number: Optional[str] = None
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    role_ids: Optional[List[int]] = []

    def create_dict(self):
        return self.model_dump(exclude_unset=True, exclude={"role_ids"})


class UserUpdate(BaseModel):
    id: int
    username: str
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    phone_number: Optional[str] = None
    role_ids: Optional[List[int]] = []


class UpdatePassword(BaseModel):
    old_password: str = Field(description="旧密码")
    new_password: str = Field(description="新密码")

class UserSimpleOut(BaseModel):
    id: int
    username: str
    alias: Optional[str] = None

    class Config:
        from_attributes = True
class UserRegister(BaseModel):
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")
    phone_number: str = Field(..., description="手机号码")
    company_name: str = Field(..., description="公司名称")
    
    def create_dict(self):
        return self.model_dump()
class UserSearchResultList(BaseModel):
    data: List[UserSimpleOut]
