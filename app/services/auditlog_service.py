from typing import Tuple, List

from tortoise.queryset import QuerySet

from app.models.admin import AuditLog
from app.schemas.auditlog import AuditLogQueryParameters, AuditLogEntry


class AuditLogService:
    """
    审计日志服务
    """

    async def get_audit_logs(
        self, params: AuditLogQueryParameters
    ) -> Tuple[List[AuditLogEntry], int]:
        """
        获取审计日志列表
        """
        query: QuerySet = AuditLog.all()

        if params.username:
            query = query.filter(username__icontains=params.username)
        if params.method:
            query = query.filter(method=params.method)
        if params.path:
            query = query.filter(path__icontains=params.path)
        if params.status_code:
            query = query.filter(status_code=params.status_code)
        if params.start_time:
            query = query.filter(created_at__gte=params.start_time)
        if params.end_time:
            query = query.filter(created_at__lte=params.end_time)

        total = await query.count()

        logs = (
            await query.order_by("-created_at")
            .offset((params.page - 1) * params.page_size)
            .limit(params.page_size)
        )

        return [AuditLogEntry.from_orm(log) for log in logs], total