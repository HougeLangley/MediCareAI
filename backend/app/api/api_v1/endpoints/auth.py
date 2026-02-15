"""
认证 API 端点 - 用户认证、注册、个人信息管理
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict
import uuid

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


class LoginRequest(BaseModel):
    """Login request with optional platform parameter / 带可选平台参数的登录请求"""
    email: EmailStr
    password: str
    platform: Optional[str] = Field(None, pattern="^(patient|doctor|admin)$")


@router.post("/login")
async def login(
    login_data: LoginRequest, 
    db: AsyncSession = Depends(get_db),
    platform: Optional[str] = None  # Allow platform from header as fallback
):
    """
    用户登录 - 支持平台选择
    User login - Support platform selection
    Platform can be provided in request body or via 'X-Platform' header
    """
    # Determine platform priority: body > header > default
    # 平台优先级：请求体 > 请求头 > 默认值
    target_platform = login_data.platform or platform or "patient"
    
    user_service = UserService(db)
    user, tokens = await user_service.authenticate_user(
        login_data.email,
        login_data.password,
        platform=target_platform
    )
    
    return {
        "user": user,
        "tokens": tokens,
        "platform": target_platform,
        "available_platforms": _get_available_platforms(user.role)
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


@router.get("/me")
async def get_current_user_info(current_user: User = Depends(get_current_active_user)) -> dict:
    """
    获取当前用户信息
    Get current user information including platform details
    """
    current_platform = getattr(current_user, '_platform', 'patient')
    
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role,
        "is_active": current_user.is_active,
        "is_verified": current_user.is_verified,
        "current_platform": current_platform,
        "available_platforms": _get_available_platforms(current_user.role),
        "platform_permissions": {
            "patient": current_user.role in ["patient", "doctor", "admin"],
            "doctor": current_user.role in ["doctor", "admin"], 
            "admin": current_user.role == "admin"
        },
        # Include role-specific fields
        **({
            "date_of_birth": current_user.date_of_birth.isoformat() if current_user.date_of_birth else None,
            "gender": current_user.gender,
            "phone": current_user.phone,
            "address": current_user.address,
            "emergency_contact": current_user.emergency_contact
        } if current_user.role == "patient" else {}),
        **({
            "title": current_user.title,
            "department": current_user.department,
            "professional_type": current_user.professional_type,
            "specialty": current_user.specialty,
            "hospital": current_user.hospital,
            "license_number": current_user.license_number,
            "phone": current_user.phone,
            "is_verified_doctor": current_user.is_verified_doctor,
            "display_name": current_user.display_name
        } if current_user.role == "doctor" else {}),
        **({
            "admin_level": current_user.admin_level
        } if current_user.role == "admin" else {})
    }


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


class PlatformSwitchRequest(BaseModel):
    """Platform switch request schema / 平台切换请求模式"""
    platform: str = Field(..., pattern="^(patient|doctor|admin)$")


@router.post("/switch-platform")
async def switch_platform(
    platform_data: PlatformSwitchRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    切换用户平台 / Switch user platform
    Validates user has permission to access the target platform
    验证用户是否有权限访问目标平台
    """
    from app.core.security import create_token_for_user
    
    # Enhanced platform access validation with detailed error messages
    # 增强平台访问验证，提供详细错误信息
    
    current_platform = getattr(current_user, '_platform', 'patient')
    
    # Check if user has permission for target platform
    # 检查用户是否有目标平台权限
    available_platforms = _get_available_platforms(current_user.role)
    
    if platform_data.platform not in available_platforms:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"作为 {current_user.role} 用户，您无法访问 {platform_data.platform} 平台。可用平台: {', '.join(available_platforms)}"
        )
    
    # Check if already on the target platform
    # 检查是否已在目标平台
    if current_platform == platform_data.platform:
        return {
            "message": f"您已在 {platform_data.platform} 平台",
            "tokens": None,  # No new tokens needed
            "platform": current_platform,
            "no_change": True
        }
    
    # Log the platform switch for audit purposes
    # 记录平台切换用于审计目的
    logger.info(f"用户 {current_user.email} 从 {current_platform} 平台切换到 {platform_data.platform} 平台")
    
    # Create new tokens with the requested platform
    # 使用请求的平台创建新令牌
    new_tokens = create_token_for_user(
        current_user.id, 
        current_user.email, 
        current_user.role, 
        platform_data.platform
    )
    
    # Update user session with new platform (if session tracking is used)
    # 如果使用会话跟踪，用新平台更新用户会话
    try:
        from app.services.user_service import UserService
        user_service = UserService(db)
        await user_service.logout_user(str(current_user.id))  # Clear old sessions
    except Exception as e:
        logger.warning(f"清理旧会话失败（非阻塞）: {e}")
    
    return {
        "message": "平台切换成功",
        "tokens": new_tokens,
        "previous_platform": current_platform,
        "current_platform": platform_data.platform,
        "available_platforms": available_platforms,
        "switched_at": datetime.utcnow().isoformat()
    }


@router.get("/platforms")
async def get_available_platforms(
    current_user: User = Depends(get_current_active_user)
) -> dict:
    """
    获取当前用户可访问的所有平台列表 / Get available platforms for current user
    """
    available_platforms = _get_available_platforms(current_user.role)
    current_platform = getattr(current_user, '_platform', 'patient')
    
    return {
        "user_id": str(current_user.id),
        "role": current_user.role,
        "current_platform": current_platform,
        "available_platforms": available_platforms,
        "platform_permissions": {
            "patient": current_user.role in ["patient", "doctor", "admin"],
            "doctor": current_user.role in ["doctor", "admin"], 
            "admin": current_user.role == "admin"
        }
    }


