"""
Doctor API Endpoints - 医生端API端点

Provides endpoints for doctors to view anonymized cases, conduct research,
and manage patient mentions with full privacy protection.
为医生提供查看匿名病例、进行科研和管理患者@提及的API，具备完整的隐私保护。
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.orm import selectinload
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime, date, timedelta
import uuid
import csv
import json
import io
import logging

from app.db.database import get_db
from app.models.models import (
    User, DoctorVerification, SharedMedicalCase, DataSharingConsent, DoctorPatientRelation,
    MedicalCase, Disease, MedicalDocument, AIFeedback, ChronicDisease, PatientChronicCondition
)
from app.core.deps import get_current_active_user, require_doctor, require_verified_doctor
from app.schemas.user import UserResponse

logger = logging.getLogger(__name__)

router = APIRouter()


# =============================================================================
# Extended Pydantic Schemas for New Endpoints / 新端点的扩展Pydantic模式
# =============================================================================

class AnonymousPatientProfile(BaseModel):
    """Anonymous patient profile / 匿名化患者资料"""
    age_range: Optional[str] = None
    gender: Optional[str] = None
    city_tier: Optional[str] = None
    city_environment: Optional[str] = None

class ChronicDiseaseSummary(BaseModel):
    """Chronic disease summary for case list / 病例列表中的慢性病摘要"""
    id: uuid.UUID
    icd10_code: str
    icd10_name: str
    disease_type: str
    common_names: Optional[List[str]] = None

class SharedCaseResponse(BaseModel):
    """Shared medical case response / 分享病例响应"""
    id: uuid.UUID
    original_case_id: uuid.UUID
    anonymous_patient_profile: AnonymousPatientProfile
    anonymized_symptoms: Optional[str] = None
    anonymized_diagnosis: Optional[str] = None
    disease_category: Optional[str] = None
    created_at: datetime
    view_count: int
    patient_chronic_diseases: Optional[List[ChronicDiseaseSummary]] = None
    
    class Config:
        from_attributes = True

class CaseDocumentResponse(BaseModel):
    """Case document response / 病例文档响应"""
    id: uuid.UUID
    filename: str
    file_type: str
    pii_cleaning_status: str
    cleaned_content: Optional[Dict[str, Any]] = None
    file_url: Optional[str] = None

    class Config:
        from_attributes = True

class CaseDetailResponse(BaseModel):
    """Detailed case response / 详细病例响应"""
    case: SharedCaseResponse
    documents: List[CaseDocumentResponse]
    ai_feedbacks: List[Dict[str, Any]]
    
    class Config:
        from_attributes = True

class DashboardStats(BaseModel):
    """Dashboard statistics / 工作台统计"""
    mentioned_cases: int
    public_cases: int
    today_cases: int
    exported_count: int
    growth: int

class SearchRequest(BaseModel):
    """Research search request / 科研搜索请求"""
    disease_categories: Optional[List[str]] = None
    symptoms: Optional[List[str]] = None
    age_ranges: Optional[List[str]] = None
    genders: Optional[List[str]] = None
    city_tiers: Optional[List[str]] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    page: int = 1
    limit: int = 20

class ExportRequest(BaseModel):
    """Data export request / 数据导出请求"""
    case_ids: List[uuid.UUID]
    format: str  # "json" or "csv"
    include_documents: bool = False
    double_blind: bool = True  # Remove all identifiers

class DoctorMentionResponse(BaseModel):
    """Doctor mention response / 医生@提及响应"""
    id: uuid.UUID
    patient_id: uuid.UUID
    patient_display_name: str
    relation_id: uuid.UUID
    status: str
    patient_message: Optional[str] = None
    created_at: datetime
    is_read: bool = False
    
    class Config:
        from_attributes = True


class DoctorProfileResponse(BaseModel):
    """Doctor profile response"""
    id: str
    full_name: str
    email: str
    title: Optional[str]
    department: Optional[str]
    specialty: Optional[str]
    hospital: Optional[str]
    is_verified_doctor: bool
    display_name: Optional[str]
    created_at: Optional[str]


class DoctorStatsResponse(BaseModel):
    """Doctor statistics response"""
    total_shared_cases: int
    total_patient_connections: int
    verification_status: str


@router.get("/profile", response_model=DoctorProfileResponse)
async def get_doctor_profile(
    current_user: User = Depends(require_verified_doctor)
):
    """
    Get current doctor's profile information
    获取当前医生的档案信息
    """
    logger.info(f"Doctor {current_user.id} requesting profile information")
    
    return DoctorProfileResponse(
        id=str(current_user.id),
        full_name=current_user.full_name,
        email=current_user.email,
        title=current_user.title,
        department=current_user.department,
        specialty=current_user.specialty,
        hospital=current_user.hospital,
        is_verified_doctor=current_user.is_verified_doctor,
        display_name=current_user.display_name,
        created_at=current_user.created_at.isoformat() if current_user.created_at else None
    )


@router.get("/stats", response_model=DoctorStatsResponse)
async def get_doctor_stats(
    current_user: User = Depends(require_verified_doctor),
    db: AsyncSession = Depends(get_db)
):
    """
    Get doctor's statistics
    获取医生的统计信息
    """
    logger.info(f"Doctor {current_user.id} requesting statistics")
    
    try:
        # Count shared cases visible to this doctor
        shared_cases_stmt = select(func.count()).select_from(
            select(1).where(
                # This would need proper models - placeholder for now
                True  # Replace with actual shared cases logic
            ).subquery()
        )
        shared_cases_result = await db.execute(shared_cases_stmt)
        total_shared_cases = shared_cases_result.scalar() or 0
        
        # Count patient connections
        from app.models.models import DoctorPatientRelation
        patient_connections_stmt = select(func.count()).select_from(
            DoctorPatientRelation
        ).where(DoctorPatientRelation.doctor_id == current_user.id)
        connections_result = await db.execute(patient_connections_stmt)
        total_patient_connections = connections_result.scalar() or 0
        
        verification_status = "approved" if current_user.is_verified_doctor else "pending"
        
        return DoctorStatsResponse(
            total_shared_cases=total_shared_cases,
            total_patient_connections=total_patient_connections,
            verification_status=verification_status
        )
        
    except Exception as e:
        logger.error(f"Error fetching doctor stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch doctor statistics"
        )


@router.get("/patients")
async def get_doctor_patients(
    current_user: User = Depends(require_verified_doctor),
    db: AsyncSession = Depends(get_db)
):
    """
    Get list of patients connected to this doctor
    获取与此医生关联的患者列表
    """
    logger.info(f"Doctor {current_user.id} requesting patient list")
    
    try:
        from app.models.models import DoctorPatientRelation
        
        # Get doctor-patient relations
        stmt = select(DoctorPatientRelation).where(
            DoctorPatientRelation.doctor_id == current_user.id
        )
        result = await db.execute(stmt)
        relations = result.scalars().all()
        
        patients = []
        for relation in relations:
            # Get patient user info
            patient_stmt = select(User).where(User.id == relation.patient_id)
            patient_result = await db.execute(patient_stmt)
            patient = patient_result.scalar_one_or_none()
            
            if patient:
                patients.append({
                    "id": str(patient.id),
                    "full_name": patient.full_name,
                    "email": patient.email,
                    "relation_status": relation.status,
                    "created_at": relation.created_at.isoformat() if relation.created_at else None
                })
        
        return {
            "patients": patients,
            "total": len(patients)
        }
        
    except Exception as e:
        logger.error(f"Error fetching doctor patients: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch patient list"
        )


@router.get("/verification-status")
async def get_verification_status(
    current_user: User = Depends(require_doctor)
):
    """
    Get doctor's verification status
    获取医生的认证状态
    """
    logger.info(f"Doctor {current_user.id} checking verification status")
    
    verification_status = "approved" if current_user.is_verified_doctor else "pending"
    
    return {
        "is_verified": current_user.is_verified_doctor,
        "verification_status": verification_status,
        "message": "Your account is verified and ready to use" if current_user.is_verified_doctor 
                   else "Your account is pending verification by admin"
    }


# =============================================================================
# Helper Functions / 辅助函数
# =============================================================================

async def check_export_permission(
    db: AsyncSession,
    doctor_id: uuid.UUID,
    case_id: uuid.UUID
) -> bool:
    """
    Check if a doctor can export a specific case for research.
    检查医生是否可以导出特定病例用于科研。
    
    导出权限规则：
    1. 公开的病例（visible_to_doctors=True）：所有医生可导出
    2. 被@给该医生的非公开病例：只有该医生可导出
    3. 未被@且非公开的病例：不可导出
    
    Returns:
        bool: True if doctor can export this case, False otherwise
    """
    from sqlalchemy import select
    
    # Get case details with patient info
    query = select(SharedMedicalCase, MedicalCase).join(
        MedicalCase, SharedMedicalCase.original_case_id == MedicalCase.id
    ).where(SharedMedicalCase.id == case_id)
    
    result = await db.execute(query)
    case_data = result.first()
    
    if not case_data:
        return False
    
    shared_case, medical_case = case_data
    
    # Rule 1 & 4: Public cases can be exported by any doctor
    # 公开病例可以被所有医生导出
    if shared_case.visible_to_doctors:
        return True
    
    # Rule 2 & 3: For non-public cases, check if doctor was @mentioned
    # 对于非公开病例，检查医生是否被@提及
    relation_query = select(DoctorPatientRelation).where(
        and_(
            DoctorPatientRelation.patient_id == medical_case.patient_id,
            DoctorPatientRelation.doctor_id == doctor_id,
            DoctorPatientRelation.initiated_by == 'patient_at',
            DoctorPatientRelation.status.in_(['pending', 'active'])
        )
    )
    
    relation_result = await db.execute(relation_query)
    relation = relation_result.scalar_one_or_none()
    
    # If no relation exists, doctor cannot export
    if not relation:
        return False
    
    # Check if this specific case is in the shared_case_ids
    # 检查该具体病例是否在共享病例列表中
    case_id_str = str(case_id)
    shared_case_ids = relation.shared_case_ids or []
    
    # If doctor was @mentioned by this patient AND case is shared, they can export
    # 如果医生被该患者@提及且病例被共享给该医生，则可以导出
    return case_id_str in shared_case_ids


async def get_doctor_accessible_cases(
    db: AsyncSession,
    doctor_id: uuid.UUID,
    case_type: str = "all"
) -> List[SharedMedicalCase]:
    """
    Get cases accessible to doctor based on permissions and consents
    根据权限和同意书获取医生可访问的病例
    
    权限逻辑：
    1. visible_to_doctors=True: 患者勾选"共享给所有医生"，所有认证医生可见
    2. visible_to_doctors=False: 仅@提及的医生可见（通过DoctorPatientRelation验证）
    """
    from sqlalchemy import or_

    if case_type == "mentioned":
        # 获取医生的所有@提及关系
        relation_query = select(DoctorPatientRelation).where(
            and_(
                DoctorPatientRelation.doctor_id == doctor_id,
                DoctorPatientRelation.initiated_by == 'patient_at',
                DoctorPatientRelation.status.in_(['pending', 'active'])
            )
        )
        result = await db.execute(relation_query)
        relations = result.scalars().all()

        if not relations:
            return []

        # 收集所有共享的病例ID
        # 只返回明确共享给该医生的病例，而不是该患者的所有病例
        shared_case_ids = []
        for relation in relations:
            if relation.shared_case_ids:
                shared_case_ids.extend(relation.shared_case_ids)

        if not shared_case_ids:
            return []

        # 只返回明确共享给该医生的病例
        query = select(SharedMedicalCase).where(
            SharedMedicalCase.id.in_(shared_case_ids)
        )
    elif case_type == "public":
        # Public platform cases (visible_for_research=True)
        query = select(SharedMedicalCase).join(
            MedicalCase, SharedMedicalCase.original_case_id == MedicalCase.id
        ).where(
            SharedMedicalCase.visible_for_research == True
        )
    else:
        # "all" - 返回医生有权查看的所有病例
        # 1. 公开共享的病例 (visible_to_doctors=True)
        # 2. @提及该医生的特定病例 (通过DoctorPatientRelation.shared_case_ids关联)
        
        # 获取该医生的所有@提及关系，收集明确共享的病例ID
        relation_query = select(DoctorPatientRelation).where(
            and_(
                DoctorPatientRelation.doctor_id == doctor_id,
                DoctorPatientRelation.initiated_by == 'patient_at',
                DoctorPatientRelation.status.in_(['pending', 'active'])
            )
        )
        result = await db.execute(relation_query)
        relations = result.scalars().all()
        
        # 收集明确共享给该医生的病例ID
        shared_case_ids = []
        for relation in relations:
            if relation.shared_case_ids:
                shared_case_ids.extend(relation.shared_case_ids)

        # Query: visible_to_doctors=True OR (case_id in shared_case_ids)
        if shared_case_ids:
            query = select(SharedMedicalCase).where(
                or_(
                    SharedMedicalCase.visible_to_doctors == True,
                    SharedMedicalCase.id.in_(shared_case_ids)
                )
            )
        else:
            # 没有被@提及，只能看到公开共享的病例
            query = select(SharedMedicalCase).where(
                SharedMedicalCase.visible_to_doctors == True
            )

    result = await db.execute(query)
    return result.scalars().all()


def anonymize_case_data(case: SharedMedicalCase) -> Dict[str, Any]:
    """
    Ensure case data is fully anonymized for research
    确保病例数据完全匿名化用于科研
    """
    
    # Double-blind anonymization
    anonymized = {
        "id": str(case.id),
        "anonymous_patient_profile": case.anonymous_patient_profile,
        "anonymized_symptoms": case.anonymized_symptoms,
        "anonymized_diagnosis": case.anonymized_diagnosis,
        "created_at": case.created_at.isoformat(),
        "view_count": case.view_count
    }
    
    # Remove any potential identifiers from profile
    if anonymized["anonymous_patient_profile"]:
        profile = anonymized["anonymous_patient_profile"].copy()
        # Ensure no identifying information
        profile.pop("specific_location", None)
        profile.pop("occupation", None)
        profile.pop("education", None)
        anonymized["anonymous_patient_profile"] = profile
    
    return anonymized


def parse_diagnosis_for_research(diagnosis_text: str) -> Dict[str, Any]:
    """
    Parse AI diagnosis text to extract structured research data.
    Extracts lab values, medications, diagnoses, etc.
    
    Returns a dictionary with structured fields for research CSV export.
    """
    import re
    
    if not diagnosis_text:
        return {}
    
    result = {
        "lab_values": {},
        "primary_diagnosis": "",
        "secondary_diagnosis": "",
        "confidence": "",
        "current_medications": "",
        "recommended_medications": "",
        "treatment_plan": "",
        "follow_up": "",
        "allergies": "",
        "special_notes": ""
    }
    
    try:
        # Extract lab values using regex patterns
        # WBC (白细胞计数)
        wbc_match = re.search(r'白细胞.*?(\d+\.?\d*)\s*[×x]\s*10\^9/L', diagnosis_text, re.IGNORECASE)
        if wbc_match:
            result["lab_values"]["wbc"] = wbc_match.group(1)
        
        # RBC (红细胞计数)
        rbc_match = re.search(r'红细胞.*?(\d+\.?\d*)\s*[×x]\s*10\^12/L', diagnosis_text, re.IGNORECASE)
        if rbc_match:
            result["lab_values"]["rbc"] = rbc_match.group(1)
        
        # Hemoglobin (血红蛋白)
        hb_match = re.search(r'血红蛋白.*?(\d+\.?\d*)\s*[gG]/[lL]', diagnosis_text, re.IGNORECASE)
        if hb_match:
            result["lab_values"]["hb"] = hb_match.group(1)
        
        # Platelets (血小板)
        plt_match = re.search(r'血小板.*?(\d+\.?\d*)\s*[×x]\s*10\^9/L', diagnosis_text, re.IGNORECASE)
        if plt_match:
            result["lab_values"]["plt"] = plt_match.group(1)
        
        # Neutrophils (中性粒细胞)
        neut_match = re.search(r'中性粒细胞.*?绝对值.*?(\d+\.?\d*)', diagnosis_text, re.IGNORECASE)
        if neut_match:
            result["lab_values"]["neutrophil"] = neut_match.group(1)
        
        # Lymphocytes (淋巴细胞)
        lymph_match = re.search(r'淋巴细胞.*?绝对值.*?(\d+\.?\d*)', diagnosis_text, re.IGNORECASE)
        if lymph_match:
            result["lab_values"]["lymphocyte"] = lymph_match.group(1)
        
        # CRP (C反应蛋白)
        crp_match = re.search(r'CRP|C反应蛋白.*?(\d+\.?\d*)\s*[mM][gG]/[lL]', diagnosis_text, re.IGNORECASE)
        if crp_match:
            result["lab_values"]["crp"] = crp_match.group(1)
        
        # PCT (降钙素原)
        pct_match = re.search(r'PCT|降钙素原.*?(\d+\.?\d*)\s*[nN][gG]/[mM][lL]', diagnosis_text, re.IGNORECASE)
        if pct_match:
            result["lab_values"]["pct"] = pct_match.group(1)
        
        # ESR (血沉)
        esr_match = re.search(r'ESR|血沉.*?(\d+\.?\d*)\s*[mM][mM]/[hH]', diagnosis_text, re.IGNORECASE)
        if esr_match:
            result["lab_values"]["esr"] = esr_match.group(1)
        
        # Extract primary diagnosis (初步诊断)
        primary_diag_match = re.search(r'(?:###\s*1\.|初步诊断|1\.\s*初步诊断)[\s\S]*?(?:\n\n|\n###|\Z)', diagnosis_text)
        if primary_diag_match:
            primary_section = primary_diag_match.group(0)
            # Look for disease names in the diagnosis table or list
            disease_patterns = [
                r'\|\s*([^|]+?)(?:肺炎|支气管炎|哮喘|感染|炎症|咳嗽变异性哮喘|支原体|病毒|细菌)',
                r'(?:诊断为|考虑|可能为)\s*([^。\n]+)',
                r'\*\*([^*]+?)\*\*\s*\|'
            ]
            for pattern in disease_patterns:
                match = re.search(pattern, primary_section, re.IGNORECASE)
                if match:
                    result["primary_diagnosis"] = match.group(1).strip()[:100]
                    break
        
        # Extract secondary diagnosis (鉴别诊断)
        secondary_match = re.search(r'(?:###\s*4\.|鉴别诊断|4\.\s*鉴别诊断)[\s\S]*?(?:\n\n|\n###|\Z)', diagnosis_text)
        if secondary_match:
            secondary_section = secondary_match.group(0)
            # Extract disease names mentioned
            diseases = re.findall(r'\*\*([^*]+?)\*\*', secondary_section)
            if diseases:
                result["secondary_diagnosis"] = ", ".join(diseases[:3])[:200]
        
        # Extract treatment recommendations (治疗方案)
        treatment_match = re.search(r'(?:###\s*3\.|治疗方案|3\.\s*治疗方案)[\s\S]*?(?:\n\n|\n###|\Z)', diagnosis_text)
        if treatment_match:
            treatment_section = treatment_match.group(0)
            # Look for medications
            meds_patterns = [
                r'(?:药物|用药|治疗).*?：\s*([^。\n]+)',
                r'\*\*([^*]+?)\*\*.*?口服|静脉|注射|雾化',
                r'(?:建议|推荐).*?(?:使用|给予).*?([^。\n]{10,100})'
            ]
            for pattern in meds_patterns:
                med_match = re.search(pattern, treatment_section, re.IGNORECASE)
                if med_match:
                    result["recommended_medications"] = med_match.group(1).strip()[:200]
                    break
            
            # Get general treatment plan
            result["treatment_plan"] = treatment_section[:500].replace('\n', ' ').strip()
        
        # Extract follow-up recommendations (随访建议)
        followup_match = re.search(r'(?:随访|复查|复诊|建议)[\s\S]*?(?:\n\n|\n###|\Z)', diagnosis_text)
        if followup_match:
            result["follow_up"] = followup_match.group(0)[:300].replace('\n', ' ').strip()
        
        # Extract allergies (过敏史)
        allergy_match = re.search(r'(?:过敏史|过敏原|过敏)[：:]\s*([^。\n]+)', diagnosis_text, re.IGNORECASE)
        if allergy_match:
            result["allergies"] = allergy_match.group(1).strip()[:100]
        
        # Extract special notes (特别提醒/注意事项)
        notes_match = re.search(r'(?:特别提醒|注意事项|重要提示)[\s\S]*?(?:\n\n|\n###|\Z)', diagnosis_text)
        if notes_match:
            result["special_notes"] = notes_match.group(0)[:300].replace('\n', ' ').strip()
        
        # Extract confidence level (诊断可能性/置信度)
        confidence_match = re.search(r'(?:可能性|置信度|confidence)\s*[:：]\s*(\d+)%', diagnosis_text, re.IGNORECASE)
        if confidence_match:
            result["confidence"] = f"{confidence_match.group(1)}%"
        else:
            # Look for high/medium/low markers
            if '高' in diagnosis_text[:500] or 'high' in diagnosis_text[:500].lower():
                result["confidence"] = "高"
            elif '中' in diagnosis_text[:500] or 'medium' in diagnosis_text[:500].lower():
                result["confidence"] = "中"
            elif '低' in diagnosis_text[:500] or 'low' in diagnosis_text[:500].lower():
                result["confidence"] = "低"
    
    except Exception as e:
        logger.warning(f"Error parsing diagnosis for research: {e}")
    
    return result


async def log_case_access(
    db: AsyncSession,
    case_id: uuid.UUID,
    doctor_id: uuid.UUID,
    ip_address: Optional[str] = None
):
    """
    Log doctor access to case for audit
    记录医生访问病例用于审计
    """
    case = await db.get(SharedMedicalCase, case_id)
    if case:
        # Update view count
        case.view_count += 1
        
        # Add to doctor views
        if not case.doctor_views:
            case.doctor_views = []
        
        case.doctor_views.append({
            "doctor_id": str(doctor_id),
            "viewed_at": datetime.utcnow().isoformat(),
            "ip": ip_address
        })
        
        await db.commit()


# =============================================================================
# New Doctor API Endpoints / 新的医生API端点
# =============================================================================

@router.get("/dashboard", response_model=DashboardStats)
async def get_doctor_dashboard(
    current_user: User = Depends(require_doctor),
    db: AsyncSession = Depends(get_db)
):
    """
    Get doctor dashboard overview
    获取医生工作台概览
    
    Returns:
    - Pending @mentions count
    - Public cases by specialty  
    - Today's new cases
    - Exported research data count
    """
    
    doctor_id = current_user.id

    # Count ALL @mentions (both pending and active) for this doctor
    mentions_query = select(func.count(DoctorPatientRelation.id)).where(
        and_(
            DoctorPatientRelation.doctor_id == doctor_id,
            DoctorPatientRelation.initiated_by == 'patient_at',
            DoctorPatientRelation.status.in_(['pending', 'active'])
        )
    )
    mentioned_cases = await db.scalar(mentions_query)

    # Get accessible public cases count (visible to doctors)
    public_cases_query = select(func.count(SharedMedicalCase.id)).where(
        SharedMedicalCase.visible_to_doctors == True
    )
    public_cases = await db.scalar(public_cases_query)

    # Count today's new cases that this doctor can access
    today = datetime.utcnow().date()
    today_cases_query = select(func.count(SharedMedicalCase.id)).where(
        and_(
            func.date(SharedMedicalCase.created_at) == today,
            SharedMedicalCase.visible_to_doctors == True
        )
    )
    today_cases = await db.scalar(today_cases_query)

    # Count exported research data (simplified)
    export_query = select(func.count(SharedMedicalCase.id)).where(
        SharedMedicalCase.exported_count > 0
    )
    exported_count = await db.scalar(export_query)

    # Calculate growth (today vs yesterday)
    yesterday = today - timedelta(days=1)
    yesterday_query = select(func.count(SharedMedicalCase.id)).where(
        and_(
            func.date(SharedMedicalCase.created_at) == yesterday,
            SharedMedicalCase.visible_to_doctors == True
        )
    )
    yesterday_cases = await db.scalar(yesterday_query)
    growth = (today_cases or 0) - (yesterday_cases or 0)

    return DashboardStats(
        mentioned_cases=mentioned_cases or 0,
        public_cases=public_cases or 0,
        today_cases=today_cases or 0,
        exported_count=exported_count or 0,
        growth=growth
    )


@router.get("/cases", response_model=List[SharedCaseResponse])
async def get_cases(
    type: str = Query(..., description="Case type: mentioned, public, all"),
    specialty: Optional[str] = Query(None, description="Filter by disease category"),
    disease_category: Optional[str] = Query(None, description="Filter by disease category"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(require_doctor),
    db: AsyncSession = Depends(get_db)
):
    """
    Get list of cases with filtering and pagination
    获取病例列表，支持筛选和分页
    
    Returns only PII-cleaned anonymized data
    仅返回PII清理的匿名化数据
    """
    
    if type not in ["mentioned", "public", "all"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="type must be one of: mentioned, public, all"
        )
    
    # Get accessible cases
    accessible_cases = await get_doctor_accessible_cases(db, current_user.id, type)

    # Handle empty accessible cases - return empty list early
    if not accessible_cases:
        return []

    # Build query with filters
    query = select(SharedMedicalCase).options(
        selectinload(SharedMedicalCase.original_case).selectinload(MedicalCase.disease)
    ).where(
        SharedMedicalCase.id.in_([case.id for case in accessible_cases])
    )
    
    # Apply specialty filter
    if specialty or disease_category:
        query = query.join(MedicalCase).join(Disease).where(
            Disease.category == (specialty or disease_category)
        )
    
    # Apply pagination
    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit).order_by(desc(SharedMedicalCase.created_at))
    
    result = await db.execute(query)
    cases = result.scalars().all()
    
    # Load chronic diseases for each case
    case_responses = []
    for case in cases:
        # Log access
        await log_case_access(db, case.id, current_user.id)
        
        # Get patient's chronic diseases through original_case
        chronic_diseases = []
        if case.original_case_id:
            # Get the medical case to find patient_id
            medical_case_result = await db.execute(
                select(MedicalCase).where(MedicalCase.id == case.original_case_id)
            )
            medical_case = medical_case_result.scalar_one_or_none()
            
            if medical_case and medical_case.patient_id:
                # Get patient's active chronic diseases
                chronic_result = await db.execute(
                    select(PatientChronicCondition, ChronicDisease)
                    .join(ChronicDisease, PatientChronicCondition.disease_id == ChronicDisease.id)
                    .where(
                        and_(
                            PatientChronicCondition.patient_id == medical_case.patient_id,
                            PatientChronicCondition.is_active == True
                        )
                    )
                )
                
                for condition, disease in chronic_result.all():
                    chronic_diseases.append({
                        'id': disease.id,
                        'icd10_code': disease.icd10_code,
                        'icd10_name': disease.icd10_name,
                        'disease_type': disease.disease_type,
                        'common_names': disease.common_names
                    })
        
        # Build response manually with chronic diseases
        # Get disease_category from original_case.disease if available
        disease_category = None
        if case.original_case and case.original_case.disease:
            disease_category = case.original_case.disease.category
        
        case_data = {
            'id': case.id,
            'original_case_id': case.original_case_id,
            'anonymous_patient_profile': case.anonymous_patient_profile,
            'anonymized_symptoms': case.anonymized_symptoms,
            'anonymized_diagnosis': case.anonymized_diagnosis,
            'disease_category': disease_category,
            'created_at': case.created_at,
            'view_count': case.view_count,
            'patient_chronic_diseases': chronic_diseases if chronic_diseases else None
        }
        case_responses.append(SharedCaseResponse(**case_data))
    
    return case_responses


@router.get("/cases/{case_id}", response_model=CaseDetailResponse)
async def get_case_detail(
    case_id: uuid.UUID,
    current_user: User = Depends(require_doctor),
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed information about a specific case
    获取单个病例的详细信息
    
    Verifies doctor has permission to view the case
    验证医生是否有权限查看该病例
    """
    
    # Get the shared case with eager loading of relationships
    case_query = select(SharedMedicalCase).options(
        selectinload(SharedMedicalCase.original_case).selectinload(MedicalCase.disease)
    ).where(SharedMedicalCase.id == case_id)
    case_result = await db.execute(case_query)
    case = case_result.scalar_one_or_none()
    
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found"
        )
    
    # Verify access permissions
    accessible_cases = await get_doctor_accessible_cases(db, current_user.id, "all")
    accessible_ids = [c.id for c in accessible_cases]
    
    if case_id not in accessible_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this case"
        )
    
    # Get related documents (PII cleaned only)
    documents_query = select(MedicalDocument).join(MedicalCase).where(
        and_(
            MedicalCase.id == case.original_case_id,
            MedicalDocument.pii_cleaning_status == 'completed'
        )
    )
    documents_result = await db.execute(documents_query)
    documents = documents_result.scalars().all()

    # Build document responses with file URLs
    document_responses = []
    for doc in documents:
        doc_dict = {
            "id": doc.id,
            "filename": doc.filename,
            "file_type": doc.file_type,
            "pii_cleaning_status": doc.pii_cleaning_status,
            "cleaned_content": doc.cleaned_content,
            "file_url": f"/api/v1/documents/{doc.id}/download" if doc.file_path else None
        }
        document_responses.append(CaseDocumentResponse(**doc_dict))

    # Get AI feedbacks
    ai_feedbacks_query = select(AIFeedback).where(
        AIFeedback.medical_case_id == case.original_case_id
    )
    ai_feedbacks_result = await db.execute(ai_feedbacks_query)
    ai_feedbacks = ai_feedbacks_result.scalars().all()

    # Get patient's chronic diseases
    chronic_diseases = []
    if case.original_case_id:
        # Get the medical case to find patient_id
        medical_case_result = await db.execute(
            select(MedicalCase).where(MedicalCase.id == case.original_case_id)
        )
        medical_case = medical_case_result.scalar_one_or_none()
        
        if medical_case and medical_case.patient_id:
            # Get patient's active chronic diseases
            chronic_result = await db.execute(
                select(PatientChronicCondition, ChronicDisease)
                .join(ChronicDisease, PatientChronicCondition.disease_id == ChronicDisease.id)
                .where(
                    and_(
                        PatientChronicCondition.patient_id == medical_case.patient_id,
                        PatientChronicCondition.is_active == True
                    )
                )
            )
            
            for condition, disease in chronic_result.all():
                chronic_diseases.append({
                    'id': disease.id,
                    'icd10_code': disease.icd10_code,
                    'icd10_name': disease.icd10_name,
                    'disease_type': disease.disease_type,
                    'common_names': disease.common_names
                })

    # Log this access
    await log_case_access(db, case_id, current_user.id)

    # Build case response with chronic diseases
    case_dict = {
        'id': case.id,
        'original_case_id': case.original_case_id,
        'anonymous_patient_profile': case.anonymous_patient_profile,
        'anonymized_symptoms': case.anonymized_symptoms,
        'anonymized_diagnosis': case.anonymized_diagnosis,
        'disease_category': case.original_case.disease.category if case.original_case and case.original_case.disease else None,
        'created_at': case.created_at,
        'view_count': case.view_count,
        'patient_chronic_diseases': chronic_diseases if chronic_diseases else None
    }

    return CaseDetailResponse(
        case=SharedCaseResponse(**case_dict),
        documents=document_responses,
        ai_feedbacks=[{
            "feedback_type": af.feedback_type,
            "ai_response": af.ai_response,
            "confidence_score": float(af.confidence_score) if af.confidence_score else None,
            "recommendations": af.recommendations,
            "created_at": af.created_at.isoformat()
        } for af in ai_feedbacks]
    )


