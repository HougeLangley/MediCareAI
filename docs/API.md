# API Documentation | API 文档

> **MediCare_AI** RESTful API 完整参考 / Complete RESTful API Reference
>
> **Version | 版本:** 1.0.0 | **Base URL:** `http://localhost:8000/api/v1`

---

## 📋 Table of Contents | 目录

1. [Overview | 概述](#overview)
2. [Authentication | 认证](#authentication)
3. [Error Handling | 错误处理](#error-handling)
4. [API Endpoints | API 端点](#endpoints)
5. [Data Models | 数据模型](#data-models)
6. [Code Examples | 代码示例](#examples)

---

<a name="overview"></a>
## 1. Overview | 概述

### 1.1 API Design Principles | API 设计原则

- **RESTful**: Resource-based URLs with HTTP verbs / 基于资源的 URL 和 HTTP 动词
- **JSON**: All requests and responses use JSON / 所有请求和响应使用 JSON
- **Versioned**: API version in URL path (`/api/v1/`) / API 版本在 URL 路径中
- **Consistent**: Standardized response format / 标准化的响应格式
- **Documented**: Auto-generated Swagger/OpenAPI docs / 自动生成 Swagger/OpenAPI 文档

### 1.2 Base URL | 基础 URL

```
Development / 开发环境: http://localhost:8000/api/v1
Production / 生产环境:  https://your-domain.com/api/v1
```

### 1.3 Request/Response Format | 请求/响应格式

**Standard Response Structure | 标准响应结构:**
```json
{
  "success": true,
  "data": { },
  "message": "Operation completed successfully",
  "timestamp": "2025-02-01T10:00:00Z"
}
```

**Error Response Structure | 错误响应结构:**
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": [
      {
        "field": "email",
        "message": "Email format is invalid"
      }
    ]
  },
  "timestamp": "2025-02-01T10:00:00Z"
}
```

---

<a name="authentication"></a>
## 2. Authentication | 认证

### 2.1 JWT Token Flow | JWT 令牌流程

MediCare_AI uses JWT (JSON Web Tokens) for authentication with the following flow:

MediCare_AI 使用 JWT (JSON Web Tokens) 进行认证，流程如下：

```
1. User logs in with credentials / 用户使用凭据登录
   POST /auth/login
   
2. Server returns tokens / 服务器返回令牌
   {
     "access_token": "eyJhbGciOiJIUzI1NiIs...",
     "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
     "token_type": "bearer",
     "expires_in": 1800
   }

3. Client stores tokens / 客户端存储令牌
   localStorage.setItem('access_token', token)

4. Client includes token in requests / 客户端在请求中包含令牌
   Authorization: Bearer <access_token>

5. Token expires / 令牌过期 (30 minutes)

6. Client uses refresh token / 客户端使用刷新令牌
   POST /auth/refresh
   
7. Server returns new access token / 服务器返回新的访问令牌
```

### 2.2 Token Details | 令牌详情

| Token Type | Expiry | Usage | 令牌类型 | 过期时间 | 用途 |
|------------|--------|-------|----------|----------|------|
| **Access Token** | 30 minutes | API authentication | 访问令牌 | 30 分钟 | API 认证 |
| **Refresh Token** | 7 days | Get new access token | 刷新令牌 | 7 天 | 获取新的访问令牌 |

### 2.3 Using Tokens | 使用令牌

Include the access token in the Authorization header of all protected requests:

在所有受保护请求的 Authorization 头中包含访问令牌：

```bash
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."
```

---

<a name="error-handling"></a>
## 3. Error Handling | 错误处理

### 3.1 HTTP Status Codes | HTTP 状态码

| Code | Meaning | Chinese | When to Use | 使用场景 |
|------|---------|---------|-------------|----------|
| 200 | OK | 成功 | Successful GET, PUT, DELETE | 成功的查询、更新、删除 |
| 201 | Created | 已创建 | Successful POST (creation) | 成功的创建操作 |
| 400 | Bad Request | 错误请求 | Validation errors | 验证错误 |
| 401 | Unauthorized | 未授权 | Missing or invalid token | 缺失或无效的令牌 |
| 403 | Forbidden | 禁止访问 | Insufficient permissions | 权限不足 |
| 404 | Not Found | 未找到 | Resource doesn't exist | 资源不存在 |
| 422 | Validation Error | 验证错误 | Pydantic validation failed | Pydantic 验证失败 |
| 500 | Server Error | 服务器错误 | Unexpected server error | 意外的服务器错误 |

### 3.2 Error Codes | 错误代码

```json
{
  "AUTHENTICATION_FAILED": {
    "code": 401,
    "message": "Invalid email or password"
  },
  "TOKEN_EXPIRED": {
    "code": 401,
    "message": "Access token has expired"
  },
  "VALIDATION_ERROR": {
    "code": 422,
    "message": "Input validation failed"
  },
  "RESOURCE_NOT_FOUND": {
    "code": 404,
    "message": "Requested resource not found"
  },
  "INSUFFICIENT_PERMISSIONS": {
    "code": 403,
    "message": "You don't have permission to perform this action"
  }
}
```

---

<a name="endpoints"></a>
## 4. API Endpoints | API 端点

### 4.1 Authentication | 认证模块

#### Register User | 用户注册
```http
POST /auth/register
```

**Description:** Register a new user account and create patient profile / 注册新用户账户并创建患者档案

**Request Body | 请求体:**
```json
{
  "email": "user@example.com",
  "password": "securePassword123",
  "full_name": "John Doe",
  "date_of_birth": "1990-01-01",
  "gender": "male",
  "phone": "+86 138 0013 8000",
  "emergency_contact_name": "Jane Doe",
  "emergency_contact_phone": "+86 139 0013 9000"
}
```

**Response | 响应:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "is_verified": false,
  "created_at": "2025-02-01T10:00:00Z"
}
```

**Validation Rules | 验证规则:**
- `email`: Valid email format / 有效的邮箱格式
- `password`: Minimum 6 characters / 最少 6 个字符
- `full_name`: Required, max 255 characters / 必填，最多 255 字符
- `date_of_birth`: ISO 8601 date format (YYYY-MM-DD) / ISO 8601 日期格式
- `gender`: Enum ["male", "female"] / 枚举值

---

#### Login | 用户登录
```http
POST /auth/login
```

**Description:** Authenticate user and receive tokens / 验证用户并接收令牌

**Request Body | 请求体:**
```json
{
  "email": "user@example.com",
  "password": "securePassword123"
}
```

**Response | 响应:**
```json
{
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "full_name": "John Doe",
    "is_active": true
  },
  "tokens": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 1800
  }
}
```

---

#### Logout | 用户登出
```http
POST /auth/logout
Authorization: Bearer <access_token>
```

**Description:** Invalidate current session / 使当前会话失效

**Response | 响应:**
```json
{
  "message": "Successfully logged out"
}
```

---

#### Get Current User | 获取当前用户
```http
GET /auth/me
Authorization: Bearer <access_token>
```

**Description:** Get current authenticated user information / 获取当前认证用户信息

**Response | 响应:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "is_verified": false,
  "created_at": "2025-02-01T10:00:00Z",
  "last_login": "2025-02-01T10:30:00Z"
}
```

---

#### Update User | 更新用户信息
```http
PUT /auth/me
Authorization: Bearer <access_token>
```

**Request Body | 请求体:**
```json
{
  "full_name": "John Doe Updated"
}
```

**Response | 响应:**
```json
{
  "message": "User information updated successfully",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "full_name": "John Doe Updated"
  }
}
```

---

#### Refresh Token | 刷新令牌
```http
POST /auth/refresh
```

**Request Body | 请求体:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response | 响应:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

---

### 4.2 Patients | 患者模块

#### Get My Patient Profile | 获取我的患者档案
```http
GET /patients/me
Authorization: Bearer <access_token>
```

**Response | 响应:**
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_full_name": "John Doe",
  "date_of_birth": "1990-01-01",
  "gender": "male",
  "phone": "+86 138 0013 8000",
  "emergency_contact": "Jane Doe +86 139 0013 9000",
  "address": "123 Main Street, Beijing",
  "medical_record_number": "MRN2025001",
  "notes": "Patient has allergy to penicillin",
  "created_at": "2025-02-01T10:00:00Z",
  "updated_at": "2025-02-01T10:00:00Z"
}
```

---

#### Update My Patient Profile | 更新我的患者档案
```http
PUT /patients/me
Authorization: Bearer <access_token>
```

**Request Body | 请求体:**
```json
{
  "date_of_birth": "1990-01-01",
  "gender": "male",
  "phone": "+86 138 0013 8000",
  "emergency_contact": "Jane Doe +86 139 0013 9000",
  "address": "456 New Street, Shanghai",
  "notes": "Updated medical notes"
}
```

**Response | 响应:**
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "date_of_birth": "1990-01-01",
  "gender": "male",
  "phone": "+86 138 0013 8000",
  "emergency_contact": "Jane Doe +86 139 0013 9000",
  "address": "456 New Street, Shanghai",
  "notes": "Updated medical notes",
  "updated_at": "2025-02-01T11:00:00Z"
}
```

---

#### List All Patients | 列出所有患者
```http
GET /patients?page=1&limit=20
Authorization: Bearer <access_token>
```

**Query Parameters | 查询参数:**
- `page` (integer, optional): Page number, default 1 / 页码，默认 1
- `limit` (integer, optional): Items per page, default 20, max 100 / 每页项目数，默认 20，最大 100

**Response | 响应:**
```json
{
  "items": [
    {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "user_full_name": "John Doe",
      "date_of_birth": "1990-01-01",
      "gender": "male",
      "medical_record_number": "MRN2025001"
    }
  ],
  "total": 1,
  "page": 1,
  "limit": 20,
  "pages": 1
}
```

---

#### Create Patient | 创建患者
```http
POST /patients
Authorization: Bearer <access_token>
```

**Request Body | 请求体:**
```json
{
  "date_of_birth": "1990-01-01",
  "gender": "male",
  "phone": "+86 138 0013 8000",
  "emergency_contact": "Emergency Contact +86 139 0013 9000",
  "address": "Patient Address",
  "medical_record_number": "MRN2025002"
}
```

**Response | 响应 (201 Created):**
```json
{
  "id": "770e8400-e29b-41d4-a716-446655440002",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "date_of_birth": "1990-01-01",
  "gender": "male",
  "phone": "+86 138 0013 8000",
  "emergency_contact": "Emergency Contact +86 139 0013 9000",
  "created_at": "2025-02-01T10:00:00Z"
}
```

---

#### Get Patient by ID | 根据 ID 获取患者
```http
GET /patients/{patient_id}
Authorization: Bearer <access_token>
```

**Path Parameters | 路径参数:**
- `patient_id` (UUID): Patient unique identifier / 患者唯一标识符

**Response | 响应:**
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_full_name": "John Doe",
  "date_of_birth": "1990-01-01",
  "gender": "male",
  "phone": "+86 138 0013 8000",
  "emergency_contact": "Jane Doe +86 139 0013 9000",
  "address": "123 Main Street",
  "medical_record_number": "MRN2025001",
  "notes": "Patient notes",
  "created_at": "2025-02-01T10:00:00Z",
  "updated_at": "2025-02-01T10:00:00Z"
}
```

