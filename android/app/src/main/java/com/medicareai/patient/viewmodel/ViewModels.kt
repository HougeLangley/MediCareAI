package com.medicareai.patient.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.medicareai.patient.data.model.*
import com.medicareai.patient.data.repository.*
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch
import kotlinx.coroutines.async
import kotlinx.coroutines.awaitAll
import kotlinx.coroutines.delay
import java.io.File
import javax.inject.Inject

sealed class UiState<out T> {
    object Loading : UiState<Nothing>()
    data class Success<T>(val data: T) : UiState<T>()
    data class Error(val message: String) : UiState<Nothing>()
    object Idle : UiState<Nothing>()
}

@HiltViewModel
class AuthViewModel @Inject constructor(
    private val authRepository: AuthRepository
) : ViewModel() {
    
    private val _loginState = MutableStateFlow<UiState<LoginResponse>>(UiState.Idle)
    val loginState: StateFlow<UiState<LoginResponse>> = _loginState.asStateFlow()
    
    private val _registerState = MutableStateFlow<UiState<RegisterResponse>>(UiState.Idle)
    val registerState: StateFlow<UiState<RegisterResponse>> = _registerState.asStateFlow()
    
    private val _currentUser = MutableStateFlow<User?>(null)
    val currentUser: StateFlow<User?> = _currentUser.asStateFlow()
    
    private val _isLoggedIn = MutableStateFlow(false)
    val isLoggedIn: StateFlow<Boolean> = _isLoggedIn.asStateFlow()
    
    fun login(email: String, password: String) {
        viewModelScope.launch {
            _loginState.value = UiState.Loading
            authRepository.login(email, password)
                .onSuccess { response ->
                    authRepository.setAuthToken(response.tokens.access_token)
                    _currentUser.value = response.user
                    _isLoggedIn.value = true
                    _loginState.value = UiState.Success(response)
                }
                .onFailure { error ->
                    _loginState.value = UiState.Error(error.message ?: "登录失败")
                }
        }
    }
    
    fun register(
        email: String,
        password: String,
        fullName: String,
        dateOfBirth: String? = null,
        gender: String? = null,
        phone: String? = null,
        address: String? = null,
        emergencyContactName: String? = null,
        emergencyContactPhone: String? = null
    ) {
        viewModelScope.launch {
            _registerState.value = UiState.Loading
            authRepository.register(
                email, password, fullName, dateOfBirth, gender,
                phone, address, emergencyContactName, emergencyContactPhone
            )
                .onSuccess { response ->
                    _registerState.value = UiState.Success(response)
                }
                .onFailure { error ->
                    _registerState.value = UiState.Error(error.message ?: "注册失败")
                }
        }
    }
    
    fun logout() {
        viewModelScope.launch {
            authRepository.logout()
            authRepository.setAuthToken(null)
            _currentUser.value = null
            _isLoggedIn.value = false
            _loginState.value = UiState.Idle
        }
    }
    
    fun checkAuthStatus() {
        viewModelScope.launch {
            authRepository.loadSavedToken()
            authRepository.getCurrentUser()
                .onSuccess { user ->
                    _currentUser.value = user
                    _isLoggedIn.value = true
                }
                .onFailure {
                    _isLoggedIn.value = false
                }
        }
    }
    
    fun clearLoginState() {
        _loginState.value = UiState.Idle
    }
    
    fun clearRegisterState() {
        _registerState.value = UiState.Idle
    }
}

@HiltViewModel
class ProfileViewModel @Inject constructor(
    private val patientRepository: PatientRepository
) : ViewModel() {
    
    private val _profileState = MutableStateFlow<UiState<Patient>>(UiState.Idle)
    val profileState: StateFlow<UiState<Patient>> = _profileState.asStateFlow()
    
    private val _updateState = MutableStateFlow<UiState<Patient>>(UiState.Idle)
    val updateState: StateFlow<UiState<Patient>> = _updateState.asStateFlow()
    
    fun loadProfile() {
        viewModelScope.launch {
            _profileState.value = UiState.Loading
            patientRepository.getMyProfile()
                .onSuccess { patient ->
                    _profileState.value = UiState.Success(patient)
                }
                .onFailure { error ->
                    _profileState.value = UiState.Error(error.message ?: "加载失败")
                }
        }
    }
    
    fun updateProfile(update: PatientUpdateRequest) {
        viewModelScope.launch {
            _updateState.value = UiState.Loading
            patientRepository.updateMyProfile(update)
                .onSuccess { patient ->
                    _updateState.value = UiState.Success(patient)
                    _profileState.value = UiState.Success(patient)
                }
                .onFailure { error ->
                    _updateState.value = UiState.Error(error.message ?: "更新失败")
                }
        }
    }
    
    fun clearUpdateState() {
        _updateState.value = UiState.Idle
    }
}

