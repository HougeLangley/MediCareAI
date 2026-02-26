"""
认证 API 端点 - 用户认证、注册、个人信息管理
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Request
from typing import Optional, Dict, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime, timedelta

from app.db.database import get_db
from app.schemas.user import UserLogin, UserCreate, UserResponse, UserUpdate
from app.services.user_service import UserService
from app.core.deps import get_current_active_user
from app.models.models import User
from app.core.i18n import get_message

import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """用户注册 - 创建用户账户和患者档案，返回成功信息（不自动登录）"""
    from app.schemas.patient import PatientCreate
    from app.services.patient_service import PatientService

    user_service = UserService(db)

    # 1. 创建用户账户（包含地址信息）
    user = await user_service.create_user(
        email=user_data.email,
        password=user_data.password,
        full_name=user_data.full_name,
        address=user_data.address,  # 添加地址
    )

    # 2. 创建患者档案（如果有提供额外信息）
    if any(
        [
            user_data.date_of_birth,
            user_data.gender,
            user_data.phone,
            user_data.emergency_contact_name,
            user_data.emergency_contact_phone,
            user_data.address,  # 地址也作为创建患者档案的条件
        ]
    ):
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
                date_of_birth = datetime.strptime(
                    user_data.date_of_birth, "%Y-%m-%d"
                ).date()
            except ValueError:
                logger.warning(f"日期格式无效: {user_data.date_of_birth}")

        # 创建患者档案（包含地址）
        patient_data = PatientCreate(
            date_of_birth=date_of_birth,
            gender=user_data.gender,
            phone=user_data.phone,
            address=user_data.address,  # 添加地址到患者档案
            emergency_contact=emergency_contact if emergency_contact else None,
        )

        try:
            await patient_service.create_patient(
                patient_data=patient_data, user_id=user.id
            )
            logger.info(f"患者档案创建成功，用户ID: {user.id}")
        except Exception as e:
            # 患者档案创建失败不阻止注册成功
            logger.warning(f"患者档案创建失败（非阻塞）: {e}")

    # 3. 返回成功信息（不返回登录令牌，不自动登录）
    return {
        "message": "注册成功，请登录",
        "user_id": str(user.id),
        "email": user.email,
    }
class LoginRequest(BaseModel):
    """Login request with optional platform parameter / 带可选平台参数的登录请求"""

    email: EmailStr
    password: str
    platform: Optional[str] = Field(None, pattern="^(patient|doctor|admin)$")


@router.post("/login")
async def login(
    login_data: LoginRequest,
    request: Request,  # Add request to get Accept-Language header
    db: AsyncSession = Depends(get_db),
    platform: Optional[str] = None,  # Allow platform from header as fallback
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
        login_data.email, login_data.password, platform=target_platform
    )

    # 验证用户是否有权限访问目标平台
    allowed_platforms = _get_available_platforms(user.role)
    if target_platform not in allowed_platforms:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied. {user.role} accounts can only login through {', '.join(allowed_platforms)} platform(s).",
        )

    # 特别检查：医生登录 doctor 平台时，必须已通过认证
    if user.role == "doctor" and target_platform == "doctor" and not user.is_verified_doctor:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=get_message("doctor_verification_pending", request),
        )

    return {
        "user": user,
        "tokens": tokens,
        "platform": target_platform,
        "available_platforms": allowed_platforms,
    }


class RefreshTokenRequest(BaseModel):
    refresh_token: str


@router.post("/refresh")
async def refresh_token(
    request_data: RefreshTokenRequest, db: AsyncSession = Depends(get_db)
):
    """
    刷新访问令牌
    Refresh access token using refresh token
    """
    from app.core.security import verify_token, create_token_for_user
    from app.core.config import settings
    import jwt

    try:
        # Verify the refresh token
        payload = jwt.decode(
            request_data.refresh_token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )

        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type"
            )

        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )

        # Get user from database
        user_service = UserService(db)
        user = await user_service.get_user_by_id(user_id)

        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
            )

        # Get platform from token or default to patient
        platform = payload.get("platform", "patient")

        # Create new tokens
        tokens = create_token_for_user(user.id, user.email, user.role, platform)

        return {
            "access_token": tokens["access_token"],
            "refresh_token": tokens["refresh_token"],
            "token_type": "bearer",
            "expires_in": tokens["expires_in"],
        }

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token has expired"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, str]:
    """用户登出"""
    user_service = UserService(db)
    await user_service.logout_user(current_user.id)
    return {"message": "Successfully logged out"}


@router.get("/me")
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user),
) -> dict:
    """
    获取当前用户信息
    Get current user information including platform details
    """
    current_platform = getattr(current_user, "_platform", "patient")

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
            "patient": current_user.role == "patient",
            "doctor": current_user.role == "doctor",
            "admin": current_user.role == "admin",
        },
        # Include role-specific fields
        **(
            {
                "date_of_birth": current_user.date_of_birth.isoformat()
                if current_user.date_of_birth
                else None,
                "gender": current_user.gender,
                "phone": current_user.phone,
                "address": current_user.address,
                "emergency_contact": current_user.emergency_contact,
            }
            if current_user.role == "patient"
            else {}
        ),
        **(
            {
                "title": current_user.title,
                "department": current_user.department,
                "professional_type": current_user.professional_type,
                "specialty": current_user.specialty,
                "hospital": current_user.hospital,
                "license_number": current_user.license_number,
                "phone": current_user.phone,
                "is_verified_doctor": current_user.is_verified_doctor,
                "display_name": current_user.display_name,
            }
            if current_user.role == "doctor"
            else {}
        ),
        **(
            {"admin_level": current_user.admin_level}
            if current_user.role == "admin"
            else {}
        ),
    }


@router.put("/me")
async def update_current_user_info(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
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
                "full_name": current_user.full_name,
            },
        }

    # 更新用户信息
    updated_user = await user_service.update_user(
        str(current_user.id),
        update_data,  # 传递字典而不是 UserUpdate 对象
    )

    return {"message": "用户信息更新成功", "user": updated_user}


@router.post("/change-password")
async def change_password(
    password_data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """修改密码（临时禁用）"""
    return {"message": "密码修改功能暂未启用"}


class PlatformSwitchRequest(BaseModel):
    """Platform switch request schema / 平台切换请求模式"""

    platform: str = Field(..., pattern="^(patient|doctor|admin)$")


@router.post("/switch-platform")
async def switch_platform(
    platform_data: PlatformSwitchRequest,
    request: Request,  # Add request to get Accept-Language header
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    切换用户平台 / Switch user platform
    Validates user has permission to access the target platform
    验证用户是否有权限访问目标平台
    """
    from app.core.security import create_token_for_user

    # Enhanced platform access validation with detailed error messages
    # 增强平台访问验证，提供详细错误信息

    current_platform = getattr(current_user, "_platform", "patient")

    # Check if user has permission for target platform
    # 检查用户是否有目标平台权限
    available_platforms = _get_available_platforms(current_user.role)

    if platform_data.platform not in available_platforms:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"作为 {current_user.role} 用户，您无法访问 {platform_data.platform} 平台。可用平台: {', '.join(available_platforms)}",
        )

    # 特别检查：医生切换到 doctor 平台时，必须已通过认证
    if current_user.role == "doctor" and platform_data.platform == "doctor" and not current_user.is_verified_doctor:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=get_message("doctor_verification_pending", request),
        )

    # Check if already on the target platform
    # 检查是否已在目标平台
    if current_platform == platform_data.platform:
        return {
            "message": f"您已在 {platform_data.platform} 平台",
            "tokens": None,  # No new tokens needed
            "platform": current_platform,
            "no_change": True,
        }

    # Log the platform switch for audit purposes
    # 记录平台切换用于审计目的
    logger.info(
        f"用户 {current_user.email} 从 {current_platform} 平台切换到 {platform_data.platform} 平台"
    )

    # Create new tokens with the requested platform
    # 使用请求的平台创建新令牌
    new_tokens = create_token_for_user(
        current_user.id, current_user.email, current_user.role, platform_data.platform
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
        "switched_at": datetime.utcnow().isoformat(),
    }


