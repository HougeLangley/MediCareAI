"""
MediCareAI Main Application | MediCareAI 主应用程序
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
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

from app.api.api_v1.api import api_router
from app.core.config import settings
from app.core.monitoring import PrometheusMiddleware, set_app_info


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="MediCareAI API",
    description="Intelligent Disease Management System API | 智能疾病管理系统API",
    version="1.0.0",
    docs_url="/docs" if os.getenv("DEBUG") == "true" else None,
    redoc_url="/redoc" if os.getenv("DEBUG") == "true" else None,
)

# CORS 配置：从环境变量读取，开发环境默认允许所有，生产环境必须指定具体域名
# CORS Configuration: Read from environment variables, dev allows all, prod must specify domains
def get_cors_origins():
    """获取CORS允许的源列表"""
    cors_origins = os.getenv("CORS_ORIGINS")
    if cors_origins:
        # 解析环境变量中的JSON格式或逗号分隔的字符串
        try:
            import json
            return json.loads(cors_origins)
        except:
            # 如果不是JSON格式，按逗号分隔
            return [origin.strip() for origin in cors_origins.split(",") if origin.strip()]
    # 默认：开发环境允许所有，生产环境只允许特定域名
    if os.getenv("DEBUG") == "true" or os.getenv("ENV") == "development":
        return ["*"]
    # 生产环境默认只允许常见的本地地址（需要用户配置）
    return ["http://localhost:3000", "http://127.0.0.1:3000"]

# 使用配置好的CORS源
allow_origins = get_cors_origins()

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

# TrustedHost 配置：从环境变量读取
# TrustedHost Configuration: Read from environment variables
def get_allowed_hosts():
    """获取允许的主机头列表"""
    allowed_hosts = os.getenv("ALLOWED_HOSTS")
    if allowed_hosts:
        try:
            import json
            return json.loads(allowed_hosts)
        except:
            return [host.strip() for host in allowed_hosts.split(",") if host.strip()]
    # 默认：开发环境允许所有，生产环境只允许特定主机
    if os.getenv("DEBUG") == "true" or os.getenv("ENV") == "development":
        return ["*"]
    # 生产环境必须配置
    logger.warning("ALLOWED_HOSTS not configured for production! Using empty list.")
    return []

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=get_allowed_hosts(),
)

# ProxyHeadersMiddleware 配置：从环境变量读取
# 生产环境应限制为特定的Nginx容器IP或主机名
# ProxyHeadersMiddleware Configuration: Read from environment variables
def get_trusted_proxy_hosts():
    """获取信任的代理主机列表"""
    trusted_hosts = os.getenv("TRUSTED_PROXY_HOSTS")
    if trusted_hosts:
        try:
            import json
            return json.loads(trusted_hosts)
        except:
            return [host.strip() for host in trusted_hosts.split(",") if host.strip()]
    # 默认：开发环境允许所有，生产环境建议限制
    if os.getenv("DEBUG") == "true" or os.getenv("ENV") == "development":
        return ["*"]
    # 生产环境默认只允许本地网络和常见代理IP
    logger.warning("TRUSTED_PROXY_HOSTS not configured for production! Using restricted defaults.")
    return ["127.0.0.1", "localhost", "nginx", "10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"]

app.add_middleware(
    ProxyHeadersMiddleware,
    trusted_hosts=get_trusted_proxy_hosts(),
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=[
        "*"
    ],  # In production, specify actual domains / 生产环境应指定实际域名
)

# Add ProxyHeadersMiddleware to trust X-Forwarded-* headers from Nginx
app.add_middleware(
    ProxyHeadersMiddleware,
    trusted_hosts=[
        "*"
    ],  # In production, specify Nginx container IP / 生产环境应指定 Nginx 容器 IP
)

# Add Prometheus monitoring middleware
app.add_middleware(PrometheusMiddleware)

# Set application info for metrics
set_app_info(version="1.0.0", environment=os.getenv("ENV", "production"))


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
        "timestamp": time.time(),
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
            "timestamp": time.time(),
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service unavailable: {str(e)}",
        )


@app.on_event("startup")
async def startup_event():
    """
    Application Startup Event | 应用启动事件

    Initialize database data and other startup tasks.
    初始化数据库数据和其他启动任务。
    """
    logger.info("Application starting up...")

    try:
        # Initialize chronic diseases data
        from app.db.init_chronic_diseases import init_chronic_diseases
        from app.db.database import async_session_maker

        async with async_session_maker() as db:
            await init_chronic_diseases(db)

        logger.info("Startup tasks completed successfully")
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        # Don't raise - allow app to start even if init fails


app.include_router(api_router, prefix="/api/v1")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app", host="0.0.0.0", port=8000, reload=os.getenv("DEBUG") == "true"
    )
