import api from './api';
import type {
  OAuthProvider,
  OAuthIntegration,
  OAuthProviderConfig,
  OAuthConnectionRequest,
  OAuthConnectionResponse,
  OAuthTokenRefreshRequest,
  OAuthTokenRefreshResponse,
  OAuthConsentRequest,
  OAuthConsentResponse,
} from '@/types/oauth';

class OAuthService {
  private baseUrl = '/oauth';

  /**
   * Connect to an OAuth provider
   */
  async connectProvider(
    provider: OAuthProvider,
    scopes: string[]
  ): Promise<OAuthConnectionResponse> {
    try {
      const request: OAuthConnectionRequest = {
        provider,
        scopes,
        redirectUri: `${window.location.origin}/oauth/callback/${provider}`,
        state: Math.random().toString(36).substring(2),
      };

      const response = await api.post<OAuthConnectionResponse>(
        `${this.baseUrl}/connect`,
        request
      );

      return response.data;
    } catch (error) {
      console.error('Failed to connect OAuth provider:', error);
      throw new Error('Failed to connect OAuth provider');
    }
  }

  /**
   * Disconnect from an OAuth provider
   */
  async disconnectProvider(provider: OAuthProvider): Promise<void> {
    try {
      await api.post(`${this.baseUrl}/disconnect`, { provider });
    } catch (error) {
      console.error('Failed to disconnect OAuth provider:', error);
      throw new Error('Failed to disconnect OAuth provider');
    }
  }

  /**
   * Refresh OAuth tokens
   */
  async refreshTokens(
    provider: OAuthProvider,
    refreshToken: string
  ): Promise<OAuthTokenRefreshResponse> {
    try {
      const request: OAuthTokenRefreshRequest = {
        provider,
        refreshToken,
      };

      const response = await api.post<OAuthTokenRefreshResponse>(
        `${this.baseUrl}/refresh`,
        request
      );

      return response.data;
    } catch (error) {
      console.error('Failed to refresh OAuth tokens:', error);
      throw new Error('Failed to refresh OAuth tokens');
    }
  }

  /**
   * Get integration status for a provider
   */
  async getIntegrationStatus(
    provider: OAuthProvider
  ): Promise<OAuthIntegration> {
    try {
      const response = await api.get<OAuthIntegration>(
        `${this.baseUrl}/status/${provider}`
      );

      return response.data;
    } catch (error) {
      console.error('Failed to get OAuth integration status:', error);
      throw new Error('Failed to get OAuth integration status');
    }
  }

  /**
   * Get all OAuth integrations for the current user
   */
  async getIntegrations(): Promise<OAuthIntegration[]> {
    try {
      const response = await api.get<OAuthIntegration[]>(
        `${this.baseUrl}/integrations`
      );
      return response.data;
    } catch (error) {
      console.error('Failed to get OAuth integrations:', error);
      throw new Error('Failed to get OAuth integrations');
    }
  }

  /**
   * Get provider information
   */
  async getProviderInfo(provider: OAuthProvider): Promise<OAuthProviderConfig> {
    try {
      const response = await api.get<OAuthProviderConfig>(
        `${this.baseUrl}/providers/${provider}`
      );

      return response.data;
    } catch (error) {
      console.error('Failed to get OAuth provider info:', error);
      throw new Error('Failed to get OAuth provider info');
    }
  }

  /**
   * Update OAuth scopes for a provider
   */
  async updateScopes(provider: OAuthProvider, scopes: string[]): Promise<void> {
    try {
      await api.put(`${this.baseUrl}/scopes`, {
        provider,
        scopes,
      });
    } catch (error) {
      console.error('Failed to update OAuth scopes:', error);
      throw new Error('Failed to update OAuth scopes');
    }
  }

  /**
   * Get OAuth consent information
   */
  async getConsent(
    provider: OAuthProvider,
    scopes: string[]
  ): Promise<OAuthConsentResponse> {
    try {
      const request: OAuthConsentRequest = {
        provider,
        scopes,
        userId: 1, // TODO: Get from auth store
      };

      const response = await api.post<OAuthConsentResponse>(
        `${this.baseUrl}/consent`,
        request
      );

      return response.data;
    } catch (error) {
      console.error('Failed to get OAuth consent:', error);
      throw new Error('Failed to get OAuth consent');
    }
  }

  /**
   * Handle OAuth callback
   */
  async handleCallback(
    provider: OAuthProvider,
    code: string,
    state: string
  ): Promise<OAuthIntegration> {
    try {
      const response = await api.post<OAuthIntegration>(
        `${this.baseUrl}/callback`,
        {
          provider,
          code,
          state,
        }
      );

      return response.data;
    } catch (error) {
      console.error('Failed to handle OAuth callback:', error);
      throw new Error('Failed to handle OAuth callback');
    }
  }

  /**
   * Test OAuth connection
   */
  async testConnection(provider: OAuthProvider): Promise<boolean> {
    try {
      const response = await api.post(`${this.baseUrl}/test`, { provider });
      return response.data.success;
    } catch (error) {
      console.error('Failed to test OAuth connection:', error);
      return false;
    }
  }

  /**
   * Get OAuth usage statistics
   */
  async getUsageStats(provider: OAuthProvider): Promise<any> {
    try {
      const response = await api.get(`${this.baseUrl}/usage/${provider}`);
      return response.data;
    } catch (error) {
      console.error('Failed to get OAuth usage stats:', error);
      throw new Error('Failed to get OAuth usage stats');
    }
  }

  /**
   * Mock methods for development (remove in production)
   */
  async mockConnectProvider(
    provider: OAuthProvider,
    scopes: string[]
  ): Promise<OAuthConnectionResponse> {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 1000));

    // Simulate successful connection
    return {
      success: true,
      authUrl: `https://example.com/oauth/${provider}?scopes=${scopes.join(',')}`,
    };
  }

  async mockDisconnectProvider(provider: OAuthProvider): Promise<void> {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 500));

    // Simulate successful disconnection
    console.log(`Mock disconnected from ${provider}`);
  }

  async mockGetIntegrations(): Promise<OAuthIntegration[]> {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 800));

    // Return mock integrations
    return [
      {
        id: '1',
        provider: 'google',
        status: 'connected',
        scopes: ['https://www.googleapis.com/auth/calendar.readonly'],
        connectedAt: new Date().toISOString(),
        lastUsed: new Date().toISOString(),
        usageStats: {
          apiCalls: 45,
          lastCall: new Date().toISOString(),
          errors: 0,
        },
        userId: 1,
      },
      {
        id: '2',
        provider: 'microsoft',
        status: 'disconnected',
        scopes: [],
        connectedAt: undefined,
        lastUsed: undefined,
        usageStats: {
          apiCalls: 0,
          errors: 0,
        },
        userId: 1,
      },
    ];
  }
}

export default new OAuthService();
