import React, { useEffect, useState } from 'react';
import {
  Container,
  Typography,
  Box,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  Chip,
  CircularProgress,
  Alert,
} from '@mui/material';
import { MedicalServices as MedicalIcon, People as PeopleIcon } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import apiService from '../../services/api';

interface DiseaseCard {
  id: string;
  name: string;
  code?: string;
  description?: string;
  patient_count: number;
  is_active: boolean;
}

const DashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const [diseases, setDiseases] = useState<DiseaseCard[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchDiseases();
  }, []);

  const fetchDiseases = async () => {
    try {
      setLoading(true);
      setError(null);

      // 获取患者数量
      const countResponse = await apiService.getPatientsCount();
      const patientCount = countResponse.count;

      // 模拟疾病数据（当前只有儿童哮喘）
      const diseaseData: DiseaseCard[] = [
        {
          id: 'bronchial-asthma',
          name: '儿童支气管哮喘',
          code: 'BA',
          description: '儿童期最常见的慢性呼吸系统疾病，以慢性气道炎症和气道高反应性为特征的异质性疾病。',
          patient_count: patientCount,
          is_active: true,
        },
      ];

      setDiseases(diseaseData);
    } catch (err: any) {
      setError(err.detail || '获取疾病数据失败');
    } finally {
      setLoading(false);
    }
  };

  const handleManageDisease = (diseaseId: string) => {
    // 跳转到患者管理页面
    navigate('/patients');
  };

  if (loading) {
    return (
      <Container maxWidth="lg">
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', mt: 8 }}>
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="lg">
        <Alert severity="error" sx={{ mt: 4 }}>
          {error}
        </Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 4, mb: 6 }}>
        <Typography variant="h3" gutterBottom fontWeight="bold">
          MediCare AI
        </Typography>
        <Typography variant="h5" color="textSecondary" gutterBottom>
          智能疾病管理系统
        </Typography>
        <Typography variant="body1" sx={{ mt: 2, color: 'text.secondary' }}>
          欢迎使用 MediCare AI 智能疾病管理系统！请选择您要管理的疾病类型。
        </Typography>
      </Box>

      <Typography variant="h5" gutterBottom sx={{ mt: 4, mb: 3, fontWeight: 600 }}>
        可管理的疾病
      </Typography>

      <Grid container spacing={3}>
        {diseases.map((disease) => (
          <Grid item xs={12} md={6} key={disease.id}>
            <Card
              sx={{
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                transition: 'transform 0.2s, box-shadow 0.2s',
                '&:hover': {
                  transform: 'translateY(-4px)',
                  boxShadow: 6,
                },
              }}
            >
              <CardContent sx={{ flexGrow: 1 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <MedicalIcon sx={{ fontSize: 40, color: 'primary.main', mr: 2 }} />
                  <Box>
                    <Typography variant="h5" component="h2" fontWeight="bold">
                      {disease.name}
                    </Typography>
                    {disease.code && (
                      <Chip
                        label={disease.code}
                        size="small"
                        variant="outlined"
                        sx={{ mt: 0.5 }}
                      />
                    )}
                  </Box>
                </Box>

                <Typography variant="body2" color="textSecondary" paragraph>
                  {disease.description || '暂无描述'}
                </Typography>

                <Box
                  sx={{
                    display: 'flex',
                    alignItems: 'center',
                    mt: 2,
                    p: 2,
                    bgcolor: 'action.hover',
                    borderRadius: 1,
                  }}
                >
                  <PeopleIcon sx={{ mr: 1, color: 'text.secondary' }} />
                  <Typography variant="body2" color="textSecondary">
                    已管理患者：<strong>{disease.patient_count}</strong> 人
                  </Typography>
                </Box>
              </CardContent>

              <CardActions sx={{ p: 2, pt: 0 }}>
                <Button
                  variant="contained"
                  size="large"
                  fullWidth
                  onClick={() => handleManageDisease(disease.id)}
                  sx={{
                    textTransform: 'none',
                    fontWeight: 600,
                    py: 1.5,
                  }}
                >
                  进入管理
                </Button>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>

      {diseases.length === 0 && (
        <Box sx={{ textAlign: 'center', mt: 8, py: 8, bgcolor: 'action.hover', borderRadius: 2 }}>
          <MedicalIcon sx={{ fontSize: 64, color: 'text.disabled', mb: 2 }} />
          <Typography variant="h6" color="textSecondary">
            暂无可用疾病
          </Typography>
          <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
            系统正在更新中，请稍后再试
          </Typography>
        </Box>
      )}
    </Container>
  );
};

export default DashboardPage;
