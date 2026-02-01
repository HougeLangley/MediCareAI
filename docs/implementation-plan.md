# MediCare_AI 完整实施计划

## 1. 技术栈选择

### 后端技术栈
- **FastAPI 0.104+**: 高性能异步API框架，自动API文档生成
- **PostgreSQL 15**: 关系型数据库，支持JSON字段，符合HIPAA要求
- **SQLAlchemy 2.0**: 异步ORM，支持复杂查询和数据关系
- **Alembic**: 数据库迁移管理
- **Pydantic V2**: 数据验证和序列化
- **python-jose**: JWT令牌处理
- **bcrypt**: 密码加密
- **httpx**: 异步HTTP客户端（调用外部API）
- **Redis 7**: 缓存和会话存储

### 前端技术栈
- **React 18**: 组件化前端框架
- **TypeScript 5**: 类型安全的JavaScript
- **React Router v6**: 路由管理
- **Axios**: HTTP客户端
- **React Hook Form**: 表单处理
- **Material-UI (MUI) 5**: UI组件库
- **React Query (TanStack Query)**: 服务端状态管理

### 基础设施
- **Docker & Docker Compose**: 容器化部署
- **Nginx**: 反向代理和静态文件服务
- **Let's Encrypt**: SSL证书

## 2. 项目目录结构

```
MediCare_AI/
├── backend/                    # FastAPI后端
│   ├── app/
│   │   ├── api/
│   │   │   └── api_v1/
│   │   │       ├── endpoints/  # API端点
│   │   │       └── api.py      # 路由聚合
│   │   ├── core/               # 核心配置
│   │   │   ├── config.py       # 应用配置
│   │   │   ├── security.py     # 安全相关
│   │   │   └── deps.py         # 依赖注入
│   │   ├── db/                 # 数据库
│   │   │   └── database.py     # 数据库连接
│   │   ├── models/             # 数据模型
│   │   │   └── models.py       # SQLAlchemy模型
│   │   ├── schemas/            # Pydantic模式
│   │   │   ├── user.py         # 用户模式
│   │   │   ├── patient.py      # 患者模式
│   │   │   └── case.py         # 病例模式
│   │   ├── services/           # 业务逻辑
│   │   │   ├── user_service.py # 用户服务
│   │   │   ├── patient_service.py # 患者服务
│   │   │   └── ai_service.py   # AI服务
│   │   └── utils/              # 工具函数
│   ├── tests/                  # 测试
│   ├── alembic/               # 数据库迁移
│   ├── requirements.txt       # Python依赖
│   └── Dockerfile            # Docker配置
├── frontend/                  # React前端
│   ├── src/
│   │   ├── components/        # 可复用组件
│   │   │   ├── common/        # 通用组件
│   │   │   ├── auth/          # 认证组件
│   │   │   └── medical/       # 医疗组件
│   │   ├── pages/             # 页面组件
│   │   │   ├── auth/          # 认证页面
│   │   │   ├── dashboard/     # 仪表板
│   │   │   └── patients/      # 患者管理
│   │   ├── hooks/             # 自定义Hooks
│   │   ├── services/          # API服务
│   │   ├── utils/             # 工具函数
│   │   ├── types/             # TypeScript类型
│   │   └── styles/            # 样式文件
│   ├── package.json           # Node.js依赖
│   └── Dockerfile            # Docker配置
├── docker/                    # Docker配置
│   ├── nginx/                 # Nginx配置
│   ├── postgres/             # PostgreSQL配置
│   └── redis/                 # Redis配置
├── docs/                      # 文档
│   ├── api/                   # API文档
│   ├── development/           # 开发文档
│   └── deployment/            # 部署文档
├── scripts/                   # 部署脚本
├── docker-compose.yml         # Docker编排
├── .env.example              # 环境变量示例
└── .gitignore                # Git忽略文件
```

## 3. 数据库Schema设计

### 核心表结构

