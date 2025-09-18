import React from 'react';
import { useAuthStore } from '../../../stores/authStore';
import { isPremium, isAdmin } from '../../../utils/roleUtils';

interface TabNavigationProps {
  activeTab: string;
  onTabChange: (tab: string) => void;
}

// Define tabs with their permission requirements
const allTabs = [
  { id: 'integrations', name: 'Integrations', icon: '🔗', requiredRole: null },
  { id: 'analytics', name: 'Analytics', icon: '📊', requiredRole: 'premium' },
  {
    id: 'audit',
    name: 'Audit Logs',
    icon: '📋',
    requiredRole: 'administrator',
  },
  { id: 'settings', name: 'Settings', icon: '⚙️', requiredRole: null },
];

export const TabNavigation: React.FC<TabNavigationProps> = ({
  activeTab,
  onTabChange,
}) => {
  const { user } = useAuthStore();

  // Filter tabs based on user permissions
  const getVisibleTabs = () => {
    if (!user) return allTabs;

    return allTabs.filter(tab => {
      switch (tab.requiredRole) {
        case 'premium':
          return isPremium(user);
        case 'administrator':
          return isAdmin(user);
        case null:
        case undefined:
          return true; // Public tabs
        default:
          return false;
      }
    });
  };

  const visibleTabs = getVisibleTabs();

  // If current active tab is not visible, switch to first visible tab
  React.useEffect(() => {
    if (user && !visibleTabs.find(tab => tab.id === activeTab)) {
      onTabChange(visibleTabs[0]?.id || 'integrations');
    }
  }, [user, visibleTabs, activeTab, onTabChange]);

  return (
    <div className="border-b border-gray-200">
      <nav className="-mb-px flex space-x-8 px-4 sm:px-0">
        {visibleTabs.map(tab => (
          <button
            key={tab.id}
            onClick={() => onTabChange(tab.id)}
            className={`
              whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm
              ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }
            `}
          >
            <span className="mr-2">{tab.icon}</span>
            {tab.name}
          </button>
        ))}
      </nav>
    </div>
  );
};
