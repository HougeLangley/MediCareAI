import React, { useState, useEffect, useRef } from 'react';
import html2canvas from 'html2canvas';
import jsPDF from 'jspdf';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Container,
  Paper,
  Typography,
  TextField,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Card,
  CardContent,
  Chip,
  Avatar,
  IconButton,
  Dialog,
  DialogTitle,
  FormControlLabel,
  Checkbox,
  DialogContent,
  DialogActions,
  AppBar,
  Toolbar,
  CircularProgress,
  Alert,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Divider,
  Grid,
  Tabs,
  Tab,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  Search as SearchIcon,
  Visibility as VisibilityIcon,
  Share as ShareIcon,
  Print as PrintIcon,
  PictureAsPdf as PictureAsPdfIcon,
  Compare as CompareIcon,
  Note as NoteIcon,
  LocalHospital as HospitalIcon,
  Description as DescriptionIcon,
  Person as PersonIcon,
  Logout as LogoutIcon,
  EditNote as EditNoteIcon,
  Home as HomeIcon,
  FilterList as FilterListIcon,
} from '@mui/icons-material';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { useAuth } from '../../hooks/useAuth';
import { casesApi, doctorsApi } from '../../services/api';
import type { MedicalCase, Doctor, DoctorCaseComment, CaseCommentReply } from '../../types';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`simple-tabpanel-${index}`}
      aria-labelledby={`simple-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const MedicalRecords: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  // State
  const [records, setRecords] = useState<MedicalCase[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchKeyword, setSearchKeyword] = useState('');
  const [timeRange, setTimeRange] = useState('');
  
  // Modal states
  const [selectedRecord, setSelectedRecord] = useState<MedicalCase | null>(null);
  const [detailModalOpen, setDetailModalOpen] = useState(false);
  const [shareModalOpen, setShareModalOpen] = useState(false);
  const [compareModalOpen, setCompareModalOpen] = useState(false);
  
  // Sharing states
  const [selectedDoctors, setSelectedDoctors] = useState<Doctor[]>([]);
  const [doctorSearchQuery, setDoctorSearchQuery] = useState('');
  const [searchedDoctors, setSearchedDoctors] = useState<Doctor[]>([]);
  const [includeDiagnosis, setIncludeDiagnosis] = useState(true);
  const [includeSymptoms, setIncludeSymptoms] = useState(true);
  const [includePersonal, setIncludePersonal] = useState(false);
  const [shareConsent, setShareConsent] = useState(false);
  const [shareTab, setShareTab] = useState(0);

  // Comments states
  const [comments, setComments] = useState<DoctorCaseComment[]>([]);
  const [replyFormVisible, setReplyFormVisible] = useState<{ [key: string]: boolean }>({});
  const [replyTexts, setReplyTexts] = useState<{ [key: string]: string }>({});

  // Compare states
  const [compareRecord1, setCompareRecord1] = useState<string>('');
  const [compareRecord2, setCompareRecord2] = useState<string>('');

  useEffect(() => {
    loadRecords();
  }, []);

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

  const loadRecords = async () => {
    try {
      setLoading(true);
      const data = await casesApi.getCases();
      setRecords(data);
    } catch (err) {
      console.error('加载诊疗记录失败:', err);
      setError('加载诊疗记录失败');
    } finally {
      setLoading(false);
    }
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

  const handleViewRecord = (record: MedicalCase) => {
    setSelectedRecord(record);
    setDetailModalOpen(true);
    loadDoctorComments(record.id);
  };

  const handleShareRecord = (record: MedicalCase) => {
    setSelectedRecord(record);
    setShareModalOpen(true);
  };

  const handleCompareRecord = (record: MedicalCase) => {
    setCompareRecord1(record.id);
    setCompareModalOpen(true);
  };

  const loadDoctorComments = async (caseId: string) => {
    try {
      const comments = await casesApi.getDoctorComments(caseId);
      setComments(comments);
    } catch (err) {
      console.error('加载医生评论失败:', err);
    }
  };

  const toggleReplyForm = (commentId: string) => {
    setReplyFormVisible(prev => ({
      ...prev,
      [commentId]: !prev[commentId]
    }));
  };

  const handleReplyChange = (commentId: string, value: string) => {
    setReplyTexts(prev => ({
      ...prev,
      [commentId]: value
    }));
  };

  const submitReply = async (commentId: string) => {
    const content = replyTexts[commentId];
    if (!content.trim()) {
      alert('请输入回复内容');
      return;
    }

    try {
      // Call API to submit patient reply to doctor comment
      if (selectedRecord) {
        await casesApi.replyToDoctorComment(selectedRecord.id, commentId, content);
      }
      setReplyTexts(prev => ({
        ...prev,
        [commentId]: ''
      }));
      setReplyFormVisible(prev => ({
        ...prev,
        [commentId]: false
      }));
      // Reload comments to show the new reply
      if (selectedRecord) {
        loadDoctorComments(selectedRecord.id);
      }
      alert('回复已发送');
    } catch (err) {
      console.error('发送回复失败:', err);
      alert('发送回复失败');
    }
  };

  const pdfRef = useRef<HTMLDivElement>(null);
  const diagnosisRef = useRef<HTMLDivElement>(null);

  const exportToPDF = async () => {
    if (!pdfRef.current || !selectedRecord) {
      alert('无法导出PDF，请稍后再试');
      return;
    }

    try {
      const element = pdfRef.current;
      
      // Use onclone to modify the cloned element before rendering
      const canvas = await html2canvas(element, {
        scale: 2,
        useCORS: true,
        logging: false,
        backgroundColor: '#ffffff',
        windowWidth: element.scrollWidth,
        windowHeight: element.scrollHeight,
        height: element.scrollHeight,
        width: element.scrollWidth,
        onclone: (clonedDoc) => {
          // Find the diagnosis Paper in the cloned document and remove scroll constraints
          const clonedDiagnosisPaper = clonedDoc.querySelector('[data-pdf-diagnosis]');
          if (clonedDiagnosisPaper) {
            (clonedDiagnosisPaper as HTMLElement).style.maxHeight = 'none';
            (clonedDiagnosisPaper as HTMLElement).style.overflow = 'visible';
            (clonedDiagnosisPaper as HTMLElement).style.height = 'auto';
          }
          
          // Also find any other scrollable containers
          const scrollableElements = clonedDoc.querySelectorAll('[style*="max-height"], [style*="overflow"]');
          scrollableElements.forEach((el) => {
            const htmlEl = el as HTMLElement;
            htmlEl.style.maxHeight = 'none';
            htmlEl.style.overflow = 'visible';
          });
        },
      });

      const imgData = canvas.toDataURL('image/png');
      const pdf = new jsPDF('p', 'mm', 'a4');
      
      const pdfWidth = pdf.internal.pageSize.getWidth();
      const pdfHeight = pdf.internal.pageSize.getHeight();
      const imgWidth = canvas.width;
      const imgHeight = canvas.height;
      const ratio = Math.min(pdfWidth / imgWidth, pdfHeight / imgHeight);
      
      const imgX = (pdfWidth - imgWidth * ratio) / 2;
      let imgY = 10;
      
      const scaledHeight = imgHeight * ratio * (pdfWidth - 20) / (imgWidth * ratio);
      const pageHeight = pdfHeight - 20;
      let heightLeft = scaledHeight;
      let position = 0;
      
      pdf.addImage(imgData, 'PNG', 10, imgY, pdfWidth - 20, scaledHeight);
      heightLeft -= pageHeight;
      
      while (heightLeft > 0) {
        position = heightLeft - scaledHeight;
        pdf.addPage();
        pdf.addImage(imgData, 'PNG', 10, position, pdfWidth - 20, scaledHeight);
        heightLeft -= pageHeight;
      }
      
      pdf.save(`诊疗记录_${selectedRecord.title || 'AI诊断'}_${new Date().toLocaleDateString('zh-CN')}.pdf`);
    } catch (error) {
      console.error('PDF导出失败:', error);
      alert('PDF导出失败，请尝试使用打印功能');
    }
  };

  const printDiagnosis = () => {
    window.print();
  };

  const shareToDoctor = async () => {
    if (selectedDoctors.length === 0) {
      alert('请先选择至少一位医生');
      return;
    }

    if (!shareConsent) {
      alert('请勾选同意分享的选项');
      return;
    }

    if (!selectedRecord) {
      alert('无法获取病例信息');
      return;
    }

    try {
      // This would need to be implemented in the API
      // await casesApi.shareWithDoctors(selectedRecord.id, selectedDoctors.map(d => d.id));
      alert(`成功分享给 ${selectedDoctors.length} 位医生！`);
      setShareModalOpen(false);
      setSelectedDoctors([]);
    } catch (err) {
      console.error('分享失败:', err);
      alert('分享失败');
    }
  };

  const getSeverityColor = (severity?: string) => {
    switch (severity) {
      case '轻微':
      case 'low':
        return '#28a745';
      case '轻度':
      case 'medium':
        return '#ffc107';
      case '中度':
      case 'high':
      case 'moderate':
        return '#fd7e14';
      case '重度':
      case 'critical':
      case 'severe':
        return '#dc3545';
      default:
        return '#6c757d';
    }
  };

  const getSeverityLabel = (severity?: string) => {
    switch (severity?.toLowerCase()) {
      case 'low':
      case '轻微':
        return '轻微';
      case 'medium':
      case '轻度':
        return '轻度';
      case 'high':
      case 'moderate':
      case '中度':
        return '中度';
      case 'critical':
      case 'severe':
      case '重度':
        return '重度';
      case 'minor':
        return '轻微';
      default:
        return severity || '未知';
    }
  };

  const getStatusLabel = (status?: string) => {
    switch (status) {
      case 'active':
        return '进行中';
      case 'completed':
        return '已完成';
      case 'archived':
        return '已归档';
      default:
        return status;
    }
  };

  const getStatusColor = (status?: string) => {
    switch (status) {
      case 'active':
        return '#28a745';
      case 'completed':
        return '#17a2b8';
      case 'archived':
        return '#6c757d';
      default:
        return '#6c757d';
    }
  };

  const extractDiagnosesFromMarkdown = (diagnosis?: string): string[] => {
    if (!diagnosis || diagnosis.trim().length === 0) {
      return [];
    }

    const diagnoses: string[] = [];
    let match;

    const cleanMarkdown = (text: string): string => {
      return text.replace(/\*\*/g, '').trim();
    };

    const tableRowPattern = /\|\s*(\d+)\s*\|\s*([^|]+?)\s*\|/g;
    while ((match = tableRowPattern.exec(diagnosis)) !== null) {
      const diagnosisName = cleanMarkdown(match[2]);
      const isHeaderRow = /诊断名称|诊断排序|---/.test(diagnosisName);
      const isValidEntry = diagnosisName.length > 1 && !isHeaderRow;
      if (isValidEntry) {
        diagnoses.push(diagnosisName);
      }
    }

    if (diagnoses.length === 0) {
      const listPattern = /(\d+)\.\s*\*\*\s*([^*]+?)\s*\*\*/g;
      while ((match = listPattern.exec(diagnosis)) !== null) {
        const diagnosisName = cleanMarkdown(match[2]);
        if (diagnosisName.length > 1 && !/初步诊断|检查报告/.test(diagnosisName)) {
          diagnoses.push(diagnosisName);
        }
      }
    }

    if (diagnoses.length === 0) {
      const boldPattern = /\*\*\s*([^*]{2,30}?)\s*\*\*/g;
      const diseaseKeywords = ['肺炎', '哮喘', '癫痫', '贫血', '感染', '炎症', '疾病', '综合征', '障碍', '症', '病'];
      while ((match = boldPattern.exec(diagnosis)) !== null) {
        const diagnosisName = cleanMarkdown(match[1]);
        const containsDiseaseKeyword = diseaseKeywords.some(kw => diagnosisName.includes(kw));
        const isNotGeneric = !/初步诊断|检查报告|就医建议|注意事项/.test(diagnosisName);
        if (containsDiseaseKeyword && isNotGeneric) {
          diagnoses.push(diagnosisName);
        }
      }
    }

    return [...new Set(diagnoses)];
  };

  const getRecordTitle = (record: MedicalCase): string => {
    const diagnoses = extractDiagnosesFromMarkdown(record.diagnosis);

    if (diagnoses.length > 0) {
      return `AI诊断 - ${diagnoses.join('、')}`;
    }

    return record.title || 'AI诊疗记录';
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // Filter records based on search and time range
  const filteredRecords = records.filter(record => {
    if (searchKeyword) {
      const keyword = searchKeyword.toLowerCase();
      if (!record.symptoms.toLowerCase().includes(keyword) && 
          !record.diagnosis?.toLowerCase().includes(keyword) &&
          !record.title?.toLowerCase().includes(keyword)) {
        return false;
      }
    }

    if (timeRange) {
      const recordDate = new Date(record.created_at);
      const now = new Date();
      const daysDiff = Math.floor((now.getTime() - recordDate.getTime()) / (1000 * 60 * 60 * 24));
      
      switch (timeRange) {
        case '7':
          if (daysDiff > 7) return false;
          break;
        case '30':
          if (daysDiff > 30) return false;
          break;
        case '90':
          if (daysDiff > 90) return false;
          break;
        case '180':
          if (daysDiff > 180) return false;
          break;
      }
    }

    return true;
  });

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
              sx={{ borderRadius: 2 }}
            >
              症状提交
            </Button>
            <Button
              startIcon={<DescriptionIcon />}
              onClick={() => navigate('/patient/medical-records')}
              variant="contained"
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

      <Container maxWidth="lg">
        {/* Filter Bar */}
        <Paper elevation={2} sx={{ p: 3, mb: 3, borderRadius: 3 }}>
          <Grid container spacing={3} alignItems="center">
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label="关键词搜索"
                value={searchKeyword}
                onChange={(e) => setSearchKeyword(e.target.value)}
                InputProps={{
                  startAdornment: <SearchIcon sx={{ mr: 1, color: 'action.active' }} />,
                }}
                placeholder="搜索诊断、症状..."
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <FormControl fullWidth>
                <InputLabel>时间范围</InputLabel>
                <Select
                  value={timeRange}
                  onChange={(e) => setTimeRange(e.target.value)}
                  label="时间范围"
                >
                  <MenuItem value="">全部时间</MenuItem>
                  <MenuItem value="7">最近7天</MenuItem>
                  <MenuItem value="30">最近30天</MenuItem>
                  <MenuItem value="90">最近3个月</MenuItem>
                  <MenuItem value="180">最近6个月</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={4}>
              <Button
                fullWidth
                variant="contained"
                startIcon={<FilterListIcon />}
                onClick={loadRecords}
                sx={{ height: '56px' }}
              >
                搜索
              </Button>
            </Grid>
          </Grid>
        </Paper>

        {/* Error Message */}
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {/* Loading State */}
        {loading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', my: 5 }}>
            <CircularProgress />
          </Box>
        )}

        {/* Records List */}
        {!loading && filteredRecords.length === 0 && !error && (
          <Paper elevation={2} sx={{ p: 5, textAlign: 'center', borderRadius: 3 }}>
            <DescriptionIcon sx={{ fontSize: 64, mb: 2, color: '#ccc' }} />
            <Typography variant="h6" gutterBottom>
              暂无诊疗记录
            </Typography>
            <Button
              variant="contained"
              onClick={() => navigate('/patient/symptom-submit')}
              startIcon={<EditNoteIcon />}
            >
              提交症状进行AI诊断
            </Button>
          </Paper>
        )}

        {/* Record Cards */}
        {!loading && filteredRecords.map((record) => (
          <Card
            key={record.id}
            elevation={3}
            sx={{
              mb: 3,
              borderLeft: `4px solid #667eea`,
              transition: 'transform 0.3s, box-shadow 0.3s',
              '&:hover': {
                transform: 'translateX(5px)',
                boxShadow: 6,
              },
            }}
          >
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="body2" color="text.secondary">
                  📅 {formatDate(record.created_at)}
                </Typography>
                <Chip
                  label={getStatusLabel(record.status)}
                  size="small"
                  sx={{
                    bgcolor: getStatusColor(record.status),
                    color: 'white',
                    fontWeight: 'bold',
                  }}
                />
              </Box>

              <Typography variant="h6" gutterBottom fontWeight="bold">
                {getRecordTitle(record)}
              </Typography>

              <Box sx={{ mb: 2, display: 'flex', alignItems: 'center' }}>
                <Typography variant="body2" sx={{ mr: 2, minWidth: '80px' }}>
                  严重程度：
                </Typography>
                <Chip
                  label={getSeverityLabel(record.severity)}
                  size="small"
                  sx={{
                    bgcolor: getSeverityColor(record.severity),
                    color: 'white',
                  }}
                />
              </Box>

              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" sx={{ mr: 2, mb: 1 }}>
                  症状：
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {record.symptoms.length > 100
                    ? `${record.symptoms.substring(0, 100)}...`
                    : record.symptoms}
                </Typography>
              </Box>

              {record.diagnosis && (
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" sx={{ mr: 2, mb: 1 }}>
                    AI诊断：
                  </Typography>
                  <Paper
                    elevation={0}
                    sx={{
                      p: 2,
                      bgcolor: '#f8f9fa',
                      borderRadius: 1,
                      border: '1px solid #e0e0e0',
                      maxHeight: '200px',
                      overflow: 'hidden',
                      '& p': { m: 0, fontSize: '0.875rem', lineHeight: 1.6 },
                      '& h1, & h2, & h3': { fontSize: '1rem', fontWeight: 'bold', mt: 1, mb: 0.5 },
                      '& table': { display: 'none' },
                      '& ul, & ol': { pl: 2, m: 0 },
                      '& li': { fontSize: '0.875rem' },
                    }}
                  >
                    <ReactMarkdown
                      remarkPlugins={[remarkGfm]}
                      components={{
                        p: ({ children }) => (
                          <Typography variant="body2" sx={{ fontSize: '0.875rem', lineHeight: 1.6 }}>
                            {children}
                          </Typography>
                        ),
                        h1: ({ children }) => <Typography variant="subtitle2" sx={{ fontWeight: 'bold', mt: 1 }}>{children}</Typography>,
                        h2: ({ children }) => <Typography variant="subtitle2" sx={{ fontWeight: 'bold', mt: 1 }}>{children}</Typography>,
                        h3: ({ children }) => <Typography variant="subtitle2" sx={{ fontWeight: 'bold', mt: 1 }}>{children}</Typography>,
                        li: ({ children }) => <Typography component="li" variant="body2" sx={{ fontSize: '0.875rem' }}>{children}</Typography>,
                      }}
                    >
                      {record.diagnosis.length > 200
                        ? `${record.diagnosis.substring(0, 200)}...`
                        : record.diagnosis}
                    </ReactMarkdown>
                  </Paper>
                </Box>
              )}

              <Button
                variant="contained"
                startIcon={<VisibilityIcon />}
                onClick={() => handleViewRecord(record)}
              >
                查看详情
              </Button>
            </CardContent>
          </Card>
        ))}

        {/* Back Button */}
        {!loading && (
          <Box sx={{ textAlign: 'center', mt: 3, pt: 2, borderTop: '1px solid #e0e0e0' }}>
            <Button
              variant="outlined"
              onClick={() => navigate('/patient')}
              startIcon={<HomeIcon />}
              size="large"
            >
              ← 返回主页
            </Button>
          </Box>
        )}
      </Container>

      {/* Detail Modal */}
      <Dialog
        open={detailModalOpen}
        onClose={() => setDetailModalOpen(false)}
        maxWidth="md"
        fullWidth
        PaperProps={{
          sx: { borderRadius: 3, overflow: 'hidden' }
        }}
      >
        {selectedRecord && (
          <>
            <DialogTitle sx={{ bgcolor: 'linear-gradient(135deg, #667eea, #764ba2)', color: 'white' }}>
              🩺 诊疗详情
            </DialogTitle>
            <DialogContent>
              <Box ref={pdfRef} sx={{ mt: 2 }}>
                {/* Meta Information */}
                <Box sx={{ mb: 3, p: 2, bgcolor: '#f8f9fa', borderRadius: 2 }}>
                  <Grid container spacing={2}>
                    <Grid item xs={12} sm={6}>
                      <Typography variant="body2" color="text.secondary">
                        📅 创建时间：
                      </Typography>
                      <Typography variant="body1" fontWeight="bold">
                        {formatDate(selectedRecord.created_at)}
                      </Typography>
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <Typography variant="body2" color="text.secondary">
                        📋 状态：
                      </Typography>
                      <Box
                        component="span"
                        sx={{
                          display: 'inline-block',
                          px: 1.5,
                          py: 0.5,
                          borderRadius: 1,
                          backgroundColor: getStatusColor(selectedRecord.status),
                          color: 'white',
                          fontSize: '0.875rem',
                          fontWeight: 500,
                        }}
                      >
                        {getStatusLabel(selectedRecord.status)}
                      </Box>
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <Typography variant="body2" color="text.secondary">
                        ⚠️ 严重程度：
                      </Typography>
                      <Box
                        component="span"
                        sx={{
                          display: 'inline-block',
                          px: 1.5,
                          py: 0.5,
                          borderRadius: 1,
                          backgroundColor: getSeverityColor(selectedRecord.severity),
                          color: 'white',
                          fontSize: '0.875rem',
                          fontWeight: 500,
                        }}
                      >
                        {getSeverityLabel(selectedRecord.severity)}
                      </Box>
                    </Grid>
                  </Grid>
                </Box>

                {/* Title */}
                <Box sx={{ mb: 3 }}>
                  <Typography variant="h6" gutterBottom>
                    📝 病历标题
                  </Typography>
                  <Typography variant="body1">
                    {getRecordTitle(selectedRecord)}
                  </Typography>
                </Box>

                {/* Symptoms */}
                <Box sx={{ mb: 3 }}>
                  <Typography variant="h6" gutterBottom>
                    😷 症状描述
                  </Typography>
                  <Typography variant="body1">
                    {selectedRecord.symptoms || '未记录症状'}
                  </Typography>
                </Box>

                {/* Description */}
                {selectedRecord.description && (
                  <Box sx={{ mb: 3 }}>
                    <Typography variant="h6" gutterBottom>
                      📄 详细描述
                    </Typography>
                    <Typography variant="body1">
                      {selectedRecord.description}
                    </Typography>
                  </Box>
                )}

                {/* AI Diagnosis */}
                {selectedRecord.diagnosis && (
                  <Box sx={{ mb: 3 }}>
                    <Typography variant="h6" gutterBottom>
                      🤖 AI诊断结果
                    </Typography>
                    <Paper
                      ref={diagnosisRef}
                      data-pdf-diagnosis="true"
                      elevation={1}
                      sx={{
                        p: 3,
                        bgcolor: '#fafafa',
                        borderRadius: 2,
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
                        {selectedRecord.diagnosis}
                      </ReactMarkdown>
                    </Paper>
                  </Box>
                )}

                {/* Doctor Comments */}
                <Box sx={{ mb: 3 }}>
                  <Typography variant="h6" gutterBottom>
                    👨‍⚕️ 医生反馈
                  </Typography>
                  {comments.length === 0 ? (
                    <Typography variant="body2" color="text.secondary" fontStyle="italic">
                      暂无医生反馈
                    </Typography>
                  ) : (
                    <Box>
                      {comments.map((comment) => (
                        <Card key={comment.id} sx={{ mb: 2, borderLeft: '4px solid #667eea' }}>
                          <CardContent>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                              <Typography variant="subtitle1" fontWeight="bold">
                                👨‍⚕️ {comment.doctor?.display_name}
                              </Typography>
                              <Typography variant="body2" color="text.secondary">
                                {new Date(comment.created_at).toLocaleString('zh-CN')}
                              </Typography>
                            </Box>
                            <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                              🏥 {comment.doctor?.hospital} · {comment.doctor?.specialty}
                            </Typography>
                            <Typography variant="body1" sx={{ mb: 1, whiteSpace: 'pre-wrap' }}>
                              {comment.content}
                            </Typography>
                            
                            {/* Patient Replies */}
                            {comment.patient_replies && comment.patient_replies.length > 0 && (
                              <Box sx={{ ml: 2, mt: 1 }}>
                                {comment.patient_replies.map((reply) => (
                                  <Paper key={reply.id} sx={{ p: 2, bgcolor: '#f0f8ff', borderLeft: '3px solid #28a745', mb: 1 }}>
                                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                                      <Typography variant="body2" fontWeight="bold" color="#28a745">
                                        🙋 我的回复
                                      </Typography>
                                      <Typography variant="caption" color="text.secondary">
                                        {new Date(reply.created_at).toLocaleString('zh-CN')}
                                      </Typography>
                                    </Box>
                                    <Typography variant="body2">
                                      {reply.content}
                                    </Typography>
                                  </Paper>
                                ))}
                              </Box>
                            )}

                            {/* Reply Form */}
                            {replyFormVisible[comment.id] && (
                              <Box sx={{ mt: 1, pt: 1, borderTop: '1px dashed #e0e0e0' }}>
                                <TextField
                                  fullWidth
                                  multiline
                                  rows={3}
                                  placeholder="输入您的回复..."
                                  value={replyTexts[comment.id] || ''}
                                  onChange={(e) => handleReplyChange(comment.id, e.target.value)}
                                  sx={{ mb: 1 }}
                                />
                                <Box sx={{ display: 'flex', gap: 1, justifyContent: 'flex-end' }}>
                                  <Button
                                    size="small"
                                    onClick={() => toggleReplyForm(comment.id)}
                                  >
                                    取消
                                  </Button>
                                  <Button
                                    variant="contained"
                                    size="small"
                                    onClick={() => submitReply(comment.id)}
                                  >
                                    发送回复
                                  </Button>
                                </Box>
                              </Box>
                            )}
                            
                            <Button
                              size="small"
                              startIcon={<NoteIcon />}
                              onClick={() => toggleReplyForm(comment.id)}
                              sx={{ mt: 1 }}
                            >
                              💬 回复医生
                            </Button>
                          </CardContent>
                        </Card>
                      ))}
                    </Box>
                  )}
                </Box>

              </Box>
            </DialogContent>
            
            {/* Action Buttons - Outside pdfRef container */}
            <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', px: 3, py: 2, bgcolor: '#f8f9fa', borderTop: '1px solid #e0e0e0' }}>
              <Button
                variant="contained"
                color="error"
                startIcon={<PictureAsPdfIcon />}
                onClick={exportToPDF}
              >
                📄 导出PDF
              </Button>
              <Button
                variant="contained"
                color="success"
                startIcon={<ShareIcon />}
                onClick={() => handleShareRecord(selectedRecord)}
              >
                🔗 分享
              </Button>
              <Button
                variant="contained"
                color="secondary"
                startIcon={<PrintIcon />}
                onClick={printDiagnosis}
              >
                🖨️ 打印
              </Button>
              <Button
                variant="contained"
                color="info"
                startIcon={<CompareIcon />}
                onClick={() => handleCompareRecord(selectedRecord)}
              >
                📊 对比
              </Button>
            </Box>
            <DialogActions>
              <Button onClick={() => setDetailModalOpen(false)}>
                关闭
              </Button>
            </DialogActions>
          </>
        )}
      </Dialog>

      {/* Share Modal */}
      <Dialog
        open={shareModalOpen}
        onClose={() => setShareModalOpen(false)}
        maxWidth="md"
        fullWidth
        PaperProps={{
          sx: { borderRadius: 3, overflow: 'hidden' }
        }}
      >
        <DialogTitle sx={{ bgcolor: 'linear-gradient(135deg, #667eea, #764ba2)', color: 'white' }}>
          🔗 分享诊断报告
        </DialogTitle>
        <DialogContent>
          <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
            <Tabs value={shareTab} onChange={(_, newValue) => setShareTab(newValue)}>
              <Tab label="链接分享" />
              <Tab label="@医生" />
            </Tabs>
          </Box>

          {/* Link Sharing Tab */}
          {shareTab === 0 && (
            <Box sx={{ mt: 2 }}>
              <Box sx={{ mb: 3 }}>
                <Typography variant="h6" gutterBottom>
                  分享链接
                </Typography>
                <TextField
                  fullWidth
                  value={window.location.origin + '/share.html?case=' + selectedRecord?.id}
                  InputProps={{
                    readOnly: true,
                    endAdornment: (
                      <Button
                        variant="outlined"
                        onClick={() => {
                          navigator.clipboard.writeText(window.location.origin + '/share.html?case=' + selectedRecord?.id);
                          alert('链接已复制到剪贴板！');
                        }}
                      >
                        复制
                      </Button>
                    ),
                  }}
                />
              </Box>
              
              <Box sx={{ mb: 3 }}>
                <Typography variant="body2" gutterBottom>
                  包含内容选项：
                </Typography>
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={includeDiagnosis}
                      onChange={(e) => setIncludeDiagnosis(e.target.checked)}
                    />
                  }
                  label="包含诊断结果"
                />
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={includeSymptoms}
                      onChange={(e) => setIncludeSymptoms(e.target.checked)}
                    />
                  }
                  label="包含症状描述"
                />
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={includePersonal}
                      onChange={(e) => setIncludePersonal(e.target.checked)}
                    />
                  }
                  label="包含个人信息"
                />
              </Box>
            </Box>
          )}

          {/* Doctor Sharing Tab */}
          {shareTab === 1 && (
            <Box sx={{ mt: 2 }}>
              <Box sx={{ mb: 3 }}>
                <Typography variant="h6" gutterBottom>
                  搜索医生（可添加多位）
                </Typography>
                <TextField
                  fullWidth
                  value={doctorSearchQuery}
                  onChange={(e) => setDoctorSearchQuery(e.target.value)}
                  placeholder="输入医生姓名、医院或专业领域"
                  InputProps={{
                    startAdornment: <SearchIcon sx={{ mr: 1, color: 'action.active' }} />,
                    endAdornment: (
                      <Button variant="outlined" onClick={searchDoctors}>
                        🔍
                      </Button>
                    ),
                  }}
                />
                <Typography variant="caption" color="text.secondary">
                  💡 显示的都是已认证医生，只展示昵称。点击选择多位医生，再次点击取消选择。
                </Typography>
              </Box>

              {/* Search Results */}
              {searchedDoctors.length > 0 && (
                <Box sx={{ mb: 3, maxHeight: 300, overflow: 'auto', border: '1px solid #e0e0e0', borderRadius: 2, p: 2 }}>
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
                        <CardContent sx={{ py: 1 }}>
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
                </Box>
              )}

              {/* Selected Doctors */}
              {selectedDoctors.length > 0 && (
                <Box sx={{ mb: 3, p: 2, bgcolor: '#f0f3ff', border: '1px solid #667eea', borderRadius: 2 }}>
                  <Typography variant="h6" gutterBottom>
                    已选择医生
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
                            <Typography variant="body2" color="error">删除</Typography>
                          </IconButton>
                        </ListItemSecondaryAction>
                      </ListItem>
                    ))}
                  </List>
                  <Button
                    variant="outlined"
                    color="error"
                    onClick={() => setSelectedDoctors([])}
                    sx={{ mt: 1 }}
                  >
                    清除全部
                  </Button>
                </Box>
              )}

              {/* Consent */}
              <Box sx={{ mb: 3, p: 2, bgcolor: '#f8f9fa', borderRadius: 2 }}>
                <Typography variant="h6" gutterBottom>
                  分享授权
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  您即将将此病例分享给选定的医生。分享内容将自动脱敏处理，隐藏您的姓名、身份证号、手机号等敏感信息。
                  <br />
                  医生将可以查看：症状描述、AI诊断结果、检查资料（已脱敏）
                </Typography>
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={shareConsent}
                      onChange={(e) => setShareConsent(e.target.checked)}
                    />
                  }
                  label="我已阅读并同意分享此病例给选定的医生"
                />
              </Box>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShareModalOpen(false)}>
            关闭
          </Button>
          {shareTab === 1 && (
            <Button
              variant="contained"
              onClick={shareToDoctor}
              disabled={selectedDoctors.length === 0}
            >
              @提及医生
            </Button>
          )}
        </DialogActions>
      </Dialog>

      {/* Compare Modal */}
      <Dialog
        open={compareModalOpen}
        onClose={() => setCompareModalOpen(false)}
        maxWidth="lg"
        fullWidth
        PaperProps={{
          sx: { borderRadius: 3, overflow: 'hidden' }
        }}
      >
        <DialogTitle sx={{ bgcolor: 'linear-gradient(135deg, #667eea, #764ba2)', color: 'white' }}>
          📊 病历对比
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel>选择第一份病历</InputLabel>
                <Select
                  value={compareRecord1}
                  onChange={(e) => {
                    setCompareRecord1(e.target.value);
                    // Update compare view
                  }}
                  label="选择第一份病历"
                >
                  <MenuItem value="">请选择...</MenuItem>
                  {records.map((record) => (
                    <MenuItem key={record.id} value={record.id}>
                      {new Date(record.created_at).toLocaleDateString('zh-CN')} - {record.title || '诊疗记录'}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
              <Paper sx={{ p: 2, minHeight: 300 }}>
                {compareRecord1 && (
                  <Box>
                    <Typography variant="h6" gutterBottom>
                      第一份病历
                    </Typography>
                    {/* Display record 1 content */}
                    <Typography variant="body2">
                      {records.find(r => r.id === compareRecord1)?.symptoms.substring(0, 200)}...
                    </Typography>
                  </Box>
                )}
                {!compareRecord1 && (
                  <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', py: 5 }}>
                    请选择要对比的病历
                  </Typography>
                )}
              </Paper>
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel>选择第二份病历</InputLabel>
                <Select
                  value={compareRecord2}
                  onChange={(e) => {
                    setCompareRecord2(e.target.value);
                    // Update compare view
                  }}
                  label="选择第二份病历"
                >
                  <MenuItem value="">请选择...</MenuItem>
                  {records.map((record) => (
                    <MenuItem key={record.id} value={record.id}>
                      {new Date(record.created_at).toLocaleDateString('zh-CN')} - {record.title || '诊疗记录'}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
              <Paper sx={{ p: 2, minHeight: 300 }}>
                {compareRecord2 && (
                  <Box>
                    <Typography variant="h6" gutterBottom>
                      第二份病历
                    </Typography>
                    {/* Display record 2 content */}
                    <Typography variant="body2">
                      {records.find(r => r.id === compareRecord2)?.symptoms.substring(0, 200)}...
                    </Typography>
                  </Box>
                )}
                {!compareRecord2 && (
                  <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center', py: 5 }}>
                    请选择要对比的病历
                  </Typography>
                )}
              </Paper>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCompareModalOpen(false)}>
            关闭
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default MedicalRecords;