@HiltViewModel
class MedicalRecordsViewModel @Inject constructor(
    private val caseRepository: MedicalCaseRepository
) : ViewModel() {
    
    private val _casesState = MutableStateFlow<UiState<List<MedicalCase>>>(UiState.Idle)
    val casesState: StateFlow<UiState<List<MedicalCase>>> = _casesState.asStateFlow()
    
    private val _caseDetailState = MutableStateFlow<UiState<MedicalCase>>(UiState.Idle)
    val caseDetailState: StateFlow<UiState<MedicalCase>> = _caseDetailState.asStateFlow()
    
    private val _commentsState = MutableStateFlow<UiState<List<DoctorComment>>>(UiState.Idle)
    val commentsState: StateFlow<UiState<List<DoctorComment>>> = _commentsState.asStateFlow()
    
    fun loadCases() {
        viewModelScope.launch {
            _casesState.value = UiState.Loading
            caseRepository.getCases()
                .onSuccess { cases ->
                    _casesState.value = UiState.Success(cases)
                }
                .onFailure { error ->
                    _casesState.value = UiState.Error(error.message ?: "加载失败")
                }
        }
    }
    
    fun loadCaseDetail(caseId: String) {
        viewModelScope.launch {
            _caseDetailState.value = UiState.Loading
            caseRepository.getCase(caseId)
                .onSuccess { case ->
                    _caseDetailState.value = UiState.Success(case)
                }
                .onFailure { error ->
                    _caseDetailState.value = UiState.Error(error.message ?: "加载失败")
                }
        }
    }
    
    fun loadComments(caseId: String) {
        viewModelScope.launch {
            _commentsState.value = UiState.Loading
            caseRepository.getDoctorComments(caseId)
                .onSuccess { comments ->
                    _commentsState.value = UiState.Success(comments)
                }
                .onFailure { error ->
                    _commentsState.value = UiState.Error(error.message ?: "加载失败")
                }
        }
    }
    
    fun replyToComment(caseId: String, commentId: String, content: String) {
        viewModelScope.launch {
            caseRepository.replyToComment(caseId, commentId, content)
                .onSuccess {
                    loadComments(caseId)
                }
        }
    }
}

// Streaming Diagnosis States
data class StreamingDiagnosisState(
    val isLoading: Boolean = false,
    val content: String = "",
    val status: String = "",
    val modelId: String? = null,
    val tokensUsed: Int? = null,
    val knowledgeSources: List<KnowledgeSource> = emptyList(),
    val error: String? = null,
    val isComplete: Boolean = false
)

