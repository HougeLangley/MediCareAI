"""
Migration: Add Email Verification Fields | 添加邮箱验证字段

添加邮箱验证相关字段到users表：
- email_verification_token
- email_verification_sent_at
- email_verified_at
- password_reset_token
- password_reset_sent_at

Revision ID: 003_add_email_verification_fields
Revises: 002_add_fulltext_search_to_kb
Create Date: 2025-02-26
"""

from typing import Sequence, Union

# revision identifiers, used by Alembic
revision: str = "003_add_email_verification_fields"
down_revision: Union[str, None] = "002_add_fulltext_search_to_kb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Upgrade database schema to add email verification fields.
    """
    from sqlalchemy import text
    from app.db.database import engine

    with engine.connect() as conn:
        # 添加邮箱验证token字段
        conn.execute(
            text("""
            ALTER TABLE users 
            ADD COLUMN IF NOT EXISTS email_verification_token VARCHAR(255)
        """)
        )

        # 添加邮箱验证发送时间字段
        conn.execute(
            text("""
            ALTER TABLE users 
            ADD COLUMN IF NOT EXISTS email_verification_sent_at TIMESTAMP WITH TIME ZONE
        """)
        )

        # 添加邮箱验证完成时间字段
        conn.execute(
            text("""
            ALTER TABLE users 
            ADD COLUMN IF NOT EXISTS email_verified_at TIMESTAMP WITH TIME ZONE
        """)
        )

        # 添加密码重置token字段
        conn.execute(
            text("""
            ALTER TABLE users 
            ADD COLUMN IF NOT EXISTS password_reset_token VARCHAR(255)
        """)
        )

        # 添加密码重置发送时间字段
        conn.execute(
            text("""
            ALTER TABLE users 
            ADD COLUMN IF NOT EXISTS password_reset_sent_at TIMESTAMP WITH TIME ZONE
        """)
        )

        # 创建索引以加快查询
        conn.execute(
            text("""
            CREATE INDEX IF NOT EXISTS idx_users_email_verification_token 
            ON users(email_verification_token)
        """)
        )

        conn.execute(
            text("""
            CREATE INDEX IF NOT EXISTS idx_users_password_reset_token 
            ON users(password_reset_token)
        """)
        )

        conn.commit()

    print("✅ Email verification fields added successfully")


def downgrade() -> None:
    """
    Downgrade database schema to remove email verification fields.
    """
    from sqlalchemy import text
    from app.db.database import engine

    with engine.connect() as conn:
        # 删除索引
        conn.execute(
            text("""
            DROP INDEX IF EXISTS idx_users_password_reset_token
        """)
        )

        conn.execute(
            text("""
            DROP INDEX IF EXISTS idx_users_email_verification_token
        """)
        )

        # 删除字段
        conn.execute(
            text("""
            ALTER TABLE users 
            DROP COLUMN IF EXISTS password_reset_sent_at
        """)
        )

        conn.execute(
            text("""
            ALTER TABLE users 
            DROP COLUMN IF EXISTS password_reset_token
        """)
        )

        conn.execute(
            text("""
            ALTER TABLE users 
            DROP COLUMN IF EXISTS email_verified_at
        """)
        )

        conn.execute(
            text("""
            ALTER TABLE users 
            DROP COLUMN IF EXISTS email_verification_sent_at
        """)
        )

        conn.execute(
            text("""
            ALTER TABLE users 
            DROP COLUMN IF EXISTS email_verification_token
        """)
        )

        conn.commit()

    print("✅ Email verification fields removed")
