import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui';
import {
  Brain,
  User,
  Settings,
  MessageSquare,
  Calendar,
  FileText,
  Shield,
  ChevronLeft,
  ChevronRight,
  LogOut,
  Link,
} from 'lucide-react';
import { useAuthStore } from '@/stores/authStore';
import { useDashboardStore } from '@/stores/dashboardStore';
import UserProfileCard from '@/components/dashboard/UserProfileCard';
import NavigationMenu from '../navigation/NavigationMenu';

interface SidebarProps {
  isCollapsed?: boolean;
  onToggle?: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ isCollapsed = false, onToggle }) => {
  const navigate = useNavigate();
  const { logout } = useAuthStore();
  const { isMobileMenuOpen, setMobileMenuOpen } = useDashboardStore();

  const handleLogout = async () => {
    await logout();
    navigate('/');
  };

  const navigationItems = [
    {
      label: 'Dashboard',
      href: '/dashboard',
      icon: Brain,
      exact: true,
    },
    {
      label: 'Chat',
      href: '/dashboard/chat',
      icon: MessageSquare,
    },
    {
      label: 'Calendar',
      href: '/dashboard/calendar',
      icon: Calendar,
    },
    {
      label: 'Notes',
      href: '/dashboard/notes',
      icon: FileText,
    },
    {
      label: 'Integrations',
      href: '/dashboard/integrations',
      icon: Link,
    },
    {
      label: 'Profile',
      href: '/dashboard/profile',
      icon: User,
    },
    {
      label: 'Settings',
      href: '/dashboard/settings',
      icon: Settings,
    },
    {
      label: 'Security',
      href: '/dashboard/security',
      icon: Shield,
    },
  ];

  const sidebarClasses = `
    fixed left-0 top-0 z-40 h-screen transition-transform duration-300 ease-in-out
    bg-white border-r border-gray-200 shadow-lg
    ${isCollapsed ? 'w-16' : 'w-64'}
    ${isMobileMenuOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
  `;

  const overlayClasses = `
    fixed inset-0 z-30 bg-gray-600 bg-opacity-50 lg:hidden
    ${isMobileMenuOpen ? 'block' : 'hidden'}
  `;

  return (
    <>
      {/* Mobile overlay */}
      <div
        className={overlayClasses}
        onClick={() => setMobileMenuOpen(false)}
      />

      {/* Sidebar */}
      <aside className={sidebarClasses}>
        <div className="flex h-full flex-col">
          {/* Header */}
          <div className="flex h-16 items-center justify-between border-b border-gray-200 px-4">
            <div className="flex items-center space-x-2">
              <Brain className="h-8 w-8 text-blue-600" />
              {!isCollapsed && (
                <span className="text-lg font-bold text-gray-900">
                  TDAH Assistant
                </span>
              )}
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={onToggle}
              className="hidden lg:flex"
            >
              {isCollapsed ? (
                <ChevronRight className="h-4 w-4" />
              ) : (
                <ChevronLeft className="h-4 w-4" />
              )}
            </Button>
          </div>

          {/* User Profile Section */}
          <div className="border-b border-gray-200 p-4">
            <UserProfileCard isCollapsed={isCollapsed} />
          </div>

          {/* Navigation Menu */}
          <div className="flex-1 overflow-y-auto">
            <NavigationMenu items={navigationItems} isCollapsed={isCollapsed} />
          </div>

          {/* Footer */}
          <div className="border-t border-gray-200 p-4">
            <Button
              variant="ghost"
              size="sm"
              onClick={handleLogout}
              className="w-full justify-start text-red-600 hover:bg-red-50 hover:text-red-700"
            >
              <LogOut className="h-4 w-4 mr-2" />
              {!isCollapsed && 'Logout'}
            </Button>
          </div>
        </div>
      </aside>

      {/* Mobile menu button */}
      <button
        onClick={() => setMobileMenuOpen(true)}
        className="fixed top-4 left-4 z-50 lg:hidden bg-white p-2 rounded-md shadow-lg border border-gray-200"
      >
        <Brain className="h-6 w-6 text-blue-600" />
      </button>
    </>
  );
};

export default Sidebar;
