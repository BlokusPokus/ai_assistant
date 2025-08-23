import type { OAuthProviderConfig, OAuthScope } from '@/types/oauth';

// OAuth Scopes for each provider
export const OAUTH_SCOPES: Record<string, OAuthScope[]> = {
  google: [
    {
      id: 'https://www.googleapis.com/auth/calendar',
      name: 'Google Calendar',
      description: 'View and manage your Google Calendar',
      required: false,
      category: 'read',
      provider: 'google',
    },
    {
      id: 'https://www.googleapis.com/auth/calendar.events',
      name: 'Calendar Events',
      description: 'View and manage events on your Google Calendar',
      required: false,
      category: 'write',
      provider: 'google',
    },
    {
      id: 'https://www.googleapis.com/auth/drive',
      name: 'Google Drive',
      description: 'View and manage your Google Drive files',
      required: false,
      category: 'read',
      provider: 'google',
    },
    {
      id: 'https://www.googleapis.com/auth/gmail.readonly',
      name: 'Gmail Read',
      description: 'View your Gmail messages',
      required: false,
      category: 'read',
      provider: 'google',
    },
    {
      id: 'https://www.googleapis.com/auth/tasks',
      name: 'Google Tasks',
      description: 'View and manage your Google Tasks',
      required: false,
      category: 'write',
      provider: 'google',
    },
  ],
  microsoft: [
    {
      id: 'Calendars.Read',
      name: 'Calendar Read',
      description: 'Read your calendar',
      required: false,
      category: 'read',
      provider: 'microsoft',
    },
    {
      id: 'Calendars.ReadWrite',
      name: 'Calendar Read/Write',
      description: 'Read and write to your calendar',
      required: false,
      category: 'write',
      provider: 'microsoft',
    },
    {
      id: 'Files.Read',
      name: 'OneDrive Read',
      description: 'Read your OneDrive files',
      required: false,
      category: 'read',
      provider: 'microsoft',
    },
    {
      id: 'Files.ReadWrite',
      name: 'OneDrive Read/Write',
      description: 'Read and write to your OneDrive',
      required: false,
      category: 'write',
      provider: 'microsoft',
    },
    {
      id: 'Mail.Read',
      name: 'Mail Read',
      description: 'Read your email',
      required: false,
      category: 'read',
      provider: 'microsoft',
    },
    {
      id: 'Tasks.ReadWrite',
      name: 'Tasks Read/Write',
      description: 'Read and write to your tasks',
      required: false,
      category: 'write',
      provider: 'microsoft',
    },
  ],
  notion: [
    {
      id: 'read',
      name: 'Read Access',
      description: 'Read your Notion pages and databases',
      required: true,
      category: 'read',
      provider: 'notion',
    },
    {
      id: 'write',
      name: 'Write Access',
      description: 'Create and edit your Notion content',
      required: false,
      category: 'write',
      provider: 'notion',
    },
    {
      id: 'admin',
      name: 'Admin Access',
      description: 'Manage your Notion workspace',
      required: false,
      category: 'admin',
      provider: 'notion',
    },
  ],
  youtube: [
    {
      id: 'https://www.googleapis.com/auth/youtube.readonly',
      name: 'YouTube Read',
      description: 'View your YouTube account',
      required: false,
      category: 'read',
      provider: 'youtube',
    },
    {
      id: 'https://www.googleapis.com/auth/youtube',
      name: 'YouTube Full',
      description: 'Manage your YouTube account',
      required: false,
      category: 'write',
      provider: 'youtube',
    },
    {
      id: 'https://www.googleapis.com/auth/youtube.force-ssl',
      name: 'YouTube Secure',
      description: 'Secure access to your YouTube account',
      required: false,
      category: 'read',
      provider: 'youtube',
    },
  ],
};

