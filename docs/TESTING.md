# MediCare_AI 测试指南

本文档提供了 MediCare_AI 智能疾病管理系统的完整测试流程。

## 测试环境准备

### 前提条件

1. 系统已成功部署（参考《部署指南》）
2. 所有服务正常运行
3. 数据库迁移已完成
4. 管理员账号已创建

### 验证系统状态

```bash
# 检查服务状态
docker-compose ps

# 所有服务应显示 "Up" 状态

# 测试健康检查
curl https://localhost/health

# 应返回: {"status": "healthy", "service": "MediCare_AI API"}
```

## 功能测试流程

### 测试 1: 用户注册

**目标**: 验证新用户可以成功注册

**步骤**:
1. 访问 https://localhost
2. 点击 "注册" 按钮
3. 填写注册表单：
   - 邮箱: `test@medicare.ai`
   - 密码: `Test123456!`
   - 姓名: `测试医生`
   - 职称: `主治医师`
   - 执业证号: `TEST123456`
4. 点击 "注册" 按钮

**预期结果**:
- 注册成功
- 自动登录到系统
- 跳转到仪表板页面

**验证点**:
- [ ] 注册表单显示正确
- [ ] 表单验证工作正常
- [ ] 注册成功后自动登录
- [ ] 用户信息正确显示

---

### 测试 2: 用户登录

**目标**: 验证已注册用户可以成功登录

**步骤**:
1. 访问 https://localhost
2. 点击 "登录" 按钮
3. 输入凭据：
   - 邮箱: `admin@medicare.ai`（或注册的邮箱）
   - 密码: `admin123456`（或注册的密码）
4. 点击 "登录" 按钮

**预期结果**:
- 登录成功
- 跳转到仪表板页面
- 显示用户姓名

**验证点**:
- [ ] 登录表单显示正确
- [ ] 错误凭据提示错误信息
- [ ] 登录成功后跳转到仪表板
- [ ] 令牌正确存储在 localStorage

---

### 测试 3: 仪表板 - 疾病选择

**目标**: 验证仪表板正确显示可管理的疾病

**步骤**:
1. 确保已登录
2. 查看仪表板页面
3. 检查疾病列表

**预期结果**:
- 显示 "儿童支气管哮喘" 疾病卡片
- 显示疾病描述
- 显示已管理患者数量
- "进入管理" 按钮可用

**验证点**:
- [ ] 疾病卡片正确显示
- [ ] 患者数量统计正确
- [ ] 疾病描述完整
- [ ] 点击 "进入管理" 跳转到患者列表

---

### 测试 4: 患者管理 - 查看患者列表

**目标**: 验证患者列表正确显示

**步骤**:
1. 在仪表板点击 "进入管理"
2. 查看患者列表页面

**预期结果**:
- 显示患者列表（或空状态）
- 显示 "添加新患者" 按钮
- 搜索功能可用
- 分页功能正常

**验证点**:
- [ ] 页面标题正确
- [ ] 患者列表正确显示
- [ ] 搜索功能工作正常
- [ ] 空状态显示正确提示

---

### 测试 5: 患者管理 - 创建患者

**目标**: 验证可以成功创建新患者

**步骤**:
1. 在患者列表页面点击 "添加新患者"
2. 填写患者信息：
   - 姓名: `张小明`
   - 出生日期: `2015-05-10`
   - 性别: `男`
   - 联系电话: `13800138000`
   - 地址: `北京市朝阳区`
   - 紧急联系人: `张三 13900139000`
   - 医疗记录号: `P-2024-0001`
3. 点击 "保存患者" 按钮

**预期结果**:
- 患者创建成功
- 显示成功提示
- 自动跳转到患者列表
- 新患者出现在列表中

**验证点**:
- [ ] 表单字段正确显示
- [ ] 表单验证工作正常
- [ ] 保存成功后跳转
- [ ] 新患者出现在列表
- [ ] 患者信息正确显示

---

### 测试 6: 患者管理 - 查看患者详情

**目标**: 验证可以查看患者详细信息

**步骤**:
1. 在患者列表中点击某个患者的 "查看" 按钮
2. 查看患者详情页面

**预期结果**:
- 显示患者基本信息
- 显示病例管理标签
- 显示统计信息

**验证点**:
- [ ] 患者基本信息正确
- [ ] 统计信息准确
- [ ] 标签切换正常
- [ ] 返回按钮工作正常

---

### 测试 7: AI 辅助诊断

**目标**: 验证 AI 辅助诊断功能

**注意**: 此测试需要先创建患者病例。由于病例管理功能仍在开发中，此测试暂时跳过。

**预期功能**:
- 选择病例
- 点击 "AI 辅助诊断"
- 显示 AI 诊断建议
- 显示诊断推理过程
- 显示建议和警示信息

**验证点**:
- [ ] AI 调用成功
- [ ] 诊断结果合理
- [ ] 推理过程清晰
- [ ] 建议和警示信息完整

---

### 测试 8: 文档上传

**目标**: 验证可以上传患者文档

**注意**: 此功能需要先创建患者病例。由于病例管理功能仍在开发中，此测试暂时跳过。

**预期功能**:
- 选择病例
- 点击 "上传文档"
- 选择文件
- 文件上传成功
- 文档列表更新

**验证点**:
- [ ] 文件选择正常
- [ ] 上传进度显示
- [ ] 上传成功提示
- [ ] 文件出现在列表

---

### 测试 9: 用户登出

**目标**: 验证用户可以成功登出

**步骤**:
1. 点击右上角用户菜单
2. 选择 "登出"

