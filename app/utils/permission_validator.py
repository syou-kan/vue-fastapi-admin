import logging
from typing import List, Dict, Any
from tortoise.expressions import Q

from app.models.admin import Api, Role, User

logger = logging.getLogger(__name__)


class PermissionValidator:
    """
    权限配置验证器，用于验证权限配置是否正确。
    """
    
    @classmethod
    async def validate_user_role_permissions(cls) -> Dict[str, Any]:
        """
        验证普通用户角色的权限配置。
        """
        result = {
            "status": "success",
            "message": "权限配置验证通过",
            "details": {},
            "warnings": [],
            "errors": []
        }
        
        try:
            # 检查普通用户角色是否存在
            user_role = await Role.get_or_none(name="普通用户")
            if not user_role:
                result["errors"].append("普通用户角色不存在")
                result["status"] = "error"
                return result
            
            # 获取普通用户角色的API权限
            user_apis = await user_role.apis.all()
            api_permissions = [(api.method, api.path) for api in user_apis]
            
            # 定义期望的API权限
            expected_permissions = [
                ("GET", "/api/v1/base/userinfo"),
                ("POST", "/api/v1/base/update_password"),
                ("GET", "/api/v1/base/usermenu"),
                ("GET", "/api/v1/base/userapi"),
                ("GET", "/api/v1/dashboard"),
                ("GET", "/api/v1/user/get"),
                ("POST", "/api/v1/user/update"),
                ("GET", "/api/v1/orders/"),
                ("GET", "/api/v1/orders/{order_id}"),
                ("POST", "/api/v1/orders/"),
                ("PUT", "/api/v1/orders/{order_id}"),
            ]
            
            # 检查缺失的权限
            missing_permissions = []
            for expected in expected_permissions:
                if expected not in api_permissions:
                    missing_permissions.append(f"{expected[0]} {expected[1]}")
            
            # 检查多余的权限
            extra_permissions = []
            for actual in api_permissions:
                if actual not in expected_permissions:
                    extra_permissions.append(f"{actual[0]} {actual[1]}")
            
            # 更新结果
            result["details"] = {
                "role_name": user_role.name,
                "total_apis": len(user_apis),
                "expected_apis": len(expected_permissions),
                "actual_permissions": [f"{p[0]} {p[1]}" for p in api_permissions],
                "expected_permissions": [f"{p[0]} {p[1]}" for p in expected_permissions]
            }
            
            if missing_permissions:
                result["errors"].extend([f"缺失权限: {p}" for p in missing_permissions])
                result["status"] = "error"
            
            if extra_permissions:
                result["warnings"].extend([f"多余权限: {p}" for p in extra_permissions])
                if result["status"] != "error":
                    result["status"] = "warning"
            
            if result["status"] == "success":
                result["message"] = f"普通用户角色权限配置正确，共有 {len(user_apis)} 个API权限"
            
        except Exception as e:
            logger.error(f"权限验证过程中发生错误: {e}")
            result["status"] = "error"
            result["message"] = f"权限验证失败: {str(e)}"
            result["errors"].append(str(e))
        
        return result
    
    @classmethod
    async def validate_admin_role_permissions(cls) -> Dict[str, Any]:
        """
        验证管理员角色的权限配置。
        """
        result = {
            "status": "success",
            "message": "管理员权限配置验证通过",
            "details": {},
            "warnings": [],
            "errors": []
        }
        
        try:
            # 检查管理员角色是否存在
            admin_role = await Role.get_or_none(name="管理员")
            if not admin_role:
                result["errors"].append("管理员角色不存在")
                result["status"] = "error"
                return result
            
            # 获取所有API和管理员角色的API权限
            all_apis = await Api.all()
            admin_apis = await admin_role.apis.all()
            
            result["details"] = {
                "role_name": admin_role.name,
                "total_apis_in_system": len(all_apis),
                "admin_apis": len(admin_apis)
            }
            
            # 管理员应该拥有所有API权限
            if len(admin_apis) != len(all_apis):
                result["errors"].append(
                    f"管理员权限不完整: 系统共有 {len(all_apis)} 个API，管理员只有 {len(admin_apis)} 个权限"
                )
                result["status"] = "error"
            else:
                result["message"] = f"管理员角色权限配置正确，拥有全部 {len(admin_apis)} 个API权限"
            
        except Exception as e:
            logger.error(f"管理员权限验证过程中发生错误: {e}")
            result["status"] = "error"
            result["message"] = f"管理员权限验证失败: {str(e)}"
            result["errors"].append(str(e))
        
        return result
    
    @classmethod
    async def validate_menu_permissions(cls) -> Dict[str, Any]:
        """
        验证菜单权限配置。
        """
        result = {
            "status": "success",
            "message": "菜单权限配置验证通过",
            "details": {},
            "warnings": [],
            "errors": []
        }
        
        try:
            from app.models.admin import Menu
            
            # 检查普通用户角色的菜单权限
            user_role = await Role.get_or_none(name="普通用户")
            if user_role:
                user_menus = await user_role.menus.all()
                expected_menu_names = ["仪表盘", "订单管理", "个人中心"]
                actual_menu_names = [menu.name for menu in user_menus]
                
                missing_menus = [name for name in expected_menu_names if name not in actual_menu_names]
                extra_menus = [name for name in actual_menu_names if name not in expected_menu_names]
                
                result["details"]["user_role_menus"] = {
                    "expected": expected_menu_names,
                    "actual": actual_menu_names,
                    "missing": missing_menus,
                    "extra": extra_menus
                }
                
                if missing_menus:
                    result["errors"].extend([f"普通用户缺失菜单: {menu}" for menu in missing_menus])
                    result["status"] = "error"
                
                if extra_menus:
                    result["warnings"].extend([f"普通用户多余菜单: {menu}" for menu in extra_menus])
                    if result["status"] != "error":
                        result["status"] = "warning"
            
            # 检查管理员角色的菜单权限
            admin_role = await Role.get_or_none(name="管理员")
            if admin_role:
                admin_menus = await admin_role.menus.all()
                all_menus = await Menu.all()
                
                result["details"]["admin_role_menus"] = {
                    "total_menus_in_system": len(all_menus),
                    "admin_menus": len(admin_menus)
                }
                
                if len(admin_menus) != len(all_menus):
                    result["errors"].append(
                        f"管理员菜单权限不完整: 系统共有 {len(all_menus)} 个菜单，管理员只有 {len(admin_menus)} 个权限"
                    )
                    result["status"] = "error"
            
        except Exception as e:
            logger.error(f"菜单权限验证过程中发生错误: {e}")
            result["status"] = "error"
            result["message"] = f"菜单权限验证失败: {str(e)}"
            result["errors"].append(str(e))
        
        return result
    
    @classmethod
    async def validate_all_permissions(cls) -> Dict[str, Any]:
        """
        验证所有权限配置。
        """
        logger.info("开始验证权限配置...")
        
        user_result = await cls.validate_user_role_permissions()
        admin_result = await cls.validate_admin_role_permissions()
        menu_result = await cls.validate_menu_permissions()
        
        overall_result = {
            "status": "success",
            "message": "所有权限配置验证通过",
            "user_role_validation": user_result,
            "admin_role_validation": admin_result,
            "menu_validation": menu_result,
            "summary": {
                "total_errors": 0,
                "total_warnings": 0
            }
        }
        
        # 统计错误和警告
        for validation in [user_result, admin_result, menu_result]:
            overall_result["summary"]["total_errors"] += len(validation.get("errors", []))
            overall_result["summary"]["total_warnings"] += len(validation.get("warnings", []))
        
        # 确定整体状态
        if overall_result["summary"]["total_errors"] > 0:
            overall_result["status"] = "error"
            overall_result["message"] = f"权限配置验证失败，发现 {overall_result['summary']['total_errors']} 个错误"
        elif overall_result["summary"]["total_warnings"] > 0:
            overall_result["status"] = "warning"
            overall_result["message"] = f"权限配置基本正确，但有 {overall_result['summary']['total_warnings']} 个警告"
        
        logger.info(f"权限配置验证完成: {overall_result['status']} - {overall_result['message']}")
        return overall_result


# 创建验证器实例
permission_validator = PermissionValidator()
