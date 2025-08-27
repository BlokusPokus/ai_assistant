import React, { useState } from 'react';
import { useOAuthSettingsStore } from '../../../stores/oauthSettingsStore';
import type { OAuthIntegrationEnhanced } from '../../../services/oauthSettingsService';

export const IntegrationsTab: React.FC = () => {
  const { integrations, loading, refreshIntegration, revokeIntegration } =
    useOAuthSettingsStore();

  const [selectedIntegrations, setSelectedIntegrations] = useState<number[]>(
    []
  );
  const [showRevokeDialog, setShowRevokeDialog] = useState<number | null>(null);
  const [revokeReason, setRevokeReason] = useState('');

  const handleSelectIntegration = (integrationId: number) => {
    setSelectedIntegrations(prev =>
      prev.includes(integrationId)
        ? prev.filter(id => id !== integrationId)
        : [...prev, integrationId]
    );
  };

  const handleSelectAll = () => {
    if (selectedIntegrations.length === integrations.length) {
      setSelectedIntegrations([]);
    } else {
      setSelectedIntegrations(integrations.map(i => i.id));
    }
  };

  const handleBulkRefresh = async () => {
    for (const integrationId of selectedIntegrations) {
      await refreshIntegration(integrationId);
    }
    setSelectedIntegrations([]);
  };

  const handleBulkRevoke = async () => {
    for (const integrationId of selectedIntegrations) {
      await revokeIntegration(integrationId, 'Bulk revocation');
    }
    setSelectedIntegrations([]);
  };

  const handleRevoke = async (integrationId: number) => {
    await revokeIntegration(integrationId, revokeReason);
    setShowRevokeDialog(null);
    setRevokeReason('');
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800';
      case 'expired':
        return 'bg-yellow-100 text-yellow-800';
      case 'revoked':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getProviderLogoStyle = (providerName: string) => {
    switch (providerName.toLowerCase()) {
      case 'google':
        return 'bg-gradient-to-br from-blue-500 to-blue-600';
      case 'microsoft':
        return 'bg-gradient-to-br from-blue-600 to-blue-700';
      case 'notion':
        return 'bg-gradient-to-br from-gray-800 to-gray-900';
      case 'slack':
        return 'bg-gradient-to-br from-purple-500 to-purple-600';
      case 'github':
        return 'bg-gradient-to-br from-gray-700 to-gray-800';
      case 'discord':
        return 'bg-gradient-to-br from-indigo-500 to-indigo-600';
      default:
        return 'bg-gradient-to-br from-gray-500 to-gray-600';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="px-4 sm:px-0">
      {/* Bulk Actions */}
      {selectedIntegrations.length > 0 && (
        <div className="mb-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <span className="text-sm text-blue-800">
              {selectedIntegrations.length} integration(s) selected
            </span>
            <div className="flex space-x-3">
              <button
                onClick={handleBulkRefresh}
                className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-blue-700 bg-blue-100 hover:bg-blue-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                🔄 Refresh All
              </button>
              <button
                onClick={handleBulkRevoke}
                className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-red-700 bg-red-100 hover:bg-red-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
              >
                🗑️ Revoke All
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Integrations Table */}
      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        <div className="px-4 py-5 sm:p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg leading-6 font-medium text-gray-900">
              OAuth Integrations
            </h3>
            <div className="text-sm text-gray-500">
              {integrations.length} integration(s)
            </div>
          </div>

          {/* Refresh Token Info */}
          <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
            <div className="flex items-start">
              <div className="flex-shrink-0">
                <svg
                  className="h-5 w-5 text-blue-400"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                >
                  <path
                    fillRule="evenodd"
                    d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
                    clipRule="evenodd"
                  />
                </svg>
              </div>
              <div className="ml-3">
                <h4 className="text-sm font-medium text-blue-800">
                  Refresh Token Information
                </h4>
                <div className="mt-1 text-sm text-blue-700">
                  <p>
                    Some integrations may not support token refresh if they were
                    connected before refresh token support was implemented.
                    These integrations will show a "Cannot Refresh" status.
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Select All Checkbox */}
          <div className="flex items-center space-x-3 mb-4">
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={
                  selectedIntegrations.length === integrations.length &&
                  integrations.length > 0
                }
                onChange={handleSelectAll}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <span className="ml-2 text-sm text-gray-700">Select All</span>
            </label>
          </div>
        </div>

        <ul className="divide-y divide-gray-200">
          {integrations.map(integration => (
            <li key={integration.id} className="px-4 py-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    checked={selectedIntegrations.includes(integration.id)}
                    onChange={() => handleSelectIntegration(integration.id)}
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500 mr-3"
                  />

                  <div className="flex-shrink-0">
                    <div className={`h-12 w-12 rounded-2xl flex items-center justify-center shadow-sm border border-gray-200 ${getProviderLogoStyle(integration.provider)}`}>
                      <span className="text-xl font-bold text-white">
                        {integration.provider.charAt(0).toUpperCase()}
                      </span>
                    </div>
                  </div>

                  <div className="ml-4">
                    <div className="flex items-center">
                      <p className="text-sm font-medium text-gray-900">
                        {integration.display_name || integration.provider}
                      </p>
                      <span
                        className={`ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(
                          integration.status
                        )}`}
                      >
                        {integration.status}
                      </span>
                    </div>
                    <div className="mt-1 flex items-center text-sm text-gray-500">
                      <span>Provider: {integration.provider}</span>
                      <span className="mx-2">•</span>
                      <span>Scopes: {integration.scopes.join(', ')}</span>
                      <span className="mx-2">•</span>
                      <span>
                        Created:{' '}
                        {new Date(integration.created_at).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => refreshIntegration(integration.id)}
                    disabled={loading}
                    className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-blue-700 bg-blue-100 hover:bg-blue-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {loading ? '🔄 Refreshing...' : '🔄 Refresh'}
                  </button>
                  <button
                    onClick={() => setShowRevokeDialog(integration.id)}
                    className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-red-700 bg-red-100 hover:bg-red-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                  >
                    🗑️ Revoke
                  </button>
                </div>
              </div>
            </li>
          ))}
        </ul>
      </div>

      {/* Revoke Confirmation Dialog */}
      {showRevokeDialog && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                Revoke OAuth Integration
              </h3>
              <p className="text-sm text-gray-500 mb-4">
                Are you sure you want to revoke this OAuth integration? This
                action cannot be undone.
              </p>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Reason (optional)
                </label>
                <textarea
                  value={revokeReason}
                  onChange={e => setRevokeReason(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  rows={3}
                  placeholder="Enter reason for revocation..."
                />
              </div>
              <div className="flex justify-end space-x-3">
                <button
                  onClick={() => setShowRevokeDialog(null)}
                  className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  onClick={() => handleRevoke(showRevokeDialog)}
                  className="px-4 py-2 border border-transparent rounded-md text-sm font-medium text-white bg-red-600 hover:bg-red-700"
                >
                  Revoke
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
