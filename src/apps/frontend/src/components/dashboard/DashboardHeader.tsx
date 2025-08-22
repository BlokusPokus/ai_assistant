import React from 'react';
import { useLocation } from 'react-router-dom';
import { Button } from '@/components/ui';
import { Bell, Search, Menu } from 'lucide-react';
import Breadcrumbs from '../navigation/Breadcrumbs';

interface DashboardHeaderProps {
  onMenuToggle?: () => void;
}

const DashboardHeader: React.FC<DashboardHeaderProps> = ({ onMenuToggle }) => {
  const location = useLocation();

  const getPageTitle = (pathname: string) => {
    const pathMap: Record<string, string> = {
      '/dashboard': 'Dashboard',
      '/dashboard/chat': 'Chat',
      '/dashboard/calendar': 'Calendar',
      '/dashboard/notes': 'Notes',
      '/dashboard/profile': 'Profile',
      '/dashboard/settings': 'Settings',
      '/dashboard/security': 'Security',
    };
    return pathMap[pathname] || 'Dashboard';
  };

  return (
    <header className="bg-white border-b border-gray-200 px-4 py-4 lg:px-6">
      <div className="flex items-center justify-between">
        {/* Left side - Menu toggle and breadcrumbs */}
        <div className="flex items-center space-x-4">
          {/* Mobile menu toggle */}
          <Button
            variant="ghost"
            size="sm"
            onClick={onMenuToggle}
            className="lg:hidden"
          >
            <Menu className="h-5 w-5" />
          </Button>

          {/* Breadcrumbs */}
          <div className="hidden md:block">
            <Breadcrumbs currentPath={location.pathname} />
          </div>

          {/* Page title for mobile */}
          <h1 className="text-lg font-semibold text-gray-900 md:hidden">
            {getPageTitle(location.pathname)}
          </h1>
        </div>

        {/* Right side - Search, notifications, user */}
        <div className="flex items-center space-x-3">
          {/* Search */}
          <div className="hidden md:block relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Search className="h-4 w-4 text-gray-400" />
            </div>
            <input
              type="text"
              placeholder="Search..."
              className="block w-64 pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
            />
          </div>

          {/* Notifications */}
          <Button variant="ghost" size="sm" className="relative">
            <Bell className="h-5 w-5" />
            <span className="absolute -top-1 -right-1 h-3 w-3 bg-red-500 rounded-full"></span>
          </Button>

          {/* User menu placeholder */}
          <div className="hidden md:block">
            <Button variant="ghost" size="sm">
              <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                <span className="text-sm font-medium text-blue-600">U</span>
              </div>
            </Button>
          </div>
        </div>
      </div>
    </header>
  );
};

export default DashboardHeader;
