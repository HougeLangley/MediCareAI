import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Box,
  Button,
  TextField,
  Paper,
  Grid,
  CircularProgress,
  Alert,
  MenuItem,
  FormControlLabel,
  RadioGroup,
  Radio,
  FormControl,
  FormLabel,
} from '@mui/material';
import { ArrowBack as ArrowBackIcon, Save as SaveIcon } from '@mui/icons-material';
import { useForm, Controller } from 'react-hook-form';
import apiService from '../../services/api';
import { PatientCreate } from '../../types';

const CreatePatientPage: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const {
    control,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<PatientCreate>({
    defaultValues: {
      name: '',
      date_of_birth: '',
      gender: 'other',
      phone: '',
      address: '',
      emergency_contact: '',
      medical_record_number: '',
    },
  });

  const onSubmit = async (data: PatientCreate) => {
    try {
      setLoading(true);
      setError(null);
      setSuccess(false);

      await apiService.createPatient(data);
      setSuccess(true);

      // 延迟跳转以显示成功消息
      setTimeout(() => {
        navigate('/patients');
      }, 1500);
    } catch (err: any) {
      setError(err.detail || '创建患者失败');
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    navigate('/patients');
  };

  return (
    <Container maxWidth="md">
      <Box sx={{ mt: 4, mb: 6 }}>
        <Button
          startIcon={<ArrowBackIcon />}
          onClick={handleCancel}
          sx={{ mb: 2 }}
        >
          返回患者列表
        </Button>

        <Typography variant="h4" gutterBottom fontWeight="bold">
          创建新患者
        </Typography>
        <Typography variant="body1" color="textSecondary">
          填写患者基本信息以创建新的患者档案
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert severity="success" sx={{ mb: 3 }}>
          患者创建成功！正在跳转...
        </Alert>
      )}

      <Paper sx={{ p: 4 }}>
        <form onSubmit={handleSubmit(onSubmit)}>
          <Grid container spacing={3}>
            {/* 基本信息 */}
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom sx={{ mt: 1, mb: 2 }}>
                基本信息
              </Typography>
            </Grid>

            <Grid item xs={12} md={6}>
              <Controller
                name="name"
                control={control}
                rules={{
                  required: '患者姓名为必填项',
                  minLength: {
                    value: 2,
                    message: '姓名至少需要2个字符',
                  },
                }}
                render={({ field }) => (
                  <TextField
                    {...field}
                    fullWidth
                    label="患者姓名 *"
                    error={!!errors.name}
                    helperText={errors.name?.message}
                    disabled={loading || isSubmitting}
                  />
                )}
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <Controller
                name="date_of_birth"
                control={control}
                rules={{
                  required: '出生日期为必填项',
                }}
                render={({ field }) => (
                  <TextField
                    {...field}
                    fullWidth
                    label="出生日期 *"
                    type="date"
                    InputLabelProps={{ shrink: true }}
                    error={!!errors.date_of_birth}
                    helperText={errors.date_of_birth?.message}
                    disabled={loading || isSubmitting}
                  />
                )}
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <FormControl component="fieldset">
                <FormLabel component="legend">性别</FormLabel>
                <Controller
                  name="gender"
                  control={control}
                  render={({ field }) => (
                    <RadioGroup {...field} row>
                      <FormControlLabel
                        value="male"
                        control={<Radio />}
                        label="男"
                        disabled={loading || isSubmitting}
                      />
                      <FormControlLabel
                        value="female"
                        control={<Radio />}
                        label="女"
                        disabled={loading || isSubmitting}
                      />
                      <FormControlLabel
                        value="other"
                        control={<Radio />}
                        label="其他"
                        disabled={loading || isSubmitting}
                      />
                    </RadioGroup>
                  )}
                />
              </FormControl>
            </Grid>

            <Grid item xs={12} md={6}>
              <Controller
                name="medical_record_number"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    fullWidth
                    label="医疗记录号"
                    error={!!errors.medical_record_number}
                    helperText={errors.medical_record_number?.message || '唯一标识符'}
                    disabled={loading || isSubmitting}
                  />
                )}
              />
            </Grid>

            {/* 联系信息 */}
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom sx={{ mt: 2, mb: 2 }}>
                联系信息
              </Typography>
            </Grid>

            <Grid item xs={12} md={6}>
              <Controller
                name="phone"
                control={control}
                rules={{
                  pattern: {
                    value: /^1[3-9]\d{9}$/,
                    message: '请输入有效的手机号码',
                  },
                }}
                render={({ field }) => (
                  <TextField
                    {...field}
                    fullWidth
                    label="联系电话"
                    error={!!errors.phone}
                    helperText={errors.phone?.message}
                    disabled={loading || isSubmitting}
                  />
                )}
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <Controller
                name="emergency_contact"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    fullWidth
                    label="紧急联系人"
                    error={!!errors.emergency_contact}
                    helperText={errors.emergency_contact?.message}
                    disabled={loading || isSubmitting}
                  />
                )}
              />
            />
            </Grid>

            <Grid item xs={12}>
              <Controller
                name="address"
                control={control}
                render={({ field }) => (
                  <TextField
                    {...field}
                    fullWidth
                    multiline
                    rows={3}
                    label="地址"
                    error={!!errors.address}
                    helperText={errors.address?.message}
                    disabled={loading || isSubmitting}
                  />
                )}
              />
            </Grid>

            {/* 操作按钮 */}
            <Grid item xs={12} sx={{ mt: 4 }}>
              <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
                <Button
                  variant="outlined"
                  size="large"
                  onClick={handleCancel}
                  disabled={loading || isSubmitting}
                  sx={{ minWidth: 120 }}
                >
                  取消
                </Button>
                <Button
                  variant="contained"
                  size="large"
                  type="submit"
                  startIcon={loading || isSubmitting ? <CircularProgress size={20} /> : <SaveIcon />}
                  disabled={loading || isSubmitting}
                  sx={{ minWidth: 150, textTransform: 'none', fontWeight: 600 }}
                >
                  {loading || isSubmitting ? '保存中...' : '保存患者'}
                </Button>
              </Box>
            </Grid>
          </Grid>
        </form>
      </Paper>

      {/* 帮助信息 */}
      <Box sx={{ mt: 3, p: 2, bgcolor: 'info.light', borderRadius: 1 }}>
        <Typography variant="body2" color="info.dark">
          <strong>提示：</strong>所有标记为 * 的字段为必填项。医疗记录号是患者的唯一标识符，建议使用医院分配的病历号。
        </Typography>
      </Box>
    </Container>
  );
};

export default CreatePatientPage;
