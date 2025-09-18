import React, { useState, useEffect } from 'react';
import { Card } from '@/components/ui';
import SMSAnalyticsPanel from '@/components/admin/SMSAnalyticsPanel';
import { useAuthStore } from '../../stores/authStore';
import { isAdmin } from '../../utils/roleUtils';
import {
  BarChart3,
  Users,
  TrendingUp,
  AlertTriangle,
  Shield,
  Activity,
  DollarSign,
  Clock,
} from 'lucide-react';

const AdminAnalyticsPage: React.FC = () => {
  const { user } = useAuthStore();
  const [error, setError] = useState<string | null>(null);

  // Check permissions
  useEffect(() => {
    if (!isAdmin(user)) {
      setError('Insufficient permissions to view admin analytics');
    }
  }, [user]);

  // Show access denied if user doesn't have permission
  if (!isAdmin(user)) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="text-center py-12">
          <div className="mx-auto h-12 w-12 text-gray-400">
            <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
              />
            </svg>
          </div>
          <h3 className="mt-2 text-sm font-medium text-gray-900">
            Access Denied
          </h3>
          <p className="mt-1 text-sm text-gray-500">
            You need Administrator access to view admin analytics.
          </p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="text-center py-12">
          <div className="mx-auto h-12 w-12 text-red-400">
            <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          </div>
          <h3 className="mt-2 text-sm font-medium text-gray-900">Error</h3>
          <p className="mt-1 text-sm text-gray-500">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Admin Analytics</h1>
          <p className="text-gray-600 mt-2">
            System-wide SMS analytics, performance monitoring, and cost
            management
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2 text-sm text-gray-500">
            <Shield className="w-4 h-4" />
            <span>Admin Access Required</span>
          </div>
        </div>
      </div>

      {/* Admin Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="bg-white">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
              <Users className="w-6 h-6 text-blue-600" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-600">Active Users</p>
              <p className="text-2xl font-bold text-gray-900">Loading...</p>
            </div>
          </div>
        </Card>

        <Card className="bg-white">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
              <Activity className="w-6 h-6 text-green-600" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-600">System Health</p>
              <p className="text-2xl font-bold text-gray-900">Loading...</p>
            </div>
          </div>
        </Card>

        <Card className="bg-white">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
              <DollarSign className="w-6 h-6 text-purple-600" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-600">Total Costs</p>
              <p className="text-2xl font-bold text-gray-900">Loading...</p>
            </div>
          </div>
        </Card>

        <Card className="bg-white">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center">
              <Clock className="w-6 h-6 text-orange-600" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-600">Avg Response</p>
              <p className="text-2xl font-bold text-gray-900">Loading...</p>
            </div>
          </div>
        </Card>
      </div>

      {/* Main Admin Analytics Panel */}
      <Card className="bg-white">
        <div className="mb-4">
          <h2 className="text-xl font-semibold text-gray-900 mb-2">
            System Analytics Dashboard
          </h2>
          <p className="text-gray-600">
            Comprehensive system-wide SMS analytics, performance metrics, and
            cost optimization insights
          </p>
        </div>
        <SMSAnalyticsPanel timeRange="30d" />
      </Card>

      {/* Admin Features Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card className="bg-white">
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-10 h-10 bg-indigo-100 rounded-lg flex items-center justify-center">
              <TrendingUp className="w-5 h-5 text-indigo-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900">
              Performance Monitoring
            </h3>
          </div>
          <p className="text-gray-600 mb-4">
            Real-time system performance monitoring with SLA compliance tracking
            and automated alerting.
          </p>
          <div className="space-y-2 text-sm text-gray-500">
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
              <span>Real-time performance metrics</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <span>SLA compliance monitoring</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
              <span>Automated performance alerts</span>
            </div>
          </div>
        </Card>

        <Card className="bg-white">
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center">
              <AlertTriangle className="w-5 h-5 text-red-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900">
              Alert Management
            </h3>
          </div>
          <p className="text-gray-600 mb-4">
            Proactive alerting system for performance issues, cost thresholds,
            and system health monitoring.
          </p>
          <div className="space-y-2 text-sm text-gray-500">
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
              <span>Performance threshold alerts</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <span>Cost optimization notifications</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
              <span>System health monitoring</span>
            </div>
          </div>
        </Card>
      </div>

      {/* Additional Admin Tools */}
      <Card className="bg-white">
        <div className="mb-4">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            Administrative Tools
          </h3>
          <p className="text-gray-600">
            Advanced tools for system administration and optimization
          </p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 border border-gray-200 rounded-lg">
            <div className="flex items-center space-x-2 mb-2">
              <BarChart3 className="w-5 h-5 text-blue-600" />
              <span className="font-medium text-gray-900">Usage Reports</span>
            </div>
            <p className="text-sm text-gray-600">
              Generate comprehensive usage reports for billing and analysis
            </p>
          </div>

          <div className="p-4 border border-gray-200 rounded-lg">
            <div className="flex items-center space-x-2 mb-2">
              <Users className="w-5 h-5 text-green-600" />
              <span className="font-medium text-gray-900">User Management</span>
            </div>
            <p className="text-sm text-gray-600">
              Monitor individual user usage patterns and costs
            </p>
          </div>

          <div className="p-4 border border-gray-200 rounded-lg">
            <div className="flex items-center space-x-2 mb-2">
              <Shield className="w-5 h-5 text-purple-600" />
              <span className="font-medium text-gray-900">
                Security Monitoring
              </span>
            </div>
            <p className="text-sm text-gray-600">
              Track security events and access patterns
            </p>
          </div>
        </div>
      </Card>
    </div>
  );
};

export default AdminAnalyticsPage;
