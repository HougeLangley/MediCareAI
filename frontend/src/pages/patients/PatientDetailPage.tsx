import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Box,
  Button,
  Card,
  CardContent,
  Grid,
  CircularProgress,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Tabs,
  Tab,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemSecondaryAction,
  Chip,
  IconButton,
  Divider,
  Paper,
  TextField,
} from '@mui/material';
import {
  ArrowBack as ArrowBackIcon,
  Description as DocumentIcon,
  SmartToy as AIIcon,
  EventNote as CaseIcon,
  Upload as UploadIcon,
  Delete as DeleteIcon,
  Visibility as ViewIcon,
} from '@mui/icons-material';
import apiService from '../../services/api';
import { Patient, MedicalCase, MedicalDocument } from '../../types';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div role="tabpanel" hidden={value !== index} {...other}>
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );
}

const PatientDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [patient, setPatient] = useState<Patient | null>(null);
  const [medicalCases, setMedicalCases] = useState<MedicalCase[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [tabValue, setTabValue] = useState(0);
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [aiFeedbackOpen, setAiFeedbackOpen] = useState(false);
  const [selectedCase, setSelectedCase] = useState<MedicalCase | null>(null);
  const [aiResponse, setAiResponse] = useState<any>(null);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' as 'success' | 'error' });

  useEffect(() => {
    if (id) {
      fetchPatientData();
    }
  }, [id]);

  const fetchPatientData = async () => {
    try {
      setLoading(true);
      setError(null);
      if (id) {
        const patientData = await apiService.getPatient(id);
        setPatient(patientData);
        // TODO: 获取病例列表
        setMedicalCases([]);
      }
    } catch (err: any) {
      setError(err.detail || '获取患者信息失败');
    } finally {
      setLoading(false);
    }
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleUploadClick = (medicalCase: MedicalCase) => {
    setSelectedCase(medicalCase);
    setUploadDialogOpen(true);
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      setSelectedFile(event.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile || !selectedCase) return;

    try {
      setUploading(true);
      await apiService.uploadDocument(selectedCase.id, selectedFile);
      setSnackbar({ open: true, message: '文档上传成功', severity: 'success' });
      setUploadDialogOpen(false);
      setSelectedFile(null);
      // 刷新数据
      fetchPatientData();
    } catch (err: any) {
      setSnackbar({ open: true, message: err.detail || '上传失败', severity: 'error' });
    } finally {
      setUploading(false);
    }
  };

  const handleAIFeedback = async (medicalCase: MedicalCase) => {
    try {
      setSelectedCase(medicalCase);
      setAiFeedbackOpen(true);
      setAiResponse(null);

      // 调用AI诊断接口
      const response = await apiService.getAIDiagnosis({
        patient_info: {
          name: patient?.name,
          date_of_birth: patient?.date_of_birth,
          gender: patient?.gender,
        },
        symptoms: medicalCase.symptoms,
        clinical_findings: medicalCase.clinical_findings,
        diagnosis: medicalCase.diagnosis,
        documents_content: [],
        disease_guidelines: {},
      });

      setAiResponse(response);
    } catch (err: any) {
      setSnackbar({ open: true, message: err.detail || '获取AI反馈失败', severity: 'error' });
      setAiFeedbackOpen(false);
    }
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

  if (!patient) {
    return (
      <Container maxWidth="lg">
        <Alert severity="error" sx={{ mt: 4 }}>
          {error || '患者不存在'}
        </Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 4, mb: 6 }}>
        <Button
          startIcon={<ArrowBackIcon />}
          onClick={() => navigate('/patients')}
          sx={{ mb: 2 }}
        >
          返回患者列表
        </Button>

        <Typography variant="h4" gutterBottom fontWeight="bold">
          {patient.name}
        </Typography>
        <Typography variant="body1" color="textSecondary">
          病历号：{patient.medical_record_number || '未设置'}
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* 患者基本信息卡片 */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom fontWeight="bold">
                基本信息
              </Typography>
              <Grid container spacing={2} sx={{ mt: 1 }}>
                <Grid item xs={6}>
                  <Typography variant="caption" color="textSecondary">
                    性别
                  </Typography>
                  <Typography variant="body1">
                    {patient.gender === 'male' ? '男' : patient.gender === 'female' ? '女' : '其他'}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="caption" color="textSecondary">
                    出生日期
                  </Typography>
                  <Typography variant="body1">{patient.date_of_birth}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="caption" color="textSecondary">
                    联系电话
                  </Typography>
                  <Typography variant="body1">{patient.phone || '未设置'}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="caption" color="textSecondary">
                    紧急联系人
                  </Typography>
                  <Typography variant="body1">{patient.emergency_contact || '未设置'}</Typography>
                </Grid>
                <Grid item xs={12}>
                  <Typography variant="caption" color="textSecondary">
                    地址
                  </Typography>
                  <Typography variant="body1">{patient.address || '未设置'}</Typography>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom fontWeight="bold">
                统计信息
              </Typography>
              <Box sx={{ mt: 2, display: 'grid', gap: 2 }}>
                <Box>
                  <Typography variant="caption" color="textSecondary">
                    病例数量
                  </Typography>
                  <Typography variant="h4" color="primary.main">
                    {medicalCases.length}
                  </Typography>
                </Box>
                <Box>
                  <Typography variant="caption" color="textSecondary">
                    文档数量
                  </Typography>
                  <Typography variant="h4" color="secondary.main">
                    0
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* 病例管理 */}
      <Box sx={{ mt: 4 }}>
        <Typography variant="h5" gutterBottom fontWeight="bold">
          病例管理
        </Typography>

        <Paper sx={{ mt: 2 }}>
          <Tabs value={tabValue} onChange={handleTabChange} indicatorColor="primary" textColor="primary">
            <Tab label="病例列表" />
            <Tab label="AI 辅助诊断" />
          </Tabs>

          <TabPanel value={tabValue} index={0}>
            {medicalCases.length === 0 ? (
              <Box sx={{ textAlign: 'center', py: 8 }}>
                <CaseIcon sx={{ fontSize: 64, color: 'text.disabled', mb: 2 }} />
                <Typography variant="h6" color="textSecondary">
                  暂无病例
                </Typography>
                <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
                  为该患者创建第一个病例记录
                </Typography>
              </Box>
            ) : (
              <List>
                {medicalCases.map((medicalCase, index) => (
                  <React.Fragment key={medicalCase.id}>
                    <ListItem>
                      <ListItemIcon>
                        <DescriptionIcon />
                      </ListItemIcon>
                      <ListItemText
                        primary={medicalCase.title}
                        secondary={medicalCase.diagnosis || '未诊断'}
                      />
                      <ListItemIcon>
                        <Chip
                          label={medicalCase.status || 'active'}
                          size="small"
                          color={medicalCase.status === 'active' ? 'primary' : 'default'}
                        />
                      </ListItemIcon>
                      <ListItemSecondaryAction>
                        <IconButton
                          edge="end"
                          onClick={() => handleUploadClick(medicalCase)}
                          title="上传文档"
                        >
                          <UploadIcon />
                        </IconButton>
                        <IconButton
                          edge="end"
                          onClick={() => handleAIFeedback(medicalCase)}
                          title="AI 辅助诊断"
                        >
                          <AIIcon />
                        </IconButton>
                      </ListItemSecondaryAction>
                    </ListItem>
                    {index < medicalCases.length - 1 && <Divider />}
                  </React.Fragment>
                ))}
              </List>
            )}
          </TabPanel>

          <TabPanel value={tabValue} index={1}>
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <AIIcon sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
              <Typography variant="h6" gutterBottom>
                AI 辅助诊断功能
              </Typography>
              <Typography variant="body2" color="textSecondary" sx={{ mb: 3 }}>
                选择一个病例，系统将基于患者信息和诊疗指南提供智能诊断建议
              </Typography>
            </Box>
          </TabPanel>
        </Paper>
      </Box>

      {/* 文档上传对话框 */}
      <Dialog open={uploadDialogOpen} onClose={() => setUploadDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>上传文档</DialogTitle>
        <DialogContent>
          <TextField
            type="file"
            fullWidth
            onChange={handleFileChange}
            disabled={uploading}
            helperText="支持 PDF、DOC、DOCX、PPT、PPTX、图片等格式，最大 200MB"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setUploadDialogOpen(false)} disabled={uploading}>
            取消
          </Button>
          <Button
            onClick={handleUpload}
            variant="contained"
            disabled={!selectedFile || uploading}
            startIcon={uploading && <CircularProgress size={20} />}
          >
            {uploading ? '上传中...' : '上传'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* AI 反馈对话框 */}
      <Dialog open={aiFeedbackOpen} onClose={() => setAiFeedbackOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>AI 辅助诊断结果</DialogTitle>
        <DialogContent>
          {aiResponse ? (
            <Box sx={{ mt: 2 }}>
              <Typography variant="h6" gutterBottom>
                诊断建议
              </Typography>
              <Typography variant="body1" paragraph>
                {aiResponse.response || '暂无建议'}
              </Typography>

              {aiResponse.reasoning && (
                <Box sx={{ mt: 2, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    诊断推理
                  </Typography>
                  <Typography variant="body2">{aiResponse.reasoning}</Typography>
                </Box>
              )}

              {aiResponse.recommendations && aiResponse.recommendations.length > 0 && (
                <Box sx={{ mt: 2 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    建议
                  </Typography>
                  <List dense>
                    {aiResponse.recommendations.map((rec: string, idx: number) => (
                      <ListItem key={idx}>
                        <ListItemText primary={`${idx + 1}. ${rec}`} />
                      </ListItem>
                    ))}
                  </List>
                </Box>
              )}

              {aiResponse.warnings && aiResponse.warnings.length > 0 && (
                <Alert severity="warning" sx={{ mt: 2 }}>
                  <Typography variant="subtitle2">警示信息</Typography>
                  <List dense>
                    {aiResponse.warnings.map((warn: string, idx: number) => (
                      <ListItem key={idx}>
                        <ListItemText primary={warn} />
                      </ListItem>
                    ))}
                  </List>
                </Alert>
              )}
            </Box>
          ) : (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
              <CircularProgress />
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAiFeedbackOpen(false)}>关闭</Button>
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

export default PatientDetailPage;