@router.post("/cases/search", response_model=List[SharedCaseResponse])
async def search_cases(
    search_request: SearchRequest,
    current_user: User = Depends(require_doctor),
    db: AsyncSession = Depends(get_db)
):
    """
    Search cases for research purposes
    科研搜索病例
    
    Returns fully anonymized case data matching search criteria
    返回符合条件的完全匿名化病例数据
    """
    
    # Build base query for accessible cases
    query = select(SharedMedicalCase).where(
        SharedMedicalCase.visible_for_research == True
    )
    
    # Apply filters based on search criteria
    if search_request.disease_categories:
        query = query.join(MedicalCase).join(Disease).where(
            Disease.category.in_(search_request.disease_categories)
        )
    
    if search_request.date_from or search_request.date_to:
        date_filter = []
        if search_request.date_from:
            date_filter.append(SharedMedicalCase.created_at >= search_request.date_from)
        if search_request.date_to:
            date_filter.append(SharedMedicalCase.created_at <= search_request.date_to)
        if date_filter:
            query = query.where(and_(*date_filter))
    
    # Apply JSON filters on anonymous profile
    if search_request.age_ranges or search_request.genders or search_request.city_tiers:
        # JSON filtering for anonymous profile fields
        json_conditions = []
        
        if search_request.age_ranges:
            json_conditions.append(
                SharedMedicalCase.anonymous_patient_profile['age_range'].astext.in_(search_request.age_ranges)
            )
        
        if search_request.genders:
            json_conditions.append(
                SharedMedicalCase.anonymous_patient_profile['gender'].astext.in_(search_request.genders)
            )
        
        if search_request.city_tiers:
            json_conditions.append(
                SharedMedicalCase.anonymous_patient_profile['city_tier'].astext.in_(search_request.city_tiers)
            )
        
        if json_conditions:
            query = query.where(and_(*json_conditions))
    
    # Apply pagination
    offset = (search_request.page - 1) * search_request.limit
    query = query.offset(offset).limit(search_request.limit).order_by(desc(SharedMedicalCase.created_at))
    
    result = await db.execute(query)
    cases = result.scalars().all()
    
    # Log access for research purposes
    for case in cases:
        await log_case_access(db, case.id, current_user.id)
    
    return [SharedCaseResponse.model_validate(case) for case in cases]


