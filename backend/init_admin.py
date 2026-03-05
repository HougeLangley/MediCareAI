#!/usr/bin/env python3
"""
Initialize default admin account for MediCareAI
创建默认管理员账号

Usage:
    docker-compose exec backend python /app/init_admin.py
"""

import asyncio
import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import AsyncSessionLocal
from app.models.models import User
from app.core.security import get_password_hash
from sqlalchemy import select

# 硬编码管理员账号配置
ADMIN_EMAIL = "admin@medicare.ai"
ADMIN_PASSWORD = "admin123456"

async def init_admin_account():
    """Initialize default admin account"""
    print("🚀 Initializing admin account...")
    
    async with AsyncSessionLocal() as session:
        # Check if admin already exists
        result = await session.execute(
            select(User).where(User.email == ADMIN_EMAIL)
        )
        existing_admin = result.scalar_one_or_none()
        
        if existing_admin:
            print("✅ Admin account already exists!")
            print(f"   Email: {ADMIN_EMAIL}")
            print(f"   Role: {existing_admin.role}")
            return
        
        # Create admin user
        admin_user = User(
            id=uuid.uuid4(),
            email=ADMIN_EMAIL,
            password_hash=get_password_hash(ADMIN_PASSWORD),
            role="admin",
            full_name="系统管理员",
            phone="13800000000",
            is_active=True,
            is_verified=True,
            admin_level="super",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        session.add(admin_user)
        await session.commit()
        
        print("✅ Admin account created successfully!")
        print("=" * 50)
        print("   管理员账号信息 / Admin Account:")
        print("=" * 50)
        print(f"   邮箱 / Email: {ADMIN_EMAIL}")
        print(f"   密码 / Password: {ADMIN_PASSWORD}")
        print(f"   角色 / Role: admin (super)")
        print("=" * 50)
        print("\n⚠️  安全提示：请在首次登录后立即修改密码！")
        print("⚠️  Security: Please change the password after first login!")

if __name__ == "__main__":
    asyncio.run(init_admin_account())
