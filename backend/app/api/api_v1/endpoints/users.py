"""
用户管理 API 端点
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional

from app.db.database import get_db
from app.core.deps import get_current_active_user
from app.models.models import User
from app.services.user_service import UserService

router = APIRouter()


class UserUpdateRequest(BaseModel):
    """用户信息更新请求"""
    full_name: Optional[str] = None


@router.get("/me")
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取当前用户信息
    """
    user_service = UserService(db)
    
    try:
        # 获取完整的用户信息（包括患者统计）
        user_info = {
            "id": str(current_user.id),
            "email": current_user.email,
            "full_name": current_user.full_name,
            "is_active": current_user.is_active,
            "is_verified": current_user.is_verified,
            "created_at": current_user.created_at.isoformat(),
            "last_login": current_user.last_login.isoformat() if current_user.last_login else None
        }
        
        return user_info
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取用户信息失败: {str(e)}"
        )


@router.put("/me")
async def update_current_user_info(
    user_update: UserUpdateRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    更新当前用户信息
    """
    user_service = UserService(db)
    
    try:
        # 过滤掉 None 值
        update_data = user_update.model_dump(exclude_unset=True)
        
        # 如果没有字段需要更新，直接返回
        if not update_data:
            return {
                "message": "没有需要更新的字段",
                "user": {
                    "id": str(current_user.id),
                    "email": current_user.email,
                    "full_name": current_user.full_name
                }
            }
        
        # 更新用户信息
        user = await user_service.update_user(
            str(current_user.id),
            UserUpdateRequest(**update_data)
        )
        
        return {
            "message": "用户信息更新成功",
            "user": {
                "id": str(user.id),
                "email": user.email,
                "full_name": user.full_name
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新用户信息失败: {str(e)}"
        )


@router.post("/change-password")
async def change_password(
    current_password: str,
    new_password: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    修改密码
    """
    user_service = UserService(db)
    
    try:
        await user_service.change_password(
            str(current_user.id),
            current_password,
            new_password
        )
        
        return {
            "message": "密码修改成功"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"修改密码失败: {str(e)}"
        )
