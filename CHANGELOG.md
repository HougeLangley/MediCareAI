# Changelog | 更新日志

All notable changes to this project will be documented in this file.
本项目的所有重要变更都将记录在此文件中。

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

格式基于 [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)，
并且本项目遵循 [语义化版本](https://semver.org/spec/v2.0.0.html)。

---

## [2.1.0] - 2026-02-19

### 主要更新 Highlights | Major Updates

#### 🧹 知识库架构清理与优化 (Knowledge Base Architecture Cleanup)
- **统一知识库架构确认** Unified Knowledge Base Architecture Verified
  - 删除遗留的 `diseases/` 目录结构（旧版按疾病分类）
  - 删除5个遗留向量化脚本 (`vectorize_*.py`)
  - 清理 `active/current.json` 旧版激活标记文件
  - 确认统一知识库工作流：所有文档存放于 `unified/` 目录

- **知识库工作流验证** Knowledge Base Workflow Verified
  - 管理端上传 → 保存至 `unified/` → 元数据管理 → 后台向量化
  - 支持云端向量模型配置 (Qwen/Aliyun/OpenAI API)
  - 自动生成向量嵌入存储至 PostgreSQL (pgvector)
  - AI 诊断自动使用 RAG 检索知识库内容

### 删除 Removed
- `backend/app/data/knowledge_bases/diseases/` - 遗留疾病分类知识库目录
- `backend/app/data/knowledge_bases/active/current.json` - 旧版激活标记
- `backend/vectorize_kb.py` - 遗留向量化脚本
- `backend/vectorize_simple.py` - 遗留向量化脚本
- `backend/vectorize_kb_direct.py` - 遗留向量化脚本
- `backend/vectorize_final.py` - 遗留向量化脚本
- `backend/vectorize_kb_fixed.py` - 遗留向量化脚本

### 技术细节 Technical Details
- **知识库目录结构**: 
  - `unified/` - 统一知识库存放目录
  - `metadata.json` - 文档元数据管理
- **向量化流程**: 管理端上传 → `_vectorize_knowledge_document()` 后台任务
- **向量存储**: PostgreSQL + pgvector 扩展
- **RAG 集成**: AI 诊断自动检索相关知识库内容

---

## [2.0.9] - 2026-02-19

### 主要更新 Highlights | Major Updates

#### 📢 @医生功能修复与增强 (@Doctor Mention Fixes & Enhancements)
- **修复 @提及隐私泄漏问题** Fixed @mention privacy leak
  - 患者 @A医生，B医生不再能看到该病例
  - 每个 @提及创建独立的私有共享记录
  - 严格隔离不同医生的 @提及病例

- **支持同时 @多位医生** Support mentioning multiple doctors simultaneously
  - 前端支持多选医生（点击切换选择/取消）
  - 后端支持 `doctor_ids` 数组批量处理
  - 每位被 @医生都会收到独立的病例分享

- **修复导出权限问题** Fixed export permission issues
  - @提及的医生可以正确导出病例
  - 权限检查验证具体的 case_id 是否在 shared_case_ids 中
  - 未 @提及的医生无法导出病例

#### 🔐 隐私授权逻辑分离 (Privacy Authorization Logic Separation)
- **@提及与公开共享分离** Separated @mention from public sharing
  - @提及医生：无论是否勾选"允许共享给医生端"，都仅对 @医生可见
  - 勾选"允许共享"：病例对所有医生公开可见
  - 两者独立，可同时使用

### 新增功能 Added
- `frontend/symptom-submit.html` - 多医生选择 UI（支持添加/移除多位医生）
- `frontend/medical-records.html` - 分享模态框多医生支持

### 变更 Changed
- `backend/app/api/api_v1/endpoints/ai.py`:
  - 添加 `doctor_ids` 字段支持多医生 @mention
  - 修复 `share_case_with_doctor` 总是创建新的私有 SharedMedicalCase
  - @mention 逻辑与共享 checkbox 分离
- `backend/app/api/api_v1/endpoints/doctor.py`:
  - 修复 `check_export_permission` 验证具体 case_id
  - 修复 `get_doctor_accessible_cases` 只返回明确的 shared_case_ids
- `frontend/doctor-export.html` - 修改查询类型为 `all`（公开 + @提及）

### 修复 Fixed
- 修复 @提及病例被非目标医生看到的问题
  - 问题：`share_case_with_doctor` 复用可能已公开的 SharedMedicalCase
  - 解决：每次 @提及都创建新的私有记录
- 修复医生可以看到患者的所有非公开病例的问题
  - 问题：`get_doctor_accessible_cases` 返回患者的所有 visible_to_doctors=False 病例
  - 解决：只返回 `shared_case_ids` 中明确的病例ID
- 修复导出页面显示"暂无可导出的病例"的问题
  - 问题：查询类型为 `public`，@提及病例无法显示
  - 解决：修改为 `all` 类型查询

### 技术细节 Technical Details
- **多医生 @mention**: 前端使用 `selectedDoctors` 数组管理选择状态
- **私有记录创建**: `share_case_with_doctor` 不再检查现有记录，总是新建
- **权限隔离**: `DoctorPatientRelation.shared_case_ids` 严格限制医生可见范围

---

## [2.0.8] - 2026-02-17

### 主要更新 Highlights | Major Updates

#### 🏥 慢性病与特殊病管理功能 (Chronic & Special Disease Management)
- **新增患者慢性病档案管理** Added patient chronic disease profile management
  - 支持添加/管理43种ICD-10编码的慢性病和特殊病
  - 疾病类型包括：特殊病(Special)、慢性病(Chronic)、两者兼具(Both)
  - 支持记录病情严重程度、确诊日期、备注信息
  - 软删除机制：标记为 inactive 而非物理删除

#### 🤖 AI诊断集成慢性病数据 (AI Diagnosis with Chronic Disease Context)
- **AI诊断时自动参考患者慢性病信息** AI now considers patient's chronic diseases
  - 诊断提示词中自动包含患者慢性病列表
  - AI会考虑药物相互作用和禁忌症
  - 针对慢性病患者提供个性化诊断建议

#### 👨‍⚕️ 医生端慢性病警告显示 (Doctor Side Chronic Disease Warnings)
- **病例列表显示患者慢性病标签** Case list shows patient chronic disease tags
  - 医生病例列表API返回 `patient_chronic_diseases` 字段
  - 不同疾病类型用不同颜色区分（红色-特殊病/蓝色-慢性病/紫色-两者兼具）
  - 病例详情页面突出显示慢性病警告区域

### 新增功能 Added
- `backend/app/models/models.py` - 新增 `ChronicDisease` 和 `PatientChronicCondition` 模型
- `backend/app/db/chronic_disease_data.py` - 43种ICD-10慢性病/特殊病数据
- `backend/app/db/init_chronic_diseases.py` - 数据库初始化脚本
- `backend/app/api/api_v1/endpoints/chronic_diseases.py` - 慢性病管理API端点
- `backend/app/api/api_v1/endpoints/doctor.py` - 新增病例列表慢性病数据加载
- `frontend/user-profile.html` - 患者端慢性病管理UI
- `frontend/doctor-cases.html` - 医生端病例列表慢性病标签显示
- `frontend/doctor-case-detail.html` - 医生端病例详情慢性病警告

### 变更 Changed
- `backend/app/services/ai_service.py` - AI服务支持传入患者慢性病数据
- `backend/app/api/api_v1/endpoints/ai.py` - AI诊断API自动加载患者慢性病
- `backend/app/api/api_v1/api.py` - 注册慢性病管理路由

### 修复 Fixed
- 修复 `doctor.py` 中 `disease_category` 属性访问错误
  - 问题：`MedicalCase` 对象没有 `disease_category` 属性
  - 解决：通过 `case.original_case.disease.category` 正确访问疾病分类
  - 添加 `selectinload` 预加载优化查询性能

### 技术细节 Technical Details
- **数据库表**: `chronic_diseases` (43条记录), `patient_chronic_conditions` (患者关联表)
- **软删除**: `is_active` 字段标记，删除时设为 False，重新添加时激活
- **API端点**:
  - `GET /api/v1/chronic-diseases` - 获取所有慢性病列表
  - `POST /api/v1/patients/me/chronic-diseases` - 患者添加慢性病
  - `PUT /api/v1/patients/me/chronic-diseases/{id}` - 更新慢性病信息
  - `DELETE /api/v1/patients/me/chronic-diseases/{id}` - 软删除慢性病
  - `GET /api/v1/patients/{patient_id}/chronic-diseases` - 医生查看患者慢性病

---

## [2.0.7] - 2026-02-16

### 主要更新 Highlights | Major Updates

#### 📚 文档重构与合并 (Documentation Consolidation)
- **删除分散的 RELEASE 文件** Removed scattered RELEASE files
  - 删除 `docs/RELEASE_v2.0.0.mdx`、`docs/RELEASE_v2.0.1.mdx`、`docs/RELEASE_v2.0.3.mdx`
  - 所有发布说明统一合并到根目录 `CHANGELOG.md`
  - 简化维护，避免文档分散

#### 🆘 新增故障排除指南 (New Troubleshooting Guide)
- **创建 TROUBLESHOOTING.mdx** Created comprehensive troubleshooting documentation
  - 应急脚本说明 (`cleanup-docker.sh`)
  - 常见问题解决方案
  - 系统维护任务指南
  - 调试技巧和日志查看
  - SELinux 配置参考

#### 🔧 项目清理 (Project Cleanup)
- **删除临时修复脚本** Removed temporary fix scripts
  - 删除 `fix_env_mount.sh` (环境挂载修复脚本)
  - 该功能已通过 Docker 卷挂载优化解决

#### 🗑️ 遗留文件清理 (Legacy Cleanup)
- **清理旧知识库目录** Cleaned up old knowledge base directory
  - 删除 `backend/data/knowledge_bases/diseases/` 目录及内容
  - 统一使用 `unified/` 目录作为知识库来源

### 新增功能 Added
- `docs/TROUBLESHOOTING.mdx` - 故障排除与应急修复指南
- `scripts/cleanup-docker.sh` - Docker 环境清理脚本（已在 v2.0.3 添加，现正式纳入文档）

### 变更 Changed
- `CHANGELOG.md` - 新增 v2.0.1、v2.0.3、v2.0.7 详细发布记录
- `README.md` - 更新文档结构，移除 RELEASE 文件引用，添加 TROUBLESHOOTING 链接
- `docs/` 目录结构简化，移除 3 个 RELEASE 文件

### 删除 Removed
- `docs/RELEASE_v2.0.0.mdx` - 内容已合并到 CHANGELOG.md
- `docs/RELEASE_v2.0.1.mdx` - 内容已合并到 CHANGELOG.md
- `docs/RELEASE_v2.0.3.mdx` - 内容已合并到 CHANGELOG.md
- `fix_env_mount.sh` - 临时修复脚本，功能已整合

### 文档更新 Documentation Updates
- **README.md**: 更新 docs/ 目录树，修正文档导航链接
- **CHANGELOG.md**: 统一所有版本发布记录，支持中英双语
- **TROUBLESHOOTING.mdx**: 新增完整故障排除指南（262行）

---

## [2.0.3] - 2026-02-16

### 主要更新 Highlights | Major Updates

#### 🔧 AI 诊断数据持久化修复 (AI Diagnosis Data Persistence Fix)
- **修复请求类型枚举错误** Fixed request_type enum error
  - 将 `"comprehensive_diagnosis_stream"` 改为 `"comprehensive_diagnosis"`
  - 解决数据库事务回滚导致诊断数据未保存问题
  - 病例状态现在正确更新为 "completed" (已完成)
  - 模型 ID 和 Token 用量现在正确显示
  
#### 🔐 医生评论权限逻辑修复 (Doctor Comment Permission Logic Fix)
- **@提及医生权限修复** @mention Doctor Permission Fix
  - 修复 `visible_to_doctors=False` 时 @提及医生无法评论的问题
  - 新增通过 `DoctorPatientRelation` 验证医生权限
  - 权限逻辑：
    - `visible_to_doctors=True`: 所有认证医生可评论
    - `visible_to_doctors=False`: 仅 @提及的医生可评论

#### 🏛️ 病例分享隐私逻辑澄清 (Case Sharing Privacy Logic Clarification)
- **分享与@提及关系明确** Clarified sharing vs @mention relationship
  - 仅 "分享给医生": 所有认证医生可见
  - 仅 @医生: 仅被 @提及的医生可见
  - "分享" + @医生: 所有医生可见，@医生收到通知
  - @提及仅发送通知，不限制可见性范围

#### 🗑️ 遗留知识库清理 (Legacy Knowledge Base Cleanup)
- **删除旧模块化知识库** Removed legacy modular KB
  - 删除 `backend/data/knowledge_bases/diseases/` 目录 (164KB)
  - 统一使用 `unified/` 目录作为唯一知识库来源
  - 简化架构，减少维护复杂度

#### 🚀 部署稳定性改进 (Deployment Stability Improvements)
- **PostgreSQL 健康检查优化** PostgreSQL Health Check Enhancement
  - 增加 `start_period: 60s` 给数据库初始化时间
  - 增加重试次数到 10 次
  - 解决全新部署时健康检查失败问题

#### 🐳 Docker 清理脚本增强 (Docker Cleanup Script Enhancement)
- **跨版本 Docker Compose 兼容** Cross-version Docker Compose compatibility
  - 自动检测 `docker-compose` (v1) 或 `docker compose` (v2)
  - 新增 `-y` / `--yes` 参数支持非交互式自动确认
  - 添加 10 秒超时保护，防止自动化环境挂起

### 新增功能 Added
- `scripts/cleanup-docker.sh` - Docker 数据清理工具
- `start_period` 配置 - PostgreSQL 健康检查启动宽限期
- 自动确认模式 - 清理脚本支持 `-y` 参数

### 修复 Fixed
- AI 诊断请求类型枚举错误导致数据未保存
- 医生评论权限逻辑问题
- PostgreSQL 首次部署健康检查失败
- Docker Compose 命令兼容性问题 (Ubuntu 24.04)
- 清理脚本在自动化环境超时问题

### 变更 Changed
- 删除 `backend/data/knowledge_bases/diseases/` 目录
- 更新 `docker-compose.yml` 健康检查配置
- 更新 `.gitignore` 排除遗留知识库路径
- 优化 `scripts/cleanup-docker.sh` 交互逻辑

### 技术细节 Technical Details

#### 后端变更
- `backend/app/services/ai_service.py` - Line 694: 修复 request_type
- `backend/app/api/api_v1/endpoints/doctor.py` - Lines 1193-1243: 修复评论权限
- `backend/app/api/api_v1/endpoints/ai.py` - Lines 113-202: 澄清分享逻辑
- `docker-compose.yml` - 健康检查配置优化
- `docker-compose.prod.yml` - 健康检查配置优化

#### 文档更新
- `README.md` - 更新项目结构说明
- `CHANGELOG.md` - 添加 v2.0.3 更新记录

---

## [2.0.0] - 2026-02-09

### 主要更新 Highlights | Major Updates

#### 🔗 医患互动增强 (Enhanced Patient-Doctor Interaction)
- **双向沟通** Bidirectional Communication
  - 患者可回复医生评论 | Patients can reply to doctor comments
  - @医生 提及系统 | @doctor mention system
  - 时间筛选功能 (今日/三天内/一周内) | Time-based filtering
  - 医生端查看患者回复 | Doctor view of patient replies

#### 🏛️ 系统稳定性增强 (System Stability)
- **Docker 自动重启** Auto-restart Configuration
  - PostgreSQL 和 Redis 容器设置 `restart: always`
  - 系统重启后服务自动恢复
  - 生产环境高可用性保障

#### 🔧 关键 Bug 修复 (Critical Bug Fixes)
- **医生搜索修复** Doctor Search Fix
  - 修复 `is_verified` 字段同步问题
  - 修复医生认证状态显示异常
  - 新增数据同步端点 `/api/v1/admin/doctors/sync-verification`

### 新增功能 Added
- `case_comment_replies` 表：患者回复医生评论
- `reply_status` 枚举：回复状态管理
- 时间筛选 UI：医生端提及列表
- 隐私控制：医生仅查看自己相关的讨论

### 修复 Fixed
- 医生搜索不显示已认证医生
- 管理后台显示模拟数据而非真实系统指标
- PostgreSQL 枚举类型兼容性问题

### 变更 Changed
- `docker-compose.yml` 添加 `restart: always` 策略
- 管理后台使用 `psutil` 获取真实系统指标
- 医生认证流程优化

---

## [2.0.1] - 2026-02-12

### 主要更新 Highlights | Major Updates

#### 📚 统一知识库架构 (Unified Knowledge Base Architecture)
- **扁平化存储结构** Flat Storage Structure
  - 所有文档统一存储在 `unified/` 目录 | All documents stored in unified/ directory
  - 移除疾病分类限制 | Removed disease category restrictions
  - 新增 `UnifiedKnowledgeLoader` 服务 | Added UnifiedKnowledgeLoader service
  - 自动文档分类和标签提取 | Auto document categorization and tag extraction

#### ⚙️ 动态配置系统 (Dynamic Configuration System)
- **MinerU Token 动态配置** Dynamic MinerU Token
  - 新增 `DynamicConfigService` 实现运行时配置读取
  - Admin 修改后立即生效，无需重启服务
  - 支持 URL 自动校正 (mineru.com → mineru.net)

#### 🔧 向量化修复 (Vectorization Fixes)
- **source_type 枚举修复** Added 'unified_kb' to enum
- **重复上传优化** 自动删除旧版本 chunks
- **异步操作修复** 解决 greenlet_spawn 错误

### 新增功能 Added
- `UnifiedKnowledgeLoader` - 统一知识库加载服务
- `DynamicConfigService` - 动态配置服务
- `DocumentTasks` - 后台文档处理任务
- 知识库文档自动分类和标签提取

### 修复 Fixed
- MinerU Token 动态配置不生效问题
- 向量化失败 (source_type 枚举缺失)
- 重复上传时旧 chunks 未删除
- 异步文件操作 greenlet 错误
- 知识库 API 端点 unified 目录支持

### 变更 Changed
- 知识库目录结构: diseases/ → unified/
- MinerUService 返回格式改为 dict
- 文档上传流程使用真实向量化
- 更新删除端点支持 unified 结构

### 技术细节 Technical Details

#### 后端变更
- `app/services/unified_kb_service.py` - 统一知识库服务
- `app/services/dynamic_config_service.py` - 动态配置服务
- `app/services/document_tasks.py` - 后台文档处理
- `app/api/api_v1/endpoints/admin.py` - 知识库 API 更新

#### 数据库变更
- 更新 `source_type` enum: 添加 'unified_kb'
- 支持 `knowledge_base_chunks` 按标题模糊删除

---

## [Unreleased] - 2026-02-05

### 主要更新 Highlights | Major Updates

#### 🏛️ Phase 6: 管理员系统 (Admin System)
- **系统监控** System Monitoring
  - 实时 CPU/内存/磁盘监控 | Real-time resource monitoring
  - Docker 容器状态追踪 | Container status tracking
  - AI 诊断异常检测 | AI diagnosis anomaly detection
  - 告警系统 (Critical/Warning/Info) | Alert system with 3 levels
  
- **管理员仪表板** Admin Dashboard
  - `GET /api/v1/admin/dashboard/summary` - 关键指标概览
  - `GET /api/v1/admin/system/metrics` - 系统指标历史
  - `GET /api/v1/admin/ai/statistics` - AI 诊断统计
  - `GET /api/v1/admin/ai/anomalies` - AI 异常检测
  
- **医生认证管理** Doctor Verification
  - `GET /api/v1/admin/doctors/pending` - 待审核列表
  - `POST /api/v1/admin/doctors/{id}/approve` - 批准认证
  - `POST /api/v1/admin/doctors/{id}/reject` - 拒绝认证
  
- **审计日志** Audit Logging
  - `GET /api/v1/admin/operations/logs` - 管理员操作日志
  - `GET /api/v1/admin/alerts/active` - 活跃告警
  
#### 🔧 MinerU 集成修复 | MinerU Integration Fixes
- **统一 API 格式** Unified API format
  - 修复 ai_service.py 与 mineru_service.py 格式不一致问题
  - 支持 base64 编码的文件上传
  - 自动 MIME 类型检测
  
- **数据流连接** Data Flow Connection
  - AI 诊断现在支持 `document_ids` 参数
  - 可使用预提取的文档内容进行诊断
  - 自动使用 PII 清理后的内容（隐私保护）
  
- **测试脚本** Test Scripts
  - `test_mineru_extraction.py` - MinerU 提取测试
  - `test_mineru_ai_integration.py` - 集成流程验证

### 新增功能 Added
- 管理员角色和权限系统 (Admin roles & permissions)
- AI 诊断日志记录 (AI diagnosis logging)
- 系统资源历史记录 (System resource history)
- 医生认证审核流程 (Doctor verification workflow)

### 修复 Fixed
- MinerU API 格式不一致问题
- 文档提取与 AI 诊断之间的数据流断裂
- Document service 中的属性访问错误

### 变更 Changed
- `comprehensive_diagnosis` 新增 `document_ids` 参数
- MinerUService 返回格式改为 dict（更灵活）
- 数据库模型: 新增 SystemResourceLog, AIDiagnosisLog, AdminOperationLog

---

## [1.0.3] - 2026-02-04

### 主要更新 Highlights

#### 🚀 一键部署脚本（中英双语）| One-Click Installation Script
- **统一安装脚本** `install.sh` 支持 7 大 Linux 发行版
  - ✅ Ubuntu 24.04 LTS
  - ✅ Fedora 43 Server  
  - ✅ openSUSE Leap 16.0
  - ✅ openSUSE Tumbleweed
  - ✅ AOSC OS 13.0.7
  - ✅ openEuler 24.03 LTS-SP3
  - ✅ Deepin 25
- **多语言支持**: 中文/English 双语界面
- **智能检测**: 自动识别发行版并处理兼容性问题
- **交互配置**: AI API、网络设置、端口自定义
- **自动处理**: SELinux、BuildKit 等兼容性问题

#### 🌍 AI 诊断语言自适应 | AI Language Support
- **新增 `language` 参数** 支持 `zh` (中文) 和 `en` (英文)
- **前端自动检测** 页面语言并传递参数
- **双语 Prompt**: 系统提示词和诊断提示词均支持双语
- **智能回复**: AI 根据界面语言自动切换回复语言

### 新增功能 Added

#### 症状提交增强 | Symptom Submission Enhancement
- **新增"分钟"单位** 到症状持续时间选项

### 修复 Fixed

#### Bug 修复 | Bug Fixes
- **修复诊断信息显示问题**
  - 修复 "模型: N/A" → 正确显示配置的模型ID
  - 修复 "Token用量: 0" → 显示估算的Token用量
  - 修复 "诊断时间: Invalid Date" → 正确格式化日期
- **修复 Docker Compose 兼容性**
  - `DEBUG: true` → `DEBUG: "true"` (字符串格式)
  - 解决 docker-compose v1.x 的类型验证错误

### 变更 Changed

#### 文档更新 | Documentation Updates
- **README.md 修正**
  - 移除 "集成 GLM-4.7-Flash" 描述，改为 "支持 OpenAI 兼容 API"
  - 更新联系邮箱为 hougelangley1987@gmail.com
  - 添加作者信息：苏业钦 (Su Yeqin)
- **LICENSE 更新**
  - 版权声明：Copyright (c) 2025 苏业钦 (Su Yeqin) and Contributors
  - 协议类型：MIT License

#### 界面优化 | UI Improvements
- **登录页面** 添加作者署名和 License 信息
- **首页页脚** 添加作者署名

### 技术细节 Technical Details

#### 后端变更 | Backend Changes
- `ai.py`: 新增 `language` 参数，更新流式响应数据结构
- `ai_service.py`: 双语 prompt 构建，系统提示词语言切换
- `docker-compose.yml`: 修复布尔值格式

#### 前端变更 | Frontend Changes
- `symptom-submit.html`: 语言检测逻辑，诊断信息存储
- `login.html`: 添加作者信息
- `index.html`: 页脚添加作者信息

---

## [1.0.2] - 2025-02-01

### 主要特性

#### 🤖 AI 流式诊断 | Streaming AI Diagnosis
- **实时流式输出** `/api/v1/ai/comprehensive-diagnosis-stream`
- **SSE 格式** Server-Sent Events 实现
- **逐字符显示** AI 回复实时展示
- **完整工作流**: 个人信息 + MinerU文档提取 + 知识库 → AI诊断

#### 📄 文档智能处理 | Document Processing
- **MinerU 集成** PDF/图片/文档文本提取
- **支持格式**: PDF, Word, PPT, 图片
- **自动提取** 检查报告内容结构化

#### 🏥 知识库系统 | Knowledge Base
- **模块化设计** 支持多种疾病
- **当前支持**: 呼吸系统疾病 (respiratory)
- **循证医学** 整合诊疗指南

### 核心功能

- **用户认证**: JWT + Refresh Token
- **患者管理**: 档案、病历号、随访
- **医疗记录**: 病例、附件、AI反馈
- **多科室支持**: 内科、外科、儿科、妇科

### 技术栈

- **后端**: FastAPI 0.109.2, Python 3.12, SQLAlchemy 2.0
- **数据库**: PostgreSQL 17, Redis 7.4
- **前端**: HTML5/CSS3/ES6
- **AI**: OpenAI 兼容 API
- **部署**: Docker + Docker Compose

---

## 版本历史 Version History

| 版本 | 日期 | 主要更新 |
|------|------|----------|
| 2.0.7 | 2026-02-16 | 文档重构合并、新增故障排除指南、项目清理 |
| 2.0.3 | 2026-02-16 | AI诊断修复、隐私逻辑优化、部署改进、遗留KB清理 |
| 2.0.1 | 2026-02-12 | 统一知识库架构、动态配置、向量化修复 |
| 2.0.0 | 2026-02-09 | 医患双向沟通、系统稳定性增强、Bug修复 |
| 1.0.3 | 2026-02-04 | 一键部署脚本、AI语言支持、Bug修复 |
| 1.0.2 | 2025-02-01 | 流式AI诊断、文档处理、知识库 |

---

**作者 Author**: 苏业钦 (Su Yeqin)  
**协议 License**: MIT License  
**仓库 Repository**: MediCareAI
