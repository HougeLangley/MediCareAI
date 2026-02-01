from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import get_db
from app.schemas.user import UserLogin
from typing import Dict
from datetime import datetime
from app.models.models import User

router = APIRouter()

@router.post("/login")
async def login(user_credentials: UserLogin, db: AsyncSession = Depends(get_db)):
    """
    简化的登录端点，暂时不使用JWT
    """
    try:
        # 使用原生SQL查询用户
        result = await db.execute(
            select(User).where(User.email == user_credentials.email)
        )

        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="邮箱或密码错误"
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="账号已被禁用"
            )

        # 验证密码
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
        
        if not pwd_context.verify(user_credentials.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="邮箱或密码错误"
            )

        # 更新最后登录时间
        user.last_login = datetime.utcnow()

        # 返回用户信息（暂时不使用JWT）
        return {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "access_token": str(user.id),  # 暂时使用用户ID作为token
            "token_type": "user_id",  # 标识这是用户ID，不是真正的JWT token
            "expires_in": "never",  # 暂时不设置过期时间
            "message": "登录成功（演示版本）"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"登录失败：{str(e)}"
        )
