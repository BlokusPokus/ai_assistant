# Frontend Pages Documentation

This document provides comprehensive documentation for all frontend pages in the Personal Assistant TDAH system.

## Overview

The frontend is built with React 18 and TypeScript, using a modern component-based architecture. All pages are designed with accessibility, responsiveness, and user experience in mind, specifically tailored for users with ADHD.

## Page Structure

### Public Pages

#### LandingPage (`/`)

**File**: `src/pages/LandingPage.tsx`

The main landing page showcasing the application's value proposition for ADHD users.

**Key Features**:

- Hero section with compelling value proposition
- Social proof statistics (15,000+ users, 98% satisfaction)
- ADHD-specific challenges and solutions
- Feature highlights with benefits
- Success stories from real users
- Call-to-action sections
- Responsive design with glass morphism effects

**Sections**:

- Navigation with logo and auth links
- Hero with gradient text and social proof
- ADHD challenges (time blindness, task paralysis, digital distractions, memory issues)
- Feature showcase (smart task breakdown, gentle reminders, progress visualization, etc.)
- Success stories with testimonials
- How it works (3-step process)
- Final CTA with urgency elements

**Components Used**:

- `Button`, `Card` from UI components
- Custom gradient backgrounds
- Responsive grid layouts

#### LoginPage (`/login`)

**File**: `src/pages/LoginPage.tsx`

Authentication page supporting both login and registration modes.

**Key Features**:

- Toggle between login and registration forms
- Success feedback for registration
- Automatic redirect for authenticated users
- Back to landing page navigation
- Terms and privacy policy links

**State Management**:

- `authMode`: 'login' | 'register'
- `registrationSuccess`: boolean
- Uses `useAuthStore` for authentication state

**Components Used**:

- `LoginForm`, `RegisterForm` from auth components
- `Button`, `Card`, `CardContent` from UI components
- `ArrowLeft`, `CheckCircle` icons from Lucide React

#### WaitListLandingPage (`/waitlist`)

**File**: `src/pages/WaitListLandingPage.tsx`

Waitlist signup page with urgency and social proof elements.

**Key Features**:

- Email collection form
- Urgency indicators (47 spots left)
- ADHD struggles and solutions
- Exclusive benefits for waitlist members
- Testimonials from waitlist members
- FAQ section
- Multiple CTA sections

**Sections**:

- Hero with urgency badge
- ADHD struggles identification
- Bloop solutions showcase
- Exclusive waitlist benefits
- Testimonials
- FAQ section
- Final CTA with urgency

**State Management**:

- `email`: string for form input
- `isSubmitted`: boolean for form state

#### MFASetupPage (`/mfa-setup`)

**File**: `src/pages/MFASetupPage.tsx`

Multi-factor authentication setup page with QR code and backup codes.

**Key Features**:

- MFA setup with TOTP
- QR code display for authenticator apps
- Backup codes generation
- Security information section
- Error handling and loading states
- Cancel and retry functionality

**State Management**:

- `mfaData`: MFASetupResponse | null
- `isLoading`: boolean
- `error`: string | null

**Components Used**:

- `MFAForm` from auth components
- `Button`, `Card` from UI components
- Various Lucide React icons

#### DesignSystemPage (`/design-system`)

**File**: `src/pages/DesignSystemPage.tsx`

Design system showcase page for UI components and styling.

**Key Features**:

- Color palette demonstration
- Typography scale examples
- Button system showcase
- Form components examples
- Responsive design indicators
- Animation system examples
- Glass morphism effects

**Components Used**:

- `ResponsiveContainer`, `Button`, `Card`, `Input` from UI components
- `useIsMobile` hook for responsive behavior

### Dashboard Pages

#### DashboardHome (`/dashboard`)

**File**: `src/pages/dashboard/DashboardHome.tsx`

Main dashboard page with overview, stats, and quick actions.

**Key Features**:

- Welcome section with user greeting
- Statistics cards (conversations, tasks, notes, time saved)
- Quick action buttons (chat, calendar, notes, settings)
- Recent activity feed
- System status indicators
- Coming soon features section

**Data Sources**:

