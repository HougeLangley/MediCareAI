"""
Database Models - MediCare_AI | 数据库模型 - MediCare_AI
SQLAlchemy ORM Models for Intelligent Disease Management System | 智能疾病管理系统的 SQLAlchemy ORM 模型

This module defines all database tables and their relationships using SQLAlchemy ORM.
The models follow these design principles:
- UUID primary keys for security and distribution
- Proper indexing for query performance
- Relationship cascade configuration for data integrity
- Audit fields (created_at, updated_at) on all tables

本模块使用 SQLAlchemy ORM 定义所有数据库表及其关系。
模型遵循以下设计原则：
- UUID 主键用于安全性和分布式部署
- 适当的索引用于查询性能
- 关系级联配置确保数据完整性
- 所有表都有审计字段（created_at, updated_at）

Tables | 表:
- users: User accounts | 用户账户
- patients: Patient profiles | 患者档案
- diseases: Disease definitions | 疾病定义
- medical_cases: Medical records | 医疗记录
- medical_documents: Uploaded files | 上传文件
- ai_feedbacks: AI diagnosis results | AI 诊断结果
- follow_ups: Follow-up schedules | 随访计划
- user_sessions: Active JWT sessions | 活跃 JWT 会话
- audit_logs: Security audit trail | 安全审计日志

Author: MediCare_AI Team
Version: 1.0.0
"""

from sqlalchemy import Column, String, DateTime, Date, Boolean, Text, Integer, DECIMAL, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB, INET
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.db.database import Base
import logging

logger = logging.getLogger(__name__)

# =============================================================================
# User Model | 用户模型
# =============================================================================
class User(Base):
    """
    User Model - Core authentication entity | 用户模型 - 核心认证实体
    
    Stores user account information including authentication credentials.
    Each user can have one patient profile and multiple sessions.
    
    存储用户账户信息，包括认证凭据。
    每个用户可以有一个患者档案和多个会话。
    
    Relationships | 关系:
    - patients: One-to-one with Patient / 与 Patient 一对一
    - user_sessions: One-to-many with UserSession / 与 UserSession 一对多
    - audit_logs: One-to-many with AuditLog / 与 AuditLog 一对多
    """
    __tablename__ = "users"
    
    # Primary Key | 主键
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
                comment="Unique user identifier / 唯一用户标识符")
    
    # Authentication Fields | 认证字段
    email = Column(String(255), unique=True, nullable=False, index=True,
                   comment="User email address (unique) / 用户邮箱地址（唯一）")
    password_hash = Column(String(255), nullable=False,
                          comment="Bcrypt hashed password / Bcrypt 哈希密码")
    
    # Profile Fields | 个人资料字段
    full_name = Column(String(255), nullable=False,
                      comment="User's full name / 用户全名")
    
    # Status Fields | 状态字段
    is_active = Column(Boolean, default=True,
                      comment="Account active status / 账户激活状态")
    is_verified = Column(Boolean, default=False,
                        comment="Email verification status / 邮箱验证状态")
    
    # Audit Timestamps | 审计时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(),
                       comment="Record creation time / 记录创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(),
                       comment="Record last update time / 记录最后更新时间")
    last_login = Column(DateTime(timezone=True),
                       comment="Last successful login time / 最后成功登录时间")
    
    # Relationships | 关系
    patients = relationship("Patient", back_populates="user", 
                           cascade="all, delete-orphan")
    user_sessions = relationship("UserSession", back_populates="user",
                                cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user")


# =============================================================================
# Disease Model | 疾病模型
# =============================================================================
class Disease(Base):
    """
    Disease Model - Medical condition definitions | 疾病模型 - 医疗状况定义
    
    Stores disease information including medical guidelines in JSON format.
    Used by the AI diagnosis system to provide evidence-based recommendations.
    
    存储疾病信息，包括 JSON 格式的医疗指南。
    AI 诊断系统使用这些信息提供循证建议。
    
    Relationships | 关系:
    - medical_cases: One-to-many with MedicalCase / 与 MedicalCase 一对多
    """
    __tablename__ = "diseases"
    
    # Primary Key | 主键
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
                comment="Unique disease identifier / 唯一疾病标识符")
    
    # Disease Information | 疾病信息
    name = Column(String(255), unique=True, nullable=False,
                 comment="Disease name (unique) / 疾病名称（唯一）")
    code = Column(String(50), unique=True,
                 comment="Disease code (e.g., ICD-10) / 疾病代码（如 ICD-10）")
    description = Column(Text,
                        comment="Detailed disease description / 详细疾病描述")
    
    # Guidelines | 指南
    guidelines_json = Column(JSONB,
                            comment="Medical guidelines in JSON format / JSON 格式的医疗指南")
    
    # Status | 状态
    is_active = Column(Boolean, default=True,
                      comment="Disease active status / 疾病激活状态")
    
    # Audit Timestamps | 审计时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(),
                       comment="Record creation time / 记录创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(),
                       comment="Record last update time / 记录最后更新时间")
    
    # Relationships | 关系
    medical_cases = relationship("MedicalCase", back_populates="disease")


