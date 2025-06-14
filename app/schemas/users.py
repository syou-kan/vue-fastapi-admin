# users.py
from datetime import datetime
from typing import List, Optional

from pydantic import EmailStr,  BaseModel, Field, validator
from typing import Optional

class BaseUser(BaseModel):
    id: int
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    last_login: Optional[datetime]
    roles: Optional[list] = []
    phone: Optional[str] = None  # 添加phone字段


class UserCreate(BaseModel):
    email: EmailStr = Field(example="admin@qq.com")
    username: str = Field(example="admin")
    password: str = Field(example="123456")
    phone: str = Field(example="13800000000", description="电话")  # 添加phone字段
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    role_ids: Optional[List[int]] = []
    dept_id: Optional[int] = Field(0, description="部门ID")
    user_type: Optional[str] = None  # 添加user_type字段

    def create_dict(self):
        return self.model_dump(exclude_unset=True, exclude={"role_ids"})


class RegisterUser(BaseModel):
    company_name: str = Field(..., description="公司名称")
    company_code: str = Field(..., description="统一社会信用代码")
    phone: str = Field(..., description="手机号")
    real_name: str = Field(..., description="姓名")
    password: str = Field(..., description="密码")
    confirm_password: str = Field(..., description="确认密码")
    email: Optional[str] = Field(None, description="邮箱")

    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('两次输入的密码不匹配')
        return v


class UserUpdate(BaseModel):
    id: int
    email: EmailStr
    username: str
    phone: str = Field(description="电话")  # 添加phone字段
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    role_ids: Optional[List[int]] = []
    dept_id: Optional[int] = 0
    user_type: Optional[str] = None  # 添加user_type字段


class UpdatePassword(BaseModel):
    old_password: str = Field(description="旧密码")
    new_password: str = Field(description="新密码")