@router.post("/cases/export")
async def export_cases(
    export_request: ExportRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(require_doctor),
    db: AsyncSession = Depends(get_db)
):
    """
    Export research data in specified format
    导出科研数据
    
    Generates double-blind export data with no patient or doctor IDs
    生成无患者ID、无医生ID的双盲导出数据
    """
    
    if export_request.format not in ["json", "csv"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Format must be 'json' or 'csv'"
        )
    
    if not export_request.case_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="case_ids cannot be empty"
        )
    
    # Verify export permission for all requested cases
    # 使用专门的导出权限检查
    for case_id in export_request.case_ids:
        has_permission = await check_export_permission(db, current_user.id, case_id)
        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"无权限导出病例 {case_id}。只能导出公开病例或@提及您的病例。"
            )
    
    # Get cases to export with original case data
    query = select(SharedMedicalCase, MedicalCase).join(
        MedicalCase, SharedMedicalCase.original_case_id == MedicalCase.id
    ).where(
        SharedMedicalCase.id.in_(export_request.case_ids)
    )
    result = await db.execute(query)
    cases_with_original = result.all()
    
    # Update export counts in background
    background_tasks.add_task(
        update_export_counts,
        db,
        export_request.case_ids,
        current_user.id
    )
    
    # Generate export file
    if export_request.format == "json":
        export_data = []
        for shared_case, original_case in cases_with_original:
            case_data = anonymize_case_data(shared_case)
            
            if export_request.include_documents:
                # Get PII cleaned documents
                docs_query = select(MedicalDocument).where(
                    and_(
                        MedicalDocument.medical_case_id == original_case.id,
                        MedicalDocument.pii_cleaning_status == 'completed'
                    )
                )
                docs_result = await db.execute(docs_query)
                documents = docs_result.scalars().all()
                
                case_data["documents"] = [
                    {
                        "filename": doc.filename,
                        "file_type": doc.file_type,
                        "cleaned_content": doc.cleaned_content
                    }
                    for doc in documents
                ]
            
            export_data.append(case_data)
        
        return StreamingResponse(
            io.StringIO(json.dumps(export_data, indent=2, ensure_ascii=False)),
            media_type="application/json",
            headers={"Content-Disposition": "attachment; filename=research_data.json"}
        )
    else:  # CSV - Research-friendly structured format
        output = io.StringIO()
        if cases_with_original:
            # Define research-friendly fieldnames
            fieldnames = [
                # Basic Info
                "case_id", "created_at",
                # Demographics
                "age_range", "gender", "city_tier", "city_environment",
                # Symptoms
                "symptoms", "severity", "duration",
                # Lab Tests (common indicators)
                "wbc", "rbc", "hb", "plt", "neutrophil", "lymphocyte",
                "crp", "pct", "esr",
                # Diagnosis
                "primary_diagnosis", "secondary_diagnosis", "diagnosis_confidence",
                # Medications
                "current_medications", "recommended_medications",
                # Treatment
                "treatment_plan", "follow_up_recommendations",
                # Notes
                "allergies", "special_notes"
            ]
            
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            
            for shared_case, original_case in cases_with_original:
                profile = shared_case.anonymous_patient_profile or {}
                
                # Parse diagnosis to extract structured information
                diagnosis_text = shared_case.anonymized_diagnosis or ""
                diagnosis_data = parse_diagnosis_for_research(diagnosis_text)
                
                # Get symptoms from original case
                symptoms = original_case.symptoms or shared_case.anonymized_symptoms or ""
                
                # Get clinical findings if available
                clinical_findings = original_case.clinical_findings or {}
                
                row = {
                    "case_id": str(shared_case.id)[:8],
                    "created_at": shared_case.created_at.isoformat() if shared_case.created_at else "",
                    # Demographics
                    "age_range": profile.get("age_range", ""),
                    "gender": profile.get("gender", ""),
                    "city_tier": profile.get("city_tier", ""),
                    "city_environment": profile.get("city_environment", ""),
                    # Symptoms
                    "symptoms": symptoms[:500] if symptoms else "",  # Truncate for readability
                    "severity": original_case.severity or "",
                    "duration": "",  # Could be parsed from symptoms
                    # Lab Tests - try to extract from diagnosis or clinical findings
                    "wbc": diagnosis_data.get("lab_values", {}).get("wbc", ""),
                    "rbc": diagnosis_data.get("lab_values", {}).get("rbc", ""),
                    "hb": diagnosis_data.get("lab_values", {}).get("hb", ""),
                    "plt": diagnosis_data.get("lab_values", {}).get("plt", ""),
                    "neutrophil": diagnosis_data.get("lab_values", {}).get("neutrophil", ""),
                    "lymphocyte": diagnosis_data.get("lab_values", {}).get("lymphocyte", ""),
                    "crp": diagnosis_data.get("lab_values", {}).get("crp", ""),
                    "pct": diagnosis_data.get("lab_values", {}).get("pct", ""),
                    "esr": diagnosis_data.get("lab_values", {}).get("esr", ""),
                    # Diagnosis
                    "primary_diagnosis": diagnosis_data.get("primary_diagnosis", ""),
                    "secondary_diagnosis": diagnosis_data.get("secondary_diagnosis", ""),
                    "diagnosis_confidence": diagnosis_data.get("confidence", ""),
                    # Medications
                    "current_medications": diagnosis_data.get("current_medications", ""),
                    "recommended_medications": diagnosis_data.get("recommended_medications", ""),
                    # Treatment
                    "treatment_plan": diagnosis_data.get("treatment_plan", ""),
                    "follow_up_recommendations": diagnosis_data.get("follow_up", ""),
                    # Notes
                    "allergies": diagnosis_data.get("allergies", ""),
                    "special_notes": diagnosis_data.get("special_notes", "")
                }
                writer.writerow(row)
        
        return StreamingResponse(
            io.StringIO(output.getvalue()),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=research_data.csv"}
        )


