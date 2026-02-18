"""
Chronic Disease Management API | 特殊病与慢性病管理API

Endpoints:
- GET    /api/v1/chronic-diseases              # 获取所有慢性病列表
- GET    /api/v1/chronic-diseases/{id}         # 获取单个慢性病详情
- GET    /api/v1/patients/me/chronic-diseases  # 获取当前患者的慢性病
- POST   /api/v1/patients/me/chronic-diseases  # 添加慢性病到患者档案
- PUT    /api/v1/patients/me/chronic-diseases/{id}  # 更新患者慢性病信息
- DELETE /api/v1/patients/me/chronic-diseases/{id}  # 删除患者慢性病
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from sqlalchemy.orm import selectinload
from typing import List, Optional
from uuid import UUID

from app.db.database import get_db
from app.core.deps import get_current_active_user
from app.models.models import User, ChronicDisease, PatientChronicCondition
from app.schemas.chronic_disease import (
    ChronicDiseaseResponse,
    ChronicDiseaseListResponse,
    PatientChronicConditionCreate,
    PatientChronicConditionUpdate,
    PatientChronicConditionResponse,
    PatientChronicConditionListResponse,
    DiseaseType
)

router = APIRouter(prefix="/chronic-diseases", tags=["chronic-diseases"])


@router.get("", response_model=ChronicDiseaseListResponse)
async def get_chronic_diseases(
    disease_type: Optional[DiseaseType] = Query(None, description="Filter by disease type"),
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search by name or code"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get list of chronic and special diseases.
    Returns ICD-10 coded diseases for patient selection.
    """
    # Build query
    query = select(ChronicDisease).where(ChronicDisease.is_active == True)
    
    # Apply filters
    if disease_type:
        query = query.where(ChronicDisease.disease_type == disease_type)
    if category:
        query = query.where(ChronicDisease.category == category)
    if search:
        search_filter = f"%{search}%"
        query = query.where(
            (ChronicDisease.icd10_name.ilike(search_filter)) |
            (ChronicDisease.icd10_code.ilike(search_filter)) |
            (ChronicDisease.common_names.any(search))
        )
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Apply pagination
    query = query.order_by(ChronicDisease.icd10_code)
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    diseases = result.scalars().all()
    
    return ChronicDiseaseListResponse(
        items=[ChronicDiseaseResponse.model_validate(d) for d in diseases],
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{disease_id}", response_model=ChronicDiseaseResponse)
async def get_chronic_disease(
    disease_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get details of a specific chronic disease."""
    result = await db.execute(
        select(ChronicDisease).where(
            and_(
                ChronicDisease.id == disease_id,
                ChronicDisease.is_active == True
            )
        )
    )
    disease = result.scalar_one_or_none()
    
    if not disease:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Disease not found"
        )
    
    return ChronicDiseaseResponse.model_validate(disease)


# =============================================================================
# Patient Chronic Disease Management | 患者慢性病管理
# =============================================================================

@router.get("/patients/me/chronic-diseases", response_model=PatientChronicConditionListResponse)
async def get_my_chronic_diseases(
    include_inactive: bool = Query(False, description="Include inactive conditions"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current patient's chronic and special diseases.
    Used in patient profile and AI diagnosis context.
    """
    query = select(PatientChronicCondition).where(
        PatientChronicCondition.patient_id == current_user.id
    ).options(selectinload(PatientChronicCondition.chronic_disease))
    
    if not include_inactive:
        query = query.where(PatientChronicCondition.is_active == True)
    
    query = query.order_by(PatientChronicCondition.created_at.desc())
    
    result = await db.execute(query)
    conditions = result.scalars().all()
    
    # Build response manually to ensure disease data is included
    response_items = []
    for condition in conditions:
        response_items.append(PatientChronicConditionResponse(
            id=condition.id,
            patient_id=condition.patient_id,
            disease_id=condition.disease_id,
            diagnosis_date=condition.diagnosis_date,
            severity=condition.severity,
            notes=condition.notes,
            is_active=condition.is_active,
            disease=ChronicDiseaseResponse.model_validate(condition.chronic_disease) if condition.chronic_disease else None
        ))
    
    return PatientChronicConditionListResponse(
        items=response_items,
        total=len(response_items)
    )


@router.post("/patients/me/chronic-diseases", response_model=PatientChronicConditionResponse, status_code=status.HTTP_201_CREATED)
async def add_chronic_disease_to_profile(
    condition_data: PatientChronicConditionCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Add a chronic/special disease to patient's profile.
    Validates that the disease exists and patient doesn't already have it.
    """
    # Verify user is a patient
    if current_user.role != 'patient':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only patients can manage chronic diseases"
        )
    
    # Check if disease exists
    disease_result = await db.execute(
        select(ChronicDisease).where(
            and_(
                ChronicDisease.id == condition_data.disease_id,
                ChronicDisease.is_active == True
            )
        )
    )
    disease = disease_result.scalar_one_or_none()
    
    if not disease:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Disease not found"
        )
    
    # Check if patient already has this disease (active only)
    existing_result = await db.execute(
        select(PatientChronicCondition).where(
            and_(
                PatientChronicCondition.patient_id == current_user.id,
                PatientChronicCondition.disease_id == condition_data.disease_id,
                PatientChronicCondition.is_active == True
            )
        )
    )
    if existing_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Patient already has this disease in their profile"
        )
    
    # Check if there's an inactive record for this disease (reactivate it)
    inactive_result = await db.execute(
        select(PatientChronicCondition).where(
            and_(
                PatientChronicCondition.patient_id == current_user.id,
                PatientChronicCondition.disease_id == condition_data.disease_id,
                PatientChronicCondition.is_active == False
            )
        )
    )
    inactive_condition = inactive_result.scalar_one_or_none()
    
    if inactive_condition:
        # Reactivate the existing record
        inactive_condition.is_active = True
        inactive_condition.diagnosis_date = condition_data.diagnosis_date
        inactive_condition.severity = condition_data.severity
        inactive_condition.notes = condition_data.notes
        await db.commit()
        await db.refresh(inactive_condition)
        
        # Explicitly load the disease relationship
        result = await db.execute(
            select(PatientChronicCondition)
            .where(PatientChronicCondition.id == inactive_condition.id)
            .options(selectinload(PatientChronicCondition.chronic_disease))
        )
        condition_with_disease = result.scalar_one()
        
        # Build response manually
        return PatientChronicConditionResponse(
            id=condition_with_disease.id,
            patient_id=condition_with_disease.patient_id,
            disease_id=condition_with_disease.disease_id,
            diagnosis_date=condition_with_disease.diagnosis_date,
            severity=condition_with_disease.severity,
            notes=condition_with_disease.notes,
            is_active=condition_with_disease.is_active,
            disease=ChronicDiseaseResponse.model_validate(condition_with_disease.chronic_disease) if condition_with_disease.chronic_disease else None
        )
    
    # Create new condition
    new_condition = PatientChronicCondition(
        patient_id=current_user.id,
        disease_id=condition_data.disease_id,
        diagnosis_date=condition_data.diagnosis_date,
        severity=condition_data.severity,
        notes=condition_data.notes,
        is_active=True
    )
    
    db.add(new_condition)
    await db.commit()
    await db.refresh(new_condition)
    
    # Explicitly load the disease relationship
    result = await db.execute(
        select(PatientChronicCondition)
        .where(PatientChronicCondition.id == new_condition.id)
        .options(selectinload(PatientChronicCondition.chronic_disease))
    )
    new_condition_with_disease = result.scalar_one()
    
    # Build response manually
    return PatientChronicConditionResponse(
        id=new_condition_with_disease.id,
        patient_id=new_condition_with_disease.patient_id,
        disease_id=new_condition_with_disease.disease_id,
        diagnosis_date=new_condition_with_disease.diagnosis_date,
        severity=new_condition_with_disease.severity,
        notes=new_condition_with_disease.notes,
        is_active=new_condition_with_disease.is_active,
        disease=ChronicDiseaseResponse.model_validate(new_condition_with_disease.chronic_disease) if new_condition_with_disease.chronic_disease else None
    )


@router.put("/patients/me/chronic-diseases/{condition_id}", response_model=PatientChronicConditionResponse)
async def update_chronic_disease_condition(
    condition_id: UUID,
    condition_data: PatientChronicConditionUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update patient's chronic disease information."""
    # Find the condition
    result = await db.execute(
        select(PatientChronicCondition).where(
            and_(
                PatientChronicCondition.id == condition_id,
                PatientChronicCondition.patient_id == current_user.id
            )
        )
    )
    condition = result.scalar_one_or_none()
    
    if not condition:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Condition not found"
        )
    
    # Update fields
    if condition_data.diagnosis_date is not None:
        condition.diagnosis_date = condition_data.diagnosis_date
    if condition_data.severity is not None:
        condition.severity = condition_data.severity
    if condition_data.notes is not None:
        condition.notes = condition_data.notes
    if condition_data.is_active is not None:
        condition.is_active = condition_data.is_active
    
    await db.commit()
    await db.refresh(condition)
    
    # Explicitly load the disease relationship
    result = await db.execute(
        select(PatientChronicCondition)
        .where(PatientChronicCondition.id == condition.id)
        .options(selectinload(PatientChronicCondition.chronic_disease))
    )
    condition_with_disease = result.scalar_one()
    
    # Build response manually
    return PatientChronicConditionResponse(
        id=condition_with_disease.id,
        patient_id=condition_with_disease.patient_id,
        disease_id=condition_with_disease.disease_id,
        diagnosis_date=condition_with_disease.diagnosis_date,
        severity=condition_with_disease.severity,
        notes=condition_with_disease.notes,
        is_active=condition_with_disease.is_active,
        disease=ChronicDiseaseResponse.model_validate(condition_with_disease.chronic_disease) if condition_with_disease.chronic_disease else None
    )


@router.delete("/patients/me/chronic-diseases/{condition_id}")
async def remove_chronic_disease_from_profile(
    condition_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Remove a chronic disease from patient's profile (soft delete by setting inactive)."""
    result = await db.execute(
        select(PatientChronicCondition).where(
            and_(
                PatientChronicCondition.id == condition_id,
                PatientChronicCondition.patient_id == current_user.id
            )
        )
    )
    condition = result.scalar_one_or_none()
    
    if not condition:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Condition not found"
        )
    
    # Soft delete - mark as inactive
    condition.is_active = False
    await db.commit()
    
    return {"message": "Chronic disease removed from profile successfully"}


# =============================================================================
# Doctor View - Get Patient's Chronic Diseases | 医生端查看患者慢性病
# =============================================================================

@router.get("/patients/{patient_id}/chronic-diseases", response_model=PatientChronicConditionListResponse)
async def get_patient_chronic_diseases_for_doctor(
    patient_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get patient's chronic diseases for doctor view.
    Used when viewing shared cases or @mentioned cases.
    """
    # Only doctors can view patient chronic diseases
    if current_user.role != 'doctor':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can view patient chronic diseases"
        )
    
    query = select(PatientChronicCondition).where(
        and_(
            PatientChronicCondition.patient_id == patient_id,
            PatientChronicCondition.is_active == True
        )
    ).options(selectinload(PatientChronicCondition.chronic_disease))

    result = await db.execute(query)
    conditions = result.scalars().all()

    # Build response manually to ensure disease data is included
    response_items = []
    for condition in conditions:
        response_items.append(PatientChronicConditionResponse(
            id=condition.id,
            patient_id=condition.patient_id,
            disease_id=condition.disease_id,
            diagnosis_date=condition.diagnosis_date,
            severity=condition.severity,
            notes=condition.notes,
            is_active=condition.is_active,
            disease=ChronicDiseaseResponse.model_validate(condition.chronic_disease) if condition.chronic_disease else None
        ))

    return PatientChronicConditionListResponse(
        items=response_items,
        total=len(response_items)
    )
