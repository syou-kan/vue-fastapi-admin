# enums.py
from enum import Enum, StrEnum


class EnumBase(Enum):
    @classmethod
    def get_member_values(cls):
        return [item.value for item in cls._member_map_.values()]

    @classmethod
    def get_member_names(cls):
        return [name for name in cls._member_names_]


class MethodType(StrEnum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"


# 添加用户类型枚举
class UserType(StrEnum):
    ADMIN = "admin"  # 管理员
    STAFF = "staff"  # 普通用户（后台管理用户）
    CUSTOMER = "customer"  # 客户账号