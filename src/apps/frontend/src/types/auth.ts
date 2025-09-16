// Authentication-related types
export interface LoginFormData {
  email: string;
  password: string;
}

export interface RegisterFormData {
  email: string;
  password: string;
  confirmPassword: string;
  fullName: string;
  phoneNumber: string; // Required field
}

export interface MFAFormData {
  code: string;
}

export interface AuthValidationErrors {
  email?: string;
  password?: string;
  confirmPassword?: string;
  fullName?: string;
  code?: string;
  general?: string;
}

// Form validation rules
export interface ValidationRule {
  required?: boolean;
  minLength?: number;
  maxLength?: number;
  pattern?: RegExp;
  message: string;
}

export interface ValidationRules {
  email: ValidationRule[];
  password: ValidationRule[];
  fullName: ValidationRule[];
  mfaCode: ValidationRule[];
}

// MFA setup types
export interface MFASetupData {
  qrCode?: string;
  backupCodes: string[];
  secretKey: string;
  mfaType: 'totp' | 'sms';
}

// Authentication flow states
export type AuthFlowState =
  | 'landing'
  | 'login'
  | 'register'
  | 'mfa-setup'
  | 'mfa-verify'
  | 'dashboard';

// User session data
export interface UserSession {
  user: {
    id: number;
    email: string;
    full_name: string;
    is_active: boolean;
    created_at: string;
    updated_at: string;
  };
  permissions: string[];
  roles: string[];
  lastActivity: string;
}
