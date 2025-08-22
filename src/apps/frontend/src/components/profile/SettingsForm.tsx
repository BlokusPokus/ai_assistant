import React, { useState, useEffect } from 'react';
import { Button, Card } from '@/components/ui';
import { useProfileStore } from '@/stores/profileStore';
import { Bell, Globe, Moon, Save, Edit, X } from 'lucide-react';

const SettingsForm: React.FC = () => {
  const {
    preferences,
    isLoading,
    error,
    isEditing,
    fetchPreferences,
    updatePreferences,
    setEditing,
    clearError,
  } = useProfileStore();
  const [formData, setFormData] = useState({
    theme: 'light',
    language: 'en',
    notifications: {
      email: true,
      sms: false,
      push: true,
    },
    privacy: {
      profile_visibility: 'private',
      activity_visibility: 'friends',
    },
  });

  useEffect(() => {
    fetchPreferences();
  }, [fetchPreferences]);

  useEffect(() => {
    if (preferences) {
      // Merge with defaults
      const userPrefs = preferences.preferences || {};
      const userSettings = preferences.settings || {};

      setFormData(prev => ({
        ...prev,
        ...userPrefs,
        ...userSettings,
      }));
    }
  }, [preferences]);

  const handleInputChange = (section: string, field: string, value: any) => {
    setFormData(prev => {
      const sectionData = prev[section as keyof typeof prev];
      if (typeof sectionData === 'object' && sectionData !== null) {
        return {
          ...prev,
          [section]: {
            ...sectionData,
            [field]: value,
          },
        };
      }
      return prev;
    });
  };

  const handleSimpleChange = (field: string, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    clearError();

    const success = await updatePreferences({
      preferences: {
        theme: formData.theme,
        language: formData.language,
        notifications: formData.notifications,
        privacy: formData.privacy,
      },
    });

    if (success) {
      setEditing(false);
    }
  };

  const handleEdit = () => {
    setEditing(true);
    clearError();
  };

  const handleCancel = () => {
    setEditing(false);
    clearError();
    // Reset form to original values
    if (preferences) {
      setFormData(prev => ({
        ...prev,
        ...preferences.preferences,
        ...preferences.settings,
      }));
    }
  };

  if (isLoading && !preferences) {
    return (
      <Card padding="lg">
        <div className="animate-pulse space-y-4">
          <div className="h-4 bg-gray-200 rounded w-1/4"></div>
          <div className="space-y-3">
            <div className="h-10 bg-gray-200 rounded"></div>
            <div className="h-10 bg-gray-200 rounded"></div>
            <div className="h-10 bg-gray-200 rounded"></div>
          </div>
        </div>
      </Card>
    );
  }

  return (
    <Card padding="lg">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-gray-900">
          Application Settings
        </h2>
        {!isEditing && (
          <Button onClick={handleEdit} variant="outline" size="sm">
            <Edit className="w-4 h-4 mr-2" />
            Edit Settings
          </Button>
        )}
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
          <p className="text-sm text-red-600">{error}</p>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Theme Settings */}
        <div>
          <h3 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
            <Moon className="w-5 h-5 mr-2 text-gray-600" />
            Appearance
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Theme
              </label>
              <select
                value={formData.theme}
                onChange={e => handleSimpleChange('theme', e.target.value)}
                disabled={!isEditing}
                className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-50 disabled:cursor-not-allowed"
              >
                <option value="light">Light</option>
                <option value="dark">Dark</option>
                <option value="system">System</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Language
              </label>
              <select
                value={formData.language}
                onChange={e => handleSimpleChange('language', e.target.value)}
                disabled={!isEditing}
                className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-50 disabled:cursor-not-allowed"
              >
                <option value="en">English</option>
                <option value="fr">Français</option>
                <option value="es">Español</option>
              </select>
            </div>
          </div>
        </div>

        {/* Notification Settings */}
        <div>
          <h3 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
            <Bell className="w-5 h-5 mr-2 text-gray-600" />
            Notifications
          </h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div>
                <label className="text-sm font-medium text-gray-700">
                  Email Notifications
                </label>
                <p className="text-xs text-gray-500">
                  Receive notifications via email
                </p>
              </div>
              <input
                type="checkbox"
                checked={formData.notifications.email}
                onChange={e =>
                  handleInputChange('notifications', 'email', e.target.checked)
                }
                disabled={!isEditing}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded disabled:opacity-50"
              />
            </div>
            <div className="flex items-center justify-between">
              <div>
                <label className="text-sm font-medium text-gray-700">
                  SMS Notifications
                </label>
                <p className="text-xs text-gray-500">
                  Receive notifications via SMS
                </p>
              </div>
              <input
                type="checkbox"
                checked={formData.notifications.sms}
                onChange={e =>
                  handleInputChange('notifications', 'sms', e.target.checked)
                }
                disabled={!isEditing}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded disabled:opacity-50"
              />
            </div>
            <div className="flex items-center justify-between">
              <div>
                <label className="text-sm font-medium text-gray-700">
                  Push Notifications
                </label>
                <p className="text-xs text-gray-500">
                  Receive push notifications in browser
                </p>
              </div>
              <input
                type="checkbox"
                checked={formData.notifications.push}
                onChange={e =>
                  handleInputChange('notifications', 'push', e.target.checked)
                }
                disabled={!isEditing}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded disabled:opacity-50"
              />
            </div>
          </div>
        </div>

        {/* Privacy Settings */}
        <div>
          <h3 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
            <Globe className="w-5 h-5 mr-2 text-gray-600" />
            Privacy
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Profile Visibility
              </label>
              <select
                value={formData.privacy.profile_visibility}
                onChange={e =>
                  handleInputChange(
                    'privacy',
                    'profile_visibility',
                    e.target.value
                  )
                }
                disabled={!isEditing}
                className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-50 disabled:cursor-not-allowed"
              >
                <option value="public">Public</option>
                <option value="friends">Friends Only</option>
                <option value="private">Private</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Activity Visibility
              </label>
              <select
                value={formData.privacy.activity_visibility}
                onChange={e =>
                  handleInputChange(
                    'privacy',
                    'activity_visibility',
                    e.target.value
                  )
                }
                disabled={!isEditing}
                className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-50 disabled:cursor-not-allowed"
              >
                <option value="public">Public</option>
                <option value="friends">Friends Only</option>
                <option value="private">Private</option>
              </select>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        {isEditing && (
          <div className="flex items-center justify-end space-x-3 pt-4 border-t border-gray-200">
            <Button
              type="button"
              variant="outline"
              onClick={handleCancel}
              disabled={isLoading}
            >
              <X className="w-4 h-4 mr-2" />
              Cancel
            </Button>
            <Button type="submit" disabled={isLoading} loading={isLoading}>
              <Save className="w-4 h-4 mr-2" />
              Save Changes
            </Button>
          </div>
        )}
      </form>
    </Card>
  );
};

export default SettingsForm;
