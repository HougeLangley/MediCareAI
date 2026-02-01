from fastapi import FastAPI, HTTPException, status, Request
from datetime import datetime
from typing import Optional
import bcrypt
from typing import Dict

# 创建全局变量
users_db = {}

app = FastAPI()

# CORS中间件
@app.middleware("http")
async def add_cors_middleware(request: Request, call_next):
    """CORS中间件"""
    origin = request.headers.get("origin")
    if not origin:
        return call_next

    # CORS中间件
    @app.middleware("http")
    async def add_cors_headers_middleware(request: Request, call_next):
        """添加CORS头到响应"""
        origin = request.headers.get("origin")
        if origin:
            request.state.cors_origin = origin
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type"
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Max-Age": "3600"

    return call_next

# 添加CORS预检
@app.options("/{path:path}")
async def options_handler(path: str):
    """处理OPTIONS预检请求"""
    return {
        "detail": "OK"
    }

# 内存中的用户数据
DEMO_USER = {
    "id": "00000000-0000-0000-000000001",
    "email": "demo@medicare.ai",
    "password_hash": "$2b$12$kSs6/38j1jYS2dNnLCs91u8jm0P6rUzMADc80UDgOIHmFPYzE6Aiy",
    "full_name": "演示患者",
    "is_active": True,
    "is_verified": True,
    "created_at": "2026-01-28T00:00:00",
    "updated_at": "2026-01-28T00:00:00"
}

# 临时用户存储（内存中）
TEMP_TOKENS = {}

# 简化的JWT令牌生成
def create_temp_token(user_id: str) -> str:
    """生成临时令牌（不使用真正的JWT）"""
    from datetime import datetime, timedelta
    now = datetime.utcnow()
    expires_at = now + timedelta(minutes=30)
    return f"temp_{user_id}_{int(now.timestamp())}"

# 验证密码
def verify_password(password: str, password_hash: str) -> bool:
    """验证密码"""
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

# 生成简单令牌
def generate_simple_token(user_id: str) -> str:
    """生成简化令牌"""
    import uuid
    return f"demo_token_{uuid.uuid4()}"

# 用户认证
def authenticate_user(email: str, password: str) -> Optional[dict]:
    """用户认证"""
    if email == DEMO_USER["email"]:
        if verify_password(password, DEMO_USER["password_hash"]):
            return {
                **DEMO_USER
            }
    return None

# 获取当前用户
def get_current_user(token: str) -> Optional[dict]:
    """获取当前用户信息"""
    # 暂时不验证，直接返回演示用户
    if token.startswith("demo_token_"):
        return {
            **DEMO_USER
        }
    return None

# 添加CORS处理
@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "MediCare AI - 患者智能诊疗系统",
        "version": "1.0.0",
        "status": "running",
        "demo_email": DEMO_USER["email"],
        "demo_password": "medicare123456"
    }

@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "backend": "unavailable",
        "demo_user": DEMO_USER,
        "database": "unavailable"
    }

@app.post("/simple-login")
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

    # 验证用户
    user = authenticate_user(email, password)

    if user:
        token = generate_simple_token(user["id"])
        TEMP_TOKENS[token] = {
            **user,
            "expires_at": (datetime.utcnow() + timedelta(minutes=30)).isoformat(),
            "created_at": datetime.utcnow().isoformat()
        }

        return {
            "access_token": token,
            "token_type": "temp",
            "user": {
                "id": user["id"],
                "email": user["email"],
                "full_name": user["full_name"]
            }
        }

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="邮箱或密码错误"
    )

@app.get("/me")
async def get_current_user_simple(token: str):
    """获取当前用户信息（简化版）"""
    if token.startswith("demo_token_"):
        return {
            **DEMO_USER
        }
    return None

@app.post("/logout")
async def simple_logout(request: Request):
    """简化的登出"""
    data = request.json()
    token = data.get("access_token")

    if token and token in TEMP_TOKENS:
        del TEMP_TOKENS[token]
        return {"message": "登出成功"}
    return {"message": "已登出"}

if __name__ == "__main__":
    import uvicorn

    # 启动服务器
    # uvicorn simple_login:app --host 0.0.0.0 --port 8001 --reload
    print("🚀 MediCare AI - 简化版启动在 http://0.0.0.0:8001")
    print("演示邮箱：demo@medicare.ai")
    print("演示密码：medicare123456")
