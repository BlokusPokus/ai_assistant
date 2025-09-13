import api from './api';
import type { OAuthProviderConfig } from '@/types/oauth';

// Enhanced OAuth types for settings management
export interface OAuthSettings {
  autoRefreshTokens: boolean;
  refreshThreshold: number; // minutes before expiration
  notifications: {
    tokenExpiry: boolean;
    syncFailures: boolean;
    securityAlerts: boolean;
  };
  security: {
    requireReauthForRevoke: boolean;
    auditLogRetention: number; // days
  };
}

export interface OAuthIntegrationEnhanced {
  id: number; // Backend uses numeric IDs
  provider: string;
  display_name?: string;
  status: string;
  is_active: boolean;
  scopes: string[];
  created_at: string;
  last_sync_at?: string;
  expires_at?: string;
  metadata?: Record<string, string | number | boolean>;
}

export interface OAuthAnalytics {
  integrations: {
    total: number;
    active: number;
    expired: number;
    revoked: number;
  };
  providers: Record<
    string,
    {
      count: number;
      active: number;
      expired: number;
    }
  >;
  usage: {
    total_requests: number;
    successful_requests: number;
    failed_requests: number;
    average_response_time: number;
  };
  trends: {
    daily: Array<{ date: string; requests: number; errors: number }>;
    weekly: Array<{ week: string; integrations: number; syncs: number }>;
  };
}

export interface OAuthAuditLog {
  id: number;
  timestamp: string;
  user_id: number;
  action: string;
  provider: string;
  integration_id?: number;
  details: Record<string, string | number | boolean>;
  ip_address?: string;
  user_agent?: string;
}

export interface AuditFilters {
  dateFrom?: string;
  dateTo?: string;
  provider?: string;
  action?: string;
  user_id?: number;
}

export class OAuthSettingsService {
  // Enhanced OAuth methods using real backend APIs
  async getProviders(): Promise<OAuthProviderConfig[]> {
    try {
      const response = await api.get('/oauth/providers');
      return response.data;
    } catch (error) {
      console.error('Failed to get OAuth providers:', error);
      throw new Error('Failed to get OAuth providers');
    }
  }

  async getIntegrations(params?: {
    provider?: string;
    active_only?: boolean;
  }): Promise<OAuthIntegrationEnhanced[]> {
    try {
      const response = await api.get('/oauth/integrations', { params });
      return response.data;
    } catch (error) {
      console.error('Failed to get OAuth integrations:', error);
      throw new Error('Failed to get OAuth integrations');
    }
  }

  async refreshTokens(integrationId: number): Promise<{ message: string }> {
    try {
      const response = await api.post(
        `/oauth/integrations/${integrationId}/refresh`
      );
      return response.data;
    } catch (error: unknown) {
      console.error('Failed to refresh OAuth tokens:', error);

      // Provide helpful error messages for common issues
      if (
        error &&
        typeof error === 'object' &&
        'response' in error &&
        error.response &&
        typeof error.response === 'object' &&
        'status' in error.response &&
        error.response.status === 503 &&
        'data' in error.response &&
        error.response.data &&
        typeof error.response.data === 'object' &&
        'detail' in error.response.data &&
        typeof error.response.data.detail === 'string' &&
        error.response.data.detail.includes('OAuth credentials not configured')
      ) {
        throw new Error(
          'OAuth service is not fully configured. Please contact your administrator to set up OAuth provider credentials.'
        );
      } else if (
        error &&
        typeof error === 'object' &&
        'response' in error &&
        error.response &&
        typeof error.response === 'object' &&
        'status' in error.response &&
        error.response.status === 400
      ) {
        throw new Error(
          'Failed to refresh tokens. The integration may have expired or been revoked.'
        );
      } else if (error.response?.status === 500) {
        // Check if it's a missing refresh token issue
        if (
          error.response?.data?.detail?.includes('No refresh token available')
        ) {
          throw new Error(
            'This integration cannot be refreshed because no refresh token was stored during the initial OAuth connection. You may need to reconnect the integration.'
          );
        } else {
          throw new Error(
            'OAuth service error. Please try again later or contact support.'
          );
        }
      } else {
        throw new Error(
          'Failed to refresh OAuth tokens. Please check your connection and try again.'
        );
      }
    }
  }

  async revokeIntegration(
    integrationId: number,
    reason?: string
  ): Promise<{ message: string }> {
    try {
      const response = await api.delete(
        `/oauth/integrations/${integrationId}`,
        {
          data: { reason },
        }
      );
      return response.data;
    } catch (error) {
      console.error('Failed to revoke OAuth integration:', error);
      throw new Error('Failed to revoke OAuth integration');
    }
  }