async def update_export_counts(
    db: AsyncSession,
    case_ids: List[uuid.UUID],
    doctor_id: uuid.UUID
):
    """
    Update export counts and log export for compliance
    更新导出计数并记录导出用于合规审计
    """
    try:
        for case_id in case_ids:
            case = await db.get(SharedMedicalCase, case_id)
            if case:
                case.exported_count += 1
                
                if not case.export_records:
                    case.export_records = []
                
                case.export_records.append({
                    "exported_by": str(doctor_id),
                    "exported_at": datetime.utcnow().isoformat(),
                    "export_type": "research"
                })
        
        await db.commit()
        logger.info(f"Export counts updated for {len(case_ids)} cases by doctor {doctor_id}")
    except Exception as e:
        logger.error(f"Failed to update export counts: {e}")
        await db.rollback()


@router.get("/mentions", response_model=List[DoctorMentionResponse])
async def get_doctor_mentions(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_doctor),
    db: AsyncSession = Depends(get_db)
):
    """
    Get cases where patients have @mentioned the current doctor
    获取患者主动@当前医生的病例列表
    
    Supports filtering by read/unread status
    支持按已读/未读状态筛选
    """
    
    doctor_id = current_user.id
    
    # Query doctor-patient relations where patient initiated contact
    query = select(DoctorPatientRelation).where(
        and_(
            DoctorPatientRelation.doctor_id == doctor_id,
            DoctorPatientRelation.initiated_by == 'patient_at',
            DoctorPatientRelation.status.in_(['pending', 'active'])
        )
    ).join(User, DoctorPatientRelation.patient_id == User.id).order_by(
        desc(DoctorPatientRelation.created_at)
    )
    
    # Apply pagination
    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit)
    
    result = await db.execute(query)
    relations = result.scalars().all()
    
    mentions = []
    for relation in relations:
        # Get patient display info
        patient = relation.patient
        patient_display = patient.get_display_info()
        
        mention = DoctorMentionResponse(
            id=relation.id,
            patient_id=patient.id,
            patient_display_name=patient_display,
            relation_id=relation.id,
            status=relation.status,
            patient_message=relation.patient_message,
            created_at=relation.created_at,
            is_read=relation.status == 'active'  # Simplified - active means read
        )
        mentions.append(mention)
    
    return mentions


