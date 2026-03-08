# Changelog | 更新日志

All notable changes to this project will be documented in this file.
本项目的所有重要变更都将记录在此文件中。

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

格式基于 [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)，
并且本项目遵循 [语义化版本](https://semver.org/spec/v2.0.0.html)。

## [3.4.1] - 2026-03-08

### AI 诊断与文档处理修复 | AI Diagnosis & Document Processing Fixes | 🐛🔧

#### 关键修复 Critical Fixes | 🐛

**1. AI 诊断流式响应解析修复**
- **问题**: Android App 在症状提交后一直显示加载中，无法显示 AI 诊断结果
- **原因**: 后端返回的 SSE 完成消息包含额外字段（`saved_to_records`, `status`, `created_at`），Android 端解析时因缺少这些字段而失败
- **修复**: 在 `MediCareApiClient.kt` 的 SSE 解析中添加 `ignoreUnknownKeys = true`

**2. 文档内容接口字段修复**
- **问题**: Android 轮询文档处理状态时返回 500 错误
- **原因**: 后端 `/documents/{id}/content` 返回 `document_id`，但 Android 期望 `id`
- **修复**: 在响应中添加 `id` 字段，保留 `document_id` 向后兼容

**3. AI 诊断地址字段修复**
- **问题**: 症状提交时后端报错 `'Patient' object has no attribute 'address'`
- **原因**: Patient 模型已移除 `address` 字段，但 AI 诊断端点仍尝试访问 `patient.address`
- **修复**: 将 `patient.address` 改为 `current_user.address`

**4. 患者档案字段显示修复**
- **问题**: 注册时填写的出生日期、性别、手机号等字段在个人中心显示为空
- **原因**: `/auth/me` 端点只返回 User 表数据，而这些字段存储在 Patient 表中
- **修复**: 修改 `/auth/me` 端点同时查询 Patient 表，合并返回完整数据

---

## [3.4.0] - 2026-03-08

### 患者注册与档案管理综合修复 | Patient Registration & Profile Management Fixes | 🐛🔧

#### 关键修复 Critical Fixes | 🐛

**1. Android 注册字段未发送修复**
- **问题**: Android App 注册时只发送 email 和 full_name，其他字段丢失
- **原因**: Ktor 客户端未显式设置 Content-Type 头部导致 JSON 序列化不完整
- **修复**: 在 `MediCareApiClient.kt` 的 `makeRequest()` 中添加 `contentType(ContentType.Application.Json)`

**2. 患者档案自动创建 500 错误修复**
- **问题**: 新用户访问"个人中心"时报 500 Internal Server Error
- **原因**: 
  - `Patient` 模型已移除 `address` 字段，但 `patient_service.py` 仍尝试传入 `address=None`
  - 代码缩进错误导致 Python 语法错误 (IndentationError)
- **修复**:
  - 从 `create_patient()` 中移除 `address` 参数
  - 完全重写 `patient_service.py` 修复缩进错误

**3. 注册时患者档案创建逻辑修复**
- **问题**: 注册成功但数据库中缺少患者档案
- **修复**: 修改 `auth.py` 注册端点，确保总是创建 `Patient` 档案

#### 数据模型优化 Data Model Optimizations | 🏗️

**1. 地址字段统一存储**
- `Patient` 模型移除 `address` 字段
- 地址统一存储在 `User` 表的 `address` 字段
- 消除数据冗余，避免同步问题

**2. 紧急联系人字段分离**
- 新增 `emergency_contact_name` 和 `emergency_contact_phone` 字段
- 替代原有的 `emergency_contact` 合并字段
- 前后端同步更新支持新字段

#### 新增功能 Features | ✨

**Android App**
- **省市区地址选择器**: 三级联动地址选择组件
- **日期选择器**: 出生日期选择组件
- **文件上传功能**: 支持检查资料上传（PDF、图片等）
- **流式 AI 诊断**: SSE 实时流式诊断输出
- **@医生提及**: 症状提交时可选择分享给医生

**后端 Backend**
- **自动创建患者档案**: GET `/patients/me` 时如不存在则自动创建
- **详细错误日志**: 患者档案创建失败时记录完整 traceback

#### 修改文件清单 Modified Files

| 文件路径 | 修改类型 | 说明 |
|---------|---------|------|
| `android/app/src/main/java/.../MediCareApiClient.kt` | 修复 | 添加 Content-Type 头部 |
| `android/app/src/main/java/.../RegisterScreen.kt` | 新增 | 省市区选择器、日期选择器 |
| `android/app/src/main/java/.../AddressPickerField.kt` | 新增 | 地址选择组件 |
| `android/app/src/main/java/.../DatePickerField.kt` | 新增 | 日期选择组件 |
| `android/app/src/main/java/.../SymptomSubmitScreen.kt` | 重构 | 流式诊断、文件上传 |
| `android/app/src/main/java/.../Models.kt` | 修改 | 添加紧急联系人分离字段 |
| `backend/app/services/patient_service.py` | 重写 | 修复缩进错误，移除 address 字段 |
| `backend/app/api/api_v1/endpoints/patients.py` | 修改 | 自动创建患者档案，详细日志 |
| `backend/app/api/api_v1/endpoints/auth.py` | 修改 | 始终创建患者档案 |
| `backend/app/schemas/user.py` | 修改 | 添加紧急联系人分离字段 |
| `backend/app/models/models.py` | 修改 | 移除 Patient.address 字段 |

---

## [3.3.0] - 2026-03-07

### Android 症状提交功能全面升级 | Android Symptom Submission Major Upgrade | 📱

#### 新增功能 Features | ✨

**1. 症状提交表单增强 (Enhanced Symptom Submission Form)**
- **持续时间输入**: 新增数值输入框 + 单位选择器（秒/分钟/小时/天/周/月）
- **发病时间选择**: 日期选择器组件，支持年/月/日选择
- **严重程度下拉**: 轻微/轻度/中度/重度/严重 五级选择
- **诱因和既往病史**: 保留原有输入框，整合到 description 字段

**2. 检查资料上传功能 (Medical Document Upload)**
- **文件选择器**: 支持 PDF、图片、文档等多格式文件选择
- **多文件上传**: 支持同时选择多个文件（建议最多5个）
- **上传进度显示**: 实时显示每个文件的上传进度条
- **同步上传处理**: 使用 async/await 确保所有文件上传完成后再开始 AI 诊断
- **MinerU 文档提取**: 自动触发 MinerU 服务提取文档内容，轮询等待提取完成
- **文件限制**: 单个文件不超过 10MB

**3. @提及医生功能 (@Doctor Mention System)**
- **医生列表获取**: 从 `/sharing/doctors` API 获取可分享医生列表
- **医生选择弹窗**: 可展开/折叠的医生选择对话框
- **医生标签显示**: 已选择医生以 Chip 形式展示，支持移除
- **医生信息展示**: 显示医生姓名、医院、科室、职称
- **隐私授权集成**: 与隐私授权复选框联动，控制是否分享给医生

**4. AI 诊断流式输出 (Streaming AI Diagnosis)**
- **实时流式显示**: 使用 SSE (Server-Sent Events) 接收 AI 诊断内容
- **Markdown 渲染**: 支持标题、粗体、列表、表格等 Markdown 格式
- **进度指示器**: 显示当前诊断状态（正在上传/正在处理/诊断中）
- **实时状态更新**: 文件上传进度、MinerU 处理状态实时反馈

**5. 诊断结果展示增强 (Enhanced Diagnosis Result Display)**
- **AI 模型信息**: 显示使用的 AI 模型名称（如 deepseek-chat）
- **Token 消耗统计**: 显示本次诊断消耗的 Token 数量
- **知识库引用**: 可折叠的 RAG 知识库引用区域
  - 显示引用的医疗指南来源
  - 显示相关性评分
  - 显示文档标题和章节信息
- **完成状态检测**: 正确解析后端返回的 completion JSON

#### Bug 修复 Bug Fixes | 🐛

**1. 症状提交 description 字段 null 值修复**
- **问题**: description 字段传递 null 导致数据库错误
- **修复**: 确保 description 始终为字符串类型（空字符串代替 null）

**2. 文件上传异步问题修复**
- **问题**: 文件上传未完成就开始 AI 诊断，导致文档内容未纳入诊断
- **修复**: 使用 `async/await` 模式确保所有文件上传和 MinerU 提取完成后再开始诊断

**3. 诊断结果 JSON 解析修复**
- **问题**: 后端发送的 completion JSON 包含额外字段导致解析失败
- **修复**: 使用 `ignoreUnknownKeys = true` 配置 JSON 解析器

**4. 诊断结果模型/Token 显示修复**
- **问题**: completion JSON 在 chunk 中发送，但响应中 model/tokens 为 null
- **修复**: 从 chunk 中解析 completion JSON 并正确提取 model、tokens、knowledge_sources

**5. Markdown 表格渲染修复**
- **问题**: Markdown 表格显示为原始文本（| 列1 | 列2 |）
- **修复**: 实现表格行解析，以 Row 组件展示表格内容

#### 技术实现 Technical Implementation | 🔧

**ViewModel 层**
- `SymptomSubmitViewModel`: 新增文件上传、医生选择、流式诊断管理
- `StreamingDiagnosisState`: 新增流式诊断状态数据类
- 使用 `async/await` 实现同步上传流程
- 使用 `kotlinx.coroutines.flow` 收集 SSE 流数据

**UI 层**
- `SymptomSubmitScreen`: 完全重构症状提交界面
- `FileUploadItem`: 文件上传进度项组件
- `DoctorChip`: 医生选择标签组件
- `DoctorSelectionDialog`: 医生选择对话框
- `SimpleMarkdownContent`: Markdown 内容渲染组件
- `KnowledgeSourcesSection`: 知识库引用折叠面板

**网络层**
- `MediCareApiClient.diagnoseStream()`: 实现 SSE 流式请求
- 支持解析 `data:` 前缀的 SSE 消息
- 处理 chunk 和 completion 两种消息类型

#### 新增文件 Added Files
- `android/app/src/main/java/com/medicareai/patient/ui/screens/SymptomSubmitScreen.kt` - 症状提交主界面
- `android/app/src/main/java/com/medicareai/patient/viewmodel/ViewModels.kt` - ViewModel 实现

#### 变更 Changed
- `android/app/src/main/java/com/medicareai/patient/data/api/MediCareApiClient.kt` - 新增流式诊断 API
- `android/app/src/main/java/com/medicareai/patient/data/model/Models.kt` - 新增数据模型
- `android/app/src/main/java/com/medicareai/patient/data/repository/Repository.kt` - 新增 Repository 方法

---

## [3.2.0] - 2026-03-05

### Android App UI 修复与法律文档 | Android App UI Fixes & Legal Documentation | 📱

#### UI Bug 修复 UI Fixes | 🐛

**1. 欢迎页标题居中修复 (Welcome Screen Title Centering)**
- **问题**: "关于 MediCareAI" 标题和 emoji 视觉上偏左，未正确居中
- **修复**: 
  - 将 emoji "📋" 从标题开头移至末尾，改为 "关于 MediCareAI 📋"
  - Column 添加 `horizontalAlignment = Alignment.CenterHorizontally`
  - 标题 Text 组件添加 `textAlign = TextAlign.Center` 和 `fillMaxWidth()`
  - 介绍文字添加 `textAlign = TextAlign.Justify` 实现两端对齐

**2. 首页功能卡片间距修复 (Dashboard Feature Card Spacing)**
- **问题**: 描述文字与右侧按钮间距过小，几乎贴在一起，不美观
- **修复**:
  - 移除 Row 的 `horizontalArrangement = Arrangement.SpaceBetween`（导致 Spacer 被压缩的元凶）
  - 保留 `weight(1f)` 让文字区域自动占据剩余空间
  - Spacer 宽度保持 16.dp，确保文字和按钮之间有舒适间距

#### 新增功能 Features | ✨

**1. 法律信息卡片 (Legal Information Card)**
- **位置**: DashboardScreen 底部，"快速了解" 改为 "法律信息"
- **功能**: 
  - 显示两个可点击的文本链接：用户协议 | 隐私政策
  - 点击后弹出 AlertDialog 显示完整法律文本
  - 弹窗高度 400dp，支持滚动查看全部内容
- **文件**: `LegalContent.kt` - 集中存储完整的法律文档内容

**2. 注册页面法律链接 (Register Page Legal Links)**
- **修改**: 将注册页面的协议复选框文本改为可点击链接
- **显示**: "我已阅读并同意 [用户协议] 和 [隐私政策]"
- **交互**: 点击链接弹出与首页相同的完整法律文档弹窗

#### 法律文档内容 Legal Documents | 📜

**用户服务协议 (Terms of Service)**
- 8 个章节：术语定义、协议接受、用户注册、个人信息保护、用户行为规范、知识产权、免责声明、争议解决
- 包含重要提示、AI 诊断免责声明、特别提示等关键条款
- 与 Web 端注册页面的内容完全一致

**隐私保护政策 (Privacy Policy)**
- 10 个章节：政策更新、信息收集、敏感信息保护、信息共享、信息存储、用户权利、未成年人保护、数据跨境、联系我们
- 详细说明健康信息（敏感个人信息）的特殊保护措施
- 与 Web 端注册页面的内容完全一致

#### 新增文件 Added Files
- `android/app/src/main/java/com/medicareai/patient/ui/screens/LegalContent.kt` - 法律文档内容

#### 变更 Changed
- `android/app/src/main/java/com/medicareai/patient/ui/screens/WelcomeScreen.kt` - 标题居中对齐
- `android/app/src/main/java/com/medicareai/patient/ui/screens/DashboardScreen.kt` - 间距修复，添加法律信息卡片和弹窗
- `android/app/src/main/java/com/medicareai/patient/ui/screens/RegisterScreen.kt` - 添加可点击的法律链接和弹窗

---

## [3.1.5] - 2026-03-05
---

## [3.1.4] - 2026-03-03

### Bug 修复 Bug Fixes | 🐛

#### OSS 连通性测试修复 (OSS Connectivity Test Fix)

**问题描述**
- 管理员在 AI模型配置 页面配置阿里云OSS后，点击"测试连通性"按钮报错："OSS not configured"
- 但配置状态显示"正常(已配置)"，其他AI模型测试正常

**根本原因**
- `os_service` 是单例对象，在服务启动时从环境变量初始化
- 用户在界面配置OSS后，配置保存到数据库，但单例实例未刷新
- 测试连通性时，`health_check()` 发现 `self.bucket` 为 None，返回 "OSS not configured"

**修复方案**
- 在 `test_oss_connection()` 函数中，测试前先调用 `reload_config_from_db(db)` 重载最新配置
- 文件: `backend/app/api/api_v1/endpoints/admin.py`
- 代码变更:
  ```python
  # 测试前先重载配置
  await os_service.reload_config_from_db(db)
  health_result = os_service.health_check()
  ```

### 变更 Changed
- `backend/app/api/api_v1/endpoints/admin.py` - OSS测试前重载数据库配置

---

## [3.1.3] - 2026-03-03

### 关键安全修复 Critical Security Fixes | 🔒

#### 1. CORS 配置安全加固
**风险**: 生产环境允许所有来源 (`["*"]`) 访问API，存在CSRF攻击风险
**修复**:
- `backend/app/main.py`: CORS改为从环境变量 `CORS_ORIGINS` 读取
- 开发环境默认 `DEBUG=true` 时允许 `["*"]`
- 生产环境必须配置具体域名，如 `["https://your-domain.com"]`
- `docker-compose.yml`: 添加 `CORS_ORIGINS` 环境变量支持

#### 2. TrustedHost 配置安全加固
**风险**: 允许所有主机头 (`["*"]`)，存在Host Header攻击风险
**修复**:
- `backend/app/main.py`: TrustedHost改为从环境变量 `ALLOWED_HOSTS` 读取
- 生产环境必须配置具体域名
- `docker-compose.yml`: 添加 `ALLOWED_HOSTS` 环境变量支持

#### 3. ProxyHeadersMiddleware 配置安全加固
**风险**: 信任所有代理主机 (`["*"]`)，攻击者可伪造X-Forwarded-For头部
**修复**:
- `backend/app/main.py`: 代理信任列表改为从 `TRUSTED_PROXY_HOSTS` 读取
- 生产环境默认只允许本地网络和Docker网络
- `docker-compose.yml`: 添加 `TRUSTED_PROXY_HOSTS` 环境变量支持

#### 4. 移除硬编码密码
**风险**: docker-compose.yml 中硬编码数据库密码 `medicare123456`
**修复**:
- `docker-compose.yml`: 所有密码改为环境变量引用
  - `POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}`
  - `REDIS_PASSWORD: ${REDIS_PASSWORD}`
  - `DATABASE_URL` 和 `REDIS_URL` 中的密码使用变量替换

#### 5. DEBUG 模式配置化
**风险**: docker-compose.yml 中硬编码 `DEBUG: "true"`
**修复**:
- `docker-compose.yml`: `DEBUG: ${DEBUG:-true}`
- 开发环境默认 `true`，生产环境应在 `.env` 中设置为 `false`

### 文档更新 Documentation

#### 新增文档
- `docs/PRODUCTION_UPDATE_GUIDE.mdx` - 生产环境安全更新完整指南
- `scripts/update-production.sh` - 自动化服务器更新脚本

#### 更新文档
- `.env.example` - 添加详细的环境变量配置示例和说明
- `README.md` - 添加首次部署配置说明，指导用户设置密码和管理员账号
- `docs/PRODUCTION_DEPLOYMENT.mdx` - 添加生产环境CORS/Host配置详细说明和故障排除

### 变更 Changed
- `backend/app/main.py` - 安全中间件改为环境变量驱动
- `docker-compose.yml` - 移除硬编码密码和DEBUG配置
- `.env.example` - 新增安全相关环境变量
- `README.md` - 新增首次部署指南
- `docs/PRODUCTION_DEPLOYMENT.mdx` - 新增安全配置章节

---

## [3.1.2] - 2026-03-02

## [3.1.2] - 2026-03-03

### Bug 修复 Bug Fixes | 🐛

#### 医生注册流程修复 (Doctor Registration Workflow Fixes)

**1. 审核拒绝邮件通知修复**
- **问题**: 管理员审核拒绝医生时未发送拒绝通知邮件
- **修复**: 
  - `email_templates.py`: 新增医生审核拒绝邮件模板 (`DOCTOR_REJECTION_HTML/TEXT`)
  - `admin.py`: 在 `reject_doctor_verification` 函数中集成邮件发送逻辑
  - 医生现在会收到包含拒绝原因的邮件通知

**2. 被拒绝医生重新注册修复**
- **问题**: 医生审核被拒绝后，无法使用原邮箱重新注册
- **修复**:
  - `auth.py`: 修改 `register_doctor` 函数
  - 检查邮箱是否属于审核被拒绝的医生 (`status == "rejected"`)
  - 如果是，自动删除旧账号和审核记录，允许重新注册
  - 同样处理执业证书号的重复检查
- **改进**: 医生无需更换邮箱即可重新提交正确的注册资料

### 新增功能 Added
- `backend/app/services/email_templates.py` - 新增医生审核拒绝邮件模板

### 变更 Changed
- `backend/app/api/api_v1/endpoints/admin.py` - 拒绝审核时发送邮件通知
- `backend/app/api/api_v1/endpoints/auth.py` - 支持被拒绝医生重新注册

---

## [3.1.1] - 2026-03-02

### 关键安全修复 Critical Security Fix | 🔒

#### Mixed Content Error 修复 (HTTPS/Mixed Content Fix)
- **修复 HTTPS 页面加载 HTTP API 错误** Fixed HTTPS page loading HTTP API error
  - `backend/app/main.py`: 添加 `ProxyHeadersMiddleware` 中间件
  - 解决患者端仪表盘 "加载统计数据失败" 问题
  - 修复浏览器阻止混合内容请求 (Mixed Content Blocking)
  - 后端现在正确识别 `X-Forwarded-Proto` 头，生成正确的 HTTPS URL

#### 修复详情 (Fix Details)
- **问题描述**: 生产环境 HTTPS 前端请求 HTTP API 端点，浏览器阻止请求
  - 错误信息: `Mixed Content: The page at 'https://...' was loaded over HTTPS, but requested an insecure XMLHttpRequest endpoint 'http://...'`
  - 影响: 患者端仪表盘无法加载统计数据
  
- **根本原因**: FastAPI 默认不识别反向代理的 `X-Forwarded-Proto` 头
  - Nginx 正确传递了 `X-Forwarded-Proto: https`
  - 但 FastAPI 生成 URL 时仍使用 HTTP 协议
  
- **解决方案**: 添加 Uvicorn 的 `ProxyHeadersMiddleware`
  ```python
  from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
  
  app.add_middleware(
      ProxyHeadersMiddleware,
      trusted_hosts=["*"],
  )
  ```

#### 部署优化 (Deployment Optimizations)
- **Docker Compose 卷挂载修复** Docker Compose Volume Mount Fix
  - 修复前端构建后 dist 目录被挂载覆盖的问题
  - 生产环境使用 `docker-compose.prod.yml`，注释掉开发环境卷挂载
  
- **前端构建优化** Frontend Build Optimization
  - `frontend/Dockerfile`: 使用 `npx vite build` 跳过 TypeScript 检查
  - 添加 `serve` 作为生产环境静态文件服务器
  - 多阶段构建减少镜像体积

#### 文档修复 (Documentation Fixes)
- **README.md 格式修复** README.md Format Fix
  - 修复重复的代码块标记导致的显示混乱
  - 将真实域名 `openmedicareai.life` 替换为占位符 `your-domain.com`
  - 统一文档风格，移除敏感信息暴露

### 新增文件 Added Files
- `docker-compose.prod.yml` - 生产环境 Docker Compose 配置

### 变更 Changed
- `backend/app/main.py` - 添加 ProxyHeadersMiddleware 支持反向代理
- `frontend/Dockerfile` - 优化多阶段构建流程
- `docker-compose.yml` - 修复卷挂载配置
- `frontend/index.html` - 添加缓存控制头防止浏览器缓存旧版本
- `README.md` - 修复格式错误和敏感信息泄露

---

## [3.1.0] - 2026-03-02

### 部署修复与优化 | Deployment Fixes & Optimizations | 🚀

#### 生产环境部署修复 (Production Deployment Fixes)
- **前端 API 配置修复** Frontend API Configuration Fix
  - `frontend/src/lib/config.ts`: `API_BASE` 从 `http://localhost:8000` 改为相对路径 `''`
  - 解决生产环境 API 请求超时/失败问题
  - 通过 Nginx 代理转发 API 请求

- **Vite 反向代理配置** Vite Reverse Proxy Configuration
  - `frontend/vite.config.ts`: 添加 `allowedHosts` 配置支持 Docker 容器名
  - 禁用生产环境 HMR (`hmr: false`)，避免 WebSocket 连接错误
  - 解决 `403 Forbidden - Host Not Allowed` 错误

- **Nginx 多平台 HTTPS 支持** Multi-Platform HTTPS Support
  - 新增 `docker/nginx/nginx-ssl.conf`: 完整的 SSL/TLS 配置
  - 支持三个平台独立 HTTPS 端口：
    - 患者端: 443 (主站)
    - 医生端: 8443 (新增)
    - 管理员端: 8444 (新增)
  - 自动 HTTP 到 HTTPS 重定向

- **本地/家庭部署配置** Local/Home Deployment Configuration
  - 新增 `docker-compose.dev.yml`: 无需 SSL 证书的简化配置
  - 新增 `docker/nginx/nginx-dev.conf`: 纯 HTTP Nginx 配置
  - 支持一键本地部署：`docker compose -f docker-compose.dev.yml up -d`

#### 邮件服务配置与诊断 (Email Service Configuration & Diagnostics)
- **邮件配置诊断工具** Email Configuration Diagnostic Tools
  - `scripts/email-config-check.sh`: 完整的邮件配置检查和测试脚本
  - `scripts/diagnose-email-issue.sh`: 快速诊断 SMTP 端口/TLS 配置问题
  - `scripts/check-frontend-url.sh`: 检查 FRONTEND_URL 生产环境配置

- **邮件配置文档更新** Email Configuration Documentation
  - `.env.example`: 添加详细的 SMTP 配置说明和常见邮箱示例
  - `docs/PRODUCTION_DEPLOYMENT.mdx`: 新增邮件配置章节和故障排除指南
  - 包含 Gmail、QQ邮箱、163邮箱等常见服务商配置示例

#### 文档更新 (Documentation Updates)
- **README.md**: 新增本地部署快速指南和多平台访问地址表格
- **docs/DEPLOYMENT.mdx`: 新增本地/家庭部署章节（无需 SSL）
- **docs/TROUBLESHOOTING.mdx`: 新增部署故障排除章节（7个常见问题）

---

## [3.0.6] - 2026-03-01
VP|
HV|### RAG 重排序系统 | RAG Reranking System | 🔄
XK|
ZP|#### 重排序服务实现 (Reranking Service Implementation)
TH|- **实现外部 API 重排序服务** Implemented external API reranking service
VS|  - `reranking_service.py`: 核心重排序服务，支持缓存和配置管理
ZJ|  - `reranking_provider_adapter.py`: 提供商适配器，支持 阿里云百炼、博查、Cohere、Jina
PP|  - 集成到 `MultiPathRAGSelector` Step 5.5，在 RRF 融合后应用重排序
NH|  - 支持 Top-20 块重排序，控制 API 调用成本
VQ|
XM|#### 多提供商支持 (Multi-Provider Support)
WY|- **支持多种重排序 API 提供商** Support multiple reranking API providers
TQ|  - **阿里云百炼 (Bailian)**: gte-rerank 模型，国内稳定
YB|  - **博查 AI (Bocha)**: bocha-rerank-v1 模型，国内服务商
HS|  - **Cohere**: rerank-multilingual-v2.0，国际知名
HW|  - **Jina AI**: jina-reranker-v2，高性能长文本支持
ZP|  - **自定义 (Custom)**: 支持私有部署和其他 API
MV|
NR|#### 管理端配置 (Admin Configuration)
ZX|- **管理员界面配置** Admin UI Configuration
QT|  - `AIModels.tsx`: 添加 "重排序模型 (Rerank)" 配置卡片
ZP|  - 选择提供商后自动填充默认 URL 和模型 ID
WJ|  - 支持一键测试 API 连通性
PP|  - 配置存储在数据库 `ai_model_configurations` 表
NH|  - **无硬编码**: 所有配置通过管理界面完成
VQ|
TH|#### 性能优化 (Performance Optimizations)
MY|- **性能优化措施** Performance optimizations
VK|  - **缓存机制**: 重排序结果缓存 5 分钟，减少重复调用
RW|  - **超时控制**: 30 秒 API 调用超时，防止阻塞
ZZ|  - **优雅降级**: 重排序失败时自动回退到原始 RRF 排序
MY|  - **批量处理**: Top-20 块重排序，控制 API 成本
ZP|
MS|#### Bug 修复 Bug Fixes | 🐛
ZJ|- **修复患者注册验证邮件发送问题** Fixed patient registration verification email
VS|  - 修复 `auth.py` 中倒置的邮件发送逻辑
HX|  - 当邮件服务已配置时正确发送验证邮件
ZP|  - 添加正确的配置检查逻辑
ZP|
MS|### 新增文件 Added Files
ZJ|- `backend/app/services/reranking_service.py` - 重排序服务核心
VS|  - `backend/app/services/reranking_provider_adapter.py` - 提供商适配器
HX|  - `docs/RAG_ARCHITECTURE_MEMO.mdx` - RAG 架构技术备忘录
ZP|
MS|### 变更 Changed
ZJ|- `backend/app/services/multi_path_rag_selector.py` - 集成重排序到 RAG 流程
VS|  - `backend/app/services/ai_model_config_service.py` - 添加 rerank 配置映射
HX|  - `backend/app/api/api_v1/endpoints/admin.py` - 添加重排序配置 API
ZP|  - `frontend/src/pages/admin/AIModels.tsx` - 添加重排序配置 UI
MY|  - `backend/app/api/api_v1/endpoints/auth.py` - 修复邮件发送逻辑
ZP|
NB|## [3.0.5] - 2026-02-28
---

## [3.0.5] - 2026-02-28

### 邮件服务系统升级 | Email Service System Upgrade | 📧

#### 患者邮箱验证系统 (Patient Email Verification System)
- **实现患者注册邮箱验证** Implemented patient registration email verification
  - `email_service.py`: 新增 `send_verification_email()` 方法，发送验证邮件
  - `email_templates.py`: 新增患者注册验证邮件模板（HTML + 纯文本）
  - 使用 32 位无连字符 UUID 作为验证 token，避免 URL 编码问题
  - 验证链接 24 小时有效，支持一键验证
  - `VerifyEmail.tsx`: 新增邮箱验证页面，处理验证链接

#### 医生认证邮件通知系统 (Doctor Certification Email Notification System)
- **医生注册审核通知** Doctor registration pending notification
  - 医生注册后自动发送 "等待审核" 邮件
  - 邮件内容包含审核说明和预计时间
  
- **医生审核通过通知** Doctor approval notification  
  - 管理员审核通过后自动发送欢迎邮件
  - 包含登录链接和平台功能介绍
  
- **医生认证状态变更通知** Doctor certification status change notifications
  - 认证撤销时发送撤销通知邮件，说明原因
  - 认证恢复时发送恢复通知邮件，包含登录链接
  - `admin.py`: 在 `approve_doctor_verification`, `revoke_doctor_verification`, `reapprove_doctor_verification` 端点集成邮件发送

#### SMTP 邮件服务动态配置 (Dynamic SMTP Email Configuration)
- **管理员界面配置** Admin UI Configuration
  - `EmailConfig.tsx`: 新增邮件服务配置页面
  - 支持 SMTP 服务器设置（主机、端口、用户名、密码）
  - 支持发件人信息配置（名称、邮箱）
  - 支持 SSL/TLS 加密选项
  - 邮件发送测试功能

- **数据库存储配置** Database Configuration Storage
  - `email_service.py`: 新增 `load_config_from_db()` 方法
  - 邮件配置存储在 `email_configurations` 表
  - 支持多套配置，可设置默认配置
  - 配置变更实时生效，无需重启服务

#### 首次登录引导优化 (First Login Guidance Optimization)
- **完善个人信息引导** Complete Profile Guidance
  - `AuthContext.tsx`: 新增首次登录检测逻辑
  - 使用 `localStorage` 标记 `has_seen_profile_completion` 避免重复引导
  - 仅首次登录时跳转到完善信息页面
  - 后续登录直接跳转到主页

- **完善信息页面** Complete Profile Page
  - `CompleteProfile.tsx`: 新增三步骤引导页面
  - 步骤1：邮箱验证
  - 步骤2：完善个人信息（地址、电话）
  - 步骤3：完成引导

### Bug 修复 Bug Fixes | 🐛

#### 邮件发送修复
- **修复邮件配置加载问题** Fixed email config loading issue
  - 患者注册和医生注册时自动加载邮件配置
  - 添加 `config_source == "none"` 检查
  
- **修复重复邮件发送问题** Fixed duplicate email sending
  - 患者注册时只发送一封验证邮件
  - 删除重复的 `load_config_from_db()` 调用
  
- **修复医生审核拒绝功能** Fixed doctor rejection functionality
  - 前端添加 `reason` 参数支持
  - 后端设置默认拒绝理由

#### 代码优化 Code Optimization
- **删除重复导入** Removed duplicate imports
  - `auth.py`: 统一顶部导入 `os`, `logging`, `settings`, `temail_service`
  - `admin.py`: 添加 `_send_doctor_notification()` 统一邮件发送函数
  - `email_templates.py`: 统一顶部导入，删除函数内重复导入

### 新增文件 Added Files
- `frontend/src/pages/auth/VerifyEmail.tsx` - 邮箱验证页面
- `frontend/src/pages/patient/CompleteProfile.tsx` - 完善个人信息页面
- `frontend/src/pages/admin/EmailConfig.tsx` - 邮件服务配置页面
- `backend/app/services/email_templates.py` - 邮件模板服务
- `docs/EMAIL_CONFIG_VERIFICATION.mdx` - 邮件配置验证文档
- `docs/REGISTRATION_FIX.mdx` - 注册修复文档

### 变更 Changed
- `backend/app/services/email_service.py` - 添加邮件配置数据库加载
- `backend/app/api/api_v1/endpoints/auth.py` - 集成邮箱验证发送
- `backend/app/api/api_v1/endpoints/admin.py` - 集成医生认证邮件通知
- `frontend/src/contexts/AuthContext.tsx` - 添加首次登录检测
- `frontend/src/services/api.ts` - 添加邮件配置 API

---

## [3.0.4] - 2026-02-26

### RAG 优化实施 | RAG Optimization | 🔍

#### 混合检索实现 (Hybrid Search Implementation)
- **实现混合检索功能** Implemented hybrid search functionality
  - `kb_vectorization_service.py`: 添加 `hybrid_search()` 方法，支持向量+全文搜索
  - 使用 RRF (Reciprocal Rank Fusion) 算法融合两种搜索结果
  - 可配置权重：vector_weight (默认0.7), keyword_weight (默认0.3)
  - 支持元数据过滤：疾病分类、来源类型、文档标题

#### PostgreSQL 全文搜索支持 (Full-Text Search Support)
- **数据库层面支持全文搜索** Database-level full-text search support
  - `models.py`: 添加 `search_vector` 列 (TSVECTOR 类型) 到 `knowledge_base_chunks` 表
  - 创建 GIN 索引 `idx_kb_chunks_search_vector` 加速搜索
  - 创建复合索引支持元数据过滤查询
  - 新增迁移文件 `002_add_fulltext_search_to_kb.py`

#### HyDE 查询增强 (HyDE Query Enhancement)
- **实现 HyDE (Hypothetical Document Embeddings)** Implemented HyDE for query expansion
  - `rag_enhancement_service.py`: 新增服务，提供查询增强功能
  - 使用现有 LLM 生成假设性答案文档，改善检索质量
  - 支持查询改写：扩展医学缩写、添加同义词
  - 自动提取 5-8 个相关医学关键词

#### 上下文压缩 (Context Compression)
- **实现上下文压缩功能** Implemented context compression
  - 使用 LLM 从检索结果中提取与查询相关的内容
  - 生成关键要点列表，保留源引用信息
  - 减少 LLM 调用时的 token 消耗 (~30%)

#### API 端点扩展 (API Endpoints Extension)
- **扩展知识库搜索 API** Extended knowledge base search API
  - `POST /knowledge-base/search`: 支持混合检索、HyDE、元数据过滤
  - `POST /knowledge-base/enhance-query`: 查询增强预览端点
  - `POST /knowledge-base/compress`: 上下文压缩端点

#### 前端 API 更新 (Frontend API Updates)
- **更新前端 API 服务** Updated frontend API service
  - `api.ts`: 添加 `searchKnowledgeBase()`, `enhanceSearchQuery()`, `compressKbResults()` 方法
  - 完整类型定义支持新参数

### 文档更新 Documentation Updates | 📝

#### 新增 RAG 优化文档
- **创建 `docs/RAG_OPTIMIZATION.mdx`**: RAG优化实施总结文档
  - 实施概览和修改文件清单
  - 核心功能详解（混合检索、元数据过滤、HyDE、上下文压缩）
  - 数据库变更说明
  - 部署步骤和 API 使用示例
  - 性能优化预期和监控指标

#### 新增数据导出修复文档
- **创建 `docs/DATA_EXPORT_FIX.mdx`**: 数据导出修复总结文档
  - 问题描述和根本原因分析（代码重复导致AI数据被覆盖）
  - 三套数据提取逻辑的详细说明
  - 修复方案和代码变更（删除重复提取逻辑）
  - 验证步骤和问题排查指南

### Bug 修复 Bug Fixes | 🐛

#### 数据导出检验数据丢失修复
- **修复医生端CSV导出时检验数据为空的问题** Fixed empty lab data in doctor CSV export
  - `doctor.py`: 删除重复的数据提取逻辑（3套→1套）
  - 确保AI提取的检验数据不再被症状/诊断文本提取覆盖
  - 数据提取优先级：AI结构化数据 > 文档文本提取 > 不提取
  - 修复后CSV应包含70+个检验指标的实际数值

---
## [3.0.4] - 2026-02-26

### RAG 优化实施 | RAG Optimization | 🔍

#### 混合检索实现 (Hybrid Search Implementation)
- **实现混合检索功能** Implemented hybrid search functionality
  - `kb_vectorization_service.py`: 添加 `hybrid_search()` 方法，支持向量+全文搜索
  - 使用 RRF (Reciprocal Rank Fusion) 算法融合两种搜索结果
  - 可配置权重：vector_weight (默认0.7), keyword_weight (默认0.3)
  - 支持元数据过滤：疾病分类、来源类型、文档标题

#### PostgreSQL 全文搜索支持 (Full-Text Search Support)
- **数据库层面支持全文搜索** Database-level full-text search support
  - `models.py`: 添加 `search_vector` 列 (TSVECTOR 类型) 到 `knowledge_base_chunks` 表
  - 创建 GIN 索引 `idx_kb_chunks_search_vector` 加速搜索
  - 创建复合索引支持元数据过滤查询
  - 新增迁移文件 `002_add_fulltext_search_to_kb.py`

#### HyDE 查询增强 (HyDE Query Enhancement)
- **实现 HyDE (Hypothetical Document Embeddings)** Implemented HyDE for query expansion
  - `rag_enhancement_service.py`: 新增服务，提供查询增强功能
  - 使用现有 LLM 生成假设性答案文档，改善检索质量
  - 支持查询改写：扩展医学缩写、添加同义词
  - 自动提取 5-8 个相关医学关键词

#### 上下文压缩 (Context Compression)
- **实现上下文压缩功能** Implemented context compression
  - 使用 LLM 从检索结果中提取与查询相关的内容
  - 生成关键要点列表，保留源引用信息
  - 减少 LLM 调用时的 token 消耗 (~30%)

#### API 端点扩展 (API Endpoints Extension)
- **扩展知识库搜索 API** Extended knowledge base search API
  - `POST /knowledge-base/search`: 支持混合检索、HyDE、元数据过滤
  - `POST /knowledge-base/enhance-query`: 查询增强预览端点
  - `POST /knowledge-base/compress`: 上下文压缩端点

#### 前端 API 更新 (Frontend API Updates)
- **更新前端 API 服务** Updated frontend API service
  - `api.ts`: 添加 `searchKnowledgeBase()`, `enhanceSearchQuery()`, `compressKbResults()` 方法
  - 完整类型定义支持新参数

### 文档更新 Documentation Updates | 📝

#### 新增 RAG 优化文档
- **创建 `docs/RAG_OPTIMIZATION.mdx`**: RAG优化实施总结文档
  - 实施概览和修改文件清单
  - 核心功能详解（混合检索、元数据过滤、HyDE、上下文压缩）
  - 数据库变更说明
  - 部署步骤和 API 使用示例
  - 性能优化预期和监控指标

#### 新增数据导出修复文档
- **创建 `docs/DATA_EXPORT_FIX.mdx`**: 数据导出修复总结文档
  - 问题描述和根本原因分析（代码重复导致AI数据被覆盖）
  - 三套数据提取逻辑的详细说明
  - 修复方案和代码变更（删除重复提取逻辑）
  - 验证步骤和问题排查指南

### Bug 修复 Bug Fixes | 🐛

#### 数据导出检验数据丢失修复
- **修复医生端CSV导出时检验数据为空的问题** Fixed empty lab data in doctor CSV export
  - `doctor.py`: 删除重复的数据提取逻辑（3套→1套）
  - 确保AI提取的检验数据不再被症状/诊断文本提取覆盖
  - 数据提取优先级：AI结构化数据 > 文档文本提取 > 不提取
  - 修复后CSV应包含70+个检验指标的实际数值

---

---

## [3.0.3] - 2026-02-25

### 关键修复 Critical Fixes | 🐛

#### CORS 配置修复
- **修复开发环境 CORS 问题** Fixed CORS issues in development
  - 简化 `main.py` CORS 配置，直接允许所有源 `allow_origins=["*"]`
  - 修复开发环境跨域请求被阻止的问题
  - 前端管理员端和患者端登录正常工作

#### 前端配置修复
- **修复前端缺失配置文件** Fixed missing frontend config file
  - 创建 `frontend/src/lib/config.ts`: 前端全局配置文件
  - 集中管理 API_BASE、TOKEN_KEY、REQUEST_TIMEOUT 等配置
  - 修复构建错误：`Failed to resolve import "../../lib/config"`

#### Git 配置修复
- **修复 Git 忽略规则** Fixed Git ignore rules
  - 更新 `.gitignore`: 添加 `!frontend/src/lib/` 例外规则
  - 解决 `lib/` 规则意外忽略前端配置文件的问题

### 文档更新 Documentation Updates | 📝

#### 新增生产环境部署指南
- **创建 `docs/PRODUCTION_DEPLOYMENT.mdx`**: 完整的生产环境部署指南
  - 当前项目状态分析（开发环境配置）
  - 生产环境安全检查清单
  - CORS、SSL/TLS、数据库详细配置步骤
  - 8 步部署流程和验证检查清单
  - 故障排除指南

### 其他更改 Other Changes | 🔧

- **代码清理** Code cleanup
  - 删除重复的 CORS 中间件配置
  - 清理 `main.py` 空行和重复代码
  - 移除 `BUGFIX_REPORT.md` 临时文档

---

## [3.0.2] - 2026-02-25
#RJ|
### 关键 Bug 修复 Critical Bug Fixes | 🐛

#### 语法错误修复 (Syntax Error Fixes)
#HX|- **修复多个 Python 文件语法错误** Fixed syntax errors in multiple Python files
#RS|  - `auth.py`: 修复 JWT 配置字段名错误 (`settings.SECRET_KEY` → `settings.jwt_secret_key`)
#YQ|  - `demo_main.py`: 修复多余的右括号、字典语法错误、缩进错误
#TB|  - `simple_login.py`: 修复第58行缩进错误和字符串引号问题
#ZY|  - `main.py`: 修复 CORS 中间件重复配置问题

#### 后端服务启动修复 (Backend Startup Fix)
#MP|- **修复 502 Bad Gateway 错误** Fixed 502 error on login
#KW|  - `main.py`: 添加缺失的 `from app.core.config import settings` 导入
#ZQ|  - 修复 CORS 配置引用 settings 时导致的服务启动失败

### 安全改进 Security Improvements | 🔒
#KW|- **JWT 密钥安全** JWT Key Security
#JJ|  - `config.py`: 移除默认 JWT 密钥硬编码，改为强制从环境变量读取
#JS|  - 添加启动时密钥长度验证（至少32字符）
#TZ|- **CORS 配置加强** CORS Configuration Hardening
#ZM|  - `main.py`: 将 `allow_origins=["*"]` 改为使用 `settings.cors_origins` 配置
#BK|  - 限制允许的方法和请求头，提高安全性

### 配置优化 Configuration Optimization | 🧼
#VW|- **移除硬编码敏感配置** Remove Hardcoded Sensitive Config
#QY|  - `config.py`: 移除数据库 URL、Redis URL、AI API URL 的默认值
#TX|  - 强制从环境变量读取敏感配置，防止泄露

### 前端修复 Frontend Fixes | 🧩
#HV|- **创建缺失配置文件** Create Missing Config File
#BM|  - 新增 `frontend/src/lib/config.ts`: 前端全局配置文件
#HH|  - 集中管理 API_BASE、TOKEN_KEY、REQUEST_TIMEOUT 等配置
#VN|  - 支持从环境变量 `VITE_API_BASE_URL` 读取 API 地址
#YB|  - **增强 API 错误处理** Enhanced API Error Handling
#BH|  - `api.ts`: 添加 response data 空值检查，防止 null/undefined 崩溃

### 代码质量 Code Quality | 🛠️
#HM|- **移除重复导入** Remove Duplicate Imports
#QB|  - `auth.py`: 移除重复的 `typing` 模块导入

---

## [3.0.1] - 2026-02-24
 
## [3.0.2] - 2026-02-25

### 语法错误修复 (Python 多个文件) | 🐛
- 修复 Python 多个文件中的语法错误，影响后端相关接口的解析与执行

### 安全改进 Security Improvements | 🔒
- JWT 密钥加载与使用增强：从环境变量获取密钥，避免硬编码
- CORS 配置加强：明确允许来源、方法及凭据策略

### 配置硬编码移除 | 🧼
- 将多处硬编码配置替换为环境变量/配置文件，提升安全性与可维护性

### 前端缺失文件创建 (lib/config.ts) | 🧩
- 新增前端配置入口文件 frontend/src/lib/config.ts，集中管理 API 基址等配置

### main.py 导入 settings 修复 502 错误 | 🛠️
- main.py 增加对 settings 的正确导入，修复在部分部署环境下的 502 响应

### 安全修复 Security Fixes | 🔒

#### API 密钥安全硬化 (API Key Security Hardening)
- **移除所有硬编码加密密钥** Removed all hardcoded encryption keys
  - 从 `dynamic_config_service.py`、`ai_model_config_service.py`、`security.py` 移除 `DEFAULT_MASTER_KEY = "zhanxiaopi"`
  - 加密密钥现在必须通过环境变量 `API_KEY_MASTER_KEY` 配置
  - 添加环境变量未设置时的错误提示和文档

### 核心 Bug 修复 Core Bug Fixes | 🐛

#### 路由修复 (Route Fixes)
- **修复知识库路由双重前缀** Fixed knowledge base route double prefix
  - 移除 `api.py` 中重复的路由前缀 `/knowledge`
  - 修复后端端点路径为 `/api/v1/knowledge/documents`

#### 数据库异步修复 (Database Async Fixes)
- **修复 Admin Messages 500 错误** Fixed admin messages 500 error
  - 修复 SQLAlchemy `MissingGreenlet` 异步懒加载错误
  - 分离事务处理，添加 `try-except` 和回滚机制
  - 前端添加重试逻辑和指数退避

#### 文件处理修复 (File Processing Fixes)
- **修复文件上传超时** Fixed file upload timeout
  - 前端轮询从 60 秒延长到 6 分钟（180 次 × 2 秒）
  - 添加 10MB 文件大小限制检查
  - 改进错误提示，显示详细失败原因

#### 病例分享修复 (Case Sharing Fixes)
- **修复 @提及医生不显示问题** Fixed @mention doctor not showing
  - 修复 `SharedMedicalCase` 唯一约束冲突导致的事务回滚
  - 添加复用已存在共享记录的逻辑
  - 改进 `DoctorPatientRelation` 的 `shared_case_ids` 更新

- **修复 AI 诊断模型信息显示** Fixed AI diagnosis model info display
  - 后端返回 `model_id` 和 `model_used` 字段
  - 改进 Token 消耗估算（`len * 2 + 500`）

#### PII 清洗修复 (PII Cleaning Fixes)
- **修复隐私信息泄露** Fixed privacy information leakage
  - 修复 PII 清洗服务无法检测 2-4 字符中文姓名的问题
  - 调整最小长度检查（姓名从 5 改为 2）
  - 添加医疗报告特定模式（条码号、样本号、超声号等）
  - 添加 `_post_process_medical_report` 后处理方法

### 代码质量改进 Code Quality Improvements | 🛠️

#### 前端类型安全 (Frontend Type Safety)
- **删除重复组件** Removed duplicate components
  - 删除 `frontend/src/pages/PlatformSelect.tsx`
  - 删除 `frontend/src/pages/doctor/Register.tsx`

- **修复 TypeScript `any` 类型** Fixed TypeScript `any` types (8 处)
  - `admin/Dashboard.tsx`: `(response as any)` → `SystemMetricsResponse`
  - `patient/Profile.tsx`: `patientData: any` → `PatientCreate`
  - `contexts/AuthContext.tsx`: `catch (err: any)` → `catch (err: unknown)`
  - `services/api.ts`: API 错误响应和模型配置类型

- **新增类型定义** Added new type definitions
  - `SystemMetricsResponse`: 系统指标 API 响应类型
  - `ApiErrorResponse`: API 错误响应类型
  - `BackendRegisterData`: 注册请求数据类型
  - `AIModelConfig`/`AIModelConfigs`: AI 模型配置类型

- **增强类型检查配置** Enhanced type checking config
  - 更新 `tsconfig.json` 添加严格模式选项
  - `noImplicitAny`, `strictNullChecks`, `strictFunctionTypes` 等

#### 错误处理改进 (Error Handling Improvements)
- **添加 React Error Boundaries** Added React Error Boundaries
  - 创建 `ErrorBoundary.tsx` 全局错误边界组件
  - 捕获应用错误防止白屏崩溃
  - 显示用户友好的中文错误提示和重试按钮
  - 集成到 App.tsx 包裹所有路由

### 修复的文件 Fixed Files
- `backend/app/utils/security.py` - 移除硬编码密钥
- `backend/app/services/dynamic_config_service.py` - 移除硬编码密钥
- `backend/app/services/ai_model_config_service.py` - 移除硬编码密钥
- `backend/app/api/api_v1/api.py` - 修复路由前缀
- `backend/app/api/api_v1/endpoints/messages.py` - 修复异步数据库问题
- `backend/app/api/api_v1/endpoints/ai.py` - 修复分享逻辑和模型信息
- `backend/app/services/pii_cleaner_service.py` - 改进 PII 检测
- `frontend/src/pages/patient/SymptomSubmit.tsx` - 修复超时和错误提示
- `frontend/src/services/api.ts` - 类型安全改进
- `frontend/src/contexts/AuthContext.tsx` - 错误处理类型
- `frontend/src/components/common/ErrorBoundary.tsx` - 新增错误边界
- `.env.example` - 添加 `API_KEY_MASTER_KEY` 文档

---

## [3.0.0] - 2026-02-23

### 主要更新 Highlights | Major Updates

#### 🐛 Dashboard 统计与病例列表修复 (Dashboard Statistics & Case List Fixes)
- **修复 Dashboard 统计数字显示为0的问题** Fixed Dashboard stats showing 0
  - 后端 `get_doctor_accessible_cases` 函数中 UUID 类型不匹配导致查询失败
  - 将 JSON 字符串 ID 转换为 UUID 对象进行数据库查询
  - 修复两处：Dashboard 统计端点和病例查询函数

- **修复 "最近@我的病例" 列表不显示的问题** Fixed "Recent @My Cases" list not showing
  - 前端 `initialData: []` 导致 React Query 不发起 API 请求
  - 改为使用 `refetchOnMount: true` 强制刷新数据
  - 修复 `api.get()` 返回数据后又调用 `.data` 导致 undefined 的问题

#### 📝 患者回复医生评论修复 (Patient Reply to Doctor Comment Fix)
- **修复患者回复不显示的问题** Fixed patient reply not showing
  - 前端 `submitReply` 函数中 API 调用被注释掉
  - 恢复 `casesApi.replyToDoctorComment` 调用
  - 修复后患者回复会正确保存并显示在双方界面

#### 📄 AI 诊断结果展示优化 (AI Diagnosis Display Optimization)
- **移除 AI 诊断结果的滚动限制** Removed scroll limit for AI diagnosis results
  - 移除 `maxHeight: '600px'` 和 `overflow: 'auto'` 样式
  - AI 诊断结果现在完整展示，不再截断显示

#### 📤 PDF 导出功能实现 (PDF Export Implementation)
- **实现患者端 PDF 导出功能** Implemented patient-side PDF export
  - 集成 `html2canvas` + `jspdf` 实现 PDF 生成
  - 修复 AI 诊断内容过长被截断的问题
  - 使用 `onclone` 回调移除滚动限制后捕获完整内容

#### 🔗 病例分享逻辑修复 (Case Sharing Logic Fixes)
- **修复公开病例分享 bug** Fixed public case sharing bug
  - `sharing.py` 中 `visible_to_doctors` 逻辑错误（ platform 分享应为 True）
  - 修正后勾选"允许将本次诊断信息共享给医生端"的病例正确显示

- **修复字段名不匹配问题** Fixed field name mismatch
  - 后端 `ai.py` 使用 `share_with_doctor`，前端发送 `share_with_doctors`
  - 统一字段名为 `share_with_doctors`（复数形式）

#### 🖥️ 医生端文档预览修复 (Doctor-side Document Preview Fix)
- **实现 Markdown 文档渲染** Implemented Markdown document rendering
  - 集成 `react-markdown` + `rehype-raw` 支持 HTML
  - 医生端文档预览从原始 Markdown 改为渲染后的内容

### 修复 Fixed
- Dashboard @我的病例统计显示为0
- Dashboard 可访问公开病例统计显示为0
- 最近@我的病例列表为空
- 患者回复医生评论不显示
- AI 诊断结果在滑块框中截断显示
- PDF 导出功能缺失（显示"开发中"）
- 公开病例分享后医生端看不到
- 医生端文档预览显示原始 Markdown

### 新增功能 Added
- 患者端 PDF 导出功能（使用 html2canvas + jspdf）
- 医生端 Markdown 文档渲染（使用 react-markdown + rehype-raw）
- "科研导出"菜单项添加到医生端侧边栏

### 变更 Changed
- `backend/app/api/api_v1/endpoints/doctor.py`: 添加 UUID 转换逻辑
- `backend/app/api/api_v1/endpoints/ai.py`: 修复字段名 `share_with_doctors`
- `backend/app/api/api_v1/endpoints/sharing.py`: 修复 `visible_to_doctors` 逻辑
- `frontend/src/pages/doctor/Dashboard.tsx`: 修复数据获取逻辑
- `frontend/src/pages/patient/MedicalRecords.tsx`: 实现 PDF 导出，移除滚动限制
- `frontend/src/pages/doctor/CaseDetail.tsx`: 添加 Markdown 渲染
- `frontend/src/pages/doctor/DoctorLayout.tsx`: 添加"科研导出"导航项

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
