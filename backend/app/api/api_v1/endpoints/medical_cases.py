"""
病历记录 API 端点
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import uuid
from app.db.database import get_db
from app.core.deps import get_current_active_user
from app.models.models import User
from app.services.medical_case_service import MedicalCaseService
from app.services.patient_service import PatientService
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()


class MedicalCaseResponse(BaseModel):
    """病历响应模型"""
    id: uuid.UUID
    patient_id: uuid.UUID
    title: str
    description: str
    symptoms: str
    diagnosis: str
    severity: str
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


@router.get("/", response_model=List[MedicalCaseResponse])
async def get_my_medical_cases(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取当前用户的所有病历记录
    """
    try:
        # 先获取患者信息
        patient_service = PatientService(db)
        patients = await patient_service.get_patients_by_user(current_user.id, skip=0, limit=1)
        
        if not patients:
            return []  # 如果没有患者记录，返回空列表
        
        patient = patients[0]
        
        # 获取病历记录
        case_service = MedicalCaseService(db)
        cases = await case_service.get_medical_cases_by_patient(patient.id, skip, limit)
        
        return cases
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取病历记录失败: {str(e)}"
        )


@router.get("/count")
async def get_medical_case_count(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    获取病历记录数量统计
    """
    try:
        # 先获取患者信息
        patient_service = PatientService(db)
        patients = await patient_service.get_patients_by_user(current_user.id, skip=0, limit=1)
        
        if not patients:
            return {"total": 0, "active": 0, "completed": 0}
        
        patient = patients[0]
        
        # 获取病历数量
        case_service = MedicalCaseService(db)
        total = await case_service.count_medical_cases_by_patient(patient.id)
        
        return {
            "total": total,
            "active": total,  # 简化处理，后续可按状态统计
            "completed": 0
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取病历统计失败: {str(e)}"
        )


@router.get("/{case_id}", response_model=MedicalCaseResponse)
async def get_medical_case_detail(
    case_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取单个病历详情
    """
    try:
        # 先获取患者信息
        patient_service = PatientService(db)
        patients = await patient_service.get_patients_by_user(current_user.id, skip=0, limit=1)
        
        if not patients:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="患者记录不存在"
            )
        
        patient = patients[0]
        
        # 获取病历详情
        case_service = MedicalCaseService(db)
        case = await case_service.get_medical_case_by_id(case_id, patient.id)
        
        if not case:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="病历记录不存在"
            )
        
        return case
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取病历详情失败: {str(e)}"
        )
