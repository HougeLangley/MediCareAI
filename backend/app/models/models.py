"""
Database Models v2.0 - MediCare_AI | 数据库模型 v2.0
Enhanced with Patient/Doctor/Admin roles, Data Sharing, Vector RAG, and Privacy Protection

Tables | 表:
- users: Unified user accounts (patient/doctor/admin) | 统一用户账户
- diseases: Disease definitions | 疾病定义
- medical_cases: Medical records | 医疗记录
- medical_documents: Uploaded files with PII-cleaned content | 上传文件（PII清理后）
- ai_feedbacks: AI diagnosis results | AI 诊断结果
- follow_ups: Follow-up schedules | 随访计划
- user_sessions: Active JWT sessions | 活跃 JWT 会话
- audit_logs: Security audit trail | 安全审计日志
- data_sharing_consents: Data sharing agreements | 数据共享同意书
- shared_medical_cases: Anonymized shared cases | 匿名化分享病例
- doctor_patient_relations: Doctor-patient relationships | 医生-患者关系
- knowledge_base_chunks: Vectorized knowledge base | 向量化知识库
- vector_embedding_configs: Vector model configurations | 向量模型配置
- system_resource_logs: System monitoring logs | 系统监控日志

Author: MediCare_AI Team
Version: 2.0.0
"""

