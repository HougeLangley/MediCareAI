package com.medicareai.patient.data.api

import com.medicareai.patient.data.local.TokenManager
import com.medicareai.patient.data.model.*
import io.ktor.client.*
import io.ktor.client.call.*
import io.ktor.client.engine.okhttp.*
import io.ktor.client.statement.*
import io.ktor.client.plugins.*
import io.ktor.client.plugins.contentnegotiation.*
import io.ktor.client.plugins.logging.*
import io.ktor.client.request.*
import io.ktor.client.request.forms.*
import io.ktor.http.*
import io.ktor.serialization.kotlinx.json.*
import io.ktor.utils.io.*
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.flow.flow
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import kotlinx.serialization.json.Json
import okhttp3.logging.HttpLoggingInterceptor
import java.security.SecureRandom
import java.security.cert.X509Certificate
import java.util.concurrent.TimeUnit
import javax.inject.Inject
import javax.inject.Singleton
import javax.net.ssl.*
import android.util.Log
import java.io.File

@Singleton
class MediCareApiClient @Inject constructor(
    private val tokenManager: TokenManager
) {

    companion object {
        const val BASE_URL = "https://8.137.177.147/api/v1/"
        const val TAG = "MediCareApiClient"
    }

    private var authToken: String? = null
    private var isRefreshing = false
    private val refreshMutex = Mutex()

    private fun createUnsafeTrustManager(): X509TrustManager {
        return object : X509TrustManager {
            override fun checkClientTrusted(chain: Array<out X509Certificate>?, authType: String?) {
                Log.d(TAG, "checkClientTrusted: $authType")
            }
            override fun checkServerTrusted(chain: Array<out X509Certificate>?, authType: String?) {
                Log.d(TAG, "checkServerTrusted: $authType, certs: ${chain?.size}")
            }
            override fun getAcceptedIssuers(): Array<X509Certificate> = arrayOf()
        }
    }

    private fun createUnsafeHostnameVerifier(): HostnameVerifier {
        return HostnameVerifier { hostname, session ->
            Log.d(TAG, "Verifying hostname: $hostname, peerHost: ${session?.peerHost}")
            true
        }
    }

    private fun createUnsafeSSLContext(): SSLContext {
        val trustAllCerts = arrayOf<TrustManager>(createUnsafeTrustManager())
        return SSLContext.getInstance("SSL").apply {
            init(null, trustAllCerts, SecureRandom())
        }
    }

    val client = HttpClient(OkHttp) {
        install(ContentNegotiation) {
            json(Json {
                ignoreUnknownKeys = true
                isLenient = true
                encodeDefaults = true
            })
        }

        install(Logging) {
            level = LogLevel.ALL
            logger = object : Logger {
                override fun log(message: String) {
                    Log.d(TAG, message)
                }
            }
        }

        install(DefaultRequest) {
            header(HttpHeaders.ContentType, ContentType.Application.Json)
            header("X-Platform", "patient")
        }

        install(HttpTimeout) {
            requestTimeoutMillis = 120000
            connectTimeoutMillis = 30000
            socketTimeoutMillis = 120000
        }

        engine {
            config {
                val sslContext = createUnsafeSSLContext()
                sslSocketFactory(sslContext.socketFactory, createUnsafeTrustManager())
                hostnameVerifier(createUnsafeHostnameVerifier())

                connectTimeout(30, TimeUnit.SECONDS)
                readTimeout(30, TimeUnit.SECONDS)
                writeTimeout(30, TimeUnit.SECONDS)

                retryOnConnectionFailure(true)
                followRedirects(true)
                followSslRedirects(true)

                connectionPool(okhttp3.ConnectionPool(10, 5, TimeUnit.MINUTES))
                protocols(listOf(okhttp3.Protocol.HTTP_2, okhttp3.Protocol.HTTP_1_1))

                addInterceptor(HttpLoggingInterceptor().apply {
                    level = HttpLoggingInterceptor.Level.BODY
                })
            }
        }

        followRedirects = true
        expectSuccess = false
    }

    fun setAuthToken(token: String?) {
        Log.d(TAG, "Setting auth token: ${if (token != null) "token present" else "null"}")
        authToken = token
    }

    private suspend fun refreshAccessToken(): Boolean {
        refreshMutex.withLock {
            if (isRefreshing) {
                while (isRefreshing) {
                    kotlinx.coroutines.delay(100)
                }
                return authToken != null
            }

            isRefreshing = true
            try {
                val refreshToken = tokenManager.getRefreshToken()
                if (refreshToken == null) {
                    Log.e(TAG, "No refresh token available")
                    return false
                }

                Log.d(TAG, "Attempting to refresh access token")

                val response = client.request(BASE_URL + "auth/refresh") {
                    method = HttpMethod.Post
                    contentType(ContentType.Application.Json)
                    setBody(mapOf("refresh_token" to refreshToken))
                }

                if (response.status.isSuccess()) {
                    val tokenResponse: Token = response.body()
                    tokenManager.saveTokens(
                        tokenResponse.access_token,
                        tokenResponse.refresh_token,
                        tokenResponse.expires_in.toLong()
                    )
                    authToken = tokenResponse.access_token
                    Log.d(TAG, "Token refreshed successfully")
                    return true
                } else {
                    Log.e(TAG, "Token refresh failed: ${response.status}")
                    tokenManager.clearTokens()
                    authToken = null
                    return false
                }
            } catch (e: Exception) {
                Log.e(TAG, "Token refresh exception: ${e.message}", e)
                tokenManager.clearTokens()
                authToken = null
                return false
            } finally {
                isRefreshing = false
            }
        }
    }

    private suspend fun <T> makeRequestInternal(
        method: HttpMethod,
        endpoint: String,
        body: Any? = null,
        queryParams: Map<String, String>? = null,
        retryCount: Int = 0,
        parseResponse: suspend (HttpResponse) -> T
    ): Result<T> {
        return try {
            Log.d(TAG, "Making $method request to: $BASE_URL$endpoint")

            val currentToken = authToken ?: tokenManager.getAccessToken()

            val response = client.request(BASE_URL + endpoint) {
                this.method = method
                currentToken?.let {
                    header(HttpHeaders.Authorization, "Bearer $it")
                }
                body?.let {
                    contentType(ContentType.Application.Json)
                    setBody(it)
                }
                queryParams?.forEach { (key, value) ->
                    parameter(key, value)
                }
            }

            Log.d(TAG, "Response status: ${response.status}")

            if (response.status.value == 401 && retryCount < 1) {
                Log.d(TAG, "Received 401, attempting to refresh token")
                val refreshed = refreshAccessToken()
                if (refreshed) {
                    Log.d(TAG, "Token refreshed, retrying request")
                    return makeRequestInternal(method, endpoint, body, queryParams, retryCount + 1, parseResponse)
                } else {
                    Log.e(TAG, "Token refresh failed, returning auth error")
                    return Result.failure(
                        AuthException("Session expired. Please login again.")
                    )
                }
            }

            if (response.status.isSuccess()) {
                Result.success(parseResponse(response))
            } else {
                val errorBody = try {
                    response.body<ApiResponse<String>>()
                } catch (e: Exception) {
                    Log.e(TAG, "Error parsing error body", e)
                    null
                }
                Result.failure(
                    ApiException(
                        response.status.value,
                        errorBody?.detail ?: errorBody?.message ?: "Unknown error (HTTP ${response.status.value})"
                    )
                )
            }
        } catch (e: Exception) {
            Log.e(TAG, "Request failed: ${e.message}", e)
            Result.failure(e)
        }
    }

    private suspend inline fun <reified T> makeRequest(
        method: HttpMethod,
        endpoint: String,
        body: Any? = null,
        queryParams: Map<String, String>? = null
    ): Result<T> {
        return makeRequestInternal(method, endpoint, body, queryParams, 0) { response ->
            response.body()
        }
    }

    suspend fun loadSavedToken() {
        val token = tokenManager.getAccessToken()
        authToken = token
        Log.d(TAG, "Loaded saved token: ${if (token != null) "present" else "null"}")
    }

    suspend fun isTokenExpired(): Boolean {
        return tokenManager.isTokenExpired()
    }

    suspend fun shouldRefreshToken(): Boolean {
        return tokenManager.shouldRefreshToken()
    }

    // Auth APIs
    suspend fun login(request: LoginRequest): Result<LoginResponse> =
        makeRequest(HttpMethod.Post, "auth/login", request)

    suspend fun register(request: RegisterRequest): Result<RegisterResponse> =
        makeRequest(HttpMethod.Post, "auth/register", request)

    suspend fun logout(): Result<Unit> =
        makeRequest(HttpMethod.Post, "auth/logout")

    suspend fun getCurrentUser(): Result<User> =
        makeRequest(HttpMethod.Get, "auth/me")

    suspend fun updateCurrentUser(userUpdate: Map<String, String?>): Result<User> =
        makeRequest(HttpMethod.Put, "auth/me", userUpdate)

    suspend fun refreshToken(refreshToken: String): Result<Token> =
        makeRequest(HttpMethod.Post, "auth/refresh", mapOf("refresh_token" to refreshToken))

    suspend fun getVerificationStatus(): Result<VerificationStatus> =
        makeRequest(HttpMethod.Get, "auth/verification-status")

    suspend fun sendVerificationEmail(): Result<Unit> =
        makeRequest(HttpMethod.Post, "auth/send-verification-email")

    suspend fun verifyEmail(token: String): Result<Unit> =
        makeRequest(HttpMethod.Get, "auth/verify-email?token=$token")

    // Patient APIs
    suspend fun getMyPatientProfile(): Result<Patient> =
        makeRequest(HttpMethod.Get, "patients/me")

    suspend fun updateMyPatientProfile(update: PatientUpdateRequest): Result<Patient> =
        makeRequest(HttpMethod.Put, "patients/me", update)

    // Medical Case APIs
    suspend fun getMedicalCases(): Result<List<MedicalCase>> =
        makeRequest(HttpMethod.Get, "medical-cases")

    suspend fun getMedicalCase(caseId: String): Result<MedicalCase> =
        makeRequest(HttpMethod.Get, "medical-cases/$caseId")

    suspend fun createMedicalCase(request: CreateCaseRequest): Result<MedicalCase> =
        makeRequest(HttpMethod.Post, "medical-cases", request)

    suspend fun getDoctorComments(caseId: String): Result<List<DoctorComment>> =
        makeRequest(HttpMethod.Get, "medical-cases/$caseId/doctor-comments")

    suspend fun replyToDoctorComment(caseId: String, commentId: String, request: CreateReplyRequest): Result<Unit> =
        makeRequest(
            HttpMethod.Post,
            "medical-cases/$caseId/doctor-comments/$commentId/reply",
            request
        )

    // AI Diagnosis APIs
    suspend fun diagnose(request: DiagnosisRequest): Result<AIFeedback> =
        makeRequest(HttpMethod.Post, "ai/comprehensive-diagnosis", request)

    // Doctor APIs
    suspend fun getDoctors(): Result<List<Doctor>> =
        makeRequest(HttpMethod.Get, "sharing/doctors")

    // Document Upload APIs
    suspend fun uploadDocument(
        file: File,
        caseId: String,
        onProgress: ((Float) -> Unit)? = null
    ): Result<MedicalDocument> {
        return try {
            Log.d(TAG, "Uploading document: ${file.name} for case: $caseId")

            val currentToken = authToken ?: tokenManager.getAccessToken()

            val response = client.submitFormWithBinaryData(
                url = BASE_URL + "documents/upload",
                formData = formData {
                    append("file", file.readBytes(), Headers.build {
                        append(HttpHeaders.ContentDisposition, "filename=\"${file.name}\"")
                        append(HttpHeaders.ContentType, ContentType.Application.OctetStream.toString())
                    })
                    append("medical_case_id", caseId)
                }
            ) {
                currentToken?.let {
                    header(HttpHeaders.Authorization, "Bearer $it")
                }
                onUpload { bytesSentTotal, contentLength ->
                    if (contentLength > 0) {
                        val progress = bytesSentTotal.toFloat() / contentLength.toFloat()
                        onProgress?.invoke(progress)
                    }
                }
                timeout {
                    requestTimeoutMillis = 120000
                }
            }

            Log.d(TAG, "Upload response status: ${response.status}")

            if (response.status.isSuccess()) {
                Result.success(response.body())
            } else {
                Result.failure(ApiException(
                    response.status.value,
                    "Upload failed: ${response.status}"
                ))
            }
        } catch (e: Exception) {
            Log.e(TAG, "Document upload failed: ${e.message}", e)
            Result.failure(e)
        }
    }

    suspend fun extractDocument(documentId: String): Result<Unit> =
        makeRequest(HttpMethod.Post, "documents/$documentId/extract")

    suspend fun getDocumentContent(documentId: String): Result<MedicalDocument> =
        makeRequest(HttpMethod.Get, "documents/$documentId/content")

    suspend fun getChronicDiseases(): Result<ChronicDiseaseListResponse> =
        makeRequest(HttpMethod.Get, "chronic-diseases")

    suspend fun getMyChronicDiseases(): Result<PatientChronicConditionListResponse> =
        makeRequest(HttpMethod.Get, "chronic-diseases/patients/me/chronic-diseases")

    suspend fun addChronicDisease(request: AddChronicDiseaseRequest): Result<PatientChronicCondition> =
        makeRequest(HttpMethod.Post, "chronic-diseases/patients/me/chronic-diseases", request)

    suspend fun updateChronicDisease(conditionId: String, request: UpdateChronicDiseaseRequest): Result<PatientChronicCondition> =
        makeRequest(HttpMethod.Put, "chronic-diseases/patients/me/chronic-diseases/$conditionId", request)

    suspend fun deleteChronicDisease(conditionId: String): Result<Unit> =
        makeRequest(HttpMethod.Delete, "chronic-diseases/patients/me/chronic-diseases/$conditionId")

    // Streaming AI Diagnosis API
    fun diagnoseStream(
        request: DiagnosisRequest
    ): Flow<StreamingDiagnosisResponse> = flow {
        try {
            Log.d(TAG, "Starting streaming diagnosis")

            val currentToken = authToken ?: tokenManager.getAccessToken()

            val response = client.preparePost(BASE_URL + "ai/comprehensive-diagnosis-stream") {
                currentToken?.let {
                    header(HttpHeaders.Authorization, "Bearer $it")
                }
                header(HttpHeaders.ContentType, ContentType.Application.Json)
                header(HttpHeaders.Accept, "text/event-stream")
                setBody(Json.encodeToString(DiagnosisRequest.serializer(), request))
                timeout {
                    requestTimeoutMillis = 300000
                }
            }.execute()

            if (response.status.isSuccess()) {
                val channel: ByteReadChannel = response.body()

                while (!channel.isClosedForRead) {
                    val line = channel.readUTF8Line() ?: continue

                    if (line.startsWith("data: ")) {
                        val data = line.substring(6)
                        Log.d(TAG, "Received SSE data: $data")
                        try {
                            val jsonParser = kotlinx.serialization.json.Json {
                                ignoreUnknownKeys = true
                            }
                            val parsed = jsonParser.decodeFromString(StreamingDiagnosisResponse.serializer(), data)
                            Log.d(TAG, "Parsed response - done: ${parsed.done}, chunk: ${parsed.chunk != null}, model: ${parsed.model_id ?: parsed.model_used}")
                            emit(parsed)

                            if (parsed.done == true) {
                                Log.d(TAG, "Completion response received, breaking loop")
                                break
                            }
                        } catch (e: Exception) {
                            Log.w(TAG, "Failed to parse SSE data: $data", e)
                            emit(StreamingDiagnosisResponse(chunk = data))
                        }
                    }
                }

                emit(StreamingDiagnosisResponse(done = true))
            } else {
                emit(StreamingDiagnosisResponse(
                    error = "HTTP ${response.status.value}",
                    done = true
                ))
            }
        } catch (e: Exception) {
            Log.e(TAG, "Streaming diagnosis failed: ${e.message}", e)
            emit(StreamingDiagnosisResponse(
                error = e.message ?: "Unknown error",
                done = true
            ))
        }
    }
}

class ApiException(val code: Int, message: String) : Exception(message)
class AuthException(message: String) : Exception(message)
