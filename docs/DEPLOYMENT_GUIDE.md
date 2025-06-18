# 部署和配置指南

## 概述

本指南详细说明了如何部署和配置 Vue FastAPI Admin 系统，包括普通用户权限配置的完整部署流程。

## 系统要求

### 最低配置
- **操作系统**：Linux/Windows/macOS
- **Python**：3.11+
- **Node.js**：18.8.0+
- **内存**：2GB RAM
- **存储**：5GB 可用空间

### 推荐配置
- **操作系统**：Ubuntu 20.04+ / CentOS 8+
- **Python**：3.11
- **Node.js**：18.8.0+
- **内存**：4GB RAM
- **存储**：10GB 可用空间
- **数据库**：SQLite（默认）/ PostgreSQL / MySQL

## 部署方式

### 方式一：Docker 部署（推荐）

#### 1. 使用预构建镜像
```bash
# 拉取最新镜像
docker pull mizhexiaoxiao/vue-fastapi-admin:latest

# 启动容器
docker run -d \
  --restart=always \
  --name=vue-fastapi-admin \
  -p 9999:80 \
  -v $(pwd)/data:/app/data \
  mizhexiaoxiao/vue-fastapi-admin:latest
```

#### 2. 自定义构建
```bash
# 克隆项目
git clone https://gitee.com/mizhexiaoxiao/vue-fastapi-admin.git
cd vue-fastapi-admin

# 构建镜像
docker build --no-cache . -t vue-fastapi-admin

# 启动容器
docker run -d \
  --restart=always \
  --name=vue-fastapi-admin \
  -p 9999:80 \
  -v $(pwd)/data:/app/data \
  vue-fastapi-admin
```

#### 3. Docker Compose 部署
```yaml
# docker-compose.yml
version: '3.8'
services:
  vue-fastapi-admin:
    image: mizhexiaoxiao/vue-fastapi-admin:latest
    container_name: vue-fastapi-admin
    restart: always
    ports:
      - "9999:80"
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    environment:
      - ENV=production
```

```bash
# 启动服务
docker-compose up -d
```

### 方式二：本地部署

#### 1. 后端部署

##### 环境准备
```bash
# 克隆项目
git clone https://gitee.com/mizhexiaoxiao/vue-fastapi-admin.git
cd vue-fastapi-admin

# 创建虚拟环境（推荐使用 uv）
pip install uv
uv venv
source .venv/bin/activate  # Linux/Mac
# 或 .venv\Scripts\activate  # Windows

# 安装依赖
uv add pyproject.toml
# 或使用 pip
# pip install -r requirements.txt
```

##### 配置文件
```bash
# 复制配置文件模板
cp app/settings/config.py.example app/settings/config.py

# 编辑配置文件
vim app/settings/config.py
```

##### 启动后端服务
```bash
# 开发环境
python run.py

# 生产环境
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

#### 2. 前端部署

##### 开发环境
```bash
cd web

# 安装依赖
npm install -g pnpm
pnpm install

# 启动开发服务器
pnpm dev
```

##### 生产环境
```bash
cd web

# 构建生产版本
pnpm build

