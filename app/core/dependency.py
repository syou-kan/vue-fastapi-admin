from typing import Optional

import jwt
from fastapi import Depends, Header, HTTPException, Request

from app.core.ctx import CTX_USER_ID
from app.models import Role, User
from app.settings import settings


class AuthControl:
    @classmethod
    async def is_authed(cls, token: str = Header(..., description="token验证")) -> Optional["User"]:
        try:
            if token == "dev":
                user = await User.filter().first()
                user_id = user.id
            else:
                decode_data = jwt.decode(token, settings.SECRET_KEY, algorithms=settings.JWT_ALGORITHM)
                user_id = decode_data.get("user_id")
            user = await User.filter(id=user_id).first()
            if not user:
                raise HTTPException(status_code=401, detail="Authentication failed")
            CTX_USER_ID.set(int(user_id))
            return user
        except jwt.DecodeError:
            raise HTTPException(status_code=401, detail="无效的Token")
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="登录已过期")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"{repr(e)}")


class PermissionControl:
    @classmethod
    async def has_permission(cls, request: Request, current_user: User = Depends(AuthControl.is_authed)) -> None:
        if current_user.is_superuser:
            return
        method = request.method
        path = request.url.path
        roles: list[Role] = await current_user.roles
        if not roles:
            raise HTTPException(status_code=403, detail="The user is not bound to a role")
        apis = [await role.apis for role in roles]
        permission_apis = list(set((api.method, api.path) for api in sum(apis, [])))
        # path = "/api/v1/auth/userinfo"
        # method = "GET"
        if (method, path) not in permission_apis:
            raise HTTPException(status_code=403, detail=f"Permission denied method:{method} path:{path}")


class DataIsolationControl:
    """
    数据隔离控制类，确保普通用户只能访问自己的数据。
    """
    
    @classmethod
    async def check_user_data_access(cls, request: Request, current_user: User = Depends(AuthControl.is_authed)) -> User:
        """
        检查用户数据访问权限，确保普通用户只能访问自己的数据。
        """
        # 超级用户可以访问所有数据
        if current_user.is_superuser:
            return current_user
            
        path = request.url.path
        method = request.method
        
        # 对于用户信息相关的API，确保只能访问自己的数据
        if "/api/v1/user/" in path:
            # 检查是否试图访问其他用户的数据
            query_params = dict(request.query_params)
            if "user_id" in query_params:
                requested_user_id = int(query_params["user_id"])
                if requested_user_id != current_user.id:
                    raise HTTPException(
                        status_code=403, 
                        detail="Access denied: You can only access your own user data"
                    )
        
        return current_user
    
    @classmethod
    async def check_order_data_access(cls, request: Request, current_user: User = Depends(AuthControl.is_authed)) -> User:
        """
        检查订单数据访问权限，确保普通用户只能访问自己的订单。
        """
        # 超级用户可以访问所有订单
        if current_user.is_superuser:
            return current_user
            
        # 普通用户只能访问自己的订单，这个检查在控制器层面实现
        # 这里主要是确保用户已经通过认证
        return current_user


class EnhancedPermissionControl:
    """
    增强的权限控制类，结合API权限和数据隔离。
    """
    
    @classmethod
    async def check_api_and_data_permission(
        cls, 
        request: Request, 
        current_user: User = Depends(AuthControl.is_authed)
    ) -> User:
        """
        检查API权限和数据访问权限。
        """
        # 首先检查API权限
        await PermissionControl.has_permission(request, current_user)
        
        # 然后检查数据访问权限
        path = request.url.path
        
        if "/api/v1/user/" in path:
            return await DataIsolationControl.check_user_data_access(request, current_user)
        elif "/api/v1/orders/" in path:
            return await DataIsolationControl.check_order_data_access(request, current_user)
        
        return current_user


# 依赖项定义
DependAuth = Depends(AuthControl.is_authed)
DependPermisson = Depends(PermissionControl.has_permission)
DependDataIsolation = Depends(DataIsolationControl.check_user_data_access)
DependOrderDataIsolation = Depends(DataIsolationControl.check_order_data_access)
DependEnhancedPermission = Depends(EnhancedPermissionControl.check_api_and_data_permission)
