import React from 'react';
import { Card } from '@/components/ui';
import { useOAuthStore } from '@/stores/oauthStore';
import type { OAuthProvider } from '@/types/oauth';
import { OAUTH_HEALTH_COLORS, OAUTH_HEALTH_LABELS } from '@/constants/oauth';

interface OAuthStatusProps {
  provider: OAuthProvider;
}

const OAuthStatus: React.FC<OAuthStatusProps> = ({ provider }) => {
  const { getIntegration, getProviderConfig } = useOAuthStore();

  const integration = getIntegration(provider);
  const providerConfig = getProviderConfig(provider);

  if (!providerConfig) {
    return null;
  }

  if (!integration) {
    return (
      <Card className="p-4">
        <div className="text-center text-gray-500">
          <p className="text-sm">Not connected to {providerConfig.name}</p>
        </div>
      </Card>
    );
  }

  const health = integration.usageStats.errors > 0 ? 'warning' : 'healthy';
  const healthColor = OAUTH_HEALTH_COLORS[health];
  const healthLabel = OAUTH_HEALTH_LABELS[health];

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

  return (
    <Card className="p-4">
      <div className="flex items-center space-x-3 mb-3">
        <div className={`w-10 h-10 rounded-2xl flex items-center justify-center shadow-sm border border-gray-200 ${getProviderLogoStyle(providerConfig.name)}`}>
          <span className="text-lg font-bold text-white">
            {providerConfig.name.charAt(0).toUpperCase()}
          </span>
        </div>
        <div>
          <h4 className="text-sm font-medium text-gray-700">
            Connection Status
          </h4>
          <span
            className="px-2 py-1 text-xs font-medium rounded-full"
            style={{
              backgroundColor: `${healthColor}20`,
              color: healthColor,
            }}
          >
            {healthLabel}
          </span>
        </div>
      </div>

      <div className="space-y-2 text-sm">
        <div className="flex justify-between">
          <span className="text-gray-600">Status:</span>
          <span className="font-medium capitalize">{integration.status}</span>
        </div>

        {integration.connectedAt && (
          <div className="flex justify-between">
            <span className="text-gray-600">Connected:</span>
            <span className="font-medium">
              {new Date(integration.connectedAt).toLocaleDateString()}
            </span>
          </div>
        )}

        {integration.lastUsed && (
          <div className="flex justify-between">
            <span className="text-gray-600">Last Used:</span>
            <span className="font-medium">
              {new Date(integration.lastUsed).toLocaleDateString()}
            </span>
          </div>
        )}

        <div className="flex justify-between">
          <span className="text-gray-600">API Calls:</span>
          <span className="font-medium">{integration.usageStats.apiCalls}</span>
        </div>

        {integration.usageStats.errors > 0 && (
          <div className="flex justify-between">
            <span className="text-gray-600">Errors:</span>
            <span className="font-medium text-red-600">
              {integration.usageStats.errors}
            </span>
          </div>
        )}
      </div>
    </Card>
  );
};

export default OAuthStatus;
