#!/bin/bash

# MediCare_AI 部署脚本
# 用于部署MediCare_AI系统到生产环境

set -e

echo "🚀 开始部署 MediCare_AI 系统..."

# 检查Docker和Docker Compose是否已安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装，请先安装 Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose 未安装，请先安装 Docker Compose"
    exit 1
fi

# 检查环境变量文件
if [ ! -f .env ]; then
    echo "⚠️  .env 文件不存在，正在从 .env.example 创建..."
    cp .env.example .env
    echo "📝 请编辑 .env 文件设置正确的环境变量"
    echo "⚠️  特别是数据库密码、JWT密钥等安全相关配置"
    read -p "按 Enter 继续，或按 Ctrl+C 退出..."
fi

# 检查SSL证书
if [ ! -d "docker/nginx/ssl" ]; then
    echo "⚠️  SSL证书目录不存在，正在创建自签名证书..."
    mkdir -p docker/nginx/ssl
    
    # 生成自签名证书（生产环境请使用有效证书）
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout docker/nginx/ssl/key.pem \
        -out docker/nginx/ssl/cert.pem \
        -subj "/C=CN/ST=State/L=City/O=MediCare_AI/CN=localhost"
    
    echo "🔐 自签名SSL证书已生成（仅用于测试）"
    echo "⚠️  生产环境请使用有效的SSL证书"
fi

# 创建必要的目录
echo "📁 创建必要的目录..."
mkdir -p uploads
mkdir -p logs
mkdir -p backups

# 设置权限
echo "🔒 设置文件权限..."
chmod 755 uploads logs backups
chmod 600 docker/nginx/ssl/key.pem 2>/dev/null || true
chmod 644 docker/nginx/ssl/cert.pem 2>/dev/null || true

# 构建和启动服务
echo "🔨 构建Docker镜像..."
docker-compose build --no-cache

echo "🚀 启动服务..."
docker-compose up -d

# 等待数据库启动
echo "⏳ 等待数据库启动..."
sleep 10

# 运行数据库迁移
echo "🗄️ 运行数据库迁移..."
docker-compose exec backend alembic upgrade head

# 创建初始管理员用户（可选）
echo "👤 创建初始管理员用户..."
docker-compose exec backend python -c "
from app.core.database import AsyncSessionLocal
from app.models.models import User
from app.core.security import get_password_hash
import asyncio

async def create_admin():
    async with AsyncSessionLocal() as db:
        admin_email = 'admin@medicare.ai'
        admin_password = 'admin123456'
        
        # 检查是否已存在管理员用户
        result = await db.execute(select(User).where(User.email == admin_email))
        if not result.scalar_one_or_none():
            admin_user = User(
                email=admin_email,
                password_hash=get_password_hash(admin_password),
                full_name='系统管理员',
                is_active=True,
                is_verified=True
            )
            db.add(admin_user)
            await db.commit()
            print('✅ 管理员用户已创建')
        else:
            print('ℹ️  管理员用户已存在')

asyncio.run(create_admin())
"

# 检查服务状态
echo "🔍 检查服务状态..."
docker-compose ps

# 显示访问信息
echo ""
echo "🎉 MediCare_AI 系统部署完成！"
echo ""
echo "📱 访问信息："
echo "   前端应用: https://localhost"
echo "   API文档:  https://localhost/api/docs"
echo "   管理界面: https://localhost/admin"
echo ""
echo "👤 默认管理员账号："
echo "   邮箱: admin@medicare.ai"
echo "   密码: admin123456"
echo ""
echo "⚠️  安全提醒："
echo "   1. 请立即修改默认密码"
echo "   2. 请使用有效的SSL证书"
echo "   3. 请定期备份数据库"
echo ""
echo "📋 常用命令："
echo "   查看日志: docker-compose logs -f [service]"
echo "   重启服务: docker-compose restart [service]"
echo "   停止服务: docker-compose down"
echo "   数据备份: ./scripts/backup.sh"
echo ""
echo "🔧 故障排除："
echo "   如果遇到问题，请检查 logs/ 目录中的日志文件"
echo "   或运行 docker-compose logs 查看服务日志"
echo ""