"""
MediCare AI Main Application | MediCare AI 主应用程序
Intelligent Disease Management System - FastAPI Entry Point | 智能疾病管理系统 - FastAPI 主入口

This module serves as the entry point for the MediCare_AI backend application.
It initializes the FastAPI application, configures middleware, and sets up routing.

本模块作为 MediCare_AI 后端应用的入口点，初始化 FastAPI 应用，配置中间件，并设置路由。

Author: MediCare_AI Team
Version: 1.0.0
Date: 2025-02-01
"""

from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import logging
import time
from typing import Dict
import os
from app.api.api_v1.api import api_router

# =============================================================================
# Logging Configuration | 日志配置
# =============================================================================
# Configure logging format and level for the application
# 为应用配置日志格式和级别
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# =============================================================================
# FastAPI Application Initialization | FastAPI 应用初始化
# =============================================================================
# Create the main FastAPI application instance
# 创建主要的 FastAPI 应用实例
app = FastAPI(
    title="MediCare_AI API",
    description="Intelligent Disease Management System API | 智能疾病管理系统API",
    version="1.0.0",
    # Enable Swagger UI docs only in debug mode for security
    # 仅在调试模式下启用 Swagger UI 文档以确保安全
    docs_url="/docs" if os.getenv("DEBUG") == "true" else None,
    redoc_url="/redoc" if os.getenv("DEBUG") == "true" else None,
)

# =============================================================================
# Middleware Configuration | 中间件配置
# =============================================================================

# CORS Middleware - Cross-Origin Resource Sharing
# CORS 中间件 - 跨域资源共享
# WARNING: allow_origins=["*"] allows all origins - ONLY for development!
# 警告：allow_origins=["*"] 允许所有来源 - 仅用于开发环境！
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific domains / 生产环境应限制为特定域名
    allow_credentials=True,  # Allow cookies/auth headers / 允许 cookie/认证头
    allow_methods=["*"],     # Allow all HTTP methods / 允许所有 HTTP 方法
    allow_headers=["*"],     # Allow all headers / 允许所有头
)

# Trusted Host Middleware - Security protection against host header attacks
# 受信任主机中间件 - 防止主机头攻击的安全保护
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"],  # In production, specify actual domains / 生产环境应指定实际域名
)

# =============================================================================
# Custom Middleware - Request Logging | 自定义中间件 - 请求日志
# =============================================================================
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    HTTP Request Logging Middleware | HTTP 请求日志中间件
    
    Logs all incoming HTTP requests with timing information.
    记录所有传入的 HTTP 请求及时间信息。
    
    Args:
        request: The incoming HTTP request / 传入的 HTTP 请求
        call_next: Function to call the next middleware/endpoint / 调用下一个中间件/端点的函数
    
    Returns:
        Response object with X-Process-Time header / 带有 X-Process-Time 头的响应对象
    """
    start_time = time.time()  # Record start time / 记录开始时间
    response = await call_next(request)  # Process request / 处理请求
    process_time = time.time() - start_time  # Calculate duration / 计算耗时
    
    # Log request details / 记录请求详情
    logger.info(
        f"Method: {request.method}, "
        f"Path: {request.url.path}, "
        f"Status: {response.status_code}, "
        f"Time: {process_time:.4f}s"
    )
    
    # Add processing time header for debugging/monitoring
    # 添加处理时间头用于调试/监控
    response.headers["X-Process-Time"] = str(process_time)
    return response

# =============================================================================
# Root Endpoint | 根端点
# =============================================================================
@app.get("/")
async def root() -> Dict:
    """
    Root Endpoint - Application Welcome | 根端点 - 应用欢迎信息
    
    Returns basic application information.
    返回基本应用信息。
    
    Returns:
        Dict containing app info: name, version, docs URL, environment
        包含应用信息的字典：名称、版本、文档 URL、环境
    """
    return {
        "message": "MediCare_AI API",
        "version": "1.0.0",
        "docs": "/docs" if os.getenv("DEBUG") == "true" else None,
        "environment": os.getenv("ENV", "production"),
        "timestamp": time.time()
    }

# =============================================================================
# Health Check Endpoint | 健康检查端点
# =============================================================================
@app.get("/health")
async def health_check() -> Dict:
    """
    Health Check Endpoint | 健康检查端点
    
    Checks if the application is running properly.
    This is a simplified check that doesn't verify database connectivity.
    检查应用是否正常运行。这是一个简化检查，不验证数据库连接。
    
    Returns:
        Dict with health status and system info / 包含健康状态和系统信息的字典
    
    Raises:
        HTTPException: 503 if health check fails / 如果健康检查失败返回 503
    """
    try:
        # Check Python environment / 检查 Python 环境
        import sys
        
        return {
            "status": "healthy",  # Service is running / 服务运行中
            "service": "MediCare_AI API",
            "version": "1.0.0",
            "python_version": sys.version,  # Python version info / Python 版本信息
            "environment": os.getenv("ENV", "production"),
            "timestamp": time.time()
        }
    except Exception as e:
        # Log error and return 503 Service Unavailable
        # 记录错误并返回 503 服务不可用
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service unavailable: {str(e)}"
        )

# =============================================================================
# API Router Registration | API 路由注册
# =============================================================================
# Include all API v1 routes under /api/v1 prefix
# 在 /api/v1 前缀下包含所有 API v1 路由
# Routes included: auth, patients, documents, ai diagnosis
# 包含的路由：认证、患者、文档、AI 诊断
app.include_router(api_router, prefix="/api/v1")

# =============================================================================
# Application Entry Point | 应用入口点
# =============================================================================
if __name__ == "__main__":
    # Run the application with uvicorn when executed directly
    # 直接执行时使用 uvicorn 运行应用
    import uvicorn
    uvicorn.run(
        "app.main:app",  # Module:app instance / 模块:应用实例
        host="0.0.0.0",  # Listen on all interfaces / 监听所有接口
        port=8000,       # Default port / 默认端口
        reload=os.getenv("DEBUG") == "true"  # Auto-reload in debug mode / 调试模式下自动重载
    )
