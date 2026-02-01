"""
MediCare AI - 简化用户认证（不使用JWT）
"""
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
import uuid
import bcrypt
from typing import Optional, Dict

# 模拟数据库（内存中存储）
DEMO_USERS = {
    "00000000-0000-0000-0000-000000001": {
        "id": "00000000-0000-0000-0000-000000000001",
        "email": "demo@medicare.ai",
        "password_hash": "$2b$12$kSs6/38j1jYS2dNnLCs91u8jm0P6rUzMADc80UDgOIHmFPYzE6Aiy",
        "full_name": "演示患者",
        "professional_title": "主治医师",
        "license_number": "DEMO001",
        "is_active": True,
        "is_verified": True,
        "created_at": "2026-01-28T00:00:00",
        "updated_at": "2026-01-28T00:00:00"
    }
}

# 临时JWT令牌存储（内存中）
TEMP_TOKENS = {}

app = FastAPI()

# CORS配置
origins = [
    "http://192.168.50.115:3000",
    "http://192.168.50.115:8000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True
)

@app.middleware("http")
async def add_cors_middleware(request: Request, call_next):
    """CORS中间件"""
    origin = request.headers.get("origin")
    if not origin:
        origin = request.headers.get("Access-Control-Request-Method")

    if origin:
        response = await call_next(request)
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type"
        response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Max-Age"] = "3600"
        return response

# 演示用户
DEMO_USER = {
    "id": "00000000-0000-0000-0000-0000-000000001",
    "email": "demo@medicare.ai",
    "password_hash": "$2b$12$kSs6/38j1jYS2dNnLCs91u8jm0P6rUzMADc80UDgOIHmFPYzE6Aiy"
}

@app.get("/")
async def root():
    return {
        "message": "MediCare AI - 患者端",
        "version": "1.0.0",
        "status": "running",
        "demo_user": {
            "email": "demo@medicare.ai",
            "full_name": "演示患者",
            "password": "medicare123456"
        }
    }

@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "frontend": "healthy",
        "backend": "healthy",
        "database": "available",
        "authentication": "simplified (no JWT)"
    }

@app.post("/api/v1/simple-login", tags=["authentication"])
async def simple_login(request: dict):
    """简化登录（不使用JWT）"""
    data = await request.json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱和密码不能为空"
        )

    # 演示账号登录
    if email == DEMO_USER["email"] and password == DEMO_USER["password"]:
        user = DEMO_USER.copy()
        user.pop('password', None)
        user.pop('password_hash', None)
        
        return {
            "user": {
                "id": str(user["id"]),
                "email": user["email"],
                "full_name": user["full_name"],
                "professional_title": user["professional_title"],
                "is_active": user["is_active"],
                "is_verified": user["is_verified"]
            },
            "message": "登录成功（演示账号）",
            "token_type": "demo",
            "access_token": f"demo_token_{user['id']}"
        }

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="邮箱或密码错误"
    )

@app.get("/api/v1/users/me", tags=["users"])
async def get_current_user(request: Request):
    """获取当前用户信息"""
    auth_header = request.headers.get("Authorization")

    if not auth_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="需要Authorization头"
        )

    token = auth_header.replace("Bearer ", "")
    if token.startswith("demo_token_"):
        user_id = token.replace("demo_token_", "")
        user = DEMO_USERS.get(user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        return {
            "user": {
                "id": str(user["id"]),
                "email": user["email"],
                "full_name": user["full_name"],
                "professional_title": user["professional_title"],
                "is_active": user["is_active"],
                "is_verified": user["is_verified"]
            },
            "message": "获取用户信息成功"
        }

@app.post("/api/v1/logout", tags=["users"])
async def logout(request: dict):
    """登出"""
    auth_header = request.headers.get("Authorization")

    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.replace("Bearer ", "")
        TEMP_TOKENS.pop(token, None)
        
        return {
            "message": "登出成功"
        }
    
    return {
        "message": "登出成功"
    }

@app.post("/api/v1/register", tags=["authentication"])
async def register(request: dict):
    """用户注册"""
    data = await request.json()

    email = data.get("email")
    password = data.get("password")
    full_name = data.get("full_name")
    professional_title = data.get("professional_title", "license_number", None)
    license_number = data.get("license_number")

    if not email or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱、密码和姓名不能为空"
        )

    # 检查邮箱是否已存在
    for user_id, user_data in DEMO_USERS.items():
        if user_data["email"] == email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="邮箱已被注册"
            )

    # 密码哈希
    pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
    password_hash = pwd_context.hash(password.encode('utf-8'))

    # 创建新用户
    new_user_id = str(uuid.uuid4())

    DEMO_USERS[new_user_id] = {
        "id": new_user_id,
        "email": email,
        "password_hash": password_hash,
        "full_name": full_name,
        "professional_title": professional_title,
        "license_number": license_number,
        "is_active": True,
        "is_verified": False,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }

    return {
        "user": {
            "id": new_user_id,
            "email": email,
            " "full_name": full_name,
            "is_active": True,
            "is_verified": False
        },
        "message": "注册成功，请完成邮箱验证"
    }
