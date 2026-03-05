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
  Link,
  Divider,
  InputAdornment,
  IconButton,
  FormControlLabel,
  Checkbox,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
} from '@mui/material';
import {
  Visibility,
  VisibilityOff,
  Email,
  Lock,
  LocalHospital,
  ArrowBack,
  FolderShared,
  Assessment,
  Science,
} from '@mui/icons-material';
import { useForm } from 'react-hook-form';
import { useNavigate, Link as RouterLink } from 'react-router-dom';
import { useAuthContext } from '../../contexts/AuthContext';
import type { LoginCredentials } from '../../types';

const DoctorLoginPage: React.FC = () => {
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
      platform: 'doctor',
    },
  });

  useEffect(() => {
    if (isAuthenticated && user?.role === 'doctor') {
      navigate('/doctor', { replace: true });
    }
  }, [isAuthenticated, user, navigate]);

  useEffect(() => {
    clearError();
    const savedEmail = localStorage.getItem('medicare_doctor_remember_email');
    if (savedEmail) {
      setValue('email', savedEmail);
      setRememberMe(true);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const onSubmit = async (data: LoginCredentials) => {
    setIsSubmitting(true);
    try {
      if (rememberMe) {
        localStorage.setItem('medicare_doctor_remember_email', data.email);
      } else {
        localStorage.removeItem('medicare_doctor_remember_email');
      }
      
      await login(data);
      
      if (user?.role !== 'doctor') {
        throw new Error('此账号不是医生账号');
      }
    } catch (error: any) {
      console.error('Login error:', error);
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
        background: 'linear-gradient(135deg, #11998e 0%, #38ef7d 100%)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        py: 4,
      }}
    >
      <Container maxWidth="sm">
        <Paper elevation={3} sx={{ p: 4, borderRadius: 2 }}>
          <Box textAlign="center" mb={3}>
            <LocalHospital sx={{ fontSize: 48, color: '#11998e', mb: 1 }} />
            <Typography variant="h4" component="h1" fontWeight="bold" gutterBottom>
              MediCareAI
            </Typography>
            <Typography variant="subtitle1" color="text.secondary">
              医生登录
            </Typography>

            <Card sx={{ mt: 3, mb: 2, bgcolor: '#f0f9f6', borderLeft: '4px solid #11998e' }}>
              <CardContent sx={{ py: 2 }}>
                <Typography variant="h6" sx={{ color: '#11998e', mb: 1, fontWeight: 600 }}>
                  👨‍⚕️ 医生专业平台
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2, lineHeight: 1.6 }}>
                  MediCareAI 医生平台为专业医疗工作者提供强大的临床辅助工具，
                  助力精准诊疗和医学研究。
                </Typography>
                <List dense sx={{ py: 0 }}>
                  <ListItem sx={{ py: 0.5 }}>
                    <ListItemIcon sx={{ minWidth: 32 }}>
                      <FolderShared sx={{ color: '#11998e', fontSize: 20 }} />
                    </ListItemIcon>
                    <ListItemText 
                      primary="浏览匿名化病例，获取临床参考"
                      primaryTypographyProps={{ variant: 'body2' }}
                    />
                  </ListItem>
                  <ListItem sx={{ py: 0.5 }}>
                    <ListItemIcon sx={{ minWidth: 32 }}>
                      <Assessment sx={{ color: '#11998e', fontSize: 20 }} />
                    </ListItemIcon>
                    <ListItemText 
                      primary="查看@我的病例，管理患者咨询"
                      primaryTypographyProps={{ variant: 'body2' }}
                    />
                  </ListItem>
                  <ListItem sx={{ py: 0.5 }}>
                    <ListItemIcon sx={{ minWidth: 32 }}>
                      <Science sx={{ color: '#11998e', fontSize: 20 }} />
                    </ListItemIcon>
                    <ListItemText 
                      primary="科研数据检索与导出，支持双盲研究"
                      primaryTypographyProps={{ variant: 'body2' }}
                    />
                  </ListItem>
                </List>
              </CardContent>
            </Card>
          </Box>

          {error && (
            <Alert 
              severity="error" 
              sx={{ 
                mb: 3, 
                borderRadius: 2,
                border: '2px solid',
                borderColor: 'error.main',
                boxShadow: '0 4px 12px rgba(211, 47, 47, 0.2)',
                '& .MuiAlert-icon': {
                  fontSize: 32,
                  color: 'error.main'
                }
              }}
            >
              <Typography variant="subtitle1" fontWeight="bold" gutterBottom sx={{ color: 'error.main' }}>
                登录失败
              </Typography>
              <Typography variant="body1" sx={{ fontWeight: 500 }}>
                {error}
              </Typography>
              {error.includes('认证已撤销') && (
                <Box sx={{ mt: 2, p: 1.5, bgcolor: 'error.light', borderRadius: 1 }}>
                  <Typography variant="body2" sx={{ color: 'error.dark', fontWeight: 500 }}>
                    💡 如需恢复账号，请联系管理员重新认证
                  </Typography>
                </Box>
              )}
            </Alert>
          )}

          <form onSubmit={handleSubmit(onSubmit)}>
            <TextField
              fullWidth
              label="邮箱地址"
              variant="outlined"
              margin="normal"
              {...register('email', { 
                required: '请输入邮箱地址',
                pattern: {
                  value: /^\S+@\S+$/i,
                  message: '请输入有效的邮箱地址'
                }
              })}
              error={!!errors.email}
              helperText={errors.email?.message}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Email color="action" />
                  </InputAdornment>
                ),
              }}
            />

            <TextField
              fullWidth
              label="密码"
              type={showPassword ? 'text' : 'password'}
              variant="outlined"
              margin="normal"
              {...register('password', { 
                required: '请输入密码',
                minLength: {
                  value: 6,
                  message: '密码至少需要6个字符'
                }
              })}
              error={!!errors.password}
              helperText={errors.password?.message}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Lock color="action" />
                  </InputAdornment>
                ),
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton onClick={handleTogglePassword} edge="end">
                      {showPassword ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                  </InputAdornment>
                ),
              }}
            />

            <FormControlLabel
              control={
                <Checkbox
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                />
              }
              label="记住我"
              sx={{ mt: 1 }}
            />

            <Button
              type="submit"
              fullWidth
              variant="contained"
              size="large"
              disabled={isSubmitting}
              sx={{
                mt: 2,
                mb: 2,
                background: 'linear-gradient(135deg, #11998e 0%, #38ef7d 100%)',
                '&:hover': {
                  background: 'linear-gradient(135deg, #0f887c 0%, #32e075 100%)',
                },
              }}
            >
              {isSubmitting ? <CircularProgress size={24} /> : '登录'}
            </Button>
          </form>

          <Divider sx={{ my: 2 }} />

          <Box textAlign="center">
            <Typography variant="body2" color="text.secondary" gutterBottom>
              还没有医生账号？{' '}
              <Link component={RouterLink} to="/doctor-register" color="primary">
                立即注册
              </Link>
            </Typography>
            
            <Button
              component={RouterLink}
              to="/"
              startIcon={<ArrowBack />}
              sx={{ mt: 2 }}
            >
              返回平台选择
            </Button>
          </Box>
        </Paper>
      </Container>
    </Box>
  );
};

export default DoctorLoginPage;
