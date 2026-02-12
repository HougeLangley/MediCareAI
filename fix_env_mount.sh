#!/bin/bash
# 修复脚本：确保 .env 文件正确挂载

echo "=== 修复 MINERU_TOKEN 同步问题 ==="

# 1. 首先，备份当前的 .env
cp .env .env.backup.$(date +%Y%m%d_%H%M%S)

# 2. 检查 docker-compose.yml 是否已修改
if ! grep -q "./.env:/app/.env" docker-compose.yml; then
    echo "错误：docker-compose.yml 未正确修改，请手动添加 .env 挂载"
    exit 1
fi

# 3. 停止并删除后端容器
echo "停止后端容器..."
docker stop medicare_backend 2>/dev/null
docker rm medicare_backend 2>/dev/null

# 4. 重新创建后端容器
echo "重新创建后端容器..."
docker-compose up -d backend

# 5. 等待服务启动
echo "等待服务启动..."
sleep 5

# 6. 检查健康状态
if curl -s http://localhost:8000/health | grep -q "healthy"; then
    echo "✅ 后端服务已正常启动"
else
    echo "❌ 后端服务启动失败"
    exit 1
fi

# 7. 验证挂载
echo "验证 .env 挂载..."
CONTAINER_TOKEN=$(docker exec medicare_backend cat /app/.env 2>/dev/null | grep MINERU_TOKEN | cut -d= -f2)
HOST_TOKEN=$(cat .env | grep MINERU_TOKEN | cut -d= -f2)

if [ "$CONTAINER_TOKEN" = "$HOST_TOKEN" ]; then
    echo "✅ .env 文件挂载正确，容器内外 TOKEN 一致"
else
    echo "⚠️ 警告：容器内外 TOKEN 不一致"
    echo "容器 TOKEN: ${CONTAINER_TOKEN:0:50}..."
    echo "宿主机 TOKEN: ${HOST_TOKEN:0:50}..."
fi

echo ""
echo "=== 修复完成 ==="
echo "现在您可以通过管理界面修改 MinerU 配置，.env 文件会自动同步更新。"
