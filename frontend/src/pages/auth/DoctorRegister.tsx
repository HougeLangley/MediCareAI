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
  InputAdornment,
  IconButton,
  Divider,
  Link,
  Grid,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemText,
} from '@mui/material';
import {
  Visibility,
  VisibilityOff,
  Email,
  Lock,
  LocalHospital,
  ArrowBack,
  Phone,
  Person,
  Business,
  MedicalServices,
  School,
  Upload,
  Delete,
} from '@mui/icons-material';
import { useForm, Controller } from 'react-hook-form';
import { useNavigate } from 'react-router-dom';
import { authApi } from '../../services/api';

interface DoctorRegisterData {
  email: string;
  password: string;
  full_name: string;
  phone?: string;
  license_number: string;
  hospital: string;
  department: string;
  title: string;
  specialty: string;
  terms: boolean;
}

const MAX_FILE_SIZE = 10 * 1024 * 1024

const DoctorRegister: React.FC = () => {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [licenseFiles, setLicenseFiles] = useState<File[]>([]);

  const {
    control,
    handleSubmit,
    formState: { errors },
  } = useForm<DoctorRegisterData>({
    defaultValues: {
      email: '',
      password: '',
      full_name: '',
      phone: '',
      license_number: '',
      hospital: '',
      department: '',
      title: '',
      specialty: '',
      terms: false,
    },
  });

  useEffect(() => {
    setError(null);
  }, []);

  const clearError = () => setError(null);

  const handleTogglePassword = () => {
    setShowPassword(!showPassword);
  };

  const handleBackToPlatformSelect = () => {
    navigate('/platform-select');
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files.length > 0) {
      const files = Array.from(event.target.files);

      const oversizedFiles = files.filter(file => file.size > MAX_FILE_SIZE);
      if (oversizedFiles.length > 0) {
        setError(`以下文件超过10MB限制: ${oversizedFiles.map(f => f.name).join(', ')}`);
        return;
      }

      setLicenseFiles(prev => [...prev, ...files]);
    }
  };

  const handleRemoveFile = (index: number) => {
    setLicenseFiles(prev => prev.filter((_, i) => i !== index));
  };

  const onSubmit = async (data: DoctorRegisterData) => {
    setIsSubmitting(true);
    setIsLoading(true);
    try {
      if (licenseFiles.length === 0) {
        setError('请上传执业证书文件');
        setIsSubmitting(false);
        setIsLoading(false);
        return;
      }

      const registerData = {
        email: data.email,
        password: data.password,
        full_name: data.full_name,
        phone: data.phone,
        title: data.title,
        department: data.department,
        hospital: data.hospital,
        license_number: data.license_number,
        specialty: data.specialty,
        professional_type: data.specialty,
      };

      await authApi.registerDoctor(registerData, licenseFiles);

      navigate('/doctor-login');
    } catch (err: any) {
      setError(err.message || '注册失败');
    } finally {
      setIsSubmitting(false);
      setIsLoading(false);
    }
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #11998e 0%, #38ef7d 100%)',
        display: 'flex',
        alignItems: 'center',
        py: 4,
      }}
    >
      <Container maxWidth="md">
        <Paper
          elevation={24}
          sx={{
            p: 4,
            borderRadius: 4,
            background: 'rgba(255, 255, 255, 0.98)',
          }}
        >
          <Box sx={{ textAlign: 'center', mb: 4 }}>
            <LocalHospital sx={{ fontSize: 64, color: '#11998e', mb: 2 }} />
            <Typography variant="h4" component="h1" fontWeight="bold" sx={{ color: '#11998e' }} gutterBottom>
              MediCareAI
            </Typography>
            <Typography variant="subtitle1" sx={{ color: '#333' }}>
              医生认证申请 - 加入我们的医疗专家团队
            </Typography>
          </Box>

          <Card sx={{ mb: 3, bgcolor: '#f0f9f0', border: '1px solid #38ef7d' }}>
            <CardContent sx={{ py: 2 }}>
              <Typography variant="body2" sx={{ color: '#11998e', fontWeight: 'bold' }}>
                认证说明：
              </Typography>
              <Typography variant="body2" sx={{ color: '#333' }}>
                提交申请后，我们的管理员会在1-3个工作日内审核您的资质。审核通过后，您将可以使用医生平台的全部功能。
              </Typography>
            </CardContent>
          </Card>

          {error && (
            <Alert severity="error" sx={{ mb: 3 }} onClose={clearError}>
              {error}
            </Alert>
          )}

          <Box component="form" onSubmit={handleSubmit(onSubmit)}>
            <Typography variant="h6" sx={{ color: '#11998e', fontWeight: 'bold' }} gutterBottom>
              基本信息
            </Typography>

            <Grid container spacing={2} sx={{ mb: 3 }}>
              <Grid item xs={12} sm={6}>
                <Controller
                  name="full_name"
                  control={control}
                  rules={{ required: '请输入真实姓名' }}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="真实姓名"
                      placeholder="请输入真实姓名"
                      autoComplete="name"
                      disabled={isSubmitting || isLoading}
                      InputProps={{
                        startAdornment: (
                          <InputAdornment position="start">
                            <Person color="action" />
                          </InputAdornment>
                        ),
                      }}
                      error={!!errors.full_name}
                      helperText={errors.full_name?.message}
                    />
                  )}
                />
              </Grid>

              <Grid item xs={12} sm={6}>
                <Controller
                  name="email"
                  control={control}
                  rules={{ 
                    required: '请输入邮箱地址',
                    pattern: {
                      value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                      message: '请输入有效的邮箱地址',
                    },
                  }}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="邮箱地址"
                      type="email"
                      placeholder="请输入邮箱地址"
                      autoComplete="email"
                      disabled={isSubmitting || isLoading}
                      InputProps={{
                        startAdornment: (
                          <InputAdornment position="start">
                            <Email color="action" />
                          </InputAdornment>
                        ),
                      }}
                      error={!!errors.email}
                      helperText={errors.email?.message}
                    />
                  )}
                />
              </Grid>

              <Grid item xs={12} sm={6}>
                <Controller
                  name="phone"
                  control={control}
                  rules={{ required: '请输入手机号码' }}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="手机号"
                      type="tel"
                      placeholder="请输入手机号码"
                      autoComplete="tel"
                      disabled={isSubmitting || isLoading}
                      InputProps={{
                        startAdornment: (
                          <InputAdornment position="start">
                            <Phone color="action" />
                          </InputAdornment>
                        ),
                      }}
                      error={!!errors.phone}
                      helperText={errors.phone?.message}
                    />
                  )}
                />
              </Grid>

              <Grid item xs={12} sm={6}>
                <Controller
                  name="password"
                  control={control}
                  rules={{
                    required: '请输入密码',
                    minLength: {
                      value: 8,
                      message: '密码长度至少为8位',
                    },
                  }}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="密码"
                      type={showPassword ? 'text' : 'password'}
                      placeholder="至少8位字符"
                      autoComplete="new-password"
                      disabled={isSubmitting || isLoading}
                      InputProps={{
                        startAdornment: (
                          <InputAdornment position="start">
                            <Lock color="action" />
                          </InputAdornment>
                        ),
                        endAdornment: (
                          <InputAdornment position="end">
                            <IconButton
                              size="small"
                              onClick={handleTogglePassword}
                              edge="end"
                              disabled={isSubmitting || isLoading}
                              aria-label="toggle password visibility"
                            >
                              {showPassword ? <VisibilityOff /> : <Visibility />}
                            </IconButton>
                          </InputAdornment>
                        ),
                      }}
                      error={!!errors.password}
                      helperText={errors.password?.message}
                    />
                  )}
                />
              </Grid>
            </Grid>

            <Divider sx={{ my: 3 }} />

            <Typography variant="h6" sx={{ color: '#11998e', fontWeight: 'bold' }} gutterBottom>
              职业信息
            </Typography>

            <Grid container spacing={2} sx={{ mb: 3 }}>
              <Grid item xs={12} sm={6}>
                <Controller
                  name="license_number"
                  control={control}
                  rules={{ required: '请输入执业证号' }}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="执业证号"
                      placeholder="请输入执业证号"
                      autoComplete="off"
                      disabled={isSubmitting || isLoading}
                      error={!!errors.license_number}
                      helperText={errors.license_number?.message}
                    />
                  )}
                />
              </Grid>

              <Grid item xs={12} sm={6}>
                <Controller
                  name="hospital"
                  control={control}
                  rules={{ required: '请输入所在医院' }}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="所在医院"
                      placeholder="请输入所在医院"
                      autoComplete="organization"
                      disabled={isSubmitting || isLoading}
                      InputProps={{
                        startAdornment: (
                          <InputAdornment position="start">
                            <Business color="action" />
                          </InputAdornment>
                        ),
                      }}
                      error={!!errors.hospital}
                      helperText={errors.hospital?.message}
                    />
                  )}
                />
              </Grid>

              <Grid item xs={12} sm={6}>
                <Controller
                  name="department"
                  control={control}
                  rules={{ required: '请输入科室' }}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="科室"
                      placeholder="请输入科室"
                      autoComplete="organization-title"
                      disabled={isSubmitting || isLoading}
                      error={!!errors.department}
                      helperText={errors.department?.message}
                    />
                  )}
                />
              </Grid>

              <Grid item xs={12} sm={6}>
                <Controller
                  name="title"
                  control={control}
                  rules={{ required: '请输入职称' }}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="职称"
                      placeholder="如：主任医师、副主任医师等"
                      autoComplete="organization-title"
                      disabled={isSubmitting || isLoading}
                      InputProps={{
                        startAdornment: (
                          <InputAdornment position="start">
                            <School color="action" />
                          </InputAdornment>
                        ),
                      }}
                      error={!!errors.title}
                      helperText={errors.title?.message}
                    />
                  )}
                />
              </Grid>

              <Grid item xs={12}>
                <Controller
                  name="specialty"
                  control={control}
                  rules={{ required: '请输入专业领域' }}
                  render={({ field }) => (
                    <TextField
                      {...field}
                      fullWidth
                      label="专业领域"
                      placeholder="请输入专业领域，如：心血管内科、神经外科等"
                      autoComplete="off"
                      disabled={isSubmitting || isLoading}
                      InputProps={{
                        startAdornment: (
                          <InputAdornment position="start">
                            <MedicalServices color="action" />
                          </InputAdornment>
                        ),
                      }}
                      error={!!errors.specialty}
                      helperText={errors.specialty?.message}
                    />
                  )}
                />
              </Grid>

              <Grid item xs={12}>
                <Box>
                  <Typography variant="subtitle2" sx={{ color: '#11998e', fontWeight: 'bold' }} gutterBottom>
                    中华人民共和国医师资格证书、中华人民共和国医师执业证书
                  </Typography>
                  <Typography variant="caption" sx={{ color: '#666', display: 'block', mb: 1 }}>
                    请上传含两个证书的封面、照片页和有签发人的页面，一般4张图片即可（单个文件不超过10MB）
                  </Typography>
                  <input
                    accept="image/*,.pdf"
                    id="license-file"
                    type="file"
                    multiple
                    onChange={handleFileChange}
                    disabled={isSubmitting || isLoading}
                    style={{ display: 'none' }}
                  />
                  <label htmlFor="license-file">
                    <Button
                      variant="outlined"
                      component="span"
                      startIcon={<Upload />}
                      disabled={isSubmitting || isLoading}
                      sx={{ mb: 1 }}
                    >
                      选择证书文件
                    </Button>
                  </label>
                  {licenseFiles.length > 0 && (
                    <List dense sx={{ mt: 1, bgcolor: '#f5f5f5', borderRadius: 1 }}>
                      {licenseFiles.map((file, index) => (
                        <ListItem
                          key={index}
                          secondaryAction={
                            <IconButton
                              edge="end"
                              size="small"
                              onClick={() => handleRemoveFile(index)}
                              disabled={isSubmitting || isLoading}
                            >
                              <Delete fontSize="small" />
                            </IconButton>
                          }
                        >
                          <ListItemText
                            primary={file.name}
                            secondary={`${(file.size / 1024 / 1024).toFixed(2)} MB`}
                          />
                        </ListItem>
                      ))}
                    </List>
                  )}
                </Box>
              </Grid>
            </Grid>

            <Button
              type="submit"
              fullWidth
              variant="contained"
              size="large"
              disabled={isSubmitting || isLoading}
              sx={{
                mb: 2,
                py: 1.5,
                background: 'linear-gradient(135deg, #11998e 0%, #38ef7d 100%)',
                color: 'white',
                '&:hover': {
                  background: 'linear-gradient(135deg, #0d8a7d 0%, #32d66f 100%)',
                },
              }}
            >
              {isSubmitting || isLoading ? (
                <CircularProgress size={24} color="inherit" />
              ) : (
                '提交认证申请'
              )}
            </Button>

            <Divider sx={{ my: 2 }} />

            <Box sx={{ textAlign: 'center' }}>
              <Link
                component="button"
                variant="body2"
                onClick={handleBackToPlatformSelect}
                sx={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: 1,
                  color: '#666',
                  textDecoration: 'none',
                  '&:hover': {
                    color: '#11998e',
                    textDecoration: 'underline',
                  },
                }}
              >
                <ArrowBack fontSize="small" />
                返回平台选择
              </Link>
            </Box>
          </Box>
        </Paper>
      </Container>
    </Box>
  );
};

export default DoctorRegister;