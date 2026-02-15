"""
MediCare AI Main Application | MediCare AI 主应用程序
Intelligent Disease Management System - FastAPI Entry Point | 智能疾病管理系统 - FastAPI 主入口
"""

from __future__ import annotations

import logging
import os
import time
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.api.api_v1.api import api_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="MediCareAI API",
    description="Intelligent Disease Management System API | 智能疾病管理系统API",
    version="1.0.0",
    docs_url="/docs" if os.getenv("DEBUG") == "true" else None,
    redoc_url="/redoc" if os.getenv("DEBUG") == "true" else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific domains / 生产环境应限制为特定域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"],  # In production, specify actual domains / 生产环境应指定实际域名
)


@app.middleware("http")
async def log_requests(request: Request, call_next) -> Request:
    """
    HTTP Request Logging Middleware | HTTP 请求日志中间件
    
    Logs all incoming HTTP requests with timing information.
    记录所有传入的 HTTP 请求及时间信息。
    """
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    logger.info(
        f"Method: {request.method}, "
        f"Path: {request.url.path}, "
        f"Status: {response.status_code}, "
        f"Time: {process_time:.4f}s"
    )
    
    response.headers["X-Process-Time"] = str(process_time)
    return response


@app.get("/")
async def root() -> Dict[str, Any]:
    """
    Root Endpoint - Application Welcome | 根端点 - 应用欢迎信息
    """
    return {
        "message": "MediCareAI API",
        "version": "1.0.0",
        "docs": "/docs" if os.getenv("DEBUG") == "true" else None,
        "environment": os.getenv("ENV", "production"),
        "timestamp": time.time()
    }


@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Health Check Endpoint | 健康检查端点
    
    Checks if the application is running properly.
    This is a simplified check that doesn't verify database connectivity.
    检查应用是否正常运行。这是一个简化检查，不验证数据库连接。
    """
    try:
        import sys
        
        return {
            "status": "healthy",
            "service": "MediCareAI API",
            "version": "1.0.0",
            "python_version": sys.version,
            "environment": os.getenv("ENV", "production"),
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service unavailable: {str(e)}"
        )


app.include_router(api_router, prefix="/api/v1")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=os.getenv("DEBUG") == "true"
    )