---

### 4.3 AI Diagnosis | AI 诊断模块

#### Comprehensive Diagnosis | 综合诊断
```http
POST /ai/comprehensive-diagnosis
Authorization: Bearer <access_token>
```

**Description:** Perform comprehensive AI diagnosis with document analysis / 执行包含文档分析的综合 AI 诊断

**Request Body | 请求体:**
```json
{
  "symptoms": "Patient has persistent cough for 2 weeks, shortness of breath during exercise, and mild chest tightness.",
  "document_id": "880e8400-e29b-41d4-a716-446655440003",
  "patient_info": {
    "age": 35,
    "gender": "male",
    "medical_history": ["asthma", "allergies"]
  }
}
```

**Response | 响应:**
```json
{
  "diagnosis_id": "990e8400-e29b-41d4-a716-446655440004",
  "preliminary_diagnosis": "Possible exercise-induced bronchospasm or mild asthma exacerbation",
  "severity": "moderate",
  "confidence_score": 0.85,
  "recommendations": [
    "Consult pulmonologist for spirometry testing",
    "Monitor peak flow readings daily",
    "Avoid triggers: cold air, strong odors, smoke"
  ],
  "follow_up_plan": {
    "recommended_tests": ["Spirometry", "Chest X-ray", "Allergy testing"],
    "follow_up_date": "2025-02-08",
    "specialist_referral": "Pulmonologist"
  },
  "knowledge_base_references": [
    {
      "source": "Respiratory Guidelines 2025",
      "relevance": 0.92,
      "url": "/knowledge/respiratory/asthma"
    }
  ],
  "created_at": "2025-02-01T10:30:00Z"
}
```