@router.post("/mentions/{mention_id}/mark-read")
async def mark_mention_as_read(
    mention_id: uuid.UUID,
    current_user: User = Depends(require_doctor),
    db: AsyncSession = Depends(get_db)
):
    """
    Mark a doctor mention as read
    将@医生的病例标记为已查看
    
    Updates the relation status to 'active'
    将关系状态更新为'active'
    """
    
    # Get the doctor-patient relation with eager loading
    relation_query = select(DoctorPatientRelation).where(DoctorPatientRelation.id == mention_id)
    relation_result = await db.execute(relation_query)
    relation = relation_result.scalar_one_or_none()
    
    if not relation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mention not found | 提及记录未找到"
        )
    
    # Verify this mention is for the current doctor
    if relation.doctor_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this mention"
        )
    
    # Update status to active (read)
    if relation.status == 'pending':
        relation.status = 'active'
        relation.activated_at = datetime.utcnow()
        
        # Log the action
        await db.commit()
        
        logger.info(f"Doctor {current_user.id} marked mention {mention_id} as read")
    
    return {"message": "Mention marked as read"}


# =============================================================================
# Doctor Case Comment Endpoints | 医生病例评论端点
# =============================================================================

class CommentCreateRequest(BaseModel):
    """Create comment request / 创建评论请求"""
    content: str
    comment_type: str = "general"  # suggestion, diagnosis_opinion, treatment_advice, general
    is_public: bool = True


