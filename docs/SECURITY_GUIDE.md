# 安全配置和最佳实践指南

## 概述

本指南详细说明了 Vue FastAPI Admin 系统的安全配置和最佳实践，特别针对普通用户权限配置的安全考虑。

## 安全架构

### 1. 多层安全验证

#### JWT 身份验证
- **Token 生成**：使用 HS256 算法
- **Token 过期**：默认30分钟
- **自动刷新**：支持 Token 自动续期
- **安全存储**：前端使用 httpOnly Cookie

#### RBAC 权限控制
- **角色分离**：管理员和普通用户严格分离
- **最小权限原则**：用户只获得必需的最小权限
- **动态权限检查**：每次请求都进行权限验证

#### 数据隔离机制
- **用户级隔离**：普通用户只能访问自己的数据
- **API级隔离**：在控制器层面实现数据过滤
- **数据库级隔离**：通过查询条件确保数据安全

### 2. 安全配置清单

#### 必须配置项
- [ ] 修改默认 JWT 密钥
- [ ] 配置强密码策略
- [ ] 启用 HTTPS
- [ ] 配置 CORS 白名单
- [ ] 设置安全响应头
- [ ] 启用请求频率限制
- [ ] 配置日志审计

## JWT 安全配置

### 1. 密钥管理

#### 生成强密钥
```bash
# 生成256位随机密钥
python -c "import secrets; print(secrets.token_urlsafe(32))"

# 或使用 openssl
openssl rand -base64 32
```

#### 配置示例
```python
# app/settings/config.py
class Settings:
    # 生产环境必须使用强密钥
    SECRET_KEY = "your-super-secret-key-here-256-bits"
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    REFRESH_TOKEN_EXPIRE_DAYS = 7
```

#### 密钥轮换策略
```python
# 支持多密钥验证（密钥轮换）
SECRET_KEYS = [
    "current-secret-key",
    "previous-secret-key"  # 用于验证旧 token
]
```

### 2. Token 安全

#### 安全存储
```javascript
// 前端 Token 存储（推荐）
// 使用 httpOnly Cookie
document.cookie = `token=${token}; httpOnly; secure; sameSite=strict`;

// 避免使用 localStorage（XSS 风险）
// localStorage.setItem('token', token); // 不推荐
```

#### Token 验证增强
```python
# app/utils/jwt.py
def verify_token(token: str) -> dict:
    try:
        # 验证 Token 签名
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # 验证必要字段
        if not payload.get("sub") or not payload.get("exp"):
            raise JWTError("Invalid token payload")
            
        # 验证用户状态
        user = get_user_by_id(payload["sub"])
        if not user or not user.is_active:
            raise JWTError("User inactive")
            
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

## 权限安全配置

### 1. 角色权限矩阵

| 功能模块 | 超级管理员 | 普通用户 | 访客 |
|----------|------------|----------|------|
| 用户管理 | ✅ 全部 | ✅ 仅自己 | ❌ |
| 角色管理 | ✅ | ❌ | ❌ |
| 菜单管理 | ✅ | ❌ | ❌ |
| API管理 | ✅ | ❌ | ❌ |
| 订单管理 | ✅ 全部 | ✅ 仅自己 | ❌ |
| 审计日志 | ✅ | ❌ | ❌ |
| 仪表盘 | ✅ 全部数据 | ✅ 个人数据 | ❌ |

### 2. API 权限验证

#### 装饰器实现
```python
# app/core/dependency.py
class EnhancedPermissionControl:
    def __init__(self, required_permission: str):
        self.required_permission = required_permission
    
    async def __call__(self, 
                      request: Request,
                      current_user: User = Depends(get_current_user)):
        # 1. 验证用户权限
        if not await self.check_user_permission(current_user, self.required_permission):
            raise HTTPException(status_code=403, detail="权限不足")
        
        # 2. 记录访问日志
        await self.log_access(current_user, request)
        
        return current_user
    
    async def check_user_permission(self, user: User, permission: str) -> bool:
        """检查用户是否有指定权限"""
        user_permissions = await get_user_permissions(user.id)
        return permission in user_permissions
```

#### 数据隔离实现
```python
# app/core/dependency.py
class DataIsolationControl:
    async def __call__(self, 
                      current_user: User = Depends(get_current_user)):
        # 超级用户可以访问所有数据
        if current_user.is_superuser:
            return None  # 无数据过滤
        
        # 普通用户只能访问自己的数据
        return {"user_id": current_user.id}
