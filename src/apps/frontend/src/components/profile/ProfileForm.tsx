import React, { useState, useEffect } from 'react';
import { Button, Input, Card } from '@/components/ui';
import { useProfileStore } from '@/stores/profileStore';
import { User, Mail, Phone, Save, Edit, X } from 'lucide-react';

const ProfileForm: React.FC = () => {
  const {
    profile,
    isLoading,
    error,
    isEditing,
    fetchProfile,
    updateProfile,
    setEditing,
    clearError,
  } = useProfileStore();
  const [formData, setFormData] = useState({
    full_name: '',
    phone_number: '',
  });

  useEffect(() => {
    fetchProfile();
  }, [fetchProfile]);

  useEffect(() => {
    if (profile) {
      setFormData({
        full_name: profile.full_name || '',
        phone_number: profile.phone_number || '',
      });
    }
  }, [profile]);

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    clearError();

    const success = await updateProfile(formData);
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
    if (profile) {
      setFormData({
        full_name: profile.full_name || '',
        phone_number: profile.phone_number || '',
      });
    }
  };

  if (isLoading && !profile) {
    return (
      <Card>
        <div className="animate-pulse space-y-4">
          <div className="h-4 bg-gray-200 rounded w-1/4"></div>
          <div className="space-y-3">
            <div className="h-10 bg-gray-200 rounded"></div>
            <div className="h-10 bg-gray-200 rounded"></div>
          </div>
        </div>
      </Card>
    );
  }

  if (!profile) {
    return (
      <Card>
        <div className="text-center text-gray-500">
          Failed to load profile information
        </div>
      </Card>
    );
  }

  return (
    <Card>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-gray-900">
          Profile Information
        </h2>
        {!isEditing && (
          <Button onClick={handleEdit} variant="secondary" size="sm">
            <Edit className="w-4 h-4 mr-2" />
            Edit Profile
          </Button>
        )}
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
          <p className="text-sm text-red-600">{error}</p>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Email (read-only) */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Email Address
          </label>
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Mail className="h-5 w-5 text-gray-400" />
            </div>
            <input
              type="email"
              value={profile.email}
              disabled
              className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md bg-gray-50 text-gray-500 cursor-not-allowed"
            />
          </div>
          <p className="mt-1 text-xs text-gray-500">
            Email address cannot be changed
          </p>
        </div>

        {/* Full Name */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Full Name
          </label>
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <User className="h-5 w-5 text-gray-400" />
            </div>
            <Input
              type="text"
              value={formData.full_name}
              onChange={e => handleInputChange('full_name', e.target.value)}
              placeholder="Enter your full name"
              disabled={!isEditing}
              required
              className="pl-10"
            />
          </div>
        </div>

        {/* Phone Number */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Phone Number
          </label>
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Phone className="h-5 w-5 text-gray-400" />
            </div>
            <Input
              type="tel"
              value={formData.phone_number}
              onChange={e => handleInputChange('phone_number', e.target.value)}
              placeholder="Enter your phone number"
              disabled={!isEditing}
              className="pl-10"
            />
          </div>
          <p className="mt-1 text-xs text-gray-500">
            Optional - used for SMS notifications
          </p>
        </div>

        {/* Account Status */}
        <div className="pt-4 border-t border-gray-200">
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-gray-500">Account Status:</span>
              <span
                className={`ml-2 font-medium ${profile.is_active ? 'text-green-600' : 'text-red-600'}`}
              >
                {profile.is_active ? 'Active' : 'Inactive'}
              </span>
            </div>
            <div>
              <span className="text-gray-500">Email Verified:</span>
              <span
                className={`ml-2 font-medium ${profile.is_verified ? 'text-green-600' : 'text-yellow-600'}`}
              >
                {profile.is_verified ? 'Yes' : 'No'}
              </span>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        {isEditing && (
          <div className="flex items-center justify-end space-x-3 pt-4 border-t border-gray-200">
            <Button
              type="button"
              variant="secondary"
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

export default ProfileForm;