---

#### Simple Diagnosis | 简单诊断
```http
POST /ai/diagnose
Authorization: Bearer <access_token>
```

**Request Body | 请求体:**
```json
{
  "symptoms": "Headache, fever, fatigue for 3 days",
  "patient_id": "660e8400-e29b-41d4-a716-446655440001"
}
```

**Response | 响应:**
```json
{
  "diagnosis": "Possible viral infection or influenza",
  "confidence": 0.75,
  "suggestions": [
    "Rest and hydration",
    "Monitor temperature",
    "Consider COVID-19 test"
  ]
}
```

---

#### Analyze Symptoms | 症状分析
```http
POST /ai/analyze
Authorization: Bearer <access_token>
```

**Request Body | 请求体:**
```json
{
  "symptoms": "Severe chest pain, radiating to left arm, shortness of breath"
}
```

**Response | 响应:**
```json
{
  "urgency_level": "high",
  "possible_conditions": [
    {
      "condition": "Acute coronary syndrome",
      "probability": 0.88,
      "severity": "critical"
    },
    {
      "condition": "Pulmonary embolism",
      "probability": 0.65,
      "severity": "critical"
    }
  ],
  "recommendation": "Seek emergency medical attention immediately",
  "warning_flags": ["chest_pain", "radiating_pain", "dyspnea"]
}
```

