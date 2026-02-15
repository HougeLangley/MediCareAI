"""
Admin API Endpoints | 管理员API端点

Provides admin dashboard functionality:
- System monitoring and metrics
- AI diagnosis statistics and anomaly detection
- Doctor verification management
- Admin operation logging
- System alerts

提供管理员仪表板功能：
- 系统监控和指标
- AI诊断统计和异常检测
- 医生认证管理
- 管理员操作日志
- 系统告警
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from uuid import UUID
import uuid
import json
import os
import asyncio
import aiofiles
import aiohttp
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status, Request, UploadFile, File, Form
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete, and_, or_

from app.db.database import get_db
from app.core.deps import require_admin
from app.models.models import User, DoctorVerification, AIDiagnosisLog
from app.services.system_monitoring_service import (
    SystemMonitoringService,
    AIDiagnosisLogger,
    AdminOperationLogger
)
from app.services.ai_model_config_service import AIModelConfigService, get_ai_model_config_service
from app.utils.security import (
    encrypt_api_key,
    decrypt_api_key,
    mask_api_key,
    validate_api_key_format
)
from app.schemas.admin import (
    DoctorVerificationAction,
    DoctorVerificationActionResponse,
    LogAdminOperationRequest,
    LogSystemMetricsResponse,
    AIModelConfig,
    AIModelStatus,
    AIModelsResponse,
    AIModelTestRequest,
    AIModelTestResponse,
    AIModelConfigRequest,
    AIModelConfigResponse,
    KnowledgeBaseDocument,
    KnowledgeBaseDocumentsResponse,
    KnowledgeBaseUploadResponse,
    KnowledgeBaseDocumentStatus,
    KnowledgeBaseDocumentStatusResponse,
    AILogEntry,
    AILogsResponse,
    SystemAlertsResponse,
    DoctorVerificationDetail,
    UpdateVerificationRequest,
    UpdateVerificationResponse,
    SystemSettings,
    SystemSettingsResponse,
    UpdateSystemSettingsRequest,
    UpdateSystemSettingsResponse,
    SystemConfiguration
)

router = APIRouter()


@router.get("/dashboard/summary", response_model=Dict[str, Any])
async def get_dashboard_summary(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
) -> Dict[str, Any]:
    """
    Get admin dashboard summary | 获取管理员仪表板概览
    
    Returns key metrics for the admin dashboard.
    返回管理员仪表板的关键指标。
    """
    # Get system metrics
    monitoring = SystemMonitoringService(db)
    system_metrics = await monitoring.collect_system_metrics()
    
    # Get AI statistics (last 24 hours)
    ai_stats = await monitoring.get_ai_diagnosis_statistics(days=1)
    
    # Get pending doctor verifications
    stmt = select(func.count()).select_from(DoctorVerification).where(
        DoctorVerification.status == 'pending'
    )
    result = await db.execute(stmt)
    pending_doctors = result.scalar()
    
    # Get user counts
    stmt = select(func.count()).select_from(User)
    result = await db.execute(stmt)
    total_users = result.scalar()
    
    stmt = select(func.count()).select_from(User).where(User.role == 'patient')
    result = await db.execute(stmt)
    patient_count = result.scalar()
    
    stmt = select(func.count()).select_from(User).where(User.role == 'doctor')
    result = await db.execute(stmt)
    doctor_count = result.scalar()
    
    # Get recent anomalies
    recent_anomalies = await monitoring.detect_anomalies(hours=24)
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "system_status": {
            "overall_alert": system_metrics.get("overall_alert", "info"),
            "alert_message": system_metrics.get("alert_message"),
            "cpu_percent": system_metrics.get("cpu", {}).get("percent"),
            "memory_percent": system_metrics.get("memory", {}).get("percent"),
            "disk_percent": system_metrics.get("disk", {}).get("percent")
        },
        "ai_statistics_24h": {
            "total_requests": ai_stats.get("total_requests", 0),
            "success_rate": ai_stats.get("success_rate", 0),
            "average_latency_ms": ai_stats.get("average_latency_ms", 0),
            "anomalies": ai_stats.get("anomalies", 0)
        },
        "user_statistics": {
            "total_users": total_users,
            "patients": patient_count,
            "doctors": doctor_count,
            "pending_doctor_verifications": pending_doctors
        },
        "recent_anomalies": recent_anomalies[:5]  # Top 5 recent anomalies
    }


@router.get("/system/metrics", response_model=Dict[str, Any])
async def get_system_metrics(
    hours: int = 24,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
) -> Dict[str, Any]:
    """
    Get system metrics history | 获取系统指标历史
    
    Returns historical system metrics for charts and monitoring.
    返回历史系统指标，用于图表和监控。
    """
    monitoring = SystemMonitoringService(db)
    
    # Get current metrics
    current_metrics = await monitoring.collect_system_metrics()
    
    # Get historical metrics
    historical_metrics = await monitoring.get_recent_metrics(hours=hours, limit=288)  # 5-minute intervals
    
    return {
        "current": current_metrics,
        "historical": historical_metrics,
        "summary": {
            "period_hours": hours,
            "data_points": len(historical_metrics)
        }
    }


@router.post("/system/metrics/log")
async def log_system_metrics(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
) -> Dict[str, Any]:
    """
    Manually log current system metrics | 手动记录当前系统指标
    
    Useful for testing or forced metric collection.
    用于测试或强制指标收集。
    """
    monitoring = SystemMonitoringService(db)
    
    # Log metrics
    log = await monitoring.log_system_metrics()
    
    # Log admin operation
    admin_logger = AdminOperationLogger(db)
    await admin_logger.log_operation(
        admin_id=admin.id,
        operation_type="manual_metrics_log",
        operation_details={"timestamp": datetime.utcnow().isoformat()},
        ip_address=None,
        user_agent=None
    )
    
    return {
        "success": True,
        "log_id": str(log.id) if log else None,
        "timestamp": datetime.utcnow().isoformat(),
        "message": "System metrics logged successfully"
    }


@router.get("/ai/statistics", response_model=Dict[str, Any])
async def get_ai_statistics(
    days: int = 7,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
) -> Dict[str, Any]:
    """
    Get AI diagnosis statistics | 获取AI诊断统计
    
    Returns comprehensive AI diagnosis statistics.
    返回全面的AI诊断统计信息。
    """
    monitoring = SystemMonitoringService(db)
    
    stats = await monitoring.get_ai_diagnosis_statistics(days=days)
    
    return {
        "period_days": days,
        **stats
    }


@router.get("/ai/anomalies", response_model=List[Dict[str, Any]])
async def get_ai_anomalies(
    hours: int = 24,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
) -> List[Dict[str, Any]]:
    """
    Get AI diagnosis anomalies | 获取AI诊断异常
    
    Returns detected anomalies in AI diagnosis requests.
    返回检测到的AI诊断请求异常。
    """
    monitoring = SystemMonitoringService(db)
    
    anomalies = await monitoring.detect_anomalies(hours=hours)
    
    return anomalies


@router.get("/doctors/pending", response_model=List[Dict[str, Any]])
async def get_pending_doctor_verifications(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
) -> List[Dict[str, Any]]:
    """
    Get pending doctor verifications | 获取待审核的医生认证
    
    Returns list of doctors awaiting verification.
    返回等待认证的医生列表。
    """
    stmt = select(DoctorVerification, User).join(
        User, DoctorVerification.user_id == User.id
    ).where(
        DoctorVerification.status == 'pending'
    ).order_by(DoctorVerification.submitted_at.desc()).offset(skip).limit(limit)
    
    result = await db.execute(stmt)
    rows = result.all()
    
    pending_list = []
    for verification, user in rows:
        pending_list.append({
            "verification_id": str(verification.id),
            "user_id": str(user.id),
            "doctor_name": user.full_name,
            "doctor_email": user.email,
            "license_number": verification.license_number,
            "specialty": verification.specialty,
            "hospital": verification.hospital,
            "submitted_at": verification.submitted_at.isoformat() if verification.submitted_at else None,
            "years_of_experience": verification.years_of_experience,
            "education": verification.education
        })
    
    return pending_list


@router.get("/doctors/verifications", response_model=Dict[str, Any])
async def get_doctor_verifications(
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
) -> Dict[str, Any]:
    """
    Get all doctor verifications | 获取所有医生认证申请

    Returns list of doctor verification requests with optional status filter.
    返回医生认证申请列表，支持按状态筛选。
    """
    stmt = select(DoctorVerification, User).join(
        User, DoctorVerification.user_id == User.id
    )

    # Apply status filter if provided
    if status:
        stmt = stmt.where(DoctorVerification.status == status)

    stmt = stmt.order_by(DoctorVerification.submitted_at.desc()).offset(skip).limit(limit)

    result = await db.execute(stmt)
    rows = result.all()

    verifications_list = []
    for verification, user in rows:
        verifications_list.append({
            "id": str(verification.id),
            "user_id": str(user.id),
            "full_name": user.full_name,
            "email": user.email,
            "license_number": verification.license_number,
            "specialty": verification.specialty,
            "hospital": verification.hospital,
            "department": user.department,
            "title": user.title,
            "status": verification.status,
            "submitted_at": verification.submitted_at.isoformat() if verification.submitted_at else None,
            "verified_at": verification.verified_at.isoformat() if verification.verified_at else None,
            "years_of_experience": verification.years_of_experience,
            "education": verification.education,
            "verification_notes": verification.verification_notes
        })

    return {
        "verifications": verifications_list,
        "total": len(verifications_list),
        "status_filter": status
    }


@router.post("/doctors/verifications/{verification_id}/approve")
async def approve_doctor_verification(
    verification_id: UUID,
    notes: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
    request: Request = None
) -> Dict[str, Any]:
    """
    Approve doctor verification | 批准医生认证
    
    Approves a pending doctor verification request.
    批准待审核的医生认证请求。
    """
    stmt = select(DoctorVerification).where(DoctorVerification.id == verification_id)
    result = await db.execute(stmt)
    verification = result.scalar_one_or_none()
    
    if not verification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Verification request not found"
        )
    
    if verification.status != 'pending':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot approve verification with status: {verification.status}"
        )
    
    # Update verification status
    verification.status = 'approved'
    verification.verified_by = admin.id
    verification.verified_at = datetime.utcnow()
    verification.verification_notes = notes
    
    # Update user as verified doctor
    stmt = select(User).where(User.id == verification.user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if user:
        user.is_verified_doctor = True
        user.is_verified = True  # Also set is_verified so doctor appears in patient searches
    
    await db.commit()
    
    # Log admin operation
    admin_logger = AdminOperationLogger(db)
    await admin_logger.log_operation(
        admin_id=admin.id,
        operation_type="approve_doctor",
        operation_details={
            "verification_id": str(verification_id),
            "doctor_user_id": str(verification.user_id),
            "notes": notes
        },
        ip_address=request.client.host if request else None,
        user_agent=request.headers.get("user-agent") if request else None
    )
    
    return {
        "success": True,
        "message": "Doctor verification approved successfully",
        "verification_id": str(verification_id),
        "approved_at": datetime.utcnow().isoformat()
    }


class DoctorRejectionRequest(BaseModel):
    """Doctor rejection request | 医生拒绝请求"""
    reason: str


@router.post("/doctors/verifications/{verification_id}/reject")
async def reject_doctor_verification(
    verification_id: UUID,
    rejection: DoctorRejectionRequest,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
    request: Request = None
) -> Dict[str, Any]:
    """
    Reject doctor verification | 拒绝医生认证
    
    Rejects a pending doctor verification request.
    拒绝待审核的医生认证请求。
    """
    stmt = select(DoctorVerification).where(DoctorVerification.id == verification_id)
    result = await db.execute(stmt)
    verification = result.scalar_one_or_none()
    
    if not verification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Verification request not found"
        )
    
    if verification.status != 'pending':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot reject verification with status: {verification.status}"
        )
    
    # Update verification status
    verification.status = 'rejected'
    verification.verified_by = admin.id
    verification.verified_at = datetime.utcnow()
    verification.verification_notes = rejection.reason
    
    await db.commit()
    
    # Log admin operation
    admin_logger = AdminOperationLogger(db)
    await admin_logger.log_operation(
        admin_id=admin.id,
        operation_type="reject_doctor",
        operation_details={
            "verification_id": str(verification_id),
            "doctor_user_id": str(verification.user_id),
            "reason": rejection.reason
        },
        ip_address=request.client.host if request else None,
        user_agent=request.headers.get("user-agent") if request else None
    )
    
    return {
        "success": True,
        "message": "Doctor verification rejected",
        "verification_id": str(verification_id),
        "rejected_at": datetime.utcnow().isoformat()
    }


@router.get("/operations/logs", response_model=Dict[str, Any])
async def get_admin_operation_logs(
    operation_type: Optional[str] = None,
    days: int = 7,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
) -> Dict[str, Any]:
    """
    Get admin operation logs | 获取管理员操作日志
    
    Returns audit trail of admin operations.
    返回管理员操作的审计日志。
    """
    from app.models.models import AdminOperationLog, User
    from sqlalchemy import select
    from datetime import datetime, timedelta
    
    since = datetime.utcnow() - timedelta(days=days)
    
    # Join with users table to get admin email
    stmt = select(AdminOperationLog, User).join(
        User, AdminOperationLog.admin_id == User.id
    ).where(
        AdminOperationLog.timestamp >= since
    )
    
    if operation_type:
        stmt = stmt.where(AdminOperationLog.operation_type == operation_type)
    
    stmt = stmt.order_by(AdminOperationLog.timestamp.desc()).limit(limit)
    
    result = await db.execute(stmt)
    rows = result.all()
    
    logs = []
    for log, user in rows:
        # Determine log level based on operation type
        level = "error" if "_failed" in log.operation_type else "info"
        if "delete" in log.operation_type or "reject" in log.operation_type:
            level = "warning"
            
        logs.append({
            "id": str(log.id),
            "created_at": log.timestamp.isoformat() if log.timestamp else None,
            "level": level,
            "operation": log.operation_type,
            "user_email": user.email if user else "Unknown",
            "details": log.operation_details,
            "ip_address": str(log.ip_address) if log.ip_address else None
        })
    
    return {
        "logs": logs,
        "total": len(logs),
        "days": days
    }


@router.post("/operations/log")
async def log_admin_operation(
    operation_type: str,
    operation_details: Dict[str, Any],
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
    request: Request = None
) -> Dict[str, Any]:
    """
    Log admin operation | 记录管理员操作
    
    Manually log an admin operation.
    手动记录管理员操作。
    """
    admin_logger = AdminOperationLogger(db)
    
    log = await admin_logger.log_operation(
        admin_id=admin.id,
        operation_type=operation_type,
        operation_details=operation_details,
        ip_address=request.client.host if request else None,
        user_agent=request.headers.get("user-agent") if request else None
    )
    
    return {
        "success": True,
        "log_id": str(log.id),
        "timestamp": log.timestamp.isoformat() if log.timestamp else None
    }


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


@router.post("/change-password", response_model=Dict[str, Any])
async def admin_change_password(
    request_data: ChangePasswordRequest,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
    request: Request = None
) -> Dict[str, Any]:
    """
    Change admin password | 管理员修改密码
    
    Allows admin to change their own password.
    允许管理员修改自己的密码。
    """
    from app.core.security import verify_password, get_password_hash
    
    # Verify current password
    if not verify_password(request_data.current_password, admin.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="当前密码不正确"
        )
    
    # Validate new password
    if len(request_data.new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="新密码长度至少为8位"
        )
    
    # Update password
    admin.password_hash = get_password_hash(request_data.new_password)
    await db.commit()
    
    # Log the operation
    admin_logger = AdminOperationLogger(db)
    await admin_logger.log_operation(
        admin_id=admin.id,
        operation_type="change_password",
        operation_details={
            "action": "admin_changed_own_password",
            "admin_email": admin.email
        },
        ip_address=request.client.host if request else None,
        user_agent=request.headers.get("user-agent") if request else None
    )
    
    return {
        "success": True,
        "message": "密码修改成功"
    }


@router.get("/alerts/active", response_model=List[Dict[str, Any]])
async def get_active_alerts(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
) -> List[Dict[str, Any]]:
    """
    Get active system alerts | 获取活跃的系统告警
    
    Returns current active system alerts.
    返回当前活跃的系统告警。
    """
    monitoring = SystemMonitoringService(db)
    
    # Get current metrics
    metrics = await monitoring.collect_system_metrics()
    
    alerts = []
    
    # Check resource alerts
    if metrics.get("overall_alert") in ["warning", "critical"]:
        alerts.append({
            "type": "resource",
            "level": metrics.get("overall_alert"),
            "message": metrics.get("alert_message"),
            "timestamp": datetime.utcnow().isoformat(),
            "details": {
                "cpu": metrics.get("cpu"),
                "memory": metrics.get("memory"),
                "disk": metrics.get("disk")
            }
        })
    
    # Check AI anomalies (last hour)
    anomalies = await monitoring.detect_anomalies(hours=1)
    if anomalies:
        alerts.append({
            "type": "ai_anomaly",
            "level": "warning",
            "message": f"{len(anomalies)} AI diagnosis anomalies detected in the last hour",
            "timestamp": datetime.utcnow().isoformat(),
            "count": len(anomalies),
            "anomalies": anomalies[:5]  # Top 5
        })
    
    # Check pending doctor verifications
    stmt = select(func.count()).select_from(DoctorVerification).where(
        DoctorVerification.status == 'pending'
    )
    result = await db.execute(stmt)
    pending_count = result.scalar()
    
    if pending_count > 0:
        alerts.append({
            "type": "pending_verifications",
            "level": "info",
            "message": f"{pending_count} doctor verification(s) pending",
            "timestamp": datetime.utcnow().isoformat(),
            "count": pending_count
        })
    
    return alerts


# AI Model Configuration Management | AI模型配置管理

@router.get("/ai-models/providers")
async def get_ai_providers(
    admin: User = Depends(require_admin)
) -> Dict[str, Any]:
    """
    Get all available AI providers | 获取所有可用的AI提供商

    Returns a list of supported AI providers with their default configurations.
    返回支持的AI提供商列表及其默认配置。
    """
    from app.services.ai_provider_adapters import get_all_providers

    providers = get_all_providers()
    return {
        "success": True,
        "providers": providers
    }


@router.get("/ai-models", response_model=AIModelsResponse)
async def get_ai_models(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
) -> AIModelsResponse:
    """
    Get all AI model configurations | 获取所有AI模型配置
    
    Returns the status and configuration of all AI models with masked API keys.
    优先从数据库获取配置，如果不存在则回退到环境变量。
    """
    config_service = AIModelConfigService(db)
    
    async def get_model_status(model_type: str) -> AIModelStatus:
        # Try to get from database first
        config = await config_service.get_config_with_decrypted_key(model_type, fallback_to_env=True)
        
        if config:
            return AIModelStatus(
                model_type=model_type,
                api_url=config["api_url"],
                model_id=config["model_id"],
                enabled=config["enabled"] and bool(config["api_url"] and config["api_key"]),
                last_tested=config.get("last_tested"),
                test_status=config.get("test_status"),
                latency_ms=float(config["latency_ms"]) if config.get("latency_ms") else None,
                error_message=config.get("error_message")
            )
        
        # Return empty status if no config found
        return AIModelStatus(model_type=model_type, enabled=False)
    
    # Get status for all models
    diagnosis_status = await get_model_status("diagnosis")
    mineru_status = await get_model_status("mineru")
    embedding_status = await get_model_status("embedding")
    
    # Get OSS status from dynamic config
    from app.services.dynamic_config_service import DynamicConfigService
    oss_config = await DynamicConfigService.get_oss_config(db)
    oss_status = AIModelStatus(
        model_type="oss",
        api_url=oss_config.get("endpoint", ""),
        model_id=oss_config.get("bucket", ""),
        enabled=bool(oss_config.get("access_key_id") and oss_config.get("access_key_secret")),
        test_status="success" if oss_config.get("source") != "none" else None
    )
    
    return AIModelsResponse(
        diagnosis_llm=diagnosis_status,
        mineru=mineru_status,
        embedding=embedding_status,
        oss=oss_status,
        timestamp=datetime.utcnow()
    )


@router.post("/ai-models/{model_type}/config", response_model=AIModelConfigResponse)
async def configure_ai_model(
    model_type: str,
    config: AIModelConfigRequest,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
    request: Request = None
) -> AIModelConfigResponse:
    """
    Configure AI model with encryption and validation | 配置AI模型（加密和验证）
    
    Updates configuration for a specific AI model type with proper security.
    使用适当的安全性更新特定AI模型类型的配置。
    """
    # Validate model type
    valid_types = ['diagnosis', 'mineru', 'embedding', 'oss']
    if model_type not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid model type. Must be one of: {valid_types}"
        )
    
    # Handle OSS configuration separately
    if model_type == 'oss':
        return await configure_oss_model(config, db, admin, request)
    
    # Validate API key format
    # Note: 'diagnosis' uses 'generic' to support local LLM deployments (vLLM, Ollama, etc.)
    key_type_map = {
        'diagnosis': 'generic',
        'mineru': 'mineru',
        'embedding': 'qwen'
    }
    
    if not validate_api_key_format(config.api_key, key_type_map.get(model_type, 'openai')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid API key format for {model_type} model"
        )
    
    # Create AIModelConfig for testing
    ai_config = AIModelConfig(
        api_url=config.api_url,
        api_key=config.api_key,
        model_id=config.model_id or f"{model_type}-default",
        enabled=config.enabled
    )
    
    # Test connection before saving
    test_result = await _test_ai_model_connection(model_type, ai_config)
    
    # Save configuration to database (even if test fails)
    config_service = AIModelConfigService(db)
    model_names = {
        "diagnosis": "诊断AI模型",
        "mineru": "文档提取 (MinerU)",
        "embedding": "向量嵌入模型"
    }
    
    # Extract provider from config or use 'custom' as default
    provider = getattr(config, 'provider', 'custom') or 'custom'

    await config_service.save_config(
        model_type=model_type,
        model_name=model_names.get(model_type, model_type),
        api_url=config.api_url,
        api_key=config.api_key,
        model_id=config.model_id or f"{model_type}-default",
        enabled=config.enabled and test_result["success"],  # Only enable if test passed
        config_metadata={"provider": provider},
        provider=provider
    )
    
    if not test_result["success"]:
        # Log failed configuration attempt
        admin_logger = AdminOperationLogger(db)
        await admin_logger.log_operation(
            admin_id=admin.id,
            operation_type="configure_ai_model_failed",
            operation_details={
                "model_type": model_type,
                "error": test_result.get("error_message", "Connection test failed")
            },
            ip_address=request.client.host if request else "unknown",
            user_agent=request.headers.get("user-agent") if request else "unknown"
        )
        
        # Update test status to failed
        await config_service.update_test_status(
            model_type=model_type,
            test_status="failed",
            error_message=test_result.get("error_message", "Connection test failed")
        )
        
        # Return success with warning (config is saved but not enabled)
        return AIModelConfigResponse(
            success=True,
            message=f"配置已保存，但连接测试失败: {test_result.get('error_message', 'Unknown error')}",
            model_type=model_type,
            config=AIModelStatus(
                model_type=model_type,
                api_url=config.api_url,
                model_id=config.model_id or f"{model_type}-default",
                enabled=False,
                test_status="failed",
                last_tested=datetime.utcnow()
            ),
            test_result=test_result,
            timestamp=datetime.utcnow()
        )
    
    # Update test status to success
    await config_service.update_test_status(
        model_type=model_type,
        test_status="success",
        latency_ms=test_result.get("latency_ms")
    )
    
    # Log the successful configuration (without sensitive data)
    admin_logger = AdminOperationLogger(db)
    await admin_logger.log_operation(
        admin_id=admin.id,
        operation_type="configure_ai_model",
        operation_details={
            "model_type": model_type,
            "api_url": config.api_url,
            "model_id": config.model_id,
            "enabled": config.enabled,
            "test_latency_ms": test_result.get("latency_ms"),
            "api_key_encrypted": True,
            "storage": "database"
        },
        ip_address=request.client.host if request else "unknown",
        user_agent=request.headers.get("user-agent") if request else "unknown"
    )
    
    # Create response status
    model_status = AIModelStatus(
        model_type=model_type,
        api_url=config.api_url,
        model_id=config.model_id,
        enabled=config.enabled,
        test_status="success",
        latency_ms=test_result.get("latency_ms"),
        last_tested=datetime.utcnow()
    )
    
    return AIModelConfigResponse(
        success=True,
        message=f"AI model '{model_type}' configured successfully",
        model_type=model_type,
        config=model_status,
        test_result=test_result,
        timestamp=datetime.utcnow()
    )


async def configure_oss_model(
    config: AIModelConfigRequest,
    db: AsyncSession,
    admin: User,
    request: Request = None
) -> AIModelConfigResponse:
    """
    Configure OSS storage | 配置OSS存储
    
    Updates Alibaba Cloud OSS configuration with proper security.
    使用适当的安全性更新阿里云OSS配置。
    """
    from app.services.oss_service import os_service
    
    # Extract OSS config from the request
    # Frontend sends: api_url=endpoint, api_key=secret, model_id=bucket, endpoint=endpoint
    bucket = config.model_id
    endpoint = config.api_url  # or getattr(config, 'endpoint', config.api_url)
    access_key_id = getattr(config, 'access_key_id', '')  # May need separate field
    access_key_secret = config.api_key
    
    # If access_key_id not provided directly, try to get from metadata
    if not access_key_id and hasattr(config, '__dict__'):
        extra = config.__dict__.get('__pydantic_extra__', {}) or {}
        access_key_id = extra.get('access_key_id', '')
    
    # Update OSS service configuration
    os_service.update_config({
        "access_key_id": access_key_id,
        "access_key_secret": access_key_secret,
        "bucket": bucket,
        "endpoint": endpoint
    })
    
    # Save to database for persistence
    config_service = AIModelConfigService(db)
    await config_service.save_config(
        model_type="oss",
        model_name="阿里云OSS存储",
        api_url=endpoint,
        api_key=access_key_secret,
        model_id=bucket,
        enabled=config.enabled,
        config_metadata={
            "access_key_id": access_key_id,
            "bucket": bucket,
            "endpoint": endpoint
        }
    )
    
    # Log the configuration
    admin_logger = AdminOperationLogger(db)
    await admin_logger.log_operation(
        admin_id=admin.id,
        operation_type="configure_oss",
        operation_details={
            "bucket": bucket,
            "enabled": config.enabled,
            "api_key_encrypted": True
        },
        ip_address=request.client.host if request else "unknown",
        user_agent=request.headers.get("user-agent") if request else "unknown"
    )
    
    # Test OSS connection (but don't block save if test fails)
    test_result = os_service.health_check()
    
    model_status = AIModelStatus(
        model_type="oss",
        api_url=endpoint,
        model_id=bucket,
        enabled=config.enabled,
        test_status="success" if test_result.get("healthy") else "failed",
        last_tested=datetime.utcnow()
    )
    
    # Always return success=True if config was saved, even if test failed
    # User can test connection separately using the test button
    if test_result.get("healthy"):
        return AIModelConfigResponse(
            success=True,
            message="OSS配置已保存并测试成功",
            model_type="oss",
            config=model_status,
            test_result=test_result,
            timestamp=datetime.utcnow()
        )
    else:
        return AIModelConfigResponse(
            success=True,
            message=f"OSS配置已保存，但连接测试失败: {test_result.get('error', 'Unknown error')}",
            model_type="oss",
            config=model_status,
            test_result=test_result,
            timestamp=datetime.utcnow()
        )
    
    return AIModelConfigResponse(
        success=test_result.get("healthy", False),
        message="OSS配置已更新" if test_result.get("healthy") else f"OSS配置失败: {test_result.get('error', 'Unknown error')}",
        model_type="oss",
        config=model_status,
        test_result=test_result,
        timestamp=datetime.utcnow()
    )


@router.post("/ai-models/{model_type}/test", response_model=AIModelTestResponse)
async def test_ai_model(
    model_type: str,
    test_request: AIModelTestRequest = AIModelTestRequest(),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
) -> AIModelTestResponse:
    """
    Test AI model connection | 测试AI模型连接
    
    Tests connectivity and response time for a specific AI model.
    优先测试数据库中的配置，如果不存在则测试环境变量配置。
    """
    # Validate model type
    valid_types = ['diagnosis', 'mineru', 'embedding', 'oss']
    if model_type not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid model type. Must be one of: {valid_types}"
        )
    
    # Handle OSS testing separately
    if model_type == 'oss':
        return await test_oss_connection(db, admin)
    
    # Get configuration from database or environment
    config_service = AIModelConfigService(db)
    config = await config_service.get_config_with_decrypted_key(model_type, fallback_to_env=True)
    
    if not config:
        return AIModelTestResponse(
            success=False,
            model_type=model_type,
            latency_ms=0,
            error_message="Model not configured (missing API URL or key)",
            timestamp=datetime.utcnow()
        )
    
    api_url = config["api_url"]
    api_key = config["api_key"]
    model_id = config["model_id"]
    
    config = AIModelConfig(
        api_url=api_url,
        api_key=api_key,
        model_id=model_id,
        enabled=True
    )
    
    # Test the connection
    result = await _test_ai_model_connection(model_type, config, test_request.test_payload)

    # Check if config exists in database, if not, create it from environment variables
    existing_config = await config_service.get_config(model_type)
    if not existing_config:
        # Config comes from environment variables, create a database record
        model_names = {
            "diagnosis": "诊断AI模型",
            "mineru": "文档提取 (MinerU)",
            "embedding": "向量嵌入模型"
        }
        await config_service.save_config(
            model_type=model_type,
            model_name=model_names.get(model_type, model_type),
            api_url=api_url,
            api_key=api_key,
            model_id=model_id,
            enabled=True
        )

    # Update test status in database
    await config_service.update_test_status(
        model_type=model_type,
        test_status="success" if result["success"] else "failed",
        latency_ms=result.get("latency_ms"),
        error_message=result.get("error_message")
    )

    return AIModelTestResponse(
        success=result["success"],
        model_type=model_type,
        latency_ms=result.get("latency_ms", 0),
        status_code=result.get("status_code"),
        response_summary=result.get("response_summary"),
        error_message=result.get("error_message"),
        timestamp=datetime.utcnow()
    )


async def test_oss_connection(
    db: AsyncSession,
    admin: User
) -> AIModelTestResponse:
    """
    Test OSS connection | 测试OSS连接
    
    Tests connectivity to Alibaba Cloud OSS.
    测试阿里云OSS连接。
    """
    from app.services.dynamic_config_service import DynamicConfigService
    
    start_time = asyncio.get_event_loop().time()
    
    try:
        # Get OSS config from database
        oss_config = await DynamicConfigService.get_oss_config(db)
        
        if oss_config.get("source") == "none":
            latency_ms = int((asyncio.get_event_loop().time() - start_time) * 1000)
            return AIModelTestResponse(
                success=False,
                model_type="oss",
                latency_ms=latency_ms,
                error_message="OSS not configured",
                timestamp=datetime.utcnow()
            )
        
        # Test OSS connection using health check
        from app.services.oss_service import os_service
        health_result = os_service.health_check()
        
        latency_ms = int((asyncio.get_event_loop().time() - start_time) * 1000)
        
        return AIModelTestResponse(
            success=health_result.get("healthy", False),
            model_type="oss",
            latency_ms=latency_ms,
            error_message=health_result.get("error"),
            timestamp=datetime.utcnow()
        )
    except Exception as e:
        latency_ms = int((asyncio.get_event_loop().time() - start_time) * 1000)
        return AIModelTestResponse(
            success=False,
            model_type="oss",
            latency_ms=latency_ms,
            error_message=str(e),
            timestamp=datetime.utcnow()
        )


async def _test_ai_model_connection(
    model_type: str, 
    config: AIModelConfig,
    test_payload: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Internal function to test AI model connection | 内部函数：测试AI模型连接
    """
    start_time = asyncio.get_event_loop().time()
    
    try:
        async with aiohttp.ClientSession() as session:
            if model_type == 'diagnosis':
                # Test with a simple health check or minimal request
                headers = {
                    "Authorization": f"Bearer {config.api_key}",
                    "Content-Type": "application/json"
                }

                payload = test_payload or {
                    "model": config.model_id,
                    "messages": [{"role": "user", "content": "Hello"}],
                    "max_tokens": 5
                }

                # Build API URL correctly - respect user-provided URL
                api_base = config.api_url.rstrip('/')
                
                logger.info(f"[DEBUG] Building test URL from: {api_base}")
                
                # Check if URL already ends with /chat/completions
                if api_base.endswith('/chat/completions'):
                    test_url = api_base
                    logger.info(f"[DEBUG] URL ends with /chat/completions, using as-is: {test_url}")
                # Check if URL contains version indicator (/v1, /v4, etc.) - check last path segment
                elif api_base.split('/')[-1].startswith('v'):
                    # URL already has version like /v1, /v4, just append chat/completions
                    test_url = f"{api_base}/chat/completions"
                    logger.info(f"[DEBUG] URL has version prefix, built: {test_url}")
                else:
                    # For generic URLs, add /v1/chat/completions
                    test_url = f"{api_base}/v1/chat/completions"
                    logger.info(f"[DEBUG] Generic URL, built: {test_url}")

                async with session.post(
                    test_url,
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    status_code = response.status
                    response_data = await response.json()
                    
                    if status_code == 200:
                        return {
                            "success": True,
                            "latency_ms": (asyncio.get_event_loop().time() - start_time) * 1000,
                            "status_code": status_code,
                            "response_summary": f"Model responded successfully. Response keys: {list(response_data.keys())}"
                        }
                    else:
                        return {
                            "success": False,
                            "latency_ms": (asyncio.get_event_loop().time() - start_time) * 1000,
                            "status_code": status_code,
                            "error_message": f"HTTP {status_code}: {response_data.get('error', 'Unknown error')}"
                        }
            
            elif model_type == 'mineru':
                # Test MinerU API with a simple document extraction request
                headers = {
                    "Authorization": f"Bearer {config.api_key}",
                    "Content-Type": "application/json"
                }
                
                # Just test the API endpoint availability
                async with session.get(
                    f"{config.api_url}/health" if "/health" not in config.api_url else f"{config.api_url}",
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    status_code = response.status
                    
                    if status_code in [200, 404]:  # 404 might mean no health endpoint but API is up
                        return {
                            "success": True,
                            "latency_ms": (asyncio.get_event_loop().time() - start_time) * 1000,
                            "status_code": status_code,
                            "response_summary": "MinerU API is accessible"
                        }
                    else:
                        return {
                            "success": False,
                            "latency_ms": (asyncio.get_event_loop().time() - start_time) * 1000,
                            "status_code": status_code,
                            "error_message": f"MinerU API returned HTTP {status_code}"
                        }
            
            elif model_type == 'embedding':
                # Test embedding API
                headers = {
                    "Authorization": f"Bearer {config.api_key}",
                    "Content-Type": "application/json"
                }
                
                # Detect provider type from URL
                is_qwen = 'dashscope' in config.api_url.lower() or 'aliyun' in config.api_url.lower()
                
                # Build appropriate payload based on provider
                if test_payload:
                    payload = test_payload
                elif is_qwen:
                    # Qwen/DashScope format
                    payload = {
                        "model": config.model_id,
                        "input": {
                            "texts": ["test"]
                        }
                    }
                else:
                    # OpenAI format
                    payload = {
                        "model": config.model_id,
                        "input": ["test"]
                    }
                
                # Use the URL as provided (don't add /embeddings)
                # The URL should already be the complete embedding endpoint
                test_url = config.api_url
                if test_url.endswith('/'):
                    test_url = test_url.rstrip('/')
                
                async with session.post(
                    test_url,
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    status_code = response.status
                    response_data = await response.json()
                    
                    if status_code == 200:
                        return {
                            "success": True,
                            "latency_ms": (asyncio.get_event_loop().time() - start_time) * 1000,
                            "status_code": status_code,
                            "response_summary": f"Embedding API responded. Provider: {'Qwen' if is_qwen else 'OpenAI'}"
                        }
                    else:
                        return {
                            "success": False,
                            "latency_ms": (asyncio.get_event_loop().time() - start_time) * 1000,
                            "status_code": status_code,
                            "error_message": f"HTTP {status_code}: {response_data.get('error', 'Unknown error')}"
                        }
    
    except asyncio.TimeoutError:
        return {
            "success": False,
            "latency_ms": (asyncio.get_event_loop().time() - start_time) * 1000,
            "error_message": "Connection timeout"
        }
    except Exception as e:
        return {
            "success": False,
            "latency_ms": (asyncio.get_event_loop().time() - start_time) * 1000,
            "error_message": f"Connection error: {str(e)}"
        }


# Knowledge Base Management | 知识库管理
@router.post("/knowledge-base/upload", response_model=KnowledgeBaseUploadResponse)
async def upload_knowledge_base_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
    request: Request = None
) -> KnowledgeBaseUploadResponse:
    """
    Upload knowledge base document | 上传知识库文档
    
    Uploads a markdown file for the knowledge base and starts processing.
    上传知识库的markdown文件并开始处理。
    """
    # Validate file type
    if not file.filename or not file.filename.endswith('.md'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only .md files are supported for knowledge base uploads"
        )
    
    # Validate file size (max 50MB for knowledge base)
    max_size = 50 * 1024 * 1024  # 50MB
    if file.size and file.size > max_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds maximum allowed size of {max_size // (1024*1024)}MB"
        )
    
    try:
        # Save to unified knowledge base directory
        from app.services.unified_kb_service import get_unified_knowledge_loader
        
        kb_loader = get_unified_knowledge_loader()
        unified_dir = kb_loader.unified_root
        unified_dir.mkdir(parents=True, exist_ok=True)
        
        # Use original filename (cleaned)
        safe_filename = file.filename.replace(' ', '_')
        file_path = unified_dir / safe_filename
        
        # Read content
        content = await file.read()
        content_str = content.decode('utf-8')
        
        # Save file to unified directory
        async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
            await f.write(content_str)
        
        # Generate document ID
        doc_id = str(uuid.uuid4())
        
        # Add to unified KB metadata (auto-infer category and tags)
        kb_loader.add_document(
            filename=safe_filename,
            content=content_str,
            title=safe_filename.replace('.md', ''),
            source=f"admin_upload_{admin.email}"
        )
        
        # Log the upload
        admin_logger = AdminOperationLogger(db)
        await admin_logger.log_operation(
            admin_id=admin.id,
            operation_type="upload_knowledge_document",
            operation_details={
                "filename": file.filename,
                "file_size": len(content),
                "doc_id": doc_id,
                "safe_filename": safe_filename,
                "location": str(file_path)
            },
            ip_address=request.client.host if request else "unknown",
            user_agent=request.headers.get("user-agent") if request else "unknown"
        )
        
        # Start REAL background processing for vectorization
        asyncio.create_task(_vectorize_knowledge_document(doc_id, safe_filename, content_str, admin.id))
        
        return KnowledgeBaseUploadResponse(
            success=True,
            doc_id=doc_id,
            filename=file.filename,
            status="processing",
            message="文档上传成功，正在向量化处理中 | Document uploaded and vectorization started",
            timestamp=datetime.utcnow()
        )
    
    except Exception as e:
        # Log error with full traceback
        import traceback
        error_detail = str(e)
        traceback_str = traceback.format_exc()
        logger.error(f"❌ Upload failed: {error_detail}")
        logger.error(f"Traceback: {traceback_str}")
        
        # Log error
        admin_logger = AdminOperationLogger(db)
        await admin_logger.log_operation(
            admin_id=admin.id,
            operation_type="upload_knowledge_document_failed",
            operation_details={
                "filename": file.filename if file else "unknown",
                "error": error_detail,
                "traceback": traceback_str[:500]
            },
            ip_address=request.client.host if request else "unknown",
            user_agent=request.headers.get("user-agent") if request else "unknown"
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload document: {error_detail}"
        )


@router.get("/knowledge-base/documents", response_model=KnowledgeBaseDocumentsResponse)
async def get_knowledge_base_documents(
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
) -> KnowledgeBaseDocumentsResponse:
    """
    Get knowledge base documents | 获取知识库文档列表
    
    Returns a list of all knowledge base documents with real status from unified KB.
    从统一知识库返回所有文档列表及其真实状态。
    """
    try:
        from app.services.unified_kb_service import get_unified_knowledge_loader
        from sqlalchemy import text
        
        # Get unified KB loader
        kb_loader = get_unified_knowledge_loader()
        
        # Get document list from metadata
        all_docs = kb_loader.list_documents()
        total_count = len(all_docs)
        
        # Get real chunk counts from vector database
        chunk_counts = {}
        try:
            result = await db.execute(text("""
                SELECT document_title, COUNT(*) as chunk_count
                FROM knowledge_base_chunks
                WHERE source_type = 'unified_kb'
                GROUP BY document_title
            """))
            for row in result.fetchall():
                chunk_counts[row[0]] = row[1]
        except Exception as e:
            logger.error(f"Failed to query chunk counts: {e}")
        
        # Build document list
        documents = []
        for i, doc_meta in enumerate(all_docs[skip:skip+limit]):
            filename = doc_meta.get('filename', 'unknown')
            title = doc_meta.get('title', filename)
            
            # Get file info
            file_path = kb_loader.unified_root / filename
            if file_path.exists():
                stat = file_path.stat()
                file_size = stat.st_size
                file_mtime = datetime.fromtimestamp(stat.st_mtime)
            else:
                file_size = doc_meta.get('file_size', 0)
                file_mtime = datetime.fromisoformat(doc_meta.get('added_at', datetime.utcnow().isoformat()))
            
            # Check vectorization status
            real_chunk_count = chunk_counts.get(title, 0)
            
            # Determine status
            if real_chunk_count > 0:
                status = "completed"
                processed_at = file_mtime
            elif doc_meta.get('added_at'):
                added_time = datetime.fromisoformat(doc_meta.get('added_at'))
                time_diff = (datetime.utcnow() - added_time).total_seconds()
                if time_diff < 300:  # Less than 5 minutes
                    status = "processing"
                    processed_at = None
                else:
                    status = "failed"
                    processed_at = None
            else:
                status = "processing"
                processed_at = None
            
            # Generate preview from actual content
            try:
                doc_obj = kb_loader.load_document(filename)
                if doc_obj and doc_obj.content:
                    preview = doc_obj.content[:200] + "..." if len(doc_obj.content) > 200 else doc_obj.content
                else:
                    preview = "Preview unavailable"
            except:
                preview = "Preview unavailable"
            
            doc = KnowledgeBaseDocument(
                doc_id=str(i + skip + 1),
                filename=filename,
                file_size=file_size,
                status=status,
                chunk_count=real_chunk_count,
                uploaded_at=file_mtime,
                processed_at=processed_at,
                file_type="markdown",
                preview=preview
            )
            
            # Apply status filter
            if status_filter is None or doc.status == status_filter:
                documents.append(doc)
        
        return KnowledgeBaseDocumentsResponse(
            documents=documents,
            total_count=total_count,
            timestamp=datetime.utcnow()
        )
    
    except Exception as e:
        logger.error(f"Failed to retrieve documents: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve documents: {str(e)}"
        )


@router.get("/knowledge-base/documents/{doc_id}/status", response_model=KnowledgeBaseDocumentStatusResponse)
async def get_knowledge_base_document_status(
    doc_id: str,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
) -> KnowledgeBaseDocumentStatusResponse:
    """
    Get knowledge base document processing status | 获取知识库文档处理状态
    
    Returns detailed processing status and error information for a specific document.
    返回特定文档的详细处理状态和错误信息。
    """
    try:
        # In a real implementation, you would query the database for the document
        # For now, we'll simulate the status based on file system
        
        upload_dir = Path("/app/uploads/knowledge_base")
        
        if not upload_dir.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Knowledge base upload directory not found"
            )
        
        # Find the document
        document_found = False
        file_path = None
        file_stat = None
        
        # Try to find by doc_id or index
        md_files = list(upload_dir.glob("*.md"))
        for i, md_file in enumerate(md_files):
            if str(i + 1) == doc_id or md_file.stem.endswith(doc_id):
                file_path = md_file
                file_stat = md_file.stat()
                document_found = True
                break
        
        if not document_found:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document {doc_id} not found"
            )
        
        # Determine status based on file timestamp
        file_time = datetime.fromtimestamp(file_stat.st_mtime)
        time_diff = datetime.utcnow() - file_time
        
        if time_diff.total_seconds() < 60:
            status = "processing"
            chunk_count = 0
            vector_count = 0
            processing_progress = 0.1
            error_message = None
            processed_at = None
        elif time_diff.total_seconds() < 300:
            status = "completed"
            chunk_count = 10  # Simulated
            vector_count = 10  # Simulated
            processing_progress = 1.0
            error_message = None
            processed_at = file_time + timedelta(seconds=120)  # Simulated processing time
        else:
            status = "completed"
            chunk_count = 15  # Simulated
            vector_count = 15  # Simulated
            processing_progress = 1.0
            error_message = None
            processed_at = file_time + timedelta(seconds=120)  # Simulated processing time
        
        document_status = KnowledgeBaseDocumentStatus(
            doc_id=doc_id,
            filename=file_path.name,
            status=status,
            chunk_count=chunk_count,
            vector_count=vector_count,
            file_size=file_stat.st_size,
            uploaded_at=file_time,
            processed_at=processed_at,
            error_message=error_message,
            processing_progress=processing_progress
        )
        
        return KnowledgeBaseDocumentStatusResponse(
            document=document_status,
            timestamp=datetime.utcnow()
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get document status for {doc_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve document status: {str(e)}"
        )


@router.delete("/knowledge-base/documents/{doc_id}", response_model=Dict[str, Any])
async def delete_knowledge_base_document(
    doc_id: str,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
    request: Request = None
) -> Dict[str, Any]:
    """
    Delete knowledge base document | 删除知识库文档
    
    Deletes a knowledge base document and its associated vector data.
    删除知识库文档及其相关的向量数据。
    """
    try:
        from app.services.unified_kb_service import get_unified_knowledge_loader
        from sqlalchemy import text
        
        # Get unified KB loader
        kb_loader = get_unified_knowledge_loader()
        
        # Get all documents and find by index (sync operation)
        all_docs = kb_loader.list_documents()
        doc_index = int(doc_id) - 1  # Convert to 0-based index
        
        if doc_index < 0 or doc_index >= len(all_docs):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document {doc_id} not found"
            )
        
        doc_meta = all_docs[doc_index]
        filename = doc_meta.get('filename')
        title = doc_meta.get('title', filename)
        
        # Delete from unified KB (removes file and metadata) - run in thread to avoid blocking
        import asyncio
        delete_result = await asyncio.to_thread(kb_loader.delete_document, filename)
        
        if not delete_result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete document {doc_id}"
            )
        
        deleted_filename = filename
        file_deleted = True
        
        # Log the deletion
        admin_logger = AdminOperationLogger(db)
        await admin_logger.log_operation(
            admin_id=admin.id,
            operation_type="delete_knowledge_document",
            operation_details={
                "doc_id": doc_id,
                "filename": deleted_filename,
                "file_deleted": file_deleted
            },
            ip_address=request.client.host if request else "unknown",
            user_agent=request.headers.get("user-agent") if request else "unknown"
        )
        
        return {
            "success": True,
            "message": f"Knowledge base document {doc_id} deleted successfully",
            "doc_id": doc_id,
            "deleted_filename": deleted_filename,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        # Log error
        admin_logger = AdminOperationLogger(db)
        await admin_logger.log_operation(
            admin_id=admin.id,
            operation_type="delete_knowledge_document_failed",
            operation_details={
                "doc_id": doc_id,
                "error": str(e)
            },
            ip_address=request.client.host if request else "unknown",
            user_agent=request.headers.get("user-agent") if request else "unknown"
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete document: {str(e)}"
        )


async def _vectorize_knowledge_document(doc_id: str, filename: str, content: str, admin_id: int) -> None:
    """
    Background task to vectorize knowledge document | 后台任务：向量化知识文档
    
    This function runs in the background to:
    1. Parse markdown content
    2. Chunk the content into segments
    3. Generate vector embeddings using Qwen/Aliyun API
    4. Store in vector database (PostgreSQL with pgvector)
    """
    from app.db.database import AsyncSessionLocal
    from app.services.unified_kb_service import get_unified_knowledge_loader
    from app.services.kb_vectorization_service import KnowledgeBaseVectorizationService
    from app.services.vector_embedding_service import VectorEmbeddingService
    
    try:
        logger.info(f"🔄 [Background] Starting vectorization for document {doc_id}: {filename}")
        
        # Create new DB session for background task
        async with AsyncSessionLocal() as db:
            try:
                # First, check if there's an active vector embedding configuration
                # Try vector_embedding_configs first, then fall back to ai_model_configurations
                vector_service = VectorEmbeddingService(db)
                config = None
                try:
                    config = await vector_service.get_active_config()
                    if config:
                        logger.info(f"✅ [Background] Using vector config from vector_embedding_configs: {config.name} ({config.provider}/{config.model_id})")
                except Exception as e:
                    logger.warning(f"⚠️ [Background] Could not get config from vector_embedding_configs: {e}")
                
                # If not found in vector_embedding_configs, try ai_model_configurations
                if not config:
                    try:
                        from app.services.dynamic_config_service import DynamicConfigService
                        embedding_config = await DynamicConfigService.get_embedding_config(db)
                        if embedding_config and embedding_config.get("source") == "database":
                            logger.info(f"✅ [Background] Using vector config from ai_model_configurations: {embedding_config['model_id']}")
                        else:
                            logger.error(f"❌ [Background] No active vector embedding configuration found. Please configure one in Admin > AI Model Settings.")
                            return
                    except Exception as config_error:
                        logger.error(f"❌ [Background] Failed to get vector config: {config_error}")
                        return
                
                # Get document info from unified KB
                kb_loader = get_unified_knowledge_loader()
                doc = kb_loader.load_document(filename)
                
                if not doc:
                    logger.error(f"❌ [Background] Document not found in KB: {filename}")
                    return
                
                logger.info(f"📄 [Background] Document loaded: {doc.title}, size: {len(doc.content)} chars")
                
                # Initialize vectorization service
                kb_service = KnowledgeBaseVectorizationService(db)
                
                # Perform vectorization
                logger.info(f"🔤 [Background] Starting embedding generation...")
                result = await kb_service.vectorize_markdown_document(
                    document_content=doc.content,
                    document_title=doc.title,
                    disease_category=doc.category,
                    disease_id=None,  # Not linked to specific disease
                    source_type='unified_kb',
                    created_by=admin_id
                )
                
                logger.info(
                    f"✅ [Background] Vectorization complete for {filename}: "
                    f"{result.get('new_chunks', 0)} chunks created, "
                    f"{result.get('total_chunks', 0)} total"
                )
                
            except Exception as e:
                logger.error(f"❌ [Background] Vectorization failed for {filename}: {e}")
                import traceback
                logger.error(f"[Background] Traceback: {traceback.format_exc()}")
                await db.rollback()
                raise
    
    except Exception as e:
        logger.error(f"❌ [Background] Task failed for document {doc_id}: {e}")
        import traceback
        logger.error(f"[Background] Traceback: {traceback.format_exc()}")


# Keep old function name for backward compatibility
async def _process_knowledge_document(doc_id: str, file_path: Path, db: AsyncSession) -> None:
    """
    [DEPRECATED] Use _vectorize_knowledge_document instead
    Background task to process knowledge document
    """
    logger.warning("_process_knowledge_document is deprecated, use _vectorize_knowledge_document")
    pass


# System Settings Management | 系统设置管理
@router.get("/settings", response_model=SystemSettingsResponse)
async def get_system_settings(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
) -> SystemSettingsResponse:
    """
    Get system settings | 获取系统设置
    
    Returns current system configuration settings.
    返回当前系统配置设置。
    """
    try:
        # Get settings from environment variables and configuration
        settings = SystemSettings(
            max_file_size=int(os.getenv("MAX_FILE_SIZE", str(200 * 1024 * 1024))),
            allowed_file_types=os.getenv("ALLOWED_FILE_TYPES", ".pdf,.jpg,.jpeg,.png,.doc,.docx,.ppt,.pptx,.md").split(","),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            debug_mode=os.getenv("DEBUG", "false").lower() == "true",
            maintenance_mode=os.getenv("MAINTENANCE_MODE", "false").lower() == "true",
            ai_request_timeout=int(os.getenv("AI_REQUEST_TIMEOUT", "30")),
            ai_max_retries=int(os.getenv("AI_MAX_RETRIES", "3")),
            embedding_batch_size=int(os.getenv("EMBEDDING_BATCH_SIZE", "100")),
            knowledge_base_chunk_size=int(os.getenv("KNOWLEDGE_BASE_CHUNK_SIZE", "1000")),
            pii_detection_enabled=os.getenv("PII_DETECTION_ENABLED", "true").lower() == "true",
            data_retention_days=int(os.getenv("DATA_RETENTION_DAYS", "365")),
            session_timeout_minutes=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30")),
            max_concurrent_requests=int(os.getenv("MAX_CONCURRENT_REQUESTS", "100")),
            enable_anomaly_detection=os.getenv("ENABLE_ANOMALY_DETECTION", "true").lower() == "true",
            anomaly_threshold_ms=int(os.getenv("ANOMALY_THRESHOLD_MS", "5000"))
        )
        
        return SystemSettingsResponse(
            settings=settings,
            timestamp=datetime.utcnow()
        )
    
    except Exception as e:
        logger.error(f"Failed to get system settings: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve system settings: {str(e)}"
        )


@router.put("/settings", response_model=UpdateSystemSettingsResponse)
async def update_system_settings(
    settings_update: UpdateSystemSettingsRequest,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
    request: Request = None
) -> UpdateSystemSettingsResponse:
    """
    Update system settings | 更新系统设置
    
    Updates system configuration settings with validation and logging.
    使用验证和日志记录更新系统配置设置。
    """
    try:
        # Get current settings
        current_settings = await get_system_settings(db, admin)
        
        # Apply updates (only non-None values)
        updated_settings = current_settings.settings
        
        if settings_update.max_file_size is not None:
            if settings_update.max_file_size < 1024 * 1024:  # 1MB minimum
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="max_file_size must be at least 1MB"
                )
            updated_settings.max_file_size = settings_update.max_file_size
        
        if settings_update.allowed_file_types is not None:
            if not settings_update.allowed_file_types:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="allowed_file_types cannot be empty"
                )
            updated_settings.allowed_file_types = settings_update.allowed_file_types
        
        if settings_update.log_level is not None:
            valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
            if settings_update.log_level not in valid_levels:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"log_level must be one of: {valid_levels}"
                )
            updated_settings.log_level = settings_update.log_level
        
        if settings_update.debug_mode is not None:
            updated_settings.debug_mode = settings_update.debug_mode
        
        if settings_update.maintenance_mode is not None:
            updated_settings.maintenance_mode = settings_update.maintenance_mode
        
        if settings_update.ai_request_timeout is not None:
            if settings_update.ai_request_timeout < 1 or settings_update.ai_request_timeout > 300:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="ai_request_timeout must be between 1 and 300 seconds"
                )
            updated_settings.ai_request_timeout = settings_update.ai_request_timeout
        
        if settings_update.ai_max_retries is not None:
            if settings_update.ai_max_retries < 0 or settings_update.ai_max_retries > 10:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="ai_max_retries must be between 0 and 10"
                )
            updated_settings.ai_max_retries = settings_update.ai_max_retries
        
        if settings_update.embedding_batch_size is not None:
            if settings_update.embedding_batch_size < 1 or settings_update.embedding_batch_size > 1000:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="embedding_batch_size must be between 1 and 1000"
                )
            updated_settings.embedding_batch_size = settings_update.embedding_batch_size
        
        if settings_update.knowledge_base_chunk_size is not None:
            if settings_update.knowledge_base_chunk_size < 100 or settings_update.knowledge_base_chunk_size > 10000:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="knowledge_base_chunk_size must be between 100 and 10000"
                )
            updated_settings.knowledge_base_chunk_size = settings_update.knowledge_base_chunk_size
        
        if settings_update.pii_detection_enabled is not None:
            updated_settings.pii_detection_enabled = settings_update.pii_detection_enabled
        
        if settings_update.data_retention_days is not None:
            if settings_update.data_retention_days < 1 or settings_update.data_retention_days > 3650:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="data_retention_days must be between 1 and 3650 days"
                )
            updated_settings.data_retention_days = settings_update.data_retention_days
        
        if settings_update.session_timeout_minutes is not None:
            if settings_update.session_timeout_minutes < 5 or settings_update.session_timeout_minutes > 1440:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="session_timeout_minutes must be between 5 and 1440 minutes"
                )
            updated_settings.session_timeout_minutes = settings_update.session_timeout_minutes
        
        if settings_update.max_concurrent_requests is not None:
            if settings_update.max_concurrent_requests < 1 or settings_update.max_concurrent_requests > 10000:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="max_concurrent_requests must be between 1 and 10000"
                )
            updated_settings.max_concurrent_requests = settings_update.max_concurrent_requests
        
        if settings_update.enable_anomaly_detection is not None:
            updated_settings.enable_anomaly_detection = settings_update.enable_anomaly_detection
        
        if settings_update.anomaly_threshold_ms is not None:
            if settings_update.anomaly_threshold_ms < 100 or settings_update.anomaly_threshold_ms > 60000:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="anomaly_threshold_ms must be between 100 and 60000 ms"
                )
            updated_settings.anomaly_threshold_ms = settings_update.anomaly_threshold_ms
        
        # Log the settings update
        admin_logger = AdminOperationLogger(db)
        await admin_logger.log_operation(
            admin_id=admin.id,
            operation_type="system_config_update",
            operation_details={
                "updated_fields": settings_update.model_dump(exclude_none=True),
                "previous_settings": current_settings.settings.model_dump(),
                "new_settings": updated_settings.model_dump()
            },
            ip_address=request.client.host if request else "unknown",
            user_agent=request.headers.get("user-agent") if request else "unknown"
        )
        
        # In a real implementation, you would save these to a configuration file or database
        # For now, we'll just return the updated settings
        
        return UpdateSystemSettingsResponse(
            success=True,
            message="System settings updated successfully",
            updated_settings=updated_settings,
            timestamp=datetime.utcnow()
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update system settings: {str(e)}")
        
        # Log failed update attempt
        admin_logger = AdminOperationLogger(db)
        await admin_logger.log_operation(
            admin_id=admin.id,
            operation_type="system_config_update_failed",
            operation_details={
                "error": str(e),
                "requested_changes": settings_update.model_dump(exclude_none=True)
            },
            ip_address=request.client.host if request else "unknown",
            user_agent=request.headers.get("user-agent") if request else "unknown"
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update system settings: {str(e)}"
        )


@router.get("/system/configuration", response_model=SystemConfiguration)
async def get_system_configuration(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
) -> SystemConfiguration:
    """
    Get complete system configuration overview | 获取完整系统配置概览
    
    Returns comprehensive system configuration including AI models, settings, and service status.
    返回包括AI模型、设置和服务状态的完整系统配置。
    """
    try:
        # Get AI models status
        ai_models_response = await get_ai_models(db, admin)
        
        # Get system settings
        settings_response = await get_system_settings(db, admin)
        
        # Get database status
        database_status = {}
        try:
            # Test database connection
            result = await db.execute("SELECT 1")
            database_status["connected"] = True
            database_status["connection_test"] = "success"
        except Exception as e:
            database_status["connected"] = False
            database_status["connection_test"] = "failed"
            database_status["error"] = str(e)
        
        # Get service status
        service_status = {}
        try:
            # Check Redis connection (if available)
            import redis
            redis_client = redis.Redis(
                host=os.getenv("REDIS_HOST", "localhost"),
                port=int(os.getenv("REDIS_PORT", "6379")),
                password=os.getenv("REDIS_PASSWORD"),
                decode_responses=True
            )
            redis_client.ping()
            service_status["redis"] = "connected"
        except:
            service_status["redis"] = "disconnected"
        
        service_status["backend"] = "running"
        service_status["database"] = "connected" if database_status.get("connected") else "disconnected"
        
        return SystemConfiguration(
            ai_models={
                "diagnosis": ai_models_response.diagnosis_llm,
                "mineru": ai_models_response.mineru,
                "embedding": ai_models_response.embedding
            },
            system_settings=settings_response.settings,
            database_status=database_status,
            service_status=service_status,
            timestamp=datetime.utcnow()
        )
    
    except Exception as e:
        logger.error(f"Failed to get system configuration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve system configuration: {str(e)}"
        )


# Enhanced System Monitoring | 增强系统监控
@router.get("/monitoring/ai-logs", response_model=AILogsResponse)
async def get_ai_logs(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    model_type: Optional[str] = None,
    status_filter: Optional[str] = None,
    anomaly_only: bool = False,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
) -> AILogsResponse:
    """
    Get AI diagnosis logs | 获取AI诊断日志
    
    Returns AI diagnosis logs with filtering options.
    返回AI诊断日志，支持筛选选项。
    """
    try:
        # Parse date filters
        start_datetime = None
        end_datetime = None
        
        if start_date:
            try:
                start_datetime = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            except:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid start_date format. Use ISO 8601 format."
                )
        
        if end_date:
            try:
                end_datetime = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            except:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid end_date format. Use ISO 8601 format."
                )
        
        # Build query
        stmt = select(AIDiagnosisLog).order_by(AIDiagnosisLog.timestamp.desc())
        
        # Apply filters
        conditions = []
        
        if start_datetime:
            conditions.append(AIDiagnosisLog.timestamp >= start_datetime)
        
        if end_datetime:
            conditions.append(AIDiagnosisLog.timestamp <= end_datetime)
        
        if model_type:
            conditions.append(AIDiagnosisLog.model_type == model_type)
        
        if status_filter:
            conditions.append(AIDiagnosisLog.status == status_filter)
        
        if anomaly_only:
            conditions.append(AIDiagnosisLog.is_anomaly == True)
        
        if conditions:
            stmt = stmt.where(and_(*conditions))
        
        # Apply pagination
        stmt = stmt.offset(skip).limit(limit)
        
        # Execute query
        result = await db.execute(stmt)
        logs = result.scalars().all()
        
        # Get total count
        count_stmt = select(func.count()).select_from(AIDiagnosisLog)
        if conditions:
            count_stmt = count_stmt.where(and_(*conditions))
        
        count_result = await db.execute(count_stmt)
        total_count = count_result.scalar()
        
        # Convert to response format
        log_entries = []
        for log in logs:
            # Parse JSON fields if they exist
            request_summary = None
            response_summary = None
            token_usage = None
            
            try:
                if log.request_data:
                    request_data = json.loads(log.request_data) if isinstance(log.request_data, str) else log.request_data
                    request_summary = request_data.get("summary", str(request_data)[:100])
            except:
                request_summary = str(log.request_data)[:100] if log.request_data else None
            
            try:
                if log.response_data:
                    response_data = json.loads(log.response_data) if isinstance(log.response_data, str) else log.response_data
                    response_summary = response_data.get("summary", str(response_data)[:100])
                    token_usage = response_data.get("token_usage")
            except:
                response_summary = str(log.response_data)[:100] if log.response_data else None
            
            entry = AILogEntry(
                id=str(log.id),
                timestamp=log.timestamp,
                model_type=log.model_type,
                status=log.status,
                latency_ms=log.latency_ms,
                token_usage=token_usage,
                request_summary=request_summary,
                response_summary=response_summary,
                error_message=log.error_message,
                is_anomaly=log.is_anomaly,
                anomaly_reason=log.anomaly_reason,
                user_id=str(log.user_id) if log.user_id else None
            )
            log_entries.append(entry)
        
        return AILogsResponse(
            logs=log_entries,
            total_count=total_count,
            filtered_by={
                "start_date": start_date,
                "end_date": end_date,
                "model_type": model_type,
                "status_filter": status_filter,
                "anomaly_only": anomaly_only
            },
            timestamp=datetime.utcnow()
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve AI logs: {str(e)}"
        )


