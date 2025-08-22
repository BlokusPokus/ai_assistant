import { create } from 'zustand';
import type { UserProfile, UserPreferences } from '@/types/profile';
import profileService from '@/services/profileService';

interface ProfileState {
  // State
  profile: UserProfile | null;
  preferences: UserPreferences | null;
  isLoading: boolean;
  error: string | null;
  isEditing: boolean;

  // Actions
  fetchProfile: () => Promise<void>;
  updateProfile: (data: Partial<UserProfile>) => Promise<boolean>;
  fetchPreferences: () => Promise<void>;
  updatePreferences: (data: Partial<UserPreferences>) => Promise<boolean>;
  setEditing: (editing: boolean) => void;
  clearError: () => void;
  reset: () => void;
}

export const useProfileStore = create<ProfileState>(set => ({
  // Initial state
  profile: null,
  preferences: null,
  isLoading: false,
  error: null,
  isEditing: false,

  // Fetch profile
  fetchProfile: async () => {
    set({ isLoading: true, error: null });
    try {
      const profile = await profileService.getCurrentProfile();
      set({ profile, isLoading: false });
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } };
      const errorMessage =
        error.response?.data?.detail || 'Failed to fetch profile';
      set({ error: errorMessage, isLoading: false });
    }
  },

  // Update profile
  updateProfile: async (data: Partial<UserProfile>): Promise<boolean> => {
    set({ isLoading: true, error: null });
    try {
      const updatedProfile = await profileService.updateProfile(data);
      set({ profile: updatedProfile, isLoading: false, isEditing: false });
      return true;
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } };
      const errorMessage =
        error.response?.data?.detail || 'Failed to update profile';
      set({ error: errorMessage, isLoading: false });
      return false;
    }
  },

  // Fetch preferences
  fetchPreferences: async () => {
    set({ isLoading: true, error: null });
    try {
      const preferences = await profileService.getPreferences();
      set({ preferences, isLoading: false });
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } };
      const errorMessage =
        error.response?.data?.detail || 'Failed to fetch preferences';
      set({ error: errorMessage, isLoading: false });
    }
  },

  // Update preferences
  updatePreferences: async (
    data: Partial<UserPreferences>
  ): Promise<boolean> => {
    set({ isLoading: true, error: null });
    try {
      const updatedPreferences = await profileService.updatePreferences(data);
      set({ preferences: updatedPreferences, isLoading: false });
      return true;
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } };
      const errorMessage =
        error.response?.data?.detail || 'Failed to update preferences';
      set({ error: errorMessage, isLoading: false });
      return false;
    }
  },

  // Set editing state
  setEditing: (editing: boolean) => set({ isEditing: editing }),

  // Clear error
  clearError: () => set({ error: null }),

  // Reset state
  reset: () =>
    set({
      profile: null,
      preferences: null,
      isLoading: false,
      error: null,
      isEditing: false,
    }),
}));
