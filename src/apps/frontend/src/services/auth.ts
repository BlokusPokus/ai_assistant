import api from './api';
import type { User, ApiResponse } from '@/types';

// Authentication request interfaces
export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name: string;
  phone_number: string; // Required field
}

export interface MFASetupRequest {
  user_id: number;
  mfa_type: 'totp' | 'sms';
}

export interface MFAVerifyRequest {
  user_id: number;
  mfa_code: string;
  mfa_type: 'totp' | 'sms';
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  user: User;
  mfa_required: boolean;
  mfa_setup_required: boolean;
}

export interface MFASetupResponse {
  qr_code?: string;
  backup_codes: string[];
  secret_key: string;
}

class AuthService {
  // Login user
  async login(credentials: LoginRequest): Promise<AuthResponse> {
    const response = await api.post<AuthResponse>('/auth/login', credentials);
    return response.data;
  }

  // Register new user
  async register(userData: RegisterRequest): Promise<User> {
    const response = await api.post<User>('/auth/register', userData);
    return response.data;
  }

  // Logout user
  async logout(): Promise<void> {
    try {
      await api.post('/auth/logout');
    } catch {
      // Even if logout fails, clear local storage
      console.warn('Logout API call failed, clearing local storage anyway');
    } finally {
      // Always clear local storage
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user');
    }
  }

  // Setup MFA
  async setupMFA(mfaData: MFASetupRequest): Promise<MFASetupResponse> {
    const response = await api.post<ApiResponse<MFASetupResponse>>(
      '/auth/mfa/setup',
      mfaData
    );
    return response.data.data;
  }

  // Verify MFA
  async verifyMFA(mfaData: MFAVerifyRequest): Promise<{ success: boolean }> {
    const response = await api.post<ApiResponse<{ success: boolean }>>(
      '/auth/mfa/verify',
      mfaData
    );
    return response.data.data;
  }

  // Get current user profile
  async getCurrentUser(): Promise<User> {
    const response = await api.get<ApiResponse<User>>('/users/me');
    return response.data.data;
  }

  // Get current user with roles and permissions
  async getCurrentUserWithRoles(): Promise<User> {
    const response = await api.get<User>('/users/me/roles');
    return response.data;
  }

  // Update user profile
  async updateProfile(userData: Partial<User>): Promise<User> {
    const response = await api.put<ApiResponse<User>>('/users/me', userData);
    return response.data.data;
  }

  // Check if user is authenticated
  isAuthenticated(): boolean {
    const token = localStorage.getItem('access_token');
    return !!token;
  }

  // Get stored user data
  getStoredUser(): User | null {
    const userStr = localStorage.getItem('user');
    if (userStr) {
      try {
        return JSON.parse(userStr);
      } catch {
        return null;
      }
    }
    return null;
  }

  // Store authentication data
  storeAuthData(authData: AuthResponse): void {
    localStorage.setItem('access_token', authData.access_token);
    localStorage.setItem('refresh_token', authData.refresh_token);
    localStorage.setItem('user', JSON.stringify(authData.user));
  }
}

export default new AuthService();