// OAuth Provider configurations
export const OAUTH_PROVIDERS: OAuthProviderConfig[] = [
  {
    id: 'google',
    name: 'Google',
    logo: '/icons/google.svg',
    description:
      'Connect your Google account to access Calendar, Drive, Gmail, and Tasks',
    availableScopes: OAUTH_SCOPES.google,
    features: [
      'Calendar Integration',
      'File Management',
      'Email Access',
      'Task Management',
    ],
    color: '#4285F4',
    authUrl: 'https://accounts.google.com/o/oauth2/v2/auth',
    clientId: import.meta.env.VITE_GOOGLE_CLIENT_ID || '',
    redirectUri: `${window.location.origin}/oauth/callback/google`,
  },
  {
    id: 'microsoft',
    name: 'Microsoft',
    logo: '/icons/microsoft.svg',
    description:
      'Connect your Microsoft account to access Outlook, OneDrive, Teams, and SharePoint',
    availableScopes: OAUTH_SCOPES.microsoft,
    features: [
      'Email & Calendar',
      'Cloud Storage',
      'Team Collaboration',
      'Document Management',
    ],
    color: '#0078D4',
    authUrl: 'https://login.microsoftonline.com/common/oauth2/v2.0/authorize',
    clientId: import.meta.env.VITE_MICROSOFT_CLIENT_ID || '',
    redirectUri: `${window.location.origin}/oauth/callback/microsoft`,
  },
  {
    id: 'notion',
    name: 'Notion',
    logo: '/icons/notion.svg',
    description:
      'Connect your Notion workspace to manage pages, databases, and templates',
    availableScopes: OAUTH_SCOPES.notion,
    features: [
      'Page Management',
      'Database Access',
      'Template Library',
      'Collaboration',
    ],
    color: '#000000',
    authUrl: 'https://api.notion.com/v1/oauth/authorize',
    clientId: import.meta.env.VITE_NOTION_CLIENT_ID || '',
    redirectUri: `${window.location.origin}/oauth/callback/notion`,
  },
  {
    id: 'youtube',
    name: 'YouTube',
    logo: '/icons/youtube.svg',
    description:
      'Connect your YouTube account to manage playlists, history, and recommendations',
    availableScopes: OAUTH_SCOPES.youtube,
    features: [
      'Playlist Management',
      'Viewing History',
      'Recommendations',
      'Channel Analytics',
    ],
    color: '#FF0000',
    authUrl: 'https://accounts.google.com/o/oauth2/v2/auth',
    clientId: import.meta.env.VITE_YOUTUBE_CLIENT_ID || '',
    redirectUri: `${window.location.origin}/oauth/callback/youtube`,
  },
];

// OAuth Status colors for UI
export const OAUTH_STATUS_COLORS = {
  connected: '#10B981', // green-500
  disconnected: '#6B7280', // gray-500
  pending: '#F59E0B', // amber-500
  error: '#EF4444', // red-500
  expired: '#F97316', // orange-500
};

// OAuth Status labels for UI
export const OAUTH_STATUS_LABELS = {
  connected: 'Connected',
  disconnected: 'Disconnected',
  pending: 'Pending',
  error: 'Error',
  expired: 'Expired',
};

// OAuth Health status colors
export const OAUTH_HEALTH_COLORS = {
  healthy: '#10B981', // green-500
  warning: '#F59E0B', // amber-500
  error: '#EF4444', // red-500
};

// OAuth Health status labels
export const OAUTH_HEALTH_LABELS = {
  healthy: 'Healthy',
  warning: 'Warning',
  error: 'Error',
};

// Default OAuth scopes for each provider (minimal required scopes)
export const DEFAULT_OAUTH_SCOPES: Record<string, string[]> = {
  google: ['https://www.googleapis.com/auth/calendar.readonly'],
  microsoft: ['Calendars.Read'],
  notion: ['read'],
  youtube: ['https://www.googleapis.com/auth/youtube.readonly'],
};

// OAuth error messages
export const OAUTH_ERROR_MESSAGES = {
  connection_failed: 'Failed to connect to the service. Please try again.',
  token_expired: 'Your connection has expired. Please reconnect.',
  insufficient_permissions:
    'Insufficient permissions. Please grant the required access.',
  service_unavailable:
    'The service is currently unavailable. Please try again later.',
  network_error: 'Network error. Please check your connection and try again.',
  user_cancelled: 'Connection was cancelled by the user.',
  invalid_state: 'Invalid OAuth state. Please try again.',
  scope_denied: 'Some requested permissions were denied.',
};
