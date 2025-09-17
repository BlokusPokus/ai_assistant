import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import dashboardService from '@/services/dashboardService';
import type {
  DashboardOverviewStats,
  RecentActivity,
  DashboardSystemStatus,
} from '@/services/dashboardService';
import type { OAuthIntegration } from '@/types/oauth';

interface DashboardDataState {
  // State
  stats: DashboardOverviewStats | null;
  recentActivity: RecentActivity[];
  systemStatus: DashboardSystemStatus[];
  oauthIntegrations: OAuthIntegration[];
  isLoading: boolean;
  error: string | null;
  lastUpdated: string | null;

  // Actions
  loadDashboardData: () => Promise<void>;
  refreshStats: () => Promise<void>;
  refreshActivity: () => Promise<void>;
  refreshSystemStatus: () => Promise<void>;
  refreshOAuthIntegrations: () => Promise<void>;
  clearError: () => void;
  reset: () => void;
}

export const useDashboardDataStore = create<DashboardDataState>()(
  devtools(
    (set, get) => ({
      // Initial state
      stats: null,
      recentActivity: [],
      systemStatus: [],
      oauthIntegrations: [],
      isLoading: false,
      error: null,
      lastUpdated: null,

      // Load all dashboard data
      loadDashboardData: async () => {
        set({ isLoading: true, error: null });

        try {
          const [stats, activity, systemStatus, integrations] =
            await Promise.all([
              dashboardService.getDashboardStats(),
              dashboardService.getRecentActivity(),
              dashboardService.getSystemStatus(),
              dashboardService.getOAuthIntegrations(),
            ]);

          set({
            stats,
            recentActivity: activity,
            systemStatus,
            oauthIntegrations: integrations,
            isLoading: false,
            lastUpdated: new Date().toISOString(),
          });
        } catch (error) {
          const errorMessage =
            error instanceof Error
              ? error.message
              : 'Failed to load dashboard data';
          set({
            error: errorMessage,
            isLoading: false,
          });
        }
      },

      // Refresh stats only
      refreshStats: async () => {
        try {
          const stats = await dashboardService.getDashboardStats();
          set({ stats });
        } catch (error) {
          const errorMessage =
            error instanceof Error ? error.message : 'Failed to refresh stats';
          set({ error: errorMessage });
        }
      },

      // Refresh activity only
      refreshActivity: async () => {
        try {
          const activity = await dashboardService.getRecentActivity();
          set({ recentActivity: activity });
        } catch (error) {
          const errorMessage =
            error instanceof Error
              ? error.message
              : 'Failed to refresh activity';
          set({ error: errorMessage });
        }
      },

      // Refresh system status only
      refreshSystemStatus: async () => {
        try {
          const systemStatus = await dashboardService.getSystemStatus();
          set({ systemStatus });
        } catch (error) {
          const errorMessage =
            error instanceof Error
              ? error.message
              : 'Failed to refresh system status';
          set({ error: errorMessage });
        }
      },

      // Refresh OAuth integrations only
      refreshOAuthIntegrations: async () => {
        try {
          const integrations = await dashboardService.getOAuthIntegrations();
          set({ oauthIntegrations: integrations });
        } catch (error) {
          const errorMessage =
            error instanceof Error
              ? error.message
              : 'Failed to refresh OAuth integrations';
          set({ error: errorMessage });
        }
      },

      // Clear error
      clearError: () => set({ error: null }),

      // Reset store
      reset: () =>
        set({
          stats: null,
          recentActivity: [],
          systemStatus: [],
          oauthIntegrations: [],
          isLoading: false,
          error: null,
          lastUpdated: null,
        }),
    }),
    {
      name: 'dashboard-data-store',
    }
  )
);
