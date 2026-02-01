#!/bin/bash
# MediCare AI - 快速启动脚本

echo "🚀 启动 MediCare AI 服务..."

# 检查容器状态
if ! docker ps | grep -q medicare_backend; then
    echo "❌ Backend not running. Starting..."
    docker start medicare_backend 2>/dev/null || echo "Backend container not found"
fi

if ! docker ps | grep -q medicare_frontend_static; then
    echo "❌ Frontend not running. Starting..."
    docker start medicare_frontend_static 2>/dev/null || echo "Frontend container not found"
fi

# 显示服务状态
echo ""
echo "📊 服务状态："
docker ps --format "table {{.Names}}\t{{.Ports}}\t{{.Status}}" | grep medicare

echo ""
echo "🌐 访问地址："
echo "   前端: http://192.168.50.115:8080"
echo "   后端: http://192.168.50.115:8000"
echo ""
echo "🔑 演示账号："
echo "   邮箱: demo@medicare.ai"
echo "   密码: medicare123456"
echo ""
