-- PostgreSQL初始化脚本
-- 创建MediCare_AI数据库和用户

-- 创建数据库（如果不存在）
SELECT 'CREATE DATABASE medicare_ai'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'medicare_ai')\gexec

-- 连接到medicare_ai数据库
\c medicare_ai;

-- 创建用户（如果不存在）
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'medicare_user') THEN
        CREATE USER medicare_user WITH PASSWORD 'your_secure_postgres_password';
    END IF;
END
$$;

-- 授予权限
GRANT ALL PRIVILEGES ON DATABASE medicare_ai TO medicare_user;

-- 设置schema权限
GRANT ALL ON SCHEMA public TO medicare_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO medicare_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO medicare_user;

-- 设置默认权限
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO medicare_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO medicare_user;

-- 创建pgcrypto扩展（用于加密）
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- 创建uuid-ossp扩展（用于UUID生成）
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 设置时区
SET timezone = 'UTC';
