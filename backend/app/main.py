"""
MediCareAI Main Application | MediCareAI 主应用程序
Intelligent Disease Management System - FastAPI Entry Point | 智能疾病管理系统 - FastAPI 主入口
"""

from __future__ import annotations

import logging
import os
import time
import socket
from typing import Dict, Any, List

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


def get_server_ips() -> List[str]:
    """Get all server IP addresses for ALLOWED_HOSTS | 获取服务器所有 IP 地址用于 ALLOWED_HOSTS"""
    ips = set()
    try:
        # Get hostname
        hostname = socket.gethostname()
        ips.add(hostname)

        # Get all IP addresses associated with hostname
        try:
            host_ips = socket.gethostbyname_ex(hostname)
            ips.update(host_ips[2])
        except socket.gaierror:
            pass

        # Get IP from specific interface (works on most Linux systems)
        try:
            # Connect to a public DNS to get the outbound IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(0.1)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            if local_ip:
                ips.add(local_ip)
            s.close()
        except Exception:
            pass

    except Exception as e:
        logger.warning(f"Could not determine server IPs: {e}")

    return list(ips)


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
            return [
                origin.strip() for origin in cors_origins.split(",") if origin.strip()
            ]
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


# TrustedHost 配置：从环境变量读取，并自动添加服务器 IP 地址
# TrustedHost Configuration: Read from environment variables and auto-add server IPs
def get_allowed_hosts():
    """获取允许的主机头列表（自动包含服务器 IP 地址）"""
    allowed_hosts = os.getenv("ALLOWED_HOSTS")
    hosts = []

    if allowed_hosts:
        try:
            import json

            hosts = json.loads(allowed_hosts)
        except:
            hosts = [host.strip() for host in allowed_hosts.split(",") if host.strip()]

    # 开发环境允许所有
    if os.getenv("DEBUG") == "true" or os.getenv("ENV") == "development":
        if not hosts:
            return ["*"]

    # 自动添加服务器 IP 地址（支持 IP 直接访问）
    server_ips = get_server_ips()
    for ip in server_ips:
        if ip and ip not in hosts:
            hosts.append(ip)
            logger.info(f"Auto-added server IP to ALLOWED_HOSTS: {ip}")

    if not hosts:
        logger.warning("ALLOWED_HOSTS not configured for production! Using empty list.")
        return []

    return hosts


allowed_hosts_list = get_allowed_hosts()
logger.info(f"ALLOWED_HOSTS configured: {allowed_hosts_list}")

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=allowed_hosts_list,
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
    logger.warning(
        "TRUSTED_PROXY_HOSTS not configured for production! Using restricted defaults."
    )
    return [
        "127.0.0.1",
        "localhost",
        "nginx",
        "10.0.0.0/8",
        "172.16.0.0/12",
        "192.168.0.0/16",
    ]


app.add_middleware(
    ProxyHeadersMiddleware,
    trusted_hosts=get_trusted_proxy_hosts(),
)


# Add Prometheus monitoring middleware
app.add_middleware(PrometheusMiddleware)

# Set application info for metrics
set_app_info(version="1.0.0", environment=os.getenv("ENV", "production"))


@app.middleware("http")
async def log_requests(request: Request, call_next) -> Request:
    """
    HTTP Request Logging Middleware | HTTP 请求日志中间件
    Logs method, path, status code and processing time | 记录请求方法、路径、状态码和处理时间
    """
    start_time = time.time()

    # Extract client IP | 提取客户端 IP
    client_ip = request.headers.get(
        "X-Forwarded-For", request.client.host if request.client else "unknown"
    )

    response = await call_next(request)

    process_time = time.time() - start_time

    logger.info(
        f"Method: {request.method}, Path: {request.url.path}, Status: {response.status_code}, Time: {process_time:.4f}s, IP: {client_ip}"
    )

    return response


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup | 应用启动时初始化"""
    logger.info("=" * 60)
    logger.info("MediCareAI API Server Starting...")
    logger.info(f"Environment: {os.getenv('ENV', 'production')}")
    logger.info(f"Debug Mode: {os.getenv('DEBUG', 'false')}")
    logger.info(f"CORS Origins: {allow_origins}")
    logger.info(f"Allowed Hosts: {allowed_hosts_list}")
    logger.info("=" * 60)


@app.get("/health")
async def health_check():
    """Health check endpoint | 健康检查端点"""
    return {"status": "healthy", "service": "MediCareAI API"}


@app.get("/api/health")
async def api_health_check():
    """API health check endpoint | API 健康检查端点"""
    return {"status": "healthy", "service": "MediCareAI API", "version": "1.0.0"}


# Include API router
app.include_router(api_router, prefix="/api/v1")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
