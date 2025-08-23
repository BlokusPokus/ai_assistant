import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import type {
  OAuthState,
  OAuthActions,
  OAuthIntegration,
  OAuthProvider,
  OAuthProviderConfig,
} from '@/types/oauth';
import { OAUTH_PROVIDERS } from '@/constants/oauth';

// Initial state
const initialState: OAuthState = {
  integrations: [],
  isLoading: false,
  error: null,
  activeIntegrations: [],
  scopes: {},
  providers: OAUTH_PROVIDERS,
};

// OAuth store with Zustand
export const useOAuthStore = create<OAuthState & OAuthActions>()(
  devtools(
    (set, get) => ({
      ...initialState,

      // Actions
      connectIntegration: async (provider: OAuthProvider, scopes: string[]) => {
        try {
          set({ isLoading: true, error: null });

          // Generate OAuth state for CSRF protection
          const state = Math.random().toString(36).substring(2);

          // Get provider configuration
          const providerConfig = get().providers.find(p => p.id === provider);
          if (!providerConfig) {
            throw new Error(`Provider ${provider} not found`);
          }

          // Build OAuth URL
          const params = new URLSearchParams({
            client_id: providerConfig.clientId,
            redirect_uri: providerConfig.redirectUri,
            response_type: 'code',
            scope: scopes.join(' '),
            state: state,
            access_type: 'offline',
            prompt: 'consent',
          });

          const authUrl = `${providerConfig.authUrl}?${params.toString()}`;

          // Store state and scopes in localStorage for callback handling
          localStorage.setItem(`oauth_state_${provider}`, state);
          localStorage.setItem(
            `oauth_scopes_${provider}`,
            JSON.stringify(scopes)
          );

          // Redirect to OAuth provider
          window.location.href = authUrl;
        } catch (error) {
          const errorMessage =
            error instanceof Error
              ? error.message
              : 'Failed to connect integration';
          set({ error: errorMessage, isLoading: false });
          throw error;
        }
      },

      disconnectIntegration: async (provider: OAuthProvider) => {
        try {
          set({ isLoading: true, error: null });

          // Remove integration from state
          const updatedIntegrations = get().integrations.filter(
            integration => integration.provider !== provider
          );

          const updatedActiveIntegrations = get().activeIntegrations.filter(
            id => id !== provider
          );

          // Remove scopes for this provider
          const updatedScopes = { ...get().scopes };
          delete updatedScopes[provider];

          set({
            integrations: updatedIntegrations,
            activeIntegrations: updatedActiveIntegrations,
            scopes: updatedScopes,
            isLoading: false,
          });

          // TODO: Call backend API to revoke tokens
          // await oauthService.disconnectProvider(provider);
        } catch (error) {
          const errorMessage =
            error instanceof Error
              ? error.message
              : 'Failed to disconnect integration';
          set({ error: errorMessage, isLoading: false });
          throw error;
        }
      },

      refreshTokens: async (provider: OAuthProvider) => {
        try {
          set({ isLoading: true, error: null });

          // Find the integration
          const integration = get().integrations.find(
            i => i.provider === provider
          );
          if (!integration) {
            throw new Error(`Integration for ${provider} not found`);
          }

          // TODO: Call backend API to refresh tokens
          // const result = await oauthService.refreshTokens(provider);

          // Update integration with new tokens
          const updatedIntegrations = get().integrations.map(i =>
            i.provider === provider ? { ...i, status: 'connected' as const } : i
          );

          set({
            integrations: updatedIntegrations,
            isLoading: false,
          });
        } catch (error) {
          const errorMessage =
            error instanceof Error ? error.message : 'Failed to refresh tokens';
          set({ error: errorMessage, isLoading: false });
          throw error;
        }
      },

      updateScopes: async (provider: OAuthProvider, scopes: string[]) => {
        try {
          set({ isLoading: true, error: null });

          // Update scopes in state
          const updatedScopes = { ...get().scopes, [provider]: scopes };
          set({ scopes: updatedScopes });

          // TODO: Call backend API to update scopes
          // await oauthService.updateScopes(provider, scopes);

          set({ isLoading: false });
        } catch (error) {
          const errorMessage =
            error instanceof Error ? error.message : 'Failed to update scopes';
          set({ error: errorMessage, isLoading: false });
          throw error;
        }
      },

      // State setters
      setLoading: (loading: boolean) => set({ isLoading: loading }),

      setError: (error: string | null) => set({ error }),

      setIntegrations: (integrations: OAuthIntegration[]) =>
        set({ integrations }),

      setActiveIntegrations: (activeIntegrations: string[]) =>
        set({ activeIntegrations }),

      setScopes: (scopes: Record<string, string[]>) => set({ scopes }),

      setProviders: (providers: OAuthProviderConfig[]) => set({ providers }),

      // Helper methods
      getIntegration: (provider: OAuthProvider) => {
        return get().integrations.find(i => i.provider === provider);
      },

      isConnected: (provider: OAuthProvider) => {
        return get().activeIntegrations.includes(provider);
      },

      getProviderConfig: (provider: OAuthProvider) => {
        return get().providers.find(p => p.id === provider);
      },

      // Mock data for development (remove in production)
      loadMockData: () => {
        const mockIntegrations: OAuthIntegration[] = [
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

        const mockScopes: Record<string, string[]> = {
          google: ['https://www.googleapis.com/auth/calendar.readonly'],
          microsoft: [],
          notion: [],
          youtube: [],
        };

        set({
          integrations: mockIntegrations,
          activeIntegrations: ['google'],
          scopes: mockScopes,
        });
      },
    }),
    {
      name: 'oauth-store',
    }
  )
);
