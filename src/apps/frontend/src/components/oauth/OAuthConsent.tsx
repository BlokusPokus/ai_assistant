import React, { useState } from 'react';
import { Button, Card, Input } from '@/components/ui';
import { useOAuthStore } from '@/stores/oauthStore';
import type { OAuthProvider } from '@/types/oauth';
import { OAUTH_SCOPES } from '@/constants/oauth';

interface OAuthConsentProps {
  provider: OAuthProvider;
  onConsent: (scopes: string[]) => void;
  onCancel: () => void;
}

const OAuthConsent: React.FC<OAuthConsentProps> = ({
  provider,
  onConsent,
  onCancel,
}) => {
  const { getProviderConfig } = useOAuthStore();
  const [selectedScopes, setSelectedScopes] = useState<string[]>([]);
  const [searchTerm, setSearchTerm] = useState('');

  const providerConfig = getProviderConfig(provider);
  const availableScopes = OAUTH_SCOPES[provider] || [];

  if (!providerConfig) {
    return null;
  }

  const handleScopeToggle = (scopeId: string) => {
    setSelectedScopes(prev =>
      prev.includes(scopeId)
        ? prev.filter(id => id !== scopeId)
        : [...prev, scopeId]
    );
  };

  const handleConsent = () => {
    onConsent(selectedScopes);
  };

  const filteredScopes = availableScopes.filter(
    scope =>
      scope.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      scope.description.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const requiredScopes = availableScopes.filter(scope => scope.required);

  return (
    <Card className="p-6 max-w-2xl mx-auto">
      <div className="text-center mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Connect to {providerConfig.name}
        </h2>
        <p className="text-gray-600">
          Choose which permissions to grant to {providerConfig.name}
        </p>
      </div>

      {/* Search */}
      <div className="mb-6">
        <Input
          type="text"
          placeholder="Search permissions..."
          value={searchTerm}
          onChange={setSearchTerm}
          className="w-full"
        />
      </div>

      {/* Required Scopes */}
      {requiredScopes.length > 0 && (
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-3">
            Required Permissions
          </h3>
          <div className="space-y-3">
            {requiredScopes.map(scope => (
              <div
                key={scope.id}
                className="flex items-start space-x-3 p-3 bg-blue-50 rounded-lg"
              >
                <input
                  type="checkbox"
                  checked={true}
                  disabled={true}
                  className="mt-1 h-4 w-4 text-blue-600 border-gray-300 rounded"
                />
                <div className="flex-1">
                  <div className="flex items-center space-x-2">
                    <span className="font-medium text-gray-900">
                      {scope.name}
                    </span>
                    <span className="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded">
                      Required
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 mt-1">
                    {scope.description}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Optional Scopes */}
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-3">
          Optional Permissions
        </h3>
        <div className="space-y-3">
          {filteredScopes
            .filter(scope => !scope.required)
            .map(scope => (
              <div
                key={scope.id}
                className="flex items-start space-x-3 p-3 border border-gray-200 rounded-lg hover:bg-gray-50"
              >
                <input
                  type="checkbox"
                  checked={selectedScopes.includes(scope.id)}
                  onChange={() => handleScopeToggle(scope.id)}
                  className="mt-1 h-4 w-4 text-blue-600 border-gray-300 rounded"
                />
                <div className="flex-1">
                  <div className="flex items-center space-x-2">
                    <span className="font-medium text-gray-900">
                      {scope.name}
                    </span>
                    <span
                      className={`px-2 py-1 text-xs rounded ${
                        scope.category === 'read'
                          ? 'bg-green-100 text-green-800'
                          : scope.category === 'write'
                            ? 'bg-yellow-100 text-yellow-800'
                            : 'bg-red-100 text-red-800'
                      }`}
                    >
                      {scope.category}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 mt-1">
                    {scope.description}
                  </p>
                </div>
              </div>
            ))}
        </div>
      </div>

      {/* Privacy Notice */}
      <div className="mb-6 p-4 bg-gray-50 rounded-lg">
        <h4 className="font-medium text-gray-900 mb-2">Privacy & Security</h4>
        <p className="text-sm text-gray-600">
          By connecting to {providerConfig.name}, you agree to share the
          selected data. We only access the data you explicitly grant permission
          for, and you can revoke access at any time from your settings.
        </p>
      </div>

      {/* Actions */}
      <div className="flex space-x-3">
        <Button variant="outline" onClick={onCancel} className="flex-1">
          Cancel
        </Button>
        <Button
          variant="primary"
          onClick={handleConsent}
          disabled={selectedScopes.length === 0}
          className="flex-1"
        >
          Connect with Selected Permissions
        </Button>
      </div>
    </Card>
  );
};

export default OAuthConsent;
