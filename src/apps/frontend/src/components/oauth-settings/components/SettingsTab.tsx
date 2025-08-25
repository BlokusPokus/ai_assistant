import React, { useState } from "react";
import { useOAuthSettingsStore } from "../../../stores/oauthSettingsStore";
import type { OAuthSettings } from "../../../services/oauthSettingsService";

export const SettingsTab: React.FC = () => {
  const { settings, loading, updateSettings } = useOAuthSettingsStore();
  const [localSettings, setLocalSettings] = useState<OAuthSettings | null>(null);
  const [isEditing, setIsEditing] = useState(false);

  React.useEffect(() => {
    if (settings && !localSettings) {
      setLocalSettings(settings);
    }
  }, [settings, localSettings]);

  const handleSettingChange = (key: keyof OAuthSettings, value: any) => {
    if (localSettings) {
      setLocalSettings({
        ...localSettings,
        [key]: value,
      });
    }
  };

  const handleNestedSettingChange = (
    parentKey: keyof OAuthSettings,
    childKey: string,
    value: any
  ) => {
    if (localSettings) {
      setLocalSettings({
        ...localSettings,
        [parentKey]: {
          ...localSettings[parentKey],
          [childKey]: value,
        },
      });
    }
  };

  const handleSave = async () => {
    if (localSettings) {
      await updateSettings(localSettings);
      setIsEditing(false);
    }
  };

  const handleCancel = () => {
    if (settings) {
      setLocalSettings(settings);
    }
    setIsEditing(false);
  };

  if (loading || !localSettings) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="px-4 sm:px-0">
      {/* Settings Header */}
      <div className="bg-white shadow rounded-lg mb-6">
        <div className="px-4 py-5 sm:p-6">
          <div className="flex items-center justify-between">
            <h3 className="text-lg leading-6 font-medium text-gray-900">
              OAuth Settings
            </h3>
            <div className="flex space-x-3">
              {isEditing ? (
                <>
                  <button
                    onClick={handleCancel}
                    className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleSave}
                    className="px-4 py-2 border border-transparent rounded-md text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
                  >
                    Save Changes
                  </button>
                </>
              ) : (
                <button
                  onClick={() => setIsEditing(true)}
                  className="px-4 py-2 border border-transparent rounded-md text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
                >
                  Edit Settings
                </button>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Token Management Settings */}
      <div className="bg-white shadow rounded-lg mb-6">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
            Token Management
          </h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <label className="text-sm font-medium text-gray-700">
                  Auto-refresh tokens
                </label>
                <p className="text-sm text-gray-500">
                  Automatically refresh OAuth tokens before they expire
                </p>
              </div>
              <input
                type="checkbox"
                checked={localSettings.autoRefreshTokens}
                onChange={(e) =>
                  handleSettingChange("autoRefreshTokens", e.target.checked)
                }
                disabled={!isEditing}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500 disabled:opacity-50"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Refresh threshold (minutes)
              </label>
              <input
                type="number"
                value={localSettings.refreshThreshold}
                onChange={(e) =>
                  handleSettingChange("refreshThreshold", parseInt(e.target.value))
                }
                disabled={!isEditing}
                min="1"
                max="1440"
                className="w-32 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
              />
              <p className="text-sm text-gray-500 mt-1">
                Refresh tokens this many minutes before they expire
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Notification Settings */}
      <div className="bg-white shadow rounded-lg mb-6">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
            Notifications
          </h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <label className="text-sm font-medium text-gray-700">
                  Token expiry notifications
                </label>
                <p className="text-sm text-gray-500">
                  Get notified when OAuth tokens are about to expire
                </p>
              </div>
              <input
                type="checkbox"
                checked={localSettings.notifications.tokenExpiry}
                onChange={(e) =>
                  handleNestedSettingChange(
                    "notifications",
                    "tokenExpiry",
                    e.target.checked
                  )
                }
                disabled={!isEditing}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500 disabled:opacity-50"
              />
            </div>
            <div className="flex items-center justify-between">
              <div>
                <label className="text-sm font-medium text-gray-700">
                  Sync failure notifications
                </label>
                <p className="text-sm text-gray-500">
                  Get notified when OAuth integrations fail to sync
                </p>
              </div>
              <input
                type="checkbox"
                checked={localSettings.notifications.syncFailures}
                onChange={(e) =>
                  handleNestedSettingChange(
                    "notifications",
                    "syncFailures",
                    e.target.checked
                  )
                }
                disabled={!isEditing}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500 disabled:opacity-50"
              />
            </div>
            <div className="flex items-center justify-between">
              <div>
                <label className="text-sm font-medium text-gray-700">
                  Security alerts
                </label>
                <p className="text-sm text-gray-500">
                  Get notified about security-related OAuth events
                </p>
              </div>
              <input
                type="checkbox"
                checked={localSettings.notifications.securityAlerts}
                onChange={(e) =>
                  handleNestedSettingChange(
                    "notifications",
                    "securityAlerts",
                    e.target.checked
                  )
                }
                disabled={!isEditing}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500 disabled:opacity-50"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Security Settings */}
      <div className="bg-white shadow rounded-lg mb-6">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
            Security
          </h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <label className="text-sm font-medium text-gray-700">
                  Require re-authentication for revocation
                </label>
                <p className="text-sm text-gray-500">
                  Require password confirmation before revoking OAuth integrations
                </p>
              </div>
              <input
                type="checkbox"
                checked={localSettings.security.requireReauthForRevoke}
                onChange={(e) =>
                  handleNestedSettingChange(
                    "security",
                    "requireReauthForRevoke",
                    e.target.checked
                  )
                }
                disabled={!isEditing}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500 disabled:opacity-50"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Audit log retention (days)
              </label>
              <input
                type="number"
                value={localSettings.security.auditLogRetention}
                onChange={(e) =>
                  handleNestedSettingChange(
                    "security",
                    "auditLogRetention",
                    parseInt(e.target.value)
                  )
                }
                disabled={!isEditing}
                min="30"
                max="365"
                className="w-32 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
              />
              <p className="text-sm text-gray-500 mt-1">
                How long to keep OAuth audit logs (30-365 days)
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Information Notice */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex">
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
            <h3 className="text-sm font-medium text-blue-800">
              Settings Information
            </h3>
            <div className="mt-2 text-sm text-blue-700">
              <p>
                These settings control how OAuth integrations are managed and
                secured. Changes take effect immediately after saving.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
