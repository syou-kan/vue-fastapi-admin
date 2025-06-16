from fastapi import APIRouter

from .users import public_router, router

users_router = APIRouter()
users_router.include_router(router, tags=["用户模块"])

__all__ = ["users_router", "public_router"]
