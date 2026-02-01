from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.models.models import Patient, MedicalCase
from app.schemas.patient import PatientCreate, PatientUpdate
from datetime import datetime
import uuid


class PatientService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_patient_by_id(self, patient_id: uuid.UUID, user_id: uuid.UUID) -> Patient | None:
        stmt = select(Patient).where(Patient.id == patient_id, Patient.user_id == user_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_patients_by_user(
        self, 
        user_id: uuid.UUID, 
        skip: int = 0, 
        limit: int = 20
    ) -> list[Patient]:
        stmt = (
            select(Patient)
            .where(Patient.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .order_by(Patient.created_at.desc())
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def count_patients_by_user(self, user_id: uuid.UUID) -> int:
        stmt = select(func.count(Patient.id)).where(Patient.user_id == user_id)
        result = await self.db.execute(stmt)
        return result.scalar()

    async def create_patient(self, patient_data: PatientCreate, user_id: uuid.UUID) -> Patient:
        # 检查病历号是否已存在
        if patient_data.medical_record_number:
            stmt = select(Patient).where(Patient.medical_record_number == patient_data.medical_record_number)
            result = await self.db.execute(stmt)
            if result.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Medical record number already exists"
                )

        # 注意：name 字段现在从 User 表获取，不在 Patient 表中存储
        # 这里保留 name 字段用于向后兼容，但设置为空
        db_patient = Patient(
            user_id=user_id,
            name=None,  # 从 User 表动态获取，避免数据冗余
            date_of_birth=patient_data.date_of_birth,  # 直接使用 date 对象
            gender=patient_data.gender,
            phone=patient_data.phone,
            address=patient_data.address,
            emergency_contact=patient_data.emergency_contact,
            medical_record_number=patient_data.medical_record_number
        )

        try:
            self.db.add(db_patient)
            await self.db.commit()
            await self.db.refresh(db_patient)
            return db_patient
        except IntegrityError:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Error creating patient"
            )

    async def update_patient(
        self, 
        patient_id: uuid.UUID, 
        patient_data: PatientUpdate, 
        user_id: uuid.UUID
    ) -> Patient:
        patient = await self.get_patient_by_id(patient_id, user_id)
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found"
            )

        # 检查病历号是否已被其他患者使用
        if patient_data.medical_record_number and patient_data.medical_record_number != patient.medical_record_number:
            stmt = select(Patient).where(
                Patient.medical_record_number == patient_data.medical_record_number,
                Patient.id != patient_id
            )
            result = await self.db.execute(stmt)
            if result.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Medical record number already exists"
                )

        update_data = patient_data.model_dump(exclude_unset=True)
        # date_of_birth 已经是 date 对象，不需要转换

        for field, value in update_data.items():
            setattr(patient, field, value)

        try:
            await self.db.commit()
            await self.db.refresh(patient)
            return patient
        except IntegrityError:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Error updating patient"
            )

    async def delete_patient(self, patient_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        patient = await self.get_patient_by_id(patient_id, user_id)
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found"
            )

        # 检查是否有关联的病例
        stmt = select(func.count(MedicalCase.id)).where(MedicalCase.patient_id == patient_id)
        result = await self.db.execute(stmt)
        cases_count = result.scalar()
        
        if cases_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete patient with {cases_count} associated medical cases"
            )

        try:
            await self.db.delete(patient)
            await self.db.commit()
            return True
        except Exception:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error deleting patient"
            )