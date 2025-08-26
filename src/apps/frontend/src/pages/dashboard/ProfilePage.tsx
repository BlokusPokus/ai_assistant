import React from 'react';
import {
  ProfileForm,
  SettingsForm,
  SecuritySettings,
  PhoneManagement,
} from '@/components/profile';

const ProfilePage: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Profile & Settings</h1>
        <p className="text-gray-600">
          Manage your personal information, preferences, and security settings.
        </p>
      </div>

      {/* Profile Information */}
      <ProfileForm />

      {/* Application Settings */}
      <SettingsForm />

      {/* Security Settings */}
      <SecuritySettings />

      {/* Phone Management */}
      <PhoneManagement />
    </div>
  );
};

export default ProfilePage;
