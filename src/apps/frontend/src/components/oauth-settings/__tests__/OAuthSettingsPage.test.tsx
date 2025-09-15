// import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { OAuthSettingsPage } from '../OAuthSettingsPage';

// Mock the store
vi.mock('../../../stores/oauthSettingsStore', () => ({
  useOAuthSettingsStore: () => ({
    loadSettings: vi.fn(),
    loadIntegrations: vi.fn(),
    loadAnalytics: vi.fn(),
    loadAuditLogs: vi.fn(),
    loading: false,
    error: null,
  }),
}));

describe('OAuthSettingsPage', () => {
  it('renders OAuth settings page', () => {
    render(<OAuthSettingsPage />);
    expect(screen.getByText('OAuth Settings & Management')).toBeInTheDocument();
  });

  it('renders tab navigation', () => {
    render(<OAuthSettingsPage />);
    expect(screen.getByText('Integrations')).toBeInTheDocument();
    expect(screen.getByText('Analytics')).toBeInTheDocument();
    expect(screen.getByText('Audit Logs')).toBeInTheDocument();
    expect(screen.getByText('Settings')).toBeInTheDocument();
  });

  it('shows page description', () => {
    render(<OAuthSettingsPage />);
    expect(
      screen.getByText(/Manage your OAuth integrations/)
    ).toBeInTheDocument();
  });
});
