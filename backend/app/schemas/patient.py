from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime, date
import uuid


class PatientBase(BaseModel):
    """患者基础信息 - name 从 User 表获取，避免数据冗余"""
    date_of_birth: Optional[date] = None
    gender: Optional[str] = Field(None, pattern="^(male|female)$")
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None
    emergency_contact: Optional[str] = Field(None, max_length=255)
    medical_record_number: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None


class PatientCreate(PatientBase):
    """创建患者 - 不需要提供 name，自动从 User 表获取"""
    pass


class PatientUpdate(BaseModel):
    """更新患者信息 - 不允许修改 name，name 应该在 User 表中修改"""
    date_of_birth: Optional[date] = None
    gender: Optional[str] = Field(None, pattern="^(male|female)$")
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None
    emergency_contact: Optional[str] = Field(None, max_length=255)
    medical_record_number: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None


class PatientResponse(BaseModel):
    """患者响应 - 包含从 User 表获取的 user_full_name"""
    id: uuid.UUID
    user_id: uuid.UUID
    # 从 User 表获取的姓名，避免数据冗余
    user_full_name: Optional[str] = None
    # 兼容旧字段
    name: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    emergency_contact: Optional[str] = None
    medical_record_number: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PatientSummary(BaseModel):
    """患者摘要"""
    id: uuid.UUID
    # 从 User 表获取的姓名
    user_full_name: Optional[str] = None
    name: Optional[str] = None  # 兼容旧字段
    date_of_birth: Optional[date] = None
    gender: Optional[str]
    medical_record_number: Optional[str]
    active_cases_count: int = 0
    
    class Config:
        from_attributes = True
