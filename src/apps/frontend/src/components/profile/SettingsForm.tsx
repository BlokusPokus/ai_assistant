import React, { useState, useEffect } from 'react';
import {
  Button,
  Card,
  CardHeader,
  CardTitle,
  CardContent,
  Select,
} from '@/components/ui';
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

  const handleInputChange = (
    section: string,
    field: string,
    value: string | number | boolean
  ) => {
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

  const handleSimpleChange = (
    field: string,
    value: string | number | boolean
  ) => {
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
      <Card>
        <CardContent>
          <div className="animate-pulse space-y-6">
            <div className="h-6 bg-gray-200 rounded w-1/4"></div>
            <div className="space-y-4">
              <div className="h-12 bg-gray-200 rounded-2xl"></div>
              <div className="h-12 bg-gray-200 rounded-2xl"></div>
              <div className="h-12 bg-gray-200 rounded-2xl"></div>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  const themeOptions = [
    { value: 'light', label: 'Light Theme' },
    { value: 'dark', label: 'Dark Theme' },
    { value: 'system', label: 'System Default' },
  ];

  const languageOptions = [
    { value: 'en', label: 'English' },
    { value: 'fr', label: 'Français' },
    { value: 'es', label: 'Español' },
  ];

  const visibilityOptions = [
    { value: 'private', label: 'Private' },
    { value: 'friends', label: 'Friends Only' },
    { value: 'public', label: 'Public' },
  ];

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Application Settings</CardTitle>
          {!isEditing && (
            <Button onClick={handleEdit} variant="secondary" size="sm">
              <Edit className="w-4 h-4 mr-2" />
              Edit Settings
            </Button>
          )}
        </div>
      </CardHeader>

      <CardContent>
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-2xl">
            <p className="text-sm text-red-600 font-medium">{error}</p>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-8">
          {/* Theme Settings */}
          <div className="space-y-6">
            <h3 className="text-lg font-semibold text-primary flex items-center">
              <Moon className="w-5 h-5 mr-3 text-accent" />
              Appearance
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Select
                label="Theme"
                options={themeOptions}
                value={formData.theme}
                onChange={value => handleSimpleChange('theme', value)}
                disabled={!isEditing}
                placeholder="Select a theme"
              />
              <Select
                label="Language"
                options={languageOptions}
                value={formData.language}
                onChange={value => handleSimpleChange('language', value)}
                disabled={!isEditing}
                placeholder="Select a language"
              />
            </div>
          </div>

          {/* Notification Settings */}
          <div className="space-y-6">
            <h3 className="text-lg font-semibold text-primary flex items-center">
              <Bell className="w-5 h-5 mr-3 text-accent" />
              Notifications
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="space-y-3">
                <label className="block text-sm font-medium text-primary font-semibold">
                  Email Notifications
                </label>
                <div className="flex items-center space-x-3">
                  <input
                    type="checkbox"
                    id="email-notifications"
                    checked={formData.notifications.email}
                    onChange={e =>
                      handleInputChange(
                        'notifications',
                        'email',
                        e.target.checked
                      )
                    }
                    disabled={!isEditing}
                    className="w-5 h-5 text-accent bg-white border-gray-300 rounded-lg focus:ring-accent focus:ring-2 focus:ring-offset-2"
                  />
                  <label
                    htmlFor="email-notifications"
                    className="text-sm text-gray-600"
                  >
                    Receive email notifications
                  </label>
                </div>
              </div>

              <div className="space-y-3">
                <label className="block text-sm font-medium text-primary font-semibold">
                  SMS Notifications
                </label>
                <div className="flex items-center space-x-3">
                  <input
                    type="checkbox"
                    id="sms-notifications"
                    checked={formData.notifications.sms}
                    onChange={e =>
                      handleInputChange(
                        'notifications',
                        'sms',
                        e.target.checked
                      )
                    }
                    disabled={!isEditing}
                    className="w-5 h-5 text-accent bg-white border-gray-300 rounded-lg focus:ring-accent focus:ring-2 focus:ring-offset-2"
                  />
                  <label
                    htmlFor="sms-notifications"
                    className="text-sm text-gray-600"
                  >
                    Receive SMS notifications
                  </label>
                </div>
              </div>

              <div className="space-y-3">
                <label className="block text-sm font-medium text-primary font-semibold">
                  Push Notifications
                </label>
                <div className="flex items-center space-x-3">
                  <input
                    type="checkbox"
                    id="push-notifications"
                    checked={formData.notifications.push}
                    onChange={e =>
                      handleInputChange(
                        'notifications',
                        'push',
                        e.target.checked
                      )
                    }
                    disabled={!isEditing}
                    className="w-5 h-5 text-accent bg-white border-gray-300 rounded-lg focus:ring-accent focus:ring-2 focus:ring-offset-2"
                  />
                  <label
                    htmlFor="push-notifications"
                    className="text-sm text-gray-600"
                  >
                    Receive push notifications
                  </label>
                </div>
              </div>
            </div>
          </div>

          {/* Privacy Settings */}
          <div className="space-y-6">
            <h3 className="text-lg font-semibold text-primary flex items-center">
              <Globe className="w-5 h-5 mr-3 text-accent" />
              Privacy
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Select
                label="Profile Visibility"
                options={visibilityOptions}
                value={formData.privacy.profile_visibility}
                onChange={value =>
                  handleInputChange('privacy', 'profile_visibility', value)
                }
                disabled={!isEditing}
                placeholder="Select visibility"
              />
              <Select
                label="Activity Visibility"
                options={visibilityOptions}
                value={formData.privacy.activity_visibility}
                onChange={value =>
                  handleInputChange('privacy', 'activity_visibility', value)
                }
                disabled={!isEditing}
                placeholder="Select visibility"
              />
            </div>
          </div>

          {/* Action Buttons */}
          {isEditing && (
            <div className="flex items-center justify-end space-x-4 pt-6 border-t border-white/20">
              <Button
                type="button"
                variant="ghost"
                onClick={handleCancel}
                size="md"
              >
                <X className="w-4 h-4 mr-2" />
                Cancel
              </Button>
              <Button
                type="submit"
                variant="primary"
                size="md"
                loading={isLoading}
              >
                <Save className="w-4 h-4 mr-2" />
                Save Changes
              </Button>
            </div>
          )}
        </form>
      </CardContent>
    </Card>
  );
};

export default SettingsForm;
