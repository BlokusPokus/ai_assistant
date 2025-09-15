import React, { useState, useEffect } from 'react';
import { Button, Card, Input, Loading } from '@/components/ui';
import { useOAuthSettingsStore } from '../../stores/oauthSettingsStore';
import OAuthProviderCard from './OAuthProviderCard';
import OAuthConsent from './OAuthConsent';
import type { OAuthProvider } from '@/types/oauth';
import { OAUTH_PROVIDERS } from '@/constants/oauth';

const OAuthManager: React.FC = () => {
  const { integrations, loading, error, loadIntegrations } =
    useOAuthSettingsStore();

  const [searchTerm, setSearchTerm] = useState('');
  const [selectedProvider, setSelectedProvider] =
    useState<OAuthProvider | null>(null);
  const [showConsent, setShowConsent] = useState(false);

  useEffect(() => {
    // Load real integrations data
    loadIntegrations();
  }, [loadIntegrations]);

  const handleConsent = async (scopes: string[]) => {
    if (!selectedProvider) return;

    try {
      // TODO: Implement actual OAuth connection
      console.log(`Connecting to ${selectedProvider} with scopes:`, scopes);

      // Close consent modal
      setShowConsent(false);
      setSelectedProvider(null);
    } catch (error) {
      console.error('Failed to connect:', error);
      // Note: setError is not available in oauthSettingsStore, so we'll log it
      console.error('Failed to connect to the service. Please try again.');
    }
  };

  const handleCancelConsent = () => {
    setShowConsent(false);
    setSelectedProvider(null);
  };

  const filteredProviders = OAUTH_PROVIDERS.filter(
    provider =>
      provider.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      provider.description.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const connectedCount = integrations.filter(
    i => i.status === 'active' && i.is_active
  ).length;
  const totalProviders = OAUTH_PROVIDERS.length;

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <Loading size="lg" text="Loading OAuth integrations..." />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          OAuth Integrations
        </h1>
        <p className="text-gray-600 max-w-2xl mx-auto">
          Connect your accounts to external services to enhance your personal
          assistant experience. Choose which permissions to grant and manage
          your connections securely.
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="p-4 text-center">
          <div className="text-2xl font-bold text-blue-600">
            {connectedCount}
          </div>
          <div className="text-sm text-gray-600">Connected Services</div>
        </Card>
        <Card className="p-4 text-center">
          <div className="text-2xl font-bold text-gray-600">
            {totalProviders}
          </div>
          <div className="text-sm text-gray-600">Available Services</div>
        </Card>
        <Card className="p-4 text-center">
          <div className="text-2xl font-bold text-green-600">
            {totalProviders > 0
              ? Math.round((connectedCount / totalProviders) * 100)
              : 0}
            %
          </div>
          <div className="text-sm text-gray-600">Integration Rate</div>
        </Card>
      </div>

      {/* Search */}
      <div className="max-w-md mx-auto">
        <Input
          type="text"
          placeholder="Search services..."
          value={searchTerm}
          onChange={e => setSearchTerm(e.target.value)}
          className="w-full"
        />
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center">
            <div className="text-red-600 text-sm">{error}</div>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => {}} // setError is not available
              className="ml-auto text-red-600 hover:text-red-800"
            >
              Dismiss
            </Button>
          </div>
        </div>
      )}

      {/* Provider Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredProviders.map(provider => (
          <OAuthProviderCard key={provider.id} provider={provider.id} />
        ))}
      </div>

      {/* Empty State */}
      {filteredProviders.length === 0 && (
        <div className="text-center py-12">
          <div className="text-gray-400 text-6xl mb-4">🔍</div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            No services found
          </h3>
          <p className="text-gray-600">
            Try adjusting your search terms or browse all available services.
          </p>
        </div>
      )}

      {/* Consent Modal */}
      {showConsent && selectedProvider && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="max-w-4xl w-full max-h-full overflow-y-auto">
            <OAuthConsent
              provider={selectedProvider}
              onConsent={handleConsent}
              onCancel={handleCancelConsent}
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default OAuthManager;