from sqlalchemy import (
    Column, String, DateTime, Date, Boolean, Text, Integer, 
    DECIMAL, ForeignKey, Enum, Float, Index, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, INET, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.db.database import Base
import logging

logger = logging.getLogger(__name__)

# =============================================================================
# Unified User Model | 统一用户模型
# =============================================================================
class User(Base):
    """
    Unified User Model - Patient/Doctor/Admin | 统一用户模型 - 患者/医生/管理员
    
    Merges users and patients tables from v1.0.
    Uses role-based field access to support three user types in one table.
    
    合并v1.0的users和patients表。
    使用基于角色的字段访问，在一个表中支持三种用户类型。
    
    Roles | 角色:
    - patient: 患者 - 提交诊断、查看记录
    - doctor: 医生 - 查看分享病例、科研数据
    - admin: 管理员 - 系统监控、模型配置
    """
    __tablename__ = "users"
    
    # Primary Key | 主键
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
                comment="Unique user identifier / 唯一用户标识符")
    
    # Authentication Fields | 认证字段
    email = Column(String(255), unique=True, nullable=False, index=True,
                   comment="User email address / 用户邮箱地址")
    password_hash = Column(String(255), nullable=False,
                          comment="Bcrypt hashed password / Bcrypt 哈希密码")
    
    # Role Field (Critical Design) | 角色字段（关键设计）
    role = Column(Enum('patient', 'doctor', 'admin', name='user_role'), 
                  nullable=False, default='patient',
                  comment="User role: patient/doctor/admin / 用户角色")
    
    # Common Profile Fields | 通用个人资料字段
    full_name = Column(String(255), nullable=False,
                      comment="Full name / 全名")
    phone = Column(String(20), nullable=True,
                  comment="Contact phone / 联系电话")
    
    # Status Fields | 状态字段
    is_active = Column(Boolean, default=True,
                      comment="Account active status / 账户激活状态")
    is_verified = Column(Boolean, default=False,
                        comment="Email verification status / 邮箱验证状态")
    
    # =============================================================================
    # Patient-Specific Fields (nullable for doctors/admins) | 患者特有字段
    # =============================================================================
    date_of_birth = Column(Date, nullable=True,
                          comment="[Patient] Date of birth / [患者] 出生日期")
    gender = Column(String(10), nullable=True,
                   comment="[Patient] Gender / [患者] 性别")
    address = Column(Text, nullable=True,
                    comment="[Patient] Address (city/environment info) / [患者] 地址（城市/环境信息）")
    emergency_contact = Column(String(255), nullable=True,
                              comment="[Patient] Emergency contact / [患者] 紧急联系人")
    
    # Anonymized profile for sharing (auto-generated) | 匿名化资料（自动生成）
    anonymous_profile = Column(JSONB, nullable=True,
                              comment="Anonymized profile for sharing / 用于分享的匿名化资料")
    # Format: {"age_range": "30-40", "gender": "female", "city_tier": "tier_1", 
    #          "city_environment": "urban", "has_family_history": true}
    
    # =============================================================================
    # Doctor-Specific Fields (nullable for patients/admins) | 医生特有字段
    # =============================================================================
    title = Column(String(50), nullable=True,
                  comment="[Doctor] Professional title / [医生] 职称")
    # e.g., 主任医师, 副主任医师, 主治医师, 住院医师
    
    department = Column(String(100), nullable=True,
                       comment="[Doctor] Department / [医生] 科室")
    
    professional_type = Column(String(100), nullable=True,
                              comment="[Doctor] Professional type/category / [医生] 专业类型")
    # e.g., 内科, 外科, 儿科, 妇产科, etc.
    
    specialty = Column(String(200), nullable=True,
                      comment="[Doctor] Specialty areas/expertise (comma-separated) / [医生] 专业领域")
    
    hospital = Column(String(255), nullable=True,
                     comment="[Doctor] Hospital/Medical institution / [医生] 医疗机构")
    
    license_number = Column(String(100), nullable=True,
                           comment="[Doctor] Medical license number / [医生] 执业证书号")
    
    is_verified_doctor = Column(Boolean, default=False,
                               comment="[Doctor] License verified / [医生] 资质已认证")
    
    # Doctor display info (surname only + hospital + specialty) | 医生展示信息
    display_name = Column(String(255), nullable=True,
                         comment="[Doctor] Display name: Surname + Hospital + Specialty / [医生] 展示名称")
    # e.g., "李医生 | 北京协和医院 | 呼吸内科"
    
    # =============================================================================
    # Admin-Specific Fields (nullable for patients/doctors) | 管理员特有字段
    # =============================================================================
    admin_level = Column(Enum('super', 'regular', name='admin_level'), 
                        nullable=True,
                        comment="[Admin] Admin level / [管理员] 管理员级别")
    
    last_login_at = Column(DateTime(timezone=True), nullable=True,
                          comment="Last login timestamp / 最后登录时间")
    
    # Audit Timestamps | 审计时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(),
                       comment="Record creation time / 记录创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(),
                       comment="Record last update time / 记录最后更新时间")
    
    # Relationships | 关系
    # Patient relationships
    medical_cases = relationship("MedicalCase", back_populates="patient",
                                foreign_keys="MedicalCase.patient_id",
                                cascade="all, delete-orphan")
    
    # Doctor relationships
    doctor_relations = relationship("DoctorPatientRelation",
                                   back_populates="doctor",
                                   foreign_keys="DoctorPatientRelation.doctor_id")
    patient_relations = relationship("DoctorPatientRelation",
                                    back_populates="patient",
                                    foreign_keys="DoctorPatientRelation.patient_id")
    doctor_verifications = relationship("DoctorVerification",
                                       back_populates="doctor",
                                       foreign_keys="DoctorVerification.user_id")
    doctor_comments = relationship("DoctorCaseComment",
                                  back_populates="doctor",
                                  foreign_keys="DoctorCaseComment.doctor_id")
    patient_replies = relationship("CaseCommentReply",
                                  back_populates="patient",
                                  foreign_keys="CaseCommentReply.patient_id")

    # Admin relationships (for logging)
    admin_operations = relationship("AdminOperationLog", back_populates="admin")
    
    # Common relationships
    user_sessions = relationship("UserSession", back_populates="user",
                                 cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user")
    data_sharing_consents = relationship("DataSharingConsent", back_populates="patient",
                                         foreign_keys="DataSharingConsent.patient_id",
                                         cascade="all, delete-orphan")

    # Chronic conditions relationship | 慢性病关联
    chronic_conditions = relationship("PatientChronicCondition",
                                      back_populates="patient",
                                      cascade="all, delete-orphan")
    
    def get_display_info(self):
        """Get display information based on role / 根据角色获取展示信息"""
        if self.role == 'doctor':
            return self.display_name or f"{self.full_name[0]}医生"
        elif self.role == 'admin':
            return f"{self.full_name} (管理员)"
        else:
            return self.full_name
    
    def generate_anonymous_profile(self):
        """Generate anonymized profile for sharing / 生成匿名化分享资料"""
        if self.role != 'patient':
            return None
        
        # Calculate age range
        age_range = None
        if self.date_of_birth:
            from datetime import datetime
            age = datetime.now().year - self.date_of_birth.year
            if age < 18:
                age_range = "<18"
            elif age < 30:
                age_range = "18-30"
            elif age < 40:
                age_range = "30-40"
            elif age < 50:
                age_range = "40-50"
            elif age < 60:
                age_range = "50-60"
            else:
                age_range = "60+"
        
        # Extract city tier from address
        city_tier = "unknown"
        if self.address:
            tier1_cities = ["北京", "上海", "广州", "深圳"]
            tier2_cities = ["杭州", "南京", "成都", "武汉", "西安"]
            if any(city in self.address for city in tier1_cities):
                city_tier = "tier_1"
            elif any(city in self.address for city in tier2_cities):
                city_tier = "tier_2"
            else:
                city_tier = "tier_3_plus"
        
        self.anonymous_profile = {
            "age_range": age_range,
            "gender": self.gender,
            "city_tier": city_tier,
            "city_environment": "urban" if self.address and "市" in self.address else "rural"
        }
        return self.anonymous_profile


# =============================================================================
# Disease Model | 疾病模型
# =============================================================================
class Disease(Base):
    """Disease Model - Enhanced with vector search support / 疾病模型 - 支持向量检索"""
    __tablename__ = "diseases"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), unique=True, nullable=False)
    code = Column(String(50), unique=True)
    description = Column(Text)
    category = Column(String(100), index=True,
                     comment="Disease category for grouping / 疾病分类")
    guidelines_json = Column(JSONB)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    medical_cases = relationship("MedicalCase", back_populates="disease")
    knowledge_chunks = relationship("KnowledgeBaseChunk", back_populates="disease")


