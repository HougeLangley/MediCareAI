import React, { useEffect, useState } from 'react';
import {
  Box,
  Container,
  Typography,
  Card,
  CardContent,
  Button,
  Grid,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Paper,
  Fade,
} from '@mui/material';
import {
  Person,
  LocalHospital,
  Settings,
  CheckCircle,
  Login as LoginIcon,
  ArrowForward,
} from '@mui/icons-material';
import { Link as RouterLink, useNavigate } from 'react-router-dom';

interface Platform {
  id: string;
  title: string;
  description: string;
  icon: React.ReactNode;
  features: string[];
  gradient: string;
  hoverColor: string;
}

const PlatformSelect: React.FC = () => {
  const navigate = useNavigate();
  const [visible, setVisible] = useState(false);

  const platforms: Platform[] = [
    {
      id: 'patient',
      title: '患者平台',
      description: '提交症状、获取AI诊断建议、管理您的健康档案',
      icon: <Person sx={{ fontSize: 64 }} />,
      features: [
        '智能症状分析与诊断',
        '诊疗记录管理',
        '文档上传与解析',
        '分享给指定医生',
      ],
      gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      hoverColor: '#5a6fd8',
    },
    {
      id: 'doctor',
      title: '医生平台',
      description: '浏览专业领域病例、科研数据导出、患者@病例管理',
      icon: <LocalHospital sx={{ fontSize: 64 }} />,
      features: [
        '浏览匿名化病例',
        '查看@我的病例',
        '科研数据检索与导出',
        '双盲数据收集',
      ],
      gradient: 'linear-gradient(135deg, #11998e 0%, #38ef7d 100%)',
      hoverColor: '#0f887c',
    },
    {
      id: 'admin',
      title: '管理平台',
      description: '系统监控、AI模型配置、知识库管理、医生认证审核',
      icon: <Settings sx={{ fontSize: 64 }} />,
      features: [
        '系统资源监控',
        'AI模型配置与管理',
        '知识库文档管理',
        '医生资质审核',
      ],
      gradient: 'linear-gradient(135deg, #fc4a1a 0%, #f7b733 100%)',
      hoverColor: '#e5410a',
    },
  ];

  useEffect(() => {
    setVisible(true);
  }, []);

  return (
    <Box
      sx={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        py: 4,
      }}
    >
      <Container maxWidth="lg">
        <Box sx={{ textAlign: 'center', mb: 8 }}>
          <Typography
            variant="h2"
            component="h1"
            fontWeight="bold"
            color="white"
            gutterBottom
            sx={{
              fontSize: { xs: '2.5rem', md: '3.5rem' },
              animation: 'float 3s ease-in-out infinite',
              '@keyframes float': {
                '0%, 100%': { transform: 'translateY(0px)' },
                '50%': { transform: 'translateY(-10px)' },
              },
            }}
          >
            🏥 MediCareAI
          </Typography>
          <Typography
            variant="h5"
            color="rgba(255, 255, 255, 0.9)"
            paragraph
            sx={{ maxWidth: 600, mx: 'auto' }}
          >
            智能疾病管理系统 - 选择您的登录平台
            <br />
            Intelligent Disease Management System
          </Typography>
        </Box>

        <Grid container spacing={4} justifyContent="center">
          {platforms.map((platform, index) => (
            <Grid item xs={12} md={4} key={platform.id}>
              <Fade
                in={visible}
                timeout={1000}
                style={{
                  transitionDelay: visible ? `${index * 200}ms` : '0ms',
                }}
              >
                <Card
                  sx={{
                    height: '100%',
                    transition: 'all 0.3s ease',
                    '&:hover': {
                      transform: 'translateY(-5px)',
                      boxShadow: '0 20px 60px rgba(0, 0, 0, 0.3)',
                    },
                    position: 'relative',
                    overflow: 'visible',
                    '&::before': {
                      content: '""',
                      position: 'absolute',
                      top: 0,
                      left: 0,
                      right: 0,
                      height: 5,
                      background: platform.gradient,
                      borderTopLeftRadius: 8,
                      borderTopRightRadius: 8,
                    },
                  }}
                >
                  <CardContent sx={{ p: 4 }}>
                    <Box sx={{ textAlign: 'center', mb: 3 }}>
                      <Box
                        sx={{
                          color: platform.hoverColor,
                          mb: 2,
                        }}
                      >
                        {platform.icon}
                      </Box>
                      <Typography
                        variant="h4"
                        component="h2"
                        fontWeight="bold"
                        color="text.primary"
                        gutterBottom
                      >
                        {platform.title}
                      </Typography>
                      <Typography
                        variant="body1"
                        color="text.secondary"
                        paragraph
                      >
                        {platform.description}
                      </Typography>
                    </Box>

                    <List sx={{ mb: 2 }}>
                      {platform.features.map((feature, idx) => (
                        <ListItem key={idx} sx={{ px: 0, py: 0.5 }}>
                          <ListItemIcon sx={{ minWidth: 32 }}>
                            <CheckCircle
                              sx={{
                                color: platform.hoverColor,
                                fontSize: 20,
                              }}
                            />
                          </ListItemIcon>
                          <ListItemText
                            primary={feature}
                            primaryTypographyProps={{
                              variant: 'body2',
                              color: 'text.secondary',
                            }}
                          />
                        </ListItem>
                      ))}
                    </List>

                    <Button
                      component={RouterLink}
                      to={
                        platform.id === 'patient'
                          ? '/login'
                          : platform.id === 'doctor'
                          ? '/doctor-login'
                          : '/admin-login'
                      }
                      fullWidth
                      variant="contained"
                      size="large"
                      endIcon={<ArrowForward />}
                      sx={{
                        py: 1.5,
                        background: platform.gradient,
                        '&:hover': {
                          background: platform.hoverColor,
                          transform: 'scale(1.02)',
                        },
                      }}
                    >
                      登录
                    </Button>

                    {platform.id === 'patient' && (
                      <Button
                        component={RouterLink}
                        to="/register"
                        fullWidth
                        variant="text"
                        size="small"
                        sx={{ mt: 1 }}
                      >
                        注册患者账号
                      </Button>
                    )}

                    {platform.id === 'doctor' && (
                      <Button
                        component={RouterLink}
                        to="/doctor-register"
                        fullWidth
                        variant="text"
                        size="small"
                        sx={{ mt: 1 }}
                      >
                        注册医生账号
                      </Button>
                    )}
                  </CardContent>
                </Card>
              </Fade>
            </Grid>
          ))}
        </Grid>

        <Paper
          elevation={0}
          sx={{
            mt: 4,
            py: 4,
            background: 'rgba(255, 255, 255, 0.1)',
            backdropFilter: 'blur(10px)',
            textAlign: 'center',
          }}
        >
          <Typography variant="body2" color="rgba(255, 255, 255, 0.8)">
            MediCareAI © 2025 | 作者：苏业钦 | MIT License
          </Typography>
          <Typography
            variant="body2"
            color="rgba(255, 255, 255, 0.8)"
            sx={{ mt: 1 }}
          >
            🏥 用AI赋能医疗健康，让诊疗更智能、更便捷
          </Typography>
        </Paper>
      </Container>
    </Box>
  );
};

export default PlatformSelect;