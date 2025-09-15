import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import OAuthProviderCard from '../OAuthProviderCard';
import { useOAuthStore } from '@/stores/oauthStore';

// Mock the OAuth store
vi.mock('@/stores/oauthStore', () => ({
  useOAuthStore: vi.fn(),
}));

// Mock the UI components
vi.mock('@/components/ui', () => ({
  Button: ({
    children,
    onClick,
    disabled,
    className,
  }: {
    children: React.ReactNode;
    onClick?: () => void;
    disabled?: boolean;
    className?: string;
  }) => (
    <button onClick={onClick} disabled={disabled} className={className}>
      {children}
    </button>
  ),
  Card: ({
    children,
    className,
  }: {
    children: React.ReactNode;
    className?: string;
  }) => <div className={className}>{children}</div>,
}));

describe('OAuthProviderCard', () => {
  const mockProvider = 'google';

  const mockStore = {
    getProviderConfig: vi.fn(),
    getIntegration: vi.fn(),
    isConnected: vi.fn(),
    connectIntegration: vi.fn(),
    disconnectIntegration: vi.fn(),
    isLoading: false,
  };

  beforeEach(() => {
    vi.clearAllMocks();
    (useOAuthStore as any).mockReturnValue(mockStore);
  });

  it('renders provider information correctly', () => {
    mockStore.getProviderConfig.mockReturnValue({
      id: 'google',
      name: 'Google',
      logo: '/icons/google.svg',
      description: 'Connect your Google account',
      features: ['Calendar', 'Drive', 'Gmail'],
      color: '#4285F4',
    });

    mockStore.getIntegration.mockReturnValue(null);
    mockStore.isConnected.mockReturnValue(false);

    render(<OAuthProviderCard provider={mockProvider} />);

    expect(screen.getByText('Google')).toBeInTheDocument();
    expect(screen.getByText('Connect your Google account')).toBeInTheDocument();
    expect(screen.getByText('Calendar')).toBeInTheDocument();
    expect(screen.getByText('Drive')).toBeInTheDocument();
    expect(screen.getByText('Gmail')).toBeInTheDocument();
  });

  it('shows connect button when not connected', () => {
    mockStore.getProviderConfig.mockReturnValue({
      id: 'google',
      name: 'Google',
      logo: '/icons/google.svg',
      description: 'Connect your Google account',
      features: ['Calendar', 'Drive', 'Gmail'],
      color: '#4285F4',
    });

    mockStore.getIntegration.mockReturnValue(null);
    mockStore.isConnected.mockReturnValue(false);

    render(<OAuthProviderCard provider={mockProvider} />);

    expect(screen.getByText('Connect')).toBeInTheDocument();
  });

  it('shows disconnect button when connected', () => {
    mockStore.getProviderConfig.mockReturnValue({
      id: 'google',
      name: 'Google',
      logo: '/icons/google.svg',
      description: 'Connect your Google account',
      features: ['Calendar', 'Drive', 'Gmail'],
      color: '#4285F4',
    });

    mockStore.getIntegration.mockReturnValue({
      id: '1',
      provider: 'google',
      status: 'connected',
      connectedAt: '2024-01-01T00:00:00Z',
      usageStats: { apiCalls: 10, errors: 0 },
      userId: 1,
    });

    mockStore.isConnected.mockReturnValue(true);

    render(<OAuthProviderCard provider={mockProvider} />);

    expect(screen.getByText('Disconnect')).toBeInTheDocument();
    expect(screen.getByText('Manage')).toBeInTheDocument();
  });

  it('calls connectIntegration when connect button is clicked', () => {
    mockStore.getProviderConfig.mockReturnValue({
      id: 'google',
      name: 'Google',
      logo: '/icons/google.svg',
      description: 'Connect your Google account',
      features: ['Calendar', 'Drive', 'Gmail'],
      color: '#4285F4',
    });

    mockStore.getIntegration.mockReturnValue(null);
    mockStore.isConnected.mockReturnValue(false);

    render(<OAuthProviderCard provider={mockProvider} />);

    const connectButton = screen.getByText('Connect');
    fireEvent.click(connectButton);

    expect(mockStore.connectIntegration).toHaveBeenCalledWith('google', [
      'read',
    ]);
  });

  it('calls disconnectIntegration when disconnect button is clicked', () => {
    mockStore.getProviderConfig.mockReturnValue({
      id: 'google',
      name: 'Google',
      logo: '/icons/google.svg',
      description: 'Connect your Google account',
      features: ['Calendar', 'Drive', 'Gmail'],
      color: '#4285F4',
    });

    mockStore.getIntegration.mockReturnValue({
      id: '1',
      provider: 'google',
      status: 'connected',
      connectedAt: '2024-01-01T00:00:00Z',
      usageStats: { apiCalls: 10, errors: 0 },
      userId: 1,
    });

    mockStore.isConnected.mockReturnValue(true);

    render(<OAuthProviderCard provider={mockProvider} />);

    const disconnectButton = screen.getByText('Disconnect');
    fireEvent.click(disconnectButton);

    expect(mockStore.disconnectIntegration).toHaveBeenCalledWith('google');
  });

  it('shows loading state when isLoading is true', () => {
    mockStore.getProviderConfig.mockReturnValue({
      id: 'google',
      name: 'Google',
      logo: '/icons/google.svg',
      description: 'Connect your Google account',
      features: ['Calendar', 'Drive', 'Gmail'],
      color: '#4285F4',
    });

    mockStore.getIntegration.mockReturnValue(null);
    mockStore.isConnected.mockReturnValue(false);
    mockStore.isLoading = true;

    render(<OAuthProviderCard provider={mockProvider} />);

    expect(screen.getByText('Connecting...')).toBeInTheDocument();
  });

  it('returns null when provider config is not found', () => {
    mockStore.getProviderConfig.mockReturnValue(null);

    const { container } = render(<OAuthProviderCard provider={mockProvider} />);
    expect(container.firstChild).toBeNull();
  });
});
