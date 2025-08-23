import { describe, it, expect, vi } from 'vitest';
import { useOAuthStore } from '../oauthStore';

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
};
Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
});

// Mock window.location
Object.defineProperty(window, 'location', {
  value: {
    href: 'http://localhost:3000',
    origin: 'http://localhost:3000',
  },
  writable: true,
});

describe('OAuth Store', () => {
  it('should have the correct initial state structure', () => {
    // Test that the store can be accessed without errors
    expect(useOAuthStore).toBeDefined();
  });

  it('should have all required methods', () => {
    // Test that the store has all the required methods
    const store = useOAuthStore.getState();

    expect(store.connectIntegration).toBeDefined();
    expect(store.disconnectIntegration).toBeDefined();
    expect(store.refreshTokens).toBeDefined();
    expect(store.updateScopes).toBeDefined();
    expect(store.setLoading).toBeDefined();
    expect(store.setError).toBeDefined();
    expect(store.setIntegrations).toBeDefined();
    expect(store.setActiveIntegrations).toBeDefined();
    expect(store.setScopes).toBeDefined();
    expect(store.setProviders).toBeDefined();
    expect(store.getIntegration).toBeDefined();
    expect(store.isConnected).toBeDefined();
    expect(store.getProviderConfig).toBeDefined();
    expect(store.loadMockData).toBeDefined();
  });

  it('should have the correct initial state values', () => {
    const store = useOAuthStore.getState();

    expect(store.integrations).toEqual([]);
    expect(store.isLoading).toBe(false);
    expect(store.error).toBeNull();
    expect(store.activeIntegrations).toEqual([]);
    expect(store.scopes).toEqual({});
    expect(store.providers).toHaveLength(4); // Google, Microsoft, Notion, YouTube
  });

  it('should have provider configurations', () => {
    const store = useOAuthStore.getState();

    const googleProvider = store.providers.find(p => p.id === 'google');
    expect(googleProvider).toBeDefined();
    expect(googleProvider?.name).toBe('Google');
    expect(googleProvider?.color).toBe('#4285F4');

    const microsoftProvider = store.providers.find(p => p.id === 'microsoft');
    expect(microsoftProvider).toBeDefined();
    expect(microsoftProvider?.name).toBe('Microsoft');
    expect(microsoftProvider?.color).toBe('#0078D4');

    const notionProvider = store.providers.find(p => p.id === 'notion');
    expect(notionProvider).toBeDefined();
    expect(notionProvider?.name).toBe('Notion');
    expect(notionProvider?.color).toBe('#000000');

    const youtubeProvider = store.providers.find(p => p.id === 'youtube');
    expect(youtubeProvider).toBeDefined();
    expect(youtubeProvider?.name).toBe('YouTube');
    expect(youtubeProvider?.color).toBe('#FF0000');
  });

  it('should have OAuth scopes defined', () => {
    const store = useOAuthStore.getState();

    // Test that scopes are defined for each provider
    const googleProvider = store.providers.find(p => p.id === 'google');
    expect(googleProvider?.availableScopes).toBeDefined();
    expect(googleProvider?.availableScopes.length).toBeGreaterThan(0);

    const microsoftProvider = store.providers.find(p => p.id === 'microsoft');
    expect(microsoftProvider?.availableScopes).toBeDefined();
    expect(microsoftProvider?.availableScopes.length).toBeGreaterThan(0);

    const notionProvider = store.providers.find(p => p.id === 'notion');
    expect(notionProvider?.availableScopes).toBeDefined();
    expect(notionProvider?.availableScopes.length).toBeGreaterThan(0);

    const youtubeProvider = store.providers.find(p => p.id === 'youtube');
    expect(youtubeProvider?.availableScopes).toBeDefined();
    expect(youtubeProvider?.availableScopes.length).toBeGreaterThan(0);
  });

  it('should have provider features defined', () => {
    const store = useOAuthStore.getState();

    // Test that features are defined for each provider
    const googleProvider = store.providers.find(p => p.id === 'google');
    expect(googleProvider?.features).toBeDefined();
    expect(googleProvider?.features.length).toBeGreaterThan(0);

    const microsoftProvider = store.providers.find(p => p.id === 'microsoft');
    expect(microsoftProvider?.features).toBeDefined();
    expect(microsoftProvider?.features.length).toBeGreaterThan(0);

    const notionProvider = store.providers.find(p => p.id === 'notion');
    expect(notionProvider?.features).toBeDefined();
    expect(notionProvider?.features.length).toBeGreaterThan(0);

    const youtubeProvider = store.providers.find(p => p.id === 'youtube');
    expect(youtubeProvider?.features).toBeDefined();
    expect(youtubeProvider?.features.length).toBeGreaterThan(0);
  });

  it('should have provider descriptions', () => {
    const store = useOAuthStore.getState();

    // Test that descriptions are defined for each provider
    const googleProvider = store.providers.find(p => p.id === 'google');
    expect(googleProvider?.description).toBeDefined();
    expect(googleProvider?.description.length).toBeGreaterThan(0);

    const microsoftProvider = store.providers.find(p => p.id === 'microsoft');
    expect(microsoftProvider?.description).toBeDefined();
    expect(microsoftProvider?.description.length).toBeGreaterThan(0);

    const notionProvider = store.providers.find(p => p.id === 'notion');
    expect(notionProvider?.description).toBeDefined();
    expect(notionProvider?.description.length).toBeGreaterThan(0);

    const youtubeProvider = store.providers.find(p => p.id === 'youtube');
    expect(youtubeProvider?.description).toBeDefined();
    expect(youtubeProvider?.description.length).toBeGreaterThan(0);
  });

  it('should have provider auth URLs', () => {
    const store = useOAuthStore.getState();

    // Test that auth URLs are defined for each provider
    const googleProvider = store.providers.find(p => p.id === 'google');
    expect(googleProvider?.authUrl).toBeDefined();
    expect(googleProvider?.authUrl.length).toBeGreaterThan(0);

    const microsoftProvider = store.providers.find(p => p.id === 'microsoft');
    expect(microsoftProvider?.authUrl).toBeDefined();
    expect(microsoftProvider?.authUrl.length).toBeGreaterThan(0);

    const notionProvider = store.providers.find(p => p.id === 'notion');
    expect(notionProvider?.authUrl).toBeDefined();
    expect(notionProvider?.authUrl.length).toBeGreaterThan(0);

    const youtubeProvider = store.providers.find(p => p.id === 'youtube');
    expect(youtubeProvider?.authUrl).toBeDefined();
    expect(youtubeProvider?.authUrl.length).toBeGreaterThan(0);
  });

  it('should have provider redirect URIs', () => {
    const store = useOAuthStore.getState();

    // Test that redirect URIs are defined for each provider
    const googleProvider = store.providers.find(p => p.id === 'google');
    expect(googleProvider?.redirectUri).toBeDefined();
    expect(googleProvider?.redirectUri).toContain('/oauth/callback/google');

    const microsoftProvider = store.providers.find(p => p.id === 'microsoft');
    expect(microsoftProvider?.redirectUri).toBeDefined();
    expect(microsoftProvider?.redirectUri).toContain(
      '/oauth/callback/microsoft'
    );

    const notionProvider = store.providers.find(p => p.id === 'notion');
    expect(notionProvider?.redirectUri).toBeDefined();
    expect(notionProvider?.redirectUri).toContain('/oauth/callback/notion');

    const youtubeProvider = store.providers.find(p => p.id === 'youtube');
    expect(youtubeProvider?.redirectUri).toBeDefined();
    expect(youtubeProvider?.redirectUri).toContain('/oauth/callback/youtube');
  });
});
