import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { TabNavigation } from '../TabNavigation';

// Mock the stores and utilities
vi.mock('../../../../stores/authStore', () => ({
  useAuthStore: vi.fn(() => ({
    user: null,
  })),
}));

vi.mock('../../../../utils/roleUtils', () => ({
  isPremium: vi.fn(() => false),
  isAdmin: vi.fn(() => false),
}));

describe('TabNavigation', () => {
  const mockOnTabChange = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders basic tabs for non-authenticated user', () => {
    render(
      <TabNavigation activeTab="integrations" onTabChange={mockOnTabChange} />
    );

    expect(screen.getByText('Integrations')).toBeInTheDocument();
    expect(screen.getByText('Settings')).toBeInTheDocument();
    expect(screen.queryByText('Analytics')).not.toBeInTheDocument();
    expect(screen.queryByText('Audit Logs')).not.toBeInTheDocument();
  });

  it('calls onTabChange when tab is clicked', () => {
    render(
      <TabNavigation activeTab="integrations" onTabChange={mockOnTabChange} />
    );

    const settingsTab = screen.getByText('Settings');
    fireEvent.click(settingsTab);

    expect(mockOnTabChange).toHaveBeenCalledWith('settings');
  });

  it('shows active tab styling', () => {
    render(
      <TabNavigation activeTab="integrations" onTabChange={mockOnTabChange} />
    );

    const integrationsTab = screen.getByText('Integrations');
    expect(integrationsTab).toHaveClass('border-blue-500', 'text-blue-600');
  });

  describe('Role-based tab visibility', () => {
    it('shows all tabs for admin user', () => {
      // Mock admin user
      const { useAuthStore } = require('../../../../stores/authStore');
      const { isAdmin, isPremium } = require('../../../../utils/roleUtils');

      useAuthStore.mockReturnValue({
        user: { id: 1, roles: [{ name: 'administrator' }] },
      });
      isAdmin.mockReturnValue(true);
      isPremium.mockReturnValue(true);

      render(
        <TabNavigation activeTab="integrations" onTabChange={mockOnTabChange} />
      );

      expect(screen.getByText('Integrations')).toBeInTheDocument();
      expect(screen.getByText('Analytics')).toBeInTheDocument();
      expect(screen.getByText('Audit Logs')).toBeInTheDocument();
      expect(screen.getByText('Settings')).toBeInTheDocument();
    });

    it('shows premium tabs for premium user', () => {
      // Mock premium user
      const { useAuthStore } = require('../../../../stores/authStore');
      const { isAdmin, isPremium } = require('../../../../utils/roleUtils');

      useAuthStore.mockReturnValue({
        user: { id: 1, roles: [{ name: 'premium' }] },
      });
      isAdmin.mockReturnValue(false);
      isPremium.mockReturnValue(true);

      render(
        <TabNavigation activeTab="integrations" onTabChange={mockOnTabChange} />
      );

      expect(screen.getByText('Integrations')).toBeInTheDocument();
      expect(screen.getByText('Analytics')).toBeInTheDocument();
      expect(screen.getByText('Settings')).toBeInTheDocument();
      expect(screen.queryByText('Audit Logs')).not.toBeInTheDocument();
    });

    it('shows only basic tabs for regular user', () => {
      // Mock regular user
      const { useAuthStore } = require('../../../../stores/authStore');
      const { isAdmin, isPremium } = require('../../../../utils/roleUtils');

      useAuthStore.mockReturnValue({
        user: { id: 1, roles: [{ name: 'user' }] },
      });
      isAdmin.mockReturnValue(false);
      isPremium.mockReturnValue(false);

      render(
        <TabNavigation activeTab="integrations" onTabChange={mockOnTabChange} />
      );

      expect(screen.getByText('Integrations')).toBeInTheDocument();
      expect(screen.getByText('Settings')).toBeInTheDocument();
      expect(screen.queryByText('Analytics')).not.toBeInTheDocument();
      expect(screen.queryByText('Audit Logs')).not.toBeInTheDocument();
    });

    it('switches to first visible tab when active tab becomes unavailable', () => {
      // Mock user without premium access
      const { useAuthStore } = require('../../../../stores/authStore');
      const { isAdmin, isPremium } = require('../../../../utils/roleUtils');

      useAuthStore.mockReturnValue({
        user: { id: 1, roles: [{ name: 'user' }] },
      });
      isAdmin.mockReturnValue(false);
      isPremium.mockReturnValue(false);

      render(
        <TabNavigation activeTab="analytics" onTabChange={mockOnTabChange} />
      );

      // Should switch to integrations (first visible tab)
      expect(mockOnTabChange).toHaveBeenCalledWith('integrations');
    });
  });
});