# =============================================================================
# Patient Model | 患者模型
# =============================================================================
class Patient(Base):
    """
    Patient Model - Medical profile entity | 患者模型 - 医疗档案实体
    
    Stores patient-specific medical information.
    Note: Patient name is retrieved from User.full_name to avoid data redundancy.
    The name field here is kept for backward compatibility.
    
    存储患者特定的医疗信息。
    注意：患者名称从 User.full_name 获取以避免数据冗余。
    此处的 name 字段保留用于向后兼容。
    
    Relationships | 关系:
    - user: Many-to-one with User / 与 User 多对一
    - medical_cases: One-to-many with MedicalCase / 与 MedicalCase 一对多
    """
    __tablename__ = "patients"
    
    # Primary Key | 主键
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
                comment="Unique patient identifier / 唯一患者标识符")
    
    # Foreign Keys | 外键
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), 
                     nullable=False, index=True,
                     comment="Reference to users.id / 引用 users.id")
    
    # Profile Fields | 个人资料字段
    # Note: name is deprecated, use User.full_name instead / 注意：name 已弃用，请使用 User.full_name
    name = Column(String(255), nullable=True,
                 comment="[DEPRECATED] Use User.full_name / [已弃用] 请使用 User.full_name")
    date_of_birth = Column(Date, nullable=True,
                          comment="Patient date of birth / 患者出生日期")
    gender = Column(String(10),
                   comment="Patient gender (male/female) / 患者性别（男/女）")
    phone = Column(String(20),
                  comment="Contact phone number / 联系电话")
    
    # Contact Information | 联系信息
    address = Column(Text,
                    comment="Residential address / 居住地址")
    emergency_contact = Column(String(255),
                              comment="Emergency contact info (name + phone) / 紧急联系人信息（姓名+电话）")
    
    # Medical Information | 医疗信息
    medical_record_number = Column(String(100), unique=True,
                                  comment="Unique medical record number / 唯一病历号")
    notes = Column(Text,
                  comment="Additional medical notes / 额外医疗备注")
    
    # Audit Timestamps | 审计时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(),
                       comment="Record creation time / 记录创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(),
                       comment="Record last update time / 记录最后更新时间")
    
    # Relationships | 关系
    user = relationship("User", back_populates="patients")
    medical_cases = relationship("MedicalCase", back_populates="patient",
                                cascade="all, delete-orphan")


