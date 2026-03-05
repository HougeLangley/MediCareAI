import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Container,
  Paper,
  Typography,
  Grid,
  Card,
  Button,
  Avatar,
  Chip,
  Alert,
  CircularProgress,
} from '@mui/material';
import {
  LocalHospital as HospitalIcon,
  Description as DescriptionIcon,
  Person as PersonIcon,
  Logout as LogoutIcon,
  EditNote as EditNoteIcon,
  FolderOpen as FolderOpenIcon,
  Group as GroupIcon,
  CalendarToday as CalendarTodayIcon,
  Star as StarIcon,
  Home as HomeIcon,
} from '@mui/icons-material';
import { useAuth } from '../../hooks/useAuth';
import { patientsApi } from '../../services/api';
import type { Patient } from '../../types';

const Dashboard: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [stats, setStats] = useState({
    totalPatients: 0,
    managedPatients: 0,
    todayDate: '',
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadQuickStats();
  }, []);

  const loadQuickStats = async () => {
    try {
      setLoading(true);
      const patients = await patientsApi.getPatients();
      const patientCount = patients?.length || 0;
      
      setStats({
        totalPatients: patientCount,
        managedPatients: patientCount,
        todayDate: new Date().toLocaleDateString('zh-CN'),
      });
    } catch (err) {
      console.error('加载统计数据失败:', err);
      setError('加载统计数据失败');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    if (window.confirm('确定要退出登录吗？')) {
      logout();
    }
  };

  const getInitial = (name?: string) => {
    return name?.charAt(0) || '患';
  };

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: '#f5f5f5' }}>
      <Container maxWidth="lg" sx={{ mt: 2 }}>
        <Paper
          elevation={4}
          sx={{
            p: 4,
            mb: 3,
            borderRadius: 3,
            background: 'linear-gradient(135deg, rgba(102, 126, 234, 0.9) 0%, rgba(118, 75, 162, 0.9) 100%)',
            color: 'white',
            position: 'relative',
            overflow: 'hidden',
          }}
        >
          <Box sx={{ position: 'relative', zIndex: 1, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <Box>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <HospitalIcon sx={{ fontSize: 28, mr: 1.5, color: 'rgba(255,255,255,0.9)' }} />
                <Typography variant="h5" sx={{ fontWeight: 'bold', color: 'rgba(255,255,255,0.9)' }}>
                  MediCareAI
                </Typography>
              </Box>
              <Typography variant="h4" component="h1" sx={{ fontWeight: 'light', letterSpacing: 1 }}>
                {user?.full_name ? `${user.full_name}，您好！` : '您好！'}
                <Chip
                  label="✨ VIP 用户"
                  size="small"
                  sx={{
                    ml: 1.5,
                    bgcolor: 'rgba(255, 215, 0, 0.3)',
                    color: '#ffd700',
                    border: '1px solid rgba(255, 215, 0, 0.5)',
                    fontWeight: 'bold',
                  }}
                />
              </Typography>
              <Typography variant="body1" sx={{ opacity: 0.9, mt: 0.5 }}>
                您的智能健康助手
              </Typography>
            </Box>
            <Avatar sx={{ bgcolor: 'rgba(255,255,255,0.2)', width: 56, height: 56, border: '2px solid rgba(255,255,255,0.5)' }}>
              <Typography variant="h4">{getInitial(user?.full_name)}</Typography>
            </Avatar>
          </Box>
        </Paper>

        {/* Navigation */}
        <Paper elevation={2} sx={{ p: 2, mb: 3, borderRadius: 2 }}>
          <Box sx={{ display: 'flex', justifyContent: 'center', gap: 1, flexWrap: 'wrap' }}>
            <Button
              startIcon={<HomeIcon />}
              onClick={() => navigate('/patient')}
              sx={{ borderRadius: 2, textTransform: 'none' }}
            >
              首页
            </Button>
            <Button
              startIcon={<PersonIcon />}
              onClick={() => navigate('/patient/profile')}
              sx={{ borderRadius: 2, textTransform: 'none' }}
            >
              个人中心
            </Button>
            <Button
              startIcon={<EditNoteIcon />}
              onClick={() => navigate('/patient/symptom-submit')}
              sx={{ borderRadius: 2, textTransform: 'none' }}
            >
              症状提交
            </Button>
            <Button
              startIcon={<DescriptionIcon />}
              onClick={() => navigate('/patient/medical-records')}
              sx={{ borderRadius: 2, textTransform: 'none' }}
            >
              诊疗记录
            </Button>
            <Button
              startIcon={<LogoutIcon />}
              onClick={handleLogout}
              color="error"
              sx={{ borderRadius: 2, textTransform: 'none' }}
            >
              退出
            </Button>
          </Box>
        </Paper>

        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} md={4} sx={{ display: 'flex' }}>
            <Card
              sx={{
                flex: 1,
                display: 'flex',
                flexDirection: 'column',
                p: 4,
                textAlign: 'center',
                cursor: 'pointer',
                transition: 'all 0.3s',
                '&:hover': {
                  transform: 'translateY(-10px)',
                  boxShadow: 6,
                },
              }}
              onClick={() => navigate('/patient/symptom-submit')}
            >
              <EditNoteIcon sx={{ fontSize: 64, mb: 2, color: '#667eea' }} />
              <Typography variant="h5" gutterBottom fontWeight="bold">
                症状提交
              </Typography>
              <Typography variant="body1" color="text.secondary" sx={{ mb: 3, flex: 1 }}>
                描述您的症状，AI 将基于 MinerU 和先进的大语言模型为您进行智能诊断分析
              </Typography>
              <Button variant="contained" sx={{ borderRadius: 2, background: 'linear-gradient(135deg, #667eea, #764ba2)' }}>
                开始诊断
              </Button>
            </Card>
          </Grid>

          <Grid item xs={12} md={4} sx={{ display: 'flex' }}>
            <Card
              sx={{
                flex: 1,
                display: 'flex',
                flexDirection: 'column',
                p: 4,
                textAlign: 'center',
                cursor: 'pointer',
                transition: 'all 0.3s',
                '&:hover': {
                  transform: 'translateY(-10px)',
                  boxShadow: 6,
                },
              }}
              onClick={() => navigate('/patient/medical-records')}
            >
              <DescriptionIcon sx={{ fontSize: 64, mb: 2, color: '#667eea' }} />
              <Typography variant="h5" gutterBottom fontWeight="bold">
                诊疗记录
              </Typography>
              <Typography variant="body1" color="text.secondary" sx={{ mb: 3, flex: 1 }}>
                查看您的历史诊疗记录、诊断历史和健康状况变化
              </Typography>
              <Button variant="contained" sx={{ borderRadius: 2, background: 'linear-gradient(135deg, #667eea, #764ba2)' }}>
                查看记录
              </Button>
            </Card>
          </Grid>

          <Grid item xs={12} md={4} sx={{ display: 'flex' }}>
            <Card
              sx={{
                flex: 1,
                display: 'flex',
                flexDirection: 'column',
                p: 4,
                textAlign: 'center',
                cursor: 'pointer',
                transition: 'all 0.3s',
                '&:hover': {
                  transform: 'translateY(-10px)',
                  boxShadow: 6,
                },
              }}
              onClick={() => navigate('/patient/profile')}
            >
              <PersonIcon sx={{ fontSize: 64, mb: 2, color: '#667eea' }} />
              <Typography variant="h5" gutterBottom fontWeight="bold">
                个人中心
              </Typography>
              <Typography variant="body1" color="text.secondary" sx={{ mb: 3, flex: 1 }}>
                管理您的个人信息、基本资料、联系信息和健康档案
              </Typography>
              <Button variant="contained" sx={{ borderRadius: 2, background: 'linear-gradient(135deg, #667eea, #764ba2)' }}>
                编辑信息
              </Button>
            </Card>
          </Grid>
        </Grid>

        {/* Quick Info */}
        <Paper elevation={2} sx={{ p: 4, borderRadius: 3, mb: 4 }}>
          <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <StarIcon />
            快速了解
          </Typography>
          <Grid container spacing={3}>
            <Grid item xs={12} sm={6} md={3}>
              <Card variant="outlined" sx={{ p: 3, textAlign: 'center' }}>
                <GroupIcon sx={{ fontSize: 24, mb: 1, color: '#667eea' }} />
                <Typography variant="h4" sx={{ fontWeight: 'bold', color: '#667eea' }}>
                  {loading ? <CircularProgress size={24} /> : stats.totalPatients}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  患者总数
                </Typography>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card variant="outlined" sx={{ p: 3, textAlign: 'center' }}>
                <HospitalIcon sx={{ fontSize: 24, mb: 1, color: '#667eea' }} />
                <Typography variant="h4" sx={{ fontWeight: 'bold', color: '#667eea' }}>
                  {loading ? <CircularProgress size={24} /> : stats.managedPatients}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  管理患者
                </Typography>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card variant="outlined" sx={{ p: 3, textAlign: 'center' }}>
                <CalendarTodayIcon sx={{ fontSize: 24, mb: 1, color: '#667eea' }} />
                <Typography variant="h4" sx={{ fontWeight: 'bold', color: '#667eea' }}>
                  {stats.todayDate}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  今天日期
                </Typography>
              </Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card variant="outlined" sx={{ p: 3, textAlign: 'center' }}>
                <StarIcon sx={{ fontSize: 24, mb: 1, color: '#667eea' }} />
                <Typography variant="h6" sx={{ fontWeight: 'bold', color: '#667eea' }}>
                  AI 智能诊断
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  智能分析
                </Typography>
              </Card>
            </Grid>
          </Grid>
        </Paper>

        {/* Footer */}
        <Box sx={{ textAlign: 'center', py: 3, mb: 4 }}>
          <Typography variant="body2" color="text.secondary">
            MediCareAI 使用先进的 AI 技术为您提供智能诊疗建议。
            <br />
            本系统仅供参考，请以医生的实际诊断为准。
            <br />
            <Typography component="span" color="#667eea" sx={{ mt: 1, display: 'inline-block' }}>
              作者：苏业钦 | License: MIT
            </Typography>
          </Typography>
        </Box>

        {/* Error Alert */}
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}
      </Container>
    </Box>
  );
};

export default Dashboard;
