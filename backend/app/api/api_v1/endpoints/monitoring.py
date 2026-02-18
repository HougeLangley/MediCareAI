"""
Monitoring API Endpoints
监控指标API端点
"""

from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession
from prometheus_client import CONTENT_TYPE_LATEST

from app.core.monitoring import get_metrics, PrometheusMiddleware
from app.db.database import get_db
from app.core.deps import require_admin

router = APIRouter()


@router.get("/metrics")
async def prometheus_metrics():
    """
    Prometheus metrics endpoint
    Prometheus指标采集端点
    
    Returns metrics in Prometheus exposition format
    以Prometheus格式返回指标数据
    """
    metrics_data = get_metrics()
    return Response(
        content=metrics_data,
        media_type=CONTENT_TYPE_LATEST
    )


@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    Health check endpoint with detailed status
    健康检查端点（含详细状态）
    """
    try:
        # Check database connectivity
        from sqlalchemy import text
        result = await db.execute(text("SELECT 1"))
        await result.scalar_one()
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    return {
        "status": "healthy" if db_status == "healthy" else "unhealthy",
        "components": {
            "database": db_status,
            "api": "healthy"
        },
        "timestamp": "auto"
    }


@router.get("/stats", dependencies=[Depends(require_admin)])
async def get_system_stats(db: AsyncSession = Depends(get_db)):
    """
    Get system statistics (admin only)
    获取系统统计信息（仅管理员）
    """
    from sqlalchemy import func, select
    from app.models.models import User, MedicalCase, DoctorCaseComment, SharedMedicalCase
    
    # Get counts
    user_count = await db.execute(select(func.count()).select_from(User))
    case_count = await db.execute(select(func.count()).select_from(MedicalCase))
    comment_count = await db.execute(select(func.count()).select_from(DoctorCaseComment))
    shared_case_count = await db.execute(select(func.count()).select_from(SharedMedicalCase))
    
    return {
        "users": {
            "total": user_count.scalar(),
            "patients": 0,  # Add specific queries if needed
            "doctors": 0,
            "admins": 0
        },
        "cases": {
            "total": case_count.scalar(),
            "shared": shared_case_count.scalar()
        },
        "engagement": {
            "total_comments": comment_count.scalar()
        }
    }