@HiltViewModel
class SymptomSubmitViewModel @Inject constructor(
    private val caseRepository: MedicalCaseRepository,
    private val aiRepository: AIDiagnosisRepository,
    private val documentRepository: DocumentRepository,
    private val doctorRepository: DoctorRepository
) : ViewModel() {
    
    private val _submitState = MutableStateFlow<UiState<MedicalCase>>(UiState.Idle)
    val submitState: StateFlow<UiState<MedicalCase>> = _submitState.asStateFlow()
    
    private val _diagnosisState = MutableStateFlow<UiState<AIFeedback>>(UiState.Idle)
    val diagnosisState: StateFlow<UiState<AIFeedback>> = _diagnosisState.asStateFlow()
    
    // Streaming diagnosis state
    private val _streamingState = MutableStateFlow(StreamingDiagnosisState())
    val streamingState: StateFlow<StreamingDiagnosisState> = _streamingState.asStateFlow()
    
    // File upload state
    private val _uploadState = MutableStateFlow<UiState<List<MedicalDocument>>>(UiState.Idle)
    val uploadState: StateFlow<UiState<List<MedicalDocument>>> = _uploadState.asStateFlow()
    
    private val _uploadProgress = MutableStateFlow<Map<String, Float>>(emptyMap())
    val uploadProgress: StateFlow<Map<String, Float>> = _uploadProgress.asStateFlow()
    
    // Selected files for upload
    private val _selectedFiles = MutableStateFlow<List<File>>(emptyList())
    val selectedFiles: StateFlow<List<File>> = _selectedFiles.asStateFlow()
    
    // Doctors list
    private val _doctorsState = MutableStateFlow<UiState<List<Doctor>>>(UiState.Idle)
    val doctorsState: StateFlow<UiState<List<Doctor>>> = _doctorsState.asStateFlow()
    
    // Selected doctors for @ mention
    private val _selectedDoctors = MutableStateFlow<List<Doctor>>(emptyList())
    val selectedDoctors: StateFlow<List<Doctor>> = _selectedDoctors.asStateFlow()
    
    fun submitSymptoms(
        title: String,
        symptoms: String,
        severity: String? = null,
        description: String? = null,
        onsetTime: String? = null,
        duration: String? = null,
        documentIds: List<String> = emptyList(),
        doctorIds: List<String> = emptyList(),
        shareWithDoctors: Boolean = false
    ) {
        viewModelScope.launch {
            // Set loading state IMMEDIATELY for better UX
            _streamingState.value = StreamingDiagnosisState(
                isLoading = true,
                status = "正在准备..."
            )
            _submitState.value = UiState.Loading
            
            caseRepository.createCase(CreateCaseRequest(title, symptoms, severity, description))
                .onSuccess { case ->
                    _submitState.value = UiState.Success(case)
                    
                    // Upload any pending files first - SYNCHRONOUSLY
                    val files = _selectedFiles.value
                    val uploadedDocIds = mutableListOf<String>()
                    
                    if (files.isNotEmpty()) {
                        _uploadState.value = UiState.Loading
                        _streamingState.value = _streamingState.value.copy(
                            status = "正在上传 ${files.size} 个文件..."
                        )
                        
                        // Use async/await to wait for all uploads to complete
                        val uploadJobs = files.mapIndexed { index, file ->
                            async {
                                _streamingState.value = _streamingState.value.copy(
                                    status = "正在上传文件 ${index + 1}/${files.size}: ${file.name}"
                                )
                                
                                documentRepository.uploadDocument(file, case.id) { progress ->
                                    _uploadProgress.value = _uploadProgress.value + (file.name to progress)
                                }.onSuccess { doc ->
                                    uploadedDocIds.add(doc.id)
                                    // Trigger document extraction
                                    _streamingState.value = _streamingState.value.copy(
                                        status = "正在处理文档 (${index + 1}/${files.size}): MinerU提取中..."
                                    )
                                    documentRepository.extractDocument(doc.id)
                                    // Poll for extraction completion
                                    var isProcessed = false
                                    var attempts = 0
                                    val maxAttempts = 60  // 5 minutes (5 seconds * 60)
                                    
                                    while (!isProcessed && attempts < maxAttempts) {
                                        delay(5000)  // Wait 5 seconds between checks
                                        documentRepository.getDocumentContent(doc.id)
                                            .onSuccess { updatedDoc ->
                                                when (updatedDoc.upload_status) {
                                                    "processed" -> {
                                                        isProcessed = true
                                                        _streamingState.value = _streamingState.value.copy(
                                                            status = "文档 ${index + 1}/${files.size} 处理完成"
                                                        )
                                                    }
                                                    "failed" -> {
                                                        isProcessed = true
                                                        _uploadState.value = UiState.Error("文档处理失败: ${updatedDoc.filename}")
                                                    }
                                                    else -> {
                                                        // Still processing, update status
                                                        _streamingState.value = _streamingState.value.copy(
                                                            status = "正在处理文档 (${index + 1}/${files.size}): 第${attempts + 1}次检查..."
                                                        )
                                                    }
                                                }
                                            }
                                        attempts++
                                    }
                                    
                                    if (!isProcessed) {
                                        _uploadState.value = UiState.Error("文档处理超时: ${doc.filename}")
                                    }
                                }.onFailure { error ->
                                    _uploadState.value = UiState.Error("上传失败: ${error.message}")
                                }
                            }
                        }
                        
                        // Wait for all uploads AND extractions to complete
                        uploadJobs.awaitAll()
                        
                        _uploadState.value = UiState.Success(emptyList())
                    }
                    
                    // Start streaming AI diagnosis with uploaded documents and selected doctors
                    _streamingState.value = _streamingState.value.copy(
                        status = "正在启动AI诊断..."
                    )
                    
                    diagnoseStream(
                        caseId = case.id,
                        symptoms = symptoms,
                        severity = severity,
                        onsetTime = onsetTime,
                        duration = duration,
                        documentIds = uploadedDocIds + documentIds,
                        doctorIds = doctorIds + _selectedDoctors.value.map { it.id },
                        shareWithDoctors = shareWithDoctors
                    )
                }
                .onFailure { error ->
                    _submitState.value = UiState.Error(error.message ?: "提交失败")
                    _streamingState.value = StreamingDiagnosisState(
                        isLoading = false,
                        error = error.message ?: "提交失败",
                        status = "提交失败"
                    )
                }
        }
    }

    
    fun loadDoctors() {
        viewModelScope.launch {
            _doctorsState.value = UiState.Loading
            doctorRepository.getDoctors()
                .onSuccess { doctors ->
                    _doctorsState.value = UiState.Success(doctors)
                }
                .onFailure { error ->
                    _doctorsState.value = UiState.Error(error.message ?: "加载医生列表失败")
                }
        }
    }
    
    fun addSelectedFile(file: File) {
        _selectedFiles.value = _selectedFiles.value + file
    }
    
    fun removeSelectedFile(file: File) {
        _selectedFiles.value = _selectedFiles.value - file
    }
    
    fun selectDoctor(doctor: Doctor) {
        if (!_selectedDoctors.value.contains(doctor)) {
            _selectedDoctors.value = _selectedDoctors.value + doctor
        }
    }
    
    fun unselectDoctor(doctor: Doctor) {
        _selectedDoctors.value = _selectedDoctors.value - doctor
    }
    
    fun clearStates() {
        _submitState.value = UiState.Idle
        _diagnosisState.value = UiState.Idle
        _streamingState.value = StreamingDiagnosisState()
        _uploadState.value = UiState.Idle
        _uploadProgress.value = emptyMap()
        _selectedFiles.value = emptyList()
        _selectedDoctors.value = emptyList()
    }
    
    private fun diagnoseStream(
        caseId: String,
        symptoms: String,
        severity: String?,
        onsetTime: String?,
        duration: String?,
        documentIds: List<String>,
        doctorIds: List<String>,
        shareWithDoctors: Boolean
    ) {
        viewModelScope.launch {
            _streamingState.value = _streamingState.value.copy(
                isLoading = true,
                status = "AI诊断中..."
            )

            val request = DiagnosisRequest(
                case_id = caseId,
                symptoms = symptoms,
                symptom_severity = severity,
                onset_time = onsetTime,
                symptom_duration = duration,
                document_ids = documentIds,
                doctor_ids = doctorIds,
                share_with_doctors = shareWithDoctors
            )

            aiRepository.diagnoseStream(request)
                .collect { response ->
                    android.util.Log.d("DiagnosisVM", "Received response - done: ${response.done}, chunk: ${response.chunk != null}, model: ${response.model_id ?: response.model_used}, tokens: ${response.tokens_used}")
                    when {
                        response.error != null -> {
                            android.util.Log.e("DiagnosisVM", "Error: ${response.error}")
                            _streamingState.value = _streamingState.value.copy(
                                isLoading = false,
                                error = response.error,
                                status = "诊断失败"
                            )
                        }
                        response.done == true -> {
                            android.util.Log.d("DiagnosisVM", "Completion received - model: ${response.model_id ?: response.model_used}, tokens: ${response.tokens_used}, kb: ${response.knowledge_base_sources?.size ?: 0}")
                            val newModelId = response.model_id ?: response.model_used
                            val newTokens = response.tokens_used
                            val newKbSources = response.knowledge_sources ?: response.knowledge_base_sources

                            _streamingState.value = _streamingState.value.copy(
                                isLoading = false,
                                status = "诊断完成",
                                modelId = if (newModelId != null) newModelId else _streamingState.value.modelId,
                                tokensUsed = if (newTokens != null) newTokens else _streamingState.value.tokensUsed,
                                knowledgeSources = if (!newKbSources.isNullOrEmpty()) newKbSources else _streamingState.value.knowledgeSources,
                                isComplete = true
                            )
                        }
                        else -> {
                            val chunk = response.chunk ?: ""
                            android.util.Log.d("DiagnosisVM", "Chunk received: ${chunk.take(50)}...")

                            if (chunk.trimStart().startsWith("{\"done\"") && chunk.contains("case_id")) {
                                try {
                                    val jsonParser = kotlinx.serialization.json.Json {
                                        ignoreUnknownKeys = true
                                    }
                                    val completionData = jsonParser.decodeFromString(
                                        com.medicareai.patient.data.model.StreamingDiagnosisResponse.serializer(),
                                        chunk
                                    )
                                    android.util.Log.d("DiagnosisVM", "Parsed completion from chunk - model: ${completionData.model_id ?: completionData.model_used}, tokens: ${completionData.tokens_used}")

                                    _streamingState.value = _streamingState.value.copy(
                                        modelId = completionData.model_id ?: completionData.model_used,
                                        tokensUsed = completionData.tokens_used,
                                        knowledgeSources = completionData.knowledge_sources
                                            ?: completionData.knowledge_base_sources
                                            ?: emptyList(),
                                        isComplete = true
                                    )
                                } catch (e: Exception) {
                                    android.util.Log.e("DiagnosisVM", "Failed to parse completion JSON from chunk", e)
                                }
                            } else {
                                val currentContent = _streamingState.value.content
                                _streamingState.value = _streamingState.value.copy(
                                    content = currentContent + chunk,
                                    status = response.message ?: "诊断中..."
                                )
                            }
                        }
                    }
                }
        }
    }
}

