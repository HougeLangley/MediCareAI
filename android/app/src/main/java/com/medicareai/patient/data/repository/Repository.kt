package com.medicareai.patient.data.repository

import com.medicareai.patient.data.api.MediCareApiClient
import com.medicareai.patient.data.local.TokenManager
import com.medicareai.patient.data.model.*
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.first
import java.io.File
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class AuthRepository @Inject constructor(
    private val apiClient: MediCareApiClient,
    private val tokenManager: TokenManager
) {
    suspend fun login(email: String, password: String): Result<LoginResponse> {
        return apiClient.login(LoginRequest(email, password))
            .onSuccess { response ->
                tokenManager.saveTokens(
                    response.tokens.access_token,
                    response.tokens.refresh_token,
                    response.tokens.expires_in.toLong()
                )
                apiClient.setAuthToken(response.tokens.access_token)
            }
    }

    suspend fun register(
        email: String,
        password: String,
        fullName: String,
        dateOfBirth: String? = null,
        gender: String? = null,
        phone: String? = null,
        address: String? = null,
        emergencyContactName: String? = null,
        emergencyContactPhone: String? = null
    ): Result<RegisterResponse> {
        return apiClient.register(
            RegisterRequest(
                email = email,
                password = password,
                full_name = fullName,
                date_of_birth = dateOfBirth,
                gender = gender,
                phone = phone,
                address = address,
                emergency_contact_name = emergencyContactName,
                emergency_contact_phone = emergencyContactPhone
            )
        )
    }

    suspend fun logout(): Result<Unit> {
        return apiClient.logout()
            .onSuccess {
                tokenManager.clearTokens()
                apiClient.setAuthToken(null)
            }
    }

    suspend fun getCurrentUser(): Result<User> {
        return apiClient.getCurrentUser()
    }

    suspend fun updateCurrentUser(updates: Map<String, String?>): Result<User> {
        return apiClient.updateCurrentUser(updates)
    }

    suspend fun refreshToken(refreshToken: String): Result<Token> {
        return apiClient.refreshToken(refreshToken)
    }

    suspend fun getVerificationStatus(): Result<VerificationStatus> {
        return apiClient.getVerificationStatus()
    }

    suspend fun sendVerificationEmail(): Result<Unit> {
        return apiClient.sendVerificationEmail()
    }

    fun setAuthToken(token: String?) {
        apiClient.setAuthToken(token)
    }

    suspend fun loadSavedToken() {
        apiClient.loadSavedToken()
    }

    suspend fun isTokenExpired(): Boolean {
        return apiClient.isTokenExpired()
    }

    suspend fun shouldRefreshToken(): Boolean {
        return apiClient.shouldRefreshToken()
    }
}

@Singleton
class PatientRepository @Inject constructor(
    private val apiClient: MediCareApiClient
) {
    suspend fun getMyProfile(): Result<Patient> {
        return apiClient.getMyPatientProfile()
    }

    suspend fun updateMyProfile(update: PatientUpdateRequest): Result<Patient> {
        return apiClient.updateMyPatientProfile(update)
    }
}

@Singleton
class MedicalCaseRepository @Inject constructor(
    private val apiClient: MediCareApiClient
) {
    suspend fun getCases(): Result<List<MedicalCase>> {
        return apiClient.getMedicalCases()
    }

    suspend fun getCase(caseId: String): Result<MedicalCase> {
        return apiClient.getMedicalCase(caseId)
    }

    suspend fun createCase(request: CreateCaseRequest): Result<MedicalCase> {
        return apiClient.createMedicalCase(request)
    }

    suspend fun getDoctorComments(caseId: String): Result<List<DoctorComment>> {
        return apiClient.getDoctorComments(caseId)
    }

    suspend fun replyToComment(caseId: String, commentId: String, content: String): Result<Unit> {
        return apiClient.replyToDoctorComment(caseId, commentId, CreateReplyRequest(content))
    }
}

@Singleton
class AIDiagnosisRepository @Inject constructor(
    private val apiClient: MediCareApiClient
) {
    suspend fun diagnose(request: DiagnosisRequest): Result<AIFeedback> {
        return apiClient.diagnose(request)
    }

    fun diagnoseStream(request: DiagnosisRequest): Flow<StreamingDiagnosisResponse> {
        return apiClient.diagnoseStream(request)
    }
}

@Singleton
class DoctorRepository @Inject constructor(
    private val apiClient: MediCareApiClient
) {
    suspend fun getDoctors(): Result<List<Doctor>> {
        return apiClient.getDoctors()
    }
}

@Singleton
class DocumentRepository @Inject constructor(
    private val apiClient: MediCareApiClient
) {
    suspend fun uploadDocument(
        file: File,
        caseId: String,
        onProgress: ((Float) -> Unit)? = null
    ): Result<MedicalDocument> {
        return apiClient.uploadDocument(file, caseId, onProgress)
    }

    suspend fun extractDocument(documentId: String): Result<Unit> {
        return apiClient.extractDocument(documentId)
    }

    suspend fun getDocumentContent(documentId: String): Result<MedicalDocument> {
        return apiClient.getDocumentContent(documentId)
    }
}

@Singleton
class ChronicDiseaseRepository @Inject constructor(
    private val apiClient: MediCareApiClient
) {
    suspend fun getChronicDiseases(): Result<ChronicDiseaseListResponse> {
        return apiClient.getChronicDiseases()
    }

    suspend fun getMyChronicDiseases(): Result<PatientChronicConditionListResponse> {
        return apiClient.getMyChronicDiseases()
    }

    suspend fun addChronicDisease(request: AddChronicDiseaseRequest): Result<PatientChronicCondition> {
        return apiClient.addChronicDisease(request)
    }

    suspend fun updateChronicDisease(conditionId: String, request: UpdateChronicDiseaseRequest): Result<PatientChronicCondition> {
        return apiClient.updateChronicDisease(conditionId, request)
    }

    suspend fun deleteChronicDisease(conditionId: String): Result<Unit> {
        return apiClient.deleteChronicDisease(conditionId)
    }
}