---

### 4.4 Medical Cases | 医疗病例模块

#### List Medical Cases | 列出医疗病例
```http
GET /medical-cases?patient_id={patient_id}&page=1&limit=20
Authorization: Bearer <access_token>
```

**Query Parameters | 查询参数:**
- `patient_id` (UUID, optional): Filter by patient / 按患者筛选
- `status` (string, optional): Filter by status ["active", "closed", "pending"] / 按状态筛选
- `page` (integer, optional): Page number / 页码
- `limit` (integer, optional): Items per page / 每页数量

**Response | 响应:**
```json
{
  "items": [
    {
      "id": "aa0e8400-e29b-41d4-a716-446655440005",
      "patient_id": "660e8400-e29b-41d4-a716-446655440001",
      "title": "Respiratory Consultation",
      "description": "Follow-up for persistent cough",
      "symptoms": "Cough, shortness of breath",
      "diagnosis": "Possible asthma exacerbation",
      "severity": "moderate",
      "status": "active",
      "created_at": "2025-02-01T10:00:00Z"
    }
  ],
  "total": 5,
  "page": 1,
  "limit": 20
}
```

---

#### Create Medical Case | 创建医疗病例
```http
POST /medical-cases
Authorization: Bearer <access_token>
```

**Request Body | 请求体:**
```json
{
  "patient_id": "660e8400-e29b-41d4-a716-446655440001",
  "title": "Annual Health Checkup",
  "description": "Routine annual physical examination",
  "symptoms": "No specific symptoms",
  "severity": "low",
  "status": "active"
}
```

**Response | 响应 (201 Created):**
```json
{
  "id": "bb0e8400-e29b-41d4-a716-446655440006",
  "patient_id": "660e8400-e29b-41d4-a716-446655440001",
  "title": "Annual Health Checkup",
  "description": "Routine annual physical examination",
  "symptoms": "No specific symptoms",
  "severity": "low",
  "status": "active",
  "created_at": "2025-02-01T11:00:00Z"
}
```

---

#### Get Medical Case | 获取医疗病例
```http
GET /medical-cases/{case_id}
Authorization: Bearer <access_token>
```

**Response | 响应:**
```json
{
  "id": "aa0e8400-e29b-41d4-a716-446655440005",
  "patient_id": "660e8400-e29b-41d4-a716-446655440001",
  "title": "Respiratory Consultation",
  "description": "Follow-up for persistent cough",
  "symptoms": "Cough, shortness of breath",
  "clinical_findings": {
    "vital_signs": {
      "blood_pressure": "120/80",
      "heart_rate": 72,
      "temperature": 36.8
    }
  },
  "diagnosis": "Possible asthma exacerbation",
  "severity": "moderate",
  "status": "active",
  "created_at": "2025-02-01T10:00:00Z",
  "updated_at": "2025-02-01T11:30:00Z"
}
```

---

### 4.5 Documents | 文档模块

