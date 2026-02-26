/**
 * MediCareAI TypeScript Types
 * 类型定义文件 - 与后端 API 对应
 */

// User Types
export interface User {
  id: string;
  email: string;
  full_name: string;
  role: 'patient' | 'doctor' | 'admin';
  phone?: string;
  is_active: boolean;
  is_verified: boolean;

  // Patient fields
  date_of_birth?: string;
  gender?: string;
  address?: string;
  emergency_contact?: string;
  anonymous_profile?: AnonymousProfile;

  // Doctor fields
  title?: string;
  department?: string;
  professional_type?: string;
  specialty?: string;
  hospital?: string;
  license_number?: string;
  is_verified_doctor?: boolean;
  display_name?: string;

  // Admin fields
  admin_level?: 'super' | 'regular';
  last_login_at?: string;

  created_at: string;
  updated_at?: string;
}

export interface AnonymousProfile {
  age_range?: string;
  gender?: string;
  city_tier?: string;
  city_environment?: string;
  has_family_history?: boolean;
}

  // Auth Types
export interface RegisterData {
  email: string;
  password: string;
  role: 'patient' | 'doctor' | 'admin';
  full_name: string;
  emergency_contact?: string;
  phone?: string;
  date_of_birth?: string;
  gender?: string;
  address?: string;
  terms?: boolean;

  // Doctor specific
  title?: string;
  department?: string;
  hospital?: string;
  license_number?: string;
  specialty?: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
  platform?: string;
}

export interface AuthResponse {
  user: User;
  tokens: {
    access_token: string;
    refresh_token: string;
    token_type: string;
    expires_in: number;
  };
}

// Patient Types
export interface Patient {
  id: string;
  user_id: string;
  full_name: string;
  name?: string;
  phone?: string;
  address?: string;
  date_of_birth?: string;
  gender?: string;
  emergency_contact?: string;
  medical_record_number?: string;
  created_at: string;
}

// Medical Case Types
export interface MedicalCase {
  id: string;
  patient_id: string;
  disease_id?: string;
  title: string;
  description?: string;
  symptoms: string;
  clinical_findings?: ClinicalFindings;
  diagnosis?: string;
  severity?: 'low' | 'medium' | 'high' | 'critical';
  status: 'active' | 'completed' | 'archived';
  is_shared: boolean;
  share_scope: 'private' | 'to_doctor' | 'platform_anonymous';
  created_at: string;
  updated_at: string;

  // Relations
  patient?: User;
  disease?: Disease;
  medical_documents?: MedicalDocument[];
  ai_feedbacks?: AIFeedback[];
}

export interface ClinicalFindings {
  body_temperature?: number;
  blood_pressure?: string;
  heart_rate?: number;
  respiratory_rate?: number;
  physical_exam?: string;
}

// Disease Types
export interface Disease {
  id: string;
  name: string;
  code?: string;
  description?: string;
  category?: string;
  guidelines_json?: unknown;
  is_active: boolean;
}

// Chronic Disease Types
export interface ChronicDisease {
  id: string;
  name?: string;
  icd10_code: string;
  icd10_name: string;
  disease_type: 'chronic' | 'special' | 'both';
  common_names?: string[];
  category?: string;
  description?: string;
  medical_notes?: string;
  is_active: boolean;
}

export interface ChronicDiseaseListResponse {
  items: ChronicDisease[];
  total: number;
  page: number;
  page_size: number;
}

export interface PatientChronicConditionListResponse {
  items: PatientChronicCondition[];
  total: number;
}

export interface PatientChronicCondition {
  id: string;
  patient_id: string;
  disease_id: string;
  diagnosis_date?: string;
  severity?: 'mild' | 'moderate' | 'severe';
  notes?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  disease?: ChronicDisease;
  chronic_disease?: ChronicDisease;
}

