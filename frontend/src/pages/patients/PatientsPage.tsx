import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Box,
  Button,
  TextField,
  Grid,
  Card,
  CardContent,
  CircularProgress,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Snackbar,
} from '@mui/material';
import { Add as AddIcon, Search as SearchIcon, Edit as EditIcon, Delete as DeleteIcon, Visibility as ViewIcon } from '@mui/icons-material';
import apiService from '../../services/api';
import { Patient } from '../../types';

const PatientsPage: React.FC = () => {
  const navigate = useNavigate();
  const [patients, setPatients] = useState<Patient[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [selectedPatient, setSelectedPatient] = useState<Patient | null>(null);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' as 'success' | 'error' });

  useEffect(() => {
    fetchPatients();
  }, []);

  const fetchPatients = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await apiService.getPatients(0, 100);
      setPatients(data);
    } catch (err: any) {
      setError(err.detail || '获取患者列表失败');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(event.target.value);
  };

  const filteredPatients = patients.filter((patient) =>
    patient.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    patient.medical_record_number?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    patient.phone?.includes(searchTerm)
  );

  const handleDeleteClick = (patient: Patient) => {
    setSelectedPatient(patient);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!selectedPatient) return;

    try {
      await apiService.deletePatient(selectedPatient.id);
      setSnackbar({ open: true, message: '患者删除成功', severity: 'success' });
      setDeleteDialogOpen(false);
      fetchPatients();
    } catch (err: any) {
      setSnackbar({ open: true, message: err.detail || '删除失败', severity: 'error' });
    }
  };

  const handleCreatePatient = () => {
    navigate('/patients/new');
  };

  const handleViewPatient = (patientId: string) => {
    navigate(`/patients/${patientId}`);
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

  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 4, mb: 6 }}>
        <Typography variant="h4" gutterBottom fontWeight="bold">
          患者管理
        </Typography>
        <Typography variant="body1" color="textSecondary">
          管理您的患者信息，创建、编辑和查看患者档案
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      <Box sx={{ mb: 4, display: 'flex', gap: 2, flexWrap: 'wrap' }}>
        <TextField
          fullWidth
          variant="outlined"
          placeholder="搜索患者姓名、病历号或电话..."
          value={searchTerm}
          onChange={handleSearch}
          InputProps={{
            startAdornment: <SearchIcon sx={{ mr: 1, color: 'text.secondary' }} />,
          }}
          sx={{ maxWidth: 500, flexGrow: 1 }}
        />
        <Button
          variant="contained"
          size="large"
          startIcon={<AddIcon />}
          onClick={handleCreatePatient}
          sx={{
            textTransform: 'none',
            fontWeight: 600,
            px: 3,
          }}
        >
          添加新患者
        </Button>
      </Box>

      {filteredPatients.length === 0 ? (
        <Box sx={{ textAlign: 'center', py: 8, bgcolor: 'action.hover', borderRadius: 2 }}>
          <Typography variant="h6" color="textSecondary" gutterBottom>
            {searchTerm ? '未找到匹配的患者' : '暂无患者'}
          </Typography>
          <Typography variant="body2" color="textSecondary">
            {searchTerm ? '请尝试其他搜索关键词' : '点击上方按钮添加您的第一位患者'}
          </Typography>
        </Box>
      ) : (
        <Grid container spacing={3}>
          {filteredPatients.map((patient) => (
            <Grid item xs={12} md={6} key={patient.id}>
              <Card
                sx={{
                  height: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                  transition: 'transform 0.2s, box-shadow 0.2s',
                  '&:hover': {
                    transform: 'translateY(-2px)',
                    boxShadow: 4,
                  },
                }}
              >
                <CardContent sx={{ flexGrow: 1 }}>
                  <Typography variant="h6" gutterBottom fontWeight="bold">
                    {patient.name}
                  </Typography>

                  <Box sx={{ mt: 2, display: 'grid', gap: 1.5 }}>
                    {patient.medical_record_number && (
                      <Box>
                        <Typography variant="caption" color="textSecondary">
                          病历号
                        </Typography>
                        <Typography variant="body2">{patient.medical_record_number}</Typography>
                      </Box>
                    )}

                    <Box>
                      <Typography variant="caption" color="textSecondary">
                        性别
                      </Typography>
                      <Typography variant="body2">
                        {patient.gender === 'male' ? '男' : patient.gender === 'female' ? '女' : '其他'}
                      </Typography>
                    </Box>

                    {patient.date_of_birth && (
                      <Box>
                        <Typography variant="caption" color="textSecondary">
                          出生日期
                        </Typography>
                        <Typography variant="body2">{patient.date_of_birth}</Typography>
                      </Box>
                    )}

                    {patient.phone && (
                      <Box>
                        <Typography variant="caption" color="textSecondary">
                          联系电话
                        </Typography>
                        <Typography variant="body2">{patient.phone}</Typography>
                      </Box>
                    )}
                  </Box>

                  <Typography variant="caption" color="textSecondary" sx={{ mt: 2, display: 'block' }}>
                    创建时间：{new Date(patient.created_at).toLocaleDateString('zh-CN')}
                  </Typography>
                </CardContent>

                <Box sx={{ p: 2, pt: 0, display: 'flex', gap: 1, justifyContent: 'flex-end' }}>
                  <Button
                    size="small"
                    startIcon={<ViewIcon />}
                    onClick={() => handleViewPatient(patient.id)}
                  >
                    查看
                  </Button>
                  <Button
                    size="small"
                    color="error"
                    startIcon={<DeleteIcon />}
                    onClick={() => handleDeleteClick(patient)}
                  >
                    删除
                  </Button>
                </Box>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {/* 删除确认对话框 */}
      <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)}>
        <DialogTitle>确认删除患者</DialogTitle>
        <DialogContent>
          <Typography>
            您确定要删除患者 <strong>{selectedPatient?.name}</strong> 吗？
            <br />
            <Typography variant="caption" color="error" sx={{ mt: 1, display: 'block' }}>
              此操作将同时删除该患者的所有病例和相关数据，且无法恢复。
            </Typography>
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>取消</Button>
          <Button onClick={handleDeleteConfirm} color="error" variant="contained">
            确认删除
          </Button>
        </DialogActions>
      </Dialog>

      {/* 提示消息 */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <Alert
          onClose={() => setSnackbar({ ...snackbar, open: false })}
          severity={snackbar.severity}
          sx={{ width: '100%' }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Container>
  );
};

export default PatientsPage;
