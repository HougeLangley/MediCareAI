import React from 'react';
import { Container, Typography, Box } from '@mui/material';

const RegisterPage: React.FC = () => {
  return (
    <Container>
      <Box sx={{ mt: 4, textAlign: 'center' }}>
        <Typography variant="h4">注册页面</Typography>
        <Typography variant="body1" sx={{ mt: 2 }}>
          注册功能正在开发中...
        </Typography>
      </Box>
    </Container>
  );
};

export default RegisterPage;