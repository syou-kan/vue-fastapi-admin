from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.schemas.base import Success


class AuditLogQueryParameters(BaseModel):
    """
    审计日志查询参数
    """
    username: Optional[str] = Field(None, description="用户名")
    method: Optional[str] = Field(None, description="请求方法")
    path: Optional[str] = Field(None, description="请求路径")
    status_code: Optional[int] = Field(None, description="响应状态码")
    start_time: Optional[datetime] = Field(None, description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")
    page: int = Field(1, description="页码")
    page_size: int = Field(20, description="每页数量")


class AuditLogEntry(BaseModel):
    """
    审计日志条目
    """
    id: int
    username: str
    ip_address: str
    method: str
    path: str
    status_code: int
    response_time: float
    created_at: datetime

    class Config:
        from_attributes = True


class PaginatedAuditLogResponse(BaseModel):
    """
    分页审计日志响应
    """
    code: int = 200
    msg: str = "Success"
    data: List[AuditLogEntry]
    total: int
    page: int
    page_size: int