import React, { useState, useEffect, useRef } from 'react';
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
  LinearProgress,
  Chip,
  IconButton,
  Card,
  CardContent,
  Avatar,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  AppBar,
  Toolbar,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  CloudUpload as CloudUploadIcon,
  Delete as DeleteIcon,
  Send as SendIcon,
  Refresh as RefreshIcon,
  Cancel as CancelIcon,
  Search as SearchIcon,
  LocalHospital as HospitalIcon,
  Description as DescriptionIcon,
  Person as PersonIcon,
  Logout as LogoutIcon,
  EditNote as EditNoteIcon,
  Home as HomeIcon,
} from '@mui/icons-material';
import { useAuth } from '../../hooks/useAuth';
import { casesApi, documentsApi, aiApi, doctorsApi } from '../../services/api';
import type {
  MedicalCase,
  MedicalDocument,
  DiagnosisRequest,
  Doctor,
  AIFeedback,
  KnowledgeSource,
} from '../../types';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

const SymptomSubmit: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Form state
  const [symptoms, setSymptoms] = useState('');
  const [durationValue, setDurationValue] = useState('');
  const [durationUnit, setDurationUnit] = useState('');
  const [severity, setSeverity] = useState('');
  const [onsetTime, setOnsetTime] = useState('');
  const [triggers, setTriggers] = useState('');
  const [previousDiseases, setPreviousDiseases] = useState('');
  const [shareWithDoctor, setShareWithDoctor] = useState(false);

  // File upload state
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);
  const [uploadedDocuments, setUploadedDocuments] = useState<MedicalDocument[]>([]);

  // Doctor selection state
  const [doctorSearchQuery, setDoctorSearchQuery] = useState('');
  const [searchedDoctors, setSearchedDoctors] = useState<Doctor[]>([]);
  const [selectedDoctors, setSelectedDoctors] = useState<Doctor[]>([]);

  // UI state
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [diagnosisResult, setDiagnosisResult] = useState<AIFeedback | null>(null);
  const [knowledgeSources, setKnowledgeSources] = useState<KnowledgeSource[]>([]);

  // Streaming diagnosis state
  const [streamingContent, setStreamingContent] = useState('');
  const [streamingStatus, setStreamingStatus] = useState('');
  const [currentCaseId, setCurrentCaseId] = useState<string | null>(null);

  useEffect(() => {
    if (doctorSearchQuery) {
      searchDoctors();
    }
  }, [doctorSearchQuery]);

  const handleLogout = () => {
    if (window.confirm('确定要退出登录吗？')) {
      logout();
    }
  };

  const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB - MinerU API 限制

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files) {
      const newFiles = Array.from(event.target.files);
      const validFiles: File[] = [];
      const oversizedFiles: string[] = [];

      newFiles.forEach(file => {
        if (file.size > MAX_FILE_SIZE) {
          oversizedFiles.push(file.name);
        } else {
          validFiles.push(file);
        }
      });

      if (oversizedFiles.length > 0) {
        setError(`以下文件超过 10MB 限制，无法上传：\n${oversizedFiles.join(', ')}\n\n请压缩图片或使用更小尺寸的文件。`);
        setTimeout(() => setError(null), 8000);
      }

      if (validFiles.length > 0) {
        setUploadedFiles([...uploadedFiles, ...validFiles]);
      }
    }
  };

  const handleFileDrop = (event: React.DragEvent) => {
    event.preventDefault();
    const droppedFiles = Array.from(event.dataTransfer.files);
    const validFiles: File[] = [];
    const oversizedFiles: string[] = [];

    droppedFiles.forEach(file => {
      if (file.size > MAX_FILE_SIZE) {
        oversizedFiles.push(file.name);
      } else {
        validFiles.push(file);
      }
    });

    if (oversizedFiles.length > 0) {
      setError(`以下文件超过 10MB 限制，无法上传：\n${oversizedFiles.join(', ')}\n\n请压缩图片或使用更小尺寸的文件。`);
      setTimeout(() => setError(null), 8000);
    }

    if (validFiles.length > 0) {
      setUploadedFiles([...uploadedFiles, ...validFiles]);
    }
  };

  const handleDragOver = (event: React.DragEvent) => {
    event.preventDefault();
  };

  const removeFile = (index: number) => {
    const newFiles = uploadedFiles.filter((_, i) => i !== index);
    setUploadedFiles(newFiles);
  };

  const searchDoctors = async () => {
    if (!doctorSearchQuery.trim()) {
      setSearchedDoctors([]);
      return;
    }

    try {
      const doctors = await doctorsApi.getDoctors();
      const filteredDoctors = doctors.filter(doctor => 
        doctor.display_name?.toLowerCase().includes(doctorSearchQuery.toLowerCase()) ||
        doctor.hospital?.toLowerCase().includes(doctorSearchQuery.toLowerCase()) ||
        doctor.specialty?.toLowerCase().includes(doctorSearchQuery.toLowerCase())
      ).slice(0, 10);
      setSearchedDoctors(filteredDoctors);
    } catch (err) {
      console.error('搜索医生失败:', err);
    }
  };

  const toggleDoctorSelection = (doctor: Doctor) => {
    const isSelected = selectedDoctors.some(d => d.id === doctor.id);
    if (isSelected) {
      setSelectedDoctors(selectedDoctors.filter(d => d.id !== doctor.id));
    } else {
      setSelectedDoctors([...selectedDoctors, doctor]);
    }
  };

  const uploadFiles = async (caseId: string): Promise<string[]> => {
    const documentIds: string[] = [];

    for (const file of uploadedFiles) {
      try {
        setStreamingStatus(`正在上传文件: ${file.name}...`);
        const document = await documentsApi.upload(file, caseId);
        documentIds.push(document.id);

        setStreamingStatus(`正在提取文件内容: ${file.name}...`);
        try {
          await documentsApi.extract(document.id);

          // 轮询等待提取完成
          // 注意：文档提取可能需要 2-5 分钟（AI 识别 + PII 脱敏处理）
          let attempts = 0;
          const maxAttempts = 180; // 最多等待 6 分钟 (180 × 2秒)
          const pollInterval = 2000; // 每 2 秒检查一次

          while (attempts < maxAttempts) {
            const doc = await documentsApi.getDocument(document.id);
            if (doc.extracted_content || doc.cleaned_content) {
              setStreamingStatus(`文件提取完成: ${file.name}`);
              break;
            }

            // 如果状态是 failed，获取详细错误信息
            if (doc.upload_status === 'failed') {
              try {
                const contentInfo = await documentsApi.getDocumentContent(document.id);
                const errorDetail = contentInfo.error || contentInfo.message || '未知错误';
                console.warn(`文件提取失败: ${file.name}, 原因: ${errorDetail}`);
                setStreamingStatus(`文件 ${file.name} 提取失败: ${errorDetail}`);
              } catch (err) {
                console.warn(`文件提取失败: ${file.name}`);
                setStreamingStatus(`文件 ${file.name} 提取失败，请检查配置`);
              }
              break;
            }

            // 更新进度提示（每 15 秒更新一次提示）
            const elapsedSeconds = (attempts + 1) * (pollInterval / 1000);
            if (attempts % 7 === 0) { // 约每 14 秒更新一次
              setStreamingStatus(`正在提取文件内容: ${file.name} (${elapsedSeconds}秒)...\nAI 识别和隐私保护处理可能需要几分钟，请耐心等待`);
            }

            await new Promise(resolve => setTimeout(resolve, pollInterval));
            attempts++;
          }

          if (attempts >= maxAttempts) {
            // 超时但继续处理，不阻塞用户
            console.warn(`文件提取时间较长: ${file.name}，后台仍在处理中`);
            setStreamingStatus(`文件 ${file.name} 正在后台处理中，您可先提交症状`);
          }
        } catch (err) {
          console.error('文档提取失败:', file.name, err);
          // 提取失败不阻塞，继续处理其他文件
          setStreamingStatus(`文件 ${file.name} 提取遇到问题，继续处理...`);
        }
      } catch (err) {
        console.error('上传文件失败:', file.name, err);
      }
    }

    return documentIds;
  };

  const handleReset = () => {
    setSymptoms('');
    setDurationValue('');
    setDurationUnit('');
    setSeverity('');
    setOnsetTime('');
    setTriggers('');
    setPreviousDiseases('');
    setShareWithDoctor(false);
    setUploadedFiles([]);
    setSelectedDoctors([]);
    setDiagnosisResult(null);
    setStreamingContent('');
    setStreamingStatus('');
    setCurrentCaseId(null);
    setKnowledgeSources([]);
  };

  const handleSubmit = async () => {
    if (!symptoms.trim()) {
      setError('请描述您的主要症状');
      return;
    }

    setSubmitting(true);
    setError(null);
    setSuccess(null);
    setStreamingContent('');
    setStreamingStatus('正在创建病历记录...');

    try {
      // Step 1: Create medical case
      const caseTitle = `AI诊断 - ${severity}${durationValue ? ` - ${durationValue}${durationUnit}` : ''}`;
      const caseDescriptionParts = [];
      if (triggers) caseDescriptionParts.push(`诱发因素: ${triggers}`);
      if (previousDiseases) caseDescriptionParts.push(`既往病史: ${previousDiseases}`);

      const medicalCase = await casesApi.createCase({
        title: caseTitle,
        symptoms,
        severity: severity as 'low' | 'medium' | 'high' | 'critical' | undefined,
        description: caseDescriptionParts.join(' | ') || '',
      });

      const caseId = medicalCase.id;
      setCurrentCaseId(caseId);
      setStreamingStatus('正在上传文件...');

      // Step 2: Upload files
      const documentIds = uploadedFiles.length > 0 ? await uploadFiles(caseId) : [];

      // Step 3: Submit to AI for streaming diagnosis
      setStreamingStatus('AI正在分析您的症状...');
      const requestBody: DiagnosisRequest = {
        symptoms,
        symptom_severity: severity,
        symptom_duration: durationValue ? `${durationValue}${durationUnit}` : '',
        document_ids: documentIds,
        doctor_ids: selectedDoctors.map(doctor => doctor.id),
        share_with_doctors: shareWithDoctor,
        language: 'zh',
        case_id: caseId,  // 传递病例ID，避免重复创建
      };

      let fullDiagnosis = '';
      await aiApi.diagnoseStream(
        requestBody,
        (chunk) => {
          fullDiagnosis += chunk;
          setStreamingContent(fullDiagnosis);
        },
        (fullText, caseId, modelInfo, knowledgeSources) => {
          setStreamingStatus('诊断完成');
          const aiFeedback: AIFeedback = {
            id: `stream-${Date.now()}`,
            medical_case_id: caseId || currentCaseId || '',
            feedback_type: 'ai_diagnosis',
            input_data: requestBody,
            ai_response: {
              diagnosis: fullText,
              model_id: modelInfo?.model_id || '未知模型',
              tokens_used: modelInfo?.tokens_used,
            },
            knowledge_sources: knowledgeSources,
            is_reviewed: false,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          };
          setDiagnosisResult(aiFeedback);
          setSuccess('AI诊断完成！已保存到您的诊疗记录中。');
        },
        (error) => {
          console.error('Streaming error:', error);
          setError('AI诊断流式传输错误：' + error);
          setStreamingStatus('');
        }
      );
      
    } catch (err) {
      console.error('提交失败:', err);
      setError('提交失败：' + (err instanceof Error ? err.message : '未知错误'));
      setStreamingStatus('');
    } finally {
      setSubmitting(false);
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
              sx={{ borderRadius: 2 }}
            >
              个人中心
            </Button>
            <Button
              startIcon={<EditNoteIcon />}
              onClick={() => navigate('/patient/symptom-submit')}
              variant="contained"
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
              退出
            </Button>
          </Box>
        </Paper>
      </Container>

      <Container maxWidth="md">
        {/* Symptom Form */}
        <Paper elevation={3} sx={{ p: 4, mb: 3, borderRadius: 3 }}>
          <Typography variant="h4" gutterBottom sx={{ fontWeight: 'bold', color: '#333' }}>
            症状提交
          </Typography>

          {/* Symptom Description */}
          <Box sx={{ mb: 4 }}>
            <Typography variant="h6" gutterBottom>
              症状描述
            </Typography>
            <TextField
              fullWidth
              multiline
              rows={4}
              label="主要症状（必填）"
              value={symptoms}
              onChange={(e) => setSymptoms(e.target.value)}
              placeholder="请详细描述您的症状，例如：咳嗽一周，多在夜间加重，运动后症状明显"
              required
            />
          </Box>

          {/* Duration and Severity */}
          <Grid container spacing={3} sx={{ mb: 4 }}>
            <Grid item xs={12} md={6}>
              <Typography variant="h6" gutterBottom>
                症状持续时间
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={7}>
                  <TextField
                    fullWidth
                    type="number"
                    label="输入数值"
                    value={durationValue}
                    onChange={(e) => setDurationValue(e.target.value)}
                  />
                </Grid>
                <Grid item xs={5}>
                  <FormControl fullWidth>
                    <InputLabel id="duration-unit-label">选择单位</InputLabel>
                    <Select
                      labelId="duration-unit-label"
                      id="duration-unit"
                      value={durationUnit}
                      label="选择单位"
                      onChange={(e) => setDurationUnit(e.target.value)}
                    >
                      <MenuItem value="">选择单位</MenuItem>
                      <MenuItem value="秒">秒</MenuItem>
                      <MenuItem value="分钟">分钟</MenuItem>
                      <MenuItem value="小时">小时</MenuItem>
                      <MenuItem value="天">天</MenuItem>
                      <MenuItem value="周">周</MenuItem>
                      <MenuItem value="月">月</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
              </Grid>
            </Grid>
            <Grid item xs={12} md={6}>
              <Typography variant="h6" gutterBottom>
                症状严重程度
              </Typography>
              <FormControl fullWidth>
                <InputLabel id="severity-label">请选择严重程度</InputLabel>
                <Select
                  labelId="severity-label"
                  id="severity"
                  value={severity}
                  label="请选择严重程度"
                  onChange={(e) => setSeverity(e.target.value)}
                >
                  <MenuItem value="">请选择严重程度</MenuItem>
                  <MenuItem value="轻微">轻微</MenuItem>
                  <MenuItem value="轻度">轻度</MenuItem>
                  <MenuItem value="中度">中度</MenuItem>
                  <MenuItem value="重度">重度</MenuItem>
                  <MenuItem value="严重">严重</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>

          {/* Document Upload */}
          <Box sx={{ mb: 4 }}>
            <Typography variant="h6" gutterBottom>
              检查资料上传
            </Typography>
            <Paper
              elevation={1}
              sx={{
                p: 4,
                border: '2px dashed #667eea',
                borderRadius: 2,
                textAlign: 'center',
                cursor: 'pointer',
                bgcolor: '#f8f9fa',
                '&:hover': {
                  bgcolor: '#e9ecef',
                  borderColor: '#764ba2',
                },
              }}
              onClick={() => fileInputRef.current?.click()}
              onDrop={handleFileDrop}
              onDragOver={handleDragOver}
            >
              <input
                type="file"
                multiple
                ref={fileInputRef}
                style={{ display: 'none' }}
                onChange={handleFileSelect}
                accept=".pdf,.jpg,.jpeg,.png,.doc,.docx"
              />
              <CloudUploadIcon sx={{ fontSize: 64, mb: 2, color: '#667eea' }} />
              <Typography variant="body1" gutterBottom>
                点击或拖拽文件到此处
              </Typography>
              <Typography variant="body2" color="text.secondary">
                支持 PDF、图片、Word 文档（单个文件不超过 10MB）
              </Typography>
            </Paper>

            {uploadedFiles.length > 0 && (
              <Box sx={{ mt: 2 }}>
                <Typography variant="h6" gutterBottom>
                  已选择的文件
                </Typography>
                {uploadedFiles.map((file, index) => (
                  <Card key={index} sx={{ mb: 1 }}>
                    <CardContent sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                      <Typography>
                        📎 {file.name} ({Math.round(file.size / 1024)} KB)
                      </Typography>
                      <IconButton onClick={() => removeFile(index)} color="error">
                        <DeleteIcon />
                      </IconButton>
                    </CardContent>
                  </Card>
                ))}
              </Box>
            )}

            <Alert severity="warning" sx={{ mt: 2 }}>
              <Typography variant="body2">
                <strong>隐私保护提醒：</strong><br />
                请在上传前删除或裁切图片中的<strong>个人姓名、身份证号、电话号码</strong>等敏感信息。
                系统会自动进行隐私信息识别和清理，但提前处理能更好保护您的隐私。
              </Typography>
            </Alert>
          </Box>

          {/* Additional Information */}
          <Box sx={{ mb: 4 }}>
            <Typography variant="h6" gutterBottom>
              其他信息
            </Typography>
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  type="datetime-local"
                  label="发病时间"
                  value={onsetTime}
                  onChange={(e) => setOnsetTime(e.target.value)}
                  InputLabelProps={{ shrink: true }}
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  multiline
                  rows={2}
                  label="诱因（如果知道）"
                  value={triggers}
                  onChange={(e) => setTriggers(e.target.value)}
                  placeholder="例如：接触过敏原、气候变化、运动后等"
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  multiline
                  rows={2}
                  label="既往史相关疾病（可选）"
                  value={previousDiseases}
                  onChange={(e) => setPreviousDiseases(e.target.value)}
                  placeholder="例如：曾经患过类似症状的疾病"
                />
              </Grid>
            </Grid>
          </Box>

          {/* Doctor Mention */}
          <Box sx={{ mb: 4 }}>
            <Typography variant="h6" gutterBottom>
              @提及医生（可选）
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              如果您希望特定医生关注您的病例，可以在这里@提及医生。
              您可以同时选择多位医生，所有被@的医生将收到通知并可以查看您的诊断信息。
            </Typography>

            {/* Doctor Search */}
            <Box sx={{ mb: 2 }}>
              <TextField
                fullWidth
                label="搜索医生（可添加多位）"
                value={doctorSearchQuery}
                onChange={(e) => setDoctorSearchQuery(e.target.value)}
                InputProps={{
                  startAdornment: <SearchIcon sx={{ mr: 1, color: 'action.active' }} />,
                }}
                placeholder="输入医生姓名、医院或专业领域"
              />
            </Box>

            {/* Search Results */}
            {searchedDoctors.length > 0 && (
              <Paper elevation={1} sx={{ mb: 2, p: 2, maxHeight: 300, overflowY: 'auto' }}>
                {searchedDoctors.map((doctor) => {
                  const isSelected = selectedDoctors.some(d => d.id === doctor.id);
                  return (
                    <Card
                      key={doctor.id}
                      sx={{
                        mb: 1,
                        border: isSelected ? '2px solid #667eea' : '1px solid #e0e0e0',
                        bgcolor: isSelected ? '#f0f3ff' : 'white',
                        cursor: 'pointer',
                      }}
                      onClick={() => toggleDoctorSelection(doctor)}
                    >
                      <CardContent>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <Box>
                            <Typography variant="subtitle1" fontWeight="bold">
                              {doctor.display_name}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              {doctor.hospital || '未知医院'} · {doctor.department || '未知科室'}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              专业领域：{doctor.specialty || '未填写'}
                            </Typography>
                          </Box>
                          <Typography variant="h6" color={isSelected ? '#667eea' : '#ccc'}>
                            {isSelected ? '✓' : '+'}
                          </Typography>
                        </Box>
                      </CardContent>
                    </Card>
                  );
                })}
              </Paper>
            )}

            {/* Selected Doctors */}
            {selectedDoctors.length > 0 && (
              <Paper elevation={1} sx={{ mb: 2, p: 2, bgcolor: '#f0f3ff', border: '1px solid #667eea' }}>
                <Typography variant="h6" gutterBottom>
                  已选择 {selectedDoctors.length} 位医生
                </Typography>
                <List>
                  {selectedDoctors.map((doctor) => (
                    <ListItem key={doctor.id}>
                      <ListItemText
                        primary={doctor.display_name}
                        secondary={`${doctor.hospital || '未知医院'} · ${doctor.department || '未知科室'}`}
                      />
                      <ListItemSecondaryAction>
                        <IconButton
                          edge="end"
                          onClick={() => toggleDoctorSelection(doctor)}
                          color="error"
                        >
                          <DeleteIcon />
                        </IconButton>
                      </ListItemSecondaryAction>
                    </ListItem>
                  ))}
                </List>
                <Button
                  variant="outlined"
                  color="error"
                  onClick={() => setSelectedDoctors([])}
                >
                  清除全部选择
                </Button>
              </Paper>
            )}
          </Box>

          {/* Privacy Consent */}
          <Box sx={{ mb: 4 }}>
            <Typography variant="h6" gutterBottom>
              隐私授权
            </Typography>
            <FormControlLabel
              control={
                <Checkbox
                  checked={shareWithDoctor}
                  onChange={(e) => setShareWithDoctor(e.target.checked)}
                />
              }
              label={
                <Box>
                  <Typography variant="body1" fontWeight="bold">
                    允许将本次诊断信息共享给医生端
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    勾选后，医生可以查看您的症状、AI诊断结果和上传的检查资料（个人敏感信息如姓名、身份证号等将被自动隐藏）。不勾选则仅您自己可见。
                  </Typography>
                </Box>
              }
            />
          </Box>

          {/* Buttons */}
          <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center' }}>
            <Button
              variant="contained"
              size="large"
              onClick={handleSubmit}
              disabled={submitting || !symptoms.trim()}
              startIcon={submitting ? <CircularProgress size={20} /> : <SendIcon />}
              sx={{ borderRadius: 2, minWidth: 200 }}
            >
              提交给AI诊断
            </Button>
            <Button
              variant="outlined"
              size="large"
              onClick={handleReset}
              startIcon={<RefreshIcon />}
              sx={{ borderRadius: 2 }}
            >
              重置
            </Button>
            <Button
              variant="outlined"
              size="large"
              onClick={() => navigate('/patient')}
              startIcon={<CancelIcon />}
              color="error"
              sx={{ borderRadius: 2 }}
            >
              取消并返回
            </Button>
          </Box>
        </Paper>

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

        {/* Streaming Diagnosis Result */}
        {(submitting || streamingContent || diagnosisResult) && (
          <Paper elevation={3} sx={{ p: 4, borderRadius: 3 }}>
            <Typography variant="h5" gutterBottom sx={{ fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: 1 }}>
              🤖 AI诊断结果
            </Typography>

            {submitting && streamingStatus && (
              <Box sx={{ mb: 2 }}>
                <LinearProgress />
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                  {streamingStatus}
                </Typography>
              </Box>
            )}

            {(streamingContent || diagnosisResult) && (
              <Paper
                elevation={1}
                sx={{
                  p: 3,
                  mb: 3,
                  bgcolor: '#fafafa',
                  maxHeight: '600px',
                  overflow: 'auto',
                  '& img': { maxWidth: '100%', height: 'auto' },
                  '& table': {
                    borderCollapse: 'collapse',
                    width: '100%',
                    mb: 2,
                  },
                  '& th, & td': {
                    border: '1px solid #ddd',
                    p: 1,
                    textAlign: 'left',
                  },
                  '& th': {
                    bgcolor: '#f0f0f0',
                    fontWeight: 'bold',
                  },
                }}
              >
                <ReactMarkdown
                  remarkPlugins={[remarkGfm]}
                  components={{
                    p: ({ children }) => (
                      <Typography variant="body1" sx={{ mb: 1.5, lineHeight: 1.7 }}>
                        {children}
                      </Typography>
                    ),
                    h1: ({ children }) => (
                      <Typography variant="h4" sx={{ mt: 3, mb: 2, fontWeight: 'bold' }}>
                        {children}
                      </Typography>
                    ),
                    h2: ({ children }) => (
                      <Typography variant="h5" sx={{ mt: 2.5, mb: 1.5, fontWeight: 'bold' }}>
                        {children}
                      </Typography>
                    ),
                    h3: ({ children }) => (
                      <Typography variant="h6" sx={{ mt: 2, mb: 1, fontWeight: 'bold' }}>
                        {children}
                      </Typography>
                    ),
                    li: ({ children }) => (
                      <Typography component="li" variant="body1" sx={{ mb: 0.5, ml: 2 }}>
                        {children}
                      </Typography>
                    ),
                    code: ({ children }) => (
                      <Box
                        component="code"
                        sx={{
                          bgcolor: '#e0e0e0',
                          px: 0.5,
                          py: 0.25,
                          borderRadius: 0.5,
                          fontFamily: 'monospace',
                          fontSize: '0.9em',
                        }}
                      >
                        {children}
                      </Box>
                    ),
                    pre: ({ children }) => (
                      <Box
                        component="pre"
                        sx={{
                          bgcolor: '#f5f5f5',
                          p: 2,
                          borderRadius: 1,
                          overflow: 'auto',
                          fontFamily: 'monospace',
                          fontSize: '0.9em',
                          mb: 2,
                        }}
                      >
                        {children}
                      </Box>
                    ),
                  }}
                >
                  {streamingContent || diagnosisResult?.ai_response?.diagnosis || diagnosisResult?.ai_response?.analysis || ''}
                </ReactMarkdown>
              </Paper>
            )}

            {diagnosisResult && (
              <Paper
                elevation={0}
                sx={{
                  mb: 3,
                  p: 2.5,
                  background: 'linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%)',
                  borderRadius: 3,
                  border: '1px solid rgba(102, 126, 234, 0.15)',
                  position: 'relative',
                  overflow: 'hidden',
                  '&::before': {
                    content: '""',
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    right: 0,
                    height: '3px',
                    background: 'linear-gradient(90deg, #667eea 0%, #764ba2 100%)',
                  },
                }}
              >
                <Grid container spacing={3} alignItems="center">
                  <Grid item xs={12} sm={6}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                      <Box
                        sx={{
                          width: 44,
                          height: 44,
                          borderRadius: '12px',
                          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          boxShadow: '0 4px 12px rgba(102, 126, 234, 0.3)',
                        }}
                      >
                        <span style={{ fontSize: '1.5em' }}>🤖</span>
                      </Box>
                      <Box>
                        <Typography
                          variant="caption"
                          sx={{
                            color: '#64748b',
                            fontWeight: 600,
                            textTransform: 'uppercase',
                            letterSpacing: '0.5px',
                            fontSize: '0.7rem',
                          }}
                        >
                          AI 模型
                        </Typography>
                        <Typography
                          variant="body1"
                          sx={{
                            fontWeight: 700,
                            color: '#334155',
                            fontSize: '0.95rem',
                            fontFamily: 'monospace',
                            letterSpacing: '-0.3px',
                          }}
                        >
                          {diagnosisResult.ai_response?.model_id || 'AI Model'}
                        </Typography>
                      </Box>
                    </Box>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <Box
                      sx={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: { xs: 'flex-start', sm: 'flex-end' },
                        gap: 2,
                      }}
                    >
                      <Box
                        sx={{
                          width: 44,
                          height: 44,
                          borderRadius: '12px',
                          background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          boxShadow: '0 4px 12px rgba(16, 185, 129, 0.3)',
                        }}
                      >
                        <span style={{ fontSize: '1.5em' }}>🪙</span>
                      </Box>
                      <Box>
                        <Typography
                          variant="caption"
                          sx={{
                            color: '#64748b',
                            fontWeight: 600,
                            textTransform: 'uppercase',
                            letterSpacing: '0.5px',
                            fontSize: '0.7rem',
                          }}
                        >
                          Token 消耗
                        </Typography>
                        <Typography
                          variant="body1"
                          sx={{
                            fontWeight: 700,
                            color: '#334155',
                            fontSize: '0.95rem',
                            fontFamily: 'monospace',
                          }}
                        >
                          {diagnosisResult.ai_response?.tokens_used?.toLocaleString() || 'N/A'}
                        </Typography>
                      </Box>
                    </Box>
                  </Grid>
                </Grid>
              </Paper>
            )}

            {diagnosisResult?.knowledge_sources && diagnosisResult.knowledge_sources.length > 0 && (
              <Accordion defaultExpanded={false} sx={{ bgcolor: '#fafafa' }}>
                <AccordionSummary
                  expandIcon={<ExpandMoreIcon />}
                  sx={{
                    '&:hover': { bgcolor: '#f0f0f0' },
                    borderRadius: 1
                  }}
                >
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                    <span style={{ fontSize: '1.5em' }}>📚</span>
                    <Box>
                      <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>
                        RAG 知识库引用
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        基于 {diagnosisResult.knowledge_sources.reduce((acc, src) => acc + (src.chunks?.length || 0), 0)} 个相关医疗知识片段
                      </Typography>
                    </Box>
                  </Box>
                </AccordionSummary>
                <AccordionDetails>
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                    {diagnosisResult.knowledge_sources.map((source, sourceIndex) => (
                      source.chunks?.map((chunk, chunkIndex) => (
                        <Card
                          key={`${sourceIndex}-${chunkIndex}`}
                          sx={{
                            mb: 1,
                            borderLeft: '4px solid #667eea',
                            boxShadow: '0 2px 4px rgba(0,0,0,0.05)',
                            '&:hover': { boxShadow: '0 4px 8px rgba(0,0,0,0.1)' }
                          }}
                        >
                          <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                              <Typography variant="subtitle2" sx={{ fontWeight: 'bold', color: '#667eea', flex: 1 }}>
                                {chunk.document_title || source.document_title || source.category_name || source.category || '未知文档'}
                              </Typography>
                              {chunk.relevance_score !== undefined && (
                                <Chip
                                  label={`${(chunk.relevance_score * 100).toFixed(1)}% 相关`}
                                  size="small"
                                  sx={{
                                    ml: 1,
                                    bgcolor: chunk.relevance_score > 0.8 ? '#dcfce7' : chunk.relevance_score > 0.6 ? '#fef3c7' : '#fee2e2',
                                    color: chunk.relevance_score > 0.8 ? '#166534' : chunk.relevance_score > 0.6 ? '#92400e' : '#991b1b',
                                    fontWeight: 'bold',
                                    fontSize: '0.75rem'
                                  }}
                                />
                              )}
                            </Box>
                            {(chunk.section_title || source.section_title) && (
                              <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 1 }}>
                                📖 {chunk.section_title || source.section_title}
                              </Typography>
                            )}
                            {(chunk.chunk_text || chunk.text_preview) && (
                              <Typography
                                variant="body2"
                                color="text.secondary"
                                sx={{
                                  mt: 1,
                                  p: 1.5,
                                  bgcolor: '#f8f9fa',
                                  borderRadius: 1,
                                  fontSize: '0.875rem',
                                  lineHeight: 1.6
                                }}
                              >
                                {(chunk.chunk_text || chunk.text_preview || '').length > 200
                                  ? `${(chunk.chunk_text || chunk.text_preview || '').substring(0, 200)}...`
                                  : (chunk.chunk_text || chunk.text_preview || '')}
                              </Typography>
                            )}
                          </CardContent>
                        </Card>
                      ))
                    ))}
                  </Box>
                </AccordionDetails>
              </Accordion>
            )}
          </Paper>
        )}
      </Container>
    </Box>
  );
};

export default SymptomSubmit;
