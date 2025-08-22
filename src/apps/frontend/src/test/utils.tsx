import React from 'react';
import {
  render,
  RenderOptions,
  screen,
  fireEvent,
  waitFor,
} from '@testing-library/react';
import { AllTheProviders } from './providers';

// Custom render function that includes providers
const customRender = (
  ui: React.ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
) => render(ui, { wrapper: AllTheProviders, ...options });

// Export all testing library functions
export { customRender as render, screen, fireEvent, waitFor };

// Test data factories
export const createMockUser = (overrides = {}) => ({
  id: 1,
  email: 'test@example.com',
  full_name: 'Test User',
  is_active: true,
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
  ...overrides,
});

export const createMockAuthResponse = (overrides = {}) => ({
  access_token: 'mock-access-token',
  refresh_token: 'mock-refresh-token',
  user: createMockUser(),
  mfa_required: false,
  mfa_setup_required: false,
  ...overrides,
});

export const createMockMFASetupResponse = (overrides = {}) => ({
  qr_code: 'data:image/png;base64,mock-qr-code',
  backup_codes: ['123456', '789012', '345678', '901234'],
  secret_key: 'MOCKSECRETKEY123',
  ...overrides,
});
