export interface User {
  id: string;
  email: string;
  full_name: string;
  professional_title?: string;
  license_number?: string;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  last_login?: string;
}

export interface UserCreate {
  email: string;
  password: string;
  full_name: string;
  professional_title?: string;
  license_number?: string;
}

export interface UserLogin {
  email: string;
  password: string;
}

export interface Token {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface Patient {
  id: string;
  user_id: string;
  name: string;
  date_of_birth: string;
  gender?: 'male' | 'female' | 'other';
  phone?: string;
  address?: string;
  emergency_contact?: string;
  medical_record_number?: string;
  created_at: string;
  updated_at: string;
}

export interface PatientCreate {
  name: string;
  date_of_birth: string;
  gender?: 'male' | 'female' | 'other';
  phone?: string;
  address?: string;
  emergency_contact?: string;
  medical_record_number?: string;
}

export interface PatientUpdate {
  name?: string;
  gender?: 'male' | 'female' | 'other';
  phone?: string;
  address?: string;
  emergency_contact?: string;
}

export interface Disease {
  id: string;
  name: string;
  code?: string;
  description?: string;
  guidelines_json?: any;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface MedicalCase {
  id: string;
  patient_id: string;
  disease_id: string;
  title: string;
  description?: string;
  symptoms?: string;
  clinical_findings?: any;
  diagnosis?: string;
  severity?: 'mild' | 'moderate' | 'severe';
  status?: 'active' | 'resolved' | 'chronic';
  created_at: string;
  updated_at: string;
  patient?: Patient;
  disease?: Disease;
}

export interface MedicalDocument {
  id: string;
  medical_case_id: string;
  filename: string;
  original_filename: string;
  file_type: string;
  file_size: number;
  file_path: string;
  upload_status: 'uploaded' | 'processing' | 'processed' | 'failed';
  extracted_content?: any;
  extraction_metadata?: any;
  created_at: string;
  updated_at: string;
}

export interface AIFeedback {
  id: string;
  medical_case_id: string;
  feedback_type: 'diagnosis' | 'treatment' | 'follow_up';
  input_data: any;
  ai_response: any;
  confidence_score?: number;
  recommendations?: string;
  follow_up_plan?: any;
  is_reviewed: boolean;
  reviewed_by?: string;
  review_notes?: string;
  created_at: string;
  updated_at: string;
}

export interface FollowUp {
  id: string;
  medical_case_id: string;
  scheduled_date: string;
  actual_date?: string;
  follow_up_type: string;
  status?: 'scheduled' | 'completed' | 'missed' | 'cancelled';
  notes?: string;
  symptoms_changes?: string;
  medication_adherence?: 'good' | 'moderate' | 'poor';
  next_follow_up_date?: string;
  created_at: string;
  updated_at: string;
}

export interface ApiResponse<T = any> {
  data?: T;
  detail?: string;
  message?: string;
  count?: number;
}

export interface PaginatedResponse<T> extends ApiResponse<T[]> {
  count: number;
  next?: string;
  previous?: string;
}

export interface ApiError {
  detail: string;
  status?: number;
}