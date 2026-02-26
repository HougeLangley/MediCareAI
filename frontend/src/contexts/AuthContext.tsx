import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { authApi } from '../services/api';
import { CONFIG } from '../lib/config';
import type { User, LoginCredentials, RegisterData } from '../types';

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => void;
  clearError: () => void;
  setUser: React.Dispatch<React.SetStateAction<User | null>>;
}
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => void;
  clearError: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const clearError = () => setError(null);

  useEffect(() => {
    const initAuth = async () => {
      const token = localStorage.getItem(CONFIG.TOKEN_KEY);
      if (token) {
        try {
          const userData = await authApi.me();
          setUser(userData);
        } catch {
          localStorage.removeItem(CONFIG.TOKEN_KEY);
          localStorage.removeItem(CONFIG.REFRESH_TOKEN_KEY);
        }
      }
      setIsLoading(false);
    };
    initAuth();
  }, []);

  const login = async (credentials: LoginCredentials) => {
    try {
      setError(null);
      const response = await authApi.login(credentials);
      
      if (!response || !response.tokens || !response.user) {
        throw new Error('登录响应格式错误');
      }
      
      localStorage.setItem(CONFIG.TOKEN_KEY, response.tokens.access_token);
      localStorage.setItem(CONFIG.REFRESH_TOKEN_KEY, response.tokens.refresh_token);
      setUser(response.user);
      
      // 检查是否需要引导完善信息（首次登录或信息不完整）
      const needsProfileCompletion = !response.user.is_verified || 
        (response.user.role === 'patient' && (!response.user.address || !response.user.phone));
      
      if (needsProfileCompletion && response.user.role === 'patient') {
        // 跳转到完善信息页面
        window.location.href = '/patient/complete-profile';
      } else {
        const roleRoutes: { [key: string]: string } = {
          patient: '/patient',
          doctor: '/doctor',
          admin: '/admin',
        };
        window.location.href = roleRoutes[response.user.role] || '/';
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : '登录失败');
      setError(err.message || '登录失败');
      throw err;
    }
  };
    try {
      setError(null);
      const response = await authApi.login(credentials);
      
      if (!response || !response.tokens || !response.user) {
        throw new Error('登录响应格式错误');
      }
      
      localStorage.setItem(CONFIG.TOKEN_KEY, response.tokens.access_token);
      localStorage.setItem(CONFIG.REFRESH_TOKEN_KEY, response.tokens.refresh_token);
      setUser(response.user);
      
      const roleRoutes: { [key: string]: string } = {
        patient: '/patient',
        doctor: '/doctor',
        admin: '/admin',
      };
      window.location.href = roleRoutes[response.user.role] || '/';
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : '登录失败');
      setError(err.message || '登录失败');
      throw err;
    }
  };

  const register = async (data: RegisterData) => {
    try {
      setError(null);
      const response = await authApi.register(data);
      
      if (!response || !response.message) {
        throw new Error('注册响应格式错误：服务器返回数据不完整');
      }
      
      // 注册成功，不自动登录，不存储token
      // 由调用方（RegisterPage）处理跳转
      
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : '注册失败');
      setError(err.message || '注册失败');
      throw err;
    }
  };

  const logout = () => {
    const currentUser = user;
    authApi.logout().catch(() => {});
    localStorage.removeItem(CONFIG.TOKEN_KEY);
    localStorage.removeItem(CONFIG.REFRESH_TOKEN_KEY);
    setUser(null);
    
    if (currentUser?.role === 'admin') {
      window.location.href = '/admin-login';
    } else if (currentUser?.role === 'doctor') {
      window.location.href = '/doctor-login';
    } else {
      window.location.href = '/login';
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        error,
        login,
        register,
        logout,
        clearError,
        setUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        error,
        login,
        register,
        logout,
        clearError,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuthContext = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuthContext must be used within an AuthProvider');
  }
  return context;
};

// Alias for backward compatibility
export const useAuth = useAuthContext;

export { AuthContext };