# 使用 nginx 部署
sudo cp -r dist/* /var/www/html/
```

## 配置说明

### 1. 后端配置

#### 数据库配置
```python
# app/settings/config.py
class Settings:
    # SQLite（默认）
    DATABASE_URL = "sqlite:///./data/app.db"
    
    # PostgreSQL
    # DATABASE_URL = "postgresql://user:password@localhost/dbname"
    
    # MySQL
    # DATABASE_URL = "mysql+pymysql://user:password@localhost/dbname"
```

#### JWT 配置
```python
# JWT 密钥（生产环境必须修改）
SECRET_KEY = "your-secret-key-here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
```

#### CORS 配置
```python
# 允许的前端域名
ALLOWED_HOSTS = ["*"]  # 生产环境应指定具体域名
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8080",
    "https://yourdomain.com"
]
```

### 2. 前端配置

#### API 基础地址
```javascript
// web/src/api/index.js
const baseURL = process.env.NODE_ENV === 'production' 
  ? 'https://your-api-domain.com/api'
  : 'http://localhost:8000/api'
```

#### 环境变量
```bash
# web/.env.production
VITE_API_BASE_URL=https://your-api-domain.com/api
VITE_APP_TITLE=Vue FastAPI Admin
```

## 权限配置部署

### 1. 自动初始化
系统启动时会自动执行权限初始化：

```bash
# 启动应用
python run.py

# 查看初始化日志
tail -f logs/conport.log | grep "权限"
```

### 2. 手动验证权限配置
```bash
# 运行权限配置测试
python tests/test_permission_config.py

# 查看详细验证报告
python -c "from app.utils.permission_validator import permission_validator; import asyncio; print(asyncio.run(permission_validator.validate_all_permissions()))"
```

### 3. 权限配置检查清单

- [ ] 普通用户角色已创建
- [ ] 11个API权限已配置
- [ ] 菜单权限已分配
- [ ] 数据隔离机制已启用
- [ ] 权限验证通过测试

## Nginx 配置

### 1. 基础配置
```nginx
# /etc/nginx/sites-available/vue-fastapi-admin
server {
    listen 80;
    server_name your-domain.com;
    
    # 前端静态文件
    location / {
        root /var/www/html;
        try_files $uri $uri/ /index.html;
    }
    
    # API 代理
    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # WebSocket 支持
    location /ws {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### 2. HTTPS 配置
```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    # 其他配置同上...
}

# HTTP 重定向到 HTTPS
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}
```

## 数据库迁移

### 1. 备份现有数据
```bash
# SQLite 备份
cp data/app.db data/app.db.backup

# PostgreSQL 备份
pg_dump dbname > backup.sql
```

### 2. 执行迁移
```bash
# 启动应用进行自动迁移
python run.py

# 或手动执行迁移脚本
python -c "from app.core.init_app import init_db; init_db()"
```

## 监控和日志

### 1. 日志配置
```python
# app/settings/config.py
LOG_LEVEL = "INFO"
LOG_FILE = "logs/app.log"
LOG_ROTATION = "1 day"
LOG_RETENTION = "30 days"
```

### 2. 日志查看
```bash
# 查看应用日志
tail -f logs/conport.log

# 查看权限相关日志
grep "权限" logs/conport.log

# 查看错误日志
grep "ERROR" logs/conport.log
```

### 3. 性能监控
```bash
# 查看系统资源使用
top -p $(pgrep -f "python run.py")

# 查看数据库连接
lsof -i :8000
```

## 安全配置

### 1. 防火墙设置
```bash
# Ubuntu/Debian
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 22
sudo ufw enable

# CentOS/RHEL
sudo firewall-cmd --permanent --add-port=80/tcp
sudo firewall-cmd --permanent --add-port=443/tcp
sudo firewall-cmd --reload
```

### 2. SSL/TLS 配置
```bash
# 使用 Let's Encrypt
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### 3. 安全头配置
```nginx
# 添加到 nginx 配置
add_header X-Frame-Options DENY;
add_header X-Content-Type-Options nosniff;
add_header X-XSS-Protection "1; mode=block";
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";
```

## 故障排除

### 常见问题

#### 1. 服务启动失败
```bash
# 检查端口占用
sudo netstat -tlnp | grep :8000

# 检查权限
ls -la run.py

# 查看详细错误
python run.py --debug
```

#### 2. 数据库连接失败
```bash
# 检查数据库文件权限
ls -la data/

# 检查数据库连接字符串
grep DATABASE_URL app/settings/config.py
```

#### 3. 前端无法访问后端
```bash
# 检查 CORS 配置
grep CORS app/settings/config.py

# 检查防火墙
sudo ufw status
```

### 调试命令

```bash
# 检查系统状态
systemctl status vue-fastapi-admin

# 查看容器日志（Docker 部署）
docker logs vue-fastapi-admin

# 测试 API 连接
curl -X GET http://localhost:8000/api/v1/base/health

# 验证权限配置
python tests/test_permission_config.py
```

## 更新和维护

### 1. 应用更新
```bash
# 备份数据
cp -r data data.backup

# 拉取最新代码
git pull origin main

# 更新依赖
uv sync

# 重启服务
sudo systemctl restart vue-fastapi-admin
```

### 2. 定期维护
```bash
# 清理日志
find logs/ -name "*.log" -mtime +30 -delete

# 数据库优化（SQLite）
sqlite3 data/app.db "VACUUM;"

# 检查磁盘空间
df -h
```

## 性能优化

### 1. 后端优化
```python
# 增加工作进程
uvicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker

# 启用缓存
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
```

### 2. 前端优化
```bash
# 启用 gzip 压缩
# 在 nginx 配置中添加
gzip on;
gzip_types text/plain text/css application/json application/javascript;

# 启用浏览器缓存
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

## 备份策略

### 1. 自动备份脚本
```bash
#!/bin/bash
# backup.sh
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backup/vue-fastapi-admin"

# 创建备份目录
mkdir -p $BACKUP_DIR

# 备份数据库
cp data/app.db $BACKUP_DIR/app_$DATE.db

# 备份配置文件
cp -r app/settings $BACKUP_DIR/settings_$DATE

# 清理旧备份（保留30天）
find $BACKUP_DIR -name "*.db" -mtime +30 -delete
```

### 2. 定时任务
```bash
# 添加到 crontab
crontab -e

# 每天凌晨2点备份
0 2 * * * /path/to/backup.sh
```

## 总结

本部署指南涵盖了从基础环境准备到生产环境部署的完整流程，包括：

1. **多种部署方式**：Docker 和本地部署
2. **完整配置说明**：数据库、安全、性能配置
3. **权限配置部署**：自动初始化和验证
4. **监控和维护**：日志、性能监控、备份策略
5. **故障排除**：常见问题和解决方案

按照本指南操作，可以快速部署一个安全、稳定的 Vue FastAPI Admin 系统。