@router.get("/verify-token")
async def verify_token(
    current_user: User = Depends(get_current_active_user)
) -> dict:
    """
    验证当前token并返回用户平台和权限信息 / Verify current token and return user platform and permissions
    """
    from app.core.security import verify_token
    from fastapi import Depends
    from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
    
    # This will be populated by the dependency system
    # For now, return current user info
    return {
        "user_id": str(current_user.id),
        "email": current_user.email,
        "role": current_user.role,
        "is_active": current_user.is_active,
        "is_verified": current_user.is_verified,
        "available_platforms": _get_available_platforms(current_user.role)
    }


def _get_available_platforms(role: str) -> list[str]:
    """根据用户角色获取可用平台列表 / Get available platforms based on user role"""
    if role == "admin":
        return ["patient", "doctor", "admin"]
    elif role == "doctor":
        return ["patient", "doctor"]
    else:  # patient
        return ["patient"]


# ============== Doctor Registration / 医生注册 ==============

class DoctorRegistrationRequest(BaseModel):
    """Doctor registration request schema / 医生注册请求模式"""
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str
    title: str  # 职称: 主任医师, 副主任医师, etc.
    department: str  # 科室
    professional_type: str  # 专业类型: 内科, 外科, 儿科, etc.
    specialty: str  # 专业领域
    hospital: str  # 医疗机构
    license_number: str  # 执业证书号
    phone: Optional[str] = None


@router.post("/register/doctor", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_doctor(
    doctor_data: DoctorRegistrationRequest,
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    医生注册 - 创建医生账户（需要管理员审核）
    Doctor registration - Creates doctor account (requires admin approval)
    """
    from datetime import datetime
    user_service = UserService(db)
    
    # Check if email exists
    existing_user = await user_service.get_user_by_email(doctor_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已被注册"
        )
    
    # Check if license number is already registered
    from sqlalchemy import select
    stmt = select(User).where(User.license_number == doctor_data.license_number)
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该执业证书号已被注册"
        )
    
    # Create doctor user
    from app.core.security import get_password_hash
    user = User(
        email=doctor_data.email,
        password_hash=get_password_hash(doctor_data.password),
        full_name=doctor_data.full_name,
        role='doctor',
        title=doctor_data.title,
        department=doctor_data.department,
        professional_type=doctor_data.professional_type,
        specialty=doctor_data.specialty,
        hospital=doctor_data.hospital,
        license_number=doctor_data.license_number,
        phone=doctor_data.phone,
        is_verified=False,  # Doctors need admin verification
        is_verified_doctor=False,
        display_name=None  # Let doctors set their own display name in profile
    )
    
    try:
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
        # Create doctor verification record
        from app.models.models import DoctorVerification
        verification = DoctorVerification(
            user_id=user.id,
            license_number=doctor_data.license_number,
            specialty=doctor_data.specialty,
            hospital=doctor_data.hospital,
            status='pending',
            submitted_at=datetime.utcnow()
        )
        db.add(verification)
        await db.commit()
        
        logger.info(f"医生注册成功: {doctor_data.email}, 等待审核, verification_id: {verification.id}")
        
        return user
    except Exception as e:
        logger.error(f"医生注册失败: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="医生注册失败"
        )


# ============== Role Verification Status / 角色认证状态 ==============

@router.get("/verification-status")
async def get_verification_status(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    获取当前用户的认证状态
    Get current user's verification status
    """
    status_info = {
        "role": current_user.role,
        "is_verified": current_user.is_verified,
        "email_verified": current_user.is_verified,
    }
    
    if current_user.role == 'doctor':
        status_info.update({
            "doctor_verified": current_user.is_verified_doctor,
            "title": current_user.title,
            "department": current_user.department,
            "hospital": current_user.hospital,
            "specialty": current_user.specialty,
            "display_name": current_user.display_name,
            "verification_status": "approved" if current_user.is_verified_doctor else "pending"
        })
    
    return status_info


# ============== Admin: Verify Doctor / 管理员: 审核医生 ==============

@router.post("/admin/verify-doctor/{doctor_id}")
async def verify_doctor(
    doctor_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    管理员审核医生账户（仅管理员）
    Admin verifies doctor account (admin only)
    """
    # Check if current user is admin
    if current_user.role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有管理员可以审核医生"
        )
    
    # Get doctor
    user_service = UserService(db)
    doctor = await user_service.get_user_by_id(str(doctor_id))
    
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="医生不存在"
        )
    
    if doctor.role != 'doctor':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该用户不是医生"
        )
    
    # Verify doctor
    doctor.is_verified = True
    doctor.is_verified_doctor = True
    await db.commit()
    
    logger.info(f"医生已审核通过: {doctor.email} (by {current_user.email})")
    
    return {
        "message": "医生审核通过",
        "doctor_id": str(doctor_id),
        "doctor_name": doctor.full_name,
        "verified_by": current_user.full_name
    }


@router.get("/admin/pending-doctors")
async def get_pending_doctors(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> list[dict]:
    """
    获取待审核的医生列表（仅管理员）
    Get list of pending doctors (admin only)
    """
    if current_user.role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有管理员可以查看待审核医生"
        )
    
    from sqlalchemy import select
    stmt = select(User).where(
        User.role == 'doctor',
        User.is_verified_doctor == False
    )
    result = await db.execute(stmt)
    pending_doctors = result.scalars().all()
    
    return [
        {
            "id": str(doctor.id),
            "email": doctor.email,
            "full_name": doctor.full_name,
            "title": doctor.title,
            "department": doctor.department,
            "hospital": doctor.hospital,
            "specialty": doctor.specialty,
            "license_number": doctor.license_number,
            "created_at": doctor.created_at.isoformat() if doctor.created_at else None
        }
        for doctor in pending_doctors
    ]