// Medical Document Types
export interface MedicalDocument {
  id: string;
  medical_case_id: string;
  filename: string;
  original_filename: string;
  file_type: string;
  file_size?: number;
  file_path?: string;
  upload_status: string;
  extracted_content?: ExtractedContent;
  cleaned_content?: ExtractedContent;
  pii_cleaning_status: 'pending' | 'completed' | 'failed';
  pii_detected?: PIIDetected[];
  cleaning_confidence?: number;
  extraction_metadata?: unknown;
  created_at: string;
  updated_at: string;
}

export interface ExtractedContent {
  text?: string;
  markdown?: string;
  tables?: unknown[];
  images?: unknown[];
  metadata?: {
    page_count?: number;
    title?: string;
    author?: string;
  };
}

export interface PIIDetected {
  type: 'name' | 'id_number' | 'phone' | 'address' | 'email' | 'other';
  value: string;
  start: number;
  end: number;
}

// AI Feedback Types
export interface AIFeedback {
  id: string;
  medical_case_id: string;
  feedback_type: string;
  input_data: unknown;
  ai_response: AIResponse;
  knowledge_sources?: KnowledgeSource[];
  confidence_score?: number;
  recommendations?: string;
  follow_up_plan?: FollowUpPlan;
  is_reviewed: boolean;
  reviewed_by?: string;
  review_notes?: string;
  created_at: string;
  updated_at: string;
}

export interface AIResponse {
  summary?: string;
  analysis?: string;
  diagnosis?: string;
  recommendations?: string[];
  warnings?: string[];
  follow_up_suggestions?: string[];
  severity_assessment?: string;
  model_id?: string;
  tokens_used?: number;
}

export interface KnowledgeChunk {
  chunk_id: string;
  document_title?: string;
  section_title?: string;
  chunk_text?: string;
  text_preview?: string;
  relevance_score?: number;
  similarity_score?: number;
  source_file?: string;
}

export interface KnowledgeSource {
  chunk_id?: string;
  disease_category?: string;
  document_title?: string;
  section_title?: string;
  relevance_score?: number;
  chunk_text?: string;
  category?: string;
  category_name?: string;
  chunks?: KnowledgeChunk[];
  chunks_count?: number;
  selection_reason?: string;
}

export interface FollowUpPlan {
  recommended_date?: string;
  type?: string;
  notes?: string;
}

// AI Diagnosis Request Types
export interface DiagnosisRequest {
  symptoms: string;
  symptom_duration?: string;
  symptom_severity?: string;
  document_ids?: string[];
  doctor_ids?: string[];
  share_with_doctors?: boolean;
  language?: 'zh' | 'en';
  case_id?: string;  // 用于更新现有病历，避免重复创建
}

// Doctor Types
export interface Doctor {
  id: string;
  full_name: string;
  display_name?: string;
  title?: string;
  department?: string;
  specialty?: string;
  hospital?: string;
  is_verified_doctor: boolean;
  professional_type?: string;
}

export interface DoctorVerification {
  id: string;
  user_id: string;
  license_number: string;
  specialty?: string;
  hospital?: string;
  years_of_experience?: number;
  education?: string;
  title?: string;
  department?: string;
  full_name?: string;
  email?: string;
  status: 'pending' | 'approved' | 'rejected';
  submitted_at: string;
  verified_by?: string;
  verified_at?: string;
  verification_notes?: string;
}

// Shared Medical Case Types
export interface SharedMedicalCase {
  id: string;
  original_case_id: string;
  consent_id: string;
  anonymous_patient_profile: AnonymousProfile;
  anonymized_symptoms?: string;
  anonymized_diagnosis?: string;
  anonymized_documents?: unknown[];
  visible_to_doctors: boolean;
  visible_for_research: boolean;
  view_count: number;
  doctor_views?: DoctorView[];
  exported_count: number;
  export_records?: unknown[];
  created_at: string;
  original_case?: MedicalCase;
  patient_chronic_diseases?: ChronicDisease[];
}

export interface DoctorView {
  doctor_id: string;
  viewed_at: string;
  ip?: string;
}