@router.get("/platforms")
async def get_available_platforms(
    current_user: User = Depends(get_current_active_user),
) -> dict:
    """
    获取当前用户可访问的所有平台列表 / Get available platforms for current user
    """
    available_platforms = _get_available_platforms(current_user.role)
    current_platform = getattr(current_user, "_platform", "patient")

    return {
        "user_id": str(current_user.id),
        "role": current_user.role,
        "current_platform": current_platform,
        "available_platforms": available_platforms,
        "platform_permissions": {
            "patient": current_user.role in ["patient", "doctor", "admin"],
            "doctor": current_user.role in ["doctor", "admin"],
            "admin": current_user.role == "admin",
        },
    }


@router.get("/verify-token")
async def verify_token(current_user: User = Depends(get_current_active_user)) -> dict:
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
        "available_platforms": _get_available_platforms(current_user.role),
    }


def _get_available_platforms(role: str) -> list[str]:
    """根据用户角色获取可用平台列表 / Get available platforms based on user role

    为了安全，每个角色只能访问对应的平台：
    - admin 只能访问 admin 平台
    - doctor 只能访问 doctor 平台
    - patient 只能访问 patient 平台
    """
    if role == "admin":
        return ["admin"]
    elif role == "doctor":
        return ["doctor"]
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