# =============================================================================
# ICD-10 Chronic and Special Disease Model | ICD-10特殊病与慢性病模型
# =============================================================================
class ChronicDisease(Base):
    """
    Chronic and Special Disease Model - Based on ICD-10 / 慢性病与特殊病模型

    中国医保规定的特殊病和慢性病列表，基于ICD-10编码。
    用于患者档案管理和AI诊断参考。
    """
    __tablename__ = "chronic_diseases"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # ICD-10 Coding | ICD-10编码
    icd10_code = Column(String(20), unique=True, nullable=False, index=True,
                       comment="ICD-10 disease code / ICD-10疾病编码")
    icd10_name = Column(String(255), nullable=False,
                       comment="ICD-10 official name / ICD-10官方名称")

    # Disease Classification | 疾病分类
    disease_type = Column(Enum('chronic', 'special', 'both', name='disease_type'),
                         nullable=False,
                         comment="Disease type: chronic/special/both / 疾病类型：慢性病/特殊病/两者皆是")

    # Common Names | 常用名称
    common_names = Column(ARRAY(String),
                         comment="Common aliases / 常用别名列表")

    # Category | 分类
    category = Column(String(100), index=True,
                     comment="Disease category / 疾病分类")

    # Status | 状态
    is_active = Column(Boolean, default=True,
                      comment="Whether disease is active in list / 是否在列表中启用")

    # Description | 描述
    description = Column(Text,
                        comment="Disease description / 疾病描述")

    # Medical Notes | 医疗注意事项
    medical_notes = Column(Text,
                          comment="Important medical notes for AI / AI诊断医疗注意事项")

    # Audit Timestamps | 审计时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    patient_conditions = relationship("PatientChronicCondition",
                                     back_populates="chronic_disease",
                                     cascade="all, delete-orphan")


class PatientChronicCondition(Base):
    """
    Patient Chronic Condition Association / 患者慢性病关联表

    关联患者和慢性病，支持多对多关系。
    """
    __tablename__ = "patient_chronic_conditions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign Keys | 外键
    patient_id = Column(UUID(as_uuid=True), ForeignKey("users.id"),
                       nullable=False, index=True)
    disease_id = Column(UUID(as_uuid=True), ForeignKey("chronic_diseases.id"),
                       nullable=False, index=True)

    # Condition Details | 病情详情
    diagnosis_date = Column(Date, nullable=True,
                           comment="Date of diagnosis / 确诊日期")
    severity = Column(Enum('mild', 'moderate', 'severe', name='condition_severity'),
                     nullable=True,
                     comment="Condition severity / 病情严重程度")
    notes = Column(Text,
                  comment="Patient notes about condition / 患者备注")

    # Status | 状态
    is_active = Column(Boolean, default=True,
                      comment="Whether condition is currently active / 当前是否活跃")

    # Audit Timestamps | 审计时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    patient = relationship("User", back_populates="chronic_conditions")
    chronic_disease = relationship("ChronicDisease", back_populates="patient_conditions")

    # Unique constraint - one disease per patient
    __table_args__ = (
        UniqueConstraint('patient_id', 'disease_id',
                        name='unique_patient_disease'),
    )


# =============================================================================
# Medical Case Model | 医疗病例模型
# =============================================================================
class MedicalCase(Base):
    """
    Medical Case Model - Enhanced with sharing support / 医疗病例模型 - 支持分享
    """
    __tablename__ = "medical_cases"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign Keys
    patient_id = Column(UUID(as_uuid=True), ForeignKey("users.id"),
                       nullable=False, index=True)
    disease_id = Column(UUID(as_uuid=True), ForeignKey("diseases.id"),
                       nullable=True, index=True)
    
    # Case Information
    title = Column(String(255), nullable=False)
    description = Column(Text)
    symptoms = Column(Text)
    clinical_findings = Column(JSONB)
    diagnosis = Column(Text)
    
    # Classification
    severity = Column(String(20))
    status = Column(String(20), default='active')
    
    # Sharing Control | 分享控制
    is_shared = Column(Boolean, default=False,
                      comment="Whether case is shared / 是否已分享")
    share_scope = Column(Enum('private', 'to_doctor', 'platform_anonymous', 
                             name='share_scope'), default='private',
                        comment="Sharing scope / 分享范围")
    
    # Audit Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    patient = relationship("User", back_populates="medical_cases",
                          foreign_keys=[patient_id])
    disease = relationship("Disease", back_populates="medical_cases")
    medical_documents = relationship("MedicalDocument", back_populates="medical_case",
                                    cascade="all, delete-orphan")
    ai_feedbacks = relationship("AIFeedback", back_populates="medical_case")
    follow_ups = relationship("FollowUp", back_populates="medical_case")
    shared_version = relationship("SharedMedicalCase", back_populates="original_case",
                                 uselist=False)


