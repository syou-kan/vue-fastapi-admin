# 故障排除指南

## 概述

本指南提供了 Vue FastAPI Admin 系统常见问题的诊断和解决方案，特别针对普通用户权限配置相关的问题。

## 快速诊断

### 系统健康检查

```bash
# 1. 检查服务状态
curl -X GET http://localhost:8000/api/v1/base/health

# 2. 检查数据库连接
python -c "from app.core.init_app import init_db; init_db()"

# 3. 验证权限配置
python tests/test_permission_config.py

# 4. 查看系统日志
tail -f logs/conport.log
```

### 常见错误代码

| 错误代码 | 含义 | 常见原因 |
|----------|------|----------|
| 401 | 未授权 | Token 过期或无效 |
| 403 | 权限不足 | 用户权限不够 |
| 404 | 资源不存在 | API 路径错误或资源被删除 |
| 422 | 数据验证失败 | 请求参数格式错误 |
| 500 | 服务器内部错误 | 代码异常或数据库问题 |

## 权限相关问题

### 1. 普通用户无法访问功能

#### 问题描述
普通用户登录后看不到某些菜单或无法访问某些 API。

#### 诊断步骤

```bash
# 1. 检查用户角色
python -c "
from app.models.admin import User, Role
from app.core.init_app import get_db
db = next(get_db())
user = db.query(User).filter(User.username == 'your_username').first()
print(f'用户角色: {[role.name for role in user.roles]}')
"

# 2. 检查角色权限
python -c "
from app.models.admin import Role, Api
from app.core.init_app import get_db
db = next(get_db())
role = db.query(Role).filter(Role.name == '普通用户').first()
print(f'角色权限: {[api.path for api in role.apis]}')
"

# 3. 运行权限验证
python tests/test_permission_config.py
```

#### 解决方案

1. **重新初始化权限**
```bash
python -c "
from app.core.init_app import configure_user_role_permissions
import asyncio
asyncio.run(configure_user_role_permissions())
"
```

2. **手动分配权限**
```python
# 在 Python 控制台中执行
from app.models.admin import User, Role, Api
from app.core.init_app import get_db

db = next(get_db())
user = db.query(User).filter(User.username == 'username').first()
role = db.query(Role).filter(Role.name == '普通用户').first()

if role not in user.roles:
    user.roles.append(role)
    db.commit()
```

3. **检查前端权限配置**
```javascript
// 检查前端权限存储
console.log(localStorage.getItem('user_permissions'));
console.log(localStorage.getItem('user_menus'));
```

### 2. 数据隔离不生效

#### 问题描述
普通用户能看到其他用户的数据。

#### 诊断步骤

```bash
# 1. 检查 API 路由配置
grep -r "DependDataIsolation" app/api/
grep -r "DependEnhancedPermission" app/api/

# 2. 测试数据隔离
curl -H "Authorization: Bearer YOUR_TOKEN" \
     -X GET http://localhost:8000/api/v1/orders/
```

#### 解决方案

1. **检查依赖项配置**
```python
# 确保 API 路由使用了正确的依赖项
@router.get("/")
async def get_orders(
    current_user: User = Depends(DependEnhancedPermission("orders:read")),
    data_filter: dict = Depends(DependDataIsolation)
):
    # 实现逻辑
```

2. **验证控制器逻辑**
```python
# app/controllers/order.py
def get_orders_by_user(db: Session, user_id: int, data_filter: dict = None):
    query = db.query(Order)
    
    # 应用数据隔离过滤
    if data_filter and "user_id" in data_filter:
        query = query.filter(Order.user_id == data_filter["user_id"])
    
    return query.all()
```

### 3. 权限验证失败

#### 问题描述
权限配置测试失败或权限验证不通过。

#### 诊断步骤

