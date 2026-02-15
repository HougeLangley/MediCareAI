"""
Admin API Schemas | 管理员API数据模式

Pydantic models for admin endpoints.
管理员端点的Pydantic模型。
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class DashboardSummaryResponse(BaseModel):
    """Dashboard summary response | 仪表板概览响应"""
    timestamp: str
    system_status: Dict[str, Any]
    ai_statistics_24h: Dict[str, Any]
    user_statistics: Dict[str, Any]
    recent_anomalies: List[Dict[str, Any]]


class SystemMetricsResponse(BaseModel):
    """System metrics response | 系统指标响应"""
    current: Dict[str, Any]
    historical: List[Dict[str, Any]]
    summary: Dict[str, Any]


class AIStatisticsResponse(BaseModel):
    """AI statistics response | AI统计响应"""
    period_days: int
    total_requests: int
    successful: int
    failed: int
    timeouts: int
    anomalies: int
    success_rate: float
    average_latency_ms: float
    status_breakdown: Dict[str, int]


class PendingDoctorVerification(BaseModel):
    """Pending doctor verification | 待审核医生认证"""
    verification_id: str
    user_id: str
    doctor_name: str
    doctor_email: str
    license_number: str
    specialty: str
    hospital: str
    submitted_at: str
    years_of_experience: Optional[int]
    education: Optional[str]


class DoctorVerificationAction(BaseModel):
    """Doctor verification action | 医生认证操作"""
    notes: Optional[str] = None


class DoctorVerificationActionResponse(BaseModel):
    """Doctor verification action response | 医生认证操作响应"""
    success: bool
    message: str
    verification_id: str
    processed_at: str


class AdminOperationLogEntry(BaseModel):
    """Admin operation log entry | 管理员操作日志条目"""
    id: str
    admin_id: str
    timestamp: str
    operation_type: str
    operation_details: Dict[str, Any]
    ip_address: Optional[str]


class SystemAlert(BaseModel):
    """System alert | 系统告警"""
    type: str
    level: str
    message: str
    timestamp: str
    details: Optional[Dict[str, Any]] = None
    count: Optional[int] = None


class LogSystemMetricsResponse(BaseModel):
    """Log system metrics response | 记录系统指标响应"""
    success: bool
    log_id: Optional[str]
    timestamp: str
    message: str


class LogAdminOperationRequest(BaseModel):
    """Log admin operation request | 记录管理员操作请求"""
    operation_type: str
    operation_details: Dict[str, Any]


# AI Model Configuration Schemas | AI模型配置模式
class AIModelConfig(BaseModel):
    """AI model configuration | AI模型配置"""
    api_url: str
    api_key: str
    model_id: str
    enabled: bool = True


class AIModelStatus(BaseModel):
    """AI model status | AI模型状态"""
    model_type: str
    api_url: Optional[str] = None
    model_id: Optional[str] = None
    enabled: bool = False
    last_tested: Optional[datetime] = None
    test_status: Optional[str] = None  # 'success', 'failed', 'pending'
    latency_ms: Optional[float] = None
    error_message: Optional[str] = None


class AIModelsResponse(BaseModel):
    """AI models response | AI模型列表响应"""
    diagnosis_llm: AIModelStatus
    mineru: AIModelStatus
    embedding: AIModelStatus
    oss: Optional[AIModelStatus] = None
    timestamp: datetime


class AIModelTestRequest(BaseModel):
    """AI model test request | AI模型测试请求"""
    test_payload: Optional[Dict[str, Any]] = None


class AIModelTestResponse(BaseModel):
    """AI model test response | AI模型测试响应"""
    success: bool
    model_type: str
    latency_ms: float
    status_code: Optional[int] = None
    response_summary: Optional[str] = None
    error_message: Optional[str] = None
    timestamp: datetime


# Knowledge Base Management Schemas | 知识库管理模式
class KnowledgeBaseDocument(BaseModel):
    """Knowledge base document | 知识库文档"""
    doc_id: str
    filename: str
    file_size: int
    status: str  # 'uploading', 'processing', 'completed', 'failed'
    chunk_count: Optional[int] = 0
    error_message: Optional[str] = None
    uploaded_at: datetime
    processed_at: Optional[datetime] = None
    file_type: str
    preview: Optional[str] = None


class KnowledgeBaseDocumentsResponse(BaseModel):
    """Knowledge base documents response | 知识库文档列表响应"""
    documents: List[KnowledgeBaseDocument]
    total_count: int
    timestamp: datetime


class KnowledgeBaseUploadResponse(BaseModel):
    """Knowledge base upload response | 知识库上传响应"""
    success: bool
    doc_id: str
    filename: str
    status: str
    message: str
    timestamp: datetime


# Enhanced Monitoring Schemas | 增强监控模式
class AILogEntry(BaseModel):
    """AI diagnosis log entry | AI诊断日志条目"""
    id: str
    timestamp: datetime
    model_type: str
    status: str  # 'success', 'failed', 'timeout'
    latency_ms: float
    token_usage: Optional[Dict[str, int]] = None
    request_summary: Optional[str] = None
    response_summary: Optional[str] = None
    error_message: Optional[str] = None
    is_anomaly: bool = False
    anomaly_reason: Optional[str] = None
    user_id: Optional[str] = None


class AILogsResponse(BaseModel):
    """AI logs response | AI日志响应"""
    logs: List[AILogEntry]
    total_count: int
    filtered_by: Dict[str, Any]
    timestamp: datetime


class SystemAlertsResponse(BaseModel):
    """System alerts response | 系统告警响应"""
    alerts: List[SystemAlert]
    total_count: int
    timestamp: datetime


# Enhanced Doctor Verification Schemas | 增强医生认证模式
class DoctorVerificationDetail(BaseModel):
    """Doctor verification detail | 医生认证详情"""
    verification_id: str
    user_id: str
    doctor_name: str
    doctor_email: str
    license_number: str
    specialty: str
    hospital: str
    years_of_experience: Optional[int]
    education: Optional[str]
    status: str  # 'pending', 'approved', 'rejected', 'revoked'
    submitted_at: datetime
    verified_at: Optional[datetime] = None
    verified_by: Optional[str] = None
    verification_notes: Optional[str] = None
    documents: List[Dict[str, Any]] = []


class UpdateVerificationRequest(BaseModel):
    """Update verification request | 更新认证请求"""
    status: str  # 'approve', 'reject', 'revoke'
    notes: Optional[str] = None


class UpdateVerificationResponse(BaseModel):
    """Update verification response | 更新认证响应"""
    success: bool
    message: str
    verification_id: str
    updated_status: str
    updated_at: datetime
    processed_by: str


# System Settings Schemas | 系统设置模式
class SystemSettings(BaseModel):
    """System settings | 系统设置"""
    max_file_size: int = 200 * 1024 * 1024  # 200MB
    allowed_file_types: List[str] = [".pdf", ".jpg", ".jpeg", ".png", ".doc", ".docx", ".ppt", ".pptx", ".md"]
    log_level: str = "INFO"
    debug_mode: bool = False
    maintenance_mode: bool = False
    ai_request_timeout: int = 30  # seconds
    ai_max_retries: int = 3
    embedding_batch_size: int = 100
    knowledge_base_chunk_size: int = 1000
    pii_detection_enabled: bool = True
    data_retention_days: int = 365
    session_timeout_minutes: int = 30
    max_concurrent_requests: int = 100
    enable_anomaly_detection: bool = True
    anomaly_threshold_ms: int = 5000


class SystemSettingsResponse(BaseModel):
    """System settings response | 系统设置响应"""
    settings: SystemSettings
    timestamp: datetime


class UpdateSystemSettingsRequest(BaseModel):
    """Update system settings request | 更新系统设置请求"""
    max_file_size: Optional[int] = None
    allowed_file_types: Optional[List[str]] = None
    log_level: Optional[str] = None
    debug_mode: Optional[bool] = None
    maintenance_mode: Optional[bool] = None
    ai_request_timeout: Optional[int] = None
    ai_max_retries: Optional[int] = None
    embedding_batch_size: Optional[int] = None
    knowledge_base_chunk_size: Optional[int] = None
    pii_detection_enabled: Optional[bool] = None
    data_retention_days: Optional[int] = None
    session_timeout_minutes: Optional[int] = None
    max_concurrent_requests: Optional[int] = None
    enable_anomaly_detection: Optional[bool] = None
    anomaly_threshold_ms: Optional[int] = None


class UpdateSystemSettingsResponse(BaseModel):
    """Update system settings response | 更新系统设置响应"""
    success: bool
    message: str
    updated_settings: SystemSettings
    timestamp: datetime


# Enhanced Knowledge Base Schemas | 增强知识库模式
class KnowledgeBaseDocumentStatus(BaseModel):
    """Knowledge base document status | 知识库文档状态"""
    doc_id: str
    filename: str
    status: str  # 'pending', 'processing', 'completed', 'failed'
    chunk_count: int
    vector_count: int
    file_size: int
    uploaded_at: datetime
    processed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    processing_progress: Optional[float] = None  # 0.0 to 1.0


class KnowledgeBaseDocumentStatusResponse(BaseModel):
    """Knowledge base document status response | 知识库文档状态响应"""
    document: KnowledgeBaseDocumentStatus
    timestamp: datetime


# Enhanced AI Model Configuration Schemas | 增强AI模型配置模式
class AIModelConfigRequest(BaseModel):
    """AI model configuration request | AI模型配置请求"""
    api_url: str
    api_key: str
    model_id: Optional[str] = None
    enabled: bool = True
    provider: Optional[str] = None  # AI provider: zhipu, kimi, deepseek, ollama, vllm, lmstudio, openai, custom
    access_key_id: Optional[str] = None  # For OSS configuration


class OSSConfigRequest(BaseModel):
    """OSS configuration request | OSS配置请求"""
    bucket: str
    endpoint: str
    access_key_id: str
    access_key_secret: str
    enabled: bool = True


class AIModelConfigResponse(BaseModel):
    """AI model configuration response | AI模型配置响应"""
    success: bool
    message: str
    model_type: str
    config: AIModelStatus
    test_result: Optional[Dict[str, Any]] = None
    timestamp: datetime


# API Key Management Schemas | API密钥管理模式
class APIKeyMask(BaseModel):
    """API key mask for security | API密钥脱敏"""
    masked_key: str
    key_length: int
    is_configured: bool


class SystemConfiguration(BaseModel):
    """System configuration overview | 系统配置概览"""
    ai_models: Dict[str, AIModelStatus]
    system_settings: SystemSettings
    database_status: Dict[str, Any]
    service_status: Dict[str, str]
    timestamp: datetime
