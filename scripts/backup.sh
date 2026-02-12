#!/bin/bash

# MediCare_AI 数据备份脚本
# 用于备份PostgreSQL数据库和上传的文件

set -euo pipefail

# 配置
PROJECT_NAME="MediCareAI"
BACKUP_DIR="${HOME}/${PROJECT_NAME}/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="medicare_ai_backup_${DATE}"
DB_CONTAINER="medicare_postgres"
DB_NAME="medicare_ai"
DB_USER="medicare_user"
UPLOAD_DIR="${HOME}/${PROJECT_NAME}/uploads"

echo "🗄️ 开始备份 MediCare_AI 数据..."

# 创建备份目录
mkdir -p "${BACKUP_DIR}/${BACKUP_NAME}"

# 备份数据库
echo "📊 备份数据库..."
docker exec "${DB_CONTAINER}" pg_dump -U "${DB_USER}" "${DB_NAME}" | gzip > "${BACKUP_DIR}/${BACKUP_NAME}/database.sql.gz"

# 备份上传文件
echo "📁 备份上传文件..."
if [ -d "${UPLOAD_DIR}" ]; then
    tar -czf "${BACKUP_DIR}/${BACKUP_NAME}/uploads.tar.gz" -C "$(dirname "${UPLOAD_DIR}")" "$(basename "${UPLOAD_DIR}")"
else
    echo "⚠️ 上传目录不存在，跳过文件备份"
fi

# 备份配置文件
echo "⚙️ 备份配置文件..."
cp .env "${BACKUP_DIR}/${BACKUP_NAME}/" 2>/dev/null || echo "⚠️ .env 文件不存在，跳过"
cp docker-compose.yml "${BACKUP_DIR}/${BACKUP_NAME}/"

# 创建备份信息文件
cat > "${BACKUP_DIR}/${BACKUP_NAME}/backup_info.txt" << EOF
MediCare_AI 系统备份信息
========================

备份时间: $(date)
备份名称: ${BACKUP_NAME}
系统版本: 1.0.0

备份内容:
- 数据库: ${DB_NAME}
- 上传文件: ${UPLOAD_DIR}
- 配置文件: .env, docker-compose.yml

恢复命令:
1. 恢复数据库: gunzip -c database.sql.gz | docker exec -i ${DB_CONTAINER} psql -U ${DB_USER} ${DB_NAME}
2. 恢复文件: tar -xzf uploads.tar.gz
3. 恢复配置: 复制 .env 和 docker-compose.yml 到项目目录

注意事项:
- 请确保目标环境已正确配置
- 数据库恢复前请停止相关服务
- 建议在测试环境中先验证备份完整性
EOF

# 压缩整个备份目录
echo "🗜️ 压缩备份..."
cd "${BACKUP_DIR}"
tar -czf "${BACKUP_NAME}.tar.gz" "${BACKUP_NAME}/"
rm -rf "${BACKUP_NAME}/"

echo "✅ 备份完成！"
echo "📍 备份文件位置: ${BACKUP_DIR}/${BACKUP_NAME}.tar.gz"
echo "📊 备份大小: $(du -h "${BACKUP_DIR}/${BACKUP_NAME}.tar.gz" | cut -f1)"

# 清理旧备份（保留最近7个）
echo "🧹 清理旧备份..."
cd "${BACKUP_DIR}"
ls -t medicare_ai_backup_*.tar.gz | tail -n +8 | xargs rm -f 2>/dev/null || echo "没有需要清理的旧备份"

echo "🎉 备份任务完成！"