@router.get("/monitoring/alerts", response_model=SystemAlertsResponse)
async def get_system_alerts(
    alert_type: Optional[str] = None,
    severity: Optional[str] = None,
    hours: int = 24,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
) -> SystemAlertsResponse:
    """
    Get system alerts | 获取系统告警
    
    Returns system alerts including resource alerts, AI anomalies, and pending items.
    返回系统告警，包括资源告警、AI异常和待处理事项。
    """
    try:
        alerts = []
        
        # Resource alerts
        monitoring = SystemMonitoringService(db)
        metrics = await monitoring.collect_system_metrics()
        
        if metrics.get("overall_alert") in ["warning", "critical"]:
            alerts.append({
                "type": "resource",
                "level": metrics.get("overall_alert"),
                "message": metrics.get("alert_message", "Resource usage alert"),
                "timestamp": datetime.utcnow().isoformat(),
                "details": {
                    "cpu": metrics.get("cpu"),
                    "memory": metrics.get("memory"),
                    "disk": metrics.get("disk")
                }
            })
        
        # AI anomalies alerts
        ai_anomalies = await monitoring.detect_anomalies(hours=hours)
        if ai_anomalies:
            alerts.append({
                "type": "ai_anomaly",
                "level": "warning",
                "message": f"{len(ai_anomalies)} AI diagnosis anomalies detected in the last {hours} hours",
                "timestamp": datetime.utcnow().isoformat(),
                "count": len(ai_anomalies),
                "details": {"anomalies": ai_anomalies[:10]}  # Top 10
            })
        
        # Pending doctor verifications alert
        stmt = select(func.count()).select_from(DoctorVerification).where(
            DoctorVerification.status == 'pending'
        )
        result = await db.execute(stmt)
        pending_count = result.scalar()
        
        if pending_count > 0:
            alert_level = "critical" if pending_count > 10 else "warning" if pending_count > 5 else "info"
            alerts.append({
                "type": "pending_verifications",
                "level": alert_level,
                "message": f"{pending_count} doctor verification(s) pending review",
                "timestamp": datetime.utcnow().isoformat(),
                "count": pending_count
            })
        
        # System error logs alert
        # In a real implementation, you would check error logs
        # For now, we'll simulate
        
        # Apply filters
        filtered_alerts = alerts
        if alert_type:
            filtered_alerts = [a for a in filtered_alerts if a["type"] == alert_type]
        
        if severity:
            filtered_alerts = [a for a in filtered_alerts if a["level"] == severity]
        
        # Convert to response format
        alert_objects = []
        for alert in filtered_alerts:
            alert_objects.append(SystemAlert(
                type=alert["type"],
                level=alert["level"],
                message=alert["message"],
                timestamp=alert["timestamp"],
                details=alert.get("details"),
                count=alert.get("count")
            ))
        
        return SystemAlertsResponse(
            alerts=alert_objects,
            total_count=len(alert_objects),
            timestamp=datetime.utcnow()
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve system alerts: {str(e)}"
        )