#### 用户表 (users)
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    professional_title VARCHAR(100),
    license_number VARCHAR(100),
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE
);
```

#### 疾病表 (diseases)
```sql
CREATE TABLE diseases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) UNIQUE NOT NULL,
    code VARCHAR(50) UNIQUE, -- ICD-10代码
    description TEXT,
    guidelines_json JSONB, -- 存储诊疗指南结构化数据
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### 患者表 (patients)
```sql
CREATE TABLE patients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    date_of_birth DATE NOT NULL,
    gender VARCHAR(10) CHECK (gender IN ('male', 'female', 'other')),
    phone VARCHAR(20),
    address TEXT,
    emergency_contact VARCHAR(255),
    medical_record_number VARCHAR(100) UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### 病例表 (medical_cases)
```sql
CREATE TABLE medical_cases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id UUID NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    disease_id UUID NOT NULL REFERENCES diseases(id),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    symptoms TEXT,
    clinical_findings JSONB, -- 临床检查结果
    diagnosis TEXT,
    severity VARCHAR(20) CHECK (severity IN ('mild', 'moderate', 'severe')),
    status VARCHAR(20) CHECK (status IN ('active', 'resolved', 'chronic')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### 文档表 (medical_documents)
```sql
CREATE TABLE medical_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    medical_case_id UUID NOT NULL REFERENCES medical_cases(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    file_type VARCHAR(50) NOT NULL, -- pdf, doc, image, etc.
    file_size BIGINT,
    file_path VARCHAR(500),
    upload_status VARCHAR(20) DEFAULT 'uploaded' CHECK (upload_status IN ('uploaded', 'processing', 'processed', 'failed')),
    extracted_content JSONB, -- MinerU提取的结构化内容
    extraction_metadata JSONB, -- 提取过程元数据
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### AI诊断反馈表 (ai_feedbacks)
```sql
CREATE TABLE ai_feedbacks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    medical_case_id UUID NOT NULL REFERENCES medical_cases(id) ON DELETE CASCADE,
    feedback_type VARCHAR(50) NOT NULL, -- diagnosis, treatment, follow_up
    input_data JSONB NOT NULL, -- 输入给AI的数据
    ai_response JSONB NOT NULL, -- AI的响应
    confidence_score DECIMAL(3,2), -- 置信度 0.00-1.00
    recommendations TEXT, -- AI建议
    follow_up_plan JSONB, -- 随访计划
    is_reviewed BOOLEAN DEFAULT false,
    reviewed_by UUID REFERENCES users(id),
    review_notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### 随访记录表 (follow_ups)
```sql
CREATE TABLE follow_ups (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    medical_case_id UUID NOT NULL REFERENCES medical_cases(id) ON DELETE CASCADE,
    scheduled_date DATE NOT NULL,
    actual_date DATE,
    follow_up_type VARCHAR(50) NOT NULL, -- phone, video, in_person
    status VARCHAR(20) DEFAULT 'scheduled' CHECK (status IN ('scheduled', 'completed', 'missed', 'cancelled')),
    notes TEXT,
    symptoms_changes TEXT,
    medication_adherence VARCHAR(20), -- good, moderate, poor
    next_follow_up_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### 用户会话表 (user_sessions)
```sql
CREATE TABLE user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_id VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT true
);
```

#### 审计日志表 (audit_logs)
```sql
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    action VARCHAR(100) NOT NULL, -- login, logout, create_patient, upload_doc, etc.
    resource_type VARCHAR(50), -- user, patient, case, document
    resource_id UUID,
    details JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## 4. 核心功能模块分解

### 4.1 用户认证模块
**功能**:
- 用户注册（邮箱验证）
- 用户登录（JWT令牌）
- 密码重置和修改
- 用户会话管理
- 权限验证

**技术实现**:
- FastAPI Security
- JWT令牌认证
- bcrypt密码加密
- 邮件验证服务

### 4.2 疾病管理模块
**功能**:
- 疾病信息管理
- 诊疗指南存储
- 疾病分类和编码
- 指南版本管理

