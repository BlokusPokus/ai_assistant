import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import { oauthSettingsService } from '../services/oauthSettingsService';
import type {
  OAuthSettings,
  OAuthIntegrationEnhanced,
  OAuthAnalytics,
  OAuthAuditLog,
  AuditFilters,
} from '../services/oauthSettingsService';

interface OAuthSettingsStore {
  // State
  settings: OAuthSettings | null;
  integrations: OAuthIntegrationEnhanced[];
  analytics: OAuthAnalytics | null;
  auditLogs: OAuthAuditLog[];
  loading: boolean;
  error: string | null;

  // Actions
  loadSettings: () => Promise<void>;
  updateSettings: (settings: Partial<OAuthSettings>) => Promise<void>;
  loadIntegrations: (params?: {
    provider?: string;
    active_only?: boolean;
  }) => Promise<void>;
  connectIntegration: (provider: string, scopes: string[]) => Promise<void>;
  refreshIntegration: (id: number) => Promise<void>;
  revokeIntegration: (id: number, reason?: string) => Promise<void>;
  loadAnalytics: (timeRange?: string) => Promise<void>;
  loadAuditLogs: (filters?: AuditFilters) => Promise<void>;
  exportData: (
    format: 'csv' | 'json',
    filters?: AuditFilters
  ) => Promise<string>;
  clearError: () => void;
}

export const useOAuthSettingsStore = create<OAuthSettingsStore>()(
  devtools(
    (set, get) => ({
      // Initial state
      settings: null,
      integrations: [],
      analytics: null,
      auditLogs: [],
      loading: false,
      error: null,

      // Actions
      loadSettings: async () => {
        try {
          set({ loading: true, error: null });
          const settings = await oauthSettingsService.getSettings();
          set({ settings, loading: false });
        } catch (error) {
          set({
            error:
              error instanceof Error
                ? error.message
                : 'Failed to load settings',
            loading: false,
          });
        }
      },

      updateSettings: async (settings: Partial<OAuthSettings>) => {
        try {
          set({ loading: true, error: null });
          await oauthSettingsService.updateSettings(settings);

          // Update local state
          const currentSettings = get().settings;
          if (currentSettings) {
            set({
              settings: { ...currentSettings, ...settings },
              loading: false,
            });
          }
        } catch (error) {
          set({
            error:
              error instanceof Error
                ? error.message
                : 'Failed to update settings',
            loading: false,
          });
        }
      },

      loadIntegrations: async params => {
        try {
          set({ loading: true, error: null });
          const integrations =
            await oauthSettingsService.getIntegrations(params);
          set({ integrations, loading: false });
        } catch (error) {
          set({
            error:
              error instanceof Error
                ? error.message
                : 'Failed to load integrations',
            loading: false,
          });
        }
      },

      connectIntegration: async (provider: string, scopes: string[]) => {
        try {
          set({ loading: true, error: null });
          const result = await oauthSettingsService.connectIntegration(
            provider,
            scopes
          );

          // Redirect to OAuth provider's authorization URL
          window.location.href = result.authorization_url;
        } catch (error) {
          set({
            error:
              error instanceof Error
                ? error.message
                : 'Failed to connect integration',
            loading: false,
          });
        }
      },

      refreshIntegration: async (id: number) => {
        try {
          set({ loading: true, error: null });
          await oauthSettingsService.refreshTokens(id);

          // Reload integrations to get updated status
          await get().loadIntegrations();
        } catch (error) {
          set({
            error:
              error instanceof Error
                ? error.message
                : 'Failed to refresh tokens',
            loading: false,
          });
        }
      },

      revokeIntegration: async (id: number, reason?: string) => {
        try {
          set({ loading: true, error: null });
          await oauthSettingsService.revokeIntegration(id, reason);

          // Remove from local state
          const currentIntegrations = get().integrations;
          set({
            integrations: currentIntegrations.filter(
              integration => integration.id !== id
            ),
            loading: false,
          });
        } catch (error) {
          set({
            error:
              error instanceof Error
                ? error.message
                : 'Failed to revoke integration',
            loading: false,
          });
        }
      },

      loadAnalytics: async (_timeRange = '7d') => {
        try {
          set({ loading: true, error: null });
          const analytics = await oauthSettingsService.getAnalytics();
          set({ analytics, loading: false });
        } catch (error) {
          set({
            error:
              error instanceof Error
                ? error.message
                : 'Failed to load analytics',
            loading: false,
          });
        }
      },

      loadAuditLogs: async (_filters = {}) => {
        try {
          set({ loading: true, error: null });
          const auditLogs = await oauthSettingsService.getAuditLogs();
          set({ auditLogs, loading: false });
        } catch (error) {
          set({
            error:
              error instanceof Error
                ? error.message
                : 'Failed to load audit logs',
            loading: false,
          });
        }
      },

      exportData: async (format: 'csv' | 'json', filters?: AuditFilters) => {
        try {
          set({ loading: true, error: null });
          const data = await oauthSettingsService.exportData(format, filters);
          set({ loading: false });
          return data;
        } catch (error) {
          set({
            error:
              error instanceof Error ? error.message : 'Failed to export data',
            loading: false,
          });
          throw error;
        }
      },

      clearError: () => set({ error: null }),
    }),
    {
      name: 'oauth-settings-store',
    }
  )
);