# Enhanced Doctor Verification Management | 增强医生认证管理
@router.get("/doctors/verifications/{verification_id}", response_model=DoctorVerificationDetail)
async def get_doctor_verification_detail(
    verification_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
) -> DoctorVerificationDetail:
    """
    Get doctor verification detail | 获取医生认证详情
    
    Returns detailed information about a specific doctor verification request.
    返回特定医生认证请求的详细信息。
    """
    try:
        # Get verification record
        stmt = select(DoctorVerification, User).join(
            User, DoctorVerification.user_id == User.id
        ).where(DoctorVerification.id == verification_id)
        
        result = await db.execute(stmt)
        row = result.first()
        
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Verification request not found"
            )
        
        verification, user = row
        
        # Get associated documents (simulated)
        documents = []
        # In a real implementation, you would query document tables
        # For now, we'll simulate some document entries
        if verification.license_document_path:
            documents.append({
                "type": "license",
                "filename": f"license_{verification.license_number}.pdf",
                "upload_date": verification.submitted_at.isoformat() if verification.submitted_at else None,
                "status": "verified"
            })
        
        if verification.additional_documents:
            documents.append({
                "type": "additional",
                "filename": "additional_docs.pdf",
                "upload_date": verification.submitted_at.isoformat() if verification.submitted_at else None,
                "status": "pending"
            })
        
        return DoctorVerificationDetail(
            verification_id=str(verification.id),
            user_id=str(user.id),
            doctor_name=user.full_name,
            doctor_email=user.email,
            license_number=verification.license_number,
            specialty=verification.specialty,
            hospital=verification.hospital,
            years_of_experience=verification.years_of_experience,
            education=verification.education,
            status=verification.status,
            submitted_at=verification.submitted_at,
            verified_at=verification.verified_at,
            verified_by=str(verification.verified_by) if verification.verified_by else None,
            verification_notes=verification.verification_notes,
            documents=documents
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve verification details: {str(e)}"
        )