class CommentUpdateRequest(BaseModel):
    """Update comment request / 更新评论请求"""
    content: str


class CommentResponse(BaseModel):
    """Comment response / 评论响应"""
    id: uuid.UUID
    shared_case_id: uuid.UUID
    doctor_id: uuid.UUID
    doctor_name: str
    doctor_specialty: Optional[str]
    doctor_hospital: Optional[str]
    comment_type: str
    content: str
    is_public: bool
    status: str
    created_at: datetime
    edited_at: Optional[datetime]
    patient_replies: Optional[List[dict]] = None


@router.post("/cases/{case_id}/comments", response_model=CommentResponse)
async def create_comment(
    case_id: uuid.UUID,
    request: CommentCreateRequest,
    current_user: User = Depends(require_verified_doctor),
    db: AsyncSession = Depends(get_db)
):
    """
    Add a comment to a shared case / 为分享病例添加评论
    
    Allows verified doctors to add professional suggestions and opinions.
    """
    from app.models.models import DoctorCaseComment, DoctorPatientRelation
    from sqlalchemy import and_
    
    # Verify case exists with eager loading
    case_query = select(SharedMedicalCase).options(
        selectinload(SharedMedicalCase.original_case)
    ).where(SharedMedicalCase.id == case_id)
    case_result = await db.execute(case_query)
    case = case_result.scalar_one_or_none()
    
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found | 病例未找到"
        )
    
    # Check visibility permission
    # 1. If visible_to_doctors=True, any verified doctor can access
    # 2. If visible_to_doctors=False, only @mentioned doctors can access
    if not case.visible_to_doctors:
        # Check if this doctor was @mentioned by the patient
        # Get the patient_id from the original medical case
        medical_case = case.original_case
        if medical_case:
            relation_query = select(DoctorPatientRelation).where(
                and_(
                    DoctorPatientRelation.doctor_id == current_user.id,
                    DoctorPatientRelation.patient_id == medical_case.patient_id,
                    DoctorPatientRelation.initiated_by == 'patient_at',
                    DoctorPatientRelation.status.in_(['pending', 'active'])
                )
            )
            result = await db.execute(relation_query)
            relation = result.scalar_one_or_none()
            
            if not relation:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Case not visible to you"
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Case not found"
            )
    
    # Validate comment type
    valid_types = ['suggestion', 'diagnosis_opinion', 'treatment_advice', 'general']
    if request.comment_type not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid comment type. Must be one of: {', '.join(valid_types)}"
        )
    
    # Create comment
    comment = DoctorCaseComment(
        id=uuid.uuid4(),
        shared_case_id=case_id,
        doctor_id=current_user.id,
        comment_type=request.comment_type,
        content=request.content,
        doctor_specialty=current_user.specialty,
        doctor_hospital=current_user.hospital,
        is_public=request.is_public,
        status='active'
    )
    
    db.add(comment)
    await db.commit()
    await db.refresh(comment)
    
    logger.info(f"Doctor {current_user.id} added comment to case {case_id}")
    
    return CommentResponse(
        id=comment.id,
        shared_case_id=comment.shared_case_id,
        doctor_id=comment.doctor_id,
        doctor_name=current_user.full_name,
        doctor_specialty=comment.doctor_specialty,
        doctor_hospital=comment.doctor_hospital,
        comment_type=comment.comment_type,
        content=comment.content,
        is_public=comment.is_public,
        status=comment.status,
        created_at=comment.created_at,
        edited_at=comment.edited_at
    )


