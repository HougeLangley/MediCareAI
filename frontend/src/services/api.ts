import axios, { AxiosInstance, AxiosRequestConfig, AxiosError } from 'axios';
import { CONFIG } from '../lib/config';
import { useAuthStore } from '../store/authStore';
import type {
  ApiResponse,
  ApiErrorResponse,
  BackendRegisterData,
  AIModelConfigs,
  AIModelConfig,
  User,
  Token,
  LoginCredentials,
  RegisterData,
  MedicalCase,
  MedicalDocument,
  AIFeedback,
  Patient,
  PatientChronicCondition,
  PatientChronicConditionListResponse,
  Doctor,
  DoctorVerification,
  DoctorCaseComment,
  CaseCommentReply,
  SharedMedicalCase,
  ChronicDisease,
  ChronicDiseaseListResponse,
  DiagnosisRequest,
  ExtractedContent,
  SystemMetrics,
  AdminOperationLog,
  PaginatedResponse,
  AIProvider,
  KnowledgeSource,
} from '../types';

function unwrapApiResponse<T>(payload: ApiResponse<T> | T): T {
  if (
    payload &&
    typeof payload === 'object' &&
    'data' in payload &&
    payload.data !== undefined
  ) {
    return payload.data as T;
  }

  return payload as T;
}

function isTokenResponse(payload: unknown): payload is Token {
  return (
    !!payload &&
    typeof payload === 'object' &&
    'access_token' in payload &&
    'refresh_token' in payload
  );
}

const apiClient: AxiosInstance = axios.create({
  baseURL: `${CONFIG.API_BASE}${CONFIG.API_VERSION}`,
  timeout: CONFIG.REQUEST_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem(CONFIG.TOKEN_KEY);
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    const port = window.location.port || '80';
    if (port === '8080') {
      config.headers['X-Platform'] = 'admin';
    } else if (port === '8081') {
      config.headers['X-Platform'] = 'doctor';
    } else {
      config.headers['X-Platform'] = 'patient';
    }
    return config;
  },
  (error) => Promise.reject(error)
);

apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError<ApiResponse<unknown>>) => {
    const originalRequest = error.config as AxiosRequestConfig & { _retry?: boolean };

    // Skip redirect for login requests - login failures should stay on current page
    // 跳过登录请求的重定向 - 登录失败应该保留在当前页面
    const isLoginRequest = originalRequest.url?.includes('/auth/login');
    if (isLoginRequest && error.response?.status === 401) {
      // Return the error without redirect for login failures
      // 对于登录失败，直接返回错误而不重定向
      const responseData = error.response?.data as unknown as ApiErrorResponse;
      const errorMessage = responseData?.detail || responseData?.message || '登录失败 / Login failed';
      return Promise.reject(new Error(errorMessage));
    }

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem(CONFIG.REFRESH_TOKEN_KEY);
        if (!refreshToken) {
          throw new Error('No refresh token');
        }

        const response = await axios.post<ApiResponse<Token> | Token>(
          `${CONFIG.API_BASE}${CONFIG.API_VERSION}/auth/refresh`,
          {
            refresh_token: refreshToken,
          }
        );

        const tokens = unwrapApiResponse(response.data);
        if (!isTokenResponse(tokens)) {
          throw new Error('Invalid refresh token response');
        }

        const { access_token, refresh_token } = tokens;
        if (!access_token || !refresh_token) {
          throw new Error('Missing tokens in response');
        }
        
        localStorage.setItem(CONFIG.TOKEN_KEY, access_token);
        localStorage.setItem(CONFIG.REFRESH_TOKEN_KEY, refresh_token);


        if (originalRequest.headers) {
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
        }
        return apiClient(originalRequest);
      } catch {
        useAuthStore.getState().logout();
        
        // Determine redirect URL based on current platform
        // 根据当前平台决定重定向URL
        const port = window.location.port || '80';
        const currentPath = window.location.pathname;
        
        // Don't redirect if already on a login page
        // 如果已经在登录页面，则不重定向
        if (currentPath.includes('login')) {
          return Promise.reject(error);
        }
        
        // Redirect to appropriate login page based on port/platform
        // 根据端口/平台重定向到相应的登录页面
        if (port === '8080' || currentPath.startsWith('/admin')) {
          window.location.href = '/admin-login';
        } else if (port === '8081' || currentPath.startsWith('/doctor')) {
          window.location.href = '/doctor-login';
        } else {
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    }

    const responseData = error.response?.data as unknown as ApiErrorResponse;
    const errorMessage = responseData?.detail || responseData?.message || error.message;
    console.error('API Error:', errorMessage);
    return Promise.reject(new Error(errorMessage));
  }
);