- `useAuthStore` for user information
- `useProfileStore` for profile data
- `useDashboardDataStore` for dashboard statistics

**Quick Actions**:

- Start Chat → `/dashboard/chat`
- View Schedule → `/dashboard/calendar`
- My Notes → `/dashboard/notes`
- Settings → `/dashboard/settings`

#### ChatPage (`/dashboard/chat`)

**File**: `src/pages/dashboard/ChatPage.tsx`

Real-time chat interface with AI assistant.

**Key Features**:

- Conversation sidebar with history
- Real-time message display
- Message input with send functionality
- Conversation management (new, delete)
- Auto-scroll to latest messages
- Loading states and error handling
- Message deduplication and filtering

**State Management**:

- `messages`: MessageResponse[]
- `conversations`: ConversationResponse[]
- `currentConversationId`: string | null
- `inputMessage`: string
- `isLoading`: boolean
- `error`: string | null

**API Integration**:

- `chatApi.getConversations()`
- `chatApi.getConversationMessages()`
- `chatApi.startNewConversation()`
- `chatApi.continueConversation()`
- `chatApi.deleteConversation()`

**Components Used**:

- `MessageBubble` for individual messages
- `Input` for message input
- Various Lucide React icons

#### ProfilePage (`/dashboard/profile`)

**File**: `src/pages/dashboard/ProfilePage.tsx`

Comprehensive profile management page.

**Key Features**:

- Profile information form
- Application settings
- Security settings
- Phone number management
- Integrated profile components

**Components Used**:

- `ProfileForm`
- `SettingsForm`
- `SecuritySettings`
- `PhoneManagement`

#### SettingsPage (`/dashboard/settings`)

**File**: `src/pages/dashboard/SettingsPage.tsx`

Application settings management page.

**Key Features**:

- Theme customization
- Notification preferences
- Privacy settings
- User preferences

**Components Used**:

- `SettingsForm`

#### SecurityPage (`/dashboard/security`)

**File**: `src/pages/dashboard/SecurityPage.tsx`

Security settings and MFA management page.

**Key Features**:

- Password management
- Two-factor authentication setup
- Account security settings
- Security event monitoring

**Components Used**:

- `SecuritySettings`

#### PhoneManagementPage (`/dashboard/phone-management`)

**File**: `src/pages/dashboard/PhoneManagementPage.tsx`

Dedicated phone number management page.

**Key Features**:

- Phone number overview
- Verification process
- SMS notification settings
- Help documentation
- Breadcrumb navigation

**Components Used**:

- `PhoneManagement`
- `Button`, `Card` from UI components
- `ArrowLeft`, `Phone` icons

#### CalendarPage (`/dashboard/calendar`)

**File**: `src/pages/dashboard/CalendarPage.tsx`

Calendar interface with event management.

**Key Features**:

- Calendar grid view
- Event creation and management
- Upcoming events list
- Quick action buttons
- Integration notice (Microsoft/Google)
- Coming soon features

**Mock Data**:

- Sample events (meetings, appointments, tasks)
- Event type categorization
- Time and location display

**Components Used**:

- `Card` from UI components
- Various Lucide React icons

#### NotesPage (`/dashboard/notes`)

**File**: `src/pages/dashboard/NotesPage.tsx`

Notes management interface with search and categorization.

**Key Features**:

- Notes grid display
- Search functionality
- Category filtering
- Tag system
- Quick actions
- Integration notice (Notion)
- Coming soon features

**State Management**:

- `searchTerm`: string
- `selectedCategory`: string

**Mock Data**:

- Sample notes with categories and tags
- Work and personal categorization

**Components Used**:

- `Card` from UI components
- Various Lucide React icons

#### SMSAnalyticsPage (`/dashboard/sms-analytics`)

**File**: `src/pages/dashboard/SMSAnalyticsPage.tsx`

SMS usage analytics and performance monitoring.

**Key Features**:

- Quick stats cards
- Detailed analytics widget
- Export reports functionality
- Performance insights
- Real-time data display

**Components Used**:

- `SMSAnalyticsWidget` from dashboard components
- `Card` from UI components
- Various Lucide React icons

