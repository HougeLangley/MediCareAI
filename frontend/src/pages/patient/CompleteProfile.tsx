import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Paper,
  Typography,
  Button,
  Stepper,
  Step,
  StepLabel,
  Alert,
  CircularProgress,
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { useAuthContext } from '../../contexts/AuthContext';
import { authApi, patientsApi } from '../../services/api';
import { AddressSelect } from '../../components/common/AddressSelect';

const steps = ['验证邮箱', '完善个人信息', '完成'];

const CompleteProfilePage: React.FC = () => {
  const navigate = useNavigate();
  const { user, setUser } = useAuthContext();
  const [activeStep, setActiveStep] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  // 表单数据
  const [address, setAddress] = useState({
    province: '',
    city: '',
    district: '',
    detail: '',
    fullAddress: '',
  });
  const [phone, setPhone] = useState('');

  useEffect(() => {
    // 如果用户已经验证过邮箱且信息完整，直接跳转到首页
    if (user?.is_verified && user?.address && user?.phone) {
      navigate('/patient');
    }
    
    // 设置当前步骤
    if (!user?.is_verified) {
      setActiveStep(0);
    } else if (!user?.address || !user?.phone) {
      setActiveStep(1);
    } else {
      setActiveStep(2);
    }
  }, [user, navigate]);

  // 步骤1：发送验证邮件
  const handleSendVerificationEmail = async () => {
    setIsLoading(true);
    setError('');
    try {
      await authApi.sendVerificationEmail();
      setSuccess('验证邮件已发送，请查收邮箱');
    } catch (err: any) {
      setError(err.message || '发送失败');
    } finally {
      setIsLoading(false);
    }
  };

  // 步骤2：保存个人信息
  const handleSaveProfile = async () => {
    if (!address.fullAddress) {
      setError('请填写完整地址');
      return;
    }
    if (!phone) {
      setError('请填写手机号码');
      return;
    }

    setIsLoading(true);
    setError('');
    try {
      await patientsApi.updateMe({
        address: address.fullAddress,
        phone,
      });
      
      // 更新本地用户数据
      if (user) {
        setUser({
          ...user,
          address: address.fullAddress,
          phone,
        });
      }
      
      setActiveStep(2);
      setSuccess('信息保存成功');
    } catch (err: any) {
      setError(err.message || '保存失败');
    } finally {
      setIsLoading(false);
    }
  };

  // 完成引导
  const handleComplete = () => {
    navigate('/patient');
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        py: 4,
      }}
    >
      <Container maxWidth="md">
        <Paper elevation={20} sx={{ p: 4, borderRadius: 4 }}>
          <Typography variant="h4" align="center" gutterBottom fontWeight="bold">
            完善个人信息
          </Typography>
          <Typography variant="body1" align="center" color="text.secondary" sx={{ mb: 4 }}>
            请完成以下步骤以正常使用系统功能
          </Typography>

          <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
            {steps.map((label) => (
              <Step key={label}>
                <StepLabel>{label}</StepLabel>
              </Step>
            ))}
          </Stepper>

          {error && (
            <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError('')}>
              {error}
            </Alert>
          )}

          {success && (
            <Alert severity="success" sx={{ mb: 3 }} onClose={() => setSuccess('')}>
              {success}
            </Alert>
          )}

          {/* 步骤1：验证邮箱 */}
          {activeStep === 0 && (
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <Typography variant="h6" gutterBottom>
                验证您的邮箱地址
              </Typography>
              <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
                为确保账户安全，我们需要验证您的邮箱：{user?.email}
              </Typography>
              <Button
                variant="contained"
                size="large"
                onClick={handleSendVerificationEmail}
                disabled={isLoading}
                sx={{
                  py: 1.5,
                  px: 4,
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                }}
              >
                {isLoading ? <CircularProgress size={24} /> : '发送验证邮件'}
              </Button>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
                发送后请查收邮箱并点击验证链接
              </Typography>
            </Box>
          )}

          {/* 步骤2：完善个人信息 */}
          {activeStep === 1 && (
            <Box sx={{ py: 2 }}>
              <Typography variant="h6" gutterBottom>
                完善个人资料
              </Typography>
              
              <Box sx={{ mb: 3 }}>
                <Typography variant="subtitle1" gutterBottom>
                  居住地址
                </Typography>
                <AddressSelect
                  value={address}
                  onChange={setAddress}
                  disabled={isLoading}
                  required
                />
              </Box>

              <Box sx={{ mb: 3 }}>
                <Typography variant="subtitle1" gutterBottom>
                  手机号码
                </Typography>
                <input
                  type="tel"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  placeholder="请输入手机号码"
                  style={{
                    width: '100%',
                    padding: '12px',
                    fontSize: '16px',
                    border: '1px solid #ddd',
                    borderRadius: '4px',
                  }}
                  disabled={isLoading}
                />
              </Box>

              <Button
                variant="contained"
                size="large"
                fullWidth
                onClick={handleSaveProfile}
                disabled={isLoading}
                sx={{
                  py: 1.5,
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                }}
              >
                {isLoading ? <CircularProgress size={24} /> : '保存并继续'}
              </Button>
            </Box>
          )}

          {/* 步骤3：完成 */}
          {activeStep === 2 && (
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <Typography variant="h5" color="success.main" gutterBottom>
                🎉 恭喜，设置完成！
              </Typography>
              <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
                您的个人信息已完善，现在可以开始使用 MediCareAI 的所有功能了
              </Typography>
              <Button
                variant="contained"
                size="large"
                onClick={handleComplete}
                sx={{
                  py: 1.5,
                  px: 4,
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                }}
              >
                进入系统
              </Button>
            </Box>
          )}
        </Paper>
      </Container>
    </Box>
  );
};

export default CompleteProfilePage;
