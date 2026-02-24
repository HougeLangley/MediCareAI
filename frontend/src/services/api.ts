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

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem(CONFIG.REFRESH_TOKEN_KEY);
        if (!refreshToken) {
          throw new Error('No refresh token');
        }

        const response = await axios.post(`${CONFIG.API_BASE}${CONFIG.API_VERSION}/auth/refresh`, {
          refresh_token: refreshToken,
        });

        // Enhanced null checking for response data
        const responseData = response?.data;
        if (!responseData?.data) {
          throw new Error('Invalid refresh token response');
        }
        
        const { access_token, refresh_token } = responseData.data as Token;
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
        window.location.href = '/login';
        return Promise.reject(error);
      }
    }

    const responseData = error.response?.data as ApiErrorResponse;
    const errorMessage = responseData?.detail || responseData?.message || error.message;
    console.error('API Error:', errorMessage);
    return Promise.reject(new Error(errorMessage));
  }
);

export { apiClient };

export const api = {
  get: async <T>(url: string, config?: AxiosRequestConfig): Promise<T> => {
    const response = await apiClient.get<ApiResponse<T>>(url, config);
    return (response.data.data || response.data) as T;
  },

  post: async <T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T> => {
    const response = await apiClient.post<ApiResponse<T>>(url, data, config);
    return (response.data.data || response.data) as T;
  },

  put: async <T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T> => {
    const response = await apiClient.put<ApiResponse<T>>(url, data, config);
    return (response.data.data || response.data) as T;
  },

  patch: async <T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T> => {
    const response = await apiClient.patch<ApiResponse<T>>(url, data, config);
    return (response.data.data || response.data) as T;
  },

  delete: async <T>(url: string, config?: AxiosRequestConfig): Promise<T> => {
    const response = await apiClient.delete<ApiResponse<T>>(url, config);
    return (response.data.data || response.data) as T;
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
    return (response.data.data || response.data) as T;
  },
};

export const authApi = {
  login: (credentials: LoginCredentials) =>
    api.post<{ user: User; tokens: Token }>('/auth/login', credentials),

  register: (data: RegisterData) => {
    const { role, title, department, hospital, license_number, specialty, address, terms, emergency_contact, ...baseData } = data;
    
    const backendRequestData: BackendRegisterData = {
      ...baseData as BackendRegisterData,
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
  rejectDoctor: (id: string) => api.post<void>(`/admin/doctors/verifications/${id}/reject`),
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
  // AI Model APIs
  getAIModels: () => api.get<AIModelConfigs>('/admin/ai-models'),
  testAIModel: (modelType: string, config?: AIModelConfig) => api.post<unknown>(`/admin/ai-models/${modelType}/test`, config || {}),
  saveAIModelConfig: (modelType: string, config: AIModelConfig) => api.post<unknown>(`/admin/ai-models/${modelType}/config`, config),
  getEmbeddingProviders: () => api.get<AIProvider[]>('/admin/embedding/providers'),
  validateEmbeddingUrl: (url: string) => api.post<{
    warnings: string[];
    suggestions: string[];
    formatted_url: string;
  }>('/admin/embedding/validate-url', { url }),
  changePassword: (current_password: string, new_password: string) =>
    api.post<void>('/admin/change-password', { current_password, new_password }),
};

export const chronicDiseasesApi = {
  getAll: () => api.get<ChronicDiseaseListResponse>('/chronic-diseases'),
  getById: (id: string) => api.get<ChronicDisease>(`/chronic-diseases/${id}`),
};

