from fastapi import APIRouter
from app.api.api_v1.endpoints import auth, patients, documents, ai, medical_cases, vector_embedding, data_sharing, sharing, doctor, admin, chronic_diseases, monitoring
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

# 向量嵌入管理路由 (Admin only)
api_router.include_router(vector_embedding.router, prefix="/vector-embedding", tags=["vector-embedding"])

# 数据分享路由
api_router.include_router(data_sharing.router, prefix="/sharing", tags=["data-sharing"])
api_router.include_router(sharing.router, prefix="/sharing", tags=["sharing-doctors"])

# 医生管理路由
api_router.include_router(doctor.router, prefix="/doctor", tags=["doctor"])

# 慢性病与特殊病管理路由
api_router.include_router(chronic_diseases.router, tags=["chronic-diseases"])

# 管理员路由 (Admin only)
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])

# 监控指标路由
api_router.include_router(monitoring.router, prefix="/monitoring", tags=["monitoring"])