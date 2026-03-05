# MediCareAI 🏥🤖 - 智能疾病管理系统 / Intelligent Disease Management System

<p align="center">
  <img src="frontend/logo.svg" alt="MediCareAI Logo" width="120">
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

<p align="center">
  <strong>作者 Author: 苏业钦 (Su Yeqin)</strong>
</p>

---

## 🌐 语言选择 / Language Selection

- [简体中文](#overview-zh) | [English](#overview-en)

---

<a name="overview-zh"></a>
## 📖 项目概述 (中文) | Project Overview

**MediCareAI** 是一个基于人工智能的智能疾病管理系统，专为患者随访和疾病追踪设计。系统整合了医疗指南、AI 智能诊断、文档处理功能和完整的邮件通知系统，为医疗机构提供全面的健康支持。

### 🎯 核心功能

- **🔐 用户认证与管理** - JWT 安全认证，用户注册登录，会话管理，支持患者、医生、管理员三端
- **📧 邮箱验证系统** - 患者注册邮箱验证，确保邮箱有效性，支持一键验证链接
- **👤 患者档案管理** - 完整的患者信息，病历号管理，紧急联系人，阿里云 OSS 安全存储患者病例资料
- **🤖 AI 智能诊断** - 支持 OpenAI 兼容 API 的 AI 大模型，实时症状分析，结合患者历史病历和上传文档
- **📄 文档智能处理** - MinerU 文档抽取，支持 PDF/图片/文档，自动 PII 脱敏保护隐私
- **📊 医疗记录管理** - 病例管理，文档附件存储于阿里云 OSS，随访计划
- **🏥 知识库系统** - 基于向量检索的智能知识库(RAG)，管理员可动态创建医疗指南，AI 诊断自动引用循证医学建议
- **🔄 RAG 重排序** - 支持外部 API 重排序服务（阿里云百炼、博查等），提升检索精度 10-20%
- **👨‍⚕️ 医生协作平台** - @医生提及系统，医患双向沟通，医生可在共享病例上添加专业评论
- **📨 邮件通知系统** - 医生注册审核通知、审核通过/拒绝/撤销邮件，SMTP 动态配置
- **🏛️ 管理员系统** - 系统监控(CPU/内存/磁盘)，医生认证审核，审计日志，知识库向量化管理，邮件服务配置

<a name="overview-en"></a>
## 📖 Project Overview (English)

**MediCareAI** is an intelligent disease management system powered by AI, designed for patient follow-up and disease tracking. It combines medical guidelines, AI-powered diagnosis, document processing, and comprehensive email notification system to provide comprehensive healthcare support.

### 🎯 Core Features

- **🔐 User Authentication** - JWT secure auth, registration/login, session management, supports Patient/Doctor/Admin platforms
- **📧 Email Verification** - Patient registration email verification to ensure email validity with one-click verification link
- **👤 Patient Management** - Complete patient profiles, medical record numbers, emergency contacts, Alibaba Cloud OSS secure storage for patient case data
- **🤖 AI Diagnosis** - Support for OpenAI-compatible API AI models, real-time symptom analysis, combines patient history and uploaded documents
- **📄 Document Processing** - MinerU extraction, PDF/image/document support with automatic PII cleaning for privacy protection
- **📊 Medical Records** - Case management, document attachments stored in Alibaba Cloud OSS, follow-up plans
- **🏥 Knowledge Base** - Vector-based intelligent knowledge base (RAG), admins can dynamically create medical guidelines, AI diagnosis automatically references evidence-based recommendations
- **🔄 RAG Reranking** - Support for external API reranking services (Bailian, Bocha, Cohere, Jina), improves retrieval accuracy by 10-20%
- **👨‍⚕️ Doctor Collaboration Platform** - @doctor mention system, bidirectional patient-doctor communication, doctors can add professional comments on shared cases
- **📨 Email Notification System** - Doctor registration pending/approval/rejection/revocation notifications with SMTP dynamic configuration
- **🏛️ Admin System** - System monitoring (CPU/Memory/Disk), doctor verification workflow, audit logging, knowledge base vectorization management, email service configuration
- **🔒 Privacy Protection** - Automatic PII detection and cleaning for document sharing

---

## ✨ Features | 功能特性

### 1. 🔐 Multi-Platform Authentication | 多端用户认证
**English:** Secure JWT-based authentication supporting three platforms: Patient, Doctor, and Admin. Each platform has dedicated UI and permissions. Refresh tokens, session management, and complete audit logging for compliance.

**中文:** 基于 JWT 的安全认证系统，支持患者端、医生端、管理员端三个平台。每个平台拥有独立的界面和权限。支持刷新令牌、会话管理和完整的合规审计日志。

### 2. 👤 Patient Platform | 患者端平台
**English:** Complete patient workflow from symptom submission to diagnosis history:
- **Symptom Submission**: AI diagnosis with optional @doctor mention, document upload (PDF/images)
- **AI Diagnosis Workflow**: Smart RAG retrieves relevant medical guidelines, combines patient history + uploaded documents + knowledge base for comprehensive AI analysis
- **Medical Records**: View diagnosis history with AI feedback, doctor comments, and patient replies
- **Document Storage**: All medical documents securely stored in Alibaba Cloud OSS with PII cleaning

**中文:** 完整的患者工作流程，从症状提交到诊疗记录：
- **症状提交**: AI 智能诊断，支持 @医生提及，文档上传（PDF/图片）
- **AI 诊断工作流**: 智能 RAG 检索相关医疗指南，结合患者历史 + 上传文档 + 知识库进行综合 AI 分析
- **诊疗记录**: 查看诊断历史、AI 反馈、医生评论和患者回复
- **文档存储**: 所有医疗文档使用阿里云 OSS 安全存储，自动 PII 脱敏

### 3. 🤖 AI-Powered Diagnosis with RAG | AI 智能诊断与 RAG
**English:** Advanced AI diagnosis system with Retrieval-Augmented Generation:
- **Smart Knowledge Retrieval**: Vector-based RAG automatically selects relevant medical guidelines from knowledge base
- **Multi-Source Context**: Combines patient personal info + uploaded documents (MinerU extracted) + knowledge base guidelines
- **Streaming Response**: Real-time diagnosis output with progress indicators
- **Evidence-Based**: Each recommendation references specific medical guidelines from knowledge base
- **Language Adaptation**: Automatically responds in Chinese or English based on UI language

**中文:** 基于检索增强生成(RAG)的高级 AI 诊断系统：
- **智能知识检索**: 基于向量的 RAG 自动从知识库选择相关医疗指南
- **多源上下文**: 结合患者个人信息 + 上传文档（MinerU 提取）+ 知识库指南
- **流式响应**: 实时诊断输出，带进度指示器
- **循证医学**: 每个建议都引用知识库中的具体医疗指南
- **语言自适应**: 根据界面语言自动使用中文或英文回复

### 4. 👨‍⚕️ Doctor Platform | 医生端平台
**English:** Professional tools for verified doctors:
- **Doctor Verification**: Registration with medical license, admin approval workflow
- **@My Cases**: View cases where patient mentioned the doctor, time-based filtering (Today/3 days/1 week)
- **Case Comments**: Add professional comments on shared cases (suggestion, diagnosis, treatment advice)
- **Patient Replies**: View patient replies to your comments only (privacy protected, cannot see other doctors' threads)
- **Professional Profile**: Display hospital, department, specialty, title with anonymized name

**中文:** 为已认证医生提供的专业工具：
- **医生认证**: 使用医疗执业证注册，管理员审批工作流
- **@我的病例**: 查看患者提及医生的病例，时间筛选（今日/三天内/一周内）
- **病例评论**: 在共享病例上添加专业评论（建议、诊断意见、治疗建议）
- **患者回复**: 仅查看对自己评论的患者回复（隐私保护，无法查看其他医生的线程）
- **专业档案**: 显示医院、科室、专业、职称，名称匿名化显示

### 5. 🏛️ Admin System | 管理员系统
**English:** Comprehensive administrative control panel:
- **System Monitoring**: Real-time CPU, Memory, Disk usage with psutil (color-coded alerts)
- **AI Diagnosis Analytics**: Statistics, anomaly detection, performance metrics
- **Doctor Verification**: Review doctor registrations, approve/reject with audit logging
- **Knowledge Base Management**: Vectorize documents, manage medical guidelines, RAG configuration
- **Audit Logging**: Complete operation logs for compliance and security
- **Data Persistence**: Docker volumes with restart: always policy

**中文:** 全面的管理控制面板：
- **系统监控**: 实时 CPU、内存、磁盘使用率，使用 psutil（彩色预警）
- **AI 诊断分析**: 统计、异常检测、性能指标
- **医生认证**: 审核医生注册、批准/拒绝，带审计日志
- **知识库管理**: 文档向量化、管理医疗指南、RAG 配置
- **审计日志**: 完整的操作日志用于合规和安全
- **数据持久化**: Docker 卷配置 restart: always 策略

### 6. 📄 Document Processing & OSS Storage | 文档处理与 OSS 存储
**English:** Intelligent document pipeline:
- **MinerU Integration**: Extract text from PDFs, images, Word, PPT with OCR
- **Alibaba Cloud OSS**: Secure cloud storage for all medical documents
- **PII Cleaning**: Automatic detection and masking of personal information before AI processing
- **Vectorization**: Documents converted to embeddings for RAG knowledge retrieval
- **Reusable Content**: Extracted documents can be reused in multiple AI diagnoses

**中文:** 智能文档处理流程：
- **MinerU 集成**: 从 PDF、图片、Word、PPT 提取文本，支持 OCR
- **阿里云 OSS**: 所有医疗文档的安全云存储
- **PII 清洗**: AI 处理前自动检测和屏蔽个人信息
- **向量化**: 文档转换为嵌入向量用于 RAG 知识检索
- **内容复用**: 提取的文档可在多个 AI 诊断中重复使用

### 7. 🏥 Dynamic Knowledge Base | 动态知识库
**English:** Self-improving medical knowledge system:
- **Vector Embeddings**: Qwen API for document vectorization
- **Smart RAG Selector**: Automatically selects relevant guidelines for each diagnosis
- **Admin Management**: Upload, organize, and manage medical guidelines via admin panel
- **Chunking Strategy**: Intelligent text splitting for optimal retrieval
- **Version Control**: Track knowledge base updates and changes

**中文:** 自我完善的医学知识系统：
- **向量嵌入**: 使用 Qwen API 进行文档向量化
- **智能 RAG 选择器**: 为每次诊断自动选择相关指南
- **管理员管理**: 通过管理面板上传、组织、管理医疗指南
- **分块策略**: 智能文本分割以获得最佳检索效果
- **版本控制**: 跟踪知识库更新和变更

### 8. 🔄 RAG Reranking | RAG 重排序
**English:** External API-based reranking layer for improved retrieval accuracy:
- **Multi-Provider Support**: Bailian (阿里云), Bocha (博查), Cohere, Jina AI
- **Admin Configurable**: Configure reranking models via admin panel, no hardcoding
- **Automatic Fallback**: Gracefully falls back to RRF ranking if reranking fails
- **Caching**: Results cached for 5 minutes to reduce API costs
- **Performance Boost**: 10-20% improvement in retrieval accuracy

**中文:** 基于外部 API 的重排序层，提升检索精度：
- **多提供商支持**: 阿里云百炼、博查 AI、Cohere、Jina AI
- **管理员可配置**: 通过管理界面配置重排序模型，无需硬编码
- **自动降级**: 重排序失败时自动回退到 RRF 排序
- **结果缓存**: 5 分钟缓存减少 API 调用成本
- **性能提升**: 检索精度提升 10-20%

### 9. 🔒 Security & Privacy | 安全与隐私
**English:** Enterprise-grade security measures:
- **PII Protection**: Automatic detection of names, IDs, phone numbers, addresses in documents
- **Role-Based Access**: Strict separation between patient, doctor, and admin data
- **Privacy Controls**: Doctors only see their own threads; patients see all doctor comments
- **Audit Trail**: Every action logged for compliance
- **Secure Storage**: Sensitive data in Alibaba Cloud OSS with access controls

**中文:** 企业级安全措施：
- **PII 保护**: 自动检测文档中的姓名、身份证号、电话、地址
- **基于角色的访问**: 患者、医生、管理员数据严格分离
- **隐私控制**: 医生仅查看自己的线程；患者查看所有医生评论
- **审计追踪**: 每个操作都记录用于合规
- **安全存储**: 敏感数据存储在阿里云 OSS 中，带访问控制

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

### Quick Start | 快速开始

MediCareAI uses Docker for deployment, supporting any platform with Docker installed (Linux, macOS, Windows with WSL2).

**Prerequisites | 环境要求:**
- Docker 20.10+ & Docker Compose 2.0+
- 8GB+ RAM, 20GB+ free disk space

> ⚠️ **重要提示 | IMPORTANT NOTICE**
>
> **生产环境必须使用 SSL 证书 | SSL Certificate Required for Production**
>
> 部署到公网时，必须正确配置 SSL 证书 (`docker/nginx/ssl/cert.pem` 和 `key.pem`)，否则 HTTPS 将无法正常工作。
>
> When deploying to production, you MUST configure SSL certificates properly (`docker/nginx/ssl/cert.pem` and `key.pem`), otherwise HTTPS will not work.
>
> - 开发环境可使用自签名证书 | Self-signed certs OK for development
> - 生产环境建议使用 Let's Encrypt | Let's Encrypt recommended for production
> - 证书路径：`docker/nginx/ssl/` | Certificate path: `docker/nginx/ssl/`
>
> - 详见下方 [SSL Certificate Setup](#step-3-ssl-certificate-setup--步骤-3-ssl-证书配置) | See [SSL Certificate Setup](#step-3-ssl-certificate-setup--步骤-3-ssl-证书配置) below
>

```bash
# 1. Clone repository / 克隆仓库
git clone https://github.com/yourusername/MediCareAI.git
cd MediCareAI

# 2. Configure environment / 配置环境变量
cp .env.example .env
# Edit .env with your configuration / 编辑 .env 文件

# 3. Generate SSL certificates (for local testing) / 生成 SSL 证书（本地测试）
mkdir -p docker/nginx/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout docker/nginx/ssl/key.pem \
  -out docker/nginx/ssl/cert.pem \
  -subj "/C=CN/ST=State/L=City/O=MediCareAI/CN=localhost"

# 4. Start application / 启动应用
# 数据库会自动初始化，管理员账号会自动创建
docker-compose up -d
```

### Upgrade | 升级

```bash
git pull
docker compose pull
docker compose up -d
```

### Local/Home Deployment (No SSL Required) | 本地/家庭部署 (无需 SSL)

适合在家庭内网使用，无需域名和 SSL 证书，一键部署！

#### 快速开始 | Quick Start

```bash
# 1. 克隆仓库
git clone https://github.com/yourusername/MediCareAI.git
cd MediCareAI

# 2. 配置环境变量 (使用默认密码)
cp .env.example .env

# 3. 一键启动 (使用开发配置，无 SSL)
docker compose -f docker-compose.dev.yml up -d --build

# 4. 等待初始化完成 (约 30 秒)
sleep 30

# 5. 验证部署
curl http://localhost/health
echo "✅ 部署成功！"
```

#### 访问地址 | Access URLs

| 平台 | 地址 | 说明 |
|------|------|------|
| **患者端** | http://localhost | 主平台 |
| **医生端** | http://localhost:8081 | 医生专用 |
| **管理员端** | http://localhost:8080 | 后台管理 |
| **API 文档** | http://localhost/api/docs | Swagger UI |
| **直接访问后端** | http://localhost:8000 | FastAPI 文档 |
| **前端开发服务器** | http://localhost:3000 | Vite HMR |

#### 特点 | Features

- ✅ **无需 SSL 证书** - 纯 HTTP 访问，适合家庭内网
- ✅ **无需域名** - 使用 localhost 或局域网 IP
- ✅ **简化的配置** - 自动使用默认密码
- ✅ **调试友好** - 启用热重载 (HMR) 和详细日志
- ✅ **资源占用低** - 适合个人电脑或家用 NAS

#### 局域网访问 | LAN Access

如果你想在家庭网络的其他设备上访问：

```bash
# 1. 查找本机 IP
ip addr show | grep "inet " | head -1
# 例如: 192.168.1.100

# 2. 修改 .env 文件中的 CORS 配置
# CORS_ORIGINS=["http://localhost", "http://127.0.0.1", "http://192.168.1.100"]

# 3. 重启服务
docker compose -f docker-compose.dev.yml restart
```

然后在其他设备上访问：`http://192.168.1.100`

#### 切换到生产模式 | Switch to Production

当你准备部署到公网时：

```bash
# 停止开发环境
docker compose -f docker-compose.dev.yml down

# 切换到生产配置 (需要 SSL 证书)
docker compose up -d --build
```

---

### Production Deployment | 生产部署

#### Step 1: Server Preparation | 步骤 1: 服务器准备

```bash
# 安装 Docker 和 Docker Compose
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y docker.io docker-compose-plugin

# 或使用官方脚本
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
```

#### Step 2: Clone and Configure | 步骤 2: 克隆和配置

```bash
# 克隆仓库
git clone https://github.com/yourusername/MediCareAI.git
cd MediCareAI

# 配置环境变量
cp .env.example .env
nano .env  # 编辑配置
```

#### Step 3: SSL Certificate Setup | 步骤 3: SSL 证书配置

**Option A: Let's Encrypt (Recommended) | 方式 A: Let's Encrypt (推荐)**

```bash
# 安装 certbot
sudo apt-get install certbot

# 申请证书 (standalone 模式，需要临时停止占用 80 端口的服务)
sudo certbot certonly --standalone -d your-domain.com

# 复制证书到项目目录
sudo mkdir -p docker/nginx/ssl
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem docker/nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem docker/nginx/ssl/key.pem

# 设置正确权限 (重要!)
sudo chown $USER:$USER docker/nginx/ssl/*
chmod 644 docker/nginx/ssl/cert.pem
chmod 600 docker/nginx/ssl/key.pem

# 配置自动续期
echo "0 12 * * * /usr/bin/certbot renew --quiet" | sudo crontab -
```

**Option B: Self-Signed (Testing Only) | 方式 B: 自签名证书 (仅测试)**

```bash
mkdir -p docker/nginx/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout docker/nginx/ssl/key.pem \
  -out docker/nginx/ssl/cert.pem \
  -subj "/C=CN/ST=State/L=City/O=MediCareAI/CN=localhost"
```

#### Step 4: Deploy | 步骤 4: 部署

```bash
# 构建并启动
docker compose build --no-cache
docker compose up -d

# 等待数据库初始化 (约 15-30 秒)
sleep 20

# 验证状态
docker compose ps
curl https://localhost/health --insecure
curl https://localhost/health --insecure
```

#### Step 6: Reverse Proxy Configuration | 步骤 6: 反向代理配置 (重要!)

当使用 Nginx 作为反向代理时，需要确保后端正确识别 HTTPS 协议，**否则会出现 Mixed Content Error**。

**Verify ProxyHeadersMiddleware is configured**:

确保 `backend/app/main.py` 包含以下配置:

```python
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

app = FastAPI()

# 必须添加此中间件以支持反向代理
app.add_middleware(
    ProxyHeadersMiddleware,
    trusted_hosts=["*"],  # 生产环境应限制为具体的主机
)
```

**此配置的作用**:
- 让 FastAPI 正确识别 `X-Forwarded-Proto: https` 头
- 防止后端生成 HTTP URL 导致的 Mixed Content 错误
- 确保患者端仪表盘等页面能正常加载数据

**故障排除**: 如果遇到 "加载统计数据失败" 或 Mixed Content 错误，请参考:
- [TROUBLESHOOTING.mdx](docs/TROUBLESHOOTING.mdx) - Issue 8
- [PRODUCTION_DEPLOYMENT.mdx](docs/PRODUCTION_DEPLOYMENT.mdx) - 反向代理配置章节

---

#### Step 5: Firewall Configuration | 步骤 5: 防火墙配置

```bash
# 开放必要端口
sudo ufw allow 80/tcp      # HTTP (自动重定向到 HTTPS)
sudo ufw allow 443/tcp     # HTTPS 患者端
sudo ufw allow 8443/tcp    # HTTPS 医生端
sudo ufw allow 8444/tcp    # HTTPS 管理员端
sudo ufw enable
```

**云服务器安全组配置** (阿里云/腾讯云/AWS):
- 入方向开放: 80, 443, 8443, 8444 TCP 端口

### Access Application | 访问应用

#### Development | 开发环境
- **Frontend | 前端:** http://localhost
- **API Docs | API 文档:** http://localhost/api/docs
- **Health Check | 健康检查:** http://localhost/health

#### Production | 生产环境

| 平台 | HTTP 地址 | HTTPS 地址 | 说明 |
|------|----------|-----------|------|
| **患者端** | http://your-domain.com | https://your-domain.com | 主平台 |
| **医生端** | http://your-domain.com:8081 | https://your-domain.com:8443 | 医生专用 |
| **管理员端** | http://your-domain.com:8080 | https://your-domain.com:8444 | 后台管理 |
| **API 文档** | - | https://your-domain.com/api/docs | Swagger UI |

### Default Admin Account | 默认管理员账号

系统启动后会自动创建默认管理员账号：
- **邮箱 | Email:** `admin@medicare.ai`
- **密码 | Password:** `admin123456`
- **角色 | Role:** `admin (super)`

⚠️ **安全提示 | Security Notice:** 请在首次登录后立即修改密码！

### First-Time Deployment Configuration | 首次部署配置

**⚠️ 重要提示：现在需要手动配置管理员密码 | IMPORTANT: Manual admin password configuration now required**

由于安全加固，我们已经移除了 docker-compose.yml 中的硬编码密码。首次部署时，你需要：

#### 1. 设置数据库密码 | Set Database Password

编辑 `.env` 文件，设置强密码：

```bash
# PostgreSQL 密码（至少16位，包含大小写字母、数字和特殊字符）
POSTGRES_PASSWORD=YourStrongPassword123!

# Redis 密码
REDIS_PASSWORD=YourRedisPassword456!
```

#### 2. 配置安全设置 | Configure Security Settings

根据你的部署环境配置以下变量：

**本地开发环境 | Local Development:**
```bash
# 允许所有来源（仅开发环境）
CORS_ORIGINS=["*"]
ALLOWED_HOSTS=["*"]
TRUSTED_PROXY_HOSTS=["*"]
DEBUG=true
ENV=development
```

**生产环境 | Production Environment:**
```bash
# 只允许特定域名（必须修改为你的实际域名）
CORS_ORIGINS=["https://your-domain.com", "https://admin.your-domain.com", "https://doctor.your-domain.com"]
ALLOWED_HOSTS=["your-domain.com", "admin.your-domain.com", "doctor.your-domain.com"]
TRUSTED_PROXY_HOSTS=["nginx", "127.0.0.1", "10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"]
DEBUG=false
ENV=production
```

#### 3. 创建管理员账号 | Create Admin Account

系统首次启动时会自动创建默认管理员账号：
- **邮箱:** `admin@medicare.ai`
- **密码:** `admin123456`

**首次登录后必须立即：**
1. 登录管理员后台
2. 进入「系统设置」→「管理员管理」
3. 修改默认密码
4. 配置 AI 模型参数
5. 配置邮件服务（用于发送医生审核通知）

#### 4. 启动应用 | Start Application

```bash
# 开发环境
docker-compose up -d

# 生产环境
docker-compose -f docker-compose.prod.yml up -d
```

---

## 🏗️ Architecture | 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                    Nginx Reverse Proxy                          │
│         (Ports: 80→443 HTTP/HTTPS, 8443 Doctor, 8444 Admin)     │
├─────────────────────────────────────────────────────────────────┤
│  ┌───────────────┬───────────────┬───────────────────────────┐  │
│  │  Patient      │   Doctor      │     Admin                 │  │
│  │  Port 443     │   Port 8443   │    Port 8444              │  │
│  │  (HTTPS)      │   (HTTPS)     │    (HTTPS)                │  │
│  └───────┬───────┴───────┬───────┴───────────┬───────────────┘  │
│          │               │                   │                  │
└──────────┼───────────────┼───────────────────┼──────────────────┘
           │               │                   │
           ▼               ▼                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Backend API                              │
│                     FastAPI (Port 8000)                         │
└───────────────────────────┬─────────────────────────────────────┘
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
                    │   AI LLM API     │
                    │ (OpenAI-compatible│
                    │    API Support)  │
                    └──────────────────┘
```

### Multi-Platform Architecture | 多平台架构

MediCareAI uses a **multi-platform architecture** where each role has dedicated access points:

```
┌─────────────────────────────────────────────────────────────┐
│                         Users                               │
├─────────────────┬─────────────────┬─────────────────────────┤
│    Patients     │    Doctors      │       Admins            │
│                 │                 │                         │
│  ┌───────────┐  │  ┌───────────┐  │  ┌─────────────────┐    │
│  │   Port    │  │  │   Port    │  │  │      Port       │    │
│  │   443     │  │  │  8443     │  │  │     8444        │    │
│  │  (HTTPS)  │  │  │  (HTTPS)  │  │  │    (HTTPS)      │    │
│  └─────┬─────┘  │  └─────┬─────┘  │  └────────┬────────┘    │
│        │        │        │        │           │             │
│        ▼        │        ▼        │           ▼             │
│  ┌───────────┐  │  ┌───────────┐  │  ┌─────────────────┐    │
│  │  Patient  │  │  │  Doctor   │  │  │      Admin      │    │
│  │  Platform │  │  │  Platform │  │  │     Platform    │    │
│  │           │  │  │           │  │  │                 │    │
│  │ • Submit  │  │  │ • View    │  │  │ • System        │    │
│  │   cases   │  │  │   cases   │  │  │   monitoring    │    │
│  │ • AI diag │  │  │ • Add     │  │  │ • Doctor        │    │
│  │ • Records │  │  │   comments│  │  │   verification  │    │
│  └───────────┘  │  └───────────┘  │  └─────────────────┘    │
└─────────────────┴─────────────────┴─────────────────────────┘
```

### Architecture Components | 架构组件

**English:**
- **Frontend**: React 18 + TypeScript + Vite, Material-UI v6, three platforms (Patient/Doctor/Admin)
- **Backend**: FastAPI (Python 3.12) with async SQLAlchemy ORM
- **Database**: PostgreSQL 17 for data persistence
- **Cache**: Redis 7.4 for session and data caching
- **AI Engine**: OpenAI-compatible API support with RAG (Retrieval-Augmented Generation)
- **Document AI**: MinerU API for intelligent text extraction
- **Cloud Storage**: Alibaba Cloud OSS for secure patient document storage
- **Vector Database**: Qwen API for knowledge base embeddings and semantic search

**中文:**
- **前端**: React 18 + TypeScript + Vite，Material-UI v6 组件库，三端平台（患者/医生/管理员）
- **后端**: FastAPI (Python 3.12)，使用异步 SQLAlchemy ORM
- **数据库**: PostgreSQL 17 用于数据持久化
- **缓存**: Redis 7.4 用于会话和数据缓存
- **AI 引擎**: 支持 OpenAI 兼容 API，带 RAG（检索增强生成）
- **文档 AI**: MinerU API 用于智能文本提取
- **云存储**: 阿里云 OSS 用于患者文档安全存储
- **向量数据库**: Qwen API 用于知识库嵌入和语义搜索

---

## 📁 Project Structure | 项目结构

```
MediCareAI/
├── 📁 backend/                    # Backend - 后端
│   ├── 📁 app/
│   │   ├── 📁 api/               # API Routes - API 路由
│   │   │   └── 📁 api_v1/
│   │   │       ├── 📁 endpoints/ # API Endpoints - API 端点
│   │   │       │   ├── auth.py                  # Authentication - 认证
│   │   │       │   ├── patients.py              # Patient CRUD - 患者管理
│   │   │       │   ├── ai.py                    # AI Diagnosis - AI 诊断
│   │   │       │   ├── medical_cases.py         # Medical Records - 医疗记录
│   │   │       │   ├── documents.py             # File Upload - 文件上传
│   │   │       │   ├── admin.py                 # Admin System - 管理员系统
│   │   │       │   ├── sharing.py               # Data Sharing - 数据分享
│   │   │       │   ├── doctor.py                # Doctor Platform - 医生平台
│   │   │       │   ├── chronic_diseases.py      # Chronic Disease - 慢性病管理
│   │   │       │   ├── monitoring.py            # System Monitoring - 系统监控
│   │   │       │   ├── messages.py              # Messages - 站内信
│   │   │       │   └── vector_embedding.py      # Vector Operations - 向量操作
│   │   │       └── api.py
│   │   ├── 📁 core/              # Core Config - 核心配置
│   │   ├── 📁 models/            # Database Models - 数据库模型 (22 tables)
│   │   ├── 📁 schemas/           # Pydantic Schemas - 数据验证模式
│   │   ├── 📁 services/          # Business Logic - 业务逻辑层
│   │   │   ├── ai_service.py                  # AI Diagnosis - AI 诊断
│   │   │   ├── ai_model_config_service.py     # AI Model Management - AI 模型管理
│   │   │   ├── ai_provider_adapters.py        # AI Provider Adapters - AI提供商适配器
│   │   │   ├── data_sharing_consent_service.py # Data Sharing Consent - 数据分享同意服务
│   │   │   ├── data_sharing_service.py        # Data Sharing - 数据分享服务
│   │   │   ├── document_service.py            # Document Service - 文档服务
│   │   │   ├── document_tasks.py              # Document Tasks - 文档处理任务
│   │   │   ├── dynamic_config_service.py      # Dynamic Config - 动态配置服务
│   │   │   ├── embedding_provider_registry.py # Embedding Provider Registry - 嵌入模型注册表
│   │   │   ├── generic_rag_selector.py        # Smart RAG - 智能检索
│   │   │   ├── kb_analyzer.py                 # KB Analyzer - 知识库分析器
│   │   │   ├── kb_vectorization_service.py    # KB Vectorization - 知识库向量化
│   │   │   ├── knowledge_base_service.py      # Knowledge Base - 知识库服务
│   │   │   ├── medical_case_service.py        # Medical Case Service - 病例服务
│   │   │   ├── mineru_service.py              # MinerU Service - MinerU文档服务
│   │   │   ├── monitoring_service.py          # System Monitoring - 系统监控
│   │   │   ├── oss_service.py                 # Alibaba Cloud OSS - 阿里云 OSS
│   │   │   ├── pii_cleaner_service.py         # PII Cleaning - PII 清洗
│   │   │   ├── reranking_provider_adapter.py  # Reranking Provider Adapters - 重排序提供商适配器
│   │   │   ├── reranking_service.py           # Reranking Service - 重排序服务
│   │   │   ├── unified_kb_service.py          # Unified KB - 统一知识库
│   │   │   └── vector_embedding_service.py    # Vector Embedding - 向量嵌入服务
│   │   ├── 📁 db/                # Database - 数据库
│   │   ├── 📁 migrations/        # Database Migrations - 数据库迁移
│   │   │   └── versions/
│   │   ├── 📁 utils/             # Utilities - 工具函数
│   │   └── main.py               # Application Entry - 应用入口
│   ├── 📁 data/
│   │   └── 📁 knowledge_bases/   # Knowledge Base - 知识库
│   │       └── 📁 unified/       # Unified KB - 统一知识库 (扁平化存储)
│   ├── 📁 tests/                 # Tests - 测试
│   ├── 📁 uploads/               # Uploads - 上传文件
│   ├── Dockerfile                # Backend Container - 后端容器
│   ├── entrypoint.sh             # Entry Script - 启动脚本
│   └── requirements.txt          # Python Dependencies - Python依赖
├── 📁 frontend/                  # Frontend - 前端 (React + TypeScript + Vite)
│   ├── 📁 src/                   # Source Code - 源代码
│   │   ├── 📁 components/        # Shared Components - 共享组件
│   │   │   ├── layout/           # Layout Components - 布局组件
│   │   │   │   ├── PatientLayout.tsx
│   │   │   │   ├── DoctorLayout.tsx
│   │   │   │   └── AdminLayout.tsx
│   │   │   └── ProtectedRoute.tsx
│   │   ├── 📁 pages/             # Page Components - 页面组件
│   │   │   ├── 📁 auth/          # Auth Pages - 认证页面
│   │   │   │   ├── LoginPage.tsx
│   │   │   │   ├── RegisterPage.tsx
│   │   │   │   ├── DoctorLoginPage.tsx
│   │   │   │   ├── DoctorRegister.tsx
│   │   │   │   ├── AdminLoginPage.tsx
│   │   │   │   └── PlatformSelect.tsx
│   │   │   ├── 📁 patient/       # Patient Pages - 患者端页面
│   │   │   │   ├── Dashboard.tsx
│   │   │   │   ├── SymptomSubmit.tsx
│   │   │   │   ├── MedicalRecords.tsx
│   │   │   │   ├── MedicalRecordDetail.tsx
│   │   │   │   └── Profile.tsx
│   │   │   ├── 📁 doctor/        # Doctor Pages - 医生端页面
│   │   │   │   ├── Dashboard.tsx
│   │   │   │   ├── Cases.tsx
│   │   │   │   ├── CaseDetail.tsx
│   │   │   │   ├── Mentions.tsx
│   │   │   │   ├── Messages.tsx
│   │   │   │   ├── Export.tsx
│   │   │   │   ├── Profile.tsx
│   │   │   │   └── Register.tsx
│   │   │   └── 📁 admin/         # Admin Pages - 管理员端页面
│   │   │       ├── Dashboard.tsx
│   │   │       ├── Doctors.tsx
│   │   │       ├── KnowledgeBase.tsx
│   │   │       ├── AIModels.tsx
│   │   │       ├── Logs.tsx
│   │   │       └── Messages.tsx
│   │   ├── 📁 services/          # API Services - API服务
│   │   │   └── api.ts            # API Client - API客户端
│   │   ├── 📁 types/             # TypeScript Types - 类型定义
│   │   │   └── index.ts
│   │   ├── 📁 lib/               # Utilities - 工具函数
│   │   │   ├── config.ts         # Global Config - 全局配置
│   │   │   └── utils.ts          # Utility Functions - 工具函数
│   │   ├── 📁 store/             # State Management - 状态管理
│   │   │   └── authStore.ts      # Auth Store - 认证状态
│   │   ├── 📁 hooks/             # Custom Hooks - 自定义Hooks
│   │   │   └── useAuth.ts        # Auth Hook - 认证Hook
│   │   ├── 📁 contexts/          # React Contexts - 上下文
│   │   │   └── AuthContext.tsx
│   │   ├── App.tsx               # App Component - 应用组件
│   │   └── index.tsx             # Entry Point - 入口文件
│   ├── 📁 public/                # Public Assets - 静态资源
│   ├── 📁 build/                 # Build Output - 构建输出
│   ├── index.html                # HTML Entry - HTML入口
│   ├── package.json              # Node Dependencies - Node依赖
│   ├── tsconfig.json             # TypeScript Config - TS配置
│   ├── vite.config.ts            # Vite Config - Vite配置
│   ├── eslint.config.js          # ESLint Config - ESLint配置
│   ├── Dockerfile                # Frontend Container - 前端容器
│   └── Dockerfile.prod           # Production Container - 生产容器
├── 📁 docker/                    # Docker Config - Docker 配置
│   ├── 📁 nginx/                 # Nginx Configuration - Nginx 配置
│   │   └── ssl/                  # SSL Certificates - SSL 证书
│   ├── 📁 postgres/              # PostgreSQL Setup - PostgreSQL 设置
│   ├── 📁 grafana/               # Grafana Monitoring - Grafana 监控
│   │   ├── dashboards/           # Dashboard JSON - 仪表板配置
│   │   └── provisioning/         # Provisioning Config - 自动配置
│   └── 📁 prometheus/            # Prometheus Monitoring - Prometheus 监控
│       └── prometheus.yml        # Prometheus Config - 配置文件
├── 📁 docs/                      # Documentation - 文档
│   ├── DEPLOYMENT.mdx            # Deployment Guide - 部署指南
│   ├── ARCHITECTURE.mdx          # System Design - 架构设计
│   ├── API.mdx                   # API Reference - API 参考
│   ├── TESTING.mdx               # Testing Guide - 测试指南
│   ├── AI_ASSISTANT.mdx          # AI Assistant Context - AI 助手上下文
│   ├── SELINUX-GUIDE.mdx         # SELinux Configuration - SELinux 配置指南
│   └── TROUBLESHOOTING.mdx       # Troubleshooting Guide - 故障排除指南
├── 📁 scripts/                   # Utility Scripts - 实用脚本
│   ├── backup.sh                 # Backup Script - 备份脚本
│   ├── test_integration.sh       # Integration Test - 集成测试
│   ├── test_login.sh             # Login Test - 登录测试
│   └── cleanup-docker.sh         # Docker Cleanup - Docker 清理
├── docker-compose.yml            # Docker Compose Config - 编排配置
├── docker-compose.prod.yml       # Production Config - 生产配置
├── .env.example                  # Environment Template - 环境模板
├── README.md                     # This File - 本文件
├── CHANGELOG.md                  # Changelog - 变更日志
├── CONTRIBUTING.md               # Contributing - 贡献指南
├── CODE_OF_CONDUCT.md            # Code of Conduct - 行为准则
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
| **AI Configuration** | **AI 配置** | | |
| `AI_API_KEY` | AI model API key | AI 模型 API 密钥 | Yes |
| `AI_API_URL` | AI model endpoint URL | AI 模型端点 URL | Yes |
| `AI_MODEL_ID` | AI model identifier | AI 模型标识符 | Yes |
| **Document Processing** | **文档处理** | | |
| `MINERU_TOKEN` | MinerU API authentication token | MinerU API 认证令牌 | Yes |
| `MAX_FILE_SIZE` | Max upload file size (bytes) | 最大上传文件大小（字节） | No (default: 200MB) |
| **Alibaba Cloud OSS** | **阿里云对象存储** | | |
| `OSS_ACCESS_KEY_ID` | Alibaba Cloud Access Key ID | 阿里云访问密钥 ID | Yes |
| `OSS_ACCESS_KEY_SECRET` | Alibaba Cloud Access Key Secret | 阿里云访问密钥 Secret | Yes |
| `OSS_BUCKET_NAME` | OSS Bucket name for document storage | 文档存储 Bucket 名称 | Yes |
| `OSS_ENDPOINT` | OSS Endpoint (e.g., oss-cn-beijing.aliyuncs.com) | OSS 端点地址 | Yes |
| **Vector Database** | **向量数据库** | | |
| `QWEN_API_KEY` | Qwen API key for embeddings | Qwen API 密钥（用于向量嵌入） | Yes |
| `QWEN_API_URL` | Qwen API endpoint | Qwen API 端点 | Yes |
| `QWEN_EMBEDDING_MODEL` | Embedding model ID | 嵌入模型 ID | No (default: text-embedding-v1) |
| **System** | **系统** | | |
| `DEBUG` | Enable debug mode | 启用调试模式 | No (default: false) |

See [`.env.example`](.env.example) for full configuration template.

---

## 📚 Documentation | 文档导航

### Core Documentation | 核心文档

#### Getting Started | 入门指南
- **[📖 README.md](README.md)** - This file / 本文件 (Overview & Quick Start)
- **[🚀 DEPLOYMENT.mdx](docs/DEPLOYMENT.mdx)** - Detailed deployment guide / 详细部署指南
- **[🚀 PRODUCTION_DEPLOYMENT.mdx](docs/PRODUCTION_DEPLOYMENT.mdx)** - **⚠️ 生产环境部署指南** / Production deployment checklist & security hardening
  - 开发环境迁移到生产环境的完整步骤
  - CORS、SSL/TLS、数据库安全配置
  - 生产环境安全检查清单

#### System Documentation | 系统文档
- **[🏗️ ARCHITECTURE.mdx](docs/ARCHITECTURE.mdx)** - System architecture & design / 系统架构与设计
- **[🔌 API.mdx](docs/API.mdx)** - Complete API reference / 完整 API 参考
- **[🤖 AI_ASSISTANT.mdx](docs/AI_ASSISTANT.mdx)** - AI assistant context / AI 助手上下文
- **[🔍 RAG_OPTIMIZATION.mdx](docs/RAG_OPTIMIZATION.mdx)** - RAG optimization implementation / RAG优化实施文档（混合检索、HyDE、上下文压缩）

#### Recent Updates & Fixes | 近期更新与修复
- **[📧 EMAIL_CONFIG_VERIFICATION.mdx](docs/EMAIL_CONFIG_VERIFICATION.mdx)** - Email service configuration / 邮件服务配置验证文档
- **[📊 DATA_EXPORT_FIX.mdx](docs/DATA_EXPORT_FIX.mdx)** - Data export fix summary / 数据导出修复总结
- **[📝 REGISTRATION_FIX.mdx](docs/REGISTRATION_FIX.mdx)** - Registration flow fixes / 注册流程修复文档

#### Development & Maintenance | 开发与维护
- **[🤝 CONTRIBUTING.md](CONTRIBUTING.md)** - Development guidelines / 开发指南
- **[📝 CHANGELOG.md](CHANGELOG.md)** - Full release history / 完整版本历史
- **[🆘 TROUBLESHOOTING.mdx](docs/TROUBLESHOOTING.mdx)** - Troubleshooting & emergency fixes / 故障排除与应急修复
- **[🧪 TESTING.mdx](docs/TESTING.mdx)** - Testing guide / 测试指南

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

## 🔧 Utility Scripts | 实用脚本

位于 `scripts/` 目录：

- **`backup.sh`** - 备份数据库和配置文件 / Backup database and config files
- **`test_integration.sh`** - 集成测试 / Integration testing
- **`test_login.sh`** - 登录测试 / Login testing

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
# Install dependencies / 安装依赖
npm install

# Start development server / 启动开发服务器
npm run dev

# Build for production / 构建生产版本
npm run build
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

Copyright (c) 2025 MediCareAI Contributors

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

- **AI LLM**: OpenAI-compatible API support / 支持 OpenAI 兼容 API
- **MinerU**: Document processing and text extraction / 文档处理和文本提取
- **FastAPI**: Modern, fast web framework / 现代快速 Web 框架
- **PostgreSQL**: Powerful open-source database / 强大的开源数据库
- **OpenXLab**: AI model hosting platform / AI 模型托管平台

---

## 📞 Support | 支持

- **Issues**: [GitHub Issues](https://github.com/yourusername/MediCareAI/issues)
- **Documentation**: [Full Documentation](docs/)
- **Email**: hougelangley1987@gmail.com
---

## ☕ 支持作者 | Support the Author

<p align="center">
  <strong>如果这个项目对您有帮助，欢迎请我喝杯咖啡 ☕</strong><br>
  <strong>If this project helps you, consider buying me a coffee ☕</strong>
</p>

<p align="center">
  作为一名独立开发者，我投入了大量时间和精力来开发和维护这个项目。<br>
  MediCareAI 将始终<strong>免费开源</strong>，让每个人都能享受到 AI 带来的医疗便利。<br><br>
  您的每一份支持，都能帮助这个项目持续改进：
</p>

<p align="center">
  ✨ 支付服务器和 API 调用成本<br>
  ✨ 开发更多实用功能<br>
  ✨ 保持项目的长期维护与更新
</p>

<p align="center">
  <strong>无论金额大小，都是对我莫大的鼓励，谢谢！🙏</strong><br>
  <strong>Every donation, no matter how small, means a lot. Thank you! 🙏</strong>
</p>

<p align="center">
  <img src="qrcode.png" alt="微信收款码 | WeChat Pay" width="280">
</p>

<p align="center">
  <sub>微信扫码支持 | Scan with WeChat to support</sub>
</p>

---
<p align="center">
  <b>MediCareAI</b> - Empowering Healthcare with AI / 用 AI 赋能医疗健康
</p>

<p align="center">
  Made with ❤️ for better healthcare / 为更好的医疗而造
</p>
