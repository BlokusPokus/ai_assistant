import React from 'react';
import { Button, Card } from '@/components/ui';
import { useOAuthSettingsStore } from '../../stores/oauthSettingsStore';
import type { OAuthProvider } from '@/types/oauth';
import { OAUTH_PROVIDERS } from '@/constants/oauth';

interface OAuthProviderCardProps {
  provider: OAuthProvider;
}

const OAuthProviderCard: React.FC<OAuthProviderCardProps> = ({ provider }) => {
  const { integrations, refreshIntegration, revokeIntegration, loading } =
    useOAuthSettingsStore();

  // Find the provider config from constants
  const providerConfig = OAUTH_PROVIDERS.find(p => p.id === provider);

  // Find the integration from real data
  const integration = integrations.find(i => i.provider === provider);

  // Check if connected based on real data
  const connected = integration && integration.is_active;

  if (!providerConfig) {
    return null;
  }

  const handleConnect = async () => {
    try {
      console.log(`Connecting to ${provider} with default scopes`);

      // Call the backend to initiate OAuth flow
      const response = await fetch('/api/v1/oauth/initiate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify({
          provider: provider,
          scopes: ['read'], // Default scopes for Notion
          redirect_uri: `${window.location.origin}/oauth/callback`,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      if (data.authorization_url) {
        // Redirect to the OAuth provider's authorization page
        window.location.href = data.authorization_url;
      } else {
        throw new Error('No authorization URL received from backend');
      }
    } catch (error) {
      console.error('Failed to connect:', error);
      alert('Failed to connect to the service. Please try again.');
    }
  };

  const handleDisconnect = async () => {
    try {
      if (integration) {
        await revokeIntegration(integration.id, 'User requested disconnection');
      }
    } catch (error) {
      console.error('Failed to disconnect:', error);
    }
  };

  const handleRefresh = async () => {
    try {
      if (integration) {
        await refreshIntegration(integration.id);
      }
    } catch (error) {
      console.error('Failed to refresh:', error);
    }
  };

  // Map backend status to UI status
  const getStatusInfo = () => {
    if (!integration) return { color: '#6B7280', label: 'Not Connected' };

    switch (integration.status) {
      case 'active':
        return { color: '#10B981', label: 'Connected' };
      case 'expired':
        return { color: '#F59E0B', label: 'Expired' };
      case 'revoked':
        return { color: '#EF4444', label: 'Revoked' };
      default:
        return { color: '#6B7280', label: integration.status };
    }
  };

  const statusInfo = getStatusInfo();

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
              backgroundColor: `${statusInfo.color}20`,
              color: statusInfo.color,
            }}
          >
            {statusInfo.label}
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
              Connected: {new Date(integration.created_at).toLocaleDateString()}
            </div>
            <div>Scopes: {integration.scopes.join(', ')}</div>
            {integration.last_sync_at && (
              <div>
                Last Sync:{' '}
                {new Date(integration.last_sync_at).toLocaleDateString()}
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
              onClick={handleRefresh}
              disabled={loading}
              className="flex-1"
            >
              {loading ? 'Refreshing...' : 'Refresh'}
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={handleDisconnect}
              disabled={loading}
              className="flex-1"
            >
              {loading ? 'Disconnecting...' : 'Disconnect'}
            </Button>
          </>
        ) : (
          <Button
            variant="primary"
            size="sm"
            onClick={handleConnect}
            disabled={loading}
            className="w-full"
          >
            {loading ? 'Connecting...' : 'Connect'}
          </Button>
        )}
      </div>
    </Card>
  );
};

export default OAuthProviderCard;
