import React, { useState, useEffect } from 'react';
import { Card } from '@/components/ui';
import SMSAnalyticsWidget from '@/components/dashboard/SMSAnalyticsWidget';
import { useAuthStore } from '../../stores/authStore';
import { isPremium, isAdmin } from '../../utils/roleUtils';
import { BarChart3, Download, TrendingUp, DollarSign } from 'lucide-react';

const SMSAnalyticsPage: React.FC = () => {
  const { user } = useAuthStore();
  const [error, setError] = useState<string | null>(null);

  // Check permissions
  useEffect(() => {
    if (!isPremium(user) && !isAdmin(user)) {
      setError('Insufficient permissions to view SMS analytics');
    }
  }, [user]);

  // Show access denied if user doesn't have permission
  if (!isPremium(user) && !isAdmin(user)) {
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
            You need Premium access to view SMS analytics.
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
          <h1 className="text-3xl font-bold text-gray-900">SMS Analytics</h1>
          <p className="text-gray-600 mt-2">
            Monitor your SMS usage, costs, and performance metrics
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2 text-sm text-gray-500">
            <BarChart3 className="w-4 h-4" />
            <span>Real-time data</span>
          </div>
        </div>
      </div>

      {/* Quick Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="bg-white">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
              <BarChart3 className="w-6 h-6 text-blue-600" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-600">
                Total Messages
              </p>
              <p className="text-2xl font-bold text-gray-900">Loading...</p>
            </div>
          </div>
        </Card>

        <Card className="bg-white">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
              <TrendingUp className="w-6 h-6 text-green-600" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-600">Success Rate</p>
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
              <p className="text-sm font-medium text-gray-600">Total Cost</p>
              <p className="text-2xl font-bold text-gray-900">Loading...</p>
            </div>
          </div>
        </Card>
      </div>

      {/* Main Analytics Widget */}
      <Card className="bg-white">
        <div className="mb-4">
          <h2 className="text-xl font-semibold text-gray-900 mb-2">
            Detailed Analytics
          </h2>
          <p className="text-gray-600">
            Comprehensive view of your SMS usage patterns, costs, and
            performance metrics
          </p>
        </div>
        <SMSAnalyticsWidget
          timeRange="30d"
          showCosts={true}
          showPerformance={true}
        />
      </Card>

      {/* Additional Features Section */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card className="bg-white">
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-10 h-10 bg-orange-100 rounded-lg flex items-center justify-center">
              <Download className="w-5 h-5 text-orange-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900">
              Export Reports
            </h3>
          </div>
          <p className="text-gray-600 mb-4">
            Download detailed reports in CSV or JSON format for further analysis
            and record keeping.
          </p>
          <div className="space-y-2 text-sm text-gray-500">
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
              <span>Usage summaries by time period</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <span>Cost breakdown and trends</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
              <span>Performance metrics and SLA compliance</span>
            </div>
          </div>
        </Card>

        <Card className="bg-white">
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-10 h-10 bg-indigo-100 rounded-lg flex items-center justify-center">
              <TrendingUp className="w-5 h-5 text-indigo-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900">
              Performance Insights
            </h3>
          </div>
          <p className="text-gray-600 mb-4">
            Monitor system performance, identify bottlenecks, and optimize your
            SMS routing efficiency.
          </p>
          <div className="space-y-2 text-sm text-gray-500">
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
              <span>Real-time performance monitoring</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <span>SLA compliance tracking</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
              <span>Performance optimization recommendations</span>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
};

export default SMSAnalyticsPage;
