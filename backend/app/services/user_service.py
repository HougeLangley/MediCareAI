"""
用户服务 - 用户管理、认证
"""
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from passlib.context import CryptContext
from datetime import datetime, timedelta

from app.db.database import get_db, Base
from app.models.models import User, UserSession
from app.core.config import settings
from app.core.security import get_password_hash, verify_password, create_token_for_user

import logging

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    """用户服务类"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """根据 ID 获取用户"""
        try:
            stmt = select(User).where(User.id == user_id)
            result = await self.db.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"获取用户失败: {e}")
            return None

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        try:
            stmt = select(User).where(User.email == email)
            result = await self.db.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"根据邮箱获取用户失败: {e}")
            return None

    async def create_user(self, email: str, password: str, full_name: str) -> User:
        """创建新用户"""
        # 检查邮箱是否已存在
        existing_user = await self.get_user_by_email(email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已被注册"
            )

        password_hash = get_password_hash(password)

        user = User(
            email=email,
            password_hash=password_hash,
            full_name=full_name
        )

        try:
            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)
            return user
        except Exception as e:
            logger.error(f"创建用户失败: {e}")
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="创建用户失败"
            )

    async def authenticate_user(self, email: str, password: str) -> tuple[User, dict]:
        """用户认证"""
        try:
            user = await self.get_user_by_email(email)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="邮箱或密码不正确"
                )

            if not verify_password(password, user.password_hash):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="邮箱或密码不正确"
                )

            if not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="账户已被禁用"
                )

            # 更新最后登录时间
            user.last_login = datetime.utcnow()
            await self.db.commit()

            # 创建令牌
            tokens = create_token_for_user(user.id, user.email)

            # 清理该用户的旧会话
            try:
                stmt = select(UserSession).where(UserSession.user_id == user.id)
                result = await self.db.execute(stmt)
                old_sessions = result.scalars().all()
                for session in old_sessions:
                    session.is_active = False

                # 创建新会话
                session = UserSession(
                    user_id=user.id,
                    token_id=tokens["access_token"][:50],  # 存储部分令牌作为标识
                    expires_at=datetime.utcnow() + timedelta(minutes=30)  # 与访问令牌过期时间一致
                )
                self.db.add(session)
                await self.db.commit()
            except Exception as e:
                logger.error(f"创建会话失败: {e}")
                await self.db.rollback()
                # 即使会话创建失败，仍然返回令牌

            return user, tokens

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"用户认证失败: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="用户认证失败"
            )

    async def update_user(self, user_id: str, user_data: dict) -> User:
        """更新用户信息"""
        try:
            user = await self.get_user_by_id(user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="用户不存在"
                )

            # 只更新提供的字段
            update_data = user_data
            for field, value in update_data.items():
                if hasattr(user, field):
                    setattr(user, field, value)

            await self.db.commit()
            await self.db.refresh(user)
            return user
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"更新用户信息失败: {e}")
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="更新用户信息失败"
            )

    async def change_password(self, user_id: str, current_password: str, new_password: str) -> bool:
        """修改密码"""
        try:
            user = await self.get_user_by_id(user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="用户不存在"
                )

            if not verify_password(current_password, user.password_hash):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="当前密码不正确"
                )

            user.password_hash = get_password_hash(new_password)
            await self.db.commit()
            return True
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"修改密码失败: {e}")
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="修改密码失败"
            )

    async def logout_user(self, user_id: str) -> bool:
        """用户登出"""
        try:
            stmt = select(UserSession).where(UserSession.user_id == user_id, UserSession.is_active == True)
            result = await self.db.execute(stmt)
            sessions = result.scalars().all()

            for session in sessions:
                session.is_active = False

            await self.db.commit()
            return True
        except Exception as e:
            logger.error(f"用户登出失败: {e}")
            await self.db.rollback()
            return False
