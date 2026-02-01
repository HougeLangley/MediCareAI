# MediCare_AI 🏥🤖 - 智能疾病管理系统 / Intelligent Disease Management System

<p align="center">
  <img src="frontend/logo.svg" alt="MediCare_AI Logo" width="120">
</p>

<p align="center">
  <a href="#-features"><strong>Features | 功能特性</strong></a> •
  <a href="#-quick-start"><strong>Quick Start | 快速开始</strong></a> •
  <a href="#-architecture"><strong>Architecture | 架构</strong></a> •
  <a href="#-documentation"><strong>Documentation | 文档</strong></a> •
  <a href="#-license"><strong>License | 许可证</strong></a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL">
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/license-MIT-blue?style=for-the-badge" alt="License">
</p>

---

## 🌐 语言选择 / Language Selection

- [简体中文](#overview-zh) | [English](#overview-en)

---

<a name="overview-zh"></a>
## 📖 项目概述 (中文) | Project Overview

**MediCare_AI** 是一个基于人工智能的智能疾病管理系统，专为患者随访和疾病追踪设计。系统整合了医疗指南、AI 智能诊断和文档处理功能，为医疗机构提供全面的健康支持。

### 🎯 核心功能

- **🔐 用户认证与管理** - JWT 安全认证，用户注册登录，会话管理
- **👤 患者档案管理** - 完整的患者信息，病历号管理，紧急联系人
- **🤖 AI 智能诊断** - 集成 GLM-4.7-Flash 模型，实时症状分析
- **📄 文档智能处理** - MinerU 文档抽取，支持 PDF/图片/文档
- **📊 医疗记录管理** - 病例管理，文档附件，随访计划
- **🏥 知识库系统** - 模块化医疗指南，循证医学建议

<a name="overview-en"></a>
## 📖 Project Overview (English)

**MediCare_AI** is an intelligent disease management system powered by AI, designed for patient follow-up and disease tracking. It combines medical guidelines, AI-powered diagnosis, and document processing to provide comprehensive healthcare support.

### 🎯 Core Features

- **🔐 User Authentication** - JWT secure auth, registration/login, session management
- **👤 Patient Management** - Complete patient profiles, medical record numbers, emergency contacts
- **🤖 AI Diagnosis** - GLM-4.7-Flash integration, real-time symptom analysis
- **📄 Document Processing** - MinerU extraction, PDF/image/document support
- **📊 Medical Records** - Case management, document attachments, follow-up plans
- **🏥 Knowledge Base** - Modular medical guidelines, evidence-based recommendations

---

## ✨ Features | 功能特性

### 1. 🔐 User Authentication & Management | 用户认证与管理
**English:** Secure JWT-based authentication with refresh tokens, user registration/login, session management, and audit logging for compliance.

**中文:** 基于 JWT 的安全认证系统，支持刷新令牌、用户注册登录、会话管理和合规审计日志。

### 2. 👤 Patient Management | 患者管理
**English:** Comprehensive patient profiles including personal info, medical history, emergency contacts, and medical record number assignment.

**中文:** 全面的患者档案管理，包括个人信息、病史、紧急联系人和病历号分配。

### 3. 🤖 AI-Powered Diagnosis | AI 智能诊断
**English:** Integration with GLM-4.7-Flash AI model for real-time symptom analysis, evidence-based recommendations, and follow-up plan generation.

**中文:** 集成 GLM-4.7-Flash AI 模型，实现实时症状分析、循证建议生成和随访计划制定。

### 4. 📄 Document Processing | 文档处理
**English:** MinerU integration for intelligent document text extraction from PDFs, images, and medical documents with structured data extraction.

**中文:** MinerU 集成，智能提取 PDF、图片和医疗文档中的文本内容，并转换为结构化数据。

### 5. 📊 Medical Records | 医疗记录
**English:** Case-based medical record management with document attachments, AI feedback tracking, and automated follow-up scheduling.

**中文:** 基于病例的医疗记录管理，支持文档附件、AI 反馈追踪和自动随访计划。

### 6. 🏥 Knowledge Base | 知识库
**English:** Modular medical guidelines system supporting multiple diseases with evidence-based recommendations integrated into AI diagnosis.

**中文:** 模块化医疗指南系统，支持多种疾病，将循证医学建议集成到 AI 诊断流程中。

---

## 🚀 Quick Start | 快速开始

### Prerequisites | 系统要求

**English:**
- Docker 20.10+ & Docker Compose 2.0+
- 8GB+ RAM, 20GB+ free disk space
- Linux/macOS/Windows with WSL2

**中文:**
- Docker 20.10+ 和 Docker Compose 2.0+
- 8GB 以上内存，20GB 以上可用磁盘空间
- Linux/macOS/Windows (需 WSL2)

### Installation | 安装步骤

```bash
# 1. Clone repository / 克隆仓库
git clone https://github.com/yourusername/MediCare_AI.git
cd MediCare_AI

# 2. Configure environment / 配置环境变量
cp .env.example .env
# Edit .env with your configuration / 编辑 .env 文件

# 3. Generate SSL certificates (for local testing) / 生成 SSL 证书（本地测试）
mkdir -p docker/nginx/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout docker/nginx/ssl/key.pem \
  -out docker/nginx/ssl/cert.pem \
  -subj "/C=CN/ST=State/L=City/O=MediCare_AI/CN=localhost"

# 4. Start application / 启动应用
docker-compose up -d

# 5. Initialize database / 初始化数据库
docker-compose exec backend python -c "
import asyncio
from app.db.init_db import init_db
asyncio.run(init_db())
print('Database initialized!')
"
```

### Access Application | 访问应用

- **Frontend | 前端:** http://localhost
- **API Docs | API 文档:** http://localhost/api/docs
- **Health Check | 健康检查:** http://localhost/health

---

## 🏗️ Architecture | 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                    Nginx Reverse Proxy                          │
│                 (Port 80/443 - SSL/TLS)                         │
└───────────────────────────┬─────────────────────────────────────┘
                            │
            ┌───────────────┼───────────────┐
            │               │               │
┌───────────▼──────┐ ┌──────▼──────┐ ┌──────▼────────┐
│     Frontend     │ │   Backend   │ │  API Docs     │
│  HTML/CSS/JS     │ │   FastAPI   │ │  (Swagger)    │
│  (Port 3000)     │ │  (Port 8000)│ │               │
└──────────────────┘ └──────┬──────┘ └───────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
┌───────▼──────┐ ┌──────────▼──────────┐ ┌─────▼──────────┐
│  PostgreSQL  │ │       Redis         │ │  MinerU API    │
│   Database   │ │       Cache         │ │ (Document AI)  │
│ (Port 5432)  │ │    (Port 6379)      │ │                │
└──────────────┘ └─────────────────────┘ └────────────────┘
                            │
                            ▼
                   ┌──────────────────┐
                   │  GLM-4.7-Flash   │
                   │  (Local AI via   │
                   │    llama.cpp)    │
                   └──────────────────┘
```

### Architecture Components | 架构组件

**English:**
- **Frontend**: Vanilla HTML/CSS/JavaScript served by Nginx
- **Backend**: FastAPI (Python 3.11) with async SQLAlchemy ORM
- **Database**: PostgreSQL 17 for data persistence
- **Cache**: Redis 7.4 for session and data caching
- **AI Engine**: GLM-4.7-Flash via local llama.cpp deployment
- **Document AI**: MinerU API for intelligent text extraction

**中文:**
- **前端**: 原生 HTML/CSS/JavaScript，Nginx 提供静态文件服务
- **后端**: FastAPI (Python 3.11)，使用异步 SQLAlchemy ORM
- **数据库**: PostgreSQL 17 用于数据持久化
- **缓存**: Redis 7.4 用于会话和数据缓存
- **AI 引擎**: GLM-4.7-Flash，通过本地 llama.cpp 部署
- **文档 AI**: MinerU API 用于智能文本提取

---

## 📁 Project Structure | 项目结构

```
MediCare_AI/
├── 📁 backend/                    # Backend - 后端
│   ├── 📁 app/
│   │   ├── 📁 api/               # API Routes - API 路由
│   │   │   └── 📁 api_v1/
│   │   │       ├── 📁 endpoints/ # API Endpoints - API 端点
│   │   │       │   ├── auth.py           # Authentication - 认证
│   │   │       │   ├── patients.py       # Patient CRUD - 患者管理
│   │   │       │   ├── ai.py             # AI Diagnosis - AI 诊断
│   │   │       │   ├── medical_cases.py  # Medical Records - 医疗记录
│   │   │       │   └── documents.py      # File Upload - 文件上传
│   │   │       └── api.py
│   │   ├── 📁 core/              # Core Config - 核心配置
│   │   │   ├── config.py         # App Configuration - 应用配置
│   │   │   ├── security.py       # JWT & Password - 安全模块
│   │   │   └── deps.py           # Dependencies - 依赖注入
│   │   ├── 📁 models/            # Database Models - 数据库模型
│   │   │   └── models.py         # SQLAlchemy Models - ORM 模型
│   │   ├── 📁 schemas/           # Pydantic Schemas - 数据验证模式
│   │   │   ├── user.py           # User Schemas - 用户模式
│   │   │   └── patient.py        # Patient Schemas - 患者模式
│   │   ├── 📁 services/          # Business Logic - 业务逻辑层
│   │   │   ├── ai_service.py     # AI Diagnosis Logic - AI 诊断逻辑
│   │   │   ├── patient_service.py # Patient CRUD - 患者服务
│   │   │   ├── user_service.py   # User Management - 用户服务
│   │   │   ├── document_service.py # File Handling - 文档服务
│   │   │   ├── mineru_service.py  # MinerU Integration - MinerU 集成
│   │   │   └── knowledge_base_service.py # Knowledge Base - 知识库
│   │   ├── 📁 db/                # Database Setup - 数据库设置
│   │   │   ├── database.py       # DB Connection - 数据库连接
│   │   │   ├── init_db.py        # Table Creation - 表创建
│   │   │   └── seed_data.py      # Initial Data - 初始数据
│   │   └── main.py               # Application Entry - 应用入口
│   ├── 📁 data/
│   │   └── 📁 knowledge_bases/   # Medical Guidelines - 医疗指南
│   ├── requirements.txt          # Python Dependencies - Python 依赖
│   └── Dockerfile                # Backend Container - 后端容器
├── 📁 frontend/                  # Frontend - 前端
│   ├── index.html                # Homepage - 首页
│   ├── login.html                # Login Page - 登录页
│   ├── register.html             # Registration - 注册页
│   ├── user-profile.html         # User Profile - 个人中心
│   ├── symptom-submit.html       # Symptom Input - 症状提交
│   ├── medical-records.html      # Medical History - 诊疗记录
│   └── Dockerfile                # Frontend Container - 前端容器
├── 📁 docker/                    # Docker Config - Docker 配置
│   ├── 📁 nginx/                 # Nginx Configuration - Nginx 配置
│   │   ├── nginx.conf            # Nginx Config File - 配置文件
│   │   └── Dockerfile
│   └── 📁 postgres/              # PostgreSQL Setup - PostgreSQL 设置
│       └── init.sql              # Init Script - 初始化脚本
├── 📁 docs/                      # Documentation - 文档
│   ├── DEPLOYMENT.md             # Deployment Guide - 部署指南
│   ├── ARCHITECTURE.md           # System Design - 架构设计
│   ├── API.md                    # API Reference - API 参考
│   └── TESTING.md                # Testing Guide - 测试指南
├── 📁 scripts/                   # Utility Scripts - 实用脚本
│   ├── deploy.sh                 # Deployment Script - 部署脚本
│   └── backup.sh                 # Backup Script - 备份脚本
├── docker-compose.yml            # Docker Compose Config - 编排配置
├── .env.example                  # Environment Template - 环境模板
├── README.md                     # This File - 本文件
└── LICENSE                       # MIT License - MIT 许可证
```

---

## 🔧 Configuration | 配置说明

### Environment Variables | 环境变量

| Variable | Description (EN) | 描述 (中文) | Required |
|----------|------------------|-------------|----------|
| `POSTGRES_PASSWORD` | PostgreSQL database password | PostgreSQL 数据库密码 | Yes |
| `REDIS_PASSWORD` | Redis cache password | Redis 缓存密码 | Yes |
| `JWT_SECRET_KEY` | JWT signing key (min 32 chars) | JWT 签名密钥（至少32字符） | Yes |
| `JWT_ALGORITHM` | JWT algorithm | JWT 算法 | No (default: HS256) |
| `MINERU_TOKEN` | MinerU API authentication token | MinerU API 认证令牌 | Yes |
| `AI_API_KEY` | AI model API key | AI 模型 API 密钥 | Yes |
| `AI_API_URL` | AI model endpoint URL | AI 模型端点 URL | Yes |
| `AI_MODEL_ID` | AI model identifier | AI 模型标识符 | Yes |
| `MAX_FILE_SIZE` | Max upload file size (bytes) | 最大上传文件大小（字节） | No (default: 200MB) |
| `DEBUG` | Enable debug mode | 启用调试模式 | No (default: false) |

See [`.env.example`](.env.example) for full configuration template.

---

## 📚 Documentation | 文档导航

### Core Documentation | 核心文档

- **[📖 README.md](README.md)** - This file / 本文件 (Overview & Quick Start)
- **[🚀 DEPLOYMENT.md](docs/DEPLOYMENT.md)** - Detailed deployment guide / 详细部署指南
- **[🏗️ ARCHITECTURE.md](docs/ARCHITECTURE.md)** - System architecture & design / 系统架构与设计
- **[🔌 API.md](docs/API.md)** - Complete API reference / 完整 API 参考
- **[🤝 CONTRIBUTING.md](CONTRIBUTING.md)** - Development guidelines / 开发指南
- **[🤖 AGENTS.md](AGENTS.md)** - AI assistant context / AI 助手上下文

### API Endpoints Overview | API 端点概览

#### Authentication | 认证模块
```
POST   /api/v1/auth/register              # User registration / 用户注册
POST   /api/v1/auth/login                 # User login / 用户登录
POST   /api/v1/auth/logout                # User logout / 用户登出
GET    /api/v1/auth/me                    # Get current user / 获取当前用户
PUT    /api/v1/auth/me                    # Update user info / 更新用户信息
```

#### Patients | 患者模块
```
GET    /api/v1/patients                   # List patients / 患者列表
POST   /api/v1/patients                   # Create patient / 创建患者
GET    /api/v1/patients/me                # Get my patient profile / 获取我的患者档案
PUT    /api/v1/patients/me                # Update my profile / 更新我的档案
GET    /api/v1/patients/{id}              # Get patient by ID / 根据 ID 获取患者
```

#### AI Diagnosis | AI 诊断模块
```
POST   /api/v1/ai/comprehensive-diagnosis # Full diagnosis / 完整诊断
POST   /api/v1/ai/diagnose                # Simple diagnosis / 简单诊断
POST   /api/v1/ai/analyze                 # Symptom analysis / 症状分析
```

#### Medical Records | 医疗记录模块
```
GET    /api/v1/medical-cases              # List cases / 病例列表
POST   /api/v1/medical-cases              # Create case / 创建病例
GET    /api/v1/medical-cases/{id}         # Get case / 获取病例
```

#### Documents | 文档模块
```
POST   /api/v1/documents/upload           # Upload file / 上传文件
GET    /api/v1/documents/{id}             # Get document / 获取文档
POST   /api/v1/documents/{id}/extract     # Extract text / 提取文本
```

Full API documentation is available at `/api/docs` when the application is running.
完整 API 文档在应用运行时可访问 `/api/docs`。

---

## 🧪 Testing | 测试

### Running Tests | 运行测试

```bash
# Backend tests / 后端测试
cd backend
pytest

# Frontend tests / 前端测试
cd frontend
npm test
```

### API Testing | API 测试

```bash
# Health check / 健康检查
curl http://localhost/health

# Register test / 注册测试
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123456","full_name":"Test User"}'

# Login test / 登录测试
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123456"}'
```

---

## 🛠️ Development | 开发指南

### Backend Development | 后端开发

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development | 前端开发

```bash
cd frontend
# No build step needed / 无需构建步骤
# Simply serve static files / 直接提供静态文件
python -m http.server 3000
```

---

## 🤝 Contributing | 贡献指南

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

欢迎贡献！详情请参阅 [CONTRIBUTING.md](CONTRIBUTING.md)。

### Quick Contribution Steps | 快速贡献步骤

```bash
# 1. Fork the repository / Fork 仓库
# 2. Create feature branch / 创建功能分支
git checkout -b feature/AmazingFeature

# 3. Commit changes / 提交更改
git commit -m 'Add some AmazingFeature'

# 4. Push to branch / 推送到分支
git push origin feature/AmazingFeature

# 5. Open Pull Request / 创建 Pull Request
```

---

## 📄 License | 许可证

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

本项目采用 **MIT 许可证** - 详情请参阅 [LICENSE](LICENSE) 文件。

```
MIT License

Copyright (c) 2025 MediCare_AI Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

---

## 🙏 Acknowledgments | 致谢

- **GLM-4.7-Flash**: AI model for diagnosis / 诊断 AI 模型
- **MinerU**: Document processing and text extraction / 文档处理和文本提取
- **FastAPI**: Modern, fast web framework / 现代快速 Web 框架
- **PostgreSQL**: Powerful open-source database / 强大的开源数据库
- **OpenXLab**: AI model hosting platform / AI 模型托管平台

---

## 📞 Support | 支持

- **Issues**: [GitHub Issues](https://github.com/yourusername/MediCare_AI/issues)
- **Documentation**: [Full Documentation](docs/)
- **Email**: support@medicare-ai.example.com

---

<p align="center">
  <b>MediCare_AI</b> - Empowering Healthcare with AI / 用 AI 赋能医疗健康
</p>

<p align="center">
  Made with ❤️ for better healthcare / 为更好的医疗而造
</p>