@HiltViewModel
class ChronicDiseaseViewModel @Inject constructor(
    private val chronicDiseaseRepository: ChronicDiseaseRepository
) : ViewModel() {

    private val _availableDiseases = MutableStateFlow<UiState<List<ChronicDisease>>>(UiState.Idle)
    val availableDiseases: StateFlow<UiState<List<ChronicDisease>>> = _availableDiseases.asStateFlow()

    private val _myDiseases = MutableStateFlow<UiState<List<PatientChronicCondition>>>(UiState.Idle)
    val myDiseases: StateFlow<UiState<List<PatientChronicCondition>>> = _myDiseases.asStateFlow()

    private val _addDiseaseState = MutableStateFlow<UiState<PatientChronicCondition>>(UiState.Idle)
    val addDiseaseState: StateFlow<UiState<PatientChronicCondition>> = _addDiseaseState.asStateFlow()

    private val _deleteDiseaseState = MutableStateFlow<UiState<Unit>>(UiState.Idle)
    val deleteDiseaseState: StateFlow<UiState<Unit>> = _deleteDiseaseState.asStateFlow()

    fun loadAvailableDiseases() {
        viewModelScope.launch {
            _availableDiseases.value = UiState.Loading
            chronicDiseaseRepository.getChronicDiseases()
                .onSuccess { response ->
                    _availableDiseases.value = UiState.Success(response.items)
                }
                .onFailure { error ->
                    _availableDiseases.value = UiState.Error(error.message ?: "加载疾病列表失败")
                }
        }
    }

    fun loadMyDiseases() {
        viewModelScope.launch {
            _myDiseases.value = UiState.Loading
            chronicDiseaseRepository.getMyChronicDiseases()
                .onSuccess { response ->
                    _myDiseases.value = UiState.Success(response.items)
                }
                .onFailure { error ->
                    _myDiseases.value = UiState.Error(error.message ?: "加载我的疾病失败")
                }
        }
    }

    fun addChronicDisease(diseaseId: String, diagnosisDate: String?, severity: String?, notes: String?) {
        viewModelScope.launch {
            _addDiseaseState.value = UiState.Loading
            val request = AddChronicDiseaseRequest(
                disease_id = diseaseId,
                diagnosis_date = diagnosisDate,
                severity = severity,
                notes = notes
            )
            chronicDiseaseRepository.addChronicDisease(request)
                .onSuccess { condition ->
                    _addDiseaseState.value = UiState.Success(condition)
                    loadMyDiseases()
                }
                .onFailure { error ->
                    _addDiseaseState.value = UiState.Error(error.message ?: "添加疾病失败")
                }
        }
    }

    fun deleteChronicDisease(conditionId: String) {
        viewModelScope.launch {
            _deleteDiseaseState.value = UiState.Loading
            chronicDiseaseRepository.deleteChronicDisease(conditionId)
                .onSuccess {
                    _deleteDiseaseState.value = UiState.Success(Unit)
                    loadMyDiseases()
                }
                .onFailure { error ->
                    _deleteDiseaseState.value = UiState.Error(error.message ?: "删除疾病失败")
                }
        }
    }

    fun clearAddState() {
        _addDiseaseState.value = UiState.Idle
    }

    fun clearDeleteState() {
        _deleteDiseaseState.value = UiState.Idle
    }
}