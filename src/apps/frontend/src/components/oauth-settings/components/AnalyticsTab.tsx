import React, { useState, useEffect } from 'react';
import { useOAuthSettingsStore } from '../../../stores/oauthSettingsStore';
import { useAuthStore } from '../../../stores/authStore';
import { isPremium, isAdmin } from '../../../utils/roleUtils';
import { Select } from '@/components/ui';

const timeRanges = [
  { value: '1d', label: 'Last 24 Hours' },
  { value: '7d', label: 'Last 7 Days' },
  { value: '30d', label: 'Last 30 Days' },
  { value: '90d', label: 'Last 90 Days' },
];

export const AnalyticsTab: React.FC = () => {
  const { user } = useAuthStore();
  const { analytics, loading, loadAnalytics } = useOAuthSettingsStore();
  const [timeRange, setTimeRange] = useState('7d');
  const [error, setError] = useState<string | null>(null);

  // Check permissions before loading data
  useEffect(() => {
    if (!isPremium(user) && !isAdmin(user)) {
      setError('Insufficient permissions to view analytics');
      return;
    }

    loadAnalytics().catch(err => {
      if (err.status === 403) {
        setError('You do not have permission to access analytics data');
      } else {
        setError('Failed to load analytics data');
      }
    });
  }, [loadAnalytics, user]);

  const handleTimeRangeChange = (newTimeRange: string) => {
    setTimeRange(newTimeRange);
  };

  // Show access denied if user doesn't have permission
  if (!isPremium(user) && !isAdmin(user)) {
    return (
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
          You need Premium access to view analytics.
        </p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-accent"></div>
      </div>
    );
  }

  if (error) {
    return (
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
    );
  }

  if (!analytics) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">No analytics data available</p>
      </div>
    );
  }

  return (
    <div className="px-4 sm:px-0">
      <div className="mb-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">
          Analytics Overview
        </h3>

        <div className="flex items-center space-x-4 mb-6">
          <label className="text-sm font-medium text-gray-700">
            Time Range:
          </label>
          <Select
            value={timeRange}
            onChange={handleTimeRangeChange}
            options={timeRanges}
            placeholder="Select time range"
            className="w-48"
          />
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-blue-500 rounded-md flex items-center justify-center">
                  <span className="text-white text-sm font-bold">🔗</span>
                </div>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Total Integrations
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {analytics.integrations.total}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-green-500 rounded-md flex items-center justify-center">
                  <span className="text-white text-sm font-bold">✅</span>
                </div>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Active Integrations
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {analytics.integrations.active}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-yellow-500 rounded-md flex items-center justify-center">
                  <span className="text-white text-sm font-bold">⚠️</span>
                </div>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Expired Integrations
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {analytics.integrations.expired}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-red-500 rounded-md flex items-center justify-center">
                  <span className="text-white text-sm font-bold">❌</span>
                </div>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Revoked Integrations
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {analytics.integrations.revoked}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Provider Distribution */}
      <div className="bg-white shadow rounded-lg mb-8">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
            Provider Distribution
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {Object.entries(analytics.providers).map(([provider, stats]) => (
              <div key={provider} className="text-center">
                <div className="text-2xl font-bold text-gray-900">
                  {stats.count}
                </div>
                <div className="text-sm text-gray-500 capitalize">
                  {provider}
                </div>
                <div className="text-xs text-gray-400">
                  {stats.active} active, {stats.expired} expired
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Usage Metrics */}
      {analytics.usage && (
        <div className="bg-white shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
              Usage Metrics
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900">
                  {analytics.usage.total_requests}
                </div>
                <div className="text-sm text-gray-500">Total Requests</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">
                  {analytics.usage.successful_requests}
                </div>
                <div className="text-sm text-gray-500">Successful</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-red-600">
                  {analytics.usage.failed_requests}
                </div>
                <div className="text-sm text-gray-500">Failed</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">
                  {analytics.usage.average_response_time}ms
                </div>
                <div className="text-sm text-gray-500">Avg Response</div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
