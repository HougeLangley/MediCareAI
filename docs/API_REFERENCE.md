# API Reference

Complete API documentation for MediCare_AI.

## Base URL

```
Development: http://localhost:8000/api/v1
Production: https://your-domain.com/api/v1
```

## Authentication

All API endpoints (except login/register) require JWT authentication.

### Get Token
```bash
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### Use Token
```bash
GET /auth/me
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

---

## Authentication Endpoints

### Register User
```bash
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123",
  "full_name": "John Doe"
}
```

**Response:**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "created_at": "2025-01-31T10:00:00Z"
}
```

### Login
```bash
POST /auth/login
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=password123
```

### Logout
```bash
POST /auth/logout
Authorization: Bearer <token>
```

### Refresh Token
```bash
POST /auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

### Get Current User
```bash
GET /auth/me
Authorization: Bearer <token>
```

---

## Patient Endpoints

### List Patients
```bash
GET /patients?page=1&limit=20
Authorization: Bearer <token>
```

**Response:**
```json
{
  "items": [
    {
      "id": "uuid",
      "name": "Patient Name",
      "date_of_birth": "1990-01-01",
      "gender": "male",
      "phone": "1234567890",
      "medical_record_number": "MRN001"
    }
  ],
  "total": 100,
  "page": 1,
  "limit": 20
}
```

### Create Patient
```bash
POST /patients
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Patient Name",
  "date_of_birth": "1990-01-01",
  "gender": "male",
  "phone": "1234567890",
  "address": "123 Main St",
  "emergency_contact": "Emergency Contact: 0987654321"
}
```

### Get Patient
```bash
GET /patients/{patient_id}
Authorization: Bearer <token>
```

### Update Patient
```bash
PUT /patients/{patient_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Updated Name",
  "phone": "new-phone-number"
}
```

### Delete Patient
```bash
DELETE /patients/{patient_id}
Authorization: Bearer <token>
```

---

## AI Diagnosis Endpoints

### Comprehensive Diagnosis
Main endpoint for AI-powered diagnosis with full workflow.

```bash
POST /ai/comprehensive-diagnosis
Authorization: Bearer <token>
Content-Type: application/json

{
  "symptoms": "Patient has been experiencing persistent cough...",
  "document_id": "uuid-of-uploaded-document",  // Optional
  "patient_info": {
    "name": "Patient Name",
    "date_of_birth": "1990-01-01",
    "gender": "male"
  }
}
```

**Response:**
```json
{
  "diagnosis_id": "uuid",
  "preliminary_diagnosis": "Possible respiratory condition...",
  "severity": "moderate",
  "confidence_score": 0.85,
  "recommendations": [
    "Recommendation 1",
    "Recommendation 2"
  ],
  "follow_up_plan": {
    "recommended_tests": ["Chest X-ray", "Blood test"],
    "follow_up_date": "2025-02-07",
    "specialist_referral": "Pulmonologist"
  },
  "knowledge_base_references": [
    {
      "source": "Respiratory Guidelines",
      "relevance": 0.92
    }
  ],
  "created_at": "2025-01-31T10:00:00Z"
}
```

### Simple Diagnosis
```bash
POST /ai/diagnose
Authorization: Bearer <token>
Content-Type: application/json

{
  "symptoms": "Patient symptoms description...",
  "patient_id": "uuid"  // Optional
}
```

### Analyze Symptoms
```bash
POST /ai/analyze
Authorization: Bearer <token>
Content-Type: application/json

{
  "symptoms": "Patient symptoms..."
}
```

---

## Medical Cases Endpoints

### List Medical Cases
```bash
GET /medical-cases?patient_id=uuid&page=1&limit=20
Authorization: Bearer <token>
```

**Response:**
```json
{
  "items": [
    {
      "id": "uuid",
      "patient_id": "uuid",
      "title": "Case Title",
      "description": "Case description...",
      "symptoms": "Patient symptoms...",
      "diagnosis": "Diagnosis result...",
      "severity": "moderate",
      "status": "active",
      "created_at": "2025-01-31T10:00:00Z"
    }
  ],
  "total": 50,
  "page": 1,
  "limit": 20
}
```

### Create Medical Case
```bash
POST /medical-cases
Authorization: Bearer <token>
Content-Type: application/json

{
  "patient_id": "uuid",
  "title": "Case Title",
  "description": "Detailed description...",
  "symptoms": "Patient symptoms...",
  "disease_id": "uuid"  // Optional
}
```

### Get Medical Case
```bash
GET /medical-cases/{case_id}
Authorization: Bearer <token>
```

### Update Medical Case
```bash
PUT /medical-cases/{case_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Updated Title",
  "diagnosis": "Updated diagnosis...",
  "status": "closed"
}
```

### Delete Medical Case
```bash
DELETE /medical-cases/{case_id}
Authorization: Bearer <token>
```

---

## Document Endpoints

### Upload Document
```bash
POST /documents/upload
Authorization: Bearer <token>
Content-Type: multipart/form-data

file: <binary-file-data>
medical_case_id: uuid  // Optional
```

**Response:**
```json
{
  "id": "uuid",
  "filename": "document.pdf",
  "original_filename": "medical_report.pdf",
  "file_type": "application/pdf",
  "file_size": 1024000,
  "upload_status": "uploaded",
  "created_at": "2025-01-31T10:00:00Z"
}
```

### Get Document
```bash
GET /documents/{document_id}
Authorization: Bearer <token>
```

**Response:**
```json
{
  "id": "uuid",
  "filename": "document.pdf",
  "original_filename": "medical_report.pdf",
  "file_type": "application/pdf",
  "file_size": 1024000,
  "extracted_content": {
    "text": "Extracted text content...",
    "metadata": {...}
  },
  "created_at": "2025-01-31T10:00:00Z"
}
```

### Extract Text from Document
```bash
POST /documents/{document_id}/extract
Authorization: Bearer <token>
```

**Response:**
```json
{
  "document_id": "uuid",
  "extracted_text": "Extracted text content...",
  "extraction_metadata": {
    "method": "mineru",
    "confidence": 0.95,
    "pages": 5
  }
}
```

### Delete Document
```bash
DELETE /documents/{document_id}
Authorization: Bearer <token>
```

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid input data",
  "errors": {
    "field": "error message"
  }
}
```

### 401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```

### 403 Forbidden
```json
{
  "detail": "Not enough permissions"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "field"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

---

## Rate Limiting

API requests are rate-limited per IP address:
- **Authenticated**: 1000 requests per hour
- **Unauthenticated**: 100 requests per hour

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
```

---

## Pagination

List endpoints support pagination with these query parameters:
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 20, max: 100)

**Response includes:**
```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "limit": 20,
  "pages": 5
}
```

---

## WebSocket (Future)

Real-time updates will be available via WebSocket:
```
ws://localhost:8000/ws/notifications
```

Connect with JWT token as query parameter:
```
ws://localhost:8000/ws/notifications?token=<jwt>
```
