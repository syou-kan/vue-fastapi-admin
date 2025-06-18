# API 接口参考文档

## 概述

本文档详细说明了 Vue FastAPI Admin 系统的 API 接口，特别是普通用户可访问的 API 权限和使用方法。

## 基础信息

### API 基础地址
- **开发环境**：`http://localhost:8000/api`
- **生产环境**：`https://your-domain.com/api`

### 认证方式
所有 API 请求都需要在请求头中包含 JWT Token：

```http
Authorization: Bearer <your_jwt_token>
Content-Type: application/json
```

### 响应格式

#### 成功响应
```json
{
  "code": 200,
  "message": "success",
  "data": {
    // 响应数据
  }
}
```

#### 错误响应
```json
{
  "code": 400,
  "message": "错误描述",
  "detail": "详细错误信息"
}
```

### 状态码说明

| 状态码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 401 | 未授权（Token 无效或过期）|
| 403 | 权限不足 |
| 404 | 资源不存在 |
| 422 | 数据验证失败 |
| 500 | 服务器内部错误 |

## 普通用户可访问的 API

### 1. 基础信息 API

#### 1.1 获取个人信息

**接口地址**：`GET /api/v1/base/userinfo`

**权限要求**：普通用户

**请求示例**：
```http
GET /api/v1/base/userinfo
Authorization: Bearer <token>
```

**响应示例**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "username": "user123",
    "email": "user@example.com",
    "phone": "138****1234",
    "avatar": "/static/avatars/default.png",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00",
    "roles": [
      {
        "id": 2,
        "name": "普通用户",
        "description": "普通用户角色"
      }
    ]
  }
}
```

#### 1.2 修改密码

**接口地址**：`POST /api/v1/base/update_password`

**权限要求**：普通用户

**请求参数**：
```json
{
  "old_password": "旧密码",
  "new_password": "新密码"
}
```

**请求示例**：
```http
POST /api/v1/base/update_password
Authorization: Bearer <token>
Content-Type: application/json

{
  "old_password": "old123456",
  "new_password": "new123456"
}
```

**响应示例**：
```json
{
  "code": 200,
  "message": "密码修改成功"
}
```

#### 1.3 获取用户菜单

**接口地址**：`GET /api/v1/base/usermenu`

**权限要求**：普通用户

**请求示例**：
```http
GET /api/v1/base/usermenu
Authorization: Bearer <token>
```

**响应示例**：
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": 1,
      "title": "仪表盘",
      "path": "/dashboard",
      "icon": "dashboard",
      "component": "dashboard/index",
      "sort": 1
    },
    {
      "id": 2,
      "title": "订单管理",
      "path": "/orders",
      "icon": "order",
      "component": "order/index",
      "sort": 2
    },
    {
      "id": 3,
      "title": "个人中心",
      "path": "/profile",
      "icon": "user",
      "component": "profile/index",
      "sort": 3
    }
  ]
}
```

#### 1.4 获取用户 API 权限

**接口地址**：`GET /api/v1/base/userapi`

**权限要求**：普通用户

**请求示例**：
```http
GET /api/v1/base/userapi
Authorization: Bearer <token>
```

**响应示例**：
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "method": "GET",
      "path": "/api/v1/base/userinfo",
      "description": "获取个人信息"
    },
    {
      "method": "POST",
      "path": "/api/v1/base/update_password",
      "description": "修改密码"
    },
    {
      "method": "GET",
      "path": "/api/v1/orders/",
      "description": "查看订单列表"
    }
  ]
}
```

### 2. 仪表盘 API

#### 2.1 获取仪表盘数据

**接口地址**：`GET /api/v1/dashboard`

**权限要求**：普通用户

**请求示例**：
```http
GET /api/v1/dashboard
Authorization: Bearer <token>
```

**响应示例**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "user_stats": {
      "total_orders": 15,
      "pending_orders": 3,
      "completed_orders": 12,
      "total_amount": 25600.00
    },
    "recent_orders": [
      {
        "id": 1,
        "title": "订单标题",
        "amount": 1200.00,
        "status": "已完成",
        "created_at": "2024-01-15T10:30:00"
      }
    ],
    "monthly_stats": {
      "current_month": 8,
      "last_month": 7,
      "growth_rate": 14.3
    }
  }
}
```

### 3. 用户管理 API

#### 3.1 获取用户详情

**接口地址**：`GET /api/v1/user/get`

**权限要求**：普通用户（仅能查看自己）

**请求参数**：
- `user_id`（可选）：用户ID，普通用户只能查看自己的信息

**请求示例**：
```http
GET /api/v1/user/get?user_id=1
Authorization: Bearer <token>
```

