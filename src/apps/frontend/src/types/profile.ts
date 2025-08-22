// Profile and settings types
export interface UserProfile {
  id: number;
  email: string;
  full_name: string;
  phone_number?: string;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  updated_at: string;
}

export interface UserProfileUpdateRequest {
  full_name?: string;
  phone_number?: string;
}

export interface UserPreferences {
  user_id: number;
  preferences: Record<string, any>;
  settings: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface UserPreferencesUpdateRequest {
  preferences?: Record<string, any>;
  settings?: Record<string, any>;
}

export interface SecuritySettings {
  mfa_enabled: boolean;
  mfa_method: 'totp' | 'sms' | 'both';
  backup_codes_generated: boolean;
  last_password_change?: string;
  session_timeout: number; // in minutes
}

export interface PasswordChangeRequest {
  current_password: string;
  new_password: string;
  confirm_password: string;
}

export interface MFASetupRequest {
  method: 'totp' | 'sms';
  phone_number?: string;
}

export interface MFAVerificationRequest {
  code: string;
  method: 'totp' | 'sms';
}