# =============================================================================
# Medical Document Model with PII Cleaning | 带PII清理的医疗文档模型
# =============================================================================
class MedicalDocument(Base):
    """
    Medical Document Model - With PII cleaning / 医疗文档模型 - 带PII清理
    """
    __tablename__ = "medical_documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    medical_case_id = Column(UUID(as_uuid=True), ForeignKey("medical_cases.id"),
                            nullable=False, index=True)
    
    # File Information
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)
    file_size = Column(Integer)
    file_path = Column(String(500))
    
    # Processing Status
    upload_status = Column(String(20), default='uploaded')
    
    # Original Extracted Content (for patient view) | 原始提取内容（患者查看）
    extracted_content = Column(JSONB,
                              comment="Raw MinerU extracted content / MinerU原始提取内容")
    
    # PII-Cleaned Content (for sharing) | PII清理后内容（用于分享）
    cleaned_content = Column(JSONB,
                            comment="PII-cleaned content for sharing / PII清理后用于分享的内容")
    
    # PII Cleaning Metadata | PII清理元数据
    pii_cleaning_status = Column(Enum('pending', 'completed', 'failed', 
                                     name='pii_status'), default='pending',
                                comment="PII cleaning status / PII清理状态")
    pii_detected = Column(JSONB, default=list,
                         comment="List of detected PII / 检测到的PII列表")
    cleaning_confidence = Column(Float,
                                comment="PII cleaning confidence score / PII清理置信度")
    
    # Extraction Metadata
    extraction_metadata = Column(JSONB)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    medical_case = relationship("MedicalCase", back_populates="medical_documents")


# =============================================================================
# AI Feedback Model | AI 反馈模型
# =============================================================================
class AIFeedback(Base):
    """AI Feedback Model - Enhanced with knowledge source tracking / AI反馈模型"""
    __tablename__ = "ai_feedbacks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    medical_case_id = Column(UUID(as_uuid=True), ForeignKey("medical_cases.id"),
                            nullable=False, index=True)
    
    feedback_type = Column(String(50), nullable=False)
    input_data = Column(JSONB, nullable=False)
    ai_response = Column(JSONB, nullable=False)
    
    # Knowledge Base Sources | 知识库来源
    knowledge_sources = Column(JSONB, default=list,
                              comment="Knowledge base chunks used / 使用的知识库块")
    
    confidence_score = Column(DECIMAL(3, 2))
    recommendations = Column(Text)
    follow_up_plan = Column(JSONB)
    
    # Review Status
    is_reviewed = Column(Boolean, default=False)
    reviewed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    review_notes = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    medical_case = relationship("MedicalCase", back_populates="ai_feedbacks")
    reviewer = relationship("User", foreign_keys=[reviewed_by])


# =============================================================================
# Follow-Up Model | 随访模型
# =============================================================================
class FollowUp(Base):
    """Follow-Up Model / 随访模型"""
    __tablename__ = "follow_ups"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    medical_case_id = Column(UUID(as_uuid=True), ForeignKey("medical_cases.id"),
                            nullable=False, index=True)
    
    scheduled_date = Column(String(10), nullable=False)
    actual_date = Column(String(10))
    follow_up_type = Column(String(50), nullable=False)
    status = Column(String(20), default='scheduled')
    
    notes = Column(Text)
    symptoms_changes = Column(Text)
    medication_adherence = Column(String(20))
    next_follow_up_date = Column(String(10))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())
    
    medical_case = relationship("MedicalCase", back_populates="follow_ups")


# =============================================================================
# User Session Model | 用户会话模型
# =============================================================================
class UserSession(Base):
    """User Session Model - Enhanced with role tracking / 用户会话模型"""
    __tablename__ = "user_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"),
                    nullable=False, index=True)
    
    token_id = Column(String(255), nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_active = Column(Boolean, default=True)
    
    # Session metadata
    login_role = Column(String(20),
                       comment="Role at login (for role switching) / 登录时的角色")
    ip_address = Column(INET)
    user_agent = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="user_sessions")


# =============================================================================
# Audit Log Model | 审计日志模型
# =============================================================================
class AuditLog(Base):
    """Audit Log Model / 审计日志模型"""
    __tablename__ = "audit_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    
    action = Column(String(100), nullable=False)
    resource_type = Column(String(50))
    resource_id = Column(UUID(as_uuid=True))
    details = Column(JSONB)
    
    ip_address = Column(INET)
    user_agent = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    user = relationship("User", back_populates="audit_logs")


