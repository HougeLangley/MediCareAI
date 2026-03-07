#!/bin/bash
set -e

echo "========================================"
echo "MediCareAI Backend Startup"
echo "========================================"

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
until PGPASSWORD=$POSTGRES_PASSWORD psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\q' 2>/dev/null; do
    echo "PostgreSQL is unavailable - sleeping"
    sleep 2
done
echo "PostgreSQL is up!"

# Initialize database tables if not exists
echo "Initializing database tables..."
python /app/init_db.py

echo "Running database migrations..."
# 保留独立的迁移脚本（非 migrations/versions 目录）
python /app/migrations/add_license_document_columns.py
python /app/migrations/add_internal_messages_table.py
# 注意：003/004/005 等版本迁移已在 init_db.py 中通过 SQLAlchemy 模型自动创建
# 新部署无需执行硬编码迁移，旧部署已有这些字段
# 如需手动执行：docker-compose exec backend python /app/app/migrations/versions/XXX.py

echo "Initializing admin account..."
python /app/init_admin.py

echo "Initializing chronic diseases data..."
python -m app.db.init_chronic_diseases

echo "========================================"
echo "Starting API Server..."
echo "========================================"

# Start the application
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 "$@"
