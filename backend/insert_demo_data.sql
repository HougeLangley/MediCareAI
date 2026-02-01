-- 创建演示用户账号
-- 注意：密码是 'Demo123456!' 的bcrypt哈希值

-- 插入演示用户
INSERT INTO users (
    id,
    email,
    password_hash,
    full_name,
    professional_title,
    license_number,
    is_active,
    is_verified,
    created_at,
    updated_at
) VALUES (
    '00000000-0000-0000-0000-000000000001',
    'demo@medicare.ai',
    '$2b$12$YVZPHPlJveuse3FkKiKBfei9htyuYeTlqfvjs9Hr2yErLYBwj4S/G',
    '演示医生',
    '主治医师',
    'DEMO001',
    true,
    true,
    NOW(),
    NOW()
) ON CONFLICT (email) DO NOTHING;

-- 创建示例患者数据
INSERT INTO patients (
    id,
    user_id,
    name,
    age,
    gender,
    phone,
    email,
    address,
    created_at,
    updated_at
) VALUES (
    '00000000-0000-0000-0000-000000000002',
    '00000000-0000-0000-0000-000000000001',
    '张三',
    35,
    '男',
    '13800138000',
    'zhangsan@example.com',
    '北京市朝阳区',
    NOW(),
    NOW()
),
(
    '00000000-0000-0000-0000-000000000003',
    '00000000-0000-0000-0000-000000000001',
    '李四',
    42,
    '女',
    '13900139000',
    'lisi@example.com',
    '上海市浦东新区',
    NOW(),
    NOW()
) ON CONFLICT (id) DO NOTHING;

-- 创建示例疾病数据
INSERT INTO diseases (
    id,
    name,
    code,
    description,
    guidelines_json,
    is_active,
    created_at
) VALUES (
    '00000000-0000-0000-0000-000000000010',
    '高血压',
    'I10',
    '高血压是一种常见的心血管疾病，以体循环动脉血压增高为主要特征。',
    '{"symptoms": ["头晕", "头痛", "心悸"], "treatment": "降压药物"}',
    true,
    NOW()
),
(
    '00000000-0000-0000-0000-000000000011',
    '糖尿病',
    'E11',
    '糖尿病是一组以高血糖为特征的代谢性疾病。',
    '{"symptoms": ["多饮", "多食", "多尿"], "treatment": "胰岛素治疗"}',
    true,
    NOW()
),
(
    '00000000-0000-0000-0000-000000000012',
    '冠心病',
    'I25',
    '冠心病是冠状动脉粥样硬化性心脏病的简称。',
    '{"symptoms": ["胸痛", "呼吸困难"], "treatment": "药物治疗或手术"}',
    true,
    NOW()
) ON CONFLICT (id) DO NOTHING;
