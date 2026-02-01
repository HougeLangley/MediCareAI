"""
极简版 MediCare AI - 演示版本
只提供演示账号的静态数据
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta

app = FastAPI(title="MediCare AI - Demo")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True
)

# 静态演示数据（不使用数据库，硬编码演示账号）
DEMO_USER = {
    "id": "00000000-0000-0000-000000000001",
    "email": "demo@medicare.ai",
    "password_hash": "$2b$12$kSs6/38j1jYS2dNnLCs91u8jm0P6rUzMADc80UDgOIHmFPYzE6Aiy",
    "full_name": "演示医生",
    "professional_title": "主治医师",
    "license_number": "DEMO001",
    "is_active": True,
    "is_verified": True,
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00"
}

DEMO_PATIENT_1 = {
    "id": "00000000-0000-0000-000000000002",
    "user_id": "00000000-0000-0000-000000001",
    "name": "小明",
    "date_of_birth": "2018-05-15",
    "gender": "男",
    "phone": "13800138000",
    "address": "北京市朝阳区",
    "medical_record_number": "MRN202401001"
}

DEMO_PATIENT_2 = {
    "id": "00000000-0000-0000-000000000003",
    "user_id": "00000-0000-0000-000000000001",
    "name": "小红",
    "date_of_birth": "2019-08-20",
    "gender": "女",
    "phone": "13900139000",
    "address": "上海市浦东新区",
    "medical_record_number": "MRN202401002"
}

DEMO_DISEASE = {
    "id": "00000000-0000-0000-000000000010",
    "name": "儿童的咳嗽变异性哮喘",
    "code": "J45.9",
    "description": "咳嗽变异性哮喘是一种特殊类型的哮喘，主要表现为慢性咳嗽，是儿童慢性咳嗽的常见原因之一。诊断和治疗建议：支气管舒张剂、吸入糖皮质激素。"
}

DEMO_MEDICAL_CASES = [
    {
        "id": "00000000-0000-0000-000000000020",
        "patient_id": "00000000-0000-0000-000000001",
        "disease_id": "00000000-0000-000000000010",
        "title": "反复咳嗽一个月",
        "description": "患儿一个月前开始出现反复咳嗽症状，多在夜间和清晨加重，运动后症状明显。",
        "symptoms": "夜间和清晨咳嗽、运动后诱发咳嗽、无喘息症状",
        "diagnosis": "儿童的咳嗽变异性哮喘",
        "severity": "moderate",
        "status": "active",
        "ai_recommendations": "建议继续按医嘱使用支气管舒张剂和吸入糖皮质激素治疗。避免接触过敏原，定期复查肺功能。",
        "created_at": "2024-01-01T00:10:00",
        "updated_at": "2024-01-01T00:10:00"
    },
    {
        "id": "00000000-0000-0000-0000-000000000021",
        "patient_id": "00000000-0000-0000-000000003",
        "disease_id": "00000000-0000-000000000010",
        "title": "慢性咳嗽两月余",
        "description": "患儿两月前开始慢性咳嗽，无明显喘息，抗感染治疗效果不佳。",
        "symptoms": "持续咳嗽、干咳为主、无发热",
        "diagnosis": "儿童的咳嗽变异性哮喘",
        "severity": "mild",
        "status": "completed",
        "ai_recommendations": "建议进行过敏原检测，完善诊断。继续规范用药。",
        "created_at": "2024-01-01T00:15:00",
        "updated_at": "2024-01-01T00:15:00"
    }
]

# 健康状态
HEALTH_STATUS = {
    "status": "healthy",
    "services": {
        "backend": "healthy",
        "database": "healthy",
        "frontend": "healthy"
    }
}

# JWT配置（演示使用假令牌）
JWT_SECRET = "demo-secret-key-for-jwt-demo"

def create_demo_token():
    """创建演示JWT令牌"""
    import time
    payload = {
        "sub": "demo_user",
        "exp": int(time.time()) + 3600,  # 1小时过期
        "role": "demo_user"
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

# ==========================================
# 认证相关端点
# ==========================================

@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        **HEALTH_STATUS,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/v1/simple-login")
async def simple_login(credentials: dict):
    """简化登录（不使用数据库）"""
    email = credentials.get("email", "")
    password = credentials.get("password", "")
    
    if email == DEMO_USER["email"] and password == "medicare123456":
        access_token = create_demo_token()
        return {
            "access_token": access_token,
            "token_type": "demo",
            "user": DEMO_USER,
            "expires_in": 3600,
            "message": "登录成功（演示账号）"
        }
    else:
        raise HTTPException(
            status_code=401,
            detail="邮箱或密码错误"
        )

# ==========================================
# 用户相关端点
# ==========================================

@app.get("/api/v1/users/me")
async def get_current_user_info():
    """获取当前用户信息（不验证令牌，返回演示用户"""
    return {
        **DEMO_USER,
        "timestamp": datetime.now().isoformat()
    }

# ==========================================
# 患者相关端点
# ==========================================

@app.get("/api/v1/patients")
async def get_patients():
    """获取患者列表（返回演示患者）"""
    return {
        "total": len(DEMO_MEDICAL_CASES),
        "patients": [DEMO_PATIENT_1, DEMO_PATIENT_2]
    }

@app.get("/api/v1/patients/{patient_id}")
async def get_patient_details(patient_id: str):
    """获取患者详细信息"""
    if patient_id == "00000000-0000-0000-000000000002":
        return {
            **DEMO_PATIENT_1,
            "medical_record_number": "MRN202401001"
        }
    return {"message": f"患者 {patient_id} 不存在"}

@app.post("/api/v1/patients")
async def create_patient(patient: dict):
    """创建患者（仅内存存储）"""
    patient_id = str(int(time.time()) * 1000 + len(DEMO_MEDICAL_CASES) + 2))
    patient_data = {
        "id": patient_id,
        **patient
    }

    return {
        "message": "患者创建成功（演示版本，仅内存存储）",
        "patient": patient_data
    }

# ==========================================
# AI诊断相关端点
# ==========================================

@app.post("/api/v1/ai/diagnose")
async def ai_diagnose(symptom_data: dict):
    """AI诊断（模拟）"""
    symptoms = symptom_data.get("symptoms", "")
    duration = symptom_data.get("duration", "")
    severity = symptom_data.get("severity", "")
    
    # 基于症状进行简单的模拟诊断
    if "咳嗽" in symptoms.lower() or "喘息" in symptoms.lower():
        if "夜间" in symptoms.lower() or "清晨" in symptoms.lower():
            diagnosis = DEMO_DISEASE
            severity = "moderate"
            ai_recommendations = DEMO_DISEASE["description"]
        else:
            diagnosis = DEMO_DISEASE
            severity = "mild"
            ai_recommendations = "建议做进一步检查。"
    else:
            diagnosis = "上呼吸道感染",
            severity = "mild",
            ai_recommendations = "多喝温水，注意休息。"
    else:
        diagnosis = "消化系统问题",
            severity = "mild",
            ai_recommendations = "注意饮食卫生。"
    else:
            diagnosis = "一般症状",
            severity = "mild",
            ai_recommendations = "建议观察。"

    return {
        "diagnosis": diagnosis,
        "severity": severity,
        "ai_recommendations": ai_recommendations,
        "status": "completed"
    }

# ==========================================
# 健康档案端点
# ==========================================

@app.get("/api/v1/health/stats")
async def get_health_stats():
    """获取健康统计"""
    return {
        "stats": {
            "total_cases": len(DEMO_MEDICAL_CASES),
            "active_cases": len([c for c in DEMO_MEDICAL_CASES if c["status"] == "active"]),
            "completed_cases": len([c for c in DEMO_MEDICAL_CASES if c["status"] == "completed"]),
            "last_date": DEMO_MEDICAL_CASES[-1]["created_at"]
        }
    }

@app.get("/api/v1/health/trends")
async def get_health_trends():
    """获取健康趋势"""
    trends = {
        "labels": ["一月", "二月", "三月"],
        "values": [2, 1, 3]  # 模拟数据
        "patients": [5, 3, 4],
            "cases": [2, 1, 3],
            "active": [1, 1, 1],
            "completed": [1, 1, 1]
        }
    }

    return {
        "trends": trends,
        "stats": await get_health_stats()
    }

@app.get("/api/v1/health/alerts")
async def get_health_alerts():
    """获取健康提醒"""
    return {
        "alerts": []
    }

# ==========================================
# 文档上传端点
# ==========================================

@app.post("/api/v1/documents/upload")
async def upload_document(file_data: dict):
    """上传文档（模拟）"""
    return {
        "message": "文档上传成功（演示版本，仅模拟）"
    }

# ==========================================
# 管化数据库查询
# ==========================================

def get_user_by_email(email: str) -> dict:
    """通过邮箱获取用户"""
    if email == DEMO_USER["email"]:
        return {**DEMO_USER}
    return None

def verify_password(password: str, password_hash: str) -> bool:
    """验证密码"""
    if password == "medicare123456":
        return True
    return False

# ==========================================
# 模拟JWT处理
# ==========================================

import jwt

def create_demo_token():
    """创建演示令牌"""
    payload = {
        "sub": "demo_user",
        "exp": int(time.time()) + 3600
    "role": "demo_user"
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

def decode_demo_token(token: str) -> dict:
    """解码演示令牌"""
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=["HS256"], options={"verify_signature": False})
    except Exception:
        return {"sub": "demo_user", "exp": 0}

# ==========================================
# 启动服务器
# ==========================================

if __name__ == "__main__":
    import uvicorn
    uvicorn app:app, host="0.0.0.0", port=8000, log_level="info", reload=True)
