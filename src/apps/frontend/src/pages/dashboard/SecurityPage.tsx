import React from 'react';
import { SecuritySettings } from '@/components/profile';

const SecurityPage: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Security Settings</h1>
        <p className="text-gray-600">
          Manage your password, two-factor authentication, and account security.
        </p>
      </div>

      <SecuritySettings />
    </div>
  );
};

export default SecurityPage;
