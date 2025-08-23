// OAuth Integration types
export interface OAuthIntegration {
  id: string;
  provider: OAuthProvider;
  status: OAuthStatus;
  scopes: string[];
  connectedAt?: string;
  lastUsed?: string;
  usageStats: OAuthUsageStats;
  userId: number;
  accessToken?: string;
  refreshToken?: string;
  expiresAt?: string;
}

export type OAuthProvider = 'google' | 'microsoft' | 'notion' | 'youtube';

export type OAuthStatus =
  | 'connected'
  | 'disconnected'
  | 'pending'
  | 'error'
  | 'expired';

export interface OAuthUsageStats {
  apiCalls: number;
  lastCall?: string;
  errors: number;
  lastError?: string;
}

// OAuth Provider configuration
export interface OAuthProviderConfig {
  id: OAuthProvider;
  name: string;
  logo: string;
  description: string;
  availableScopes: OAuthScope[];
  features: string[];
  color: string;
  authUrl: string;
  clientId: string;
  redirectUri: string;
}

// OAuth Scope definition
export interface OAuthScope {
  id: string;
  name: string;
  description: string;
  required: boolean;
  category: 'read' | 'write' | 'admin';
  provider: OAuthProvider;
}

// OAuth State for Zustand store
export interface OAuthState {
  integrations: OAuthIntegration[];
  isLoading: boolean;
  error: string | null;
  activeIntegrations: string[];
  scopes: Record<string, string[]>;
  providers: OAuthProviderConfig[];
}

// OAuth Actions for Zustand store
export interface OAuthActions {
  connectIntegration: (
    provider: OAuthProvider,
    scopes: string[]
  ) => Promise<void>;
  disconnectIntegration: (provider: OAuthProvider) => Promise<void>;
  refreshTokens: (provider: OAuthProvider) => Promise<void>;
  updateScopes: (provider: OAuthProvider, scopes: string[]) => Promise<void>;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  setIntegrations: (integrations: OAuthIntegration[]) => void;
  setActiveIntegrations: (integrations: string[]) => void;
  setScopes: (scopes: Record<string, string[]>) => void;
  setProviders: (providers: OAuthProviderConfig[]) => void;
  // Helper methods
  getIntegration: (provider: OAuthProvider) => OAuthIntegration | undefined;
  isConnected: (provider: OAuthProvider) => boolean;
  getProviderConfig: (
    provider: OAuthProvider
  ) => OAuthProviderConfig | undefined;
  loadMockData: () => void;
}

// OAuth Connection Request
export interface OAuthConnectionRequest {
  provider: OAuthProvider;
  scopes: string[];
  redirectUri: string;
  state: string;
}

// OAuth Connection Response
export interface OAuthConnectionResponse {
  success: boolean;
  integration?: OAuthIntegration;
  error?: string;
  authUrl?: string;
}

// OAuth Token Refresh Request
export interface OAuthTokenRefreshRequest {
  provider: OAuthProvider;
  refreshToken: string;
}

// OAuth Token Refresh Response
export interface OAuthTokenRefreshResponse {
  success: boolean;
  accessToken?: string;
  refreshToken?: string;
  expiresAt?: string;
  error?: string;
}

// OAuth Provider Status
export interface OAuthProviderStatus {
  provider: OAuthProvider;
  isConnected: boolean;
  lastSync?: string;
  health: 'healthy' | 'warning' | 'error';
  nextSync?: string;
}

// OAuth Consent Request
export interface OAuthConsentRequest {
  provider: OAuthProvider;
  scopes: string[];
  userId: number;
}

// OAuth Consent Response
export interface OAuthConsentResponse {
  success: boolean;
  consentId?: string;
  scopes: string[];
  expiresAt?: string;
  error?: string;
}
