import React from 'react';
import { useForm } from 'react-hook-form';
import { Button, Input, Card, CardHeader, CardTitle, CardContent } from '@/components/ui';
import { useAuthStore } from '@/stores/authStore';
import type { RegisterFormData } from '@/types/auth';

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
    },
  });

  const password = watch('password');

  const onSubmit = async (data: RegisterFormData) => {
    clearError();
    const success = await registerUser({
      email: data.email,
      password: data.password,
      full_name: data.fullName,
    });
    if (success && onSuccess) {
      onSuccess();
    }
  };

  const handleInputChange = (field: keyof RegisterFormData, value: string) => {
    setValue(field, value);
    if (error) clearError();
  };

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
            onChange={(e) => handleInputChange('fullName', e.target.value)}
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
            onChange={(e) => handleInputChange('email', e.target.value)}
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
            onChange={(e) => handleInputChange('password', e.target.value)}
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
                Must contain: 8+ chars, uppercase, lowercase, number, special char
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
            onChange={(e) => handleInputChange('confirmPassword', e.target.value)}
          />

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
