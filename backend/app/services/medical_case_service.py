"""
病历服务 - 管理诊疗记录
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional, Dict, Any
from app.models.models import MedicalCase, Patient, Disease
import uuid


class MedicalCaseService:
    """病历服务类"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_medical_case(
        self,
        patient_id: uuid.UUID,
        title: str,
        symptoms: str,
        diagnosis: str,
        severity: str = "moderate",
        description: str = None,
        disease_id: uuid.UUID = None
    ) -> MedicalCase:
        """
        创建病历记录
        
        Args:
            patient_id: 患者ID
            title: 病历标题
            symptoms: 症状描述
            diagnosis: 诊断结果
            severity: 严重程度
            description: 详细描述
            disease_id: 疾病ID（可选）
            
        Returns:
            创建的病历记录
        """
        # 如果没有提供疾病ID，查询或创建默认疾病
        if not disease_id:
            stmt = select(Disease).limit(1)
            result = await self.db.execute(stmt)
            disease = result.scalar_one_or_none()
            
            if disease:
                disease_id = disease.id
            else:
                # 创建默认疾病记录
                default_disease = Disease(
                    id=uuid.uuid4(),
                    name="未分类疾病",
                    code="UNC",
                    description="默认分类，用于未明确诊断的疾病"
                )
                self.db.add(default_disease)
                await self.db.flush()  # flush但不提交，获取ID
                disease_id = default_disease.id
        
        medical_case = MedicalCase(
            id=uuid.uuid4(),
            patient_id=patient_id,
            disease_id=disease_id,
            title=title,
            description=description or symptoms[:200],  # 如果没有描述，使用症状前200字
            symptoms=symptoms,
            diagnosis=diagnosis,
            severity=severity,
            status='active'
        )
        
        self.db.add(medical_case)
        await self.db.commit()
        await self.db.refresh(medical_case)
        
        return medical_case
    
    async def get_medical_cases_by_patient(
        self,
        patient_id: uuid.UUID,
        skip: int = 0,
        limit: int = 20
    ) -> List[MedicalCase]:
        """
        获取患者的所有病历记录
        
        Args:
            patient_id: 患者ID
            skip: 跳过记录数
            limit: 返回记录数
            
        Returns:
            病历记录列表
        """
        stmt = (
            select(MedicalCase)
            .where(MedicalCase.patient_id == patient_id)
            .order_by(MedicalCase.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def get_medical_case_by_id(
        self,
        case_id: uuid.UUID,
        patient_id: uuid.UUID
    ) -> Optional[MedicalCase]:
        """
        根据ID获取病历记录
        
        Args:
            case_id: 病历ID
            patient_id: 患者ID（用于权限验证）
            
        Returns:
            病历记录或None
        """
        stmt = (
            select(MedicalCase)
            .where(
                MedicalCase.id == case_id,
                MedicalCase.patient_id == patient_id
            )
        )
        
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def count_medical_cases_by_patient(
        self,
        patient_id: uuid.UUID
    ) -> int:
        """
        统计患者的病历数量
        
        Args:
            patient_id: 患者ID
            
        Returns:
            病历数量
        """
        stmt = (
            select(func.count(MedicalCase.id))
            .where(MedicalCase.patient_id == patient_id)
        )
        
        result = await self.db.execute(stmt)
        return result.scalar()
