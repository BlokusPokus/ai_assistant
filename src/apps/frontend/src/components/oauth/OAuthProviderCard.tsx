import React from 'react';
import { Button, Card } from '@/components/ui';
import { useOAuthStore } from '@/stores/oauthStore';
import type { OAuthProvider, OAuthStatus } from '@/types/oauth';
import { OAUTH_STATUS_COLORS, OAUTH_STATUS_LABELS } from '@/constants/oauth';

interface OAuthProviderCardProps {
  provider: OAuthProvider;
}

const OAuthProviderCard: React.FC<OAuthProviderCardProps> = ({ provider }) => {
  const {
    getProviderConfig,
    getIntegration,
    isConnected,
    connectIntegration,
    disconnectIntegration,
    isLoading,
  } = useOAuthStore();

  const providerConfig = getProviderConfig(provider);
  const integration = getIntegration(provider);
  const connected = isConnected(provider);

  if (!providerConfig) {
    return null;
  }

  const handleConnect = async () => {
    try {
      // Use default scopes for now
      const defaultScopes = ['read']; // This will be enhanced later
      await connectIntegration(provider, defaultScopes);
    } catch (error) {
      console.error('Failed to connect:', error);
    }
  };

  const handleDisconnect = async () => {
    try {
      await disconnectIntegration(provider);
    } catch (error) {
      console.error('Failed to disconnect:', error);
    }
  };

  const status: OAuthStatus = integration?.status || 'disconnected';
  const statusColor = OAUTH_STATUS_COLORS[status];
  const statusLabel = OAUTH_STATUS_LABELS[status];

  return (
    <Card className="p-6 hover:shadow-lg transition-shadow duration-200">
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div
            className="w-12 h-12 rounded-lg flex items-center justify-center text-white text-xl font-bold"
            style={{ backgroundColor: providerConfig.color }}
          >
            {providerConfig.name.charAt(0)}
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900">
              {providerConfig.name}
            </h3>
            <p className="text-sm text-gray-600">
              {providerConfig.description}
            </p>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <span
            className="px-2 py-1 text-xs font-medium rounded-full"
            style={{
              backgroundColor: `${statusColor}20`,
              color: statusColor,
            }}
          >
            {statusLabel}
          </span>
        </div>
      </div>

      <div className="mb-4">
        <h4 className="text-sm font-medium text-gray-700 mb-2">Features:</h4>
        <div className="flex flex-wrap gap-1">
          {providerConfig.features
            .slice(0, 3)
            .map((feature: string, index: number) => (
              <span
                key={index}
                className="px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded"
              >
                {feature}
              </span>
            ))}
        </div>
      </div>

      {integration && (
        <div className="mb-4 p-3 bg-gray-50 rounded-lg">
          <div className="text-sm text-gray-600">
            <div>
              Connected:{' '}
              {new Date(integration.connectedAt!).toLocaleDateString()}
            </div>
            <div>API Calls: {integration.usageStats.apiCalls}</div>
            {integration.usageStats.lastCall && (
              <div>
                Last Used:{' '}
                {new Date(integration.usageStats.lastCall).toLocaleDateString()}
              </div>
            )}
          </div>
        </div>
      )}

      <div className="flex space-x-2">
        {connected ? (
          <>
            <Button
              variant="outline"
              size="sm"
              onClick={handleDisconnect}
              disabled={isLoading}
              className="flex-1"
            >
              {isLoading ? 'Disconnecting...' : 'Disconnect'}
            </Button>
            <Button variant="outline" size="sm" className="flex-1">
              Manage
            </Button>
          </>
        ) : (
          <Button
            variant="primary"
            size="sm"
            onClick={handleConnect}
            disabled={isLoading}
            className="w-full"
          >
            {isLoading ? 'Connecting...' : 'Connect'}
          </Button>
        )}
      </div>
    </Card>
  );
};

export default OAuthProviderCard;