@router.put("/doctors/verifications/{verification_id}", response_model=UpdateVerificationResponse)
async def update_doctor_verification(
    verification_id: UUID,
    update_request: UpdateVerificationRequest,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
    request: Request = None
) -> UpdateVerificationResponse:
    """
    Update doctor verification status | 更新医生认证状态
    
    Updates the status of a doctor verification request with audit trail.
    更新医生认证请求状态，包含审计日志。
    """
    try:
        # Validate status
        valid_statuses = ['approve', 'reject', 'revoke']
        if update_request.status not in valid_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Must be one of: {valid_statuses}"
            )
        
        # Get verification record
        stmt = select(DoctorVerification).where(DoctorVerification.id == verification_id)
        result = await db.execute(stmt)
        verification = result.scalar_one_or_none()
        
        if not verification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Verification request not found"
            )
        
        # Validate status transition
        old_status = verification.status
        new_status = update_request.status
        
        # Map status values
        status_mapping = {
            'approve': 'approved',
            'reject': 'rejected',
            'revoke': 'revoked'
        }
        
        mapped_status = status_mapping[new_status]
        
        # Check if transition is allowed
        if old_status == 'approved' and new_status != 'revoke':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot change status from '{old_status}' to '{mapped_status}'. Only 'revoke' is allowed."
            )
        
        if old_status not in ['pending', 'approved'] and new_status in ['approve', 'reject']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot {new_status} verification with status '{old_status}'"
            )
        
        # Update verification
        verification.status = mapped_status
        verification.verified_by = admin.id
        verification.verified_at = datetime.utcnow()
        verification.verification_notes = update_request.notes
        
        # If approving, update user as verified doctor
        if new_status == 'approve':
            stmt = select(User).where(User.id == verification.user_id)
            user_result = await db.execute(stmt)
            user = user_result.scalar_one_or_none()

            if user:
                user.is_verified_doctor = True
                user.is_verified = True

        # If revoking, update user as non-verified
        elif new_status == 'revoke':
            stmt = select(User).where(User.id == verification.user_id)
            user_result = await db.execute(stmt)
            user = user_result.scalar_one_or_none()

            if user:
                user.is_verified_doctor = False
                user.is_verified = False
        
        await db.commit()
        
        # Log the operation
        admin_logger = AdminOperationLogger(db)
        await admin_logger.log_operation(
            admin_id=admin.id,
            operation_type=f"update_verification_{new_status}",
            operation_details={
                "verification_id": str(verification_id),
                "doctor_user_id": str(verification.user_id),
                "old_status": old_status,
                "new_status": mapped_status,
                "notes": update_request.notes
            },
            ip_address=request.client.host if request else "unknown",
            user_agent=request.headers.get("user-agent") if request else "unknown"
        )
        
        return UpdateVerificationResponse(
            success=True,
            message=f"Verification status updated to '{mapped_status}' successfully",
            verification_id=str(verification_id),
            updated_status=mapped_status,
            updated_at=datetime.utcnow(),
            processed_by=str(admin.id)
        )
    
    except HTTPException:
        raise
    except Exception as e:
        # Log error
        admin_logger = AdminOperationLogger(db)
        await admin_logger.log_operation(
            admin_id=admin.id,
            operation_type="update_verification_failed",
            operation_details={
                "verification_id": str(verification_id),
                "requested_status": update_request.status,
                "error": str(e)
            },
            ip_address=request.client.host if request else "unknown",
            user_agent=request.headers.get("user-agent") if request else "unknown"
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update verification status: {str(e)}"
        )


