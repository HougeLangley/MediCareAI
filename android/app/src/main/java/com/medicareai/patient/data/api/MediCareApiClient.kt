package com.medicareai.patient.data.api

import com.medicareai.patient.data.model.*
import io.ktor.client.*
import io.ktor.client.call.*
import io.ktor.client.engine.okhttp.*
import io.ktor.client.plugins.*
import io.ktor.client.plugins.contentnegotiation.*
import io.ktor.client.plugins.logging.*
import io.ktor.client.request.*
import io.ktor.client.request.forms.*
import io.ktor.http.*
import io.ktor.serialization.kotlinx.json.*
import io.ktor.utils.io.*
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import kotlinx.serialization.json.Json
import okhttp3.logging.HttpLoggingInterceptor
import java.security.SecureRandom
import java.security.cert.X509Certificate
import java.util.concurrent.TimeUnit
import javax.net.ssl.*
import android.util.Log
import java.io.File

class MediCareApiClient {
    
    companion object {
        // Using IP address with HTTPS - certificate verification disabled for development
        const val BASE_URL = "https://8.137.177.147/api/v1/"
        const val TAG = "MediCareApiClient"
    }
    
    private var authToken: String? = null
    
    // Create all-trusting trust manager for development
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
    
    // Create unsafe hostname verifier
    private fun createUnsafeHostnameVerifier(): HostnameVerifier {
        return HostnameVerifier { hostname, session ->
            Log.d(TAG, "Verifying hostname: $hostname, peerHost: ${session?.peerHost}")
            true
        }
    }
    
    // Create SSL context that trusts all certificates
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
            requestTimeoutMillis = 120000  // 2 minutes for AI diagnosis
            connectTimeoutMillis = 30000
            socketTimeoutMillis = 120000
        }
        
        // Configure OkHttp engine for Android 16 compatibility
        engine {
            config {
                // Disable SSL verification for development
                val sslContext = createUnsafeSSLContext()
                sslSocketFactory(sslContext.socketFactory, createUnsafeTrustManager())
                hostnameVerifier(createUnsafeHostnameVerifier())
                
                // Connection settings
                connectTimeout(30, TimeUnit.SECONDS)
                readTimeout(30, TimeUnit.SECONDS)
                writeTimeout(30, TimeUnit.SECONDS)
                
                // Retry on connection failure
                retryOnConnectionFailure(true)
                
                // Follow redirects
                followRedirects(true)
                followSslRedirects(true)
                
                // Connection pool
                connectionPool(okhttp3.ConnectionPool(10, 5, TimeUnit.MINUTES))
                
                // Protocols - support TLS 1.2 and 1.3
                protocols(listOf(okhttp3.Protocol.HTTP_2, okhttp3.Protocol.HTTP_1_1))
                
                // Logging
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
        authToken = token
    }
    
    private suspend inline fun <reified T> makeRequest(
        method: HttpMethod,
        endpoint: String,
        body: Any? = null,
        queryParams: Map<String, String>? = null
    ): Result<T> {
        return try {
            Log.d(TAG, "Making $method request to: $BASE_URL$endpoint")
            Log.d(TAG, "Auth token is ${if (authToken != null) "SET" else "NULL"}")

            val response = client.request(BASE_URL + endpoint) {
                this.method = method
                authToken?.let {
                    Log.d(TAG, "Adding Authorization header with token")
                    header(HttpHeaders.Authorization, "Bearer $it")
                } ?: run {
                    Log.w(TAG, "No auth token available!")
                }
            Log.d(TAG, "Making $method request to: $BASE_URL$endpoint")
            
            val response = client.request(BASE_URL + endpoint) {
                this.method = method
                authToken?.let {
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
            
            if (response.status.isSuccess()) {
                Result.success(response.body())
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
                authToken?.let {
                    header(HttpHeaders.Authorization, "Bearer $it")
                }
                onUpload { bytesSentTotal, contentLength ->
                    if (contentLength > 0) {
                        val progress = bytesSentTotal.toFloat() / contentLength.toFloat()
                        onProgress?.invoke(progress)
                    }
                }
                timeout {
                    requestTimeoutMillis = 120000  // 2 minutes for large file uploads
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
    
    // Streaming AI Diagnosis API
    fun diagnoseStream(
        request: DiagnosisRequest
    ): Flow<StreamingDiagnosisResponse> = flow {
        try {
            Log.d(TAG, "Starting streaming diagnosis")
            
            val response = client.preparePost(BASE_URL + "ai/comprehensive-diagnosis-stream") {
                authToken?.let {
                    header(HttpHeaders.Authorization, "Bearer $it")
                }
                header(HttpHeaders.ContentType, ContentType.Application.Json)
                header(HttpHeaders.Accept, "text/event-stream")
                setBody(Json.encodeToString(DiagnosisRequest.serializer(), request))
                timeout {
                    requestTimeoutMillis = 300000  // 5 minutes timeout for streaming
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
                            val parsed = Json.decodeFromString(StreamingDiagnosisResponse.serializer(), data)
                            Log.d(TAG, "Parsed response - done: ${parsed.done}, chunk: ${parsed.chunk != null}, model: ${parsed.model_id ?: parsed.model_used}")
                            emit(parsed)
                            
                            if (parsed.done == true) {
                                Log.d(TAG, "Completion response received, breaking loop")
                                break
                            }
                        } catch (e: Exception) {
                            Log.w(TAG, "Failed to parse SSE data: $data", e)
                            // Emit as raw chunk if parsing fails
                            emit(StreamingDiagnosisResponse(chunk = data))
                        }
                    }
                }
                
                // Stream ended naturally - emit done signal
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
