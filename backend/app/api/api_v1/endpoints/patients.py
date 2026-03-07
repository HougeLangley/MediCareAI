from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from typing import List
from uuid import UUID
from app.db.database import get_db
from app.schemas.patient import (
    PatientCreate,
    PatientUpdate,
    PatientResponse,
    PatientSummary,
)
from app.services.patient_service import PatientService
from app.core.deps import get_current_active_user
from app.models.models import User, PatientChronicCondition, ChronicDisease
from app.schemas.chronic_disease import (
    ChronicDiseaseResponse,
    PatientChronicConditionCreate,
    PatientChronicConditionUpdate,
    PatientChronicConditionResponse,
    PatientChronicConditionListResponse,
)
import uuid
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


def _enrich_patient_response(patient, user: User) -> dict:
    """从 User 表获取信息并填充到患者响应中，避免数据冗余"""
    patient_dict = {
        "id": patient.id,
        "user_id": patient.user_id,
        "user_full_name": user.full_name,  # 从 User 表获取
        "name": user.full_name,  # 兼容旧字段
        "date_of_birth": patient.date_of_birth,
        "gender": patient.gender,
        "phone": patient.phone,
        # 地址统一从 User 表获取（问题4修复：消除数据冗余）
        "address": user.address,
        # 紧急联系人信息从 User 表获取
        "emergency_contact": user.emergency_contact,
        "emergency_contact_name": user.emergency_contact_name,
        "emergency_contact_phone": user.emergency_contact_phone,
        "medical_record_number": patient.medical_record_number,
        "notes": patient.notes,
        "created_at": patient.created_at,
        "updated_at": patient.updated_at,
    }
    return patient_dict