#### Upload Document | 上传文档
```http
POST /documents/upload
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

**Request Body | 请求体:**
```
file: <binary_file_data>
medical_case_id: aa0e8400-e29b-41d4-a716-446655440005 (optional)
```

**Response | 响应 (201 Created):**
```json
{
  "id": "cc0e8400-e29b-41d4-a716-446655440007",
  "filename": "medical_report.pdf",
  "original_filename": "report.pdf",
  "file_type": "application/pdf",
  "file_size": 1048576,
  "upload_status": "uploaded",
  "created_at": "2025-02-01T11:00:00Z"
}
```

---

#### Extract Document Text | 提取文档文本
```http
POST /documents/{document_id}/extract
Authorization: Bearer <access_token>
```

**Response | 响应:**
```json
{
  "document_id": "cc0e8400-e29b-41d4-a716-446655440007",
  "extracted_text": "Patient Name: John Doe\nDate: 2025-01-15\nDiagnosis: Mild respiratory infection...",
  "extraction_metadata": {
    "method": "mineru",
    "confidence": 0.95,
    "pages": 3,
    "processing_time": 2.5
  },
  "structured_data": {
    "patient_name": "John Doe",
    "date": "2025-01-15",
    "diagnosis": "Mild respiratory infection"
  }
}
```

---

<a name="data-models"></a>
## 5. Data Models | 数据模型

### 5.1 User Model | 用户模型

```typescript
interface User {
  id: string;                    // UUID
  email: string;                 // Valid email address
  password_hash: string;         // Bcrypt hashed password
  full_name: string;             // User's full name
  is_active: boolean;            // Account status
  is_verified: boolean;          // Email verification status
  created_at: string;            // ISO 8601 timestamp
  updated_at: string;            // ISO 8601 timestamp
  last_login: string | null;     // ISO 8601 timestamp
}
```

### 5.2 Patient Model | 患者模型

```typescript
interface Patient {
  id: string;                    // UUID
  user_id: string;               // Reference to User
  user_full_name: string;        // Denormalized from User
  date_of_birth: string | null;  // YYYY-MM-DD
  gender: "male" | "female" | null;
  phone: string | null;          // Phone number
  emergency_contact: string | null; // Name + Phone
  address: string | null;        // Full address
  medical_record_number: string | null; // Unique MRN
  notes: string | null;          // Additional notes
  created_at: string;            // ISO 8601 timestamp
  updated_at: string;            // ISO 8601 timestamp
}
```

### 5.3 Medical Case Model | 医疗病例模型

```typescript
interface MedicalCase {
  id: string;                    // UUID
  patient_id: string;            // Reference to Patient
  title: string;                 // Case title
  description: string | null;    // Detailed description
  symptoms: string | null;       // Reported symptoms
  clinical_findings: object | null; // Structured findings
  diagnosis: string | null;      // Diagnosis result
  severity: "low" | "moderate" | "high" | "critical";
  status: "active" | "closed" | "pending";
  created_at: string;            // ISO 8601 timestamp
  updated_at: string;            // ISO 8601 timestamp
}
```

---

<a name="examples"></a>
## 6. Code Examples | 代码示例

### JavaScript/TypeScript Example

```typescript
// API Client Class / API 客户端类
class MediCareAPI {
  private baseURL: string = 'http://localhost:8000/api/v1';
  private token: string | null = null;

  // Set authentication token / 设置认证令牌
  setToken(token: string) {
    this.token = token;
  }

  // Generic request method / 通用请求方法
  async request(
    endpoint: string, 
    method: string = 'GET', 
    body?: object
  ): Promise<any> {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    const response = await fetch(`${this.baseURL}${endpoint}`, {
      method,
      headers,
      body: body ? JSON.stringify(body) : undefined,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || 'API request failed');
    }

    return response.json();
  }

  // Authentication methods / 认证方法
  async login(email: string, password: string) {
    const result = await this.request('/auth/login', 'POST', {
      email,
      password,
    });
    this.setToken(result.tokens.access_token);
    return result;
  }

  async register(userData: object) {
    return this.request('/auth/register', 'POST', userData);
  }

  // Patient methods / 患者方法
  async getMyProfile() {
    return this.request('/patients/me');
  }

  async updateMyProfile(data: object) {
    return this.request('/patients/me', 'PUT', data);
  }

  // AI Diagnosis methods / AI 诊断方法
  async getDiagnosis(symptoms: string) {
    return this.request('/ai/diagnose', 'POST', { symptoms });
  }

  async comprehensiveDiagnosis(data: object) {
    return this.request('/ai/comprehensive-diagnosis', 'POST', data);
  }
}

