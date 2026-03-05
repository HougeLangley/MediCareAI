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
  Settings,
  ArrowBack,
  Security,
  Computer,
  School,
  VerifiedUser,
} from '@mui/icons-material';
import { useForm } from 'react-hook-form';
import { useNavigate, Link as RouterLink } from 'react-router-dom';
import { useAuthContext } from '../../contexts/AuthContext';
import type { LoginCredentials } from '../../types';

const AdminLoginPage: React.FC = () => {
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
      platform: 'admin',
    },
  });

  useEffect(() => {
    if (isAuthenticated && user?.role === 'admin') {
      navigate('/admin', { replace: true });
    }
  }, [isAuthenticated, user, navigate]);

  useEffect(() => {
    clearError();
    const savedEmail = localStorage.getItem('medicare_admin_remember_email');
    if (savedEmail) {
      setValue('email', savedEmail);
      setRememberMe(true);
    }
  }, [clearError, setValue]);

  const onSubmit = async (data: LoginCredentials) => {
    setIsSubmitting(true);
    try {
      if (rememberMe) {
        localStorage.setItem('medicare_admin_remember_email', data.email);
      } else {
        localStorage.removeItem('medicare_admin_remember_email');
      }
      
      await login(data);
      
      if (user?.role !== 'admin') {
        throw new Error('此账号不是管理员账号');
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
        background: 'linear-gradient(135deg, #fc4a1a 0%, #f7b733 100%)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        py: 4,
      }}
    >
      <Container maxWidth="sm">
        <Paper elevation={3} sx={{ p: 4, borderRadius: 2 }}>
          <Box textAlign="center" mb={3}>
            <Settings sx={{ fontSize: 48, color: '#fc4a1a', mb: 1 }} />
            <Typography variant="h4" component="h1" fontWeight="bold" gutterBottom>
              MediCareAI
            </Typography>
            <Typography variant="subtitle1" color="text.secondary">
              管理员登录
            </Typography>

            <Card sx={{ mt: 3, mb: 2, bgcolor: '#fff5f0', borderLeft: '4px solid #fc4a1a' }}>
              <CardContent sx={{ py: 2 }}>
                <Typography variant="h6" sx={{ color: '#fc4a1a', mb: 1, fontWeight: 600 }}>
                  🔐 管理员专属平台
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2, lineHeight: 1.6 }}>
                  管理平台是 MediCareAI 系统的核心控制中心，管理员肩负着系统安全、
                  数据保护和平台运维的重要职责。
                </Typography>
                <List dense sx={{ py: 0 }}>
                  <ListItem sx={{ py: 0.5 }}>
                    <ListItemIcon sx={{ minWidth: 32 }}>
                      <Security sx={{ color: '#fc4a1a', fontSize: 20 }} />
                    </ListItemIcon>
                    <ListItemText
                      primary="系统安全监控与审计日志管理"
                      primaryTypographyProps={{ variant: 'body2' }}
                    />
                  </ListItem>
                  <ListItem sx={{ py: 0.5 }}>
                    <ListItemIcon sx={{ minWidth: 32 }}>
                      <Computer sx={{ color: '#fc4a1a', fontSize: 20 }} />
                    </ListItemIcon>
                    <ListItemText
                      primary="AI 模型配置与性能调优"
                      primaryTypographyProps={{ variant: 'body2' }}
                    />
                  </ListItem>
                  <ListItem sx={{ py: 0.5 }}>
                    <ListItemIcon sx={{ minWidth: 32 }}>
                      <School sx={{ color: '#fc4a1a', fontSize: 20 }} />
                    </ListItemIcon>
                    <ListItemText
                      primary="医学知识库管理与文档审核"
                      primaryTypographyProps={{ variant: 'body2' }}
                    />
                  </ListItem>
                  <ListItem sx={{ py: 0.5 }}>
                    <ListItemIcon sx={{ minWidth: 32 }}>
                      <VerifiedUser sx={{ color: '#fc4a1a', fontSize: 20 }} />
                    </ListItemIcon>
                    <ListItemText
                      primary="医生资质认证审核与权限管理"
                      primaryTypographyProps={{ variant: 'body2' }}
                    />
                  </ListItem>
                </List>
              </CardContent>
            </Card>
          </Box>

          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
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
                background: 'linear-gradient(135deg, #fc4a1a 0%, #f7b733 100%)',
                '&:hover': {
                  background: 'linear-gradient(135deg, #e5410a 0%, #e0a52f 100%)',
                },
              }}
            >
              {isSubmitting ? <CircularProgress size={24} /> : '登录'}
            </Button>
          </form>

          <Divider sx={{ my: 2 }} />

          <Box textAlign="center">
            <Typography variant="body2" color="text.secondary">
              管理员账号由系统预设，不提供自助注册
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

export default AdminLoginPage;