// Doctor Case Comment Types
export interface DoctorCaseComment {
  id: string;
  shared_case_id: string;
  doctor_id: string;
  comment_type: 'suggestion' | 'diagnosis_opinion' | 'treatment_advice' | 'general';
  content: string;
  doctor_specialty?: string;
  doctor_hospital?: string;
  is_public: boolean;
  status: 'active' | 'edited' | 'hidden';
  edited_at?: string;
  original_content?: string;
  created_at: string;
  doctor?: Doctor;
  patient_replies?: CaseCommentReply[];
}

export interface CaseCommentReply {
  id: string;
  doctor_comment_id: string;
  patient_id: string;
  shared_case_id: string;
  content: string;
  status: 'active' | 'hidden';
  created_at: string;
  updated_at: string;
}

export interface AIProvider {
  key: string;
  name: string;
  name_zh: string;
  default_url: string;
  default_model: string;
  requires_key: boolean;
}

// Admin Types
export interface SystemMetrics {
  timestamp: string;
  cpu_percent: number;
  memory_percent: number;
  disk_percent: number;
  container_status?: ContainerStatus;
  db_connections?: number;
  db_query_time_avg?: number;
  alert_level: 'info' | 'warning' | 'critical';
  alert_message?: string;
}

export interface ContainerStatus {
  [key: string]: {
    status: 'running' | 'exited' | 'paused';
    cpu: number;
    memory: number;
  };
}

export interface AdminAlert {
  level: 'info' | 'warning' | 'danger';
  title: string;
  description: string;
  timestamp: string;
}

// System metrics API response - supports both nested and direct formats
export interface SystemMetricsResponse {
  current?: SystemMetrics;
  cpu?: { percent: number };
  memory?: { percent: number };
  disk?: { percent: number };
  timestamp?: string;
  alert_level?: 'info' | 'warning' | 'critical';
  cpu_percent?: number;
  memory_percent?: number;
  disk_percent?: number;
}

export interface AdminOperationLog {
  id: string;
  admin_id: string;
  operation_type: string;
  operation: string;
  operation_details: unknown;
  details?: string;
  level?: 'info' | 'warning' | 'error';
  ip_address?: string;
  user_agent?: string;
  user_email?: string;
  timestamp: string;
  created_at?: string;
  admin?: User;
}

// API Response Types
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  message?: string;
  error?: ApiError;
  timestamp: string;
}

export interface ApiError {
  code: string;
  message: string;
  details?: unknown;
}

// Pagination Types
export interface PaginationParams {
  page?: number;
  page_size?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

// Legacy exports for backward compatibility
export interface UserCreate extends RegisterData {}
export interface UserLogin extends LoginCredentials {}
export interface Token {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}
export interface PatientCreate {
  full_name: string;
  date_of_birth?: string;
  gender?: string;
  phone?: string;
  address?: string;
  emergency_contact?: string;
  medical_record_number?: string;
}
export interface PatientUpdate extends PatientCreate {}
export interface FollowUp {
  id: string;
  medical_case_id: string;
  scheduled_date: string;
  actual_date?: string;
  follow_up_type: string;
  status: 'scheduled' | 'completed' | 'missed' | 'cancelled';
  notes?: string;
  symptoms_changes?: string;
  medication_adherence?: 'good' | 'moderate' | 'poor';
  next_follow_up_date?: string;
  created_at: string;
  updated_at: string;
}

// API Error Response
export interface ApiErrorResponse {
  detail?: string;
  message?: string;
  [key: string]: unknown;
}

// Backend request data for registration
export interface BackendRegisterData {
  email: string;
  password: string;
  full_name: string;
  role: string;
  phone?: string;
  emergency_contact_name?: string;
  emergency_contact_phone?: string;
  title?: string;
  department?: string;
  hospital?: string;
  license_number?: string;
  specialty?: string;
  address?: string;
}

// AI Model Configuration
export interface AIModelConfig {
  model_name?: string;
  api_base?: string;
  api_key?: string;
  temperature?: number;
  max_tokens?: number;
  timeout?: number;
  [key: string]: unknown;
}

export interface AIModelConfigs {
  diagnosis_llm: AIModelConfig;
  mineru: AIModelConfig;
  embedding: AIModelConfig;
  oss: AIModelConfig;
}
// Email Configuration Types
export * from "./email";