// Usage example / 使用示例
const api = new MediCareAPI();

// Login / 登录
await api.login('user@example.com', 'password123');

// Get profile / 获取档案
const profile = await api.getMyProfile();
console.log(profile);

// Get AI diagnosis / 获取 AI 诊断
const diagnosis = await api.getDiagnosis(
  'Persistent cough and fever for 3 days'
);
console.log(diagnosis);
```

### Python Example

```python
import requests
from typing import Dict, Any, Optional

class MediCareClient:
    """MediCare_AI API Client / MediCare_AI API 客户端"""
    
    def __init__(self, base_url: str = "http://localhost:8000/api/v1"):
        self.base_url = base_url
        self.token: Optional[str] = None
    
    def set_token(self, token: str):
        """Set authentication token / 设置认证令牌"""
        self.token = token
    
    def request(
        self, 
        endpoint: str, 
        method: str = "GET", 
        data: Dict = None
    ) -> Dict[str, Any]:
        """Make API request / 发起 API 请求"""
        headers = {"Content-Type": "application/json"}
        
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        
        url = f"{self.base_url}{endpoint}"
        
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            json=data
        )
        
        response.raise_for_status()
        return response.json()
    
    # Authentication / 认证
    def login(self, email: str, password: str) -> Dict:
        """Login and get tokens / 登录并获取令牌"""
        result = self.request("/auth/login", "POST", {
            "email": email,
            "password": password
        })
        self.set_token(result["tokens"]["access_token"])
        return result
    
    def register(self, user_data: Dict) -> Dict:
        """Register new user / 注册新用户"""
        return self.request("/auth/register", "POST", user_data)
    
    # Patients / 患者
    def get_my_profile(self) -> Dict:
        """Get current user profile / 获取当前用户档案"""
        return self.request("/patients/me")
    
    def update_my_profile(self, data: Dict) -> Dict:
        """Update user profile / 更新用户档案"""
        return self.request("/patients/me", "PUT", data)
    
    # AI Diagnosis / AI 诊断
    def get_diagnosis(self, symptoms: str) -> Dict:
        """Get simple diagnosis / 获取简单诊断"""
        return self.request("/ai/diagnose", "POST", {
            "symptoms": symptoms
        })
    
    def comprehensive_diagnosis(
        self, 
        symptoms: str, 
        document_id: str = None
    ) -> Dict:
        """Get comprehensive diagnosis / 获取综合诊断"""
        data = {"symptoms": symptoms}
        if document_id:
            data["document_id"] = document_id
        return self.request("/ai/comprehensive-diagnosis", "POST", data)


# Usage example / 使用示例
client = MediCareClient()

# Login / 登录
client.login("user@example.com", "password123")

# Get profile / 获取档案
profile = client.get_my_profile()
print(f"Patient: {profile['user_full_name']}")

# Get diagnosis / 获取诊断
diagnosis = client.get_diagnosis("Headache and fever")
print(f"Diagnosis: {diagnosis['diagnosis']}")
```

### cURL Examples | cURL 示例

```bash
# 1. Register / 注册
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "test123456",
    "full_name": "Test User",
    "date_of_birth": "1990-01-01",
    "gender": "male",
    "phone": "13800138000",
    "emergency_contact_name": "Emergency Contact",
    "emergency_contact_phone": "13900139000"
  }'

# 2. Login / 登录
TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "test123456"}' | \
  grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

echo "Token: $TOKEN"

# 3. Get profile / 获取档案
curl -X GET http://localhost:8000/api/v1/patients/me \
  -H "Authorization: Bearer $TOKEN"

# 4. Get AI diagnosis / 获取 AI 诊断
curl -X POST http://localhost:8000/api/v1/ai/diagnose \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "symptoms": "Persistent cough and fever for 3 days"
  }'

# 5. Upload document / 上传文档
curl -X POST http://localhost:8000/api/v1/documents/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/path/to/medical_report.pdf"
```

---

## 📚 Additional Resources | 附加资源

- [OpenAPI/Swagger Documentation](http://localhost:8000/api/docs) - Interactive API docs
- [ReDoc Documentation](http://localhost:8000/api/redoc) - Alternative API docs format
- [FastAPI Documentation](https://fastapi.tiangolo.com/) - Framework documentation

---

**Last Updated | 最后更新:** 2025-02-01  
**API Version | API 版本:** 1.0.0  
**Maintainers | 维护者:** MediCare_AI API Team
