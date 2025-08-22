import React, { useState } from 'react';
import { Button } from '@/components/ui';
import { Brain, ArrowLeft, CheckCircle } from 'lucide-react';
import LoginForm from '@/components/auth/LoginForm';
import RegisterForm from '@/components/auth/RegisterForm';
import { useAuthStore } from '@/stores/authStore';

type AuthMode = 'login' | 'register';

const LoginPage: React.FC = () => {
  const [authMode, setAuthMode] = useState<AuthMode>('login');
  const [registrationSuccess, setRegistrationSuccess] = useState(false);
  const { isAuthenticated } = useAuthStore();

  // Redirect if already authenticated
  React.useEffect(() => {
    if (isAuthenticated) {
      window.location.href = '/dashboard';
    }
  }, [isAuthenticated]);

  const handleAuthSuccess = () => {
    // Redirect to dashboard on successful authentication
    window.location.href = '/dashboard';
  };

  const handleRegistrationSuccess = () => {
    setRegistrationSuccess(true);
    // Auto-switch to login after 2 seconds
    setTimeout(() => {
      setAuthMode('login');
      setRegistrationSuccess(false);
    }, 2000);
  };

  const handleBackToLanding = () => {
    window.location.href = '/';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 flex items-center justify-center py-12 px-4">
      <div className="w-full max-w-md">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center space-x-2 mb-4">
            <Brain className="w-8 h-8 text-blue-600" />
            <span className="text-2xl font-bold text-gray-900">
              Personal Assistant TDAH
            </span>
          </div>
          <p className="text-gray-600">
            {authMode === 'login'
              ? 'Welcome back! Sign in to your account'
              : 'Create your account to get started'}
          </p>
        </div>

        {/* Back to Landing Button */}
        <div className="mb-6">
          <Button
            variant="ghost"
            size="sm"
            onClick={handleBackToLanding}
            className="text-gray-600 hover:text-gray-800"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Home
          </Button>
        </div>

        {/* Registration Success Message */}
        {registrationSuccess && (
          <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg">
            <div className="flex items-center space-x-2 text-green-800">
              <CheckCircle className="w-5 h-5" />
              <span className="font-medium">Registration successful!</span>
            </div>
            <p className="text-green-700 text-sm mt-1">
              Your account has been created. You can now sign in.
            </p>
          </div>
        )}

        {/* Auth Forms */}
        {authMode === 'login' ? (
          <LoginForm
            onSuccess={handleAuthSuccess}
            onSwitchToRegister={() => setAuthMode('register')}
          />
        ) : (
          <RegisterForm
            onSuccess={handleRegistrationSuccess}
            onSwitchToLogin={() => setAuthMode('login')}
          />
        )}

        {/* Additional Info */}
        <div className="mt-8 text-center text-sm text-gray-500">
          <p>
            By continuing, you agree to our{' '}
            <button className="text-blue-600 hover:underline">
              Terms of Service
            </button>{' '}
            and{' '}
            <button className="text-blue-600 hover:underline">
              Privacy Policy
            </button>
          </p>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
