import { create } from 'zustand';

interface DashboardState {
  // Navigation state
  isSidebarCollapsed: boolean;
  isMobileMenuOpen: boolean;

  // Dashboard data
  dashboardStats: {
    totalConversations: number;
    tasksCompleted: number;
    notesCreated: number;
    timeSaved: string;
  };

  // User preferences
  dashboardPreferences: {
    showQuickActions: boolean;
    showRecentActivity: boolean;
    showSystemStatus: boolean;
    defaultView: 'overview' | 'chat' | 'calendar' | 'notes';
  };

  // Loading states
  isLoading: boolean;
  error: string | null;

  // Actions
  toggleSidebar: () => void;
  setMobileMenuOpen: (open: boolean) => void;
  updateDashboardStats: (
    stats: Partial<DashboardState['dashboardStats']>
  ) => void;
  updatePreferences: (
    prefs: Partial<DashboardState['dashboardPreferences']>
  ) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  reset: () => void;
}

export const useDashboardStore = create<DashboardState>(set => ({
  // Initial state
  isSidebarCollapsed: false,
  isMobileMenuOpen: false,

  dashboardStats: {
    totalConversations: 24,
    tasksCompleted: 18,
    notesCreated: 32,
    timeSaved: '6.5h',
  },

  dashboardPreferences: {
    showQuickActions: true,
    showRecentActivity: true,
    showSystemStatus: true,
    defaultView: 'overview',
  },

  isLoading: false,
  error: null,

  // Actions
  toggleSidebar: () =>
    set(state => ({
      isSidebarCollapsed: !state.isSidebarCollapsed,
    })),

  setMobileMenuOpen: (open: boolean) => set({ isMobileMenuOpen: open }),

  updateDashboardStats: stats =>
    set(state => ({
      dashboardStats: { ...state.dashboardStats, ...stats },
    })),

  updatePreferences: prefs =>
    set(state => ({
      dashboardPreferences: { ...state.dashboardPreferences, ...prefs },
    })),

  setLoading: (loading: boolean) => set({ isLoading: loading }),

  setError: (error: string | null) => set({ error }),

  reset: () =>
    set({
      isSidebarCollapsed: false,
      isMobileMenuOpen: false,
      isLoading: false,
      error: null,
    }),
}));
