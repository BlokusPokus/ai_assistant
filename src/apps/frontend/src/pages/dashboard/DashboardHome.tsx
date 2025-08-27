import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card } from '@/components/ui';
import { useAuthStore } from '@/stores/authStore';
import { useProfileStore } from '@/stores/profileStore';
import { useOAuthStore } from '@/stores/oauthStore';
import SMSAnalyticsWidget from '@/components/dashboard/SMSAnalyticsWidget';
import {
  Brain,
  MessageSquare,
  Calendar,
  FileText,
  Settings,
  TrendingUp,
  Clock,
  CheckCircle,
  Link,
  Key,
} from 'lucide-react';

const DashboardHome: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const { fetchProfile } = useProfileStore();
  const { integrations, loadMockData } = useOAuthStore();

  useEffect(() => {
    fetchProfile();
    loadMockData();
  }, [fetchProfile, loadMockData]);

  const quickActions = [
    {
      icon: MessageSquare,
      title: 'Start Chat',
      description: 'Begin a conversation with your AI assistant',
      action: () => navigate('/dashboard/chat'),
      color: 'bg-blue-100 text-blue-600',
    },
    {
      icon: Calendar,
      title: 'View Schedule',
      description: 'Check your upcoming appointments and tasks',
      action: () => navigate('/dashboard/calendar'),
      color: 'bg-green-100 text-green-600',
    },
    {
      icon: FileText,
      title: 'My Notes',
      description: 'Access your saved notes and documents',
      action: () => navigate('/dashboard/notes'),
      color: 'bg-purple-100 text-purple-600',
    },
    {
      icon: Link,
      title: 'Integrations',
      description: 'Manage your OAuth connections',
      action: () => navigate('/dashboard/integrations'),
      color: 'bg-orange-100 text-orange-600',
    },
    {
      icon: Key,
      title: 'OAuth Settings',
      description: 'Advanced OAuth management and analytics',
      action: () => navigate('/dashboard/oauth-settings'),
      color: 'bg-indigo-100 text-indigo-600',
    },
    {
      icon: Settings,
      title: 'Settings',
      description: 'Manage your account preferences',
      action: () => navigate('/dashboard/settings'),
      color: 'bg-gray-100 text-gray-600',
    },
  ];

  const recentActivity = [
    {
      id: 1,
      type: 'login',
      message: 'Successfully logged in to your account',
      timestamp: 'Just now',
      status: 'success',
    },
    {
      id: 2,
      type: 'mfa',
      message: 'Two-factor authentication enabled',
      timestamp: '2 minutes ago',
      status: 'success',
    },
    {
      id: 3,
      type: 'profile',
      message: 'Profile information updated',
      timestamp: '1 hour ago',
      status: 'info',
    },
    {
      id: 4,
      type: 'chat',
      message: 'Started a new conversation with AI assistant',
      timestamp: '2 hours ago',
      status: 'info',
    },
  ];

  const systemStatus = [
    {
      name: 'AI Assistant',
      status: 'Online & Ready',
      icon: 'orca',
      color: 'text-green-600',
      bgColor: 'bg-green-100',
    },
    {
      name: 'SMS Service',
      status: 'Connected',
      icon: MessageSquare,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100',
    },
    {
      name: 'OAuth Integrations',
      status: `${integrations.filter(i => i.status === 'connected').length} Connected`,
      icon: Link,
      color: 'text-orange-600',
      bgColor: 'bg-orange-100',
    },
  ];

  const stats = [
    {
      name: 'Total Conversations',
      value: '24',
      change: '+12%',
      changeType: 'increase',
      icon: MessageSquare,
    },
    {
      name: 'Tasks Completed',
      value: '18',
      change: '+8%',
      changeType: 'increase',
      icon: CheckCircle,
    },
    {
      name: 'Notes Created',
      value: '32',
      change: '+15%',
      changeType: 'increase',
      icon: FileText,
    },
    {
      name: 'Time Saved',
      value: '6.5h',
      change: '+2.5h',
      changeType: 'increase',
      icon: Clock,
    },
  ];

  return (
    <div className="space-y-6">
      {/* Welcome Section */}
      <Card className="bg-gradient-to-r from-accent to-purple-600 text-white border-0">
        <div className="relative z-10">
          <h1 className="text-3xl font-bold mb-2">
            Welcome back, {user?.full_name || 'User'}! 👋
          </h1>
          <p className="text-white/90 text-lg mb-4">
            Your AI assistant is ready to help you stay organized and
            productive.
          </p>
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-green-400 rounded-full"></div>
            <span className="text-sm text-white/90">
              All systems operational
            </span>
          </div>
        </div>
      </Card>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, index) => (
          <Card key={index} className="bg-white">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">{stat.name}</p>
                <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
                <div className="flex items-center mt-1">
                  <TrendingUp className="w-4 h-4 text-green-500 mr-1" />
                  <span className="text-sm text-green-600">{stat.change}</span>
                </div>
              </div>
              <div
                className={`w-12 h-12 rounded-lg flex items-center justify-center ${stat.icon === MessageSquare ? 'bg-accent/10' : stat.icon === CheckCircle ? 'bg-green-100' : stat.icon === FileText ? 'bg-purple-100' : 'bg-gray-100'}`}
              >
                <stat.icon
                  className={`w-6 h-6 ${stat.icon === MessageSquare ? 'text-accent' : stat.icon === CheckCircle ? 'text-green-600' : stat.icon === FileText ? 'text-purple-600' : 'text-gray-600'}`}
                />
              </div>
            </div>
          </Card>
        ))}
      </div>

      {/* SMS Analytics Section */}
      <div className="space-y-4">
        <h2 className="text-xl font-semibold text-gray-900">
          SMS Analytics & Usage
        </h2>
        <SMSAnalyticsWidget
          timeRange="30d"
          showCosts={true}
          showPerformance={true}
        />
      </div>

      {/* Quick Actions Grid */}
      <div>
        <h2 className="text-xl font-semibold text-gray-900 mb-4">
          Quick Actions
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
          {quickActions.map((action, index) => (
            <div
              key={index}
              className="group cursor-pointer transform transition-all duration-200"
              onClick={action.action}
            >
              <Card className="hover:shadow-lg transition-all duration-200 group-hover:scale-105">
                <div className="text-center space-y-3">
                  <div
                    className={`w-12 h-12 ${action.color} rounded-full flex items-center justify-center mx-auto`}
                  >
                    <action.icon className="w-6 h-6" />
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
      </div>

      {/* Recent Activity and System Status */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Activity */}
        <Card className="bg-white">
          <div className="space-y-4">
            {recentActivity.map((activity, index) => (
              <div key={index} className="flex items-center space-x-3">
                <div
                  className={`w-2 h-2 rounded-full ${
                    activity.status === 'success'
                      ? 'bg-green-500'
                      : activity.status === 'error'
                        ? 'bg-red-500'
                        : 'bg-blue-500'
                  }`}
                ></div>
                <div className="flex-1">
                  <p className="text-sm text-gray-900">{activity.message}</p>
                  <p className="text-xs text-gray-500">{activity.timestamp}</p>
                </div>
              </div>
            ))}
          </div>
        </Card>

        {/* System Status */}
        <Card className="bg-white">
          <div className="space-y-4">
            {systemStatus.map((status, index) => (
              <div key={index} className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div
                    className={`w-8 h-8 ${status.bgColor} rounded-lg flex items-center justify-center`}
                  >
                    {status.icon === 'orca' ? (
                      <img
                        src="/orca3d.png"
                        alt="AI Assistant"
                        className="w-4 h-4"
                      />
                    ) : (
                      <status.icon className={`w-4 h-4 ${status.color}`} />
                    )}
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-900">
                      {status.name}
                    </p>
                    <p className="text-xs text-gray-500">{status.status}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>

      {/* Coming Soon */}
      <Card className="bg-gradient-to-r from-accent/5 to-purple-50 border-accent/20">
        <div className="text-center">
          <h3 className="text-lg font-semibold text-primary mb-2">
            🚀 More Features Coming Soon!
          </h3>
          <p className="text-gray-600 mb-4">
            We're working hard to bring you more powerful features including
            advanced chat, calendar integration, and mobile apps.
          </p>
          <div className="flex justify-center space-x-4 text-sm text-gray-500">
            <span>📱 Mobile App</span>
            <span>📅 Calendar Sync</span>
            <span>🔍 Advanced Search</span>
            <span>📊 Analytics</span>
          </div>
        </div>
      </Card>
    </div>
  );
};

export default DashboardHome;
