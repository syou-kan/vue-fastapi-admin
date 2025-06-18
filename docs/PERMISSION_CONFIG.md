# 普通用户权限配置说明

## 概述

本文档说明了根据权限方案设计对系统进行的权限配置修改，实现了普通用户的精确权限控制和数据隔离机制。

## 修改内容

### 1. 初始化脚本修改 (`app/core/init_app.py`)

#### 主要变更：
- **新增 `configure_user_role_permissions()` 函数**：为普通用户角色配置精确的API权限
- **新增 `init_user_specific_apis()` 函数**：确保用户相关API正确注册
- **修改 `init_roles()` 函数**：优化角色权限分配逻辑
- **新增菜单初始化**：为普通用户添加仪表盘、订单管理、个人中心菜单

#### 普通用户API权限配置：
```python
user_api_permissions = [
    # 基础模块 - 个人信息相关
    {"method": "GET", "path": "/api/v1/base/userinfo"},
    {"method": "POST", "path": "/api/v1/base/update_password"},
    {"method": "GET", "path": "/api/v1/base/usermenu"},
    {"method": "GET", "path": "/api/v1/base/userapi"},
    
    # 仪表盘
    {"method": "GET", "path": "/api/v1/dashboard"},
    
    # 用户管理 - 仅限查看和修改自己的信息
    {"method": "GET", "path": "/api/v1/user/get"},
    {"method": "POST", "path": "/api/v1/user/update"},
    
    # 订单管理 - 仅限操作自己的订单
    {"method": "GET", "path": "/api/v1/orders/"},
    {"method": "GET", "path": "/api/v1/orders/{order_id}"},
    {"method": "POST", "path": "/api/v1/orders/"},
    {"method": "PUT", "path": "/api/v1/orders/{order_id}"},
]
```

### 2. 权限依赖项增强 (`app/core/dependency.py`)

#### 新增功能：
- **`DataIsolationControl` 类**：实现数据隔离控制
- **`EnhancedPermissionControl` 类**：结合API权限和数据隔离
- **新增依赖项**：
  - `DependDataIsolation`：用户数据隔离
  - `DependOrderDataIsolation`：订单数据隔离
  - `DependEnhancedPermission`：增强权限控制

#### 数据隔离机制：
- 普通用户只能访问自己的用户信息
- 普通用户只能操作自己的订单
- 超级用户可以访问所有数据

### 3. API路由修改

#### 用户API (`app/api/v1/users/users.py`)：
- **数据隔离**：普通用户只能查看/修改自己的信息
- **字段限制**：普通用户不能修改敏感字段（`is_superuser`, `is_active`, `role_ids`）
- **权限验证**：使用 `DependEnhancedPermission` 进行增强权限检查

#### 订单API (`app/api/v1/orders.py`)：
- **数据隔离**：普通用户只能操作自己的订单
- **自动关联**：普通用户创建的订单自动关联到当前用户
- **删除限制**：普通用户不能删除订单（无DELETE权限）

#### 仪表盘API (`app/api/v1/dashboard.py`)：
- **权限验证**：添加 `DependPermisson` 权限检查
- **数据过滤**：普通用户只能看到自己相关的数据

### 4. 权限验证工具 (`app/utils/permission_validator.py`)

#### 功能：
- **权限配置验证**：验证普通用户和管理员的权限配置是否正确
- **菜单权限检查**：验证菜单权限分配
- **详细报告**：提供详细的验证结果和错误信息

#### 使用方法：
```python
from app.utils.permission_validator import permission_validator

# 验证所有权限配置
result = await permission_validator.validate_all_permissions()
print(result)
```

### 5. 测试脚本 (`tests/test_permission_config.py`)

#### 功能：
- 自动化权限配置验证
- 详细的测试报告
- 错误和警告统计

#### 运行方法：
```bash
python tests/test_permission_config.py
```

## 权限配置详情

### 普通用户权限

| API路径 | 方法 | 功能描述 | 数据隔离 |
|---------|------|----------|----------|
| `/api/v1/base/userinfo` | GET | 查看个人信息 | ✅ 仅自己 |
| `/api/v1/base/update_password` | POST | 修改密码 | ✅ 仅自己 |
| `/api/v1/base/usermenu` | GET | 获取菜单 | ✅ 角色菜单 |
| `/api/v1/base/userapi` | GET | 获取API权限 | ✅ 角色权限 |
| `/api/v1/dashboard` | GET | 访问仪表盘 | ✅ 个人数据 |
| `/api/v1/user/get` | GET | 查看用户详情 | ✅ 仅自己 |
| `/api/v1/user/update` | POST | 修改用户信息 | ✅ 仅自己 |
| `/api/v1/orders/` | GET | 查看订单列表 | ✅ 仅自己 |
| `/api/v1/orders/{order_id}` | GET | 查看订单详情 | ✅ 仅自己 |
| `/api/v1/orders/` | POST | 创建订单 | ✅ 自动关联 |
| `/api/v1/orders/{order_id}` | PUT | 修改订单 | ✅ 仅自己 |

### 普通用户菜单权限

- **仪表盘**：个人数据概览
- **订单管理**：管理个人订单
- **个人中心**：个人信息管理

### 数据隔离机制

1. **用户数据隔离**：
   - 普通用户只能查看和修改自己的用户信息
   - 不能访问其他用户的数据
   - 不能修改敏感字段

2. **订单数据隔离**：
   - 普通用户只能看到自己的订单
   - 创建的订单自动关联到当前用户
   - 不能查看或修改其他用户的订单

3. **菜单数据隔离**：
   - 普通用户只能看到分配给其角色的菜单
   - 不能访问管理功能菜单

## 安全特性

### 1. API权限控制
- 基于角色的API访问控制
- 精确的权限配置，最小权限原则
- 自动权限验证

### 2. 数据隔离
- 用户级别的数据隔离
- 自动数据过滤
- 防止越权访问

### 3. 字段级别控制
- 普通用户不能修改敏感字段
- 自动字段过滤
- 权限升级保护

## 部署和验证

### 1. 初始化权限配置
```bash
# 启动应用时会自动执行权限初始化
python run.py
```

### 2. 验证权限配置
```bash
# 运行权限配置测试
python tests/test_permission_config.py
```

### 3. 检查日志
```bash
# 查看权限配置日志
tail -f logs/conport.log | grep "权限"
```

## 注意事项

1. **数据库迁移**：首次部署时会自动创建角色和权限配置
2. **现有用户**：现有普通用户会自动获得新的权限配置
3. **管理员权限**：管理员权限保持不变，拥有所有API和菜单权限
4. **权限更新**：每次启动时会自动同步权限配置

## 故障排除

### 常见问题

1. **普通用户无法访问某个API**
   - 检查API是否在权限配置列表中
   - 运行权限验证脚本检查配置

2. **数据隔离不生效**
   - 检查API路由是否使用了正确的依赖项
   - 确认控制器层面的数据过滤逻辑

3. **菜单不显示**
   - 检查角色菜单权限配置
   - 确认前端权限指令配置

### 调试命令

```bash
# 验证权限配置
python tests/test_permission_config.py

# 检查数据库中的权限配置
# 可以通过数据库管理工具查看 role、api、menu 等表
```

## 更新历史

- **v1.0.0**：初始权限配置实现
  - 普通用户API权限配置
  - 数据隔离机制
  - 权限验证工具
  - 测试脚本