@router.post(
    "/register/doctor", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register_doctor(
    email: str = Form(...),
    password: str = Form(...),
    full_name: str = Form(...),
    title: str = Form(...),
    department: str = Form(...),
    professional_type: str = Form(...),
    specialty: str = Form(...),
    hospital: str = Form(...),
    license_number: str = Form(...),
    phone: Optional[str] = Form(None),
    files: List[UploadFile] = File(default=[]),
    db: AsyncSession = Depends(get_db),
):
    """
    医生注册 - 创建医生账户（需要管理员审核）
    Doctor registration - Creates doctor account (requires admin approval)
    Supports uploading multiple license documents.
    """
    from datetime import datetime
    import os
    from app.core.config import settings
    from app.models.models import DoctorVerification

    user_service = UserService(db)

    existing_user = await user_service.get_user_by_email(email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="邮箱已被注册"
        )

    stmt = select(User).where(User.license_number == license_number)
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="该执业证书号已被注册"
        )

    from app.core.security import get_password_hash

    user = User(
        email=email,
        password_hash=get_password_hash(password),
        full_name=full_name,
        role="doctor",
        title=title,
        department=department,
        professional_type=professional_type,
        specialty=specialty,
        hospital=hospital,
        license_number=license_number,
        phone=phone,
        is_verified=False,
        is_verified_doctor=False,
        display_name=None,
    )

    saved_files = []
    uploaded_files_info = []

    try:
        db.add(user)
        await db.commit()
        await db.refresh(user)

        if files:
            allowed_types = [
                "application/pdf",
                "image/jpeg",
                "image/jpg",
                "image/png",
            ]
            max_size = 10 * 1024 * 1024
            upload_dir = os.path.join(settings.upload_path, "doctor_licenses")
            os.makedirs(upload_dir, exist_ok=True)

            for idx, file in enumerate(files):
                if file.content_type not in allowed_types:
                    continue

                content = await file.read()
                file_size = len(content)

                if file_size > max_size:
                    continue

                file_ext = os.path.splitext(file.filename)[1].lower()
                unique_filename = f"license_{user.id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{idx}{file_ext}"
                file_path = os.path.join(upload_dir, unique_filename)

                with open(file_path, "wb") as buffer:
                    buffer.write(content)

                saved_files.append(file_path)
                uploaded_files_info.append(
                    {
                        "original_name": file.filename,
                        "saved_name": unique_filename,
                        "size": file_size,
                    }
                )

        verification = DoctorVerification(
            user_id=user.id,
            license_number=license_number,
            specialty=specialty,
            hospital=hospital,
            status="pending",
            submitted_at=datetime.utcnow(),
            license_document_path=",".join(saved_files) if saved_files else None,
            license_document_filename=",".join(
                [f["original_name"] for f in uploaded_files_info]
            )
            if uploaded_files_info
            else None,
        )
        db.add(verification)
        await db.commit()

        logger.info(
            f"医生注册成功: {email}, 上传了 {len(uploaded_files_info)} 个证书文件, 等待审核"
        )

        return user
    except Exception as e:
        logger.error(f"医生注册失败: {e}")
        for file_path in saved_files:
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except:
                    pass
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="医生注册失败"
        )


# ============== Role Verification Status / 角色认证状态 ==============


@router.get("/verification-status")
async def get_verification_status(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
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

    if current_user.role == "doctor":
        status_info.update(
            {
                "doctor_verified": current_user.is_verified_doctor,
                "title": current_user.title,
                "department": current_user.department,
                "hospital": current_user.hospital,
                "specialty": current_user.specialty,
                "display_name": current_user.display_name,
                "verification_status": "approved"
                if current_user.is_verified_doctor
                else "pending",
            }
        )

    return status_info


# ============== Admin: Verify Doctor / 管理员: 审核医生 ==============


@router.post("/admin/verify-doctor/{doctor_id}")
async def verify_doctor(
    doctor_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    管理员审核医生账户（仅管理员）
    Admin verifies doctor account (admin only)
    """
    # Check if current user is admin
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="只有管理员可以审核医生"
        )

    # Get doctor
    user_service = UserService(db)
    doctor = await user_service.get_user_by_id(str(doctor_id))

    if not doctor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="医生不存在")

    if doctor.role != "doctor":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="该用户不是医生"
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
        "verified_by": current_user.full_name,
    }


@router.get("/admin/pending-doctors")
async def get_pending_doctors(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    """
    获取待审核的医生列表（仅管理员）
    Get list of pending doctors (admin only)
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="只有管理员可以查看待审核医生"
        )

    from sqlalchemy import select

    stmt = select(User).where(User.role == "doctor", User.is_verified_doctor == False)
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
            "created_at": doctor.created_at.isoformat() if doctor.created_at else None,
        }
        for doctor in pending_doctors
    ]