# =============================================================================
# Medical Case Model | 医疗病例模型
# =============================================================================
class MedicalCase(Base):
    """
    Medical Case Model - Individual medical consultation record | 医疗病例模型 - 单个医疗咨询记录
    
    Represents a single medical case or consultation session.
    Contains symptoms, diagnosis, and related documents.
    
    表示单个医疗病例或咨询会话。
    包含症状、诊断和相关文档。
    
    Relationships | 关系:
    - patient: Many-to-one with Patient / 与 Patient 多对一
    - disease: Many-to-one with Disease / 与 Disease 多对一
    - medical_documents: One-to-many with MedicalDocument / 与 MedicalDocument 一对多
    - ai_feedbacks: One-to-many with AIFeedback / 与 AIFeedback 一对多
    - follow_ups: One-to-many with FollowUp / 与 FollowUp 一对多
    """
    __tablename__ = "medical_cases"
    
    # Primary Key | 主键
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
                comment="Unique case identifier / 唯一病例标识符")
    
    # Foreign Keys | 外键
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"),
                        nullable=False, index=True,
                        comment="Reference to patients.id / 引用 patients.id")
    disease_id = Column(UUID(as_uuid=True), ForeignKey("diseases.id"),
                        nullable=False, index=True,
                        comment="Reference to diseases.id / 引用 diseases.id")
    
    # Case Information | 病例信息
    title = Column(String(255), nullable=False,
                  comment="Case title / 病例标题")
    description = Column(Text,
                        comment="Detailed case description / 详细病例描述")
    symptoms = Column(Text,
                     comment="Reported symptoms / 报告的症状")
    clinical_findings = Column(JSONB,
                              comment="Structured clinical findings / 结构化临床发现")
    diagnosis = Column(Text,
                      comment="Final diagnosis / 最终诊断")
    
    # Classification | 分类
    severity = Column(String(20),
                     comment="Case severity (low/moderate/high/critical) / 病例严重程度（低/中/高/危急）")
    status = Column(String(20), default='active',
                   comment="Case status (active/closed/pending) / 病例状态（活跃/已关闭/待处理）")
    
    # Audit Timestamps | 审计时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(),
                       comment="Record creation time / 记录创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(),
                       comment="Record last update time / 记录最后更新时间")
    
    # Relationships | 关系
    patient = relationship("Patient", back_populates="medical_cases")
    disease = relationship("Disease", back_populates="medical_cases")
    medical_documents = relationship("MedicalDocument", back_populates="medical_case",
                                    cascade="all, delete-orphan")
    ai_feedbacks = relationship("AIFeedback", back_populates="medical_case")
    follow_ups = relationship("FollowUp", back_populates="medical_case")


# =============================================================================
# Medical Document Model | 医疗文档模型
# =============================================================================
class MedicalDocument(Base):
    """
    Medical Document Model - File attachments | 医疗文档模型 - 文件附件
    
    Stores information about uploaded medical files (PDFs, images, etc.)
    and their extracted text content via MinerU.
    
    存储上传的医疗文件信息（PDF、图片等）及其通过 MinerU 提取的文本内容。
    
    Relationships | 关系:
    - medical_case: Many-to-one with MedicalCase / 与 MedicalCase 多对一
    """
    __tablename__ = "medical_documents"
    
    # Primary Key | 主键
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
                comment="Unique document identifier / 唯一文档标识符")
    
    # Foreign Keys | 外键
    medical_case_id = Column(UUID(as_uuid=True), ForeignKey("medical_cases.id"),
                             nullable=False, index=True,
                             comment="Reference to medical_cases.id / 引用 medical_cases.id")
    
    # File Information | 文件信息
    filename = Column(String(255), nullable=False,
                     comment="Stored filename / 存储的文件名")
    original_filename = Column(String(255), nullable=False,
                              comment="Original upload filename / 原始上传文件名")
    file_type = Column(String(50), nullable=False,
                      comment="MIME type / MIME 类型")
    file_size = Column(Integer,
                      comment="File size in bytes / 文件大小（字节）")
    file_path = Column(String(500),
                      comment="Storage path / 存储路径")
    
    # Processing Status | 处理状态
    upload_status = Column(String(20), default='uploaded',
                          comment="Upload status (uploaded/processing/failed) / 上传状态")
    
    # Extracted Content | 提取内容
    extracted_content = Column(JSONB,
                              comment="MinerU extracted content / MinerU 提取的内容")
    extraction_metadata = Column(JSONB,
                                comment="Extraction metadata (confidence, etc.) / 提取元数据")
    
    # Audit Timestamps | 审计时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(),
                       comment="Record creation time / 记录创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(),
                       comment="Record last update time / 记录最后更新时间")
    
    # Relationships | 关系
    medical_case = relationship("MedicalCase", back_populates="medical_documents")


