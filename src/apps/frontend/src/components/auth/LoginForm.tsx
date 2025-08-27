import React from 'react';
import { useForm } from 'react-hook-form';
import { Button, Input, Card, CardHeader, CardTitle, CardContent } from '@/components/ui';
import { useAuthStore } from '@/stores/authStore';
import type { LoginFormData } from '@/types/auth';

interface LoginFormProps {
  onSuccess?: () => void;
  onSwitchToRegister?: () => void;
}

const LoginForm: React.FC<LoginFormProps> = ({
  onSuccess,
  onSwitchToRegister,
}) => {
  const { login, isLoading, error, clearError } = useAuthStore();

  const {
    register,
    handleSubmit,
    formState: { errors },
    setValue,
  } = useForm<LoginFormData>({
    defaultValues: {
      email: '',
      password: '',
    },
  });

  const onSubmit = async (data: LoginFormData) => {
    clearError();
    const success = await login(data);
    if (success && onSuccess) {
      onSuccess();
    }
  };

  const handleInputChange = (field: keyof LoginFormData, value: string) => {
    setValue(field, value);
    if (error) clearError();
  };

  return (
    <Card className="max-w-md mx-auto">
      <CardHeader>
        <CardTitle>Sign In</CardTitle>
      </CardHeader>
      <CardContent className="!p-8">
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
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
            placeholder="Enter your password"
            error={errors.password?.message}
            required
            {...register('password', {
              required: 'Password is required',
              minLength: {
                value: 8,
                message: 'Password must be at least 8 characters',
              },
            })}
            onChange={(e) => handleInputChange('password', e.target.value)}
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
            {isLoading ? 'Signing In...' : 'Sign In'}
          </Button>

          {/* Switch to Register */}
          <div className="text-center pt-4">
            <p className="text-gray-600 text-sm">
              Don't have an account?{' '}
              <button
                type="button"
                onClick={onSwitchToRegister}
                className="text-accent hover:text-accent-light font-medium underline"
              >
                Sign up here
              </button>
            </p>
          </div>

          {/* Forgot Password Link */}
          <div className="text-center">
            <button
              type="button"
              className="text-gray-500 hover:text-gray-700 text-sm underline"
            >
              Forgot your password?
            </button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
};

export default LoginForm;