```bash
# 1. 运行详细的权限测试
python tests/test_permission_config.py -v

# 2. 检查数据库中的权限数据
sqlite3 data/app.db "SELECT * FROM role;"
sqlite3 data/app.db "SELECT * FROM api;"
sqlite3 data/app.db "SELECT * FROM role_api;"

# 3. 查看权限验证日志
grep "权限" logs/conport.log
```

#### 解决方案

1. **重建权限数据**
```bash
# 备份数据库
cp data/app.db data/app.db.backup

# 重新初始化
python -c "
from app.core.init_app import init_roles, init_apis, configure_user_role_permissions
import asyncio
asyncio.run(init_roles())
asyncio.run(init_apis())
asyncio.run(configure_user_role_permissions())
"
```

2. **手动修复权限关联**
```python
from app.models.admin import Role, Api
from app.core.init_app import get_db

db = next(get_db())
role = db.query(Role).filter(Role.name == '普通用户').first()

# 添加缺失的 API 权限
api_paths = [
    "/api/v1/base/userinfo",
    "/api/v1/orders/",
    # ... 其他权限
]

for path in api_paths:
    api = db.query(Api).filter(Api.path == path).first()
    if api and api not in role.apis:
        role.apis.append(api)

db.commit()
```

## 登录和认证问题

### 1. 登录失败

#### 问题描述
用户无法登录或登录后立即退出。

#### 诊断步骤

```bash
# 1. 检查用户状态
python -c "
from app.models.admin import User
from app.core.init_app import get_db
db = next(get_db())
user = db.query(User).filter(User.username == 'username').first()
print(f'用户状态: active={user.is_active}, superuser={user.is_superuser}')
"

# 2. 测试密码验证
python -c "
from app.utils.password import verify_password
from app.models.admin import User
from app.core.init_app import get_db
db = next(get_db())
user = db.query(User).filter(User.username == 'username').first()
print(f'密码验证: {verify_password("password", user.password)}')
"

# 3. 检查 JWT 配置
grep SECRET_KEY app/settings/config.py
```

#### 解决方案

1. **重置用户密码**
```python
from app.models.admin import User
from app.utils.password import hash_password
from app.core.init_app import get_db

db = next(get_db())
user = db.query(User).filter(User.username == 'username').first()
user.password = hash_password('new_password')
db.commit()
```

2. **激活用户账户**
```python
user.is_active = True
db.commit()
```

3. **检查 JWT 密钥**
```python
# 确保 SECRET_KEY 不为空且足够复杂
SECRET_KEY = "your-secret-key-here"
```

### 2. Token 过期问题

#### 问题描述
Token 频繁过期或无法刷新。

#### 诊断步骤

```bash
# 1. 检查 Token 配置
grep TOKEN_EXPIRE app/settings/config.py

# 2. 验证 Token
python -c "
from app.utils.jwt import verify_token
token = 'your_token_here'
try:
    payload = verify_token(token)
    print(f'Token 有效: {payload}')
except Exception as e:
    print(f'Token 无效: {e}')
"
```

#### 解决方案

1. **调整 Token 过期时间**
```python
# app/settings/config.py
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # 增加到60分钟
```

2. **实现 Token 自动刷新**
```javascript
// 前端自动刷新逻辑
axios.interceptors.response.use(
  response => response,
  async error => {
    if (error.response?.status === 401) {
      try {
        await refreshToken();
        return axios.request(error.config);
      } catch (refreshError) {
        // 跳转到登录页
        router.push('/login');
      }
    }
    return Promise.reject(error);
  }
);
```

## 数据库问题

### 1. 数据库连接失败

#### 问题描述
应用无法连接到数据库。

#### 诊断步骤

```bash
# 1. 检查数据库文件
ls -la data/app.db

# 2. 测试数据库连接
python -c "
from app.core.init_app import get_db
try:
    db = next(get_db())
    print('数据库连接成功')
except Exception as e:
    print(f'数据库连接失败: {e}')
"

# 3. 检查数据库权限
sudo -u www-data ls -la data/
```