# =============================================================================
# AI Feedback Model | AI 反馈模型
# =============================================================================
class AIFeedback(Base):
    """
    AI Feedback Model - AI diagnosis results | AI 反馈模型 - AI 诊断结果
    
    Stores AI-generated diagnosis results including confidence scores
    and recommendations. Linked to medical cases for tracking.
    
    存储 AI 生成的诊断结果，包括置信度分数和建议。
    与医疗病例关联以便追踪。
    
    Relationships | 关系:
    - medical_case: Many-to-one with MedicalCase / 与 MedicalCase 多对一
    """
    __tablename__ = "ai_feedbacks"
    
    # Primary Key | 主键
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
                comment="Unique feedback identifier / 唯一反馈标识符")
    
    # Foreign Keys | 外键
    medical_case_id = Column(UUID(as_uuid=True), ForeignKey("medical_cases.id"),
                             nullable=False, index=True,
                             comment="Reference to medical_cases.id / 引用 medical_cases.id")
    
    # AI Input/Output | AI 输入/输出
    feedback_type = Column(String(50), nullable=False,
                          comment="Type of AI feedback / AI 反馈类型")
    input_data = Column(JSONB, nullable=False,
                       comment="Input data sent to AI / 发送给 AI 的输入数据")
    ai_response = Column(JSONB, nullable=False,
                        comment="Raw AI response / 原始 AI 响应")
    
    # Analysis | 分析
    confidence_score = Column(DECIMAL(3, 2),
                             comment="AI confidence score (0.00-1.00) / AI 置信度分数")
    recommendations = Column(Text,
                            comment="AI-generated recommendations / AI 生成的建议")
    follow_up_plan = Column(JSONB,
                           comment="Structured follow-up plan / 结构化随访计划")
    
    # Review Status | 审核状态
    is_reviewed = Column(Boolean, default=False,
                        comment="Whether reviewed by doctor / 是否已由医生审核")
    reviewed_by = Column(UUID(as_uuid=True),
                        comment="Doctor who reviewed / 审核医生的 ID")
    review_notes = Column(Text,
                         comment="Doctor review notes / 医生审核备注")
    
    # Audit Timestamps | 审计时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(),
                       comment="Record creation time / 记录创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(),
                       comment="Record last update time / 记录最后更新时间")
    
    # Relationships | 关系
    medical_case = relationship("MedicalCase", back_populates="ai_feedbacks")


# =============================================================================
# Follow-Up Model | 随访模型
# =============================================================================
class FollowUp(Base):
    """
    Follow-Up Model - Patient follow-up appointments | 随访模型 - 患者随访预约
    
    Tracks scheduled and completed follow-up appointments for patients.
    
    追踪患者的已预约和已完成的随访。
    
    Relationships | 关系:
    - medical_case: Many-to-one with MedicalCase / 与 MedicalCase 多对一
    """
    __tablename__ = "follow_ups"
    
    # Primary Key | 主键
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
                comment="Unique follow-up identifier / 唯一随访标识符")
    
    # Foreign Keys | 外键
    medical_case_id = Column(UUID(as_uuid=True), ForeignKey("medical_cases.id"),
                             nullable=False, index=True,
                             comment="Reference to medical_cases.id / 引用 medical_cases.id")
    
    # Schedule Information | 计划信息
    scheduled_date = Column(String(10), nullable=False,
                           comment="Scheduled date (YYYY-MM-DD) / 计划日期")
    actual_date = Column(String(10),
                        comment="Actual visit date (YYYY-MM-DD) / 实际就诊日期")
    follow_up_type = Column(String(50), nullable=False,
                           comment="Type of follow-up / 随访类型")
    
    # Status | 状态
    status = Column(String(20), default='scheduled',
                   comment="Status (scheduled/completed/cancelled) / 状态")
    
    # Visit Details | 就诊详情
    notes = Column(Text,
                  comment="Follow-up notes / 随访备注")
    symptoms_changes = Column(Text,
                             comment="Changes in symptoms / 症状变化")
    medication_adherence = Column(String(20),
                                 comment="Medication adherence level / 用药依从性水平")
    next_follow_up_date = Column(String(10),
                                comment="Next scheduled follow-up / 下次计划随访")
    
    # Audit Timestamps | 审计时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(),
                       comment="Record creation time / 记录创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(),
                       comment="Record last update time / 记录最后更新时间")
    
    # Relationships | 关系
    medical_case = relationship("MedicalCase", back_populates="follow_ups")