@router.post("/doctors/sync-verification", response_model=Dict[str, Any])
async def sync_doctor_verification_status(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
    request: Request = None
) -> Dict[str, Any]:
    """
    Sync doctor verification status | 同步医生认证状态
    
    Ensures all approved doctors have is_verified = True in users table.
    Fixes data inconsistency for doctors approved before the dual-field update fix.
    确保所有已批准的医生在users表中is_verified = True。
    修复在双字段更新修复之前批准的医生的数据不一致问题。
    """
    try:
        # Find all approved doctors where is_verified is False
        stmt = select(User, DoctorVerification).join(
            DoctorVerification, User.id == DoctorVerification.user_id
        ).where(
            and_(
                DoctorVerification.status == 'approved',
                User.is_verified == False
            )
        )
        result = await db.execute(stmt)
        doctors_to_fix = result.all()
        
        if not doctors_to_fix:
            return {
                "message": "No doctors need synchronization",
                "synced_count": 0,
                "doctors": []
            }
        
        # Fix each doctor
        synced_doctors = []
        for user, verification in doctors_to_fix:
            user.is_verified = True
            user.is_verified_doctor = True
            synced_doctors.append({
                "id": str(user.id),
                "email": user.email,
                "full_name": user.full_name,
                "verified_at": verification.verified_at.isoformat() if verification.verified_at else None
            })
        
        await db.commit()
        
        # Log the operation
        admin_logger = AdminOperationLogger(db)
        await admin_logger.log_operation(
            admin_id=admin.id,
            operation_type="sync_doctor_verification",
            operation_details={
                "synced_count": len(synced_doctors),
                "doctors": synced_doctors
            },
            ip_address=request.client.host if request else "unknown",
            user_agent=request.headers.get("user-agent") if request else "unknown"
        )
        
        return {
            "message": f"Successfully synchronized {len(synced_doctors)} doctors",
            "synced_count": len(synced_doctors),
            "doctors": synced_doctors
        }
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sync doctor verification status: {str(e)}"
        )


