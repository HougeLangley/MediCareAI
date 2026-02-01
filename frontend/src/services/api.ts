import axios, { AxiosInstance, AxiosResponse } from 'axios';
import { 
  User, 
  UserCreate, 
  UserLogin, 
  Token, 
  Patient, 
  PatientCreate, 
  PatientUpdate,
  ApiResponse,
  PaginatedResponse,
  ApiError
} from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

class ApiService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: `${API_BASE_URL}/api/v1`,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // 请求拦截器 - 添加认证令牌
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // 响应拦截器 - 处理错误
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          // 令牌过期，清除本地存储并重定向到登录页
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          localStorage.removeItem('user');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // 通用请求方法
  private async request<T>(
    method: 'GET' | 'POST' | 'PUT' | 'DELETE',
    url: string,
    data?: any
  ): Promise<T> {
    try {
      const response: AxiosResponse<T> = await this.client.request({
        method,
        url,
        data,
      });
      return response.data;
    } catch (error: any) {
      const apiError: ApiError = {
        detail: error.response?.data?.detail || error.message || 'Unknown error',
        status: error.response?.status,
      };
      throw apiError;
    }
  }

  // 认证相关API
  async register(userData: UserCreate): Promise<User> {
    return this.request<User>('POST', '/auth/register', userData);
  }

  async login(credentials: UserLogin): Promise<Token> {
    return this.request<Token>('POST', '/auth/login', credentials);
  }

  async logout(): Promise<{ message: string }> {
    return this.request<{ message: string }>('POST', '/auth/logout');
  }

  async getCurrentUser(): Promise<User> {
    return this.request<User>('GET', '/auth/me');
  }

  async changePassword(currentPassword: string, newPassword: string): Promise<{ message: string }> {
    return this.request<{ message: string }>('POST', '/auth/change-password', {
      current_password: currentPassword,
      new_password: newPassword,
    });
  }

  // 患者管理API
  async getPatients(skip = 0, limit = 20): Promise<Patient[]> {
    return this.request<Patient[]>('GET', `/patients?skip=${skip}&limit=${limit}`);
  }

  async getPatientsCount(): Promise<{ count: number }> {
    return this.request<{ count: number }>('GET', '/patients/count');
  }

  async getPatient(patientId: string): Promise<Patient> {
    return this.request<Patient>('GET', `/patients/${patientId}`);
  }

  async createPatient(patientData: PatientCreate): Promise<Patient> {
    return this.request<Patient>('POST', '/patients', patientData);
  }

  async updatePatient(patientId: string, patientData: PatientUpdate): Promise<Patient> {
    return this.request<Patient>('PUT', `/patients/${patientId}`, patientData);
  }

  async deletePatient(patientId: string): Promise<{ message: string }> {
    return this.request<{ message: string }>('DELETE', `/patients/${patientId}`);
  }

  // 文档上传API
  async uploadDocument(medicalCaseId: string, file: File): Promise<any> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('medical_case_id', medicalCaseId);

    const response = await this.client.post('/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  async getCaseDocuments(medicalCaseId: string): Promise<any[]> {
    return this.request<any[]>('GET', `/documents/case/${medicalCaseId}`);
  }

  async getDocument(documentId: string): Promise<any> {
    return this.request<any>('GET', `/documents/${documentId}`);
  }

  async extractDocumentContent(documentId: string, extractionRequest: any): Promise<any> {
    return this.request<any>('POST', `/documents/${documentId}/extract`, extractionRequest);
  }

  async getDocumentContent(documentId: string): Promise<any> {
    return this.request<any>('GET', `/documents/${documentId}/content`);
  }

  async deleteDocument(documentId: string): Promise<{ message: string }> {
    return this.request<{ message: string }>('DELETE', `/documents/${documentId}`);
  }

  // AI服务API
  async getAIDiagnosis(requestData: any): Promise<any> {
    return this.request<any>('POST', '/ai/diagnose', requestData);
  }

  async getAITreatment(requestData: any): Promise<any> {
    return this.request<any>('POST', '/ai/treatment', requestData);
  }

  async getAIFollowUp(requestData: any): Promise<any> {
    return this.request<any>('POST', '/ai/follow-up', requestData);
  }

  async getAIFeedback(feedbackId: string): Promise<any> {
    return this.request<any>('GET', `/ai/feedback/${feedbackId}`);
  }

  async reviewAIFeedback(feedbackId: string, reviewData: any): Promise<any> {
    return this.request<any>('POST', `/ai/feedback/${feedbackId}/review`, reviewData);
  }
}

// 创建单例实例
const apiService = new ApiService();

export default apiService;