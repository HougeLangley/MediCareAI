from fastapi import APIRouter
from app.api.api_v1.endpoints import auth, patients, documents, ai, medical_cases
from app.services.knowledge_base_service import router as knowledge_router

api_router = APIRouter()

# 认证路由
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])

# 患者管理路由
api_router.include_router(patients.router, prefix="/patients", tags=["patients"])

# 病历记录路由
api_router.include_router(medical_cases.router, prefix="/medical-cases", tags=["medical-cases"])

# 文档管理路由
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])

# AI 诊断路由
api_router.include_router(ai.router, prefix="/ai", tags=["ai-diagnostics"])

# 知识库管理路由
api_router.include_router(knowledge_router, prefix="/knowledge", tags=["knowledge-bases"])