**预期结果**:
- 成功登出
- 清除本地存储
- 跳转到登录页面

**验证点**:
- [ ] 登出成功
- [ ] localStorage 被清除
- [ ] 跳转到登录页面
- [ ] 不能直接访问受保护页面

---

## API 测试

### 测试后端 API 端点

访问 https://localhost/api/docs 查看 Swagger UI。

#### 测试认证 API

```bash
# 注册用户
curl -X POST https://localhost/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@medicare.ai",
    "password": "Test123456!",
    "full_name": "测试医生"
  }'

# 登录
curl -X POST https://localhost/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@medicare.ai",
    "password": "Test123456!"
  }'

# 获取当前用户（需要 Bearer Token）
curl -X GET https://localhost/api/v1/auth/me \
  -H "Authorization: Bearer <access_token>"
```

#### 测试患者管理 API

```bash
# 获取患者列表
curl -X GET https://localhost/api/v1/patients \
  -H "Authorization: Bearer <access_token>"

# 创建患者
curl -X POST https://localhost/api/v1/patients \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "张小明",
    "date_of_birth": "2015-05-10",
    "gender": "male",
    "phone": "13800138000",
    "medical_record_number": "P-2024-0001"
  }'

# 获取患者详情
curl -X GET https://localhost/api/v1/patients/<patient_id> \
  -H "Authorization: Bearer <access_token>"
```

#### 测试 AI 服务 API

```bash
# 获取 AI 诊断
curl -X POST https://localhost/api/v1/ai/diagnose \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_info": {
      "name": "张小明",
      "date_of_birth": "2015-05-10",
      "gender": "male"
    },
    "symptoms": "反复咳嗽、喘息",
    "clinical_findings": {},
    "diagnosis": "",
    "documents_content": [],
    "disease_guidelines": {}
  }'
```

**验证点**:
- [ ] 所有 API 端点可访问
- [ ] 认证正常工作
- [ ] 响应格式正确
- [ ] 错误处理正确

---

## 性能测试

### 响应时间测试

```bash
# 测试 API 响应时间
time curl -X GET https://localhost/api/v1/patients \
  -H "Authorization: Bearer <access_token>"

# 预期: < 1s
```

**验证点**:
- [ ] API 响应时间 < 1s
- [ ] 页面加载时间 < 3s
- [ ] 文件上传速度正常

### 并发测试

```bash
# 使用 Apache Bench 进行并发测试
ab -n 1000 -c 10 https://localhost/api/v1/patients

# 检查结果
# - Requests per second > 100
# - Failed requests = 0
```

**验证点**:
- [ ] 系统支持 10 并发连接
- [ ] 无失败请求
- [ ] 响应时间稳定

---

## 安全测试

### SQL 注入测试

```bash
# 尝试 SQL 注入
curl -X POST https://localhost/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@medicare.ai\" OR 1=1--",
    "password": "any"
  }'

# 预期: 返回 401 未授权
```

### XSS 测试

```bash
# 尝试 XSS 攻击
curl -X POST https://localhost/api/v1/patients \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "<script>alert(\"XSS\")</script>",
    "date_of_birth": "2015-05-10"
  }'

# 预期: 请求被拒绝或数据被转义
```

### CSRF 测试

检查 CSRF 保护是否正常工作。

**验证点**:
- [ ] SQL 注入被阻止
- [ ] XSS 攻击被转义
- [ ] CSRF 保护有效
- [ ] HTTPS 强制启用

---

## 集成测试

### 完整工作流测试

1. **注册新用户**
2. **登录系统**
3. **查看仪表板**
4. **选择疾病**
5. **创建患者**
6. **查看患者详情**
7. **（待实现）创建病例**
8. **（待实现）上传文档**
9. **（待实现）获取 AI 诊断**
10. **登出系统**

**验证点**:
- [ ] 完整流程无错误
- [ ] 数据一致性正确
- [ ] 用户体验流畅

---

## 测试报告模板

```markdown
# 测试报告

测试日期: YYYY-MM-DD
测试人员: [姓名]
系统版本: v1.0.0

## 测试结果

| 测试项 | 状态 | 备注 |
|--------|------|------|
| 用户注册 | ✅/❌ | |
| 用户登录 | ✅/❌ | |
| 仪表板 | ✅/❌ | |
| 患者列表 | ✅/❌ | |
| 创建患者 | ✅/❌ | |
| 患者详情 | ✅/❌ | |
| AI 诊断 | ✅/❌ | |
| 文档上传 | ✅/❌ | |
| 用户登出 | ✅/❌ | |
| API 测试 | ✅/❌ | |

## 发现的问题

1. [问题描述]
   - 严重程度: 高/中/低
   - 复现步骤
   - 预期行为
   - 实际行为

## 总结

- 总测试数: XX
- 通过: XX
- 失败: XX
- 通过率: XX%

## 建议

[改进建议]
```

---

## 已知问题和限制

### 当前限制

1. **病例管理功能** - 正在开发中
   - 暂时无法创建患者病例
   - 暂时无法上传文档
   - 暂时无法获取 AI 诊断

2. **AI 模型响应时间**
   - 首次调用可能较慢
   - 建议使用缓存优化

3. **文件上传大小限制**
   - 当前限制: 200MB
   - 可在配置文件中调整

### 计划改进

1. [ ] 实现完整的病例管理功能
2. [ ] 添加实时通知功能
3. [ ] 优化 AI 响应时间
4. [ ] 增加更多疾病支持
5. [ ] 添加数据导出功能

---

**测试完成！**
