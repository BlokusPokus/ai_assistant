import { useEffect } from 'react';
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from 'react-router-dom';
import { useAuthStore } from '@/stores/authStore';
import LandingPage from '@/pages/LandingPage';
import WaitListLandingPage from '@/pages/WaitListLandingPage';
import LoginPage from '@/pages/LoginPage';
import MFASetupPage from '@/pages/MFASetupPage';
import DashboardLayout from '@/components/dashboard/DashboardLayout';
import {
  DashboardHome,
  ProfilePage,
  SettingsPage,
  SecurityPage,
  ChatPage,
  CalendarPage,
  NotesPage,
  OAuthIntegrationsPage,
  SMSAnalyticsPage,
  AdminAnalyticsPage,
} from '@/pages/dashboard';
import { OAuthSettingsPage } from '@/components/oauth-settings';
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
                <WaitListLandingPage
                  onJoinWaitlist={email => {
                    console.log('Joined waitlist:', email);
                    // Add your waitlist logic here
                  }}
                  onSignIn={() => (window.location.href = '/login')}
                />
              </ProtectedRoute>
            }
          />

          <Route
            path="/original"
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

          {/* Dashboard Routes with Layout */}
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <DashboardLayout />
              </ProtectedRoute>
            }
          >
            <Route index element={<DashboardHome />} />
            <Route path="profile" element={<ProfilePage />} />
            <Route path="settings" element={<SettingsPage />} />
            <Route path="security" element={<SecurityPage />} />
            <Route path="chat" element={<ChatPage />} />
            <Route path="calendar" element={<CalendarPage />} />
            <Route path="notes" element={<NotesPage />} />
            <Route path="integrations" element={<OAuthIntegrationsPage />} />
            <Route path="oauth-settings" element={<OAuthSettingsPage />} />
            <Route path="sms-analytics" element={<SMSAnalyticsPage />} />
            <Route path="admin-analytics" element={<AdminAnalyticsPage />} />
          </Route>

          {/* Catch-all route - redirect to landing */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