export { apiClient };

export const api = {
  get: async <T>(url: string, config?: AxiosRequestConfig): Promise<T> => {
    const response = await apiClient.get<ApiResponse<T>>(url, config);
    return unwrapApiResponse(response.data);
  },

  post: async <T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T> => {
    const response = await apiClient.post<ApiResponse<T>>(url, data, config);
    return unwrapApiResponse(response.data);
  },

  put: async <T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T> => {
    const response = await apiClient.put<ApiResponse<T>>(url, data, config);
    return unwrapApiResponse(response.data);
  },

  patch: async <T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T> => {
    const response = await apiClient.patch<ApiResponse<T>>(url, data, config);
    return unwrapApiResponse(response.data);
  },

  delete: async <T>(url: string, config?: AxiosRequestConfig): Promise<T> => {
    const response = await apiClient.delete<ApiResponse<T>>(url, config);
    return unwrapApiResponse(response.data);
  },

  upload: async <T>(url: string, formData: FormData, onProgress?: (progress: number) => void): Promise<T> => {
    const response = await apiClient.post<ApiResponse<T>>(url, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress(progress);
        }
      },
    });
    return unwrapApiResponse(response.data);
  },
};

export const authApi = {
  login: (credentials: LoginCredentials) =>
    api.post<{ user: User; tokens: Token }>('/auth/login', credentials),

  register: (data: RegisterData) => {
    const { role, title, department, hospital, license_number, specialty, address, terms, emergency_contact, ...baseData } = data;
    
    const backendRequestData: BackendRegisterData = {
      ...baseData as BackendRegisterData,
      address,  // 添加地址字段
    };
    
    if (emergency_contact) {
      const match = emergency_contact.match(/^(.+?)\s*\((.+?)\)$/);
      if (match) {
        backendRequestData.emergency_contact_name = match[1].trim();
        backendRequestData.emergency_contact_phone = match[2].trim();
      }
    }
    
    return api.post<{ user: User; tokens: Token }>('/auth/register', backendRequestData);
  },

  logout: () => api.post('/auth/logout'),

  me: () => api.get<User>('/auth/me'),

  refresh: (refreshToken: string) =>
    api.post<Token>('/auth/refresh', { refresh_token: refreshToken }),

  registerDoctor: (data: {
    email: string;
    password: string;
    full_name: string;
    title: string;
    department: string;
    professional_type: string;
    specialty: string;
    hospital: string;
    license_number: string;
    phone?: string;
  }, files: File[]) => {
    const formData = new FormData();
    
    formData.append('email', data.email);
    formData.append('password', data.password);
    formData.append('full_name', data.full_name);
    formData.append('title', data.title);
    formData.append('department', data.department);
    formData.append('professional_type', data.professional_type);
    formData.append('specialty', data.specialty);
    formData.append('hospital', data.hospital);
    formData.append('license_number', data.license_number);
    if (data.phone) {
      formData.append('phone', data.phone);
    }
    
    files.forEach((file) => {
      formData.append('files', file);
    });
    
    return apiClient.post('/auth/register/doctor', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
  
  sendVerificationEmail: () => api.post('/auth/send-verification-email'),
  
  verifyEmail: (token: string) => api.get(`/auth/verify-email?token=${token}`),
};


export const casesApi = {
  getCases: () => api.get<MedicalCase[]>('/medical-cases'),
  getCase: (id: string) => api.get<MedicalCase>(`/medical-cases/${id}`),
  createCase: (data: Partial<MedicalCase>) => api.post<MedicalCase>('/medical-cases', data),
  updateCase: (id: string, data: Partial<MedicalCase>) => api.put<MedicalCase>(`/medical-cases/${id}`, data),
  deleteCase: (id: string) => api.delete<void>(`/medical-cases/${id}`),
  getDoctorComments: (caseId: string) => api.get<DoctorCaseComment[]>(`/medical-cases/${caseId}/doctor-comments`),
  replyToDoctorComment: (caseId: string, commentId: string, content: string) => 
    api.post(`/medical-cases/${caseId}/doctor-comments/${commentId}/reply`, { content }),
};

export const documentsApi = {
  upload: (file: File, caseId: string, onProgress?: (progress: number) => void) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('medical_case_id', caseId);
    return api.upload<MedicalDocument>('/documents/upload', formData, onProgress);
  },
  getDocument: (id: string) => api.get<MedicalDocument>(`/documents/${id}`),
  extract: (id: string) => api.post<ExtractedContent>(`/documents/${id}/extract`),
  getDocumentContent: (id: string) => api.get<{
    document_id: string;
    filename: string;
    upload_status: string;
    extracted_content?: string;
    cleaned_content?: string;
    error?: string;
    message?: string;
  }>(`/documents/${id}/content`),
};

export const aiApi = {
  diagnose: (data: DiagnosisRequest) => api.post<AIFeedback>('/ai/comprehensive-diagnosis', data),
  diagnoseStream: (
    data: DiagnosisRequest,
    onChunk: (chunk: string) => void,
    onComplete: (
      fullText: string,
      caseId?: string,
      modelInfo?: { model_id?: string; tokens_used?: number },
      knowledgeSources?: KnowledgeSource[]
    ) => void,
    onError: (error: string) => void
  ) => {
    const token = localStorage.getItem(CONFIG.TOKEN_KEY);
    const url = `${CONFIG.API_BASE}${CONFIG.API_VERSION}/ai/comprehensive-diagnosis-stream`;

    return new Promise<void>((resolve, reject) => {
      fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(data),
      })
        .then(response => {
          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
          }
          return response.body;
        })
        .then(body => {
          if (!body) {
            throw new Error('No response body');
          }

          const reader = body.getReader();
          const decoder = new TextDecoder();
          let fullText = '';
          let buffer = '';

          const processStream = async () => {
            try {
              while (true) {
                const { done, value } = await reader.read();

                if (done) {
                  onComplete(fullText);
                  resolve();
                  return;
                }

                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split('\n');
                buffer = lines.pop() || '';

                for (const line of lines) {
                  if (line.startsWith('data: ')) {
                    const data = line.slice(6);
                    try {
                      const parsed = JSON.parse(data);
                      if (parsed.done === true) {
                        const modelInfo = {
                          model_id: parsed.model_used || parsed.model_id,
                          tokens_used: parsed.tokens_used,
                        };
                        const knowledgeSources = parsed.knowledge_base_sources || parsed.knowledge_sources || [];
                        onComplete(fullText, parsed.case_id, modelInfo, knowledgeSources);
                        resolve();
                        return;
                      }
                      if (parsed.chunk) {
                        fullText += parsed.chunk;
                        onChunk(parsed.chunk);
                      }
                    } catch {
                      fullText += data;
                      onChunk(data);
                    }
                  }
                }
              }
            } catch (error) {
              onError(error instanceof Error ? error.message : 'Stream error');
              reject(error);
            }
          };

          processStream();
        })
        .catch(error => {
          onError(error instanceof Error ? error.message : 'Request failed');
          reject(error);
        });
    });
  },
  analyze: (data: { symptoms: string; language?: 'zh' | 'en' }) => api.post<AIFeedback>('/ai/analyze', data),
  getDiagnosis: (caseId: string) => api.get<AIFeedback[]>(`/ai/diagnosis/${caseId}`),
};