**技术实现**:
- PostgreSQL JSONB存储指南
- 文档版本控制
- 分类标签系统

### 4.3 患者病例管理模块
**功能**:
- 患者信息管理
- 病例创建和编辑
- 临床数据录入
- 病例状态跟踪

**技术实现**:
- 关系型数据库设计
- 表单验证
- 数据完整性检查

### 4.4 文档抽取模块
**功能**:
- 文档上传和存储
- MinerU API集成
- 内容结构化提取
- 提取结果验证

**技术实现**:
- 异步文件处理
- HTTP客户端调用
- JSON数据解析

### 4.5 AI辅助诊断模块
**功能**:
- AI模型调用
- 诊断建议生成
- 置信度评估
- 结果审核

**技术实现**:
- LLM API集成
- 提示工程
- 结果后处理

## 5. API端点设计

### 5.1 认证相关 (/api/v1/auth)
```
POST /api/v1/auth/register          # 用户注册
POST /api/v1/auth/login             # 用户登录
POST /api/v1/auth/logout            # 用户登出
GET  /api/v1/auth/me                # 获取当前用户信息
POST /api/v1/auth/change-password   # 修改密码
POST /api/v1/auth/refresh-token     # 刷新令牌
```

### 5.2 用户管理 (/api/v1/users)
```
GET    /api/v1/users                # 获取用户列表
GET    /api/v1/users/{id}           # 获取用户详情
PUT    /api/v1/users/{id}           # 更新用户信息
DELETE /api/v1/users/{id}           # 删除用户
```

### 5.3 疾病管理 (/api/v1/diseases)
```
GET    /api/v1/diseases             # 获取疾病列表
GET    /api/v1/diseases/{id}        # 获取疾病详情
POST   /api/v1/diseases             # 创建疾病
PUT    /api/v1/diseases/{id}        # 更新疾病信息
DELETE /api/v1/diseases/{id}        # 删除疾病
GET    /api/v1/diseases/{id}/guidelines # 获取诊疗指南
```

### 5.4 患者管理 (/api/v1/patients)
```
GET    /api/v1/patients             # 获取患者列表
POST   /api/v1/patients             # 创建患者
GET    /api/v1/patients/{id}        # 获取患者详情
PUT    /api/v1/patients/{id}        # 更新患者信息
DELETE /api/v1/patients/{id}        # 删除患者
GET    /api/v1/patients/{id}/cases  # 获取患者病例
```

### 5.5 病例管理 (/api/v1/cases)
```
GET    /api/v1/cases                # 获取病例列表
POST   /api/v1/cases                # 创建病例
GET    /api/v1/cases/{id}           # 获取病例详情
PUT    /api/v1/cases/{id}           # 更新病例
DELETE /api/v1/cases/{id}           # 删除病例
GET    /api/v1/cases/{id}/documents # 获取病例文档
GET    /api/v1/cases/{id}/ai-feedback # 获取AI反馈
```

### 5.6 文档管理 (/api/v1/documents)
```
POST   /api/v1/documents/upload      # 上传文档
GET    /api/v1/documents/{id}       # 获取文档信息
DELETE /api/v1/documents/{id}       # 删除文档
POST   /api/v1/documents/{id}/extract # 提取文档内容
GET    /api/v1/documents/{id}/content # 获取提取内容
```

### 5.7 AI服务 (/api/v1/ai)
```
POST   /api/v1/ai/diagnose          # AI诊断
POST   /api/v1/ai/treatment         # AI治疗建议
POST   /api/v1/ai/follow-up         # AI随访计划
GET    /api/v1/ai/feedback/{id}     # 获取AI反馈详情
POST   /api/v1/ai/feedback/{id}/review # 审核AI反馈
```

