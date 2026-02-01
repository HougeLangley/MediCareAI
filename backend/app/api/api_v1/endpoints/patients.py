from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.db.database import get_db
from app.schemas.patient import PatientCreate, PatientUpdate, PatientResponse, PatientSummary
from app.services.patient_service import PatientService
from app.core.deps import get_current_active_user
from app.models.models import User
import uuid

router = APIRouter()


def _enrich_patient_response(patient, user: User) -> dict:
    """从 User 表获取姓名并填充到患者响应中，避免数据冗余"""
    patient_dict = {
        "id": patient.id,
        "user_id": patient.user_id,
        "user_full_name": user.full_name,  # 从 User 表获取
        "name": user.full_name,  # 兼容旧字段
        "date_of_birth": patient.date_of_birth,
        "gender": patient.gender,
        "phone": patient.phone,
        "address": patient.address,
        "emergency_contact": patient.emergency_contact,
        "medical_record_number": patient.medical_record_number,
        "notes": patient.notes,
        "created_at": patient.created_at,
        "updated_at": patient.updated_at
    }
    return patient_dict


@router.get("/me", response_model=PatientResponse)
async def get_my_patient(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> PatientResponse:
    """获取当前用户的患者信息（主档案）"""
    patient_service = PatientService(db)
    patients = await patient_service.get_patients_by_user(current_user.id, skip=0, limit=1)
    if not patients:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient profile not found"
        )
    return _enrich_patient_response(patients[0], current_user)


@router.put("/me", response_model=PatientResponse)
async def update_my_patient(
    patient_data: PatientUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> PatientResponse:
    """更新当前用户的患者信息（主档案）"""
    patient_service = PatientService(db)
    patients = await patient_service.get_patients_by_user(current_user.id, skip=0, limit=1)
    if not patients:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient profile not found"
        )
    patient = await patient_service.update_patient(patients[0].id, patient_data, current_user.id)
    return _enrich_patient_response(patient, current_user)


@router.get("/", response_model=List[PatientResponse])
async def get_patients(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    patient_service = PatientService(db)
    patients = await patient_service.get_patients_by_user(current_user.id, skip, limit)
    # 从 User 表获取姓名填充响应
    return [_enrich_patient_response(p, current_user) for p in patients]


@router.get("/count")
async def get_patients_count(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> dict:
    patient_service = PatientService(db)
    count = await patient_service.count_patients_by_user(current_user.id)
    return {"count": count}


@router.post("/", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
async def create_patient(
    patient_data: PatientCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> PatientResponse:
    patient_service = PatientService(db)
    patient = await patient_service.create_patient(patient_data, current_user.id)
    return _enrich_patient_response(patient, current_user)


@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(
    patient_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> PatientResponse:
    patient_service = PatientService(db)
    patient = await patient_service.get_patient_by_id(patient_id, current_user.id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    return _enrich_patient_response(patient, current_user)


@router.put("/{patient_id}", response_model=PatientResponse)
async def update_patient(
    patient_id: uuid.UUID,
    patient_data: PatientUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> PatientResponse:
    patient_service = PatientService(db)
    patient = await patient_service.update_patient(patient_id, patient_data, current_user.id)
    return _enrich_patient_response(patient, current_user)


@router.delete("/{patient_id}")
async def delete_patient(
    patient_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> dict:
    patient_service = PatientService(db)
    await patient_service.delete_patient(patient_id, current_user.id)
    return {"message": "Patient deleted successfully"}
