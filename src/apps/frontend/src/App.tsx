import { useEffect } from 'react';
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from 'react-router-dom';
import { useAuthStore } from '@/stores/authStore';
import LandingPage from '@/pages/LandingPage';
import LoginPage from '@/pages/LoginPage';
import MFASetupPage from '@/pages/MFASetupPage';
import DashboardPage from '@/pages/DashboardPage';
import ProtectedRoute from '@/components/auth/ProtectedRoute';

function App() {
  const { checkAuth } = useAuthStore();

  useEffect(() => {
    // Check authentication status on app mount
    checkAuth();
  }, [checkAuth]);

  return (
    <Router>
      <div className="App">
        <Routes>
          {/* Public Routes */}
          <Route
            path="/"
            element={
              <ProtectedRoute requireAuth={false}>
                <LandingPage
                  onGetStarted={() => (window.location.href = '/login')}
                  onSignIn={() => (window.location.href = '/login')}
                />
              </ProtectedRoute>
            }
          />

          <Route
            path="/login"
            element={
              <ProtectedRoute requireAuth={false}>
                <LoginPage />
              </ProtectedRoute>
            }
          />

          {/* Protected Routes */}
          <Route
            path="/mfa-setup"
            element={
              <ProtectedRoute>
                <MFASetupPage />
              </ProtectedRoute>
            }
          />

          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <DashboardPage />
              </ProtectedRoute>
            }
          />

          {/* Catch-all route - redirect to landing */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
