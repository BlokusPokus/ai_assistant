import React from 'react';
import OAuthManager from './OAuthManager';
import { useOAuthSettingsStore } from '../../stores/oauthSettingsStore';

const OAuthIntegrationsPage: React.FC = () => {
  const { loadIntegrations } = useOAuthSettingsStore();

  // Load real integrations data instead of mock data
  React.useEffect(() => {
    loadIntegrations();
  }, [loadIntegrations]);

  return (
    <div className="space-y-6">
      <OAuthManager />
    </div>
  );
};

export default OAuthIntegrationsPage;