**响应示例**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "username": "user123",
    "email": "user@example.com",
    "phone": "13800138000",
    "avatar": "/static/avatars/user123.png",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-15T10:30:00"
  }
}
```

#### 3.2 更新用户信息

**接口地址**：`POST /api/v1/user/update`

**权限要求**：普通用户（仅能修改自己）

**请求参数**：
```json
{
  "email": "新邮箱地址",
  "phone": "新手机号",
  "avatar": "新头像地址"
}
```

**请求示例**：
```http
POST /api/v1/user/update
Authorization: Bearer <token>
Content-Type: application/json

{
  "email": "newemail@example.com",
  "phone": "13900139000",
  "avatar": "/static/avatars/new_avatar.png"
}
```

**响应示例**：
```json
{
  "code": 200,
  "message": "用户信息更新成功",
  "data": {
    "id": 1,
    "username": "user123",
    "email": "newemail@example.com",
    "phone": "13900139000",
    "avatar": "/static/avatars/new_avatar.png",
    "updated_at": "2024-01-15T15:30:00"
  }
}
```

**注意事项**：
- 普通用户不能修改以下字段：`username`、`is_superuser`、`is_active`、`role_ids`
- 邮箱和手机号需要符合格式要求
- 头像地址需要是有效的图片链接

### 4. 订单管理 API

#### 4.1 获取订单列表

**接口地址**：`GET /api/v1/orders/`

**权限要求**：普通用户（仅能查看自己的订单）

**请求参数**：
- `page`（可选）：页码，默认为 1
- `size`（可选）：每页数量，默认为 10
- `status`（可选）：订单状态筛选
- `search`（可选）：搜索关键词

**请求示例**：
```http
GET /api/v1/orders/?page=1&size=10&status=pending
Authorization: Bearer <token>
```

**响应示例**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "title": "订单标题",
        "description": "订单描述",
        "amount": 1200.00,
        "status": "pending",
        "user_id": 1,
        "created_at": "2024-01-15T10:30:00",
        "updated_at": "2024-01-15T10:30:00"
      }
    ],
    "total": 15,
    "page": 1,
    "size": 10,
    "pages": 2
  }
}
```

#### 4.2 获取订单详情

**接口地址**：`GET /api/v1/orders/{order_id}`

**权限要求**：普通用户（仅能查看自己的订单）

**请求示例**：
```http
GET /api/v1/orders/1
Authorization: Bearer <token>
```

**响应示例**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "title": "订单标题",
    "description": "详细的订单描述信息",
    "amount": 1200.00,
    "status": "pending",
    "user_id": 1,
    "created_at": "2024-01-15T10:30:00",
    "updated_at": "2024-01-15T10:30:00",
    "status_history": [
      {
        "status": "pending",
        "timestamp": "2024-01-15T10:30:00",
        "note": "订单已创建"
      }
    ]
  }
}
```

#### 4.3 创建订单

**接口地址**：`POST /api/v1/orders/`

**权限要求**：普通用户

**请求参数**：
```json
{
  "title": "订单标题",
  "description": "订单描述",
  "amount": 1200.00
}
```

**请求示例**：
```http
POST /api/v1/orders/
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "新订单",
  "description": "这是一个新的订单",
  "amount": 1500.00
}
```

**响应示例**：
```json
{
  "code": 201,
  "message": "订单创建成功",
  "data": {
    "id": 2,
    "title": "新订单",
    "description": "这是一个新的订单",
    "amount": 1500.00,
    "status": "pending",
    "user_id": 1,
    "created_at": "2024-01-15T15:30:00",
    "updated_at": "2024-01-15T15:30:00"
  }
}
```

**注意事项**：
- 订单会自动关联到当前登录用户
- 订单状态默认为 "pending"
- 金额必须为正数

#### 4.4 更新订单

**接口地址**：`PUT /api/v1/orders/{order_id}`

**权限要求**：普通用户（仅能修改自己的订单）

**请求参数**：
```json
{
  "title": "更新后的标题",
  "description": "更新后的描述",
  "amount": 1800.00
}
```

**请求示例**：
```http
PUT /api/v1/orders/1
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "更新后的订单标题",
  "description": "更新后的订单描述",
  "amount": 1800.00
}
```

**响应示例**：
```json
{
  "code": 200,
  "message": "订单更新成功",
  "data": {
    "id": 1,
    "title": "更新后的订单标题",
    "description": "更新后的订单描述",
    "amount": 1800.00,
    "status": "pending",
    "user_id": 1,
    "created_at": "2024-01-15T10:30:00",
    "updated_at": "2024-01-15T16:00:00"
  }
}
```

**注意事项**：
- 只能修改自己创建的订单
- 已完成或已取消的订单可能不允许修改
- 某些字段可能因订单状态而不可编辑

## 数据模型

### 用户模型
```json
{
  "id": "用户ID",
  "username": "用户名",
  "email": "邮箱地址",
  "phone": "手机号",
  "avatar": "头像地址",
  "is_active": "是否激活",
  "is_superuser": "是否超级用户",
  "created_at": "创建时间",
  "updated_at": "更新时间",
  "roles": "用户角色列表"
}
```

### 订单模型
```json
{
  "id": "订单ID",
  "title": "订单标题",
  "description": "订单描述",
  "amount": "订单金额",
  "status": "订单状态",
  "user_id": "用户ID",
  "created_at": "创建时间",
  "updated_at": "更新时间"
}
```

### 订单状态枚举
- `pending`：待处理
- `processing`：处理中
- `completed`：已完成
- `cancelled`：已取消

## 错误处理

### 常见错误码

#### 401 未授权
```json
{
  "code": 401,
  "message": "Unauthorized",
  "detail": "Token 无效或已过期"
}
```

#### 403 权限不足
```json
{
  "code": 403,
  "message": "Forbidden",
  "detail": "您没有权限访问此资源"
}
```

#### 404 资源不存在
```json
{
  "code": 404,
  "message": "Not Found",
  "detail": "请求的资源不存在"
}
```

#### 422 数据验证失败
```json
{
  "code": 422,
  "message": "Validation Error",
  "detail": [
    {
      "field": "email",
      "message": "邮箱格式不正确"
    }
  ]
}
```

## 使用示例

### JavaScript/Axios 示例

```javascript
// 设置基础配置
const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json'
  }
});

