import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { User } from '@/types';
import type { LoginRequest, RegisterRequest } from '@/services/auth';
import authService from '@/services/auth';

interface AuthState {
  // State
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  mfaRequired: boolean;
  mfaSetupRequired: boolean;

  // Actions
  login: (credentials: LoginRequest) => Promise<boolean>;
  register: (userData: RegisterRequest) => Promise<boolean>;
  logout: () => Promise<void>;
  checkAuth: () => Promise<void>;
  clearError: () => void;
  setMFARequired: (required: boolean) => void;
  setMFASetupRequired: (required: boolean) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    set => ({
      // Initial state
      user: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,
      mfaRequired: false,
      mfaSetupRequired: false,

      // Login action
      login: async (credentials: LoginRequest): Promise<boolean> => {
        set({ isLoading: true, error: null });

        try {
          const authData = await authService.login(credentials);

          // Store authentication data
          authService.storeAuthData(authData);

          // Fetch user with roles and permissions
          try {
            const userWithRoles = await authService.getCurrentUserWithRoles();
            set({
              user: userWithRoles,
              isAuthenticated: true,
              isLoading: false,
              mfaRequired: authData.mfa_required,
              mfaSetupRequired: authData.mfa_setup_required,
              error: null,
            });
          } catch {
            // If roles fetch fails, use basic user data
            set({
              user: authData.user,
              isAuthenticated: true,
              isLoading: false,
              mfaRequired: authData.mfa_required,
              mfaSetupRequired: authData.mfa_setup_required,
              error: null,
            });
          }

          return true;
        } catch (err: unknown) {
          const error = err as { response?: { data?: { detail?: string } } };
          const errorMessage = error.response?.data?.detail || 'Login failed';
          set({
            isLoading: false,
            error: errorMessage,
            isAuthenticated: false,
            user: null,
          });
          return false;
        }
      },

      // Register action
      register: async (userData: RegisterRequest): Promise<boolean> => {
        set({ isLoading: true, error: null });

        try {
          await authService.register(userData);
          // Registration successful - don't automatically log in
          // User needs to log in separately with their credentials
          set({
            isLoading: false,
            error: null,
            // Don't set isAuthenticated or user - user needs to log in
          });

          return true;
        } catch (err: unknown) {
          const error = err as { response?: { data?: { detail?: string } } };
          const errorMessage =
            error.response?.data?.detail || 'Registration failed';
          set({
            isLoading: false,
            error: errorMessage,
            isAuthenticated: false,
            user: null,
          });
          return false;
        }
      },

      // Logout action
      logout: async (): Promise<void> => {
        set({ isLoading: true });

        try {
          await authService.logout();
        } catch {
          console.warn('Logout error occurred');
        } finally {
          // Always clear state regardless of API call success
          set({
            user: null,
            isAuthenticated: false,
            isLoading: false,
            error: null,
            mfaRequired: false,
            mfaSetupRequired: false,
          });
        }
      },

      // Check authentication status
      checkAuth: async (): Promise<void> => {
        // Check if we have stored auth data
        if (!authService.isAuthenticated()) {
          set({
            isAuthenticated: false,
            user: null,
            mfaRequired: false,
            mfaSetupRequired: false,
          });
          return;
        }

        // Try to get current user with roles from API
        try {
          const userWithRoles = await authService.getCurrentUserWithRoles();
          set({
            user: userWithRoles,
            isAuthenticated: true,
            mfaRequired: false,
            mfaSetupRequired: false,
          });
        } catch {
          // If roles fetch fails, try basic user data
          try {
            const user = await authService.getCurrentUser();
            set({
              user,
              isAuthenticated: true,
              mfaRequired: false,
              mfaSetupRequired: false,
            });
          } catch {
            // If API call fails, clear auth state
            set({
              user: null,
              isAuthenticated: false,
              mfaRequired: false,
              mfaSetupRequired: false,
            });
            // Clear invalid tokens
            authService.logout();
          }
        }
      },

      // Clear error
      clearError: () => set({ error: null }),

      // Set MFA required
      setMFARequired: (required: boolean) => set({ mfaRequired: required }),

      // Set MFA setup required
      setMFASetupRequired: (required: boolean) =>
        set({ mfaSetupRequired: required }),
    }),
    {
      name: 'auth-storage',
      partialize: state => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
        mfaRequired: state.mfaRequired,
        mfaSetupRequired: state.mfaSetupRequired,
      }),
    }
  )
);
