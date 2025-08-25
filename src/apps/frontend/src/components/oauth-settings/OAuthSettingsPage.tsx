import React, { useState, useEffect } from "react";
import { TabNavigation } from "./components/TabNavigation";
import { IntegrationsTab } from "./components/IntegrationsTab";
import { AnalyticsTab } from "./components/AnalyticsTab";
import { AuditTab } from "./components/AuditTab";
import { SettingsTab } from "./components/SettingsTab";
import { useOAuthSettingsStore } from "../../stores/oauthSettingsStore";

export const OAuthSettingsPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState("integrations");
  const {
    loadSettings,
    loadIntegrations,
    loadAnalytics,
    loadAuditLogs,
    loading,
    error,
  } = useOAuthSettingsStore();

  useEffect(() => {
    // Load initial data
    loadSettings();
    loadIntegrations();
  }, [loadSettings, loadIntegrations]);

  const handleTabChange = (tab: string) => {
    setActiveTab(tab);

    // Load tab-specific data
    switch (tab) {
      case "analytics":
        loadAnalytics();
        break;
      case "audit":
        loadAuditLogs();
        break;
      default:
        break;
    }
  };

  const renderTabContent = () => {
    switch (activeTab) {
      case "integrations":
        return <IntegrationsTab />;
      case "analytics":
        return <AnalyticsTab />;
      case "audit":
        return <AuditTab />;
      case "settings":
        return <SettingsTab />;
      default:
        return <IntegrationsTab />;
    }
  };

  if (loading && !activeTab) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        {/* Page Header */}
        <div className="px-4 py-6 sm:px-0">
          <div className="border-b border-gray-200 pb-4">
            <h1 className="text-3xl font-bold text-gray-900">
              OAuth Settings & Management
            </h1>
            <p className="mt-2 text-sm text-gray-600">
              Manage your OAuth integrations, monitor performance, and configure
              security settings.
            </p>
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div className="mb-6 px-4 sm:px-0">
            <div className="bg-red-50 border border-red-200 rounded-md p-4">
              <div className="flex">
                <div className="flex-shrink-0">
                  <svg
                    className="h-5 w-5 text-red-400"
                    viewBox="0 0 20 20"
                    fill="currentColor"
                  >
                    <path
                      fillRule="evenodd"
                      d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                      clipRule="evenodd"
                    />
                  </svg>
                </div>
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-red-800">
                    Error loading OAuth settings
                  </h3>
                  <div className="mt-2 text-sm text-red-700">
                    <p>{error}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* OAuth Configuration Warning */}
        {error && error.includes('OAuth service is not fully configured') && (
          <div className="mb-6 px-4 sm:px-0">
            <div className="bg-yellow-50 border border-yellow-200 rounded-md p-4">
              <div className="flex">
                <div className="flex-shrink-0">
                  <svg
                    className="h-5 w-5 text-yellow-400"
                    viewBox="0 0 20 20"
                    fill="currentColor"
                  >
                    <path
                      fillRule="evenodd"
                      d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
                      clipRule="evenodd"
                    />
                  </svg>
                </div>
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-yellow-800">
                    OAuth Service Configuration Required
                  </h3>
                  <div className="mt-2 text-sm text-yellow-700">
                    <p>
                      The OAuth service requires backend configuration to function properly. 
                      Your administrator needs to set up OAuth provider credentials (Google, Microsoft, Notion, YouTube) 
                      in the backend environment variables.
                    </p>
                    <p className="mt-2">
                      <strong>Required variables:</strong> GOOGLE_OAUTH_CLIENT_ID, GOOGLE_OAUTH_CLIENT_SECRET, 
                      MICROSOFT_OAUTH_CLIENT_ID, MICROSOFT_OAUTH_CLIENT_SECRET, etc.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Tab Navigation */}
        <TabNavigation activeTab={activeTab} onTabChange={handleTabChange} />

        {/* Tab Content */}
        <div className="mt-6">{renderTabContent()}</div>
      </div>
    </div>
  );
};
