#!/bin/bash
# MediCareAI Docker 数据清理脚本
# 用于完全清理数据持久化，恢复干净状态
#
# 用法:
#   ./scripts/cleanup-docker.sh        # 交互式模式
#   ./scripts/cleanup-docker.sh -y     # 非交互式模式（自动确认）

set -e

# 解析参数
AUTO_CONFIRM=false
if [ "$1" == "-y" ] || [ "$1" == "--yes" ]; then
    AUTO_CONFIRM=true
fi

echo "========================================"
echo "MediCareAI Docker 数据清理工具"
echo "========================================"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检测可用的 docker compose 命令
if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE="docker-compose"
elif docker compose version &> /dev/null; then
    DOCKER_COMPOSE="docker compose"
else
    echo -e "${RED}错误: 未找到 docker-compose 或 docker compose 命令${NC}"
    echo "请确保 Docker 和 Docker Compose 已正确安装"
    exit 1
fi

# 检查是否在项目目录
if [ ! -f "docker-compose.yml" ]; then
    echo -e "${RED}错误: 请在 MediCareAI 项目目录中运行此脚本${NC}"
    echo "用法: cd /path/to/MediCareAI && ./scripts/cleanup-docker.sh"
    exit 1
fi

# 如果不是自动确认模式，显示警告并等待确认
if [ "$AUTO_CONFIRM" = false ]; then
    echo -e "${YELLOW}⚠️  警告: 此操作将删除所有持久化数据！${NC}"
    echo "包括:"
    echo "  - PostgreSQL 数据库数据"
    echo "  - Redis 缓存数据"
    echo "  - 上传的文件"
    echo "  - 知识库文档"
    echo ""
    echo -n "是否继续? [y/N] (10秒后默认取消): "
    
    # 使用 read 的超时功能
    if read -t 10 -r response; then
        if [[ ! "$response" =~ ^[Yy]$ ]]; then
            echo "已取消"
            exit 0
        fi
    else
        echo ""
        echo "超时，已取消"
        exit 0
    fi
else
    echo -e "${YELLOW}⚠️  自动模式: 将删除所有持久化数据${NC}"
fi

echo ""
echo "========================================"
echo "步骤 1/4: 停止并删除容器"
echo "========================================"
$DOCKER_COMPOSE down --remove-orphans
echo -e "${GREEN}✓ 容器已停止并删除${NC}"

echo ""
echo "========================================"
echo "步骤 2/4: 删除数据卷 (Volumes)"
echo "========================================"
# 删除项目相关的 volumes
docker volume rm -f medicareai_postgres_data 2>/dev/null || true
docker volume rm -f medicareai_redis_data 2>/dev/null || true
docker volume rm -f medicareai_uploads_data 2>/dev/null || true
docker volume rm -f medicareai_kb_data 2>/dev/null || true
echo -e "${GREEN}✓ 数据卷已删除${NC}"

echo ""
echo "========================================"
echo "步骤 3/4: 删除构建的镜像 (可选)"
echo "========================================"
echo -n "是否删除构建的镜像? [y/N]: "
read -r response

if [[ "$response" =~ ^[Yy]$ ]]; then
    $DOCKER_COMPOSE down --rmi all 2>/dev/null || true
    # 删除 dangling 镜像
    docker image prune -f
    echo -e "${GREEN}✓ 镜像已删除${NC}"
else
    echo "跳过镜像删除"
fi

echo ""
echo "========================================"
echo "步骤 4/4: 清理悬空资源"
echo "========================================"
docker system prune -f
echo -e "${GREEN}✓ 悬空资源已清理${NC}"

echo ""
echo "========================================"
echo "清理完成！"
echo "========================================"
echo ""
echo "系统已恢复干净状态，可以重新部署:"
echo "  $DOCKER_COMPOSE up -d"
echo ""
echo -e "${YELLOW}注意: 数据库已完全重置，需要重新初始化${NC}"
echo "  - 默认管理员账号将重新创建"
echo "  - 所有用户数据已丢失"
echo "  - 需要重新上传知识库文档"
