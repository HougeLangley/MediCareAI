import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, Outlet } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { LocalizationProvider } from '@mui/x-date-pickers';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFnsV3';
import { zhCN } from 'date-fns/locale';
import { Box, CircularProgress } from '@mui/material';

import { AuthProvider } from './contexts/AuthContext';
import { useAuth } from './hooks/useAuth';
import ErrorBoundary from './components/common/ErrorBoundary';

import LoginPage from './pages/auth/LoginPage';
import RegisterPage from './pages/auth/RegisterPage';
import PlatformSelect from './pages/auth/PlatformSelect';
import DoctorLoginPage from './pages/auth/DoctorLoginPage';
import DoctorRegister from './pages/auth/DoctorRegister';
import AdminLoginPage from './pages/auth/AdminLoginPage';

import PatientLayout from './components/layout/PatientLayout';
import PatientDashboard from './pages/patient/Dashboard';
import SymptomSubmit from './pages/patient/SymptomSubmit';
import MedicalRecords from './pages/patient/MedicalRecords';
import MedicalRecordDetail from './pages/patient/MedicalRecordDetail';
import PatientProfile from './pages/patient/Profile';
import CompleteProfile from './pages/patient/CompleteProfile';

import DoctorLayout from './components/layout/DoctorLayout';
import DoctorDashboard from './pages/doctor/Dashboard';
import DoctorMentions from './pages/doctor/Mentions';
import DoctorCases from './pages/doctor/Cases';
import DoctorCaseDetail from './pages/doctor/CaseDetail';
import DoctorProfile from './pages/doctor/Profile';
import DoctorExport from './pages/doctor/Export';
import DoctorMessages from './pages/doctor/Messages';

import AdminLayout from './components/layout/AdminLayout';
import AdminDashboard from './pages/admin/Dashboard';
import AdminDoctors from './pages/admin/Doctors';
import AdminKnowledgeBase from './pages/admin/KnowledgeBase';
import AdminAIModels from './pages/admin/AIModels';
import AdminLogs from './pages/admin/Logs';
import AdminMessages from './pages/admin/Messages';

const theme = createTheme({
  palette: {
    primary: {
      main: '#667eea',
    },
    secondary: {
      main: '#764ba2',
    },
    background: {
      default: '#f5f5f5',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
  },
});

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000,
      retry: 1,
    },
  },
});

const ProtectedRoute: React.FC<{ allowedRoles?: string[] }> = ({ allowedRoles }) => {
  const { isAuthenticated, user, isLoading } = useAuth();

  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
        <CircularProgress />
      </Box>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (allowedRoles && user && !allowedRoles.includes(user.role)) {
    return <Navigate to="/" replace />;
  }

  return <Outlet />;
};

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <LocalizationProvider dateAdapter={AdapterDateFns} adapterLocale={zhCN}>
          <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
            <AuthProvider>
              <ErrorBoundary>
                <Routes>
                  <Route path="/" element={<PlatformSelect />} />
                  <Route path="/login" element={<LoginPage />} />
                  <Route path="/register" element={<RegisterPage />} />
                  <Route path="/doctor-login" element={<DoctorLoginPage />} />
                  <Route path="/doctor-register" element={<DoctorRegister />} />
                  <Route path="/admin-login" element={<AdminLoginPage />} />
                  
                  <Route element={<ProtectedRoute allowedRoles={['patient']} />}>
                    <Route path="/patient" element={<PatientLayout />}>
                      <Route index element={<PatientDashboard />} />
                      <Route path="complete-profile" element={<CompleteProfile />} />
                      <Route path="symptom-submit" element={<SymptomSubmit />} />
                      <Route index element={<PatientDashboard />} />
                      <Route path="symptom-submit" element={<SymptomSubmit />} />
                      <Route path="medical-records" element={<MedicalRecords />} />
                      <Route path="medical-records/:id" element={<MedicalRecordDetail />} />
                      <Route path="profile" element={<PatientProfile />} />
                    </Route>
                  </Route>

                  <Route element={<ProtectedRoute allowedRoles={['doctor']} />}>
                    <Route path="/doctor" element={<DoctorLayout />}>
                      <Route index element={<DoctorDashboard />} />
                      <Route path="mentions" element={<DoctorMentions />} />
                      <Route path="cases" element={<DoctorCases />} />
                      <Route path="cases/:id" element={<DoctorCaseDetail />} />
                      <Route path="profile" element={<DoctorProfile />} />
                      <Route path="export" element={<DoctorExport />} />
                      <Route path="messages" element={<DoctorMessages />} />
                    </Route>
                  </Route>

                  <Route element={<ProtectedRoute allowedRoles={['admin']} />}>
                    <Route path="/admin" element={<AdminLayout />}>
                      <Route index element={<AdminDashboard />} />
                      <Route path="doctors" element={<AdminDoctors />} />
                      <Route path="knowledge-base" element={<AdminKnowledgeBase />} />
                      <Route path="ai-models" element={<AdminAIModels />} />
                      <Route path="messages" element={<AdminMessages />} />
                      <Route path="logs" element={<AdminLogs />} />
                    </Route>
                  </Route>

                  <Route path="*" element={<Navigate to="/" replace />} />
                </Routes>
              </ErrorBoundary>
            </AuthProvider>
          </Router>
        </LocalizationProvider>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;