# =============================================================================
# Data Sharing Consent Model | 数据共享同意书模型
# =============================================================================
class DataSharingConsent(Base):
    """
    Data Sharing Consent Model - Legal compliance / 数据共享同意书模型 - 法律合规
    """
    __tablename__ = "data_sharing_consents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("users.id"),
                       nullable=False, index=True)
    
    # Share Type | 分享类型
    share_type = Column(Enum('to_specific_doctor', 'platform_anonymous', 
                            'research_project', name='share_type'),
                       nullable=False,
                       comment="Type of sharing / 分享类型")
    
    # Share Scope | 分享范围
    target_doctor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"),
                             nullable=True,
                             comment="Target doctor if specific / 指定医生")
    disease_category = Column(String(100), nullable=True,
                             comment="Limit to disease category / 限制疾病分类")
    
    # Consent Content | 同意内容
    consent_version = Column(String(20), nullable=False,
                            comment="Consent form version / 同意书版本")
    consent_text = Column(Text, nullable=False,
                         comment="Full consent text / 完整同意书文本")
    
    # Signature Info | 签署信息
    ip_address = Column(String(45),
                       comment="IP address when signing / 签署时IP地址")
    user_agent = Column(Text,
                       comment="User agent when signing / 签署时浏览器信息")
    signed_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Validity Period | 有效期
    valid_from = Column(DateTime(timezone=True), server_default=func.now())
    valid_until = Column(DateTime(timezone=True), nullable=True,
                        comment="Expiration date (null = permanent) / 过期日期")
    is_active = Column(Boolean, default=True)
    revoked_at = Column(DateTime(timezone=True), nullable=True,
                       comment="When consent was revoked / 撤回时间")
    
    # Relationships
    patient = relationship("User", back_populates="data_sharing_consents",
                          foreign_keys=[patient_id])
    target_doctor = relationship("User", foreign_keys=[target_doctor_id])


# =============================================================================
# Shared Medical Case Model (Anonymized) | 匿名化分享病例模型
# =============================================================================
class SharedMedicalCase(Base):
    """
    Shared Medical Case Model - Anonymized for doctor view / 匿名化分享病例模型
    """
    __tablename__ = "shared_medical_cases"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    original_case_id = Column(UUID(as_uuid=True), ForeignKey("medical_cases.id"),
                             nullable=False, unique=True, index=True)
    consent_id = Column(UUID(as_uuid=True), ForeignKey("data_sharing_consents.id"),
                       nullable=False)
    
    # Anonymized Patient Profile | 匿名化患者资料
    anonymous_patient_profile = Column(JSONB, nullable=False,
                                      comment="Anonymized profile / 匿名化资料")
    
    # Anonymized Case Content | 匿名化病例内容
    anonymized_symptoms = Column(Text)
    anonymized_diagnosis = Column(Text)
    anonymized_documents = Column(JSONB, default=list)
    
    # Visibility Control | 可见性控制
    visible_to_doctors = Column(Boolean, default=True)
    visible_for_research = Column(Boolean, default=False)
    
    # Access Statistics | 访问统计
    view_count = Column(Integer, default=0)
    doctor_views = Column(JSONB, default=list)
    # Format: [{"doctor_id": "...", "viewed_at": "2026-01-01T10:00:00", "ip": "..."}]
    
    # Research Export Control | 科研导出控制
    exported_count = Column(Integer, default=0)
    export_records = Column(JSONB, default=list)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    original_case = relationship("MedicalCase", back_populates="shared_version")
    consent = relationship("DataSharingConsent")


# =============================================================================
# Doctor-Patient Relation Model | 医生-患者关系模型
# =============================================================================
class DoctorPatientRelation(Base):
    """
    Doctor-Patient Relation Model - Patient initiates @doctor / 医生-患者关系模型
    """
    __tablename__ = "doctor_patient_relations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("users.id"),
                       nullable=False, index=True)
    doctor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"),
                      nullable=False, index=True)
    
    # Relationship Status | 关系状态
    status = Column(Enum('pending', 'active', 'terminated', name='relation_status'),
                   default='pending',
                   comment="Relationship status / 关系状态")
    
    # Initiation Method | 发起方式
    initiated_by = Column(Enum('patient_at', 'doctor_request', 'platform_match',
                              name='initiation_type'),
                         nullable=False,
                         comment="How relationship started / 关系发起方式")
    
    # Share Scope | 分享范围
    share_all_cases = Column(Boolean, default=False,
                            comment="Share all cases / 分享所有病例")
    shared_case_ids = Column(JSONB, default=list,
                            comment="Specific shared case IDs / 指定分享的病例ID")
    
    # Messages | 消息
    patient_message = Column(Text,
                            comment="Message from patient / 患者留言")
    doctor_response = Column(Text,
                            comment="Doctor response / 医生回复")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    activated_at = Column(DateTime(timezone=True), nullable=True)
    terminated_at = Column(DateTime(timezone=True), nullable=True)
    
    # Unique constraint: one relation per patient-doctor pair
    __table_args__ = (
        UniqueConstraint('patient_id', 'doctor_id', name='uq_patient_doctor'),
    )
    
    # Relationships
    patient = relationship("User", back_populates="patient_relations",
                          foreign_keys=[patient_id])
    doctor = relationship("User", back_populates="doctor_relations",
                         foreign_keys=[doctor_id])