### 5.8 随访管理 (/api/v1/follow-ups)
```
GET    /api/v1/follow-ups           # 获取随访列表
POST   /api/v1/follow-ups           # 创建随访
GET    /api/v1/follow-ups/{id}      # 获取随访详情
PUT    /api/v1/follow-ups/{id}      # 更新随访
DELETE /api/v1/follow-ups/{id}      # 删除随访
```

## 6. 前端组件设计

### 6.1 认证组件
```
components/auth/
├── LoginForm.tsx           # 登录表单
├── RegisterForm.tsx        # 注册表单
├── PasswordResetForm.tsx   # 密码重置表单
├── ProtectedRoute.tsx      # 路由保护组件
└── AuthProvider.tsx       # 认证上下文
```

### 6.2 通用组件
```
components/common/
├── Layout.tsx              # 页面布局
├── Header.tsx              # 页面头部
├── Sidebar.tsx             # 侧边栏
├── LoadingSpinner.tsx     # 加载动画
├── ErrorBoundary.tsx      # 错误边界
├── ConfirmDialog.tsx      # 确认对话框
└── DataTable.tsx          # 数据表格
```

### 6.3 医疗组件
```
components/medical/
├── PatientCard.tsx         # 患者卡片
├── CaseSummary.tsx         # 病例摘要
├── DocumentUploader.tsx    # 文档上传器
├── AIFeedback.tsx          # AI反馈组件
├── FollowUpCalendar.tsx    # 随访日历
└── ClinicalForm.tsx        # 临床表单
```

### 6.4 页面组件
```
pages/
├── auth/
│   ├── LoginPage.tsx       # 登录页面
│   └── RegisterPage.tsx    # 注册页面
├── dashboard/
│   └── DashboardPage.tsx   # 仪表板页面
├── patients/
│   ├── PatientListPage.tsx # 患者列表页面
│   ├── PatientDetailPage.tsx # 患者详情页面
│   └── CreatePatientPage.tsx # 创建患者页面
├── cases/
│   ├── CaseListPage.tsx    # 病例列表页面
│   ├── CaseDetailPage.tsx  # 病例详情页面
│   └── CreateCasePage.tsx  # 创建病例页面
└── settings/
    └── SettingsPage.tsx    # 设置页面
```

## 7. 实施步骤和优先级

### 阶段1: 基础架构 (高优先级)
1. **项目初始化** - 创建项目结构和基础配置
2. **数据库设计** - 创建数据库schema和迁移脚本
3. **后端基础架构** - FastAPI应用、数据库连接、基础中间件
4. **用户认证系统** - 注册、登录、JWT认证
5. **前端基础架构** - React应用、路由、状态管理

### 阶段2: 核心功能 (中优先级)
6. **疾病管理模块** - 疾病信息管理、指南存储
7. **患者管理模块** - 患者信息CRUD
8. **病例管理模块** - 病例创建、编辑、状态管理
9. **文档上传功能** - 文件上传、存储、基础管理

### 阶段3: AI集成 (中优先级)
10. **MinerU集成** - 文档内容提取
11. **AI诊断模块** - LLM API集成、诊断建议
12. **AI反馈管理** - 结果展示、审核流程

### 阶段4: 高级功能 (低优先级)
13. **随访管理** - 随访计划、提醒系统
14. **数据分析和报表** - 统计图表、导出功能
15. **系统优化** - 性能优化、缓存策略
16. **安全加固** - HIPAA合规、审计日志

### 阶段5: 部署和运维 (低优先级)
17. **Docker部署** - 容器化配置
18. **CI/CD流水线** - 自动化部署
19. **监控和日志** - 系统监控、错误追踪
20. **备份和恢复** - 数据备份策略

## 8. 推荐使用的 CATEGORY + SKILLS

### 8.1 基础架构实施
**CATEGORY**: `quick` 
**SKILLS**: `git-master`, `frontend-ui-ux`

**实施内容**:
- 使用 `git-master` 进行版本控制和代码管理
- 使用 `frontend-ui-ux` 设计用户界面和用户体验

### 8.2 后端API开发
**CATEGORY**: `quick`
**SKILLS**: `git-master`

