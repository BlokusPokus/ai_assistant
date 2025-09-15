import React from 'react';
import { Card } from '@/components/ui';
import SMSAnalyticsPanel from '@/components/admin/SMSAnalyticsPanel';
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
