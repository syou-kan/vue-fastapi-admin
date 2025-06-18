import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tortoise import Tortoise
from app.settings.config import settings
from app.utils.permission_validator import permission_validator
from app.log import logger


async def test_permission_configuration():
    """
    测试权限配置是否正确。
    """
    try:
        # 初始化数据库连接
        await Tortoise.init(config=settings.TORTOISE_ORM)
        
        print("=" * 60)
        print("权限配置验证测试")
        print("=" * 60)
        
        # 执行权限验证
        result = await permission_validator.validate_all_permissions()
        
        # 打印验证结果
        print(f"\n整体状态: {result['status'].upper()}")
        print(f"消息: {result['message']}")
        print(f"错误数量: {result['summary']['total_errors']}")
        print(f"警告数量: {result['summary']['total_warnings']}")
        
        # 打印普通用户角色验证结果
        print("\n" + "="*40)
        print("普通用户角色验证结果")
        print("="*40)
        user_validation = result['user_role_validation']
        print(f"状态: {user_validation['status'].upper()}")
        print(f"消息: {user_validation['message']}")
        
        if user_validation['details']:
            details = user_validation['details']
            print(f"角色名称: {details.get('role_name', 'N/A')}")
            print(f"实际API数量: {details.get('total_apis', 0)}")
            print(f"期望API数量: {details.get('expected_apis', 0)}")
            
            if 'actual_permissions' in details:
                print("\n实际权限:")
                for perm in details['actual_permissions']:
                    print(f"  - {perm}")
        
        if user_validation['errors']:
            print("\n错误:")
            for error in user_validation['errors']:
                print(f"  ❌ {error}")
        
        if user_validation['warnings']:
            print("\n警告:")
            for warning in user_validation['warnings']:
                print(f"  ⚠️ {warning}")
        
        # 打印管理员角色验证结果
        print("\n" + "="*40)
        print("管理员角色验证结果")
        print("="*40)
        admin_validation = result['admin_role_validation']
        print(f"状态: {admin_validation['status'].upper()}")
        print(f"消息: {admin_validation['message']}")
        
        if admin_validation['details']:
            details = admin_validation['details']
            print(f"角色名称: {details.get('role_name', 'N/A')}")
            print(f"系统API总数: {details.get('total_apis_in_system', 0)}")
            print(f"管理员API数量: {details.get('admin_apis', 0)}")
        
        if admin_validation['errors']:
            print("\n错误:")
            for error in admin_validation['errors']:
                print(f"  ❌ {error}")
        
        # 打印菜单权限验证结果
        print("\n" + "="*40)
        print("菜单权限验证结果")
        print("="*40)
        menu_validation = result['menu_validation']
        print(f"状态: {menu_validation['status'].upper()}")
        print(f"消息: {menu_validation['message']}")
        
        if menu_validation['details']:
            details = menu_validation['details']
            
            if 'user_role_menus' in details:
                user_menus = details['user_role_menus']
                print(f"\n普通用户菜单:")
                print(f"  期望菜单: {user_menus.get('expected', [])}")
                print(f"  实际菜单: {user_menus.get('actual', [])}")
                if user_menus.get('missing'):
                    print(f"  缺失菜单: {user_menus['missing']}")
                if user_menus.get('extra'):
                    print(f"  多余菜单: {user_menus['extra']}")
            
            if 'admin_role_menus' in details:
                admin_menus = details['admin_role_menus']
                print(f"\n管理员菜单:")
                print(f"  系统菜单总数: {admin_menus.get('total_menus_in_system', 0)}")
                print(f"  管理员菜单数量: {admin_menus.get('admin_menus', 0)}")
        
        if menu_validation['errors']:
            print("\n错误:")
            for error in menu_validation['errors']:
                print(f"  ❌ {error}")
        
        if menu_validation['warnings']:
            print("\n警告:")
            for warning in menu_validation['warnings']:
                print(f"  ⚠️ {warning}")
        
        print("\n" + "="*60)
        
        # 根据验证结果返回适当的退出码
        if result['status'] == 'error':
            print("❌ 权限配置验证失败！")
            return 1
        elif result['status'] == 'warning':
            print("⚠️ 权限配置基本正确，但存在警告。")
            return 0
        else:
            print("✅ 权限配置验证通过！")
            return 0
            
    except Exception as e:
        logger.error(f"权限配置测试过程中发生错误: {e}")
        print(f"❌ 测试失败: {e}")
        return 1
    finally:
        # 关闭数据库连接
        await Tortoise.close_connections()


if __name__ == "__main__":
    exit_code = asyncio.run(test_permission_configuration())
    sys.exit(exit_code)
