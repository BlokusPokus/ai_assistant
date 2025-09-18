import React, { useState } from 'react';
import { useOAuthSettingsStore } from '../../../stores/oauthSettingsStore';
import { useAuthStore } from '../../../stores/authStore';
import { isAdmin } from '../../../utils/roleUtils';
import type { AuditFilters } from '../../../services/oauthSettingsService';
import { Select } from '@/components/ui';

export const AuditTab: React.FC = () => {
  const { user } = useAuthStore();
  const { auditLogs, loading, loadAuditLogs, exportData } =
    useOAuthSettingsStore();
  const [filters, setFilters] = useState<AuditFilters>({});
  const [exportFormat, setExportFormat] = useState<'csv' | 'json'>('csv');
  const [error, setError] = useState<string | null>(null);

  // Check permissions before loading data
  React.useEffect(() => {
    if (!isAdmin(user)) {
      setError('Insufficient permissions to view audit logs');
      return;
    }

    loadAuditLogs().catch((err: any) => {
      if (err?.status === 403) {
        setError('You do not have permission to access audit logs');
      } else {
        setError('Failed to load audit logs');
      }
    });
  }, [loadAuditLogs, user]);

  const handleExport = async () => {
    if (!isAdmin(user)) {
      setError('Insufficient permissions to export audit logs');
      return;
    }

    try {
      const data = await exportData(exportFormat, filters);

      // Create and download file
      const blob = new Blob([data], {
        type: exportFormat === 'csv' ? 'text/csv' : 'application/json',
      });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `oauth-audit-${
        new Date().toISOString().split('T')[0]
      }.${exportFormat}`;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (error: any) {
      if (error?.status === 403) {
        setError('You do not have permission to export audit logs');
      } else {
        console.error('Export failed:', error);
        setError('Export failed');
      }
    }
  };

  const handleFilterChange = (key: keyof AuditFilters, value: string) => {
    setFilters(prev => ({
      ...prev,
      [key]: value || undefined,
    }));
  };

  const applyFilters = () => {
    loadAuditLogs(filters);
  };

  const clearFilters = () => {
    setFilters({});
    loadAuditLogs({});
  };

  // Show access denied if user doesn't have permission
  if (!isAdmin(user)) {
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
          You need Administrator access to view audit logs.
        </p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
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

  return (
    <div className="px-4 sm:px-0">
      {/* Filters */}
      <div className="bg-white shadow rounded-lg mb-6">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
            Filter Audit Logs
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Date From
              </label>
              <input
                type="date"
                value={filters.dateFrom || ''}
                onChange={e => handleFilterChange('dateFrom', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Date To
              </label>
              <input
                type="date"
                value={filters.dateTo || ''}
                onChange={e => handleFilterChange('dateTo', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Provider
              </label>
              <Select
                value={filters.provider || ''}
                onChange={value => handleFilterChange('provider', value)}
                options={[
                  { value: '', label: 'All Providers' },
                  { value: 'google', label: 'Google' },
                  { value: 'microsoft', label: 'Microsoft' },
                  { value: 'notion', label: 'Notion' },
                  { value: 'youtube', label: 'YouTube' },
                ]}
                placeholder="Select provider"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Action
              </label>
              <Select
                value={filters.action || ''}
                onChange={value => handleFilterChange('action', value)}
                options={[
                  { value: '', label: 'All Actions' },
                  {
                    value: 'integration_created',
                    label: 'Integration Created',
                  },
                  { value: 'tokens_refreshed', label: 'Tokens Refreshed' },
                  {
                    value: 'integration_revoked',
                    label: 'Integration Revoked',
                  },
                  { value: 'scopes_updated', label: 'Scopes Updated' },
                ]}
                placeholder="Select action"
              />
            </div>
          </div>
          <div className="flex justify-end space-x-3 mt-4">
            <button
              onClick={clearFilters}
              className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
            >
              Clear Filters
            </button>
            <button
              onClick={applyFilters}
              className="px-4 py-2 border border-transparent rounded-md text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
            >
              Apply Filters
            </button>
          </div>
        </div>
      </div>

      {/* Export Controls */}
      <div className="bg-white shadow rounded-lg mb-6">
        <div className="px-4 py-5 sm:p-6">
          <div className="flex items-center justify-between">
            <h3 className="text-lg leading-6 font-medium text-gray-900">
              Export Data
            </h3>
            <div className="flex items-center space-x-3">
              <Select
                value={exportFormat}
                onChange={value => setExportFormat(value as 'csv' | 'json')}
                options={[
                  { value: 'csv', label: 'CSV' },
                  { value: 'json', label: 'JSON' },
                ]}
                placeholder="Select format"
                className="w-32"
              />
              <button
                onClick={handleExport}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
              >
                📥 Export
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Audit Logs Table */}
      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        <div className="px-4 py-5 sm:px-6 border-b border-gray-200">
          <h3 className="text-lg leading-6 font-medium text-gray-900">
            Audit Logs
          </h3>
          <p className="mt-1 text-sm text-gray-500">
            {auditLogs.length} log entries found
          </p>
        </div>

        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Timestamp
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Action
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Provider
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Details
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  IP Address
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {auditLogs.map(log => (
                <tr key={log.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {new Date(log.timestamp).toLocaleString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                      {log.action.replace(/_/g, ' ')}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 capitalize">
                    {log.provider}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900">
                    <div className="max-w-xs truncate">
                      {JSON.stringify(log.details)}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {log.ip_address || 'N/A'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {auditLogs.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-500">No audit logs found</p>
          </div>
        )}
      </div>
    </div>
  );
};