#### 解决方案

1. **修复文件权限**
```bash
sudo chown -R www-data:www-data data/
sudo chmod 664 data/app.db
sudo chmod 775 data/
```

2. **重新创建数据库**
```bash
# 备份现有数据
cp data/app.db data/app.db.backup

# 重新初始化
rm data/app.db
python -c "from app.core.init_app import init_db; init_db()"
```

### 2. 数据迁移问题

#### 问题描述
数据库结构不匹配或迁移失败。

#### 诊断步骤

```bash
# 1. 检查数据库结构
sqlite3 data/app.db ".schema"

# 2. 检查表是否存在
sqlite3 data/app.db "SELECT name FROM sqlite_master WHERE type='table';"

# 3. 检查数据完整性
sqlite3 data/app.db "PRAGMA integrity_check;"
```

#### 解决方案

1. **手动创建缺失的表**
```python
from app.models.admin import Base
from app.core.init_app import engine

# 创建所有表
Base.metadata.create_all(bind=engine)
```

2. **数据迁移脚本**
```python
# migrate_data.py
from app.models.admin import *
from app.core.init_app import get_db, init_roles, init_apis
import asyncio

async def migrate():
    # 初始化基础数据
    await init_roles()
    await init_apis()
    print("数据迁移完成")

if __name__ == "__main__":
    asyncio.run(migrate())
```

## 前端问题

### 1. 页面无法加载

#### 问题描述
前端页面白屏或加载失败。

#### 诊断步骤

```bash
# 1. 检查前端构建
cd web
npm run build

# 2. 检查 API 连接
curl -X GET http://localhost:8000/api/v1/base/health

# 3. 查看浏览器控制台错误
# 打开浏览器开发者工具查看 Console 和 Network 标签
```

#### 解决方案

1. **重新安装依赖**
```bash
cd web
rm -rf node_modules package-lock.json
npm install
```

2. **检查环境配置**
```javascript
// web/.env.production
VITE_API_BASE_URL=http://localhost:8000/api
```

3. **清除浏览器缓存**
```bash
# 或在浏览器中按 Ctrl+Shift+R 强制刷新
```

### 2. API 请求失败

#### 问题描述
前端无法调用后端 API。

#### 诊断步骤

```bash
# 1. 检查 CORS 配置
grep CORS app/core/middlewares.py

# 2. 测试 API 直接访问
curl -X GET http://localhost:8000/api/v1/base/health

# 3. 检查网络请求
# 在浏览器开发者工具的 Network 标签中查看请求详情
```

#### 解决方案

1. **修复 CORS 配置**
```python
# app/core/middlewares.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 添加前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

2. **检查 API 基础地址**
```javascript
// web/src/api/index.js
const baseURL = 'http://localhost:8000/api';
```

## 性能问题

### 1. 响应缓慢

#### 问题描述
系统响应时间过长。

#### 诊断步骤

```bash
# 1. 检查系统资源
top -p $(pgrep -f "python run.py")
free -h
df -h

# 2. 检查数据库性能
sqlite3 data/app.db "EXPLAIN QUERY PLAN SELECT * FROM user;"

# 3. 分析慢查询
grep "slow" logs/conport.log
```

#### 解决方案

1. **优化数据库查询**
```python
# 添加数据库索引
from sqlalchemy import Index

# 在模型中添加索引
class User(Base):
    __tablename__ = "user"
    # ...
    __table_args__ = (
        Index('idx_user_username', 'username'),
        Index('idx_user_email', 'email'),
    )
```

2. **启用查询缓存**
```python
# app/core/crud.py
from functools import lru_cache

@lru_cache(maxsize=128)
def get_user_permissions(user_id: int):
    # 缓存用户权限查询
    pass