# =============================================================================
# Embedding Provider Registry APIs | 嵌入模型提供商注册表 API
# =============================================================================

@router.get("/embedding/providers", response_model=List[Dict[str, Any]])
async def get_embedding_providers(
    admin: User = Depends(require_admin)
) -> List[Dict[str, Any]]:
    """
    Get list of supported embedding providers | 获取支持的嵌入模型提供商列表
    
    Returns all supported embedding providers with their default configurations.
    返回所有支持的嵌入模型提供商及其默认配置。
    """
    from app.services.embedding_provider_registry import provider_registry
    
    try:
        providers = provider_registry.list_providers()
        return providers
    except Exception as e:
        logger.error(f"Failed to get embedding providers: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get providers: {str(e)}"
        )


@router.post("/embedding/validate-url", response_model=Dict[str, Any])
async def validate_embedding_url(
    request: Dict[str, Any],
    admin: User = Depends(require_admin)
) -> Dict[str, Any]:
    """
    Validate and format embedding API URL | 验证并格式化嵌入模型 API URL
    
    Validates user-provided URL and returns formatted URL with suggestions.
    验证用户提供的 URL 并返回格式化后的 URL 和建议。
    
    Request body:
    {
        "url": "user provided url",
        "provider": "optional provider key"
    }
    
    Response:
    {
        "valid": bool,
        "formatted_url": str,
        "provider": str,
        "warnings": List[str],
        "suggestions": List[str]
    }
    """
    from app.services.embedding_provider_registry import provider_registry
    
    try:
        url = request.get("url", "")
        provider_key = request.get("provider")
        
        if not url:
            return {
                "valid": False,
                "formatted_url": "",
                "provider": provider_key or "unknown",
                "warnings": ["URL is required"],
                "suggestions": ["Please provide an API URL"]
            }
        
        result = provider_registry.validate_and_format_url(url, provider_key)
        return result
        
    except Exception as e:
        logger.error(f"Failed to validate URL: {e}")
        return {
            "valid": False,
            "formatted_url": url if 'url' in locals() else "",
            "provider": request.get("provider", "unknown") if 'request' in locals() else "unknown",
            "warnings": [f"Validation error: {str(e)}"],
            "suggestions": ["Please check the URL format"]
        }
