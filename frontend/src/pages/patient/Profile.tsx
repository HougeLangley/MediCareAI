import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Container,
  Paper,
  Typography,
  TextField,
  Button,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Checkbox,
  FormControlLabel,
  Alert,
  CircularProgress,
  Avatar,
  AppBar,
  Toolbar,
  IconButton,
  Chip,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Divider,
} from '@mui/material';
import {
  Save as SaveIcon,
  Refresh as RefreshIcon,
  Cancel as CancelIcon,
  LocalHospital as HospitalIcon,
  Description as DescriptionIcon,
  Person as PersonIcon,
  Logout as LogoutIcon,
  EditNote as EditNoteIcon,
  Home as HomeIcon,
  Delete as DeleteIcon,
  Add as AddIcon,
} from '@mui/icons-material';
import { useAuth } from '../../hooks/useAuth';
import { patientsApi, chronicDiseasesApi } from '../../services/api';
import type { Patient, PatientChronicCondition, ChronicDisease, PatientCreate } from '../../types';

const Profile: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  // Form state
  const [email, setEmail] = useState('');
  const [fullName, setFullName] = useState('');
  const [dateOfBirth, setDateOfBirth] = useState('');
  const [gender, setGender] = useState('');
  const [phone, setPhone] = useState('');
  const [emergencyContactName, setEmergencyContactName] = useState('');
  const [emergencyContactPhone, setEmergencyContactPhone] = useState('');
  const [address, setAddress] = useState('');
  const [notes, setNotes] = useState('');

  // Chronic diseases state
  const [availableDiseases, setAvailableDiseases] = useState<ChronicDisease[]>([]);
  const [selectedDiseases, setSelectedDiseases] = useState<PatientChronicCondition[]>([]);
  const [diseaseId, setDiseaseId] = useState('');
  const [diseaseSeverity, setDiseaseSeverity] = useState('');
  const [diagnosisDate, setDiagnosisDate] = useState('');
  const [diseaseNotes, setDiseaseNotes] = useState('');

  // UI state
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  useEffect(() => {
    loadUserProfile();
    loadDiseaseOptions();
    loadChronicDiseases();
  }, []);

  const handleLogout = () => {
    if (window.confirm('确定要退出登录吗？')) {
      logout();
    }
  };

  const loadUserProfile = async () => {
    try {
      setLoading(true);
      
      // Load user information
      if (user) {
        setEmail(user.email);
        setFullName(user.full_name || '');
      }
      
      // Load patient information
      const patientData = await patientsApi.getMe();
      
      if (patientData.date_of_birth) setDateOfBirth(patientData.date_of_birth);
      if (patientData.gender) setGender(patientData.gender);
      if (patientData.phone) setPhone(patientData.phone);
      
      // Parse emergency contact
      if (patientData.emergency_contact) {
        const parts = patientData.emergency_contact.split(' ');
        if (parts.length >= 1) setEmergencyContactName(parts[0]);
        if (parts.length >= 2) setEmergencyContactPhone(parts[1]);
      }
      
      if (patientData.address) setAddress(patientData.address);
    } catch (err) {
      console.error('加载用户信息失败:', err);
      setError('加载用户信息失败');
    } finally {
      setLoading(false);
    }
  };

  const loadDiseaseOptions = async () => {
    try {
      const response = await chronicDiseasesApi.getAll();
      const diseases = response.items || response;
      setAvailableDiseases(Array.isArray(diseases) ? diseases : []);
    } catch (err) {
      console.error('加载疾病列表失败:', err);
      setAvailableDiseases([]);
    }
  };

  const loadChronicDiseases = async () => {
    try {
      const response = await patientsApi.getChronicDiseases();
      const diseases = response.items || response;
      setSelectedDiseases(Array.isArray(diseases) ? diseases : []);
    } catch (err) {
      console.error('加载患者慢性病失败:', err);
      setSelectedDiseases([]);
    }
  };

  const handleReset = () => {
    if (window.confirm('确定要重置所有表单内容吗？未保存的更改将丢失。')) {
      loadUserProfile();
      setSuccess('表单已重置');
      setTimeout(() => setSuccess(null), 3000);
    }
  };

  const handleSave = async () => {
    if (!fullName.trim()) {
      setError('姓名不能为空');
      return;
    }

    setSaving(true);
    setError(null);
    setSuccess(null);

    try {
      // Update user information
      await patientsApi.updateMe({
        full_name: fullName,
      });

      // Update patient information
      const emergencyContact = `${emergencyContactName} ${emergencyContactPhone}`.trim();
      
      const patientData: PatientCreate = {
        date_of_birth: dateOfBirth || undefined,
        gender: gender || undefined,
        phone: phone || undefined,
        emergency_contact: emergencyContact || undefined,
        address: address || undefined,
        notes: notes || undefined,
      };

      try {
        await patientsApi.updateMe(patientData);
      } catch (updateError) {
        // If patient record doesn't exist, try to create
        if (updateError instanceof Error && updateError.message.includes('404')) {
          await patientsApi.create(patientData);
        } else {
          throw updateError;
        }
      }

      setSuccess('个人信息保存成功！2秒后自动返回主页...');
      setTimeout(() => {
        navigate('/patient');
      }, 2000);
    } catch (err) {
      console.error('保存失败:', err);
      setError('保存失败：' + (err instanceof Error ? err.message : '未知错误'));
    } finally {
      setSaving(false);
    }
  };

  const addChronicDisease = async () => {
    if (!diseaseId) {
      setError('请选择疾病');
      return;
    }

    try {
      await patientsApi.addChronicDisease({
        disease_id: diseaseId,
        diagnosis_date: diagnosisDate || undefined,
        severity: diseaseSeverity || undefined,
        notes: diseaseNotes || undefined,
      });

      // Clear form
      setDiseaseId('');
      setDiseaseSeverity('');
      setDiagnosisDate('');
      setDiseaseNotes('');

      // Reload list
      loadChronicDiseases();
      setSuccess('疾病添加成功');
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      console.error('添加疾病失败:', err);
      setError('添加失败：' + (err instanceof Error ? err.message : '未知错误'));
    }
  };

  const removeChronicDisease = async (conditionId: string) => {
    if (!window.confirm('确定要删除这条疾病记录吗？')) {
      return;
    }

    try {
      await patientsApi.deleteChronicDisease(conditionId);
      loadChronicDiseases();
      setSuccess('疾病记录已删除');
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      console.error('删除疾病失败:', err);
      setError('删除失败');
    }
  };

  const getSeverityLabel = (severity?: string) => {
    const labels: { [key: string]: string } = {
      'mild': '轻度',
      'moderate': '中度',
      'severe': '重度',
    };
    return labels[severity || ''] || severity;
  };

  const getDiseaseTypeColor = (type?: string) => {
    switch (type) {
      case 'special':
        return '#fff3cd';
      case 'chronic':
        return '#d1ecf1';
      case 'both':
        return '#f8d7da';
      default:
        return '#f8f9fa';
    }
  };

  const getDiseaseTypeLabel = (type?: string) => {
    switch (type) {
      case 'special':
        return '特殊病';
      case 'chronic':
        return '慢性病';
      case 'both':
        return '特殊病+慢性病';
      default:
        return type;
    }
  };

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: '#f5f5f5' }}>
      {/* Header */}
      <AppBar position="static" elevation={4}>
        <Toolbar sx={{ backgroundColor: 'white', color: '#333' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', flexGrow: 1 }}>
            <HospitalIcon sx={{ fontSize: 32, mr: 2, color: '#667eea' }} />
            <Typography variant="h5" component="div" sx={{ fontWeight: 'bold', color: '#667eea' }}>
              MediCareAI
            </Typography>
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Avatar sx={{ bgcolor: '#667eea' }}>
              {user?.full_name?.charAt(0) || '患'}
            </Avatar>
            <Typography variant="body1">
              {user?.full_name || '欢迎您'}
            </Typography>
          </Box>
        </Toolbar>
      </AppBar>

      {/* Navigation */}
      <Container maxWidth="lg" sx={{ mt: 2 }}>
        <Paper elevation={2} sx={{ p: 2, mb: 3, borderRadius: 3 }}>
          <Box sx={{ display: 'flex', justifyContent: 'center', gap: 2 }}>
            <Button
              startIcon={<HomeIcon />}
              onClick={() => navigate('/patient')}
              sx={{ borderRadius: 2 }}
            >
              首页
            </Button>
            <Button
              startIcon={<PersonIcon />}
              onClick={() => navigate('/patient/profile')}
              variant="contained"
              sx={{ borderRadius: 2 }}
            >
              个人中心
            </Button>
            <Button
              startIcon={<EditNoteIcon />}
              onClick={() => navigate('/patient/symptom-submit')}
              sx={{ borderRadius: 2 }}
            >
              症状提交
            </Button>
            <Button
              startIcon={<DescriptionIcon />}
              onClick={() => navigate('/patient/medical-records')}
              sx={{ borderRadius: 2 }}
            >
              诊疗记录
            </Button>
            <Button
              startIcon={<LogoutIcon />}
              onClick={handleLogout}
              color="error"
              sx={{ borderRadius: 2 }}
            >
              退出登录
            </Button>
          </Box>
        </Paper>
      </Container>

      <Container maxWidth="lg">
        {/* Loading State */}
        {loading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', my: 5 }}>
            <CircularProgress />
          </Box>
        )}

        {!loading && (
          <>
            {/* Account Information */}
            <Paper elevation={3} sx={{ p: 4, mb: 3, borderRadius: 3 }}>
              <Typography variant="h5" gutterBottom>
                账户信息
              </Typography>
              
              <Alert severity="info" sx={{ mb: 3 }}>
                以下信息用于登录和系统识别，邮箱地址不可修改。
              </Alert>

              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="邮箱地址"
                    value={email}
                    disabled
                    helperText="邮箱地址用于登录，无法修改"
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="姓名"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    required
                  />
                </Grid>
              </Grid>
            </Paper>

            {/* Basic Information */}
            <Paper elevation={3} sx={{ p: 4, mb: 3, borderRadius: 3 }}>
              <Typography variant="h5" gutterBottom>
                基本信息
              </Typography>
              
              <Alert severity="info" sx={{ mb: 3 }}>
                请填写您的基本个人信息，这将帮助系统更好地为您服务。
              </Alert>

              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    type="date"
                    label="出生日期"
                    value={dateOfBirth}
                    onChange={(e) => setDateOfBirth(e.target.value)}
                    InputLabelProps={{ shrink: true }}
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <FormControl fullWidth>
                    <InputLabel>性别</InputLabel>
                    <Select
                      value={gender}
                      onChange={(e) => setGender(e.target.value)}
                      label="性别"
                    >
                      <MenuItem value="">请选择</MenuItem>
                      <MenuItem value="male">男</MenuItem>
                      <MenuItem value="female">女</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="手机号码"
                    value={phone}
                    onChange={(e) => setPhone(e.target.value)}
                  />
                </Grid>
              </Grid>
            </Paper>

            {/* Emergency Contact */}
            <Paper elevation={3} sx={{ p: 4, mb: 3, borderRadius: 3 }}>
              <Typography variant="h5" gutterBottom>
                紧急联系人
              </Typography>
              
              <Alert severity="info" sx={{ mb: 3 }}>
                请填写紧急联系人信息，在紧急情况下我们会联系此人。
              </Alert>

              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="紧急联系人姓名"
                    value={emergencyContactName}
                    onChange={(e) => setEmergencyContactName(e.target.value)}
                  />
                </Grid>
                <Grid item xs={12} md={6}>
                  <TextField
                    fullWidth
                    label="紧急联系人电话"
                    value={emergencyContactPhone}
                    onChange={(e) => setEmergencyContactPhone(e.target.value)}
                  />
                </Grid>
              </Grid>
            </Paper>

            {/* Notes */}
            <Paper elevation={3} sx={{ p: 4, mb: 3, borderRadius: 3 }}>
              <Typography variant="h5" gutterBottom>
                备注信息
              </Typography>
              
              <Alert severity="info" sx={{ mb: 3 }}>
                您可以在这里记录其他需要告知医生的重要信息。
              </Alert>

              <TextField
                fullWidth
                multiline
                rows={4}
                label="其他备注"
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="请描述其他需要记录的信息，如过敏史、既往病史、当前用药等"
              />
            </Paper>

            {/* Address */}
            <Paper elevation={3} sx={{ p: 4, mb: 3, borderRadius: 3 }}>
              <Typography variant="h5" gutterBottom>
                地址信息
              </Typography>

              <TextField
                fullWidth
                multiline
                rows={3}
                label="居住地址"
                value={address}
                onChange={(e) => setAddress(e.target.value)}
                placeholder="请输入您的详细居住地址"
              />
            </Paper>

            {/* Chronic Diseases */}
            <Paper elevation={3} sx={{ p: 4, mb: 3, borderRadius: 3 }}>
              <Typography variant="h5" gutterBottom>
                特殊病与慢性病管理
              </Typography>
              
              <Alert severity="warning" sx={{ mb: 3 }}>
                <strong>重要提示：</strong>如果您患有特殊病或慢性病，请务必如实填写。这将帮助AI在诊断时考虑您的病史，避免药物相互作用等风险。
              </Alert>

              {/* Selected Diseases */}
              <Box sx={{ mb: 3 }}>
                <Typography variant="h6" gutterBottom>
                  我的特殊病/慢性病
                </Typography>
                {selectedDiseases.length === 0 ? (
                  <Typography variant="body2" color="text.secondary" sx={{ p: 2, fontStyle: 'italic' }}>
                    暂无记录，请从下方选择添加
                  </Typography>
                ) : (
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, p: 1, minHeight: 50 }}>
                    {selectedDiseases.map((condition) => {
                      const disease = condition.disease;
                      const diseaseName = disease?.common_names && disease.common_names.length > 0
                        ? disease.common_names[0]
                        : disease?.icd10_name || '未知疾病';
                      const diseaseType = disease?.disease_type || 'unknown';
                      return (
                        <Chip
                          key={condition.id}
                          label={
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              <span>{diseaseName}</span>
                              <span style={{ fontSize: '12px', opacity: 0.8 }}>
                                ({getDiseaseTypeLabel(diseaseType)}
                                {condition.severity ? ` - ${getSeverityLabel(condition.severity)}` : ''})
                              </span>
                            </Box>
                          }
                          sx={{
                            bgcolor: getDiseaseTypeColor(diseaseType),
                            color: diseaseType === 'special' ? '#856404' :
                                   diseaseType === 'chronic' ? '#0c5460' : '#721c24',
                          }}
                          onDelete={() => removeChronicDisease(condition.id)}
                          deleteIcon={<DeleteIcon />}
                        />
                      );
                    })}
                  </Box>
                )}
              </Box>

              {/* Add Disease Form */}
              <Box sx={{ mb: 3 }}>
                <Typography variant="h6" gutterBottom>
                  添加疾病
                </Typography>
                <Grid container spacing={3}>
                  <Grid item xs={12} md={6}>
                    <FormControl fullWidth>
                      <InputLabel>选择疾病</InputLabel>
                      <Select
                        value={diseaseId}
                        onChange={(e) => setDiseaseId(e.target.value)}
                        label="选择疾病"
                      >
                        <MenuItem value="">请选择疾病...</MenuItem>
                        {availableDiseases.map((disease) => (
                          <MenuItem key={disease.id} value={disease.id}>
                            {disease.common_names && disease.common_names.length > 0
                              ? disease.common_names[0]
                              : disease.icd10_name}
                            {' '}({disease.icd10_code})
                          </MenuItem>
                        ))}
                      </Select>
                    </FormControl>
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <FormControl fullWidth>
                      <InputLabel>严重程度</InputLabel>
                      <Select
                        value={diseaseSeverity}
                        onChange={(e) => setDiseaseSeverity(e.target.value)}
                        label="严重程度"
                      >
                        <MenuItem value="">请选择</MenuItem>
                        <MenuItem value="mild">轻度</MenuItem>
                        <MenuItem value="moderate">中度</MenuItem>
                        <MenuItem value="severe">重度</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      type="date"
                      label="确诊日期"
                      value={diagnosisDate}
                      onChange={(e) => setDiagnosisDate(e.target.value)}
                      InputLabelProps={{ shrink: true }}
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      multiline
                      rows={3}
                      label="备注说明"
                      value={diseaseNotes}
                      onChange={(e) => setDiseaseNotes(e.target.value)}
                      placeholder="可选：补充说明病情、用药情况等"
                    />
                  </Grid>
                </Grid>
                <Button
                  variant="contained"
                  startIcon={<AddIcon />}
                  onClick={addChronicDisease}
                  sx={{ mt: 2 }}
                >
                  添加疾病
                </Button>
              </Box>
            </Paper>

            {/* Save Button */}
            <Paper elevation={3} sx={{ p: 4, borderRadius: 3 }}>
              {/* Error/Success Messages */}
              {error && (
                <Alert severity="error" sx={{ mb: 2 }}>
                  {error}
                </Alert>
              )}
              {success && (
                <Alert severity="success" sx={{ mb: 2 }}>
                  {success}
                </Alert>
              )}
              
              <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', pt: 2, borderTop: '1px solid #e0e0e0' }}>
                <Button
                  variant="contained"
                  startIcon={saving ? <CircularProgress size={20} /> : <SaveIcon />}
                  onClick={handleSave}
                  disabled={saving}
                  sx={{ flex: 1 }}
                >
                  保存所有信息
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<RefreshIcon />}
                  onClick={handleReset}
                  sx={{ flex: 1 }}
                >
                  重置表单
                </Button>
              </Box>
            </Paper>
          </>
        )}
      </Container>
    </Box>
  );
};

export default Profile;