```

### 3. 前端权限控制

#### 路由守卫
```javascript
// web/src/router/guard/auth-guard.js
export function createAuthGuard(router) {
  router.beforeEach(async (to, from, next) => {
    const userStore = useUserStore();
    
    // 检查登录状态
    if (!userStore.isLoggedIn) {
      return next('/login');
    }
    
    // 检查路由权限
    const hasPermission = await userStore.checkRoutePermission(to.path);
    if (!hasPermission) {
      return next('/403');
    }
    
    next();
  });
}
```

#### 组件权限指令
```javascript
// web/src/directives/permission.js
export const permission = {
  mounted(el, binding) {
    const { value } = binding;
    const userStore = useUserStore();
    
    if (!userStore.hasPermission(value)) {
      el.style.display = 'none';
      // 或者移除元素
      // el.parentNode?.removeChild(el);
    }
  }
};
```

## 数据安全

### 1. 敏感数据保护

#### 密码安全
```python
# app/utils/password.py
import bcrypt
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """使用 bcrypt 哈希密码"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)

# 密码强度验证
def validate_password_strength(password: str) -> bool:
    """验证密码强度"""
    if len(password) < 8:
        return False
    
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
    
    return sum([has_upper, has_lower, has_digit, has_special]) >= 3
```

#### 数据脱敏
```python
# app/schemas/users.py
from pydantic import BaseModel, validator

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    phone: Optional[str] = None
    
    @validator('phone')
    def mask_phone(cls, v):
        """手机号脱敏"""
        if v and len(v) >= 11:
            return v[:3] + '****' + v[-4:]
        return v
    
    @validator('email')
    def mask_email(cls, v):
        """邮箱脱敏"""
        if v and '@' in v:
            local, domain = v.split('@')
            if len(local) > 2:
                local = local[:2] + '***'
            return f"{local}@{domain}"
        return v
```

### 2. 数据库安全

#### SQL 注入防护
```python
# 使用 ORM 参数化查询
from sqlalchemy.orm import Session

# 安全的查询方式
def get_user_orders(db: Session, user_id: int):
    return db.query(Order).filter(Order.user_id == user_id).all()

# 避免字符串拼接（SQL注入风险）
# query = f"SELECT * FROM orders WHERE user_id = {user_id}"  # 危险
```

#### 数据库连接安全
```python
# app/settings/config.py
class Settings:
    # 使用连接池
    DATABASE_URL = "postgresql://user:password@localhost/dbname?sslmode=require"
    
    # 连接池配置
    DB_POOL_SIZE = 5
    DB_MAX_OVERFLOW = 10
    DB_POOL_TIMEOUT = 30
    
    # 启用 SSL
    DB_SSL_MODE = "require"
```

## 网络安全

### 1. HTTPS 配置

#### SSL/TLS 证书
```nginx
# nginx 配置
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    # SSL 证书配置
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    # SSL 安全配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # HSTS
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
}
```

### 2. CORS 安全配置

```python
# app/core/middlewares.py
from fastapi.middleware.cors import CORSMiddleware

# 生产环境 CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-domain.com",
        "https://admin.your-domain.com"
    ],  # 不要使用 ["*"]
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
    expose_headers=["X-Total-Count"]
)
```

### 3. 安全响应头

```python
# app/core/middlewares.py
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    
    # 安全响应头
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:;"
    )
    
    return response
```

## 攻击防护

### 1. 暴力破解防护

```python
# app/core/security.py
from collections import defaultdict
from datetime import datetime, timedelta

class RateLimiter:
    def __init__(self):
        self.attempts = defaultdict(list)
        self.blocked_ips = defaultdict(datetime)
    
    def is_allowed(self, ip: str, max_attempts: int = 5, window_minutes: int = 15) -> bool:
        now = datetime.now()
        
        # 检查是否被封禁
        if ip in self.blocked_ips:
            if now < self.blocked_ips[ip]:
                return False
            else:
                del self.blocked_ips[ip]
        
        # 清理过期记录
        cutoff = now - timedelta(minutes=window_minutes)
        self.attempts[ip] = [t for t in self.attempts[ip] if t > cutoff]
        
        # 检查尝试次数
        if len(self.attempts[ip]) >= max_attempts:
            # 封禁 IP
            self.blocked_ips[ip] = now + timedelta(hours=1)
            return False
        
        return True
    
    def record_attempt(self, ip: str):
        self.attempts[ip].append(datetime.now())

rate_limiter = RateLimiter()

# 在登录接口中使用
@app.post("/api/v1/auth/login")
async def login(request: Request, user_data: UserLogin):
    client_ip = request.client.host
    
    if not rate_limiter.is_allowed(client_ip):
        raise HTTPException(status_code=429, detail="请求过于频繁，请稍后再试")
    
    # 登录逻辑...
    if not authenticate_user(user_data.username, user_data.password):
        rate_limiter.record_attempt(client_ip)
        raise HTTPException(status_code=401, detail="用户名或密码错误")
```

### 2. XSS 防护

```python
# 输入验证和清理
from html import escape
import re

def sanitize_input(text: str) -> str:
    """清理用户输入，防止 XSS"""
    if not text:
        return text
    
    # HTML 转义
    text = escape(text)
    
    # 移除潜在的脚本标签
    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
    
    return text

# 在 Pydantic 模型中使用
class OrderCreate(BaseModel):
    title: str
    description: Optional[str] = None
    
    @validator('title', 'description')
    def sanitize_text(cls, v):
        return sanitize_input(v) if v else v
```

### 3. CSRF 防护

```python
# app/core/csrf.py
import secrets
from fastapi import HTTPException, Request

class CSRFProtection:
    def __init__(self):
        self.tokens = set()
    
    def generate_token(self) -> str:
        token = secrets.token_urlsafe(32)
        self.tokens.add(token)
        return token
    
    def validate_token(self, token: str) -> bool:
        if token in self.tokens:
            self.tokens.remove(token)  # 一次性使用
            return True
        return False

csrf = CSRFProtection()

# 在需要保护的接口中使用
@app.post("/api/v1/orders/")
async def create_order(request: Request, order_data: OrderCreate):
    csrf_token = request.headers.get("X-CSRF-Token")
    if not csrf_token or not csrf.validate_token(csrf_token):
        raise HTTPException(status_code=403, detail="CSRF token invalid")
    
    # 创建订单逻辑...
```

## 审计和监控

### 1. 访问日志

```python
# app/core/audit.py
from datetime import datetime
from sqlalchemy.orm import Session

class AuditLogger:
    def __init__(self, db: Session):
        self.db = db
    
    async def log_access(self, user_id: int, action: str, resource: str, 
                        ip_address: str, user_agent: str, success: bool = True):
        log_entry = AuditLog(
            user_id=user_id,
            action=action,
            resource=resource,
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
            timestamp=datetime.now()
        )
        self.db.add(log_entry)
        await self.db.commit()
    
    async def log_permission_denied(self, user_id: int, attempted_action: str, 
                                   resource: str, ip_address: str):
        await self.log_access(
            user_id=user_id,
            action=f"DENIED: {attempted_action}",
            resource=resource,
            ip_address=ip_address,
            user_agent="",
            success=False
        )
```

### 2. 异常监控

```python
# app/core/monitoring.py
import logging
from datetime import datetime

class SecurityMonitor:
    def __init__(self):
        self.logger = logging.getLogger("security")
    
    def alert_suspicious_activity(self, user_id: int, activity: str, details: dict):
        """记录可疑活动"""
        alert = {
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "activity": activity,
            "details": details,
            "severity": "HIGH"
        }
        
        self.logger.warning(f"Suspicious activity detected: {alert}")
        
        # 可以集成到监控系统（如 Sentry、DataDog 等）
        # sentry_sdk.capture_message(f"Suspicious activity: {activity}", level="warning")
    
    def check_anomalous_behavior(self, user_id: int, current_ip: str, 
                                last_login_ip: str, last_login_time: datetime):
        """检查异常行为"""
        now = datetime.now()
        
        # IP 地址变化检查
        if current_ip != last_login_ip:
            self.alert_suspicious_activity(
                user_id=user_id,
                activity="IP_CHANGE",
                details={
                    "previous_ip": last_login_ip,
                    "current_ip": current_ip,
                    "time_since_last_login": str(now - last_login_time)
                }
            )
        
        # 异常登录时间检查
        if now.hour < 6 or now.hour > 22:  # 非工作时间
            self.alert_suspicious_activity(
                user_id=user_id,
                activity="OFF_HOURS_LOGIN",
                details={"login_time": now.isoformat()}
            )
```

## 安全检查清单

### 部署前检查
- [ ] 修改所有默认密码和密钥
- [ ] 启用 HTTPS 和强制重定向
- [ ] 配置防火墙规则
- [ ] 设置安全响应头
- [ ] 启用访问日志和审计
- [ ] 配置备份策略
- [ ] 测试权限配置
- [ ] 进行安全扫描

### 运行时监控
- [ ] 监控异常登录活动
- [ ] 检查权限越权尝试
- [ ] 监控系统资源使用
- [ ] 定期检查日志异常
- [ ] 监控数据库性能
- [ ] 检查证书过期时间

### 定期维护
- [ ] 更新系统依赖
- [ ] 轮换密钥和证书
- [ ] 清理过期日志
- [ ] 备份验证
- [ ] 安全配置审查
- [ ] 渗透测试

## 应急响应

### 1. 安全事件处理

```bash
#!/bin/bash
# emergency_response.sh

# 1. 立即封禁可疑 IP
iptables -A INPUT -s SUSPICIOUS_IP -j DROP

# 2. 强制所有用户重新登录
redis-cli FLUSHDB  # 清除所有 session

# 3. 备份当前日志
cp logs/app.log logs/incident_$(date +%Y%m%d_%H%M%S).log

# 4. 通知管理员
echo "Security incident detected at $(date)" | mail -s "Security Alert" admin@domain.com
```

### 2. 数据泄露响应

1. **立即行动**
   - 隔离受影响系统
   - 保存证据和日志
   - 通知相关人员

2. **评估影响**
   - 确定泄露数据范围
   - 识别受影响用户
   - 评估业务影响

3. **修复和恢复**
   - 修复安全漏洞
   - 重置受影响账户
   - 加强监控措施

## 总结

本安全指南涵盖了系统安全的各个方面：

1. **身份验证安全**：JWT 配置、密钥管理、Token 安全
2. **权限控制安全**：RBAC 实现、数据隔离、前端权限
3. **数据安全**：敏感数据保护、数据库安全
4. **网络安全**：HTTPS、CORS、安全响应头
5. **攻击防护**：暴力破解、XSS、CSRF 防护
6. **监控审计**：访问日志、异常监控、安全检查

遵循这些安全最佳实践，可以显著提高系统的安全性和可靠性。