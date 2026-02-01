#!/usr/bin/env python3
"""
初始化数据库和演示数据
"""
import asyncio
import bcrypt
import uuid
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from app.core.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def init_db_and_insert_demo_data():
    """初始化数据库表和插入演示数据"""
    # 创建引擎，使用localhost连接
    engine = create_async_engine(
        settings.database_url,
        echo=settings.debug,
    )

    # 生成密码哈希
    password_hash = bcrypt.hashpw('Demo123456!'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    # SQL语句
    create_tables_sql = """
    -- 创建扩展
    CREATE EXTENSION IF NOT EXISTS pgcrypto;
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

    -- 创建用户表
    CREATE TABLE IF NOT EXISTS users (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        email VARCHAR(255) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        full_name VARCHAR(255) NOT NULL,
        is_active BOOLEAN DEFAULT true,
        is_verified BOOLEAN DEFAULT false,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        last_login TIMESTAMP WITH TIME ZONE
    );

    -- 创建患者表
    CREATE TABLE IF NOT EXISTS patients (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        user_id UUID NOT NULL,
        name VARCHAR(255) NOT NULL,
        age INTEGER,
        gender VARCHAR(10),
        phone VARCHAR(20),
        email VARCHAR(255),
        address TEXT,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        CONSTRAINT fk_patients_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );

    -- 创建疾病表
    CREATE TABLE IF NOT EXISTS diseases (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        name VARCHAR(255) UNIQUE NOT NULL,
        code VARCHAR(50) UNIQUE,
        description TEXT,
        guidelines_json JSONB,
        is_active BOOLEAN DEFAULT true,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );

    -- 创建文档表
    CREATE TABLE IF NOT EXISTS medical_documents (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        user_id UUID NOT NULL,
        medical_case_id UUID,
        file_name VARCHAR(255) NOT NULL,
        file_path VARCHAR(500) NOT NULL,
        file_size BIGINT,
        mime_type VARCHAR(100),
        upload_status VARCHAR(50) DEFAULT 'uploading',
        extracted_content TEXT,
        extraction_metadata JSONB,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        CONSTRAINT fk_documents_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );

    -- 创建用户会话表
    CREATE TABLE IF NOT EXISTS user_sessions (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        user_id UUID NOT NULL,
        token_id VARCHAR(255) UNIQUE NOT NULL,
        expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        is_active BOOLEAN DEFAULT true,
        CONSTRAINT fk_sessions_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );

    -- 创建审计日志表
    CREATE TABLE IF NOT EXISTS audit_logs (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        user_id UUID,
        action VARCHAR(100) NOT NULL,
        resource_type VARCHAR(50),
        resource_id UUID,
        details JSONB,
        ip_address INET,
        user_agent TEXT,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        CONSTRAINT fk_logs_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
    );
    """

    insert_demo_data_sql = """
    -- 插入演示用户
    INSERT INTO users (
        id, email, password_hash, full_name,
        is_active, is_verified
    ) VALUES (
        '00000000-0000-0000-0000-000000000001',
        'demo@medicare.ai',
        :password_hash,
        '演示患者',
        true,
        true
    ) ON CONFLICT (email) DO NOTHING;

    -- 插入示例患者数据
    INSERT INTO patients (
        id, user_id, name, age, gender, phone, email, address
    ) VALUES
        ('00000000-0000-0000-0000-000000000002',
         '00000000-0000-0000-0000-000000000001',
         '张三', 35, '男', '13800138000',
         'zhangsan@example.com', '北京市朝阳区'),
        ('00000000-0000-0000-0000-000000000003',
         '00000000-0000-0000-0000-000000000001',
         '李四', 42, '女', '13900139000',
         'lisi@example.com', '上海市浦东新区')
    ON CONFLICT DO NOTHING;

    -- 插入示例疾病数据
    INSERT INTO diseases (id, name, code, description, guidelines_json)
    VALUES
        ('00000000-0000-0000-0000-000000000010',
         '高血压', 'I10',
         '高血压是一种常见的心血管疾病，以体循环动脉血压增高为主要特征。',
         '{"symptoms": ["头晕", "头痛", "心悸"], "treatment": "降压药物"}'),
        ('00000000-0000-0000-0000-000000000011',
         '糖尿病', 'E11',
         '糖尿病是一组以高血糖为特征的代谢性疾病。',
         '{"symptoms": ["多饮", "多食", "多尿"], "treatment": "胰岛素治疗"}'),
        ('00000000-0000-0000-0000-000000000012',
         '冠心病', 'I25',
         '冠心病是冠状动脉粥样硬化性心脏病的简称。',
         '{"symptoms": ["胸痛", "呼吸困难"], "treatment": "药物治疗或手术"}')
    ON CONFLICT DO NOTHING;
    """

    try:
        async with engine.begin() as conn:
            # 创建表
            logger.info("正在创建数据库表...")
            await conn.execute(text(create_tables_sql))

            # 插入演示数据
            logger.info("正在插入演示数据...")
            await conn.execute(text(insert_demo_data_sql), {"password_hash": password_hash})

        logger.info("✅ 数据库初始化和演示数据插入成功！")
        logger.info(f"演示账号：demo@medicare.ai")
        logger.info(f"演示密码：Demo123456!")

    except Exception as e:
        logger.error(f"❌ 数据库初始化失败: {e}")
        raise
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(init_db_and_insert_demo_data())
