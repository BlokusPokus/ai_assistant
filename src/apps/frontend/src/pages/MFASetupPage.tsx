import React, { useState, useEffect } from 'react';
import { Button, Card } from '@/components/ui';
import { Brain, ArrowLeft, Shield, Smartphone, Key } from 'lucide-react';
import MFAForm from '@/components/auth/MFAForm';
import { useAuthStore } from '@/stores/authStore';
import authService from '@/services/auth';
import type { MFASetupResponse } from '@/services/auth';

const MFASetupPage: React.FC = () => {
  const { user, logout } = useAuthStore();
  const [mfaData, setMfaData] = useState<MFASetupResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const setupMFA = async () => {
      if (!user) {
        setError('User not found');
        setIsLoading(false);
        return;
      }

      try {
        const data = await authService.setupMFA({
          user_id: user.id,
          mfa_type: 'totp',
        });
        setMfaData(data);
      } catch (err: unknown) {
        const error = err as { response?: { data?: { detail?: string } } };
        setError(error.response?.data?.detail || 'Failed to setup MFA');
      } finally {
        setIsLoading(false);
      }
    };

    setupMFA();
  }, [user]);

  const handleMFASuccess = async (formData: { code: string }) => {
    try {
      const result = await authService.verifyMFA({
        user_id: user!.id,
        mfa_code: formData.code,
        mfa_type: 'totp',
      });

      if (result.success) {
        // Redirect to dashboard
        window.location.href = '/dashboard';
      }
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } };
      setError(error.response?.data?.detail || 'Failed to verify MFA');
    }
  };

  const handleCancel = async () => {
    await logout();
    window.location.href = '/';
  };

  const handleBackToLogin = () => {
    window.location.href = '/login';
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Setting up MFA...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 flex items-center justify-center">
        <Card title="Setup Error" className="max-w-md mx-auto">
          <div className="text-center space-y-4">
            <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto">
              <Shield className="w-8 h-8 text-red-600" />
            </div>
            <h3 className="text-lg font-medium text-gray-900">
              MFA Setup Failed
            </h3>
            <p className="text-gray-600">{error}</p>
            <div className="flex space-x-3">
              <Button variant="secondary" onClick={handleBackToLogin}>
                Back to Login
              </Button>
              <Button
                variant="primary"
                onClick={() => window.location.reload()}
              >
                Try Again
              </Button>
            </div>
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 py-12 px-4">
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center space-x-2 mb-4">
            <Brain className="w-8 h-8 text-blue-600" />
            <span className="text-2xl font-bold text-gray-900">
              Personal Assistant TDAH
            </span>
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Secure Your Account
          </h1>
          <p className="text-gray-600">
            Set up two-factor authentication for enhanced security
          </p>
        </div>

        {/* Back Button */}
        <div className="mb-6">
          <Button
            variant="ghost"
            size="sm"
            onClick={handleCancel}
            className="text-gray-600 hover:text-gray-800"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Cancel Setup
          </Button>
        </div>

        {/* MFA Setup Form */}
        {mfaData && (
          <MFAForm
            type="setup"
            onSuccess={handleMFASuccess}
            onCancel={handleCancel}
            qrCode={mfaData.qr_code}
            backupCodes={mfaData.backup_codes}
            secretKey={mfaData.secret_key}
          />
        )}

        {/* Security Information */}
        <Card title="Why Two-Factor Authentication?" className="mt-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3">
                <Shield className="w-6 h-6 text-blue-600" />
              </div>
              <h4 className="font-medium text-gray-900 mb-2">
                Enhanced Security
              </h4>
              <p className="text-sm text-gray-600">
                Protect your account even if your password is compromised
              </p>
            </div>

            <div className="text-center">
              <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-3">
                <Smartphone className="w-6 h-6 text-green-600" />
              </div>
              <h4 className="font-medium text-gray-900 mb-2">Easy to Use</h4>
              <p className="text-sm text-gray-600">
                Simple setup with popular authenticator apps
              </p>
            </div>

            <div className="text-center">
              <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-3">
                <Key className="w-6 h-6 text-purple-600" />
              </div>
              <h4 className="font-medium text-gray-900 mb-2">Backup Codes</h4>
              <p className="text-sm text-gray-600">
                Access your account even without your phone
              </p>
            </div>
          </div>
        </Card>

        {/* Help Section */}
        <div className="mt-8 text-center text-sm text-gray-500">
          <p>
            Need help?{' '}
            <button className="text-blue-600 hover:underline">
              Contact support
            </button>{' '}
            or{' '}
            <button className="text-blue-600 hover:underline">
              View our guide
            </button>
          </p>
        </div>
      </div>
    </div>
  );
};

export default MFASetupPage;