# =============================================================================
# Doctor Case Comment Model | 医生病例评论模型
# =============================================================================
class DoctorCaseComment(Base):
    """
    Doctor Case Comment Model - Professional advice on shared cases / 医生病例评论模型
    
    Allows verified doctors to add professional comments and suggestions 
    on anonymized shared medical cases.
    """
    __tablename__ = "doctor_case_comments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign Keys
    shared_case_id = Column(UUID(as_uuid=True), ForeignKey("shared_medical_cases.id"),
                           nullable=False, index=True)
    doctor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"),
                      nullable=False, index=True)
    
    # Comment Content | 评论内容
    comment_type = Column(Enum('suggestion', 'diagnosis_opinion', 'treatment_advice', 
                              'general', name='comment_type'),
                         default='general',
                         comment="Type of comment / 评论类型")
    
    content = Column(Text, nullable=False,
                    comment="Comment content / 评论内容")
    
    # Professional Info | 专业信息
    doctor_specialty = Column(String(200),
                             comment="Doctor's specialty at time of comment / 评论时医生专业")
    doctor_hospital = Column(String(255),
                            comment="Doctor's hospital at time of comment / 评论时医院")
    
    # Visibility | 可见性
    is_public = Column(Boolean, default=True,
                      comment="Visible to other doctors / 对其他医生可见")
    
    # Status | 状态
    status = Column(Enum('active', 'edited', 'hidden', name='comment_status'),
                   default='active',
                   comment="Comment status / 评论状态")
    
    # Edit History | 编辑历史
    edited_at = Column(DateTime(timezone=True), nullable=True)
    original_content = Column(Text, nullable=True,
                             comment="Original content before edit / 编辑前的原始内容")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    shared_case = relationship("SharedMedicalCase")
    doctor = relationship("User", back_populates="doctor_comments", foreign_keys=[doctor_id])
    patient_replies = relationship("CaseCommentReply", back_populates="doctor_comment",
                                   cascade="all, delete-orphan")


# =============================================================================
# Case Comment Reply Model | 病例评论回复模型 (Patient replies to doctor comments)
# =============================================================================
class CaseCommentReply(Base):
    """
    Case Comment Reply Model - Patient replies to doctor comments
    Allows patients to respond to specific doctor comments on their cases.
    Doctors can see replies to their own comments, but not to other doctors' comments.
    """
    __tablename__ = "case_comment_replies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign Keys
    doctor_comment_id = Column(UUID(as_uuid=True), ForeignKey("doctor_case_comments.id"),
                              nullable=False, index=True)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("users.id"),
                       nullable=False, index=True)
    shared_case_id = Column(UUID(as_uuid=True), ForeignKey("shared_medical_cases.id"),
                           nullable=False, index=True)

    # Reply Content
    content = Column(Text, nullable=False,
                    comment="Patient reply content / 患者回复内容")

    # Status
    status = Column(Enum('active', 'hidden', name='reply_status'),
                   default='active',
                   comment="Reply status / 回复状态")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    doctor_comment = relationship("DoctorCaseComment", back_populates="patient_replies")
    patient = relationship("User", foreign_keys=[patient_id])
    shared_case = relationship("SharedMedicalCase")


# =============================================================================
# Case-Knowledge Match Model | 病例-知识匹配模型
# =============================================================================
# Vector Embedding Config Model | 向量嵌入配置模型
# =============================================================================
class VectorEmbeddingConfig(Base):
    """
    Vector Embedding Config Model - Admin managed / 向量嵌入配置模型 - 管理员管理
    """
    __tablename__ = "vector_embedding_configs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Basic Info | 基本信息
    name = Column(String(100), nullable=False,
                 comment="Configuration name / 配置名称")
    provider = Column(String(50), nullable=False,
                     comment="Provider: openai, local, etc. / 提供商")
    model_id = Column(String(100), nullable=False,
                     comment="Model ID / 模型ID")
    
    # API Configuration | API配置
    api_url = Column(String(500), nullable=False)
    api_key = Column(String(500), nullable=False)  # Should be encrypted in production
    
    # Parameters | 参数
    vector_dimension = Column(Integer, default=1536,
                             comment="Embedding dimension / 嵌入维度")
    max_input_length = Column(Integer, default=8192,
                             comment="Max input length / 最大输入长度")
    
    # Status | 状态
    is_active = Column(Boolean, default=False,
                      comment="Is active config / 是否为活跃配置")
    is_default = Column(Boolean, default=False,
                       comment="Is default config / 是否为默认配置")
    
    # Test Status | 测试状态
    last_tested_at = Column(DateTime(timezone=True), nullable=True)
    test_status = Column(Enum('untested', 'success', 'failed', name='test_status'),
                        default='untested',
                        comment="Connection test status / 连接测试状态")
    test_error_message = Column(Text, nullable=True,
                               comment="Error message if test failed / 测试失败错误信息")
    
    # Audit
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"),
                       nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())