// 添加请求拦截器（自动添加 Token）
api.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// 获取个人信息
const getUserInfo = async () => {
  try {
    const response = await api.get('/v1/base/userinfo');
    return response.data;
  } catch (error) {
    console.error('获取用户信息失败:', error.response.data);
  }
};

// 创建订单
const createOrder = async (orderData) => {
  try {
    const response = await api.post('/v1/orders/', orderData);
    return response.data;
  } catch (error) {
    console.error('创建订单失败:', error.response.data);
  }
};

// 获取订单列表
const getOrders = async (params = {}) => {
  try {
    const response = await api.get('/v1/orders/', { params });
    return response.data;
  } catch (error) {
    console.error('获取订单列表失败:', error.response.data);
  }
};
```

### Python/Requests 示例

```python
import requests
import json

class APIClient:
    def __init__(self, base_url, token):
        self.base_url = base_url
        self.headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
    
    def get_user_info(self):
        """获取个人信息"""
        response = requests.get(
            f'{self.base_url}/v1/base/userinfo',
            headers=self.headers
        )
        return response.json()
    
    def create_order(self, order_data):
        """创建订单"""
        response = requests.post(
            f'{self.base_url}/v1/orders/',
            headers=self.headers,
            data=json.dumps(order_data)
        )
        return response.json()
    
    def get_orders(self, params=None):
        """获取订单列表"""
        response = requests.get(
            f'{self.base_url}/v1/orders/',
            headers=self.headers,
            params=params
        )
        return response.json()

# 使用示例
client = APIClient('http://localhost:8000/api', 'your_token_here')

# 获取用户信息
user_info = client.get_user_info()
print(user_info)

# 创建订单
order_data = {
    'title': '测试订单',
    'description': '这是一个测试订单',
    'amount': 1000.00
}
result = client.create_order(order_data)
print(result)
```

## 限制和注意事项

### 1. 数据隔离
- 普通用户只能访问自己的数据
- 无法查看或修改其他用户的信息
- 订单数据严格按用户隔离

### 2. 权限限制
- 普通用户无法访问管理功能 API
- 无法删除订单（只能创建和修改）
- 无法修改敏感用户字段

### 3. 请求限制
- API 请求频率限制：每分钟最多 60 次
- 文件上传大小限制：最大 10MB
- 请求超时时间：30 秒

### 4. 数据验证
- 所有输入数据都会进行严格验证
- 邮箱和手机号必须符合格式要求
- 金额字段必须为正数

## 总结

本 API 参考文档涵盖了普通用户可访问的所有接口：

1. **基础信息 API**：个人信息、密码修改、菜单权限
2. **仪表盘 API**：个人数据统计和概览
3. **用户管理 API**：查看和修改个人信息
4. **订单管理 API**：订单的增删改查操作

所有 API 都实现了严格的权限控制和数据隔离，确保用户只能访问自己的数据。开发者可以根据本文档快速集成和使用这些 API 接口。