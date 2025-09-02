import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import {
  Button,
  Input,
  Card,
  CardHeader,
  CardTitle,
  CardContent,
} from '@/components/ui';
import { useAuthStore } from '@/stores/authStore';
import type { RegisterFormData } from '@/types/auth';
import { CheckCircle, ArrowLeft, Phone } from 'lucide-react';

interface RegisterFormProps {
  onSuccess?: () => void;
  onSwitchToLogin?: () => void;
}

const RegisterForm: React.FC<RegisterFormProps> = ({
  onSuccess,
  onSwitchToLogin,
}) => {
  const {
    register: registerUser,
    isLoading,
    error,
    clearError,
  } = useAuthStore();

  // Phone verification state
  const [verificationStep, setVerificationStep] = useState<'form' | 'verify'>(
    'form'
  );
  const [phoneToVerify, setPhoneToVerify] = useState('');
  const [verificationCode, setVerificationCode] = useState('');
  const [isVerifying, setIsVerifying] = useState(false);
  const [verificationError, setVerificationError] = useState<string | null>(
    null
  );
  const [verificationSent, setVerificationSent] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
    setValue,
    watch,
  } = useForm<RegisterFormData>({
    defaultValues: {
      email: '',
      password: '',
      confirmPassword: '',
      fullName: '',
      phoneNumber: '',
    },
  });

  const password = watch('password');

  const onSubmit = async (data: RegisterFormData) => {
    clearError();
    setVerificationError(null);

    // If phone number is provided, go to verification step
    if (data.phoneNumber && data.phoneNumber.trim()) {
      setPhoneToVerify(data.phoneNumber);
      setVerificationStep('verify');
      await sendVerificationCode(data.phoneNumber);
      return;
    }

    // If no phone number, proceed with registration
    const success = await registerUser({
      email: data.email,
      password: data.password,
      full_name: data.fullName,
      phone_number: undefined,
    });
    if (success && onSuccess) {
      onSuccess();
    }
  };

  const sendVerificationCode = async (phoneNumber: string) => {
    setIsVerifying(true);
    setVerificationError(null);

    try {
      // First create the user account
      const registerResponse = await registerUser({
        email: watch('email'),
        password: watch('password'),
        full_name: watch('fullName'),
        phone_number: phoneNumber,
      });

      if (!registerResponse) {
        throw new Error('Failed to create account');
      }

      // Then send verification code
      const response = await fetch('/api/v1/users/me/phone-numbers/verify', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify({
          phone_number: phoneNumber,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to send verification code');
      }

      setVerificationSent(true);
    } catch (err) {
      setVerificationError(
        err instanceof Error ? err.message : 'Failed to send verification code'
      );
    } finally {
      setIsVerifying(false);
    }
  };

  const handleVerificationSubmit = async () => {
    if (!verificationCode.trim()) {
      setVerificationError('Please enter the verification code');
      return;
    }

    setIsVerifying(true);
    setVerificationError(null);

    try {
      // Verify the phone number
      const verifyResponse = await fetch(
        '/api/v1/users/me/phone-numbers/verify-code',
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${localStorage.getItem('access_token')}`,
          },
          body: JSON.stringify({
            phone_number: phoneToVerify,
            verification_code: verificationCode,
          }),
        }
      );

      if (!verifyResponse.ok) {
        throw new Error('Invalid verification code');
      }

      // Registration is already complete, just redirect
      if (onSuccess) {
        onSuccess();
      }
    } catch (err) {
      setVerificationError(
        err instanceof Error ? err.message : 'Verification failed'
      );
    } finally {
      setIsVerifying(false);
    }
  };

  const handleBackToForm = () => {
    setVerificationStep('form');
    setVerificationError(null);
    setVerificationSent(false);
    setVerificationCode('');
  };

  const handleInputChange = (field: keyof RegisterFormData, value: string) => {
    setValue(field, value);
    if (error) clearError();
  };

  // Verification step UI
  if (verificationStep === 'verify') {
    return (
      <Card className="max-w-md mx-auto">
        <CardHeader>
          <div className="flex items-center space-x-3">
            <Button
              variant="ghost"
              size="sm"
              onClick={handleBackToForm}
              className="p-1"
            >
              <ArrowLeft className="w-4 h-4" />
            </Button>
            <CardTitle>Verify Phone Number</CardTitle>
          </div>
        </CardHeader>
        <CardContent className="!p-8">
          <div className="space-y-6">
            {/* Phone number display */}
            <div className="text-center">
              <div className="w-16 h-16 bg-teal-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Phone className="w-8 h-8 text-teal-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Verify Your Phone Number
              </h3>
              <p className="text-gray-600 text-sm">
                We sent a verification code to:
              </p>
              <p className="font-medium text-gray-900 mt-1">{phoneToVerify}</p>
            </div>

            {/* Verification code input */}
            <div>
              <Input
                label="Verification Code"
                type="text"
                placeholder="Enter 6-digit code"
                value={verificationCode}
                onChange={e => setVerificationCode(e.target.value)}
                maxLength={6}
                className="text-center text-lg tracking-widest"
              />
              {verificationSent && (
                <p className="text-sm text-green-600 mt-2 flex items-center justify-center">
                  <CheckCircle className="w-4 h-4 mr-1" />
                  Verification code sent!
                </p>
              )}
            </div>

            {/* Error display */}
            {verificationError && (
              <div className="text-red-600 text-sm bg-red-50 p-4 rounded-2xl border border-red-200">
                {verificationError}
              </div>
            )}

            {/* Submit button */}
            <Button
              variant="primary"
              size="lg"
              onClick={handleVerificationSubmit}
              loading={isVerifying}
              className="w-full"
              disabled={isVerifying || !verificationCode.trim()}
            >
              {isVerifying ? 'Verifying...' : 'Verify & Create Account'}
            </Button>

            {/* Resend code */}
            <div className="text-center">
              <p className="text-gray-600 text-sm">
                Didn't receive the code?{' '}
                <button
                  type="button"
                  onClick={() => sendVerificationCode(phoneToVerify)}
                  className="text-accent hover:text-accent-light font-medium underline"
                  disabled={isVerifying}
                >
                  Resend code
                </button>
              </p>
            </div>

            {/* Back to form */}
            <div className="text-center">
              <button
                type="button"
                onClick={handleBackToForm}
                className="text-gray-500 hover:text-gray-700 text-sm underline"
              >
                ← Back to registration form
              </button>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  // Registration form UI
  return (
    <Card className="max-w-md mx-auto">
      <CardHeader>
        <CardTitle>Create Account</CardTitle>
      </CardHeader>
      <CardContent className="!p-8">
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          {/* Full Name Field */}
          <Input
            label="Full Name"
            type="text"
            placeholder="Enter your full name"
            error={errors.fullName?.message}
            required
            {...register('fullName', {
              required: 'Full name is required',
              minLength: {
                value: 2,
                message: 'Full name must be at least 2 characters',
              },
              maxLength: {
                value: 100,
                message: 'Full name must be less than 100 characters',
              },
            })}
            onChange={e => handleInputChange('fullName', e.target.value)}
          />

          {/* Email Field */}
          <Input
            label="Email Address"
            type="email"
            placeholder="Enter your email"
            error={errors.email?.message}
            required
            {...register('email', {
              required: 'Email is required',
              pattern: {
                value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                message: 'Please enter a valid email address',
              },
            })}
            onChange={e => handleInputChange('email', e.target.value)}
          />

          {/* Password Field */}
          <Input
            label="Password"
            type="password"
            placeholder="Create a password"
            error={errors.password?.message}
            required
            {...register('password', {
              required: 'Password is required',
              minLength: {
                value: 8,
                message: 'Password must be at least 8 characters',
              },
              pattern: {
                value:
                  /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]/,
                message:
                  'Password must contain uppercase, lowercase, number, and special character',
              },
            })}
            onChange={e => handleInputChange('password', e.target.value)}
          />

          {/* Password Strength Indicator */}
          {password && (
            <div className="text-xs text-gray-600 bg-gray-50 p-4 rounded-2xl border border-gray-200">
              <div className="flex items-center space-x-2 mb-2">
                <span className="font-medium">Password strength:</span>
                <div className="flex space-x-1">
                  {[
                    password.length >= 8,
                    /[a-z]/.test(password),
                    /[A-Z]/.test(password),
                    /\d/.test(password),
                    /[@$!%*?&]/.test(password),
                  ].map((met, index) => (
                    <div
                      key={index}
                      className={`w-2 h-2 rounded-full ${
                        met ? 'bg-green-500' : 'bg-gray-300'
                      }`}
                    />
                  ))}
                </div>
              </div>
              <p className="text-gray-500">
                Must contain: 8+ chars, uppercase, lowercase, number, special
                char
              </p>
            </div>
          )}

          {/* Confirm Password Field */}
          <Input
            label="Confirm Password"
            type="password"
            placeholder="Confirm your password"
            error={errors.confirmPassword?.message}
            required
            {...register('confirmPassword', {
              required: 'Please confirm your password',
              validate: value => value === password || 'Passwords do not match',
            })}
            onChange={e => handleInputChange('confirmPassword', e.target.value)}
          />

          {/* Phone Number Field */}
          <div>
            <Input
              label="Phone Number (Optional)"
              type="tel"
              placeholder="Enter your phone number"
              error={errors.phoneNumber?.message}
              {...register('phoneNumber', {
                pattern: {
                  value: /^[\+]?[1-9][\d]{0,15}$/,
                  message: 'Please enter a valid phone number',
                },
              })}
              onChange={e => handleInputChange('phoneNumber', e.target.value)}
            />
            <p className="text-xs text-gray-500 mt-1">
              If provided, we'll send a verification code to confirm your number
            </p>
          </div>

          {/* Error Display */}
          {error && (
            <div className="text-red-600 text-sm bg-red-50 p-4 rounded-2xl border border-red-200">
              {error}
            </div>
          )}

          {/* Submit Button */}
          <Button
            type="submit"
            variant="primary"
            size="lg"
            loading={isLoading}
            className="w-full"
            disabled={isLoading}
          >
            {isLoading ? 'Creating Account...' : 'Create Account'}
          </Button>

          {/* Switch to Login */}
          <div className="text-center pt-4">
            <p className="text-gray-600 text-sm">
              Already have an account?{' '}
              <button
                type="button"
                onClick={onSwitchToLogin}
                className="text-accent hover:text-accent-light font-medium underline"
              >
                Sign in here
              </button>
            </p>
          </div>

          {/* Terms and Privacy */}
          <div className="text-center text-xs text-gray-500 pt-2">
            By creating an account, you agree to our{' '}
            <button type="button" className="text-accent hover:underline">
              Terms of Service
            </button>{' '}
            and{' '}
            <button type="button" className="text-accent hover:underline">
              Privacy Policy
            </button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
};

export default RegisterForm;
