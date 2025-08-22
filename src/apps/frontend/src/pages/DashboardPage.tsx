import React from 'react';
import { Button, Card } from '@/components/ui';
import {
  Brain,
  LogOut,
  User,
  Settings,
  MessageSquare,
  Calendar,
  FileText,
  Shield,
} from 'lucide-react';
import { useAuthStore } from '@/stores/authStore';

const DashboardPage: React.FC = () => {
  const { user, logout } = useAuthStore();

  const handleLogout = async () => {
    await logout();
    window.location.href = '/';
  };

  const quickActions = [
    {
      icon: MessageSquare,
      title: 'Start Chat',
      description: 'Begin a conversation with your AI assistant',
      action: () => console.log('Start chat'),
    },
    {
      icon: Calendar,
      title: 'View Schedule',
      description: 'Check your upcoming appointments and tasks',
      action: () => console.log('View schedule'),
    },
    {
      icon: FileText,
      title: 'My Notes',
      description: 'Access your saved notes and documents',
      action: () => console.log('View notes'),
    },
    {
      icon: Settings,
      title: 'Settings',
      description: 'Manage your account preferences',
      action: () => console.log('Open settings'),
    },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation Header */}
      <nav className="bg-white shadow-sm border-b border-gray-200">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Brain className="w-8 h-8 text-blue-600" />
              <span className="text-xl font-bold text-gray-900">
                Personal Assistant TDAH
              </span>
            </div>

            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <User className="w-5 h-5 text-gray-600" />
                <span className="text-gray-700">
                  {user?.full_name || 'User'}
                </span>
              </div>
              <Button variant="outline" size="sm" onClick={handleLogout}>
                <LogOut className="w-4 h-4 mr-2" />
                Logout
              </Button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-8">
        {/* Welcome Section */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Welcome back, {user?.full_name || 'User'}! 👋
          </h1>
          <p className="text-gray-600">
            Your AI assistant is ready to help you stay organized and
            productive.
          </p>
        </div>

        {/* Quick Actions Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {quickActions.map((action, index) => (
            <div key={index} className="cursor-pointer" onClick={action.action}>
              <Card padding="lg" className="hover:shadow-md transition-shadow">
                <div className="text-center space-y-3">
                  <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto">
                    <action.icon className="w-6 h-6 text-blue-600" />
                  </div>
                  <h3 className="font-semibold text-gray-900">
                    {action.title}
                  </h3>
                  <p className="text-sm text-gray-600">{action.description}</p>
                </div>
              </Card>
            </div>
          ))}
        </div>

        {/* Recent Activity */}
        <Card title="Recent Activity" padding="lg" className="mb-8">
          <div className="space-y-4">
            <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <span className="text-sm text-gray-600">
                Successfully logged in to your account
              </span>
              <span className="text-xs text-gray-400 ml-auto">Just now</span>
            </div>
            <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
              <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
              <span className="text-sm text-gray-600">
                Two-factor authentication enabled
              </span>
              <span className="text-xs text-gray-400 ml-auto">Just now</span>
            </div>
            <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
              <div className="w-2 h-2 bg-gray-400 rounded-full"></div>
              <span className="text-sm text-gray-600">
                Account created successfully
              </span>
              <span className="text-xs text-gray-400 ml-auto">Just now</span>
            </div>
          </div>
        </Card>

        {/* System Status */}
        <Card title="System Status" padding="lg">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-3">
                <Brain className="w-8 h-8 text-green-600" />
              </div>
              <h4 className="font-medium text-gray-900 mb-1">AI Assistant</h4>
              <p className="text-sm text-green-600">Online & Ready</p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3">
                <MessageSquare className="w-8 h-8 text-blue-600" />
              </div>
              <h4 className="font-medium text-gray-900 mb-1">SMS Service</h4>
              <p className="text-sm text-blue-600">Connected</p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-3">
                <Shield className="w-8 h-8 text-purple-600" />
              </div>
              <h4 className="font-medium text-gray-900 mb-1">Security</h4>
              <p className="text-sm text-purple-600">MFA Enabled</p>
            </div>
          </div>
        </Card>

        {/* Coming Soon */}
        <div className="mt-8 text-center">
          <Card
            padding="lg"
            className="bg-gradient-to-r from-blue-50 to-purple-50 border-blue-200"
          >
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              🚀 More Features Coming Soon!
            </h3>
            <p className="text-gray-600 mb-4">
              We're working hard to bring you more powerful features including
              advanced chat, calendar integration, and mobile apps.
            </p>
            <Button variant="outline" size="sm">
              Learn More
            </Button>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
