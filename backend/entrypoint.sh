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

echo "Initializing admin account..."
python /app/init_admin.py

echo "Initializing chronic diseases data..."
python -m app.db.init_chronic_diseases

echo "========================================"
echo "Starting API Server..."
echo "========================================"

# Start the application
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 "$@"
