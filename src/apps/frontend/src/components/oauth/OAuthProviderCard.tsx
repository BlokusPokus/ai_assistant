import React, { useState } from 'react';
import { Button, Card } from '@/components/ui';
import { useOAuthSettingsStore } from '../../stores/oauthSettingsStore';
import type { OAuthProvider } from '@/types/oauth';
import { OAUTH_PROVIDERS } from '@/constants/oauth';

interface OAuthProviderCardProps {
  provider: OAuthProvider;
}

const OAuthProviderCard: React.FC<OAuthProviderCardProps> = ({ provider }) => {
  const { integrations, revokeIntegration, refreshIntegration } =
    useOAuthSettingsStore();

  const [isDisconnecting, setIsDisconnecting] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const providerConfig = OAUTH_PROVIDERS.find(p => p.id === provider);
  const integration = integrations.find(i => i.provider === provider);

  if (!providerConfig) {
    return null;
  }

  const isConnected = integration?.status === 'active' && integration?.is_active;

  const handleDisconnect = async () => {
    if (!integration) return;

    setIsDisconnecting(true);
    try {
      await revokeIntegration(integration.id, 'User requested disconnection');
    } catch (error) {
      console.error('Failed to disconnect:', error);
    } finally {
      setIsDisconnecting(false);
    }
  };

  const handleRefresh = async () => {
    if (!integration) return;

    setIsRefreshing(true);
    try {
      await refreshIntegration(integration.id);
    } catch (error) {
      console.error('Failed to refresh:', error);
    } finally {
      setIsRefreshing(false);
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

  return (
    <Card className="h-full flex flex-col">
      {/* Header with Status Badge */}
      <div className="relative">
        <div className="flex items-center space-x-3 mb-4">
          <div
            className={`w-12 h-12 rounded-2xl flex items-center justify-center text-white text-xl font-bold shadow-lg border border-white/20 ${getProviderLogoStyle(providerConfig.name)}`}
          >
            {providerConfig.name.charAt(0).toUpperCase()}
          </div>
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-gray-900">
              {providerConfig.name}
            </h3>
            <p className="text-sm text-gray-600">
              {providerConfig.description}
            </p>
          </div>
        </div>
        
        {/* Status Badge */}
        <div className="absolute top-0 right-0">
          <span
            className={`px-3 py-1 text-xs font-medium rounded-full ${
              isConnected
                ? 'bg-green-100 text-green-800 border border-green-200'
                : 'bg-gray-100 text-gray-800 border border-gray-200'
            }`}
          >
            {isConnected ? 'Connected' : 'Not Connected'}
          </span>
        </div>
      </div>

      {/* Features */}
      <div className="mb-4">
        <h4 className="text-sm font-medium text-gray-700 mb-2">Features:</h4>
        <div className="flex flex-wrap gap-2">
          {providerConfig.features?.map((feature, index) => (
            <span
              key={index}
              className="px-3 py-1 bg-gray-100 text-gray-700 text-xs rounded-lg border border-gray-200"
            >
              {feature}
            </span>
          ))}
        </div>
      </div>

      {/* Connection Details - Only show if connected */}
      {isConnected && integration && (
        <div className="mb-4 space-y-2">
          <div className="text-sm text-gray-600">
            <span className="font-medium">Connected:</span> {new Date(integration.created_at).toLocaleDateString()}
          </div>
          <div className="text-sm text-gray-600">
            <span className="font-medium">Scopes:</span> {integration.scopes?.join(', ') || 'read'}
          </div>
          <div className="text-sm text-gray-600">
            <span className="font-medium">Last Sync:</span> {integration.last_sync_at ? new Date(integration.last_sync_at).toLocaleDateString() : 'Never'}
          </div>
        </div>
      )}

      {/* Action Buttons - Always at bottom */}
      <div className="mt-auto pt-4">
        {isConnected ? (
          <div className="flex gap-2">
            <Button
              variant="secondary"
              size="sm"
              onClick={handleRefresh}
              disabled={isRefreshing}
              className="flex-1"
            >
              {isRefreshing ? 'Refreshing...' : 'Refresh'}
            </Button>
            <Button
              variant="secondary"
              size="sm"
              onClick={handleDisconnect}
              disabled={isDisconnecting}
              className="flex-1"
            >
              {isDisconnecting ? 'Disconnecting...' : 'Disconnect'}
            </Button>
          </div>
        ) : (
          <Button
            variant="primary"
            size="sm"
            onClick={() => {}} // TODO: Implement connect flow
            className="w-full"
          >
            Connect
          </Button>
        )}
      </div>
    </Card>
  );
};

export default OAuthProviderCard;
