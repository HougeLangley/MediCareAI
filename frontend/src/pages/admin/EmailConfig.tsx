import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  Divider,
  Alert,
  Chip,
  Tooltip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemSecondaryAction,
  CircularProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Grid,
} from '@mui/material';
import {
  ExpandMore,
  Add,
  Edit,
  Delete,
  CheckCircle,
  Error,
  Warning,
  Refresh,
  Send,
  Settings,
  Help,
  Email,
} from '@mui/icons-material';
import { adminApi } from '../../services/api';
import type {
  EmailProviderPreset,
  ProviderCategory,
  EmailConfig,
} from '../../types';

interface EmailConfigFormData {
  smtp_host: string;
  smtp_port: number;
  smtp_user: string;
  smtp_password: string;
  smtp_from_email: string;
  smtp_from_name: string;
  smtp_use_tls: boolean;
  description: string;
}

const defaultFormData: EmailConfigFormData = {
  smtp_host: '',
  smtp_port: 587,
  smtp_user: '',
  smtp_password: '',
  smtp_from_email: '',
  smtp_from_name: 'MediCareAI',
  smtp_use_tls: true,
  description: '',
};

const EmailConfigPage: React.FC = () => {
  // 状态管理
  const [providers, setProviders] = useState<EmailProviderPreset[]>([]);
  const [categories, setCategories] = useState<Record<string, ProviderCategory>>({});
  const [configs, setConfigs] = useState<EmailConfig[]>([]);
  const [serviceStatus, setServiceStatus] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // 表单状态
  const [selectedProvider, setSelectedProvider] = useState<string>('');
  const [formData, setFormData] = useState<EmailConfigFormData>(defaultFormData);
  const [isCustom, setIsCustom] = useState(false);

  // 对话框状态
  const [openDialog, setOpenDialog] = useState(false);
  const [editingConfig, setEditingConfig] = useState<EmailConfig | null>(null);
  const [testEmail, setTestEmail] = useState('');
  const [testDialogOpen, setTestDialogOpen] = useState(false);
  const [testingConfigId, setTestingConfigId] = useState<string>('');

  // 加载数据
  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [providersRes, configsRes, statusRes] = await Promise.all([
        adminApi.getEmailProviderPresets(),
        adminApi.getEmailConfigs(),
        adminApi.getEmailServiceStatus(),
      ]);
      setProviders(providersRes.providers);
      setCategories(providersRes.categories);
      setConfigs(configsRes.configs);
      setServiceStatus(statusRes);
    } catch (err: any) {
      setError(err.message || '加载数据失败');
    } finally {
      setLoading(false);
    }
  };

  // 处理服务商选择
  const handleProviderChange = (providerId: string) => {
    setSelectedProvider(providerId);
    const provider = providers.find((p) => p.id === providerId);

    if (provider) {
      if (provider.id === 'custom') {
        setIsCustom(true);
        setFormData(defaultFormData);
      } else {
        setIsCustom(false);
        // 自动填充配置
        setFormData({
          smtp_host: provider.smtp.host,
          smtp_port: provider.smtp.port,
          smtp_user: '',
          smtp_password: '',
          smtp_from_email: '',
          smtp_from_name: 'MediCareAI',
          smtp_use_tls: provider.smtp.useTLS,
          description: provider.description,
        });
      }
    }
  };

  // 保存配置
  const handleSave = async () => {
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      if (editingConfig) {
        await adminApi.updateEmailConfig(editingConfig.id, formData);
        setSuccess('配置更新成功');
      } else {
        await adminApi.createEmailConfig(formData);
        setSuccess('配置创建成功');
      }
      setOpenDialog(false);
      loadData();
    } catch (err: any) {
      setError(err.message || '保存失败');
    } finally {
      setLoading(false);
    }
  };

  // 删除配置
  const handleDelete = async (id: string) => {
    if (!window.confirm('确定要删除这个配置吗？')) return;

    setLoading(true);
    try {
      await adminApi.deleteEmailConfig(id);
      setSuccess('配置删除成功');
      loadData();
    } catch (err: any) {
      setError(err.message || '删除失败');
    } finally {
      setLoading(false);
    }
  };

  // 测试配置
  const handleTest = async () => {
    if (!testEmail) {
      setError('请输入测试邮箱地址');
      return;
    }

    setLoading(true);
    try {
      const result = await adminApi.testEmailConfig(testingConfigId, testEmail);
      if (result.success) {
        setSuccess(`测试邮件发送成功：${result.message}`);
      } else {
        setError(`测试失败：${result.message}`);
      }
      setTestDialogOpen(false);
      loadData();
    } catch (err: any) {
      setError(err.message || '测试失败');
    } finally {
      setLoading(false);
    }
  };

  // 设为默认
  const handleSetDefault = async (id: string) => {
    setLoading(true);
    try {
      await adminApi.setDefaultEmailConfig(id);
      setSuccess('已设为默认配置');
      loadData();
    } catch (err: any) {
      setError(err.message || '设置失败');
    } finally {
      setLoading(false);
    }
  };

  // 打开编辑对话框
  const openEditDialog = (config?: EmailConfig) => {
    if (config) {
      setEditingConfig(config);
      setFormData({
        smtp_host: config.smtp_host,
        smtp_port: config.smtp_port,
        smtp_user: config.smtp_user,
        smtp_password: '', // 密码不回显
        smtp_from_email: config.smtp_from_email,
        smtp_from_name: config.smtp_from_name,
        smtp_use_tls: config.smtp_use_tls,
        description: config.description || '',
      });
      setIsCustom(true);
      setSelectedProvider('custom');
    } else {
      setEditingConfig(null);
      setFormData(defaultFormData);
      setSelectedProvider('');
      setIsCustom(false);
    }
    setOpenDialog(true);
  };

  // 打开测试对话框
  const openTestDialog = (configId: string) => {
    setTestingConfigId(configId);
    setTestEmail('');
    setTestDialogOpen(true);
  };

  // 获取分类下的服务商
  const getProvidersByCategory = (category: string) => {
    return providers.filter((p) => p.category === category);
  };

  // 获取当前选中服务商的帮助信息
  const getSelectedProviderHelp = () => {
    const provider = providers.find((p) => p.id === selectedProvider);
    return provider;
  };

  if (loading && !configs.length) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        邮件服务配置
      </Typography>

      {/* 服务状态 */}
      {serviceStatus && (
        <Alert
          severity={serviceStatus.is_available ? 'success' : 'warning'}
          sx={{ mb: 3 }}
          icon={serviceStatus.is_available ? <CheckCircle /> : <Warning />}
        >
          <Typography variant="subtitle2">
            邮件服务状态：{serviceStatus.is_available ? '可用' : '未配置'}
          </Typography>
          {serviceStatus.is_available && (
            <Typography variant="body2">
              配置来源：{serviceStatus.config_source === 'database' ? '数据库配置' : '环境变量'}
              {serviceStatus.smtp_host && ` | SMTP: ${serviceStatus.smtp_host}:${serviceStatus.smtp_port}`}
            </Typography>
          )}
        </Alert>
      )}

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess('')}>
          {success}
        </Alert>
      )}

      {/* 配置列表 */}
      <Paper sx={{ mb: 3 }}>
        <Box sx={{ p: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h6">SMTP配置列表</Typography>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => openEditDialog()}
          >
            添加配置
          </Button>
        </Box>
        <Divider />
        <List>
          {configs.map((config) => (
            <ListItem
              key={config.id}
              sx={{
                bgcolor: config.is_default ? 'success.light' : 'inherit',
                '&:hover': { bgcolor: config.is_default ? 'success.light' : 'action.hover' },
              }}
            >
              <ListItemIcon>
                <Email color={config.is_active ? 'primary' : 'disabled'} />
              </ListItemIcon>
              <ListItemText
                primary={
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Typography variant="subtitle1">
                      {config.smtp_host}:{config.smtp_port}
                    </Typography>
                    {config.is_default && (
                      <Chip label="默认" color="success" size="small" />
                    )}
                    {!config.is_active && (
                      <Chip label="已禁用" color="default" size="small" />
                    )}
                  </Box>
                }
                secondary={
                  <Box>
                    <Typography variant="body2" color="text.secondary">
                      发件人: {config.smtp_from_name} &lt;{config.smtp_from_email}&gt;
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      测试状态:{' '}
                      {config.test_status === 'success' ? (
                        <span style={{ color: 'green' }}>✓ 通过</span>
                      ) : config.test_status === 'failed' ? (
                        <span style={{ color: 'red' }}>✗ 失败</span>
                      ) : (
                        <span>未测试</span>
                      )}
                      {config.tested_at && ` (${new Date(config.tested_at).toLocaleString()})`}
                    </Typography>
                  </Box>
                }
              />
              <ListItemSecondaryAction>
                <Tooltip title="测试">
                  <IconButton onClick={() => openTestDialog(config.id)}>
                    <Send />
                  </IconButton>
                </Tooltip>
                {!config.is_default && (
                  <Tooltip title="设为默认">
                    <IconButton onClick={() => handleSetDefault(config.id)}>
                      <CheckCircle />
                    </IconButton>
                  </Tooltip>
                )}
                <Tooltip title="编辑">
                  <IconButton onClick={() => openEditDialog(config)}>
                    <Edit />
                  </IconButton>
                </Tooltip>
                <Tooltip title="删除">
                  <IconButton onClick={() => handleDelete(config.id)} color="error">
                    <Delete />
                  </IconButton>
                </Tooltip>
              </ListItemSecondaryAction>
            </ListItem>
          ))}
          {configs.length === 0 && (
            <ListItem>
              <ListItemText
                primary="暂无配置"
                secondary="点击右上角按钮添加SMTP配置"
              />
            </ListItem>
          )}
        </List>
      </Paper>

      {/* 添加/编辑配置对话框 */}
      <Dialog
        open={openDialog}
        onClose={() => setOpenDialog(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          {editingConfig ? '编辑配置' : '添加邮件配置'}
        </DialogTitle>
        <DialogContent>
          {!editingConfig && (
            <Box sx={{ mb: 3 }}>
              <Typography variant="subtitle2" gutterBottom>
                选择邮箱服务商（将自动填充配置）
              </Typography>

              {/* 国内主流 */}
              {categories.domestic && (
                <Accordion defaultExpanded>
                  <AccordionSummary expandIcon={<ExpandMore />}>
                    <Typography>
                      {categories.domestic.icon} {categories.domestic.label}
                      <Typography variant="caption" color="text.secondary" sx={{ ml: 1 }}>
                        {categories.domestic.description}
                      </Typography>
                    </Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Grid container spacing={2}>
                      {getProvidersByCategory('domestic').map((provider) => (
                        <Grid item xs={12} sm={6} md={4} key={provider.id}>
                          <Paper
                            sx={{
                              p: 2,
                              cursor: 'pointer',
                              border: selectedProvider === provider.id ? 2 : 1,
                              borderColor: selectedProvider === provider.id ? 'primary.main' : 'divider',
                              '&:hover': { borderColor: 'primary.main' },
                            }}
                            onClick={() => handleProviderChange(provider.id)}
                          >
                            <Typography variant="h6">{provider.icon}</Typography>
                            <Typography variant="subtitle2">{provider.name}</Typography>
                            <Typography variant="caption" color="text.secondary">
                              {provider.description}
                            </Typography>
                          </Paper>
                        </Grid>
                      ))}
                    </Grid>
                  </AccordionDetails>
                </Accordion>
              )}

              {/* 国际服务 */}
              {categories.international && (
                <Accordion>
                  <AccordionSummary expandIcon={<ExpandMore />}>
                    <Typography>
                      {categories.international.icon} {categories.international.label}
                      <Typography variant="caption" color="text.secondary" sx={{ ml: 1 }}>
                        {categories.international.description}
                      </Typography>
                    </Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Grid container spacing={2}>
                      {getProvidersByCategory('international').map((provider) => (
                        <Grid item xs={12} sm={6} md={4} key={provider.id}>
                          <Paper
                            sx={{
                              p: 2,
                              cursor: 'pointer',
                              border: selectedProvider === provider.id ? 2 : 1,
                              borderColor: selectedProvider === provider.id ? 'primary.main' : 'divider',
                              '&:hover': { borderColor: 'primary.main' },
                            }}
                            onClick={() => handleProviderChange(provider.id)}
                          >
                            <Typography variant="h6">{provider.icon}</Typography>
                            <Typography variant="subtitle2">{provider.name}</Typography>
                            <Typography variant="caption" color="text.secondary">
                              {provider.description}
                            </Typography>
                          </Paper>
                        </Grid>
                      ))}
                    </Grid>
                  </AccordionDetails>
                </Accordion>
              )}

              {/* 自定义 */}
              {categories.custom && (
                <Accordion>
                  <AccordionSummary expandIcon={<ExpandMore />}>
                    <Typography>
                      {categories.custom.icon} {categories.custom.label}
                    </Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Paper
                      sx={{
                        p: 2,
                        cursor: 'pointer',
                        border: selectedProvider === 'custom' ? 2 : 1,
                        borderColor: selectedProvider === 'custom' ? 'primary.main' : 'divider',
                      }}
                      onClick={() => handleProviderChange('custom')}
                    >
                      <Typography variant="h6">⚙️</Typography>
                      <Typography variant="subtitle2">自定义配置</Typography>
                      <Typography variant="caption" color="text.secondary">
                        手动输入SMTP服务器信息
                      </Typography>
                    </Paper>
                  </AccordionDetails>
                </Accordion>
              )}
            </Box>
          )}

          <Divider sx={{ my: 2 }} />

          {/* 配置表单 */}
          <Typography variant="subtitle2" gutterBottom>
            SMTP配置
          </Typography>

          {selectedProvider && !editingConfig && (
            <Alert severity="info" sx={{ mb: 2 }}>
              <Typography variant="body2">
                <strong>提示：</strong>
                {getSelectedProviderHelp()?.helpText}
              </Typography>
              {getSelectedProviderHelp()?.helpLink && (
                <Button
                  size="small"
                  href={getSelectedProviderHelp()?.helpLink || ''}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  查看帮助文档
                </Button>
              )}
            </Alert>
          )}

          <Grid container spacing={2}>
            <Grid item xs={12} sm={8}>
              <TextField
                fullWidth
                label="SMTP服务器"
                value={formData.smtp_host}
                onChange={(e) => setFormData({ ...formData, smtp_host: e.target.value })}
                placeholder="如: smtp.qq.com"
                disabled={!isCustom && !editingConfig}
              />
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField
                fullWidth
                label="端口"
                type="number"
                value={formData.smtp_port}
                onChange={(e) => setFormData({ ...formData, smtp_port: parseInt(e.target.value) })}
                disabled={!isCustom && !editingConfig}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="用户名"
                value={formData.smtp_user}
                onChange={(e) => setFormData({ ...formData, smtp_user: e.target.value })}
                placeholder="如: your-qq@qq.com"
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="密码/授权码"
                type="password"
                value={formData.smtp_password}
                onChange={(e) => setFormData({ ...formData, smtp_password: e.target.value })}
                placeholder={editingConfig ? '留空表示不修改' : '输入授权码或密码'}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="发件人邮箱"
                value={formData.smtp_from_email}
                onChange={(e) => setFormData({ ...formData, smtp_from_email: e.target.value })}
                placeholder="如: noreply@medicare.ai"
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="发件人名称"
                value={formData.smtp_from_name}
                onChange={(e) => setFormData({ ...formData, smtp_from_name: e.target.value })}
                placeholder="如: MediCareAI"
              />
            </Grid>
            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Switch
                    checked={formData.smtp_use_tls}
                    onChange={(e) => setFormData({ ...formData, smtp_use_tls: e.target.checked })}
                  />
                }
                label="使用TLS加密（推荐）"
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="配置描述"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                placeholder="可选：添加配置说明"
                multiline
                rows={2}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>取消</Button>
          <Button
            variant="contained"
            onClick={handleSave}
            disabled={!formData.smtp_host || !formData.smtp_user}
          >
            保存
          </Button>
        </DialogActions>
      </Dialog>

      {/* 测试对话框 */}
      <Dialog open={testDialogOpen} onClose={() => setTestDialogOpen(false)}>
        <DialogTitle>测试邮件配置</DialogTitle>
        <DialogContent>
          <Typography variant="body2" sx={{ mb: 2 }}>
            输入一个邮箱地址接收测试邮件：
          </Typography>
          <TextField
            fullWidth
            label="测试邮箱地址"
            type="email"
            value={testEmail}
            onChange={(e) => setTestEmail(e.target.value)}
            placeholder="your-email@example.com"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setTestDialogOpen(false)}>取消</Button>
          <Button
            variant="contained"
            onClick={handleTest}
            disabled={!testEmail || loading}
            startIcon={loading ? <CircularProgress size={20} /> : <Send />}
          >
            发送测试邮件
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default EmailConfigPage;
