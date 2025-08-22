import React from 'react';
import { User, Shield } from 'lucide-react';
import { useAuthStore } from '@/stores/authStore';

interface UserProfileCardProps {
  isCollapsed?: boolean;
}

const UserProfileCard: React.FC<UserProfileCardProps> = ({
  isCollapsed = false,
}) => {
  const { user } = useAuthStore();

  if (!user) {
    return null;
  }

  if (isCollapsed) {
    return (
      <div className="flex justify-center">
        <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
          <User className="w-4 h-4 text-blue-600" />
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {/* Avatar */}
      <div className="flex items-center space-x-3">
        <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
          <User className="w-5 h-5 text-blue-600" />
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-gray-900 truncate">
            {user.full_name}
          </p>
          <p className="text-xs text-gray-500 truncate">{user.email}</p>
        </div>
      </div>

      {/* Status indicators */}
      <div className="space-y-2">
        <div className="flex items-center space-x-2 text-xs">
          <div className="w-2 h-2 bg-green-500 rounded-full"></div>
          <span className="text-gray-600">Active</span>
        </div>
        <div className="flex items-center space-x-2 text-xs">
          <Shield className="w-3 h-3 text-blue-500" />
          <span className="text-gray-600">MFA Enabled</span>
        </div>
      </div>
    </div>
  );
};

export default UserProfileCard;