@router.get("/me", response_model=PatientResponse)
async def get_my_patient(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> PatientResponse:
    """获取当前用户的患者信息（主档案）
    
    如果没有患者档案，自动创建一个空档案"""
    import traceback
    
    patient_service = PatientService(db)
    patients = await patient_service.get_patients_by_user(
        current_user.id, skip=0, limit=1
    )
    
    if not patients:
        # 自动创建空的患者档案
        logger.info(f"用户 {current_user.id} 没有患者档案，自动创建")
        from app.schemas.patient import PatientCreate
        empty_patient_data = PatientCreate()
        try:
            new_patient = await patient_service.create_patient(
                patient_data=empty_patient_data, user_id=current_user.id
            )
            await db.refresh(new_patient)
            patients = [new_patient]
            logger.info(f"患者档案创建成功: {new_patient.id}")
        except Exception as e:
            error_trace = traceback.format_exc()
            logger.error(f"自动创建患者档案失败: {e}")
            logger.error(f"错误详情: {error_trace}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                detail=f"无法创建患者档案: {str(e)}"
            )
    
    return _enrich_patient_response(patients[0], current_user)
async def get_my_patient(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> PatientResponse:
    """获取当前用户的患者信息（主档案）
    
    如果没有患者档案，自动创建一个空档案"""
    patient_service = PatientService(db)
    patients = await patient_service.get_patients_by_user(
        current_user.id, skip=0, limit=1
    )
    
    if not patients:
        # 自动创建空的患者档案
        logger.info(f"用户 {current_user.id} 没有患者档案，自动创建")
        from app.schemas.patient import PatientCreate
        empty_patient_data = PatientCreate()
        try:
            new_patient = await patient_service.create_patient(
                patient_data=empty_patient_data, user_id=current_user.id
            )
            await db.refresh(new_patient)
            patients = [new_patient]
        except Exception as e:
            logger.error(f"自动创建患者档案失败: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                detail="无法创建患者档案"
            )
    
    return _enrich_patient_response(patients[0], current_user)


@router.put("/me", response_model=PatientResponse)
async def update_my_patient(
    patient_data: PatientUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> PatientResponse:
    """更新当前用户的患者信息（主档案）
    
    注意：地址和紧急联系人信息现在统一存储在 User 表中"""
    patient_service = PatientService(db)
    patients = await patient_service.get_patients_by_user(
        current_user.id, skip=0, limit=1
    )
    if not patients:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Patient profile not found"
        )
    
    # 问题4修复：如果提供了地址，同时更新 User 表的地址
    if patient_data.address is not None:
        current_user.address = patient_data.address
    
    # 问题1修复：如果提供了紧急联系人，拆分为 name 和 phone 保存到 User 表
    if patient_data.emergency_contact is not None:
        # 解析 emergency_contact 格式: "姓名 电话" 或 "姓名" 或 "电话"
        parts = patient_data.emergency_contact.strip().split()
        if len(parts) >= 2:
            # 假设最后一部分是电话，前面是姓名
            current_user.emergency_contact_phone = parts[-1]
            current_user.emergency_contact_name = " ".join(parts[:-1])
        elif len(parts) == 1:
            # 只有一个部分，判断是电话还是姓名
            if parts[0].isdigit() or parts[0].startswith('1') and len(parts[0]) == 11:
                # 可能是电话号码
                current_user.emergency_contact_phone = parts[0]
            else:
                # 可能是姓名
                current_user.emergency_contact_name = parts[0]
        else:
            # 空字符串，清空字段
            current_user.emergency_contact_name = None
            current_user.emergency_contact_phone = None
    
    # 提交 User 表的更改
    await db.commit()
    
    patient = await patient_service.update_patient(
        patients[0].id, patient_data, current_user.id
    )
    
    # 刷新 user 对象以获取最新数据
    await db.refresh(current_user)
    
    return _enrich_patient_response(patient, current_user)


@router.get("/", response_model=List[PatientResponse])
async def get_patients(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    patient_service = PatientService(db)
    patients = await patient_service.get_patients_by_user(current_user.id, skip, limit)
    # 从 User 表获取姓名填充响应
    return [_enrich_patient_response(p, current_user) for p in patients]


@router.get("/count")
async def get_patients_count(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    patient_service = PatientService(db)
    count = await patient_service.count_patients_by_user(current_user.id)
    return {"count": count}


@router.post("/", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
async def create_patient(
    patient_data: PatientCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> PatientResponse:
    """创建患者档案
    
    注意：地址和紧急联系人信息统一存储在 User 表中"""
    patient_service = PatientService(db)
    
    # 问题4修复：如果提供了地址，更新 User 表
    if patient_data.address is not None:
        current_user.address = patient_data.address
    
    # 问题1修复：如果提供了紧急联系人，拆分为 name 和 phone 保存到 User 表
    if patient_data.emergency_contact is not None:
        parts = patient_data.emergency_contact.strip().split()
        if len(parts) >= 2:
            current_user.emergency_contact_phone = parts[-1]
            current_user.emergency_contact_name = " ".join(parts[:-1])
        elif len(parts) == 1:
            if parts[0].isdigit() or (parts[0].startswith('1') and len(parts[0]) == 11):
                current_user.emergency_contact_phone = parts[0]
            else:
                current_user.emergency_contact_name = parts[0]
        else:
            current_user.emergency_contact_name = None
            current_user.emergency_contact_phone = None
    
    await db.commit()
    
    patient = await patient_service.create_patient(patient_data, current_user.id)
    
    await db.refresh(current_user)
    
    return _enrich_patient_response(patient, current_user)


@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(
    patient_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> PatientResponse:
    patient_service = PatientService(db)
    patient = await patient_service.get_patient_by_id(patient_id, current_user.id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found"
        )
    return _enrich_patient_response(patient, current_user)


@router.put("/{patient_id}", response_model=PatientResponse)
async def update_patient(
    patient_id: uuid.UUID,
    patient_data: PatientUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> PatientResponse:
    """更新指定患者信息
    
    注意：地址和紧急联系人信息现在统一存储在 User 表中"""
    patient_service = PatientService(db)
    
    # 问题4修复：如果提供了地址，更新 User 表
    if patient_data.address is not None:
        current_user.address = patient_data.address
    
    # 问题1修复：如果提供了紧急联系人，拆分为 name 和 phone 保存到 User 表
    if patient_data.emergency_contact is not None:
        parts = patient_data.emergency_contact.strip().split()
        if len(parts) >= 2:
            current_user.emergency_contact_phone = parts[-1]
            current_user.emergency_contact_name = " ".join(parts[:-1])
        elif len(parts) == 1:
            if parts[0].isdigit() or (parts[0].startswith('1') and len(parts[0]) == 11):
                current_user.emergency_contact_phone = parts[0]
            else:
                current_user.emergency_contact_name = parts[0]
        else:
            current_user.emergency_contact_name = None
            current_user.emergency_contact_phone = None
    
    # 提交 User 表的更改
    await db.commit()
    
    patient = await patient_service.update_patient(
        patient_id, patient_data, current_user.id
    )
    
    await db.refresh(current_user)
    
    return _enrich_patient_response(patient, current_user)


@router.delete("/{patient_id}")
async def delete_patient(
    patient_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    patient_service = PatientService(db)
    await patient_service.delete_patient(patient_id, current_user.id)
    return {"message": "Patient deleted successfully"}


@router.get("/me/chronic-diseases", response_model=PatientChronicConditionListResponse)
async def get_my_chronic_diseases(
    include_inactive: bool = Query(False, description="Include inactive conditions"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get current patient's chronic and special diseases.
    Used in patient profile and AI diagnosis context.
    """
    query = (
        select(PatientChronicCondition)
        .where(PatientChronicCondition.patient_id == current_user.id)
        .options(selectinload(PatientChronicCondition.chronic_disease))
    )

    if not include_inactive:
        query = query.where(PatientChronicCondition.is_active == True)

    query = query.order_by(PatientChronicCondition.created_at.desc())

    result = await db.execute(query)
    conditions = result.scalars().all()

    # Build response with disease data included
    response_items = []
    for condition in conditions:
        disease_data = None
        if condition.chronic_disease:
            disease_data = ChronicDiseaseResponse(
                id=condition.chronic_disease.id,
                icd10_code=condition.chronic_disease.icd10_code,
                icd10_name=condition.chronic_disease.icd10_name,
                disease_type=condition.chronic_disease.disease_type,
                common_names=condition.chronic_disease.common_names,
                category=condition.chronic_disease.category,
                description=condition.chronic_disease.description,
                medical_notes=condition.chronic_disease.medical_notes,
                is_active=condition.chronic_disease.is_active,
                created_at=condition.chronic_disease.created_at,
                updated_at=condition.chronic_disease.updated_at,
            )

        response_items.append(
            PatientChronicConditionResponse(
                id=condition.id,
                patient_id=condition.patient_id,
                disease_id=condition.disease_id,
                diagnosis_date=condition.diagnosis_date,
                severity=condition.severity,
                notes=condition.notes,
                is_active=condition.is_active,
                created_at=condition.created_at,
                updated_at=condition.updated_at,
                disease=disease_data,
            )
        )

    return PatientChronicConditionListResponse(
        items=response_items, total=len(response_items)
    )


@router.post(
    "/me/chronic-diseases",
    response_model=PatientChronicConditionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_my_chronic_disease(
    condition_data: PatientChronicConditionCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Add a chronic/special disease to current patient's profile."""
    # Check if disease exists
    disease_result = await db.execute(
        select(ChronicDisease).where(
            and_(
                ChronicDisease.id == condition_data.disease_id,
                ChronicDisease.is_active == True,
            )
        )
    )
    disease = disease_result.scalar_one_or_none()

    if not disease:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Disease not found"
        )

    # Check if patient already has this disease (active only)
    existing_result = await db.execute(
        select(PatientChronicCondition).where(
            and_(
                PatientChronicCondition.patient_id == current_user.id,
                PatientChronicCondition.disease_id == condition_data.disease_id,
                PatientChronicCondition.is_active == True,
            )
        )
    )
    if existing_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Patient already has this disease in their profile",
        )

    # Check if there's an inactive record for this disease (reactivate it)
    inactive_result = await db.execute(
        select(PatientChronicCondition).where(
            and_(
                PatientChronicCondition.patient_id == current_user.id,
                PatientChronicCondition.disease_id == condition_data.disease_id,
                PatientChronicCondition.is_active == False,
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

        return PatientChronicConditionResponse(
            id=inactive_condition.id,
            patient_id=inactive_condition.patient_id,
            disease_id=inactive_condition.disease_id,
            diagnosis_date=inactive_condition.diagnosis_date,
            severity=inactive_condition.severity,
            notes=inactive_condition.notes,
            is_active=inactive_condition.is_active,
            created_at=inactive_condition.created_at,
            updated_at=inactive_condition.updated_at,
        )

    # Create new condition
    new_condition = PatientChronicCondition(
        patient_id=current_user.id,
        disease_id=condition_data.disease_id,
        diagnosis_date=condition_data.diagnosis_date,
        severity=condition_data.severity,
        notes=condition_data.notes,
        is_active=True,
    )

    db.add(new_condition)
    await db.commit()
    await db.refresh(new_condition)

    return PatientChronicConditionResponse(
        id=new_condition.id,
        patient_id=new_condition.patient_id,
        disease_id=new_condition.disease_id,
        diagnosis_date=new_condition.diagnosis_date,
        severity=new_condition.severity,
        notes=new_condition.notes,
        is_active=new_condition.is_active,
        created_at=new_condition.created_at,
        updated_at=new_condition.updated_at,
    )


@router.put(
    "/me/chronic-diseases/{condition_id}",
    response_model=PatientChronicConditionResponse,
)
async def update_my_chronic_disease(
    condition_id: UUID,
    condition_data: PatientChronicConditionUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Update patient's chronic disease information."""
    result = await db.execute(
        select(PatientChronicCondition).where(
            and_(
                PatientChronicCondition.id == condition_id,
                PatientChronicCondition.patient_id == current_user.id,
            )
        )
    )
    condition = result.scalar_one_or_none()

    if not condition:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chronic disease condition not found",
        )

    # Update fields
    for field, value in condition_data.model_dump(exclude_unset=True).items():
        setattr(condition, field, value)

    await db.commit()
    await db.refresh(condition)

    return PatientChronicConditionResponse(
        id=condition.id,
        patient_id=condition.patient_id,
        disease_id=condition.disease_id,
        diagnosis_date=condition.diagnosis_date,
        severity=condition.severity,
        notes=condition.notes,
        is_active=condition.is_active,
        created_at=condition.created_at,
        updated_at=condition.updated_at,
    )


@router.delete("/me/chronic-diseases/{condition_id}")
async def delete_my_chronic_disease(
    condition_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete (deactivate) patient's chronic disease."""
    result = await db.execute(
        select(PatientChronicCondition).where(
            and_(
                PatientChronicCondition.id == condition_id,
                PatientChronicCondition.patient_id == current_user.id,
            )
        )
    )
    condition = result.scalar_one_or_none()

    if not condition:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chronic disease condition not found",
        )

    # Soft delete - just mark as inactive
    condition.is_active = False
    await db.commit()

    return {"message": "Chronic disease removed from profile"}