  async getStatus(): Promise<{
    integrations: {
      total_integrations: number;
      active_integrations: number;
      pending_integrations: number;
      inactive_integrations: number;
      providers: string[];
    };
    consents: {
      total_consents: number;
      active_consents: number;
      expired_consents: number;
    };
  }> {
    try {
      const response = await api.get('/oauth/status');
      return response.data;
    } catch (error) {
      console.error('Failed to get OAuth status:', error);
      throw new Error('Failed to get OAuth status');
    }
  }

  async syncIntegrations(): Promise<{
    message: string;
    results: { success: number; failed: number; errors: string[] };
  }> {
    try {
      const response = await api.post('/oauth/integrations/sync');
      return response.data;
    } catch (error) {
      console.error('Failed to sync OAuth integrations:', error);
      throw new Error('Failed to sync OAuth integrations');
    }
  }

  // New methods for settings management
  async getSettings(): Promise<OAuthSettings> {
    // For now, return default settings
    // In the future, this could fetch from a dedicated settings endpoint
    return {
      autoRefreshTokens: true,
      refreshThreshold: 30,
      notifications: {
        tokenExpiry: true,
        syncFailures: true,
        securityAlerts: true,
      },
      security: {
        requireReauthForRevoke: true,
        auditLogRetention: 90,
      },
    };
  }

  async updateSettings(settings: Partial<OAuthSettings>): Promise<void> {
    // For now, just log the settings update
    // In the future, this could save to a settings endpoint
    console.log('Updating OAuth settings:', settings);
  }

  async getAnalytics(): Promise<OAuthAnalytics> {
    try {
      // Use existing status endpoint and enhance with time-based data
      const status = await this.getStatus();

      // Transform status data into analytics format
      // Backend returns: { integrations: { total_integrations, active_integrations, pending_integrations, inactive_integrations, providers }, consents: {...} }
      const integrations = status.integrations || {};

      return {
        integrations: {
          total: integrations.total_integrations || 0,
          active: integrations.active_integrations || 0,
          expired: integrations.inactive_integrations || 0, // Map inactive to expired for UI
          revoked: 0, // Backend doesn't track revoked separately yet
        },
        providers: integrations.providers || {},
        usage: {
          total_requests: 0, // Would come from analytics endpoint
          successful_requests: 0,
          failed_requests: 0,
          average_response_time: 0,
        },
        trends: {
          daily: [], // Would come from analytics endpoint
          weekly: [],
        },
      };
    } catch (error) {
      console.error('Failed to get OAuth analytics:', error);
      throw new Error('Failed to get OAuth analytics');
    }
  }

  async getAuditLogs(): Promise<OAuthAuditLog[]> {
    // For now, return mock audit data
    // In the future, this would come from an audit endpoint
    return [
      {
        id: 1,
        timestamp: new Date().toISOString(),
        user_id: 1,
        action: 'integration_created',
        provider: 'google',
        integration_id: 1,
        details: { scopes: ['calendar.readonly'] },
        ip_address: '192.168.1.1',
        user_agent: 'Mozilla/5.0...',
      },
      {
        id: 2,
        timestamp: new Date(Date.now() - 86400000).toISOString(), // 1 day ago
        user_id: 1,
        action: 'tokens_refreshed',
        provider: 'google',
        integration_id: 1,
        details: { scopes: ['calendar.readonly'] },
        ip_address: '192.168.1.1',
        user_agent: 'Mozilla/5.0...',
      },
      {
        id: 3,
        timestamp: new Date(Date.now() - 172800000).toISOString(), // 2 days ago
        user_id: 1,
        action: 'integration_revoked',
        provider: 'microsoft',
        integration_id: 2,
        details: { reason: 'User requested revocation' },
        ip_address: '192.168.1.1',
        user_agent: 'Mozilla/5.0...',
      },
    ];
  }

  async connectIntegration(
    provider: string,
    scopes: string[]
  ): Promise<{ authorization_url: string; state: string }> {
    try {
      const response = await api.post('/oauth/initiate', {
        provider,
        scopes,
        redirect_uri: `${window.location.origin}/oauth/callback/${provider}`,
      });
      return response.data;
    } catch (error) {
      console.error('Failed to initiate OAuth connection:', error);
      throw new Error('Failed to initiate OAuth connection');
    }
  }

  async exportData(
    format: 'csv' | 'json',
    filters?: AuditFilters
  ): Promise<string> {
    try {
      const data = await this.getAuditLogs(filters);

      if (format === 'json') {
        return JSON.stringify(data, null, 2);
      } else {
        // Simple CSV conversion
        const headers = ['ID', 'Timestamp', 'Action', 'Provider', 'Details'];
        const rows = data.map(log => [
          log.id,
          log.timestamp,
          log.action,
          log.provider,
          JSON.stringify(log.details),
        ]);

        return [headers, ...rows]
          .map(row => row.map(cell => `"${cell}"`).join(','))
          .join('\n');
      }
    } catch (error) {
      console.error('Failed to export OAuth data:', error);
      throw new Error('Failed to export OAuth data');
    }
  }
}

export const oauthSettingsService = new OAuthSettingsService();
