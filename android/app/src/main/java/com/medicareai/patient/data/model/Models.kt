package com.medicareai.patient.data.model

import kotlinx.serialization.Serializable

@Serializable
data class User(
    val id: String,
    val email: String,
    val full_name: String,
    val role: String,
    val is_active: Boolean,
    val is_verified: Boolean,
    val date_of_birth: String? = null,
    val gender: String? = null,
    val phone: String? = null,
    val address: String? = null,
    val emergency_contact: String? = null,
    val emergency_contact_name: String? = null,  // 分离字段
    val emergency_contact_phone: String? = null  // 分离字段
)

@Serializable
data class Token(
    val access_token: String,
    val refresh_token: String,
    val token_type: String,
    val expires_in: Int
)

@Serializable
data class LoginRequest(
    val email: String,
    val password: String,
    val platform: String = "patient"
)

@Serializable
data class LoginResponse(
    val user: User,
    val tokens: Token,
    val platform: String,
    val available_platforms: List<String>
)

@Serializable
data class RegisterRequest(
    val email: String,
    val password: String,
    val full_name: String,
    val date_of_birth: String? = null,
    val gender: String? = null,
    val phone: String? = null,
    val address: String? = null,
    val emergency_contact_name: String? = null,
    val emergency_contact_phone: String? = null
)

@Serializable
data class RegisterResponse(
    val message: String,
    val user_id: String,
    val email: String
)

@Serializable
data class ApiResponse<T>(
    val data: T? = null,
    val message: String? = null,
    val detail: String? = null
)

@Serializable
data class Patient(
    val id: String,
    val user_id: String,
    val user_full_name: String,
    val name: String,
    val date_of_birth: String? = null,
    val gender: String? = null,
    val phone: String? = null,
    val address: String? = null,
    val emergency_contact: String? = null,  // 组合字段（向后兼容）
    val emergency_contact_name: String? = null,  // 分离字段：姓名（问题1修复）
    val emergency_contact_phone: String? = null,  // 分离字段：电话（问题1修复）
    val medical_record_number: String? = null,
    val notes: String? = null,
    val created_at: String? = null,
    val updated_at: String? = null
)

@Serializable
data class PatientUpdateRequest(
    val date_of_birth: String? = null,
    val gender: String? = null,
    val phone: String? = null,
    val address: String? = null,
    val emergency_contact: String? = null,  // 组合字段（向后兼容）
    val emergency_contact_name: String? = null,  // 分离字段：姓名（问题1修复）
    val emergency_contact_phone: String? = null  // 分离字段：电话（问题1修复）
)

@Serializable
data class MedicalCase(
    val id: String,
    val patient_id: String,
    val title: String,
    val description: String? = null,
    val symptoms: String,
    val diagnosis: String? = null,
    val severity: String? = null,
    val status: String? = null,
    val created_at: String
)

@Serializable
data class CreateCaseRequest(
    val title: String,
    val symptoms: String,
    val severity: String? = null,
    val description: String? = null
)

@Serializable
data class DiagnosisRequest(
    val symptoms: String,
    val symptom_severity: String? = null,
    val symptom_duration: String? = null,
    val onset_time: String? = null,  // 发病时间
    val document_ids: List<String> = emptyList(),
    val doctor_ids: List<String> = emptyList(),
    val share_with_doctors: Boolean = false,
    val language: String = "zh",
    val case_id: String? = null
)

@Serializable
data class AIFeedback(
    val id: String,
    val medical_case_id: String,
    val feedback_type: String,
    val ai_response: AIResponse,
    val created_at: String
)

@Serializable
data class AIResponse(
    val diagnosis: String,
    val model_id: String? = null,
    val tokens_used: Int? = null
)

@Serializable
data class DoctorComment(
    val id: String,
    val doctor_name: String,
    val doctor_specialty: String? = null,
    val doctor_hospital: String? = null,
    val comment_type: String,
    val content: String,
    val created_at: String,
    val patient_replies: List<PatientReply>? = null
)

@Serializable
data class PatientReply(
    val id: String,
    val content: String,
    val created_at: String
)

@Serializable
data class CreateReplyRequest(
    val content: String
)

@Serializable
data class VerificationStatus(
    val role: String,
    val is_verified: Boolean,
    val email_verified: Boolean
)

@Serializable
data class Doctor(
    val id: String,
    val display_name: String,
    val hospital: String? = null,
    val department: String? = null,
    val specialty: String? = null,
    val title: String? = null
)

@Serializable
data class MedicalDocument(
    val id: String,
    val filename: String,
    val file_type: String? = null,
    val file_size: Int? = null,
    val upload_status: String? = null,
    val extracted_content: String? = null,
    val cleaned_content: String? = null,
    val medical_case_id: String? = null,
    val created_at: String? = null
)

@Serializable
data class KnowledgeSource(
    val category: String? = null,
    val category_name: String? = null,
    val document_title: String? = null,
    val section_title: String? = null,
    val chunks: List<KnowledgeChunk>? = null
)

@Serializable
data class KnowledgeChunk(
    val chunk_text: String? = null,
    val text_preview: String? = null,
    val section_title: String? = null,
    val document_title: String? = null,
    val relevance_score: Double? = null
)

@Serializable
data class StreamingDiagnosisResponse(
    val chunk: String? = null,
    val done: Boolean? = null,
    val case_id: String? = null,
    val model_id: String? = null,
    val model_used: String? = null,
    val tokens_used: Int? = null,
    val knowledge_base_sources: List<KnowledgeSource>? = null,
    val knowledge_sources: List<KnowledgeSource>? = null,
    val message: String? = null,
    val error: String? = null
)

@Serializable
data class ChronicDisease(
    val id: String,
    val icd10_code: String,
    val icd10_name: String,
    val disease_type: String,
    val common_names: List<String>? = null,
    val category: String? = null,
    val description: String? = null,
    val medical_notes: String? = null,
    val is_active: Boolean = true
)

@Serializable
data class ChronicDiseaseListResponse(
    val items: List<ChronicDisease> = emptyList(),
    val total: Int = 0,
    val page: Int = 1,
    val page_size: Int = 50
)

@Serializable
data class PatientChronicCondition(
    val id: String,
    val patient_id: String,
    val disease_id: String,
    val disease: ChronicDisease? = null,
    val diagnosis_date: String? = null,
    val severity: String? = null,
    val notes: String? = null,
    val is_active: Boolean = true
)

@Serializable
data class PatientChronicConditionListResponse(
    val items: List<PatientChronicCondition> = emptyList(),
    val total: Int = 0
)

@Serializable
data class AddChronicDiseaseRequest(
    val disease_id: String,
    val diagnosis_date: String? = null,
    val severity: String? = null,
    val notes: String? = null
)

@Serializable
data class UpdateChronicDiseaseRequest(
    val diagnosis_date: String? = null,
    val severity: String? = null,
    val notes: String? = null,
    val is_active: Boolean? = null
)