```

3. **增加工作进程**
```bash
# 使用多进程启动
uvicorn app.main:app --workers 4 --host 0.0.0.0 --port 8000
```

### 2. 内存泄漏

#### 问题描述
系统内存使用持续增长。

#### 诊断步骤

```bash
# 1. 监控内存使用
ps aux | grep python
watch -n 5 'ps -p PID -o pid,ppid,cmd,%mem,%cpu'

# 2. 检查数据库连接
lsof -p PID | grep socket

# 3. 分析内存使用
python -m memory_profiler run.py
```

#### 解决方案

1. **优化数据库连接池**
```python
# app/settings/config.py
DATABASE_POOL_SIZE = 5
DATABASE_MAX_OVERFLOW = 10
DATABASE_POOL_TIMEOUT = 30
```

2. **及时关闭资源**
```python
# 使用上下文管理器
with get_db() as db:
    # 数据库操作
    pass
```

## 日志和调试

### 1. 启用详细日志

```python
# app/settings/config.py
LOG_LEVEL = "DEBUG"

# 或临时启用
import logging
logging.getLogger().setLevel(logging.DEBUG)
```

### 2. 常用调试命令

```bash
# 查看实时日志
tail -f logs/conport.log

# 搜索特定错误
grep -i "error" logs/conport.log
grep -i "权限" logs/conport.log

# 查看最近的错误
tail -n 100 logs/conport.log | grep -i "error"

# 分析日志统计
awk '{print $1}' logs/access.log | sort | uniq -c | sort -nr
```

### 3. 调试工具

```python
# 在代码中添加调试点
import pdb; pdb.set_trace()

# 或使用 IPython
import IPython; IPython.embed()

# 性能分析
import cProfile
cProfile.run('your_function()')
```

## 应急处理

### 1. 系统无响应

```bash
# 1. 重启服务
sudo systemctl restart vue-fastapi-admin

# 2. 检查进程
ps aux | grep python
kill -9 PID  # 强制终止

# 3. 清理资源
free -h
sync && echo 3 > /proc/sys/vm/drop_caches
```

### 2. 数据损坏

```bash
# 1. 立即备份
cp data/app.db data/emergency_backup_$(date +%Y%m%d_%H%M%S).db

# 2. 检查数据完整性
sqlite3 data/app.db "PRAGMA integrity_check;"

# 3. 从备份恢复
cp data/app.db.backup data/app.db
```

### 3. 安全事件

```bash
# 1. 封禁可疑 IP
iptables -A INPUT -s SUSPICIOUS_IP -j DROP

# 2. 强制所有用户重新登录
# 清除所有 session 或重启服务

# 3. 保存证据
cp logs/conport.log logs/security_incident_$(date +%Y%m%d_%H%M%S).log
```

## 联系支持

### 收集信息
在联系技术支持前，请收集以下信息：

1. **系统信息**
```bash
uname -a
python --version
cat /etc/os-release
```

2. **错误日志**
```bash
tail -n 50 logs/conport.log
```

3. **配置信息**
```bash
# 隐藏敏感信息
grep -v "SECRET\|PASSWORD" app/settings/config.py
```

4. **权限测试结果**
```bash
python tests/test_permission_config.py
```

### 支持渠道
- **技术支持邮箱**：support@your-domain.com
- **紧急联系电话**：400-xxx-xxxx
- **在线文档**：https://docs.your-domain.com
- **社区论坛**：https://forum.your-domain.com

## 总结

本故障排除指南涵盖了系统运行中可能遇到的主要问题：

1. **权限问题**：用户权限、数据隔离、权限验证
2. **认证问题**：登录失败、Token 过期
3. **数据库问题**：连接失败、数据迁移
4. **前端问题**：页面加载、API 请求
5. **性能问题**：响应缓慢、内存泄漏
6. **应急处理**：系统无响应、数据损坏、安全事件

遇到问题时，建议按照诊断步骤逐步排查，并保存相关日志信息以便进一步分析。