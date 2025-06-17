from datetime import datetime

from pydantic import BaseModel, Field


class CredentialsSchema(BaseModel):
    phone_number: str = Field(..., description="手机号码")
    password: str = Field(..., description="密码")


class JWTOut(BaseModel):
    access_token: str
    username: str


class JWTPayload(BaseModel):
    user_id: int
    username: str
    is_superuser: bool
    exp: datetime