**实施内容**:
- 使用 `git-master` 进行原子提交和代码管理
- 实现RESTful API端点
- 数据库操作和业务逻辑

### 8.3 前端开发
**CATEGORY**: `quick`
**SKILLS**: `frontend-ui-ux`

**实施内容**:
- 使用 `frontend-ui-ux` 创建响应式UI组件
- 实现用户交互和状态管理
- 优化用户体验

### 8.4 AI集成
**CATEGORY**: `quick`
**SKILLS**: `git-master`

**实施内容**:
- 使用 `git-master` 管理AI集成代码
- 实现外部API调用
- 处理AI响应和数据转换

### 8.5 测试和部署
**CATEGORY**: `quick`
**SKILLS**: `git-master`

**实施内容**:
- 使用 `git-master` 进行代码审查
- 实现自动化测试
- 配置部署流程

## 9. 测试策略

### 9.1 单元测试
**后端测试**:
- 使用 `pytest` 进行API端点测试
- 使用 `pytest-asyncio` 测试异步函数
- 测试覆盖率目标: 90%+

**前端测试**:
- 使用 `Jest` + `React Testing Library` 进行组件测试
- 测试用户交互和状态变化
- 测试覆盖率目标: 85%+

### 9.2 集成测试
**API集成测试**:
- 测试完整的API调用流程
- 测试数据库事务
- 测试外部API集成

**前端集成测试**:
- 使用 `Cypress` 进行端到端测试
- 测试用户完整操作流程
- 测试跨浏览器兼容性

### 9.3 性能测试
**后端性能**:
- 使用 `locust` 进行负载测试
- 测试API响应时间
- 测试数据库查询性能

**前端性能**:
- 使用 `Lighthouse` 进行性能评估
- 测试页面加载时间
- 测试用户交互响应

### 9.4 安全测试
**安全扫描**:
- 使用 `bandit` 进行Python安全扫描
- 使用 `npm audit` 检查前端依赖漏洞
- 测试SQL注入和XSS防护

**HIPAA合规测试**:
- 测试数据加密
- 测试访问控制
- 测试审计日志

### 9.5 测试环境
**开发环境**:
- 本地Docker环境
- 热重载和调试支持

**测试环境**:
- 模拟生产环境配置
- 自动化测试执行

**生产环境**:
- 蓝绿部署策略
- 监控和告警系统

## 10. 质量保证

### 10.1 代码质量
- **代码规范**: 使用 `black` (Python) 和 `Prettier` (JavaScript) 格式化代码
- **代码审查**: 所有代码必须经过同行审查
- **静态分析**: 使用 `mypy` (Python) 和 `ESLint` (JavaScript) 进行静态分析

### 10.2 文档质量
- **API文档**: 使用FastAPI自动生成的OpenAPI文档
- **代码文档**: 关键函数和类必须有详细文档
- **用户文档**: 提供完整的用户使用指南

### 10.3 部署质量
- **自动化部署**: 使用CI/CD流水线
- **回滚策略**: 支持快速回滚到稳定版本
- **健康检查**: 实现应用和数据库健康检查

## 11. 风险管理

### 11.1 技术风险
- **API依赖**: 外部API服务不可用的备用方案
- **数据安全**: 实现多层安全防护
- **性能瓶颈**: 提前进行性能测试和优化

### 11.2 业务风险
- **合规要求**: 确保HIPAA合规性
- **数据质量**: 实现数据验证和清洗
- **用户体验**: 持续收集用户反馈并改进

### 11.3 运维风险
- **系统可用性**: 实现高可用架构
- **数据备份**: 定期备份和恢复测试
- **监控告警**: 完善的监控和告警系统

---

**总结**: 本实施计划提供了MediCare_AI项目的完整技术路线图，涵盖了从基础架构到高级功能的所有方面。通过分阶段实施和严格的质量控制，确保项目能够按时交付并满足医疗系统的严格要求。