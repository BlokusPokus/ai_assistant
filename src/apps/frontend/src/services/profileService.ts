import api from './api';
import type {
  UserProfile,
  UserProfileUpdateRequest,
  UserPreferences,
  UserPreferencesUpdateRequest,
} from '@/types/profile';

class ProfileService {
  // Get current user profile
  async getCurrentProfile(): Promise<UserProfile> {
    const response = await api.get('/users/me');
    return response.data;
  }

  // Update current user profile
  async updateProfile(data: UserProfileUpdateRequest): Promise<UserProfile> {
    const response = await api.put('/users/me', data);
    return response.data;
  }

  // Get user preferences
  async getPreferences(): Promise<UserPreferences> {
    const response = await api.get('/users/me/preferences');
    return response.data;
  }

  // Update user preferences
  async updatePreferences(
    data: UserPreferencesUpdateRequest
  ): Promise<UserPreferences> {
    const response = await api.put('/users/me/preferences', data);
    return response.data;
  }

  // Get user settings (alias for preferences)
  async getSettings(): Promise<UserPreferences> {
    return this.getPreferences();
  }

  // Update user settings (alias for preferences)
  async updateSettings(
    data: UserPreferencesUpdateRequest
  ): Promise<UserPreferences> {
    return this.updatePreferences(data);
  }

  // Change password
  async changePassword(
    currentPassword: string,
    newPassword: string
  ): Promise<{ message: string }> {
    const response = await api.post('/users/me/change-password', {
      current_password: currentPassword,
      new_password: newPassword,
    });
    return response.data;
  }

  // Get MFA status
  async getMFAStatus(): Promise<{ mfa_enabled: boolean; mfa_method: string }> {
    const response = await api.get('/users/me/mfa-status');
    return response.data;
  }

  // Setup MFA
  async setupMFA(
    method: 'totp' | 'sms',
    phoneNumber?: string
  ): Promise<{ qr_code?: string; backup_codes?: string[] }> {
    const response = await api.post('/users/me/mfa-setup', {
      method,
      phone_number: phoneNumber,
    });
    return response.data;
  }

  // Verify MFA
  async verifyMFA(
    code: string,
    method: 'totp' | 'sms'
  ): Promise<{ success: boolean }> {
    const response = await api.post('/users/me/mfa-verify', {
      code,
      method,
    });
    return response.data;
  }
}

export default new ProfileService();