# =============================================================================
# Email Verification Endpoints | 邮箱验证端点
# =============================================================================

@router.post("/send-verification-email")
async def send_verification_email(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    发送邮箱验证邮件 | Send Email Verification
    
    - 生成验证token并发送到用户邮箱
    - 限制发送频率（1分钟内只能发送一次）
    """
    from app.services.email_service import temail_service
    from app.core.config import settings
    
    # 检查是否已经验证
    if current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已经验证 / Email already verified"
        )
    
    # 检查发送频率限制（1分钟内只能发送一次）
    if current_user.email_verification_sent_at:
        time_since_last_send = datetime.utcnow() - current_user.email_verification_sent_at
        if time_since_last_send < timedelta(minutes=1):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="发送太频繁，请1分钟后再试 / Too frequent, please try again in 1 minute"
            )
    
    # 构建验证链接基础URL
    base_url = settings.frontend_url
    
    # 发送验证邮件
    token = await temail_service.send_verification_email(db, current_user, base_url)
    
    if token:
        return {
            "message": "验证邮件已发送 / Verification email sent",
            "email": current_user.email,
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="邮件发送失败，请稍后重试 / Failed to send email, please try again later"
        )


@router.get("/verify-email")
async def verify_email(
    token: str,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    验证邮箱 | Verify Email
    
    - 通过token验证用户邮箱
    - token有效期为24小时
    """
    from sqlalchemy import select
    
    # 查找用户
    stmt = select(User).where(User.email_verification_token == token)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的验证链接 / Invalid verification link"
        )
    
    # 检查token是否过期（24小时）
    if user.email_verification_sent_at:
        time_since_sent = datetime.utcnow() - user.email_verification_sent_at
        if time_since_sent > timedelta(hours=24):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="验证链接已过期，请重新发送 / Verification link expired, please resend"
            )
    
    # 更新用户验证状态
    user.is_verified = True
    user.email_verified_at = datetime.utcnow()
    user.email_verification_token = None
    
    await db.commit()
    
    return {
        "message": "邮箱验证成功 / Email verified successfully",
        "email": user.email,
    }


@router.post("/forgot-password")
async def forgot_password(
    email: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    请求密码重置 | Request Password Reset
    
    - 发送密码重置邮件到用户邮箱
    - 无论邮箱是否存在都返回成功（防止邮箱枚举攻击）
    """
    from sqlalchemy import select
    from app.services.email_service import temail_service
    from app.core.config import settings
    
    # 查找用户
    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    # 即使用户不存在也返回成功（防止邮箱枚举攻击）
    if not user:
        return {
            "message": "如果该邮箱存在，重置邮件已发送 / If the email exists, reset email has been sent"
        }
    
    # 检查发送频率限制（5分钟内只能发送一次）
    if user.password_reset_sent_at:
        time_since_last_send = datetime.utcnow() - user.password_reset_sent_at
        if time_since_last_send < timedelta(minutes=5):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="发送太频繁，请5分钟后再试 / Too frequent, please try again in 5 minutes"
            )
    
    # 构建重置链接基础URL
    base_url = settings.frontend_url
    
    # 发送重置邮件
    token = await temail_service.send_password_reset_email(db, user, base_url)
    
    if token:
        return {
            "message": "重置邮件已发送 / Reset email sent",
            "email": email,
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="邮件发送失败，请稍后重试 / Failed to send email, please try again later"
        )


@router.post("/reset-password")
async def reset_password(
    token: str,
    new_password: str,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    重置密码 | Reset Password
    
    - 通过token重置用户密码
    - token有效期为1小时
    """
    from sqlalchemy import select
    from app.core.security import get_password_hash
    
    # 查找用户
    stmt = select(User).where(User.password_reset_token == token)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的重置链接 / Invalid reset link"
        )
    
    # 检查token是否过期（1小时）
    if user.password_reset_sent_at:
        time_since_sent = datetime.utcnow() - user.password_reset_sent_at
        if time_since_sent > timedelta(hours=1):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="重置链接已过期，请重新请求 / Reset link expired, please request again"
            )
    
    # 验证密码长度
    if len(new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="密码长度至少为6个字符 / Password must be at least 6 characters"
        )
    
    # 更新密码
    user.password_hash = get_password_hash(new_password)
    user.password_reset_token = None
    user.password_reset_sent_at = None
    
    await db.commit()
    
    return {
        "message": "密码重置成功 / Password reset successfully",
    }
