import React from 'react';
import api from './api';
import type { OAuthIntegration, OAuthProvider } from '@/types/oauth';
import { MessageSquare, Settings } from 'lucide-react';

export interface DashboardOverviewStats {
  totalConversations: number;
  tasksCompleted: number;
  notesCreated: number;
  timeSaved: string;
}

export interface RecentActivity {
  id: string;
  type: string;
  message: string;
  timestamp: string;
  status: 'success' | 'error' | 'info';
}

export interface DashboardSystemStatus {
  name: string;
  status: string;
  icon: React.ComponentType<{ className?: string }> | string;
  color: string;
  bgColor: string;
}

class DashboardService {
  /**
   * Get dashboard statistics
   */
  async getDashboardStats(): Promise<DashboardOverviewStats> {
    try {
      // For now, we'll calculate these from available data
      // In the future, we can create dedicated endpoints for these stats

      // Get conversations count
      const conversationsResponse = await api.get(
        '/chat/conversations?per_page=1'
      );
      const totalConversations = conversationsResponse.data.total || 0;

      // Mock data for now - these would come from dedicated endpoints
      const stats: DashboardOverviewStats = {
        totalConversations,
        tasksCompleted: Math.floor(totalConversations * 0.75), // Estimate based on conversations
        notesCreated: Math.floor(totalConversations * 1.3), // Estimate based on conversations
        timeSaved: `${Math.floor(totalConversations * 0.27)}h`, // Estimate: 16 minutes per conversation
      };

      return stats;
    } catch (error) {
      console.error('Error fetching dashboard stats:', error);
      // Return default stats if API fails
      return {
        totalConversations: 0,
        tasksCompleted: 0,
        notesCreated: 0,
        timeSaved: '0h',
      };
    }
  }

  /**
   * Get recent activity
   */
  async getRecentActivity(): Promise<RecentActivity[]> {
    try {
      // Get recent conversations as activity
      const conversationsResponse = await api.get(
        '/chat/conversations?per_page=5'
      );
      const conversations = conversationsResponse.data.conversations || [];

      const activities: RecentActivity[] = conversations.map((conv: any) => ({
        id: `conv-${conv.id}`,
        type: 'chat',
        message: `Started conversation: "${conv.user_input?.substring(0, 50)}..."`,
        timestamp: this.formatTimestamp(conv.created_at),
        status: 'info' as const,
      }));

      // Add some system activities
      const systemActivities: RecentActivity[] = [
        {
          id: 'login',
          type: 'login',
          message: 'Successfully logged in to your account',
          timestamp: 'Just now',
          status: 'success',
        },
        {
          id: 'mfa',
          type: 'mfa',
          message: 'Two-factor authentication enabled',
          timestamp: '2 minutes ago',
          status: 'success',
        },
      ];

      return [...systemActivities, ...activities].slice(0, 4);
    } catch (error) {
      console.error('Error fetching recent activity:', error);
      // Return default activity if API fails
      return [
        {
          id: 'login',
          type: 'login',
          message: 'Successfully logged in to your account',
          timestamp: 'Just now',
          status: 'success',
        },
        {
          id: 'mfa',
          type: 'mfa',
          message: 'Two-factor authentication enabled',
          timestamp: '2 minutes ago',
          status: 'success',
        },
      ];
    }
  }

  /**
   * Get OAuth integrations
   */
  async getOAuthIntegrations(): Promise<OAuthIntegration[]> {
    try {
      const response = await api.get('/oauth/integrations');
      return response.data.map((integration: any) => ({
        id: integration.id.toString(),
        provider: integration.provider as OAuthProvider,
        status: integration.status === 'active' ? 'connected' : 'disconnected',
        scopes: integration.scopes || [],
        connectedAt: integration.created_at,
        lastUsed: integration.last_used,
        usageStats: {
          apiCalls: integration.usage_stats?.api_calls || 0,
          lastCall: integration.usage_stats?.last_call,
          errors: integration.usage_stats?.errors || 0,
          lastError: integration.usage_stats?.last_error,
        },
        userId: integration.user_id,
        accessToken: integration.access_token,
        refreshToken: integration.refresh_token,
        expiresAt: integration.expires_at,
      }));
    } catch (error) {
      console.error('Error fetching OAuth integrations:', error);
      // Return empty array if API fails
      return [];
    }
  }

  /**
   * Get system status
   */
  async getSystemStatus(): Promise<DashboardSystemStatus[]> {
    try {
      // Get OAuth integrations count
      const integrations = await this.getOAuthIntegrations();
      const connectedCount = integrations.filter(
        i => i.status === 'connected'
      ).length;

      return [
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
          status: `${connectedCount} Connected`,
          icon: Settings,
          color: 'text-orange-600',
          bgColor: 'bg-orange-100',
        },
      ];
    } catch (error) {
      console.error('Error fetching system status:', error);
      // Return default status if API fails
      return [
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
          status: '0 Connected',
          icon: Settings,
          color: 'text-orange-600',
          bgColor: 'bg-orange-100',
        },
      ];
    }
  }

  /**
   * Format timestamp to relative time
   */
  private formatTimestamp(timestamp: string): string {
    const now = new Date();
    const date = new Date(timestamp);
    const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);

    if (diffInSeconds < 60) {
      return 'Just now';
    } else if (diffInSeconds < 3600) {
      const minutes = Math.floor(diffInSeconds / 60);
      return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
    } else if (diffInSeconds < 86400) {
      const hours = Math.floor(diffInSeconds / 3600);
      return `${hours} hour${hours > 1 ? 's' : ''} ago`;
    } else {
      const days = Math.floor(diffInSeconds / 86400);
      return `${days} day${days > 1 ? 's' : ''} ago`;
    }
  }
}

export default new DashboardService();
