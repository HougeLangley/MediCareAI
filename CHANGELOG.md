# Changelog | 更新日志

All notable changes to this project will be documented in this file.
本项目的所有重要变更都将记录在此文件中。

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

格式基于 [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)，
并且本项目遵循 [语义化版本](https://semver.org/spec/v2.0.0.html)。

---

## [1.0.1] - 2025-02-01

### Fixed | 修复

#### Critical Bug Fixes | 关键错误修复
- **Fixed SQLAlchemy relationship comment parameter error** / 修复 SQLAlchemy relationship comment 参数错误
  - Removed unsupported `comment` parameter from all `relationship()` definitions / 从所有 `relationship()` 定义中移除不支持的 `comment` 参数
  - Fixed backend container crash on startup / 修复后端容器启动时崩溃问题
  - Affected 11 relationship definitions across models / 影响模型中的 11 处关系定义
  - Error: `TypeError: RelationshipProperty.__init__() got an unexpected keyword argument 'comment'` / 错误：`TypeError: RelationshipProperty.__init__() got an unexpected keyword argument 'comment'`

#### Documentation Updates | 文档更新
- **Updated GLM_FLASH_SUCCESS_REPORT.md** / 更新 GLM_FLASH_SUCCESS_REPORT.md
  - Converted to comprehensive local deployment guide / 转换为全面的本地部署指南
  - Added deployment instructions for Ollama, llama.cpp, vLLM, SGLang, TGI / 添加 Ollama、llama.cpp、vLLM、SGLang、TGI 的部署说明
  - Added local MinerU deployment guide / 添加本地 MinerU 部署指南
  - Removed all sensitive information (IPs, API keys, tokens) / 移除所有敏感信息（IP、API 密钥、令牌）

- **Added comprehensive bilingual documentation** / 添加全面的双语文档
  - README.md with Chinese-English content / 包含中英文内容的 README.md
  - DEPLOYMENT.md with detailed deployment instructions / 包含详细部署说明的 DEPLOYMENT.md
  - ARCHITECTURE.md with system design documentation / 包含系统设计文档的 ARCHITECTURE.md
  - API.md with complete API reference / 包含完整 API 参考的 API.md
  - Comprehensive code comments in key files / 关键文件中的全面代码注释

#### Security Improvements | 安全改进
- **Sanitized all configuration files** / 清理所有配置文件
  - Removed real API keys and tokens from .env.example / 从 .env.example 中移除真实 API 密钥和令牌
  - Replaced with placeholder values / 替换为占位符值
  - Removed sensitive files containing internal IPs and credentials / 移除包含内部 IP 和凭据的敏感文件

#### Technical Memo | 技术备忘录
- **Added TECHNICAL_MEMO_ISSUE_ANALYSIS.md** / 添加 TECHNICAL_MEMO_ISSUE_ANALYSIS.md
  - Detailed incident report / 详细的事件报告
  - Root cause analysis / 根本原因分析
  - Solution and lessons learned / 解决方案和经验教训
  - Preventive measures / 预防措施

---

## [1.0.0] - 2025-02-01

### Added | 新增

#### Core Features | 核心功能
- **User Authentication System** - 用户认证系统
  - JWT-based authentication with refresh tokens / 基于 JWT 的认证，支持刷新令牌
  - User registration and login / 用户注册和登录
  - Password hashing with bcrypt / 使用 bcrypt 进行密码哈希
  - Session management / 会话管理

- **Patient Management** - 患者管理
  - Comprehensive patient profiles / 全面的患者档案
  - Personal information management / 个人信息管理
  - Emergency contact details / 紧急联系人详情
  - Medical record number assignment / 病历号分配

- **AI-Powered Diagnosis** - AI 智能诊断
  - Integration with GLM-4.7-Flash AI model / 集成 GLM-4.7-Flash AI 模型
  - Comprehensive diagnosis workflow / 综合诊断流程
  - Real-time symptom analysis / 实时症状分析
  - Follow-up plan generation / 随访计划生成
  - Confidence scoring / 置信度评分

- **Document Processing** - 文档处理
  - MinerU API integration / MinerU API 集成
  - PDF and image text extraction / PDF 和图片文本提取
  - Structured data extraction / 结构化数据提取
  - Document upload and management / 文档上传和管理

- **Medical Records** - 医疗记录
  - Case-based record management / 基于病例的记录管理
  - Document attachment support / 文档附件支持
  - AI feedback tracking / AI 反馈追踪
  - Medical history tracking / 病史追踪

- **Knowledge Base** - 知识库
  - Modular medical guidelines system / 模块化医疗指南系统
  - Multi-disease support / 多疾病支持
  - Evidence-based recommendations / 循证建议
  - Guidelines integration with AI diagnosis / 指南与 AI 诊断集成

#### Technical Implementation | 技术实现
- **Backend** - 后端
  - FastAPI framework with Python 3.11 / FastAPI 框架，Python 3.11
  - Async SQLAlchemy ORM with PostgreSQL / 异步 SQLAlchemy ORM，PostgreSQL
  - Pydantic data validation / Pydantic 数据验证
  - Dependency injection pattern / 依赖注入模式
  - Service layer architecture / 服务层架构

- **Frontend** - 前端
  - Vanilla HTML/CSS/JavaScript / 原生 HTML/CSS/JavaScript
  - Responsive design / 响应式设计
  - JWT token management / JWT 令牌管理
  - Form validation / 表单验证

- **Infrastructure** - 基础设施
  - Docker containerization / Docker 容器化
  - Docker Compose orchestration / Docker Compose 编排
  - Nginx reverse proxy / Nginx 反向代理
  - Redis caching / Redis 缓存
  - PostgreSQL 17 database / PostgreSQL 17 数据库

#### Documentation | 文档
- Comprehensive bilingual documentation (Chinese-English) / 全面的双语文档（中英文）
- README.md with quick start guide / 包含快速开始指南的 README.md
- DEPLOYMENT.md with detailed deployment instructions / 包含详细部署说明的 DEPLOYMENT.md
- ARCHITECTURE.md with system design / 包含系统设计的 ARCHITECTURE.md
- API.md with complete API reference / 包含完整 API 参考的 API.md
- AGENTS.md for AI assistant context / 用于 AI 助手上下文的 AGENTS.md
- CONTRIBUTING.md with development guidelines / 包含开发指南的 CONTRIBUTING.md
- CODE_OF_CONDUCT.md for community standards / 社区标准的 CODE_OFDUCT.md

### Security | 安全性
- JWT authentication with configurable expiration / 可配置过期时间的 JWT 认证
- Password hashing using bcrypt / 使用 bcrypt 进行密码哈希
- CORS configuration / CORS 配置
- Input validation with Pydantic / 使用 Pydantic 进行输入验证
- SQL injection prevention via parameterized queries / 通过参数化查询防止 SQL 注入
- HTTPS support via Nginx SSL / 通过 Nginx SSL 支持 HTTPS

### Changed | 变更
- Updated Docker images to latest versions / 将 Docker 镜像更新到最新版本
  - PostgreSQL: 15 → 17 / PostgreSQL: 15 → 17
  - Redis: 7 → 7.4 / Redis: 7 → 7.4
  - Node.js: 18 → 22 / Node.js: 18 → 22

### Fixed | 修复
- Emergency contact field split into name and phone / 紧急联系人字段拆分为姓名和电话
- Patient data binding during registration / 注册期间的患者数据绑定
- User profile data display consistency / 用户档案数据显示一致性

---

## Release History | 发布历史

### Version 1.0.0 (2025-02-01)
**Initial Production Release** | 初始生产版本

This is the first stable release of MediCare_AI, featuring a complete AI-powered disease management system.

这是 MediCare_AI 的第一个稳定版本，包含完整的 AI 智能疾病管理系统。

**Key Highlights:**
- Complete user authentication and patient management
- AI diagnosis with GLM-4.7-Flash integration
- Document processing with MinerU
- Comprehensive medical records system
- Modular knowledge base architecture
- Full Docker containerization
- Bilingual documentation

---

## Upcoming Features | 即将推出的功能

### Planned for v1.1.0
- [ ] Multi-language support (i18n) / 多语言支持
- [ ] Advanced analytics dashboard / 高级分析仪表盘
- [ ] Email notification system / 邮件通知系统
- [ ] Mobile app (React Native) / 移动应用
- [ ] Enhanced AI model fine-tuning / 增强的 AI 模型微调

### Planned for v1.2.0
- [ ] Multi-tenancy support / 多租户支持
- [ ] Advanced role-based access control / 高级基于角色的访问控制
- [ ] Integration with external EHR systems / 与外部 EHR 系统集成
- [ ] Real-time collaboration features / 实时协作功能
- [ ] Advanced reporting and statistics / 高级报告和统计

---

## Migration Guides | 迁移指南

### Upgrading from v0.x to v1.0.0

**Database Migration:**
```bash
# Backup your data first / 首先备份数据
docker-compose exec postgres pg_dump -U medicare_user medicare_ai > backup.sql

# Pull latest changes / 拉取最新更改
git pull origin main

# Rebuild containers / 重建容器
docker-compose down
docker-compose up -d --build

# Initialize database / 初始化数据库
docker-compose exec backend python -c "
import asyncio
from app.db.init_db import init_db
asyncio.run(init_db())
"
```

**Configuration Changes:**
- Update `.env` file with new variables / 使用新变量更新 `.env` 文件
- Review updated Docker Compose configuration / 检查更新的 Docker Compose 配置
- Update Nginx configuration if customized / 如果自定义则更新 Nginx 配置

---

## Contributors | 贡献者

A big thank you to all contributors who helped make this release possible!

非常感谢所有帮助实现此版本的贡献者！

### Core Team | 核心团队
- Architecture & Backend Development / 架构和后端开发
- Frontend Development / 前端开发
- AI Integration / AI 集成
- Documentation / 文档

### Special Thanks | 特别感谢
- GLM-4.7-Flash Team for the AI model / GLM-4.7-Flash 团队提供 AI 模型
- MinerU Team for document processing / MinerU 团队提供文档处理
- FastAPI Community for the excellent framework / FastAPI 社区提供优秀的框架

---

## Feedback | 反馈

We welcome your feedback! Please report issues or suggest features:

我们欢迎您的反馈！请报告问题或建议功能：

- **Issues**: [GitHub Issues](https://github.com/yourusername/MediCare_AI/issues)
- **Email**: support@medicare-ai.example.com
- **Documentation**: [Full Docs](docs/)

---

**Last Updated | 最后更新:** 2025-02-01  
**Current Version | 当前版本:** 1.0.0  
**Maintained by | 维护者:** MediCare_AI Team
