# Frontend Components Documentation

This document provides comprehensive documentation for all React components in the Personal Assistant TDAH frontend application, including their props, usage patterns, and implementation details.

## Table of Contents

- [Component Overview](#component-overview)
- [Authentication Components](#authentication-components)
- [Dashboard Components](#dashboard-components)
- [UI Components](#ui-components)
- [OAuth Components](#oauth-components)
- [Profile Components](#profile-components)
- [Navigation Components](#navigation-components)
- [Admin Components](#admin-components)
- [Component Patterns](#component-patterns)
- [State Management](#state-management)

## Component Overview

The Personal Assistant TDAH frontend is built with React 18 and TypeScript, following modern React patterns and best practices. The component architecture is organized into logical modules with clear separation of concerns.

### Technology Stack

- **React 18**: Latest React features including concurrent rendering
- **TypeScript**: Type-safe development with comprehensive type definitions
- **Tailwind CSS**: Utility-first CSS framework for styling
- **React Router**: Client-side routing and navigation
- **React Hook Form**: Form handling and validation
- **Zustand**: Lightweight state management
- **Vite**: Fast build tool and development server

### Component Architecture

```
src/
├── components/
│   ├── auth/           # Authentication components
│   ├── dashboard/      # Dashboard layout and widgets
│   ├── ui/            # Reusable UI components
│   ├── oauth/         # OAuth integration components
│   ├── profile/       # User profile components
│   ├── navigation/    # Navigation components
│   └── admin/         # Admin-specific components
├── pages/             # Page components
├── stores/           # Zustand state stores
├── services/         # API service layers
├── types/           # TypeScript type definitions
└── utils/           # Utility functions
```

## Authentication Components

### LoginForm Component

**File**: `src/components/auth/LoginForm.tsx`

A comprehensive login form with validation and error handling.

```typescript
interface LoginFormProps {
  onSuccess?: () => void;
  onSwitchToRegister?: () => void;
}

const LoginForm: React.FC<LoginFormProps> = ({
  onSuccess,
  onSwitchToRegister,
}) => {
  // Component implementation
};
```

**Features:**

- Email and password validation
- Loading states and error handling
- Form validation with React Hook Form
- Responsive design with Tailwind CSS
- Integration with auth store

**Props:**

- `onSuccess?: () => void` - Callback when login succeeds
- `onSwitchToRegister?: () => void` - Callback to switch to registration

**Usage:**

```tsx
<LoginForm
  onSuccess={() => navigate("/dashboard")}
  onSwitchToRegister={() => setShowRegister(true)}
/>
```

### RegisterForm Component

**File**: `src/components/auth/RegisterForm.tsx`

User registration form with comprehensive validation.

```typescript
interface RegisterFormProps {
  onSuccess?: () => void;
  onSwitchToLogin?: () => void;
}

const RegisterForm: React.FC<RegisterFormProps> = ({
  onSuccess,
  onSwitchToLogin,
}) => {
  // Component implementation
};
```

**Features:**

- Multi-field registration form
- Password strength validation
- Email format validation
- Terms and conditions acceptance
- Error handling and loading states

**Props:**

- `onSuccess?: () => void` - Callback when registration succeeds
- `onSwitchToLogin?: () => void` - Callback to switch to login

### MFAForm Component

**File**: `src/components/auth/MFAForm.tsx`

Multi-factor authentication form supporting TOTP and SMS.

```typescript
interface MFAFormProps {
  mfaType: "totp" | "sms";
  onSuccess: (code: string) => void;
  onCancel: () => void;
  isLoading?: boolean;
  error?: string;
}

const MFAForm: React.FC<MFAFormProps> = ({
  mfaType,
  onSuccess,
  onCancel,
  isLoading,
  error,
}) => {
  // Component implementation
};
```

**Features:**

- Support for TOTP and SMS MFA
- Code input validation
- Backup code support
- Error handling and retry logic

**Props:**

- `mfaType: 'totp' | 'sms'` - Type of MFA being used
- `onSuccess: (code: string) => void` - Callback with entered code
- `onCancel: () => void` - Callback to cancel MFA
- `isLoading?: boolean` - Loading state
- `error?: string` - Error message to display

### ProtectedRoute Component

**File**: `src/components/auth/ProtectedRoute.tsx`

Route protection component for authentication and authorization.

```typescript
interface ProtectedRouteProps {
  children: React.ReactNode;
  requireAuth?: boolean;
  requiredRoles?: string[];
  requiredPermissions?: string[];
  fallback?: React.ReactNode;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  requireAuth = true,
  requiredRoles,
  requiredPermissions,
  fallback,
}) => {
  // Component implementation
};
```

**Features:**

- Authentication requirement checking
- Role-based access control
- Permission-based access control
- Custom fallback components
- Loading states during auth checks

**Props:**

- `children: React.ReactNode` - Child components to protect
- `requireAuth?: boolean` - Whether authentication is required
- `requiredRoles?: string[]` - Required user roles
- `requiredPermissions?: string[]` - Required permissions
- `fallback?: React.ReactNode` - Component to show when access denied

## Dashboard Components

### DashboardLayout Component

**File**: `src/components/dashboard/DashboardLayout.tsx`

Main dashboard layout with sidebar and header.

```typescript
const DashboardLayout: React.FC = () => {
  const { isSidebarCollapsed, toggleSidebar } = useDashboardStore();

  return (
    <div className="min-h-screen bg-gray-50">
      <Sidebar isCollapsed={isSidebarCollapsed} onToggle={toggleSidebar} />
      <div
        className={`transition-all duration-300 ease-in-out ${contentMargin}`}
      >
        <DashboardHeader onMenuToggle={toggleSidebar} />
        <main className="p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
};
```

**Features:**

- Responsive sidebar with collapse functionality
- Header with user menu and notifications
- Main content area with routing
- Smooth transitions and animations
- Mobile-responsive design

### Sidebar Component

**File**: `src/components/dashboard/Sidebar.tsx`

Navigation sidebar with menu items and user information.

```typescript
interface SidebarProps {
  isCollapsed: boolean;
  onToggle: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ isCollapsed, onToggle }) => {
  // Component implementation
};
```

**Features:**

- Collapsible sidebar design
- Navigation menu items
- User profile section
- Role-based menu visibility
- Active route highlighting

**Props:**

- `isCollapsed: boolean` - Whether sidebar is collapsed
- `onToggle: () => void` - Callback to toggle sidebar state

### DashboardHeader Component

**File**: `src/components/dashboard/DashboardHeader.tsx`

Top header with user menu, notifications, and controls.

```typescript
interface DashboardHeaderProps {
  onMenuToggle: () => void;
}

const DashboardHeader: React.FC<DashboardHeaderProps> = ({ onMenuToggle }) => {
  // Component implementation
};
```

**Features:**

- Mobile menu toggle button
- User profile dropdown
- Notification center
- Search functionality
- Theme toggle

**Props:**

- `onMenuToggle: () => void` - Callback to toggle mobile menu

### UserProfileCard Component

**File**: `src/components/dashboard/UserProfileCard.tsx`

User profile summary card for dashboard.

```typescript
interface UserProfileCardProps {
  user: User;
  onEdit?: () => void;
}

const UserProfileCard: React.FC<UserProfileCardProps> = ({ user, onEdit }) => {
  // Component implementation
};
```

**Features:**

- User avatar and basic information
- Quick stats and metrics
- Edit profile button
- Role and permission display
- MFA status indicator

**Props:**

- `user: User` - User object with profile data
- `onEdit?: () => void` - Callback to edit profile

### SMSAnalyticsWidget Component

**File**: `src/components/dashboard/SMSAnalyticsWidget.tsx`

SMS usage analytics widget for dashboard.

```typescript
interface SMSAnalyticsWidgetProps {
  userId: number;
  timeRange?: "7d" | "30d" | "90d";
  onViewDetails?: () => void;
}

const SMSAnalyticsWidget: React.FC<SMSAnalyticsWidgetProps> = ({
  userId,
  timeRange = "30d",
  onViewDetails,
}) => {
  // Component implementation
};
```

**Features:**

- SMS usage statistics
- Cost breakdown
- Usage trends
- Interactive charts
- Time range selection

**Props:**

- `userId: number` - User ID for analytics
- `timeRange?: '7d' | '30d' | '90d'` - Time range for data
- `onViewDetails?: () => void` - Callback to view detailed analytics

## UI Components

### Button Component

**File**: `src/components/ui/Button.tsx`

Reusable button component with multiple variants and states.

```typescript
interface ButtonProps {
  variant?: "primary" | "secondary" | "outline" | "ghost" | "destructive";
  size?: "sm" | "md" | "lg";
  disabled?: boolean;
  loading?: boolean;
  children: React.ReactNode;
  onClick?: () => void;
  type?: "button" | "submit" | "reset";
  className?: string;
}

const Button: React.FC<ButtonProps> = ({
  variant = "primary",
  size = "md",
  disabled = false,
  loading = false,
  children,
  onClick,
  type = "button",
  className,
}) => {
  // Component implementation
};
```

**Features:**

- Multiple visual variants
- Three size options
- Loading state with spinner
- Disabled state handling
- Custom className support
- Accessibility features

**Variants:**

- `primary`: Blue background, white text
- `secondary`: Gray background, dark text
- `outline`: White background, gray border
- `ghost`: Transparent background, hover effects
- `destructive`: Red background, white text

**Sizes:**

- `sm`: Small button (h-8, px-3)
- `md`: Medium button (h-10, px-4)
- `lg`: Large button (h-12, px-6)

### Input Component

**File**: `src/components/ui/Input.tsx`

Form input component with validation and error handling.

```typescript
interface InputProps {
  label?: string;
  type?: "text" | "email" | "password" | "number" | "tel";
  placeholder?: string;
  value?: string;
  onChange?: (value: string) => void;
  error?: string;
  required?: boolean;
  disabled?: boolean;
  className?: string;
}

const Input: React.FC<InputProps> = ({
  label,
  type = "text",
  placeholder,
  value,
  onChange,
  error,
  required,
  disabled,
  className,
}) => {
  // Component implementation
};
```

**Features:**

- Optional label
- Multiple input types
- Error state display
- Required field indicator
- Disabled state
- Controlled component pattern

### Card Component

**File**: `src/components/ui/Card.tsx`

Card container component with header, content, and footer sections.

```typescript
interface CardProps {
  children: React.ReactNode;
  className?: string;
}

interface CardHeaderProps {
  children: React.ReactNode;
  className?: string;
}

interface CardContentProps {
  children: React.ReactNode;
  className?: string;
}

interface CardFooterProps {
  children: React.ReactNode;
  className?: string;
}

const Card: React.FC<CardProps> = ({ children, className }) => {
  // Component implementation
};

const CardHeader: React.FC<CardHeaderProps> = ({ children, className }) => {
  // Component implementation
};

const CardContent: React.FC<CardContentProps> = ({ children, className }) => {
  // Component implementation
};

const CardFooter: React.FC<CardFooterProps> = ({ children, className }) => {
  // Component implementation
};
```

**Features:**

- Modular card structure
- Consistent styling
- Flexible content areas
- Responsive design
- Shadow and border effects

### Modal Component

**File**: `src/components/ui/Modal.tsx`

Modal dialog component with overlay and close functionality.

```typescript
interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  children: React.ReactNode;
  size?: "sm" | "md" | "lg" | "xl";
  closeOnOverlayClick?: boolean;
  closeOnEscape?: boolean;
}

const Modal: React.FC<ModalProps> = ({
  isOpen,
  onClose,
  title,
  children,
  size = "md",
  closeOnOverlayClick = true,
  closeOnEscape = true,
}) => {
  // Component implementation
};
```

**Features:**

- Overlay and backdrop
- Keyboard navigation (ESC to close)
- Click outside to close
- Multiple sizes
- Title and content areas
- Focus management

**Sizes:**

- `sm`: Small modal (max-w-sm)
- `md`: Medium modal (max-w-md)
- `lg`: Large modal (max-w-lg)
- `xl`: Extra large modal (max-w-xl)

### LoadingSpinner Component

**File**: `src/components/ui/LoadingSpinner.tsx`

Loading spinner component with customizable size and color.

```typescript
interface LoadingSpinnerProps {
  size?: "sm" | "md" | "lg";
  color?: "primary" | "secondary" | "white";
  className?: string;
}

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  size = "md",
  color = "primary",
  className,
}) => {
  // Component implementation
};
```

**Features:**

- Three size options
- Multiple color variants
- Smooth animation
- Customizable styling
- Accessibility support

## OAuth Components

### OAuthProviderCard Component

**File**: `src/components/oauth/OAuthProviderCard.tsx`

Card component for displaying OAuth provider information and status.

```typescript
interface OAuthProviderCardProps {
  provider: OAuthProvider;
  integration?: OAuthIntegration;
  onConnect: () => void;
  onDisconnect: () => void;
  isLoading?: boolean;
}

const OAuthProviderCard: React.FC<OAuthProviderCardProps> = ({
  provider,
  integration,
  onConnect,
  onDisconnect,
  isLoading,
}) => {
  // Component implementation
};
```

**Features:**

- Provider logo and information
- Connection status display
- Connect/disconnect actions
- Loading states
- Error handling

**Props:**

- `provider: OAuthProvider` - OAuth provider information
- `integration?: OAuthIntegration` - Current integration status
- `onConnect: () => void` - Callback to initiate connection
- `onDisconnect: () => void` - Callback to disconnect
- `isLoading?: boolean` - Loading state

### OAuthIntegrationsPage Component

**File**: `src/components/oauth/OAuthIntegrationsPage.tsx`

Main page for managing OAuth integrations.

```typescript
const OAuthIntegrationsPage: React.FC = () => {
  // Component implementation
};
```

**Features:**

- List of available providers
- Integration status overview
- Connection management
- Error handling
- Loading states

### OAuthManager Component

**File**: `src/components/oauth/OAuthManager.tsx`

Manager component for OAuth flow handling.

```typescript
interface OAuthManagerProps {
  children: React.ReactNode;
}

const OAuthManager: React.FC<OAuthManagerProps> = ({ children }) => {
  // Component implementation
};
```

**Features:**

- OAuth flow coordination
- Token management
- Error handling
- State synchronization
- Provider-specific logic

## Profile Components

### ProfileForm Component

**File**: `src/components/profile/ProfileForm.tsx`

User profile editing form.

```typescript
interface ProfileFormProps {
  user: User;
  onSave: (userData: Partial<User>) => Promise<void>;
  onCancel: () => void;
  isLoading?: boolean;
}

const ProfileForm: React.FC<ProfileFormProps> = ({
  user,
  onSave,
  onCancel,
  isLoading,
}) => {
  // Component implementation
};
```

**Features:**

- Editable user information
- Form validation
- Save/cancel actions
- Loading states
- Error handling

**Props:**

- `user: User` - Current user data
- `onSave: (userData: Partial<User>) => Promise<void>` - Save callback
- `onCancel: () => void` - Cancel callback
- `isLoading?: boolean` - Loading state

### PhoneManagement Component

**File**: `src/components/profile/PhoneManagement.tsx`

Phone number management component.

```typescript
interface PhoneManagementProps {
  userId: number;
  onPhoneAdded?: (phoneNumber: string) => void;
  onPhoneRemoved?: (phoneId: number) => void;
}

const PhoneManagement: React.FC<PhoneManagementProps> = ({
  userId,
  onPhoneAdded,
  onPhoneRemoved,
}) => {
  // Component implementation
};
```

**Features:**

- Add/remove phone numbers
- Phone number validation
- Verification status
- Primary number selection
- SMS capabilities

### SecuritySettings Component

**File**: `src/components/profile/SecuritySettings.tsx`

Security settings management component.

```typescript
interface SecuritySettingsProps {
  user: User;
  onMFAEnabled?: () => void;
  onMFADisabled?: () => void;
  onPasswordChanged?: () => void;
}

const SecuritySettings: React.FC<SecuritySettingsProps> = ({
  user,
  onMFAEnabled,
  onMFADisabled,
  onPasswordChanged,
}) => {
  // Component implementation
};
```

**Features:**

- MFA enable/disable
- Password change
- Session management
- Security event history
- Account lockout settings

## Navigation Components

### NavigationMenu Component

**File**: `src/components/navigation/NavigationMenu.tsx`

Main navigation menu component.

```typescript
interface NavigationMenuProps {
  items: NavigationItem[];
  activeItem?: string;
  onItemClick: (item: NavigationItem) => void;
  className?: string;
}

interface NavigationItem {
  id: string;
  label: string;
  icon?: React.ReactNode;
  path: string;
  roles?: string[];
  permissions?: string[];
}

const NavigationMenu: React.FC<NavigationMenuProps> = ({
  items,
  activeItem,
  onItemClick,
  className,
}) => {
  // Component implementation
};
```

**Features:**

- Dynamic menu items
- Role-based visibility
- Permission-based access
- Active state highlighting
- Icon support

### Breadcrumbs Component

**File**: `src/components/navigation/Breadcrumbs.tsx`

Breadcrumb navigation component.

```typescript
interface BreadcrumbItem {
  label: string;
  path?: string;
  active?: boolean;
}

interface BreadcrumbsProps {
  items: BreadcrumbItem[];
  onItemClick?: (item: BreadcrumbItem) => void;
  className?: string;
}

const Breadcrumbs: React.FC<BreadcrumbsProps> = ({
  items,
  onItemClick,
  className,
}) => {
  // Component implementation
};
```

**Features:**

- Hierarchical navigation
- Clickable breadcrumb items
- Active state indication
- Responsive design
- Custom styling

## Admin Components

### SMSAnalyticsPanel Component

**File**: `src/components/admin/SMSAnalyticsPanel.tsx`

Admin panel for SMS analytics and management.

```typescript
interface SMSAnalyticsPanelProps {
  onUserSelected?: (userId: number) => void;
  onExportData?: (format: "csv" | "json") => void;
}

const SMSAnalyticsPanel: React.FC<SMSAnalyticsPanelProps> = ({
  onUserSelected,
  onExportData,
}) => {
  // Component implementation
};
```

**Features:**

- System-wide SMS analytics
- User-specific data
- Export functionality
- Real-time updates
- Performance metrics

## Component Patterns

### Higher-Order Components (HOCs)

**withAuth HOC**

```typescript
const withAuth = <P extends object>(Component: React.ComponentType<P>) => {
  return (props: P) => {
    const { isAuthenticated } = useAuthStore();

    if (!isAuthenticated) {
      return <Navigate to="/login" />;
    }

    return <Component {...props} />;
  };
};
```

**withRole HOC**

```typescript
const withRole =
  (requiredRoles: string[]) =>
  <P extends object>(Component: React.ComponentType<P>) => {
    return (props: P) => {
      const { user } = useAuthStore();

      if (!user || !hasRequiredRoles(user, requiredRoles)) {
        return <AccessDenied />;
      }

      return <Component {...props} />;
    };
  };
```

### Custom Hooks

**useAuth Hook**

```typescript
const useAuth = () => {
  const { user, isAuthenticated, login, logout } = useAuthStore();

  return {
    user,
    isAuthenticated,
    login,
    logout,
    hasRole: (role: string) => user?.roles?.includes(role),
    hasPermission: (permission: string) =>
      user?.permissions?.includes(permission),
  };
};
```

**useApi Hook**

```typescript
const useApi = <T>(url: string, options?: RequestInit) => {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await api.get(url, options);
      setData(response.data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [url, options]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return { data, loading, error, refetch: fetchData };
};
```

### Error Boundaries

**ErrorBoundary Component**

```typescript
interface ErrorBoundaryState {
  hasError: boolean;
  error?: Error;
}

class ErrorBoundary extends React.Component<
  React.PropsWithChildren<{}>,
  ErrorBoundaryState
> {
  constructor(props: React.PropsWithChildren<{}>) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error("Error caught by boundary:", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return <ErrorFallback error={this.state.error} />;
    }

    return this.props.children;
  }
}
```

## State Management

### Zustand Stores

**Auth Store**

```typescript
interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  mfaRequired: boolean;
  mfaSetupRequired: boolean;

  login: (credentials: LoginRequest) => Promise<boolean>;
  register: (userData: RegisterRequest) => Promise<boolean>;
  logout: () => Promise<void>;
  checkAuth: () => Promise<void>;
  clearError: () => void;
  setMFARequired: (required: boolean) => void;
  setMFASetupRequired: (required: boolean) => void;
}
```

**Dashboard Store**

```typescript
interface DashboardState {
  isSidebarCollapsed: boolean;
  currentPage: string;
  notifications: Notification[];

  toggleSidebar: () => void;
  setCurrentPage: (page: string) => void;
  addNotification: (notification: Notification) => void;
  removeNotification: (id: string) => void;
  clearNotifications: () => void;
}
```

**OAuth Store**

```typescript
interface OAuthState {
  providers: OAuthProvider[];
  integrations: OAuthIntegration[];
  isLoading: boolean;
  error: string | null;

  loadProviders: () => Promise<void>;
  loadIntegrations: () => Promise<void>;
  connectProvider: (provider: string) => Promise<void>;
  disconnectProvider: (integrationId: string) => Promise<void>;
  clearError: () => void;
}
```

### Store Patterns

**Persistence**

```typescript
export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      // Store implementation
    }),
    {
      name: "auth-storage",
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
        mfaRequired: state.mfaRequired,
        mfaSetupRequired: state.mfaSetupRequired,
      }),
    }
  )
);
```

**Middleware**

```typescript
export const useApiStore = create<ApiState>()(
  subscribeWithSelector(
    devtools(
      (set, get) => ({
        // Store implementation
      }),
      { name: "api-store" }
    )
  )
);
```

This comprehensive component documentation provides developers with all the information needed to understand, use, and extend the Personal Assistant TDAH frontend components effectively.
