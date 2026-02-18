"""
Chronic Disease Schemas | 慢性病与特殊病数据模型
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import date, datetime
from uuid import UUID
from enum import Enum


class DiseaseType(str, Enum):
    """疾病类型枚举"""
    CHRONIC = "chronic"
    SPECIAL = "special"
    BOTH = "both"


class ConditionSeverity(str, Enum):
    """病情严重程度枚举"""
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"


class ChronicDiseaseBase(BaseModel):
    """慢性病基础模型"""
    icd10_code: str = Field(..., description="ICD-10编码")
    icd10_name: str = Field(..., description="ICD-10官方名称")
    disease_type: DiseaseType = Field(..., description="疾病类型：慢性病/特殊病/两者")
    category: Optional[str] = Field(None, description="疾病分类")
    description: Optional[str] = Field(None, description="疾病描述")
    medical_notes: Optional[str] = Field(None, description="AI诊断医疗注意事项")


class ChronicDiseaseCreate(ChronicDiseaseBase):
    """创建慢性病请求"""
    common_names: Optional[List[str]] = Field(None, description="常用别名列表")


class ChronicDiseaseUpdate(BaseModel):
    """更新慢性病请求"""
    icd10_name: Optional[str] = None
    disease_type: Optional[DiseaseType] = None
    common_names: Optional[List[str]] = None
    category: Optional[str] = None
    description: Optional[str] = None
    medical_notes: Optional[str] = None
    is_active: Optional[bool] = None


class ChronicDiseaseResponse(ChronicDiseaseBase):
    """慢性病响应模型"""
    id: UUID
    common_names: Optional[List[str]] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ChronicDiseaseListResponse(BaseModel):
    """慢性病列表响应"""
    items: List[ChronicDiseaseResponse]
    total: int
    page: int
    page_size: int


class PatientChronicConditionBase(BaseModel):
    """患者慢性病关联基础模型"""
    diagnosis_date: Optional[date] = Field(None, description="确诊日期")
    severity: Optional[ConditionSeverity] = Field(None, description="病情严重程度")
    notes: Optional[str] = Field(None, description="患者备注")


class PatientChronicConditionCreate(PatientChronicConditionBase):
    """创建患者慢性病关联请求"""
    disease_id: UUID = Field(..., description="慢性病ID")


class PatientChronicConditionUpdate(PatientChronicConditionBase):
    """更新患者慢性病关联请求"""
    is_active: Optional[bool] = Field(None, description="是否活跃")


class PatientChronicConditionResponse(PatientChronicConditionBase):
    """患者慢性病关联响应模型"""
    id: UUID
    patient_id: UUID
    disease_id: UUID
    disease: Optional[ChronicDiseaseResponse] = None
    is_active: bool

    class Config:
        from_attributes = True

    @field_validator('disease', mode='before')
    @classmethod
    def extract_disease(cls, v):
        if v is None:
            return None
        # Handle both ChronicDisease object and dict
        if hasattr(v, 'id'):
            return v
        return v


class PatientChronicConditionListResponse(BaseModel):
    """患者慢性病列表响应"""
    items: List[PatientChronicConditionResponse]
    total: int


class PatientChronicDiseaseSummary(BaseModel):
    """患者慢性病摘要（用于病例显示）"""
    id: UUID
    icd10_code: str
    icd10_name: str
    disease_type: DiseaseType
    severity: Optional[ConditionSeverity]
    is_active: bool

    class Config:
        from_attributes = True