# =============================================================================
# User Session Model | 用户会话模型
# =============================================================================
class UserSession(Base):
    """
    User Session Model - JWT session tracking | 用户会话模型 - JWT 会话追踪
    
    Tracks active JWT sessions for users. Used for logout functionality
    and session management.
    
    追踪用户的活跃 JWT 会话。用于登出功能和会话管理。
    
    Relationships | 关系:
    - user: Many-to-one with User / 与 User 多对一
    """
    __tablename__ = "user_sessions"
    
    # Primary Key | 主键
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
                comment="Unique session identifier / 唯一会话标识符")
    
    # Foreign Keys | 外键
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"),
                     nullable=False, index=True,
                     comment="Reference to users.id / 引用 users.id")
    
    # Session Information | 会话信息
    token_id = Column(String(255), nullable=False, index=True,
                     comment="JWT token identifier / JWT 令牌标识符")
    expires_at = Column(DateTime(timezone=True), nullable=False,
                       comment="Session expiration time / 会话过期时间")
    
    # Status | 状态
    is_active = Column(Boolean, default=True,
                      comment="Session active status / 会话激活状态")
    
    # Audit Timestamp | 审计时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(),
                       comment="Session creation time / 会话创建时间")
    
    # Relationships | 关系
    user = relationship("User", back_populates="user_sessions")


# =============================================================================
# Audit Log Model | 审计日志模型
# =============================================================================
class AuditLog(Base):
    """
    Audit Log Model - Security audit trail | 审计日志模型 - 安全审计日志
    
    Records all significant user actions for security and compliance.
    Tracks who did what, when, and from where.
    
    记录所有重要用户操作，用于安全和合规性。
    追踪谁在何时何地做了什么。
    
    Relationships | 关系:
    - user: Many-to-one with User (nullable) / 与 User 多对一（可空）
    """
    __tablename__ = "audit_logs"
    
    # Primary Key | 主键
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
                comment="Unique log entry identifier / 唯一日志条目标识符")
    
    # Foreign Keys | 外键
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), index=True,
                    comment="Reference to users.id (nullable) / 引用 users.id（可空）")
    
    # Action Information | 操作信息
    action = Column(String(100), nullable=False,
                   comment="Action performed / 执行的操作")
    resource_type = Column(String(50),
                          comment="Type of resource affected / 受影响的资源类型")
    resource_id = Column(UUID(as_uuid=True),
                        comment="ID of affected resource / 受影响资源的 ID")
    details = Column(JSONB,
                    comment="Additional details in JSON / JSON 格式的额外详情")
    
    # Request Context | 请求上下文
    ip_address = Column(INET,
                       comment="Client IP address / 客户端 IP 地址")
    user_agent = Column(Text,
                       comment="Client user agent string / 客户端用户代理字符串")
    
    # Audit Timestamp | 审计时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), 
                        index=True,
                        comment="Log entry time / 日志条目时间")
    
    # Relationships | 关系
    user = relationship("User", back_populates="audit_logs")
