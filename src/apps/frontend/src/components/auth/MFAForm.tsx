import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { Button, Input, Card } from '@/components/ui';
import type { MFAFormData } from '@/types/auth';

interface MFAFormProps {
  type: 'setup' | 'verify';
  onSuccess?: (data: { code: string }) => void;
  onCancel?: () => void;
  qrCode?: string;
  backupCodes?: string[];
  secretKey?: string;
}

const MFAForm: React.FC<MFAFormProps> = ({
  type,
  onSuccess,
  onCancel,
  qrCode,
  backupCodes,
  secretKey,
}) => {
  const [showBackupCodes, setShowBackupCodes] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
    setValue,
  } = useForm<MFAFormData>({
    defaultValues: {
      code: '',
    },
  });

  const onSubmit = async (data: MFAFormData) => {
    if (onSuccess) {
      onSuccess(data);
    }
  };

  const handleInputChange = (value: string) => {
    setValue('code', value);
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  return (
    <Card
      title={
        type === 'setup'
          ? 'Set Up Two-Factor Authentication'
          : 'Verify Two-Factor Authentication'
      }
      padding="lg"
      className="max-w-md mx-auto"
    >
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        {type === 'setup' && (
          <>
            {/* QR Code Display */}
            {qrCode && (
              <div className="text-center space-y-4">
                <h3 className="text-lg font-medium text-gray-900">
                  Scan QR Code
                </h3>
                <div className="bg-white p-4 rounded-lg border-2 border-gray-200 inline-block">
                  <img
                    src={qrCode}
                    alt="QR Code for MFA setup"
                    className="w-48 h-48"
                  />
                </div>
                <p className="text-sm text-gray-600">
                  Scan this QR code with your authenticator app (Google
                  Authenticator, Authy, etc.)
                </p>
              </div>
            )}

            {/* Secret Key Display */}
            {secretKey && (
              <div className="space-y-3">
                <h3 className="text-lg font-medium text-gray-900">
                  Manual Entry
                </h3>
                <div className="bg-gray-50 p-3 rounded-md">
                  <div className="flex items-center justify-between">
                    <code className="text-sm font-mono text-gray-800">
                      {secretKey}
                    </code>
                    <Button
                      type="button"
                      variant="outline"
                      size="sm"
                      onClick={() => copyToClipboard(secretKey)}
                    >
                      Copy
                    </Button>
                  </div>
                </div>
                <p className="text-sm text-gray-600">
                  If you can't scan the QR code, enter this key manually in your
                  authenticator app
                </p>
              </div>
            )}

            {/* Backup Codes */}
            {backupCodes && backupCodes.length > 0 && (
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-medium text-gray-900">
                    Backup Codes
                  </h3>
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    onClick={() => setShowBackupCodes(!showBackupCodes)}
                  >
                    {showBackupCodes ? 'Hide' : 'Show'}
                  </Button>
                </div>

                {showBackupCodes && (
                  <div className="bg-yellow-50 p-4 rounded-md border border-yellow-200">
                    <p className="text-sm text-yellow-800 mb-3">
                      <strong>Important:</strong> Save these backup codes in a
                      secure location. You'll need them if you lose access to
                      your authenticator app.
                    </p>
                    <div className="grid grid-cols-2 gap-2">
                      {backupCodes.map((code, index) => (
                        <div
                          key={index}
                          className="bg-white p-2 rounded border text-center font-mono text-sm"
                        >
                          {code}
                        </div>
                      ))}
                    </div>
                    <Button
                      type="button"
                      variant="outline"
                      size="sm"
                      className="mt-3"
                      onClick={() => copyToClipboard(backupCodes.join('\n'))}
                    >
                      Copy All Codes
                    </Button>
                  </div>
                )}
              </div>
            )}
          </>
        )}

        {/* Verification Code Input */}
        <div className="space-y-3">
          <h3 className="text-lg font-medium text-gray-900">
            {type === 'setup' ? 'Enter Verification Code' : 'Enter Code'}
          </h3>
          <Input
            label="Authentication Code"
            type="text"
            placeholder="Enter 6-digit code"
            error={errors.code?.message}
            required
            {...register('code', {
              required: 'Authentication code is required',
              pattern: {
                value: /^\d{6}$/,
                message: 'Please enter a 6-digit code',
              },
            })}
            onChange={handleInputChange}
          />
          <p className="text-sm text-gray-600">
            {type === 'setup'
              ? 'Enter the 6-digit code from your authenticator app to complete setup'
              : 'Enter the 6-digit code from your authenticator app'}
          </p>
        </div>

        {/* Action Buttons */}
        <div className="flex space-x-3">
          {onCancel && (
            <Button
              type="button"
              variant="outline"
              onClick={onCancel}
              className="flex-1"
            >
              Cancel
            </Button>
          )}
          <Button type="submit" variant="primary" className="flex-1">
            {type === 'setup' ? 'Complete Setup' : 'Verify'}
          </Button>
        </div>

        {/* Help Text */}
        <div className="text-center text-sm text-gray-500">
          <p>
            Having trouble?{' '}
            <button type="button" className="text-blue-600 hover:underline">
              Contact support
            </button>
          </p>
        </div>
      </form>
    </Card>
  );
};

export default MFAForm;