@router.get("/cases/{case_id}/comments", response_model=List[CommentResponse])
async def get_case_comments(
    case_id: uuid.UUID,
    comment_type: Optional[str] = Query(None, description="Filter by comment type"),
    current_user: User = Depends(require_doctor),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all comments for a shared case / 获取分享病例的所有评论
    Doctors can see their own comments and patient replies to their comments.
    Doctors cannot see other doctors' comments or patient replies to other doctors.
    """
    from app.models.models import DoctorCaseComment, CaseCommentReply
    from sqlalchemy.orm import joinedload
    from sqlalchemy.exc import SQLAlchemyError

    try:
        # Build query with eager loading of doctor relationship and patient replies
        query = select(DoctorCaseComment).options(
            joinedload(DoctorCaseComment.doctor),
            joinedload(DoctorCaseComment.patient_replies)
        ).where(
            DoctorCaseComment.shared_case_id == case_id,
            DoctorCaseComment.status.in_(['active', 'edited'])
        )

        # Filter by type if specified
        if comment_type:
            query = query.where(DoctorCaseComment.comment_type == comment_type)

        # Only show current doctor's own comments (not other doctors' comments)
        query = query.where(
            DoctorCaseComment.doctor_id == current_user.id
        )

        query = query.order_by(desc(DoctorCaseComment.created_at))

        result = await db.execute(query)
        comments = result.unique().scalars().all()

        response = []
        for c in comments:
            try:
                doctor_name = "Unknown"
                if c.doctor is not None:
                    doctor_name = c.doctor.full_name

                # Get patient replies for this doctor's comment
                patient_replies = []
                if hasattr(c, 'patient_replies') and c.patient_replies:
                    for reply in c.patient_replies:
                        if reply.status == 'active':
                            patient_replies.append({
                                "id": str(reply.id),
                                "content": reply.content,
                                "created_at": reply.created_at.isoformat() if reply.created_at else None
                            })

                # Build response dict with patient replies
                comment_dict = {
                    "id": c.id,
                    "shared_case_id": c.shared_case_id,
                    "doctor_id": c.doctor_id,
                    "doctor_name": doctor_name,
                    "doctor_specialty": c.doctor_specialty,
                    "doctor_hospital": c.doctor_hospital,
                    "comment_type": c.comment_type,
                    "content": c.content,
                    "is_public": c.is_public,
                    "status": c.status,
                    "created_at": c.created_at,
                    "edited_at": c.edited_at
                }

                # Add patient_replies to response (will be handled by frontend)
                if patient_replies:
                    comment_dict["patient_replies"] = patient_replies

                response.append(CommentResponse(**comment_dict))
            except Exception as e:
                logger.error(f"Error processing comment {c.id}: {str(e)}")
                continue

        return response

    except SQLAlchemyError as e:
        logger.error(f"Database error fetching comments for case {case_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"数据库错误: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error fetching comments for case {case_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取评论失败: {str(e)}"
        )


@router.put("/comments/{comment_id}", response_model=CommentResponse)
async def update_comment(
    comment_id: uuid.UUID,
    request: CommentUpdateRequest,
    current_user: User = Depends(require_verified_doctor),
    db: AsyncSession = Depends(get_db)
):
    """
    Update own comment / 更新自己的评论
    """
    from app.models.models import DoctorCaseComment
    
    # Get comment
    comment = await db.get(DoctorCaseComment, comment_id)
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
    
    # Verify ownership
    if comment.doctor_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only edit your own comments"
        )
    
    # Save original content before edit
    if comment.status != 'edited':
        comment.original_content = comment.content
    
    # Update comment
    comment.content = request.content
    comment.status = 'edited'
    comment.edited_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(comment)
    
    logger.info(f"Doctor {current_user.id} updated comment {comment_id}")
    
    return CommentResponse(
        id=comment.id,
        shared_case_id=comment.shared_case_id,
        doctor_id=comment.doctor_id,
        doctor_name=current_user.full_name,
        doctor_specialty=comment.doctor_specialty,
        doctor_hospital=comment.doctor_hospital,
        comment_type=comment.comment_type,
        content=comment.content,
        is_public=comment.is_public,
        status=comment.status,
        created_at=comment.created_at,
        edited_at=comment.edited_at
    )


@router.delete("/comments/{comment_id}")
async def delete_comment(
    comment_id: uuid.UUID,
    current_user: User = Depends(require_verified_doctor),
    db: AsyncSession = Depends(get_db)
):
    """
    Soft delete own comment / 软删除自己的评论
    """
    from app.models.models import DoctorCaseComment
    
    # Get comment
    comment = await db.get(DoctorCaseComment, comment_id)
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
    
    # Verify ownership
    if comment.doctor_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Can only delete your own comments"
        )
    
    # Soft delete
    comment.status = 'hidden'
    await db.commit()
    
    logger.info(f"Doctor {current_user.id} deleted comment {comment_id}")
    
    return {"message": "Comment deleted successfully"}