from fastapi import APIRouter, Depends

from app.schemas.auditlog import AuditLogQueryParameters, PaginatedAuditLogResponse
from app.services.auditlog_service import AuditLogService

router = APIRouter()


@router.get(
    "/list",
    summary="查看操作日志",
    response_model=PaginatedAuditLogResponse,
)
async def get_audit_log_list(
    params: AuditLogQueryParameters = Depends(),
    audit_log_service: AuditLogService = Depends(),
):
    """
    获取审计日志列表
    """
    logs, total = await audit_log_service.get_audit_logs(params)
    return PaginatedAuditLogResponse(
        data=logs,
        total=total,
        page=params.page,
        page_size=params.page_size,
    )
