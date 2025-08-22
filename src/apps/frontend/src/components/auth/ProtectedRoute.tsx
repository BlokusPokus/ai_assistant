import React, { useEffect } from 'react';
import { useAuthStore } from '@/stores/authStore';
import { Loading } from '@/components/ui';

interface ProtectedRouteProps {
  children: React.ReactNode;
  fallback?: React.ReactNode;
  requireAuth?: boolean;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  fallback,
  requireAuth = true,
}) => {
  const { isAuthenticated, isLoading, checkAuth } = useAuthStore();

  useEffect(() => {
    // Check authentication status on mount
    checkAuth();
  }, [checkAuth]);

  // Show loading while checking authentication
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loading size="lg" text="Checking authentication..." />
      </div>
    );
  }

  // If authentication is required and user is not authenticated
  if (requireAuth && !isAuthenticated) {
    if (fallback) {
      return <>{fallback}</>;
    }

    // Default redirect to login
    window.location.href = '/login';
    return null;
  }

  // If authentication is not required and user is authenticated, redirect to dashboard
  if (!requireAuth && isAuthenticated) {
    window.location.href = '/dashboard';
    return null;
  }

  // User is authenticated and can access the route
  return <>{children}</>;
};

export default ProtectedRoute;
