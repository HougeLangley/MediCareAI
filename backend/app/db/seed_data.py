"""
Seed database with initial data
"""
import asyncio
from sqlalchemy import select
from app.db.database import AsyncSessionLocal, engine
from app.models.models import Disease, Patient, MedicalCase, User
from datetime import datetime
import json

async def seed_data():
    """Seed database with initial data"""
    async with AsyncSessionLocal() as db:
        # Check if disease already exists
        result = await db.execute(
            select(Disease).where(Disease.code == "ASTHMA_PED")
        )
        existing_disease = result.scalar_one_or_none()

        if existing_disease:
            print("Disease already exists, skipping...")
            return

        # Create pediatric bronchial asthma disease
        import os
        json_path = '/app/pediatric_bronchial_asthma/pediatric_asthma_guideline.json'
        if not os.path.exists(json_path):
            print(f"Warning: Guideline file not found at {json_path}")
            guideline_data = {}
        else:
            with open(json_path, 'r', encoding='utf-8') as f:
                guideline_data = json.load(f)

        disease = Disease(
            name="儿童支气管哮喘",
            code="ASTHMA_PED",
            description="儿童支气管哮喘是一种常见的慢性呼吸道疾病，需要长期管理和规范治疗。",
            guidelines_json=guideline_data,
            is_active=True
        )
        db.add(disease)

        # Get admin user
        result = await db.execute(
            select(User).where(User.email == "admin@medicare.ai")
        )
        admin_user = result.scalar_one_or_none()

        if admin_user:
            # Create a sample patient
            patient = Patient(
                user_id=admin_user.id,
                name="张小明",
                date_of_birth="2015-05-20",
                gender="male",
                phone="13800138000",
                address="北京市朝阳区XX路XX号",
                emergency_contact="张大山（父亲）13900139000",
                medical_record_number="MED202401001"
            )
            db.add(patient)
            await db.flush()

            # Create a medical case for the patient
            medical_case = MedicalCase(
                patient_id=patient.id,
                disease_id=disease.id,
                title="儿童支气管哮喘 - 初诊",
                description="患者因反复咳嗽、喘息就诊，诊断为儿童支气管哮喘",
                symptoms="反复咳嗽，夜间加重，运动后喘息",
                severity="moderate",
                status="active"
            )
            db.add(medical_case)

        await db.commit()
        print("Database seeded successfully!")

if __name__ == "__main__":
    asyncio.run(seed_data())
