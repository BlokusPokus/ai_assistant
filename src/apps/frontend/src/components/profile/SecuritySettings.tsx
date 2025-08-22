import React, { useState } from 'react';
import { Button, Input, Card } from '@/components/ui';
import { Shield, Lock, Key, Save, Edit, X } from 'lucide-react';

const SecuritySettings: React.FC = () => {
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: '',
  });
  const [mfaMethod] = useState<'totp' | 'sms'>('totp');

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    // TODO: Implement password change logic
    console.log('Password change:', formData);
    setIsEditing(false);
  };

  const handleEdit = () => {
    setIsEditing(true);
  };

  const handleCancel = () => {
    setIsEditing(false);
    setFormData({
      currentPassword: '',
      newPassword: '',
      confirmPassword: '',
    });
  };

  return (
    <Card padding="lg">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-gray-900">
          Security Settings
        </h2>
        {!isEditing && (
          <Button onClick={handleEdit} variant="outline" size="sm">
            <Edit className="w-4 h-4 mr-2" />
            Change Password
          </Button>
        )}
      </div>

      <div className="space-y-6">
        {/* MFA Status */}
        <div>
          <h3 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
            <Shield className="w-5 h-5 mr-2 text-gray-600" />
            Two-Factor Authentication
          </h3>
          <div className="bg-green-50 border border-green-200 rounded-md p-4">
            <div className="flex items-center">
              <div className="w-2 h-2 bg-green-500 rounded-full mr-3"></div>
              <span className="text-sm font-medium text-green-800">
                MFA is currently enabled
              </span>
            </div>
            <p className="text-sm text-green-700 mt-1">
              Your account is protected with two-factor authentication using{' '}
              {mfaMethod.toUpperCase()}.
            </p>
          </div>
        </div>

        {/* Password Change Form */}
        {isEditing && (
          <form onSubmit={handleSubmit} className="space-y-4">
            <h3 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
              <Lock className="w-5 h-5 mr-2 text-gray-600" />
              Change Password
            </h3>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Current Password
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Key className="h-5 w-5 text-gray-400" />
                </div>
                <Input
                  type="password"
                  value={formData.currentPassword}
                  onChange={value =>
                    handleInputChange('currentPassword', value)
                  }
                  placeholder="Enter your current password"
                  required
                  className="pl-10"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                New Password
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Lock className="h-5 w-5 text-gray-400" />
                </div>
                <Input
                  type="password"
                  value={formData.newPassword}
                  onChange={value => handleInputChange('newPassword', value)}
                  placeholder="Enter your new password"
                  required
                  className="pl-10"
                />
              </div>
              <p className="mt-1 text-xs text-gray-500">
                Password must be at least 8 characters long
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Confirm New Password
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Lock className="h-5 w-5 text-gray-400" />
                </div>
                <Input
                  type="password"
                  value={formData.confirmPassword}
                  onChange={value =>
                    handleInputChange('confirmPassword', value)
                  }
                  placeholder="Confirm your new password"
                  required
                  className="pl-10"
                />
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex items-center justify-end space-x-3 pt-4 border-t border-gray-200">
              <Button type="button" variant="outline" onClick={handleCancel}>
                <X className="w-4 h-4 mr-2" />
                Cancel
              </Button>
              <Button type="submit">
                <Save className="w-4 h-4 mr-2" />
                Change Password
              </Button>
            </div>
          </form>
        )}

        {/* Security Information */}
        <div>
          <h3 className="text-lg font-medium text-gray-900 mb-4 flex items-center">
            <Shield className="w-5 h-5 mr-2 text-gray-600" />
            Security Information
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-gray-500">Last Password Change:</span>
              <span className="ml-2 font-medium text-gray-900">Never</span>
            </div>
            <div>
              <span className="text-gray-500">Session Timeout:</span>
              <span className="ml-2 font-medium text-gray-900">24 hours</span>
            </div>
            <div>
              <span className="text-gray-500">MFA Method:</span>
              <span className="ml-2 font-medium text-gray-900">
                {mfaMethod.toUpperCase()}
              </span>
            </div>
            <div>
              <span className="text-gray-500">Backup Codes:</span>
              <span className="ml-2 font-medium text-gray-900">Generated</span>
            </div>
          </div>
        </div>
      </div>
    </Card>
  );
};

export default SecuritySettings;
