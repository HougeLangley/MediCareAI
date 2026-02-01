# Deployment Guide | 部署指南

> **MediCare_AI** 部署完整指南 / Complete deployment guide for MediCare_AI
> 
> **版本 / Version:** 1.0.0 | **更新日期 / Updated:** 2025-02-01

---

## 📋 Table of Contents | 目录

- [System Requirements | 系统要求](#system-requirements)
- [Quick Deployment | 快速部署](#quick-deployment)
- [Detailed Installation | 详细安装步骤](#detailed-installation)
- [Configuration Guide | 配置指南](#configuration-guide)
- [Production Deployment | 生产环境部署](#production-deployment)
- [Troubleshooting | 故障排除](#troubleshooting)
- [Maintenance | 维护指南](#maintenance)

---

<a name="system-requirements"></a>
## 🖥️ System Requirements | 系统要求

### Hardware Requirements | 硬件要求

| Component | Minimum | Recommended | 说明 |
|-----------|---------|-------------|------|
| **CPU** | 2 cores | 4+ cores | 多核有助于并发处理 |
| **RAM** | 4 GB | 8+ GB | AI 模型需要较多内存 |
| **Storage** | 20 GB | 50+ GB SSD | 数据库存储和文件上传 |
| **Network** | 10 Mbps | 100+ Mbps | 文档上传和 AI 响应 |

### Software Requirements | 软件要求

#### Required | 必需软件
```bash
# Docker 20.10+ 安装 / Installation
curl -fsSL https://get.docker.com | sh
sudo systemctl enable docker
sudo systemctl start docker

# Docker Compose 2.0+ 安装 / Installation
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### Supported Operating Systems | 支持的操作系统
- **Linux**: Ubuntu 20.04+, CentOS 8+, Debian 11+
- **macOS**: 11.0+ (Big Sur and later)
- **Windows**: Windows 10/11 with WSL2

---

<a name="quick-deployment"></a>
## 🚀 Quick Deployment | 快速部署

### One-Command Deployment | 一键部署

```bash
# 克隆仓库 / Clone repository
git clone https://github.com/yourusername/MediCare_AI.git
cd MediCare_AI

# 快速启动脚本 / Quick start script
./scripts/deploy.sh
```

### Manual Quick Start | 手动快速开始

```bash
# 1. 准备环境 / Prepare environment
cp .env.example .env

# 2. 生成自签名证书（测试环境）/ Generate self-signed certs (testing)
mkdir -p docker/nginx/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout docker/nginx/ssl/key.pem \
  -out docker/nginx/ssl/cert.pem \
  -subj "/C=CN/ST=State/L=City/O=MediCare_AI/CN=localhost"

# 3. 启动服务 / Start services
docker-compose up -d

# 4. 初始化数据库 / Initialize database
docker-compose exec backend python -c "
import asyncio
from app.db.init_db import init_db
asyncio.run(init_db())
print('✅ Database initialized successfully!')
"

# 5. 验证部署 / Verify deployment
curl http://localhost/health
echo "✅ Deployment successful! Access: http://localhost"
```

---

<a name="detailed-installation"></a>
## 📖 Detailed Installation | 详细安装步骤

### Step 1: Environment Preparation | 环境准备

#### 1.1 Update System | 更新系统
```bash
# Ubuntu/Debian
sudo apt update && sudo apt upgrade -y

# CentOS/RHEL
sudo yum update -y
```

#### 1.2 Install Docker | 安装 Docker
```bash
# Automated installation script / 自动安装脚本
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
newgrp docker

# Verify installation / 验证安装
docker --version
docker-compose --version
```

### Step 2: Project Setup | 项目设置

```bash
# Clone repository / 克隆仓库
git clone https://github.com/yourusername/MediCare_AI.git
cd MediCare_AI

# Create necessary directories / 创建必要目录
mkdir -p docker/nginx/ssl
mkdir -p data/uploads
mkdir -p data/knowledge_base
mkdir -p backups
```

### Step 3: Environment Configuration | 环境配置

#### 3.1 Create .env File | 创建环境文件
```bash
cp .env.example .env
nano .env  # 或使用 vim
```

#### 3.2 Required Variables | 必需变量
```bash
# ============================================
# Database Configuration | 数据库配置
# ============================================
POSTGRES_PASSWORD=YourSecurePassword123!  # 生产环境使用强密码
POSTGRES_USER=medicare_user
POSTGRES_DB=medicare_ai

# ============================================
# Redis Configuration | Redis 配置
# ============================================
REDIS_PASSWORD=YourRedisPassword456!

# ============================================
# JWT Configuration | JWT 配置
# ============================================
JWT_SECRET_KEY=your-super-secret-jwt-key-min-32-characters-long
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# ============================================
# AI API Configuration | AI API 配置
# ============================================
AI_API_KEY=your-ai-api-key
AI_API_URL=http://your-ai-server:8033/v1/
AI_MODEL_ID=unsloth/GLM-4.7-Flash-GGUF:BF16

# ============================================
# MinerU API Configuration | MinerU API 配置
# ============================================
MINERU_TOKEN=your-mineru-api-token

# ============================================
# Application Configuration | 应用配置
# ============================================
DEBUG=false
LOG_LEVEL=INFO
MAX_FILE_SIZE=200000000  # 200MB in bytes
```

### Step 4: SSL Certificate Setup | SSL 证书配置

#### Option A: Self-Signed (Development) | 自签名证书（开发）
```bash
mkdir -p docker/nginx/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout docker/nginx/ssl/key.pem \
  -out docker/nginx/ssl/cert.pem \
  -subj "/C=CN/ST=State/L=City/O=MediCare_AI/CN=localhost"
```

#### Option B: Let's Encrypt (Production) | Let's Encrypt（生产）
```bash
# Install certbot / 安装 certbot
sudo apt install certbot

# Generate certificates / 生成证书
sudo certbot certonly --standalone -d your-domain.com

# Copy certificates / 复制证书
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem docker/nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem docker/nginx/ssl/key.pem

# Setup auto-renewal / 设置自动续期
echo "0 12 * * * /usr/bin/certbot renew --quiet" | sudo crontab -
```

### Step 5: Deploy Services | 部署服务

```bash
# Pull latest images / 拉取最新镜像
docker-compose pull

# Build custom images / 构建自定义镜像
docker-compose build --no-cache

# Start services / 启动服务
docker-compose up -d

# Wait for database to be ready / 等待数据库就绪
sleep 15

# Initialize database tables / 初始化数据库表
docker-compose exec backend python -c "
import asyncio
from app.db.init_db import init_db
asyncio.run(init_db())
"

# Verify all services / 验证所有服务
docker-compose ps
```

### Step 6: Verify Deployment | 验证部署

```bash
# Check health endpoint / 检查健康端点
curl -f http://localhost/health && echo "✅ Health check passed"

# Check API docs / 检查 API 文档
curl -f http://localhost/api/docs && echo "✅ API docs accessible"

# Check logs / 查看日志
docker-compose logs --tail=50 backend
```

---

<a name="configuration-guide"></a>
## ⚙️ Configuration Guide | 配置指南

### Docker Compose Configuration | Docker Compose 配置

```yaml
# docker-compose.yml 关键配置说明 / Key configuration explanation
version: '3.8'

services:
  postgres:
    image: postgres:17-alpine  # 使用最新稳定版本 / Use latest stable
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./docker/postgres/init.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 10s
      timeout: 5s
      retries: 5
    # 生产环境资源限制 / Production resource limits
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G

  backend:
    build: ./backend
    environment:
      DATABASE_URL: postgresql+asyncpg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
      REDIS_URL: redis://:${REDIS_PASSWORD}@redis:6379/0
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_started
    # 健康检查 / Health check
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

### Nginx Configuration | Nginx 配置

```nginx
# docker/nginx/nginx.conf 关键部分 / Key sections
server {
    listen 80;
    server_name localhost;
    
    # Redirect HTTP to HTTPS / HTTP 重定向到 HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name localhost;
    
    # SSL Configuration / SSL 配置
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # Security Headers / 安全头
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # Frontend / 前端
    location / {
        root /usr/share/nginx/html;
        try_files $uri $uri/ /index.html;
        expires 1h;
        add_header Cache-Control "public, immutable";
    }
    
    # Backend API / 后端 API
    location /api/ {
        proxy_pass http://backend:8000/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        
        # Timeouts / 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

---

<a name="production-deployment"></a>
## 🏭 Production Deployment | 生产环境部署

### Pre-Deployment Checklist | 部署前检查清单

```markdown
- [ ] 所有密码已更改为强密码 / All passwords changed to strong passwords
- [ ] SSL 证书已配置 / SSL certificates configured
- [ ] DEBUG 设置为 false / DEBUG set to false
- [ ] CORS 来源已限制 / CORS origins restricted
- [ ] 日志级别设置为 WARNING / Log level set to WARNING
- [ ] 数据库备份策略已配置 / Database backup strategy configured
- [ ] 监控和告警已设置 / Monitoring and alerting configured
- [ ] 防火墙规则已配置 / Firewall rules configured
```

### Performance Optimization | 性能优化

#### Database Optimization | 数据库优化
```sql
-- PostgreSQL 性能优化 / PostgreSQL performance tuning
-- 在 docker/postgres/init.sql 中添加 / Add to docker/postgres/init.sql

-- 连接数配置 / Connection settings
ALTER SYSTEM SET max_connections = '200';
ALTER SYSTEM SET shared_buffers = '1GB';
ALTER SYSTEM SET effective_cache_size = '3GB';
ALTER SYSTEM SET maintenance_work_mem = '256MB';
ALTER SYSTEM SET work_mem = '16MB';

-- 查询优化 / Query optimization
CREATE INDEX CONCURRENTLY idx_patients_user_id ON patients(user_id);
CREATE INDEX CONCURRENTLY idx_medical_cases_patient_id ON medical_cases(patient_id);
CREATE INDEX CONCURRENTLY idx_ai_feedbacks_medical_case_id ON ai_feedbacks(medical_case_id);
```

#### Application Optimization | 应用优化
```python
# backend/app/core/config.py
class Settings(BaseSettings):
    # 连接池配置 / Connection pool settings
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10
    
    # 缓存配置 / Cache settings
    REDIS_CACHE_TTL: int = 3600  # 1 hour
    
    # 文件上传限制 / File upload limits
    MAX_FILE_SIZE: int = 200 * 1024 * 1024  # 200MB
    MAX_UPLOAD_CONCURRENT: int = 5
```

### Security Hardening | 安全加固

```bash
# 1. 设置文件权限 / Set file permissions
chmod 600 .env
chmod 644 docker/nginx/nginx.conf
chmod 600 docker/nginx/ssl/*.pem

# 2. 配置防火墙 / Configure firewall
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# 3. 限制 Docker 容器资源 / Limit Docker container resources
# 在 docker-compose.yml 中添加 / Add to docker-compose.yml
deploy:
  resources:
    limits:
      cpus: '2.0'
      memory: 4G
    reservations:
      cpus: '1.0'
      memory: 2G
```

### Backup Strategy | 备份策略

```bash
#!/bin/bash
# scripts/backup.sh - Database backup script / 数据库备份脚本

BACKUP_DIR="/backups/$(date +%Y%m%d)"
mkdir -p $BACKUP_DIR

# PostgreSQL backup / PostgreSQL 备份
docker-compose exec -T postgres pg_dump -U medicare_user medicare_ai > $BACKUP_DIR/db_backup.sql

# Uploads backup / 上传文件备份
tar -czf $BACKUP_DIR/uploads_backup.tar.gz data/uploads/

# Compress backup / 压缩备份
tar -czf $BACKUP_DIR.tar.gz $BACKUP_DIR
rm -rf $BACKUP_DIR

# Keep only last 7 days / 只保留最近7天
find /backups -name "*.tar.gz" -mtime +7 -delete

echo "✅ Backup completed: $BACKUP_DIR.tar.gz"
```

Add to crontab / 添加到定时任务:
```bash
# 每天凌晨 2 点备份 / Backup daily at 2 AM
0 2 * * * /home/houge/Dev/MediCare_AI/scripts/backup.sh >> /var/log/medicare_backup.log 2>&1
```

---

<a name="troubleshooting"></a>
## 🔧 Troubleshooting | 故障排除

### Common Issues | 常见问题

#### Issue 1: Services Won't Start | 服务无法启动
```bash
# Check port conflicts / 检查端口冲突
sudo lsof -i :80
sudo lsof -i :443
sudo lsof -i :8000
sudo lsof -i :5432

# Check logs / 查看日志
docker-compose logs backend
docker-compose logs postgres
docker-compose logs nginx

# Restart with clean state / 清理状态后重启
docker-compose down -v
docker-compose up -d
```

#### Issue 2: Database Connection Failed | 数据库连接失败
```bash
# Check database status / 检查数据库状态
docker-compose exec postgres pg_isready -U medicare_user

# View PostgreSQL logs / 查看 PostgreSQL 日志
docker-compose logs postgres | tail -50

# Reset database (WARNING: Data loss) / 重置数据库（警告：数据丢失）
docker-compose down -v
docker-compose up -d postgres
sleep 10
docker-compose exec backend python -c "
import asyncio
from app.db.init_db import init_db
asyncio.run(init_db())
"
```

#### Issue 3: AI Diagnosis Not Working | AI 诊断不工作
```bash
# Check AI API connectivity / 检查 AI API 连接
curl -f $AI_API_URL/health

# Check backend logs / 查看后端日志
docker-compose logs backend | grep -i "ai\|diagnosis"

# Verify environment variables / 验证环境变量
docker-compose exec backend printenv | grep AI
```

#### Issue 4: File Upload Fails | 文件上传失败
```bash
# Check upload directory permissions / 检查上传目录权限
docker-compose exec backend ls -la /app/uploads/

# Check Nginx max body size / 检查 Nginx 最大请求体大小
docker-compose exec nginx nginx -T | grep client_max_body_size

# Check disk space / 检查磁盘空间
df -h
```

### Debug Mode | 调试模式

```bash
# Enable debug logging / 启用调试日志
docker-compose exec backend python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
"

# Access container shell / 访问容器 shell
docker-compose exec backend bash
docker-compose exec postgres psql -U medicare_user -d medicare_ai

# Monitor real-time logs / 实时监控日志
docker-compose logs -f --tail=100
```

---

<a name="maintenance"></a>
## 🔧 Maintenance | 维护指南

### Daily Maintenance | 日常维护

```bash
# Check service status / 检查服务状态
docker-compose ps

# View recent logs / 查看近期日志
docker-compose logs --tail=100 backend

# Check disk usage / 检查磁盘使用
df -h
docker system df
```

### Weekly Maintenance | 周维护

```bash
# Update images / 更新镜像
docker-compose pull
docker-compose up -d

# Clean up old containers / 清理旧容器
docker system prune -f

# Review logs for errors / 查看错误日志
docker-compose logs backend | grep -i error
```

### Monthly Maintenance | 月维护

```bash
# Full system update / 全面系统更新
docker-compose down
docker-compose pull
docker-compose build --no-cache
docker-compose up -d

# Database optimization / 数据库优化
docker-compose exec postgres psql -U medicare_user -d medicare_ai -c "VACUUM ANALYZE;"

# Backup verification / 备份验证
# Test restore from backup / 测试从备份恢复
```

### Upgrade Procedure | 升级流程

```bash
# 1. Backup current data / 备份当前数据
./scripts/backup.sh

# 2. Pull latest code / 拉取最新代码
git pull origin main

# 3. Review changelog / 查看更新日志
cat CHANGELOG.md

# 4. Update dependencies / 更新依赖
docker-compose pull
docker-compose build --no-cache

# 5. Deploy new version / 部署新版本
docker-compose up -d

# 6. Run migrations if needed / 如需运行迁移
docker-compose exec backend alembic upgrade head

# 7. Verify deployment / 验证部署
curl http://localhost/health
```

---

## 📞 Support | 支持

### Getting Help | 获取帮助

- **Documentation**: [Full Documentation](../README.md)
- **Issues**: [GitHub Issues](https://github.com/yourusername/MediCare_AI/issues)
- **Email**: support@medicare-ai.example.com

### Emergency Contacts | 紧急联系

If the system is down in production / 如果生产环境系统宕机:

1. Check service status: `docker-compose ps`
2. Check logs: `docker-compose logs --tail=200`
3. Restart services: `docker-compose restart`
4. Contact system administrator if issue persists

---

**Last Updated | 最后更新:** 2025-02-01  
**Version | 版本:** 1.0.0  
**Maintainers | 维护者:** MediCare_AI Team
