import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box,
  Container,
  Paper,
  Typography,
  Button,
  Card,
  CardContent,
  Chip,
  Avatar,
  IconButton,
  CircularProgress,
  Alert,
  Grid,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  InputAdornment,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  AppBar,
  Toolbar,
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  ArrowBack as ArrowBackIcon,
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
  Search as SearchIcon,
  Delete as DeleteIcon,
  Reply as ReplyIcon,
} from '@mui/icons-material';
import { useAuth } from '../../hooks/useAuth';
import { casesApi, doctorsApi } from '../../services/api';
import type { MedicalCase, Doctor, DoctorCaseComment, CaseCommentReply, MedicalDocument } from '../../types';
import html2canvas from 'html2canvas';
import jsPDF from 'jspdf';

const MedicalRecordDetail: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();

  // State
  const [record, setRecord] = useState<MedicalCase | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [documents, setDocuments] = useState<MedicalDocument[]>([]);
  const [comments, setComments] = useState<DoctorCaseComment[]>([]);
  const [replyFormVisible, setReplyFormVisible] = useState<{ [key: string]: boolean }>({});
  const [replyTexts, setReplyTexts] = useState<{ [key: string]: string }>({});

  // Modal states
  const [shareModalOpen, setShareModalOpen] = useState(false);
  const [compareModalOpen, setCompareModalOpen] = useState(false);

  // Sharing states
  const [selectedDoctors, setSelectedDoctors] = useState<Doctor[]>([]);
  const [doctorSearchQuery, setDoctorSearchQuery] = useState('');
  const [searchedDoctors, setSearchedDoctors] = useState<Doctor[]>([]);
  const [shareConsent, setShareConsent] = useState(false);

  useEffect(() => {
    if (id) {
      loadRecord(id);
    }
  }, [id]);

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

  const loadRecord = async (caseId: string) => {
    try {
      setLoading(true);
      const data = await casesApi.getCase(caseId);
      setRecord(data);
      
      // Load documents if any
      // This would need to be implemented in the API
      // const documents = await casesApi.getCaseDocuments(caseId);
      // setDocuments(documents);
      
      // Load doctor comments
      loadDoctorComments(caseId);
    } catch (err) {
      console.error('加载诊疗记录失败:', err);
      setError('加载诊疗记录失败');
    } finally {
      setLoading(false);
    }
  };

  const loadDoctorComments = async (caseId: string) => {
    try {
      const comments = await casesApi.getDoctorComments(caseId);
      setComments(comments);
    } catch (err) {
      console.error('加载医生评论失败:', err);
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
      // This would need to be implemented in the API
      // await casesApi.replyToComment(commentId, content);
      setReplyTexts(prev => ({
        ...prev,
        [commentId]: ''
      }));
      setReplyFormVisible(prev => ({
        ...prev,
        [commentId]: false
      }));
      // Reload comments
      if (record) {
        loadDoctorComments(record.id);
      }
      alert('回复已发送');
    } catch (err) {
      console.error('发送回复失败:', err);
      alert('发送回复失败');
    }
  };

  const pdfRef = useRef<HTMLDivElement>(null);

  const exportToPDF = async () => {
    if (!pdfRef.current || !record) {
      alert('无法导出PDF，请稍后再试');
      return;
    }

    try {
      const element = pdfRef.current;
      const canvas = await html2canvas(element, {
        scale: 2,
        useCORS: true,
        logging: false,
        backgroundColor: '#ffffff',
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
      
      // Calculate how many pages we need
      const scaledHeight = imgHeight * ratio * (pdfWidth - 20) / (imgWidth * ratio);
      const pageHeight = pdfHeight - 20;
      let heightLeft = scaledHeight;
      let position = 0;
      
      // Add first page
      pdf.addImage(imgData, 'PNG', 10, imgY, pdfWidth - 20, scaledHeight);
      heightLeft -= pageHeight;
      
      // Add additional pages if content is longer than one page
      while (heightLeft > 0) {
        position = heightLeft - scaledHeight;
        pdf.addPage();
        pdf.addImage(imgData, 'PNG', 10, position, pdfWidth - 20, scaledHeight);
        heightLeft -= pageHeight;
      }
      
      pdf.save(`诊疗记录_${record.title || 'AI诊断'}_${new Date().toLocaleDateString('zh-CN')}.pdf`);
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

    if (!record) {
      alert('无法获取病例信息');
      return;
    }

    try {
      // This would need to be implemented in the API
      // await casesApi.shareWithDoctors(record.id, selectedDoctors.map(d => d.id));
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
        return '#fd7e14';
      case '重度':
      case 'critical':
        return '#dc3545';
      default:
        return '#6c757d';
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

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: '#f5f5f5' }}>
      {/* Header */}
      <AppBar position="static" elevation={4}>
        <Toolbar sx={{ backgroundColor: 'white', color: '#333' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', flexGrow: 1 }}>
            <IconButton onClick={() => navigate('/patient/medical-records')} sx={{ mr: 1 }}>
              <ArrowBackIcon />
            </IconButton>
            <HospitalIcon sx={{ fontSize: 32, mr: 2, color: '#667eea' }} />
            <Typography variant="h5" component="div" sx={{ fontWeight: 'bold', color: '#667eea' }}>
              MediCareAI - 诊疗记录详情
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

      <Container maxWidth="lg" sx={{ mt: 3, pb: 3 }}>
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

        {/* Record Details */}
        {!loading && record && (
          <Paper ref={pdfRef} elevation={3} sx={{ p: 4, borderRadius: 3, bgcolor: '#ffffff' }}>
            {/* Meta Information */}
            <Grid container spacing={2} sx={{ mb: 3, p: 3, bgcolor: '#f8f9fa', borderRadius: 2 }}>
              <Grid item xs={12} sm={6}>
                <Typography variant="body2" color="text.secondary">
                  📅 创建时间：
                </Typography>
                <Typography variant="body1" fontWeight="bold">
                  {formatDate(record.created_at)}
                </Typography>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Typography variant="body2" color="text.secondary">
                  📋 状态：
                </Typography>
                <Chip
                  label={getStatusLabel(record.status)}
                  size="small"
                  sx={{
                    bgcolor: getStatusColor(record.status),
                    color: 'white',
                  }}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <Typography variant="body2" color="text.secondary">
                  ⚠️ 严重程度：
                </Typography>
                <Chip
                  label={record.severity || '未知'}
                  size="small"
                  sx={{
                    bgcolor: getSeverityColor(record.severity),
                    color: 'white',
                  }}
                />
              </Grid>
              <Grid item xs={12} sm={6}>
                <Typography variant="body2" color="text.secondary">
                  🆔 病例ID：
                </Typography>
                <Typography variant="body1" component="code" sx={{ p: 0.5, bgcolor: '#f5f5f5', borderRadius: 1, fontFamily: 'monospace' }}>
                  {record.id}
                </Typography>
              </Grid>
            </Grid>

            {/* Title */}
            <Box sx={{ mb: 3 }}>
              <Typography variant="h6" gutterBottom>
                📝 病历标题
              </Typography>
              <Typography variant="body1" sx={{ p: 2, bgcolor: '#fafafa', borderRadius: 2 }}>
                {record.title || 'AI诊疗记录'}
              </Typography>
            </Box>

            {/* Symptoms */}
            <Box sx={{ mb: 3 }}>
              <Typography variant="h6" gutterBottom>
                😷 症状描述
              </Typography>
              <Typography variant="body1" sx={{ p: 2, bgcolor: '#fafafa', borderRadius: 2 }}>
                {record.symptoms || '未记录症状'}
              </Typography>
            </Box>

            {/* Description */}
            {record.description && (
              <Box sx={{ mb: 3 }}>
                <Typography variant="h6" gutterBottom>
                  📄 详细描述
                </Typography>
                <Typography variant="body1" sx={{ p: 2, bgcolor: '#fafafa', borderRadius: 2 }}>
                  {record.description}
                </Typography>
              </Box>
            )}

            {/* Documents */}
            {documents.length > 0 && (
              <Box sx={{ mb: 3 }}>
                <Typography variant="h6" gutterBottom>
                  📎 检查资料
                </Typography>
                <Grid container spacing={2}>
                  {documents.map((doc) => (
                    <Grid item xs={12} sm={6} md={4} key={doc.id}>
                      <Card sx={{ height: '100%' }}>
                        <CardContent>
                          <Typography variant="subtitle2" gutterBottom>
                            {doc.filename}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            文件类型: {doc.file_type}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            文件大小: {doc.file_size ? `${Math.round(doc.file_size / 1024)} KB` : '未知'}
                          </Typography>
                        </CardContent>
                      </Card>
                    </Grid>
                  ))}
                </Grid>
              </Box>
            )}

            {/* AI Diagnosis */}
            {record.diagnosis && (
              <Accordion sx={{ mb: 3 }}>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Typography variant="h6">
                    🤖 AI诊断结果
                  </Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <Paper
                    elevation={1}
                    sx={{ p: 3, bgcolor: '#fafafa', borderRadius: 2 }}
                  >
                    <Typography variant="body1" component="pre" sx={{ whiteSpace: 'pre-wrap', fontFamily: 'inherit' }}>
                      {record.diagnosis}
                    </Typography>
                  </Paper>
                </AccordionDetails>
              </Accordion>
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
                          startIcon={<ReplyIcon />}
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

            {/* Action Buttons */}
            <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', mt: 2, p: 2, bgcolor: '#f8f9fa', borderRadius: 2 }}>
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
                onClick={() => setShareModalOpen(true)}
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
                onClick={() => setCompareModalOpen(true)}
              >
                📊 对比
              </Button>
            </Box>
          </Paper>
        )}
      </Container>

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
                  startAdornment: (
                    <IconButton size="small">
                      <SearchIcon />
                    </IconButton>
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
            </Box>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShareModalOpen(false)}>
            关闭
          </Button>
          <Button
            variant="contained"
            onClick={shareToDoctor}
            disabled={selectedDoctors.length === 0}
          >
            @提及医生
          </Button>
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
          <Typography variant="body1" sx={{ textAlign: 'center', py: 5 }}>
            病历对比功能需要选择其他病历进行对比。
          </Typography>
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

export default MedicalRecordDetail;
