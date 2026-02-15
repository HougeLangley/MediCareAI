#!/usr/bin/env python3
"""
初始化数据库表
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.db.database import Base
from app.core.config import settings

# Import all models to register them with Base.metadata
# 导入所有模型以确保 SQLAlchemy 能正确创建所有表
from app.models.models import (
    User, Disease, MedicalCase, MedicalDocument, AIFeedback,
    FollowUp, UserSession, AuditLog, DataSharingConsent,
    SharedMedicalCase, DoctorPatientRelation, KnowledgeBaseChunk,
    VectorEmbeddingConfig, SystemResourceLog, DoctorCaseComment,
    CaseCommentReply, CaseKnowledgeMatch, AIDiagnosisLog,
    AdminOperationLog, DoctorVerification, Patient
)
from app.models.ai_model_config import AIModelConfiguration

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def init_db():
    """初始化数据库表"""
    engine = create_async_engine(
        settings.database_url,
        echo=settings.debug,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    logger.info("数据库表创建成功")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(init_db())