# =============================================================================
# Knowledge Base Chunk Model (Vectorized) | 知识库分块模型（向量化）
# =============================================================================
class KnowledgeBaseChunk(Base):
    """
    Knowledge Base Chunk Model - Vectorized for RAG / 知识库分块模型 - 向量化
    """
    __tablename__ = "knowledge_base_chunks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Source Info | 来源信息
    source_document_id = Column(UUID(as_uuid=True), nullable=True)
    source_type = Column(Enum('disease_guideline', 'medical_document',
                             'research_paper', 'unified_kb', name='source_type'),
                         nullable=False)
    
    # Document Metadata | 文档元数据
    disease_id = Column(UUID(as_uuid=True), ForeignKey("diseases.id"),
                       nullable=True, index=True)
    disease_category = Column(String(100), index=True,
                             comment="Disease category / 疾病分类")
    document_title = Column(String(255))
    section_title = Column(String(255),
                          comment="Section title / 章节标题")
    
    # Chunk Content | 分块内容
    chunk_index = Column(Integer, nullable=False,
                        comment="Chunk sequence number / 分块序号")
    chunk_text = Column(Text, nullable=False,
                       comment="Original text content / 原始文本内容")
    chunk_text_hash = Column(String(64), unique=True,
                            comment="Text hash for deduplication / 文本哈希用于去重")
    
    # Vector Embedding (stored as JSONB for flexibility, can use pgvector) | 向量嵌入
    embedding = Column(JSONB, nullable=True,
                      comment="Vector embedding / 向量嵌入")
    embedding_model_id = Column(String(100),
                               comment="Model used for embedding / 用于嵌入的模型")
    
    # Retrieval Statistics | 检索统计
    retrieval_count = Column(Integer, default=0,
                            comment="Number of times retrieved / 被检索次数")
    avg_relevance_score = Column(Float, nullable=True,
                                comment="Average relevance score / 平均相关度分数")
    
    # Status
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    disease = relationship("Disease", back_populates="knowledge_chunks")
    
    # Indexes | 索引
    __table_args__ = (
        Index('idx_kb_chunks_category_disease', 'disease_category', 'disease_id'),
        Index('idx_kb_chunks_active', 'is_active'),
    )


# =============================================================================
# Case-Knowledge Match Model | 病例-知识匹配模型
# =============================================================================
class CaseKnowledgeMatch(Base):
    """
    Case-Knowledge Match Model - Smart RAG selection record / 病例-知识匹配记录
    """
    __tablename__ = "case_knowledge_matches"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    medical_case_id = Column(UUID(as_uuid=True), ForeignKey("medical_cases.id"),
                            nullable=False, index=True)
    
    # Query Info | 查询信息
    query_text = Column(Text, nullable=False,
                       comment="Case summary as query / 病例摘要作为查询")
    query_embedding = Column(JSONB, nullable=True)
    
    # Matched Results | 匹配结果
    matched_chunks = Column(JSONB, nullable=False,
                           comment="Top-K matched chunks / Top-K匹配的知识块")
    # Format: [{"chunk_id": "...", "relevance_score": 0.95, "chunk_text": "..."}]
    
    # Used Knowledge Sources | 使用的知识源
    knowledge_sources = Column(JSONB, default=list,
                              comment="Disease categories used / 使用的疾病分类")
    
    # AI Selection Reasoning | AI选择说明
    selection_reasoning = Column(Text,
                                comment="Why these knowledge bases were selected / 选择理由")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# =============================================================================
# System Resource Log Model | 系统资源日志模型
# =============================================================================
class SystemResourceLog(Base):
    """
    System Resource Log Model - Monitoring / 系统资源日志模型 - 监控
    """
    __tablename__ = "system_resource_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Resource Metrics | 资源指标
    cpu_percent = Column(Float,
                        comment="CPU usage percentage / CPU使用率")
    memory_percent = Column(Float,
                           comment="Memory usage percentage / 内存使用率")
    disk_percent = Column(Float,
                         comment="Disk usage percentage / 磁盘使用率")
    
    # Container Status | 容器状态
    container_status = Column(JSONB, default=dict,
                             comment="Docker container status / Docker容器状态")
    # Format: {"medicare_backend": {"status": "running", "cpu": 10.5, "memory": 256}}
    
    # Database Metrics | 数据库指标
    db_connections = Column(Integer,
                           comment="Active DB connections / 活跃数据库连接数")
    db_query_time_avg = Column(Float,
                              comment="Average query time / 平均查询时间")
    
    # Alert Level | 警告级别
    alert_level = Column(Enum('info', 'warning', 'critical', name='alert_level'),
                        default='info',
                        comment="Alert level / 警告级别")
    alert_message = Column(Text, nullable=True,
                          comment="Alert message / 警告信息")


