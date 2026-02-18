"""
Initialize Chronic Diseases Data | 初始化慢性病与特殊病数据

Usage:
    cd backend
    python -m app.db.init_chronic_diseases
"""

import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import async_session_maker
from app.models.models import ChronicDisease
from app.db.chronic_disease_data import ALL_CHRONIC_DISEASES


async def init_chronic_diseases(db: AsyncSession):
    """Initialize chronic diseases in database"""
    
    print("Initializing chronic diseases data...")
    
    # Check if data already exists
    result = await db.execute(select(ChronicDisease).limit(1))
    if result.scalar_one_or_none():
        print("Chronic diseases already initialized. Skipping.")
        return
    
    # Add all diseases
    count = 0
    for disease_data in ALL_CHRONIC_DISEASES:
        disease = ChronicDisease(
            icd10_code=disease_data["icd10_code"],
            icd10_name=disease_data["icd10_name"],
            disease_type=disease_data["disease_type"],
            common_names=disease_data.get("common_names"),
            category=disease_data.get("category"),
            description=disease_data.get("description"),
            medical_notes=disease_data.get("medical_notes"),
            is_active=True
        )
        db.add(disease)
        count += 1
    
    await db.commit()
    print(f"✅ Successfully initialized {count} chronic/special diseases")


async def main():
    """Main function"""
    async with async_session_maker() as db:
        await init_chronic_diseases(db)


if __name__ == "__main__":
    asyncio.run(main())
