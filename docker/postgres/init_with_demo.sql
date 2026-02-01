-- 创建数据库表
-- 创建扩展
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 创建用户表
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
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

-- 创建患者表
CREATE TABLE IF NOT EXISTS patients (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    name VARCHAR(255) NOT NULL,
    date_of_birth VARCHAR(10) NOT NULL,
    gender VARCHAR(10),
    phone VARCHAR(20),
    address TEXT,
    emergency_contact VARCHAR(255),
    medical_record_number VARCHAR(100) UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT fk_patients_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 创建医疗案例表
CREATE TABLE IF NOT EXISTS medical_cases (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID NOT NULL,
    disease_id UUID NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    symptoms TEXT,
    clinical_findings JSONB,
    diagnosis TEXT,
    severity VARCHAR(20),
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT fk_medical_cases_patient FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
    CONSTRAINT fk_medical_cases_disease FOREIGN KEY (disease_id) REFERENCES diseases(id)
);

-- 创建疾病表
CREATE TABLE IF NOT EXISTS diseases (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) UNIQUE NOT NULL,
    code VARCHAR(50) UNIQUE,
    description TEXT,
    guidelines_json JSONB,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 创建文档表
CREATE TABLE IF NOT EXISTS medical_documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    medical_case_id UUID NOT NULL,
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    file_size BIGINT,
    upload_status VARCHAR(50) DEFAULT 'uploading',
    extracted_content TEXT,
    extraction_metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT fk_medical_documents_medical_case FOREIGN KEY (medical_case_id) REFERENCES medical_cases(id) ON DELETE CASCADE
);

-- 创建用户会话表
CREATE TABLE IF NOT EXISTS user_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    token_id VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT true,
    CONSTRAINT fk_sessions_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 创建审计日志表
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id UUID,
    details JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT fk_logs_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_patients_user_id ON patients(user_id);
CREATE INDEX IF NOT EXISTS idx_patients_name ON patients(name);
CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_expires_at ON user_sessions(expires_at);
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_medical_documents_user_id ON medical_documents(user_id);
CREATE INDEX IF NOT EXISTS idx_medical_cases_patient_id ON medical_cases(patient_id);
CREATE INDEX IF NOT EXISTS idx_medical_cases_disease_id ON medical_cases(disease_id);

-- 插入演示用户
INSERT INTO users (
    id, email, password_hash, full_name,
    professional_title, license_number,
    is_active, is_verified
) VALUES (
    '00000000-0000-0000-0000-000000000001',
    'demo@medicare.ai',
    '$2b$12$YVZPHPlJveuse3FkKiKBfei9htyuYeTlqfvjs9Hr2yErLYBwj4S/G',
    '演示医生',
    '主治医师',
    'DEMO001',
    true,
    true
) ON CONFLICT (email) DO NOTHING;

-- 插入示例患者数据
INSERT INTO patients (
    id, user_id, name, date_of_birth, gender, phone, address
) VALUES
    ('00000000-0000-0000-0000-000000000002',
     '00000000-0000-0000-0000-000000000001',
     '小明', '2018-05-15', '男', '13800138000',
     '北京市朝阳区'),
    ('00000000-0000-0000-0000-000000000003',
     '00000000-0000-0000-0000-000000000001',
     '小红', '2019-08-20', '女', '13900139000',
     '上海市浦东新区')
ON CONFLICT DO NOTHING;

-- 插入示例疾病数据
INSERT INTO diseases (id, name, code, description, guidelines_json)
VALUES
    ('00000000-0000-0000-0000-000000000010',
     '儿童的咳嗽变异性哮喘',
     'J45.9',
     '咳嗽变异性哮喘是一种特殊类型的哮喘，主要表现为慢性咳嗽，是儿童慢性咳嗽的常见原因之一。',
     '{"symptoms": ["慢性咳嗽", "夜间或清晨加重", "运动后诱发"], "treatment": "支气管舒张剂, 吸入糖皮质激素"}')
ON CONFLICT DO NOTHING;

-- 插入示例医疗案例数据
INSERT INTO medical_cases (
    id, patient_id, disease_id, title, description, symptoms, diagnosis, severity, status
) VALUES
    ('00000000-0000-0000-0000-000000000020',
     '00000000-0000-0000-0000-000000000002',
     '00000000-0000-0000-0000-000000000010',
     '反复咳嗽一个月',
     '患儿一个月前开始出现反复咳嗽症状，多在夜间和清晨加重，运动后症状明显。',
     '夜间和清晨咳嗽、运动后诱发咳嗽、无喘息症状',
     '儿童的咳嗽变异性哮喘',
     'moderate',
     'active'
    ),
    ('00000000-0000-0000-0000-000000000021',
     '00000000-0000-0000-0000-000000000003',
     '00000000-0000-0000-0000-000000000010',
     '慢性咳嗽两月余',
     '患儿两月前开始慢性咳嗽，无明显喘息，抗感染治疗效果不佳。',
     '持续咳嗽、干咳为主、无发热',
     '儿童的咳嗽变异性哮喘',
     'mild',
     'active'
)
ON CONFLICT DO NOTHING;