#### AdminAnalyticsPage (`/dashboard/admin-analytics`)

**File**: `src/pages/dashboard/AdminAnalyticsPage.tsx`

Admin-only system-wide analytics dashboard.

**Key Features**:

- Admin quick stats
- System analytics dashboard
- Performance monitoring
- Alert management
- Administrative tools overview
- Admin access indicators

**Components Used**:

- `SMSAnalyticsPanel` from admin components
- `Card` from UI components
- Various Lucide React icons

## Page Routing

The application uses React Router for navigation with the following route structure:

```typescript
// Public routes
/ → LandingPage
/login → LoginPage
/waitlist → WaitListLandingPage
/mfa-setup → MFASetupPage
/design-system → DesignSystemPage

// Dashboard routes (protected)
/dashboard → DashboardHome
/dashboard/chat → ChatPage
/dashboard/profile → ProfilePage
/dashboard/settings → SettingsPage
/dashboard/security → SecurityPage
/dashboard/phone-management → PhoneManagementPage
/dashboard/calendar → CalendarPage
/dashboard/notes → NotesPage
/dashboard/sms-analytics → SMSAnalyticsPage
/dashboard/admin-analytics → AdminAnalyticsPage
```

## Design Patterns

### Consistent Layout Structure

- Header with navigation
- Main content area
- Footer (where applicable)
- Responsive grid layouts

### State Management

- Zustand stores for global state
- Local component state for UI interactions
- API service integration for data fetching

### Error Handling

- Loading states for async operations
- Error messages with user-friendly text
- Retry mechanisms where appropriate

### Accessibility

- Semantic HTML structure
- ARIA labels and descriptions
- Keyboard navigation support
- Screen reader compatibility

### Responsive Design

- Mobile-first approach
- Flexible grid systems
- Touch-friendly interface elements
- Adaptive layouts for different screen sizes

## Component Dependencies

### UI Components

- `Button` - Various variants and sizes
- `Card` - Container components
- `Input` - Form input fields
- `ResponsiveContainer` - Layout wrapper

### Auth Components

- `LoginForm` - Login functionality
- `RegisterForm` - Registration functionality
- `MFAForm` - Multi-factor authentication

### Profile Components

- `ProfileForm` - Profile management
- `SettingsForm` - Application settings
- `SecuritySettings` - Security configuration
- `PhoneManagement` - Phone number management

### Dashboard Components

- `SMSAnalyticsWidget` - SMS analytics display
- `SMSAnalyticsPanel` - Admin analytics panel

### Chat Components

- `MessageBubble` - Individual message display

## Styling and Theming

### Design System

- Consistent color palette
- Typography scale
- Spacing system
- Glass morphism effects
- Animation system

### Tailwind CSS Classes

- Utility-first approach
- Custom color variables
- Responsive breakpoints
- Component-specific styling

### ADHD-Friendly Design

- Clear visual hierarchy
- Reduced cognitive load
- Gentle animations
- Non-overwhelming interfaces
- Focus-friendly layouts

## Performance Considerations

### Code Splitting

- Route-based code splitting
- Lazy loading of components
- Dynamic imports for heavy components

### State Optimization

- Minimal re-renders
- Efficient state updates
- Memoization where appropriate

### Asset Optimization

- Optimized images
- Efficient icon usage
- Minimal bundle size

## Future Enhancements

### Planned Features

- Real-time WebSocket chat
- Advanced calendar integration
- Rich text note editing
- Mobile app development
- Advanced analytics
- AI-powered insights

### Integration Roadmap

- Microsoft Graph API
- Google Calendar API
- Notion API
- Advanced SMS routing
- Third-party productivity tools

## Development Guidelines

### Code Standards

- TypeScript strict mode
- ESLint configuration
- Prettier formatting
- Component documentation
- Test coverage

### File Organization

- Feature-based structure
- Consistent naming conventions
- Clear import/export patterns
- Separation of concerns

### Testing Strategy

- Unit tests for components
- Integration tests for pages
- E2E tests for user flows
- Accessibility testing
- Performance testing