# =============================================================================
# AI Diagnosis Log Model | AI诊断日志模型
# =============================================================================
class AIDiagnosisLog(Base):
    """
    AI Diagnosis Log Model - For early warning / AI诊断日志模型 - 用于预警
    """
    __tablename__ = "ai_diagnosis_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Request Info | 请求信息
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    request_type = Column(Enum('diagnosis', 'comprehensive_diagnosis', 'document_extraction', 'vector_search',
                              name='request_type'),
                         nullable=False)
    
    # AI Model Info | AI模型信息
    ai_model_id = Column(String(100))
    ai_api_url = Column(String(500))
    
    # Performance Metrics | 性能指标
    request_duration_ms = Column(Integer,
                                comment="Request duration in ms / 请求耗时毫秒")
    tokens_input = Column(Integer)
    tokens_output = Column(Integer)
    
    # Result Status | 结果状态
    status = Column(Enum('success', 'timeout', 'error', 'rate_limited',
                        name='ai_status'),
                   nullable=False)
    error_message = Column(Text, nullable=True)
    
    # Anomaly Detection | 异常检测
    is_anomaly = Column(Boolean, default=False,
                       comment="Is anomalous (timeout/high error rate) / 是否异常")
    anomaly_reason = Column(Text, nullable=True,
                           comment="Anomaly reason / 异常原因")


# =============================================================================
# Admin Operation Log Model | 管理员操作日志模型
# =============================================================================
class AdminOperationLog(Base):
    """
    Admin Operation Log Model / 管理员操作日志模型
    """
    __tablename__ = "admin_operation_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    admin_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    operation_type = Column(Enum(
        'system_config_update',
        'system_config_update_failed',
        'ai_model_change',
        'configure_ai_model',
        'configure_ai_model_failed',
        'configure_oss',
        'vector_model_test',
        'knowledge_base_update',
        'upload_knowledge_document',
        'upload_knowledge_document_failed',
        'delete_knowledge_document',
        'delete_knowledge_document_failed',
        'sync_doctor_verification',
        'doctor_verification',
        'approve_doctor',
        'reject_doctor',
        'approve_doctor_failed',
        'reject_doctor_failed',
        'change_password',
        'data_export',
        'user_management',
        'manual_metrics_log',
        'update_verification_pending',
        'update_verification_approved',
        'update_verification_rejected',
        'update_verification_failed',
        name='admin_operation_type'
    ), nullable=False)
    
    operation_details = Column(JSONB, default=dict,
                              comment="Operation details / 操作详情")
    ip_address = Column(INET)
    user_agent = Column(Text)
    
    # Relationships
    admin = relationship("User", back_populates="admin_operations")


# =============================================================================
# Doctor Verification Model | 医生认证模型
# =============================================================================
class DoctorVerification(Base):
    """
    Doctor Verification Model / 医生认证模型

    Manages doctor verification workflow including license validation
    and approval process.
    管理医生认证工作流，包括执照验证和审批流程。
    """
    __tablename__ = "doctor_verifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"),
                     nullable=False, index=True)

    # License Information / 执照信息
    license_number = Column(String(100), nullable=False)
    specialty = Column(String(255))
    hospital = Column(String(255))
    years_of_experience = Column(Integer, default=0)
    education = Column(Text)

    # Verification Status / 认证状态
    status = Column(Enum('pending', 'approved', 'rejected', name='verification_status'),
                    default='pending', nullable=False)
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    verified_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    verification_notes = Column(Text)

    # Relationships
    doctor = relationship("User", foreign_keys=[user_id],
                         back_populates="doctor_verifications")
    verifier = relationship("User", foreign_keys=[verified_by])


# =============================================================================
# Legacy Patient Model (Deprecated) | 遗留患者模型（已弃用）
# =============================================================================
class Patient(Base):
    """
    [DEPRECATED] Legacy Patient Model / [已弃用] 遗留患者模型
    
    This model is kept for backward compatibility during migration.
    New code should use User model with role='patient'.
    
    此模型保留用于迁移期间的向后兼容。
    新代码应使用 role='patient' 的 User 模型。
    """
    __tablename__ = "patients"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), 
                     nullable=False, index=True)
    name = Column(String(255), nullable=True)
    date_of_birth = Column(Date, nullable=True)
    gender = Column(String(10))
    phone = Column(String(20))
    address = Column(Text)
    emergency_contact = Column(String(255))
    medical_record_number = Column(String(100), unique=True)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Mark as deprecated in migration script
    __table_args__ = (
        {'comment': 'DEPRECATED: Use users table with role=patient'},
    )


# Export all models
__all__ = [
    'User',
    'Disease',
    'MedicalCase',
    'MedicalDocument',
    'AIFeedback',
    'FollowUp',
    'UserSession',
    'AuditLog',
    'DataSharingConsent',
    'SharedMedicalCase',
    'DoctorPatientRelation',
    'VectorEmbeddingConfig',
    'KnowledgeBaseChunk',
    'CaseKnowledgeMatch',
    'SystemResourceLog',
    'AIDiagnosisLog',
    'AdminOperationLog',
    'DoctorVerification',
    'DoctorCaseComment',  # 医生病例评论
    'Patient',  # Deprecated
]
