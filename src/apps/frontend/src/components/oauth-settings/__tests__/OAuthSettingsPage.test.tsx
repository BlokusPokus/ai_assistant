import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { OAuthSettingsPage } from '../OAuthSettingsPage';

// Mock the stores
vi.mock('../../../stores/oauthSettingsStore', () => ({
  useOAuthSettingsStore: vi.fn(() => ({
    loadSettings: vi.fn(),
    loadIntegrations: vi.fn(),
    loadAnalytics: vi.fn(),
    loadAuditLogs: vi.fn(),
    loading: false,
    error: null,
    integrations: [],
  })),
}));

vi.mock('../../../stores/authStore', () => ({
  useAuthStore: vi.fn(() => ({
    user: null,
  })),
}));

vi.mock('../../../utils/roleUtils', () => ({
  isPremium: vi.fn(() => false),
  isAdmin: vi.fn(() => false),
}));

describe('OAuthSettingsPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders OAuth settings page', () => {
    render(<OAuthSettingsPage />);
    expect(screen.getByText('OAuth Settings & Management')).toBeInTheDocument();
  });

  it('renders basic tabs for non-authenticated user', () => {
    render(<OAuthSettingsPage />);
    expect(screen.getByText('Integrations')).toBeInTheDocument();
    expect(screen.getByText('Settings')).toBeInTheDocument();
  });

  it('shows page description', () => {
    render(<OAuthSettingsPage />);
    expect(
      screen.getByText(/Manage your OAuth integrations/)
    ).toBeInTheDocument();
  });

  describe('Role-based tab visibility', () => {
    it('shows all tabs for admin user', () => {
      // Mock admin user
      const { useAuthStore } = require('../../../stores/authStore');
      const { isAdmin, isPremium } = require('../../../utils/roleUtils');

      useAuthStore.mockReturnValue({
        user: { id: 1, roles: [{ name: 'administrator' }] },
      });
      isAdmin.mockReturnValue(true);
      isPremium.mockReturnValue(true);

      render(<OAuthSettingsPage />);
      expect(screen.getByText('Integrations')).toBeInTheDocument();
      expect(screen.getByText('Analytics')).toBeInTheDocument();
      expect(screen.getByText('Audit Logs')).toBeInTheDocument();
      expect(screen.getByText('Settings')).toBeInTheDocument();
    });

    it('shows premium tabs for premium user', () => {
      // Mock premium user
      const { useAuthStore } = require('../../../stores/authStore');
      const { isAdmin, isPremium } = require('../../../utils/roleUtils');

      useAuthStore.mockReturnValue({
        user: { id: 1, roles: [{ name: 'premium' }] },
      });
      isAdmin.mockReturnValue(false);
      isPremium.mockReturnValue(true);

      render(<OAuthSettingsPage />);
      expect(screen.getByText('Integrations')).toBeInTheDocument();
      expect(screen.getByText('Analytics')).toBeInTheDocument();
      expect(screen.getByText('Settings')).toBeInTheDocument();
      // Audit Logs should not be visible for premium users
      expect(screen.queryByText('Audit Logs')).not.toBeInTheDocument();
    });

    it('shows only basic tabs for regular user', () => {
      // Mock regular user
      const { useAuthStore } = require('../../../stores/authStore');
      const { isAdmin, isPremium } = require('../../../utils/roleUtils');

      useAuthStore.mockReturnValue({
        user: { id: 1, roles: [{ name: 'user' }] },
      });
      isAdmin.mockReturnValue(false);
      isPremium.mockReturnValue(false);

      render(<OAuthSettingsPage />);
      expect(screen.getByText('Integrations')).toBeInTheDocument();
      expect(screen.getByText('Settings')).toBeInTheDocument();
      // Analytics and Audit Logs should not be visible for regular users
      expect(screen.queryByText('Analytics')).not.toBeInTheDocument();
      expect(screen.queryByText('Audit Logs')).not.toBeInTheDocument();
    });
  });
});
