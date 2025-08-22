import React from 'react';
import { SettingsForm } from '@/components/profile';

const SettingsPage: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">
          Application Settings
        </h1>
        <p className="text-gray-600">
          Customize your experience with theme, notifications, and privacy
          settings.
        </p>
      </div>

      <SettingsForm />
    </div>
  );
};

export default SettingsPage;
