import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Paper,
  Typography,
  TextField,
  Button,
  Alert,
  CircularProgress,
  Card,
  CardContent,
  Link,
  Divider,
  InputAdornment,
  IconButton,
  FormControlLabel,
  Checkbox,
} from '@mui/material';
import {
  Visibility,
  VisibilityOff,
  Email,
  Lock,
  LocalHospital,
} from '@mui/icons-material';
import { useForm } from 'react-hook-form';
import { useNavigate } from 'react-router-dom';
import { useAuthContext } from '../../contexts/AuthContext';
import type { LoginCredentials } from '../../types';

const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const { login, isAuthenticated, user, isLoading, error, clearError } = useAuthContext();

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
    setValue,
  } = useForm<LoginCredentials>({
    defaultValues: {
      email: '',
      password: '',
      platform: 'patient',
    },
  });

  // Redirect authenticated users based on their role
  useEffect(() => {
    if (isAuthenticated && user) {
      const roleRoutes: { [key: string]: string } = {
        patient: '/patient',
        doctor: '/doctor',
        admin: '/admin',
      };
      navigate(roleRoutes[user.role] || '/', { replace: true });
    }
  }, [isAuthenticated, user, navigate]);

  useEffect(() => {
    clearError();
    
    // Load saved credentials if remember me was checked
    const savedEmail = localStorage.getItem('medicare_remember_email');
    if (savedEmail) {
      setValue('email', savedEmail);
      setRememberMe(true);
    }
  }, [clearError, setValue]);

  const onSubmit = async (data: LoginCredentials) => {
    setIsSubmitting(true);
    try {
      if (rememberMe) {
        localStorage.setItem('medicare_remember_email', data.email);
      } else {
        localStorage.removeItem('medicare_remember_email');
      }
      
      await login(data);
    } catch (error) {
      // 错误已经在AuthContext中处理
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleTogglePassword = () => {
    setShowPassword(!showPassword);
  };

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="100vh">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box
      sx={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        py: 3,
      }}
    >
      <Container maxWidth="sm">
        <Paper
          elevation={20}
          sx={{
            borderRadius: 4,
            padding: 4,
            maxWidth: 450,
            margin: '0 auto',
          }}
        >
          <Box sx={{ textAlign: 'center', mb: 4 }}>
            <LocalHospital sx={{ fontSize: 64, color: '#667eea', mb: 2 }} />
            <Typography variant="h4" component="h1" fontWeight="bold" color="primary" gutterBottom>
              MediCareAI
            </Typography>
            <Typography variant="subtitle1" color="text.secondary">
              智能疾病管理系统
            </Typography>
            
            <Card sx={{ mt: 3, mb: 2, bgcolor: '#f8f9fa' }}>
              <CardContent sx={{ py: 2 }}>
                <Typography variant="h6" color="primary" gutterBottom>
                  📋 关于 MediCareAI
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ lineHeight: 1.6 }}>
                  MediCareAI 是一个依托人工智能技术实现的专业疾病管理系统。系统旨在对患者疾病进行定期随访和智能管理，
                  集成 MinerU 文档抽取和 AI 大语言模型，为医疗工作者提供强大的辅助诊断和治疗建议。
                  支持全科室疾病管理，包括内科、外科、儿科、妇科等多个专业领域。
                </Typography>
                <Typography variant="caption" color="primary" sx={{ display: 'block', mt: 1, fontWeight: 500 }}>
                  👤 作者：苏业钦 | License: MIT
                </Typography>
              </CardContent>
            </Card>
          </Box>

          <Box component="form" onSubmit={handleSubmit(onSubmit)}>
            {error && (
              <Alert severity="error" sx={{ mb: 3 }} onClose={clearError}>
                {error}
              </Alert>
            )}
            
            <TextField
              fullWidth
              label="邮箱地址"
              {...register('email', {
                required: '请输入邮箱地址',
                pattern: {
                  value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                  message: '请输入有效的邮箱地址',
                },
              })}
              error={!!errors.email}
              helperText={errors.email?.message as string}
              disabled={isSubmitting || isLoading}
              margin="normal"
              required
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Email color="action" />
                  </InputAdornment>
                ),
              }}
              sx={{ mb: 2 }}
            />

            <TextField
              fullWidth
              label="密码"
              type={showPassword ? 'text' : 'password'}
              {...register('password', {
                required: '请输入密码',
                minLength: {
                  value: 6,
                  message: '密码至少6个字符',
                },
              })}
              error={!!errors.password}
              helperText={errors.password?.message as string}
              disabled={isSubmitting || isLoading}
              margin="normal"
              required
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Lock color="action" />
                  </InputAdornment>
                ),
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      aria-label="toggle password visibility"
                      onClick={handleTogglePassword}
                      edge="end"
                      disabled={isSubmitting || isLoading}
                    >
                      {showPassword ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                  </InputAdornment>
                ),
              }}
              sx={{ mb: 2 }}
            />

            <FormControlLabel
              control={
                <Checkbox
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                  color="primary"
                />
              }
              label="记住我"
              sx={{ mb: 2 }}
            />

            <Button
              type="submit"
              fullWidth
              variant="contained"
              size="large"
              disabled={isSubmitting || isLoading}
              sx={{
                py: 1.5,
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                '&:hover': {
                  background: 'linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%)',
                },
              }}
            >
              {isSubmitting || isLoading ? (
                <CircularProgress size={24} color="inherit" />
              ) : (
                '登录'
              )}
            </Button>
          </Box>

          <Divider sx={{ my: 3 }} />

          <Box sx={{ textAlign: 'center' }}>
            <Typography variant="body2" color="text.secondary">
              还没有账号？{' '}
              <Link component="button" variant="body2" onClick={() => navigate('/register')}>
                立即注册
              </Link>
            </Typography>
          </Box>


        </Paper>
      </Container>
    </Box>
  );
};

export default LoginPage;