export const patientsApi = {
  getPatients: () => api.get<Patient[]>('/patients'),
  getMe: () => api.get<Patient>('/patients/me'),
  updateMe: (data: Partial<Patient>) => api.put<Patient>('/patients/me', data),
  create: (data: Partial<Patient>) => api.post<Patient>('/patients', data),
  getChronicDiseases: () => api.get<PatientChronicConditionListResponse>('/patients/me/chronic-diseases'),
  addChronicDisease: (data: { disease_id: string; diagnosis_date?: string; severity?: string; notes?: string }) =>
    api.post<PatientChronicCondition>('/patients/me/chronic-diseases', data),
  updateChronicDisease: (id: string, data: Partial<PatientChronicCondition>) =>
    api.put<PatientChronicCondition>(`/patients/me/chronic-diseases/${id}`, data),
  deleteChronicDisease: (id: string) => api.delete<void>(`/patients/me/chronic-diseases/${id}`),
};

export const doctorsApi = {
  getDoctors: () => api.get<Doctor[]>('/sharing/doctors'),
  getDoctor: (id: string) => api.get<Doctor>(`/doctor/${id}`),
  getMentions: (params?: { filter?: string }) => api.get<SharedMedicalCase[]>('/doctor/mentions', { params }),
  getAccessibleCases: () => api.get<SharedMedicalCase[]>('/doctor/cases?type=all'),
  getCases: (type?: string, limit?: number) => api.get<SharedMedicalCase[]>(`/doctor/cases${type ? `?type=${type}${limit ? `&limit=${limit}` : ''}` : ''}`),
  getDashboardStats: () => api.get<{
    mentioned_cases: number;
    public_cases: number;
    today_cases: number;
    exported_count: number;
    growth: number;
  }>('/doctor/dashboard'),
  addComment: (data: { shared_case_id: string; content: string; comment_type?: string }) =>
    api.post<DoctorCaseComment>('/doctor/comments', data),
  replyToComment: (data: { comment_id: string; content: string }) =>
    api.post<CaseCommentReply>('/doctor/replies', data),
  getProfile: () => api.get<Doctor>('/doctor/profile'),
  updateProfile: (data: Partial<Doctor>) => api.put<Doctor>('/doctor/profile', data),
  uploadLicenseDocument: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return apiClient.post('/doctor/upload-license-document', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
  uploadLicenseDocuments: (files: File[]) => {
    const formData = new FormData();
    files.forEach((file, index) => {
      formData.append(`file_${index}`, file);
    });
    return apiClient.post('/doctor/upload-license-documents', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
  getLicenseDocument: () => api.get<{ has_document: boolean; filename?: string; uploaded_at?: string; file_exists?: boolean; message: string }>('/doctor/license-document'),
  exportCases: (data: { case_ids: string[]; format: 'json' | 'csv'; include_documents?: boolean }) =>
    apiClient.post('/doctor/cases/export', data, {
      responseType: 'blob',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem(CONFIG.TOKEN_KEY)}`,
      },
    }),
};

export const adminApi = {
  getDashboardSummary: () => api.get<{
    user_statistics?: {
      total_users: number;
      patients: number;
      doctors: number;
      pending_doctor_verifications: number;
    };
    total_users?: number;
    total_cases?: number;
    total_doctors?: number;
    pending_verifications?: number;
    ai_statistics_24h?: {
      total_requests: number;
      success_rate: number;
      average_latency_ms: number;
      tokens_used: number;
    };
  }>('/admin/dashboard/summary'),
  getSystemMetrics: () => api.get<SystemMetrics>('/admin/system/metrics'),
  getPendingDoctors: () => api.get<DoctorVerification[]>('/admin/doctors/pending'),
  getDoctorVerifications: (status?: string) => api.get<{ verifications: DoctorVerification[] }>('/admin/doctors/verifications', 
    status ? { params: { status } } : {}),
  approveDoctor: (id: string) => api.post<void>(`/admin/doctors/verifications/${id}/approve`),
  rejectDoctor: (id: string, reason?: string) => api.post<void>(`/admin/doctors/verifications/${id}/reject`, { reason }),
  revokeDoctor: (id: string, reason?: string) => api.post<void>(`/admin/doctors/verifications/${id}/revoke`, { reason }),
  reapproveDoctor: (id: string, notes?: string) => api.post<void>(`/admin/doctors/verifications/${id}/reapprove`, { notes }),
  getDoctorVerificationDetail: (id: string) => api.get<{
    verification_id: string;
    doctor_name: string;
    doctor_email: string;
    license_number: string;
    hospital: string;
    specialty: string;
    years_of_experience: number;
    education: string;
    status: string;
    submitted_at: string;
    verified_at?: string;
    verified_by?: string;
    verification_notes?: string;
    documents: Array<{
      type: string;
      filename: string;
      upload_date?: string;
      status: string;
    }>;
    license_document?: {
      has_document: boolean;
      total_count: number;
      documents: Array<{
        index: number;
        filename: string;
        upload_date?: string;
        file_exists: boolean;
        file_path: string;
      }>;
      filename?: string;
      upload_date?: string;
      file_exists: boolean;
      file_path?: string;
    };
  }>(`/admin/doctors/verifications/${id}`),
  getOperationLogs: (params?: { page?: number; page_size?: number; type?: string; date?: string }) =>
    api.get<PaginatedResponse<AdminOperationLog>>('/admin/operations/logs', { params }),
  // Knowledge Base APIs
  uploadKnowledgeDocument: (file: File, onProgress?: (progress: number) => void) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.upload<{ doc_id: string; filename: string }>('/admin/knowledge-base/upload', formData, onProgress);
  },
  getKnowledgeDocuments: () => api.get<{ documents: Array<{
    doc_id: string;
    filename: string;
    file_size: number;
    uploaded_at: string;
    status: 'completed' | 'processing' | 'failed';
    chunk_count: number;
    preview?: string;
  }> }>('/admin/knowledge-base/documents'),
  deleteKnowledgeDocument: (docId: string) => api.delete<void>(`/admin/knowledge-base/documents/${docId}`),
  // RAG Enhancement APIs
  searchKnowledgeBase: (params: {
    query: string;
    disease_category?: string;
    source_type?: string;
    document_title?: string;
    top_k?: number;
    enable_hybrid?: boolean;
    vector_weight?: number;
    keyword_weight?: number;
    use_hyde?: boolean;
    min_similarity?: number;
  }) => api.post<Array<{
    id: string;
    text: string;
    section_title: string;
    document_title: string;
    disease_category: string;
    source_type: string;
    similarity_score: number;
    fused_score?: number;
    vector_score?: number;
    keyword_score?: number;
    retrieval_count: number;
  }>>('/vector-embedding/knowledge-base/search', params),
  enhanceSearchQuery: (params: {
    query: string;
    use_hyde?: boolean;
    use_rewrite?: boolean;
    context?: string;
  }) => api.post<{
    original_query: string;
    rewritten_query: string;
    final_search_query: string;
    expanded_keywords: string[];
    hyde_document: string | null;
    confidence: number;
  }>('/vector-embedding/knowledge-base/enhance-query', params),
  compressKbResults: (params: {
    query: string;
    chunk_ids: string[];
    max_tokens?: number;
  }) => api.post<{
    compressed_text: string;
    key_points: string[];
    sources: Array<{
      document: string;
      section: string;
      chunk_id: string;
    }>;
    relevance_score: number;
    original_chunks_count: number;
    message: string;
  }>('/vector-embedding/knowledge-base/compress'),
  // AI Model APIs
  getAIModels: () => api.get<AIModelConfigs>('/admin/ai-models'),
  testAIModel: (modelType: string, config?: AIModelConfig) => api.post<unknown>(`/admin/ai-models/${modelType}/test`, config || {}),
  saveAIModelConfig: (modelType: string, config: AIModelConfig) => api.post<unknown>(`/admin/ai-models/${modelType}/config`, config),
  getEmbeddingProviders: () => api.get<AIProvider[]>('/admin/embedding/providers'),
  getRerankProviders: () => api.get<AIProvider[]>('/admin/ai-models/rerank/providers'),
  validateEmbeddingUrl: (url: string) => api.post<{
    warnings: string[];
    suggestions: string[];
    formatted_url: string;
  }>('/admin/embedding/validate-url', { url }),
  changePassword: (current_password: string, new_password: string) =>
    api.post('/auth/change-password', { current_password, new_password }),

  getEmailProviderPresets: () => api.get<{
    providers: EmailProviderPreset[];
    categories: Record<string, ProviderCategory>;
  }>("/admin/email-providers/presets"),

  getEmailProviderPreset: (providerId: string) => api.get<EmailProviderPreset>(`/admin/email-providers/presets/${providerId}`),

  // Email Config APIs
  getEmailConfigs: () => api.get<{ configs: EmailConfig[]; total: number }>("/admin/email-config/configs"),

  createEmailConfig: (data: EmailConfigCreate) => api.post<EmailConfig>("/admin/email-config/configs", data),

  updateEmailConfig: (id: string, data: EmailConfigUpdate) => api.put<EmailConfig>(`/admin/email-config/configs/${id}`, data),

  deleteEmailConfig: (id: string) => api.delete<void>(`/admin/email-config/configs/${id}`),

  testEmailConfig: (id: string, testEmail: string) => api.post<{ success: boolean; message: string }>(`/admin/email-config/configs/${id}/test`, { test_email: testEmail }),

  setDefaultEmailConfig: (id: string) => api.post<EmailConfig>(`/admin/email-config/configs/${id}/set-default`),

  getEmailServiceStatus: () => api.get<{
    is_available: boolean;
    config_source: string;
    smtp_host?: string;
    smtp_port?: number;
    smtp_user?: string;
    from_email?: string;
    from_name?: string;
    use_tls?: boolean;
  }>("/admin/email-config/status"),
};

export const chronicDiseasesApi = {
  getAll: () => api.get<ChronicDiseaseListResponse>('/chronic-diseases'),
  getById: (id: string) => api.get<ChronicDisease>(`/chronic-diseases/${id}`),
};
