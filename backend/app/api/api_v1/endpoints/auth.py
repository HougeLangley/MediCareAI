"""
认证 API 端点 - 用户认证、注册、个人信息管理
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict

from app.db.database import get_db
from app.schemas.user import UserLogin, UserCreate, UserResponse, UserUpdate
from app.services.user_service import UserService
from app.core.deps import get_current_active_user
from app.models.models import User

import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)) -> User:
    """用户注册 - 同时创建用户账户和患者档案"""
    from datetime import datetime
    from app.schemas.patient import PatientCreate
    from app.services.patient_service import PatientService
    
    user_service = UserService(db)
    
    # 1. 创建用户账户
    user = await user_service.create_user(
        email=user_data.email,
        password=user_data.password,
        full_name=user_data.full_name
    )
    
    # 2. 创建患者档案（如果有提供额外信息）
    if any([user_data.date_of_birth, user_data.gender, user_data.phone, 
            user_data.emergency_contact_name, user_data.emergency_contact_phone]):
        patient_service = PatientService(db)
        
        # 组合紧急联系人信息
        emergency_contact = None
        if user_data.emergency_contact_name or user_data.emergency_contact_phone:
            name = user_data.emergency_contact_name or ""
            phone = user_data.emergency_contact_phone or ""
            emergency_contact = f"{name} {phone}".strip()
        
        # 转换日期字符串为 date 对象
        date_of_birth = None
        if user_data.date_of_birth:
            try:
                date_of_birth = datetime.strptime(user_data.date_of_birth, "%Y-%m-%d").date()
            except ValueError:
                logger.warning(f"日期格式无效: {user_data.date_of_birth}")
        
        # 创建患者档案
        patient_data = PatientCreate(
            date_of_birth=date_of_birth,
            gender=user_data.gender,
            phone=user_data.phone,
            emergency_contact=emergency_contact if emergency_contact else None
        )
        
        try:
            await patient_service.create_patient(
                patient_data=patient_data,
                user_id=user.id
            )
            logger.info(f"患者档案创建成功，用户ID: {user.id}")
        except Exception as e:
            # 患者档案创建失败不阻止注册成功
            logger.warning(f"患者档案创建失败（非阻塞）: {e}")
    
    return user


@router.post("/login")
async def login(user_credentials: UserLogin, db: AsyncSession = Depends(get_db)):
    """用户登录"""
    user_service = UserService(db)
    user, tokens = await user_service.authenticate_user(
        user_credentials.email,
        user_credentials.password
    )
    return {
        "user": user,
        "tokens": tokens
    }


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, str]:
    """用户登出"""
    user_service = UserService(db)
    await user_service.logout_user(current_user.id)
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)) -> User:
    """获取当前用户信息"""
    return current_user


@router.put("/me")
async def update_current_user_info(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """更新当前用户信息"""
    user_service = UserService(db)
    
    # 只更新提供的字段
    update_data = user_update.model_dump(exclude_unset=True)
    
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
    updated_user = await user_service.update_user(
        str(current_user.id),
        update_data  # 传递字典而不是 UserUpdate 对象
    )
    
    return {
        "message": "用户信息更新成功",
        "user": updated_user
    }


@router.post("/change-password")
async def change_password(
    password_data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """修改密码（临时禁用）"""
    return {"message": "密码修改功能暂未启用"}
