# Task 042: OAuth Settings and Management

## 📋 **Quick Summary**

**Task 042** extends the existing OAuth Connection UI (Task 041) with a comprehensive settings and management interface. This task provides users with advanced OAuth management capabilities including centralized configuration, token management, integration controls, usage analytics, and security settings.

**Status**: 🚀 **READY TO START**  
**Effort**: 2 days  
**Dependencies**: Task 041 ✅ **COMPLETED**

**Key Deliverables**:

- OAuth Settings Page with tabbed navigation
- Token Management & Security Controls
- Integration Controls with bulk operations
- Analytics Dashboard with usage metrics
- Security & Compliance settings

---

## 📋 **Task Overview**

**Task ID**: 042  
**Phase**: 2.4 - User Interface Development  
**Component**: 2.4.3 - OAuth Integration UI  
**Status**: 🚀 **READY TO START**  
**Effort**: 2 days  
**Dependencies**: Task 2.4.3.1 ✅ **COMPLETED** (Task 041)

## 🎯 **Objective**

Extend the existing OAuth Connection UI (Task 041) with a comprehensive settings and management interface that provides users with advanced OAuth management capabilities, including centralized configuration, token management, integration controls, usage analytics, and security settings.

## 📊 **Current System State**

### ✅ **What's Already Implemented (Task 041)**

- **OAuth Types & Interfaces**: Complete TypeScript definitions for OAuth integrations
- **OAuth Store**: Zustand-based state management with comprehensive OAuth state
- **OAuth Service Layer**: API integration ready for backend OAuth services
- **Core OAuth Components**: Provider cards, status indicators, consent management, main manager
- **Dashboard Integration**: OAuth integrations page with sidebar navigation
- **Mobile-Responsive Design**: Touch-optimized interface for all device types
- **Comprehensive Testing**: 21 tests passing with 100% success rate

### 🚀 **What Needs to be Built (Task 042)**

- **OAuth Settings Page**: Advanced configuration interface with tabbed navigation
- **Token Management Components**: Automatic and manual token refresh controls
- **Integration Management**: Bulk operations, scope modification, secure deactivation
- **Analytics Dashboard**: Usage statistics, cost tracking, performance monitoring
- **Security Controls**: Advanced security settings, compliance features, audit logging

## 🏗️ **Technical Requirements**

### **Frontend Architecture**

```
src/
├── components/
│   ├── oauth/                    # EXISTING: Core OAuth components (Task 041)
│   │   ├── OAuthManager.tsx      # ✅ COMPLETED: Main OAuth interface
│   │   ├── OAuthProviderCard.tsx # ✅ COMPLETED: Provider selection cards
│   │   ├── OAuthStatus.tsx       # ✅ COMPLETED: Connection status indicators
│   │   ├── OAuthConsent.tsx      # ✅ COMPLETED: Scope and consent UI
│   │   └── OAuthIntegrationsPage.tsx # ✅ COMPLETED: Page wrapper
│   └── oauth-settings/           # NEW: OAuth settings components
│       ├── OAuthSettingsPage.tsx # Main settings page with tabbed interface
│       ├── GeneralSettings.tsx   # Basic OAuth preferences and defaults
│       ├── TokenManagement.tsx   # Token refresh and security controls
│       ├── IntegrationControls.tsx # Bulk operations and scope management
│       ├── OAuthAnalytics.tsx    # Usage analytics and cost tracking
│       └── SecuritySettings.tsx  # Security and compliance controls
├── stores/
│   ├── oauthStore.ts             # ✅ COMPLETED: OAuth state management
│   └── oauthSettingsStore.ts     # NEW: Settings-specific state management
├── services/
│   ├── oauthService.ts           # ✅ COMPLETED: OAuth API integration
│   └── oauthSettingsService.ts   # NEW: Settings API integration
├── types/
│   ├── oauth.ts                  # ✅ COMPLETED: OAuth type definitions
│   └── oauthSettings.ts          # NEW: Settings-specific types
└── pages/
    └── dashboard/
        ├── integrations.tsx       # ✅ COMPLETED: OAuth integrations page
        └── oauth-settings.tsx    # NEW: OAuth settings page
```

### **OAuth Settings Categories**

1. **General Settings**

   - Default scope preferences per provider
   - Auto-refresh settings and intervals
   - Notification preferences
   - Language and regional settings

2. **Token Management**

   - Token refresh intervals and automation
   - Expiration warnings and notifications
   - Security token storage preferences
   - Manual refresh controls and monitoring

3. **Integration Controls**

   - Bulk operations (connect/disconnect multiple providers)
   - Scope modification for existing integrations
   - Integration deactivation and access revocation
   - Integration health monitoring

4. **Analytics & Monitoring**

   - Usage statistics per provider
   - Cost tracking and billing information
   - Performance metrics and response times
   - Error reporting and troubleshooting

5. **Security & Compliance**
   - Token encryption settings
   - Audit logging preferences
   - GDPR compliance controls
   - Security notifications and alerts

## 📱 **UI/UX Requirements**

### **OAuth Settings Page Design**

- **Layout**: Tabbed interface with logical grouping of related settings
- **Navigation**: Breadcrumb navigation from OAuth integrations page
- **Responsive Design**: Mobile-first approach with touch optimization
- **Accessibility**: WCAG 2.1 AA compliance for all settings
- **Consistency**: Matches existing OAuth interface design language

### **Settings Interface Patterns**

- **Progressive Disclosure**: Show basic settings first, advanced options on demand
- **Smart Defaults**: Pre-configure sensible defaults based on best practices
- **Real-time Validation**: Immediate feedback on setting changes
- **Confirmation Dialogs**: Require confirmation for destructive actions
- **Loading States**: Clear feedback during operations

### **Mobile Experience**

- **Touch Optimization**: Adequate touch targets and gesture support
- **Simplified Interface**: Streamlined mobile settings with essential options
- **Responsive Layout**: Adapt to different screen sizes and orientations
- **Offline Support**: Cache settings for offline access

## 🔧 **Technical Implementation**

### **State Management Extensions**

#### **OAuth Settings Store**

```typescript
interface OAuthSettingsState {
  // General settings
  defaultScopes: Record<string, string[]>;
  autoRefresh: boolean;
  refreshInterval: number;
  notifications: NotificationPreferences;
  language: string;
  timezone: string;

  // Token management
  tokenSecurity: TokenSecuritySettings;
  refreshSettings: RefreshSettings;
  expirationWarnings: ExpirationWarningSettings;

  // Analytics
  usageStats: UsageStatistics;
  costMetrics: CostMetrics;
  performanceMetrics: PerformanceMetrics;

  // Security
  securitySettings: SecuritySettings;
  complianceSettings: ComplianceSettings;
  auditLogging: AuditLoggingSettings;
}

interface OAuthSettingsActions {
  // Settings management
  updateGeneralSettings: (settings: Partial<GeneralSettings>) => void;
  updateTokenSettings: (settings: Partial<TokenSettings>) => void;
  updateSecuritySettings: (settings: Partial<SecuritySettings>) => void;

  // Token operations
  refreshAllTokens: () => Promise<void>;
  refreshProviderTokens: (provider: string) => Promise<void>;
  revokeAccess: (provider: string) => Promise<void>;

  // Analytics
  loadUsageStats: (timeframe: Timeframe) => Promise<void>;
  exportAnalytics: (format: "csv" | "json") => Promise<void>;

  // Bulk operations
  bulkConnect: (
    providers: string[],
    scopes: Record<string, string[]>
  ) => Promise<void>;
  bulkDisconnect: (providers: string[]) => Promise<void>;
  bulkUpdateScopes: (updates: Record<string, string[]>) => Promise<void>;
}
```

#### **OAuth Settings Service**

```typescript
class OAuthSettingsService {
  // Settings management
  async getSettings(): Promise<OAuthSettings>;
  async updateSettings(settings: Partial<OAuthSettings>): Promise<void>;
  async resetToDefaults(): Promise<void>;

  // Token management
  async refreshTokens(provider?: string): Promise<void>;
  async revokeAccess(provider: string): Promise<void>;
  async getTokenStatus(provider: string): Promise<TokenStatus>;

  // Analytics
  async getUsageStats(timeframe: Timeframe): Promise<UsageStatistics>;
  async getCostMetrics(timeframe: Timeframe): Promise<CostMetrics>;
  async getPerformanceMetrics(): Promise<PerformanceMetrics>;
  async exportAnalytics(format: ExportFormat): Promise<Blob>;

  // Security
  async getSecurityLogs(): Promise<SecurityLog[]>;
  async exportComplianceReport(): Promise<ComplianceReport>;
  async getAuditTrail(): Promise<AuditLog[]>;

  // Bulk operations
  async bulkConnect(
    providers: string[],
    scopes: Record<string, string[]>
  ): Promise<void>;
  async bulkDisconnect(providers: string[]): Promise<void>;
  async bulkUpdateScopes(updates: Record<string, string[]>): Promise<void>;
}
```

### **Component Implementation**

#### **OAuth Settings Page**

```typescript
const OAuthSettingsPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState("general");
  const { settings, isLoading, updateSettings } = useOAuthSettingsStore();

  const tabs = [
    { id: "general", label: "General", icon: "⚙️" },
    { id: "tokens", label: "Tokens", icon: "🔑" },
    { id: "integrations", label: "Integrations", icon: "🔗" },
    { id: "analytics", label: "Analytics", icon: "📊" },
    { id: "security", label: "Security", icon: "🛡️" },
  ];

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <nav className="flex items-center space-x-2 text-sm text-gray-500 mb-4">
          <Link to="/dashboard" className="hover:text-gray-700">
            Dashboard
          </Link>
          <span>/</span>
          <Link to="/dashboard/integrations" className="hover:text-gray-700">
            Integrations
          </Link>
          <span>/</span>
          <span className="text-gray-900">Settings</span>
        </nav>

        <h1 className="text-3xl font-bold text-gray-900">OAuth Settings</h1>
        <p className="text-gray-600 mt-2">
          Configure your OAuth integrations, manage tokens, and monitor usage.
        </p>
      </div>

      {/* Settings Tabs */}
      <div className="bg-white rounded-lg shadow">
        <TabGroup selectedIndex={tabIndex} onChange={setTabIndex}>
          <TabList className="flex space-x-1 rounded-t-lg bg-gray-50 p-1">
            {tabs.map((tab) => (
              <Tab
                key={tab.id}
                className={({ selected }) =>
                  `flex items-center space-x-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                    selected
                      ? "bg-white text-blue-600 shadow-sm"
                      : "text-gray-600 hover:text-gray-900"
                  }`
                }
              >
                <span>{tab.icon}</span>
                <span>{tab.label}</span>
              </Tab>
            ))}
          </TabList>

          <TabPanels className="p-6">
            <TabPanel>
              <GeneralSettings />
            </TabPanel>
            <TabPanel>
              <TokenManagement />
            </TabPanel>
            <TabPanel>
              <IntegrationControls />
            </TabPanel>
            <TabPanel>
              <OAuthAnalytics />
            </TabPanel>
            <TabPanel>
              <SecuritySettings />
            </TabPanel>
          </TabPanels>
        </TabGroup>
      </div>
    </div>
  );
};
```

#### **General Settings Component**

```typescript
const GeneralSettings: React.FC = () => {
  const { settings, updateGeneralSettings } = useOAuthSettingsStore();
  const [formData, setFormData] = useState(settings.general);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await updateGeneralSettings(formData);
      toast.success("Settings updated successfully");
    } catch (error) {
      toast.error("Failed to update settings");
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Default Scopes */}
      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-4">
          Default Scopes
        </h3>
        <div className="space-y-4">
          {Object.entries(OAUTH_PROVIDERS).map(([provider, config]) => (
            <div key={provider} className="border rounded-lg p-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                {config.name} Default Scopes
              </label>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                {config.availableScopes.map((scope) => (
                  <label key={scope} className="flex items-center">
                    <input
                      type="checkbox"
                      checked={
                        formData.defaultScopes[provider]?.includes(scope) ||
                        false
                      }
                      onChange={(e) => {
                        const current = formData.defaultScopes[provider] || [];
                        const updated = e.target.checked
                          ? [...current, scope]
                          : current.filter((s) => s !== scope);
                        setFormData({
                          ...formData,
                          defaultScopes: {
                            ...formData.defaultScopes,
                            [provider]: updated,
                          },
                        });
                      }}
                      className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                    <span className="ml-2 text-sm text-gray-700">{scope}</span>
                  </label>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Auto-refresh Settings */}
      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-4">
          Token Auto-refresh
        </h3>
        <div className="space-y-4">
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={formData.autoRefresh}
              onChange={(e) =>
                setFormData({ ...formData, autoRefresh: e.target.checked })
              }
              className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span className="ml-2 text-sm text-gray-700">
              Enable automatic token refresh
            </span>
          </label>

          {formData.autoRefresh && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Refresh Interval (minutes)
              </label>
              <input
                type="number"
                min="5"
                max="1440"
                value={formData.refreshInterval}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    refreshInterval: parseInt(e.target.value),
                  })
                }
                className="w-32 rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              />
            </div>
          )}
        </div>
      </div>

      {/* Submit Button */}
      <div className="flex justify-end">
        <Button type="submit" variant="primary">
          Save Settings
        </Button>
      </div>
    </form>
  );
};
```

## 🧪 **Testing Strategy**

### **Test Coverage Requirements**

- **Unit Tests**: All new components, stores, and services
- **Integration Tests**: Settings store and service integration
- **Component Tests**: Settings page and sub-components
- **E2E Tests**: Complete settings workflow and user interactions

### **Test Scenarios**

1. **Settings Management**

   - Load and save settings successfully
   - Form validation and error handling
   - Settings persistence and retrieval

2. **Token Operations**

   - Token refresh functionality
   - Access revocation and security
   - Bulk token operations

3. **Analytics Display**

   - Data loading and visualization
   - Export functionality
   - Performance metrics display

4. **Security Features**
   - Settings validation and security
   - Compliance checks and reporting
   - Audit logging and monitoring

### **Test Files Structure**

```
src/
├── components/
│   └── oauth-settings/
│       └── __tests__/
│           ├── OAuthSettingsPage.test.tsx
│           ├── GeneralSettings.test.tsx
│           ├── TokenManagement.test.tsx
│           ├── IntegrationControls.test.tsx
│           ├── OAuthAnalytics.test.tsx
│           └── SecuritySettings.test.tsx
├── stores/
│   └── __tests__/
│       └── oauthSettingsStore.test.ts
└── services/
    └── __tests__/
        └── oauthSettingsService.test.ts
```

## 📊 **Success Metrics**

### **Functional Requirements**

- ✅ Users can configure all OAuth settings categories
- ✅ Token management operations work correctly
- ✅ Integration controls are fully functional
- ✅ Analytics display accurate and useful information
- ✅ Security settings are properly enforced and validated

### **Performance Requirements**

- **Load Time**: Settings page loads in < 2 seconds
- **Response Time**: Settings updates apply in < 1 second
- **Analytics**: Usage data loads in < 3 seconds
- **Token Operations**: Refresh/revoke completes in < 2 seconds
- **Bulk Operations**: Handle up to 10 providers simultaneously

### **User Experience Requirements**

- **Intuitive Interface**: Users can find and configure settings without help
- **Clear Feedback**: All actions provide immediate visual feedback
- **Consistent Design**: Matches existing OAuth interface design language
- **Mobile Optimization**: Touch-friendly interface on all device types
- **Accessibility**: WCAG 2.1 AA compliance for all settings

## 🚨 **Risks & Mitigation**

### **Technical Risks**

- **State Complexity**: Settings store may become complex with many options
  - **Mitigation**: Use modular store design with clear separation of concerns
- **API Integration**: Backend OAuth services not yet available
  - **Mitigation**: Create comprehensive mock services for development and testing
- **Performance**: Analytics and bulk operations may impact page performance
  - **Mitigation**: Implement lazy loading, data virtualization, and progressive enhancement

### **User Experience Risks**

- **Settings Overwhelm**: Too many options may confuse users
  - **Mitigation**: Use progressive disclosure, smart defaults, and contextual help
- **Mobile Complexity**: Complex settings on mobile devices
  - **Mitigation**: Mobile-first design with simplified mobile interface and essential options

### **Security Risks**

- **Token Exposure**: Sensitive token information in settings
  - **Mitigation**: Mask sensitive data, implement proper access controls
- **Bulk Operations**: Potential for accidental bulk changes
  - **Mitigation**: Require confirmation for destructive operations, implement undo functionality

## 📋 **Implementation Plan**

### **Phase 1: Foundation (Day 1 - Morning)**

1. **Create OAuth Settings Types**

   - Define `OAuthSettings` interfaces and types
   - Extend existing OAuth types for settings
   - Create settings-specific type definitions

2. **Implement OAuth Settings Store**

   - Create `oauthSettingsStore.ts` with Zustand
   - Implement state management for all settings categories
   - Add actions for settings operations and bulk operations

3. **Create OAuth Settings Service**
   - Implement `oauthSettingsService.ts`
   - Add mock methods for development and testing
   - Prepare service layer for backend integration

### **Phase 2: Core Components (Day 1 - Afternoon)**

1. **Build Settings Page Structure**

   - Create `OAuthSettingsPage.tsx` with tabbed navigation
   - Implement responsive layout and breadcrumb navigation
   - Add loading states and error handling

2. **Implement General Settings**

   - Create `GeneralSettings.tsx` component
   - Add form controls for basic OAuth preferences
   - Implement validation, error handling, and form submission

3. **Build Token Management**
   - Create `TokenManagement.tsx` component
   - Add token refresh controls and security settings
   - Implement token status monitoring and expiration warnings

### **Phase 3: Advanced Features (Day 2 - Morning)**

1. **Create Integration Controls**

   - Build `IntegrationControls.tsx` component
   - Add bulk operations (connect/disconnect multiple providers)
   - Implement scope modification and integration health monitoring

2. **Implement Analytics Dashboard**

   - Create `OAuthAnalytics.tsx` component
   - Add usage statistics display and cost tracking
   - Implement performance metrics and export functionality

3. **Build Security Settings**
   - Create `SecuritySettings.tsx` component
   - Add compliance controls and audit logging
   - Implement security notifications and GDPR compliance

### **Phase 4: Integration & Polish (Day 2 - Afternoon)**

1. **Dashboard Integration**

   - Add OAuth settings page to dashboard routing
   - Update sidebar navigation and breadcrumbs
   - Integrate with existing OAuth components and navigation

2. **Testing & Documentation**

   - Write comprehensive tests for all components
   - Update component documentation and usage examples
   - Test responsive design and mobile experience

3. **Final Polish**
   - Error handling improvements and user feedback
   - Loading state optimization and performance
   - Accessibility enhancements and keyboard navigation

## 🔍 **Quality Gates**

### **Phase 1 Quality Gate**

- [ ] All OAuth settings types are properly defined with TypeScript
- [ ] Settings store manages state correctly with proper actions
- [ ] Settings service integrates with existing API client architecture
- [ ] Basic component structure and routing are in place

### **Phase 2 Quality Gate**

- [ ] Settings page renders correctly with tabbed navigation
- [ ] General settings form works properly with validation
- [ ] Token management functionality is implemented and functional
- [ ] Component tests pass with >90% coverage

### **Phase 3 Quality Gate**

- [ ] Integration controls are functional with bulk operations
- [ ] Analytics display works correctly with real-time data
- [ ] Security settings are properly implemented and validated
- [ ] All components are responsive and mobile-optimized

### **Phase 4 Quality Gate**

- [ ] Settings page is fully integrated into dashboard
- [ ] All tests pass with >90% coverage
- [ ] Mobile experience is optimized and touch-friendly
- [ ] Documentation is complete and up-to-date

## 📚 **Resources & References**

### **Existing Code & Patterns**

- **OAuth Components**: `src/components/oauth/` (Task 041 implementation)
- **OAuth Store**: `src/stores/oauthStore.ts` (Task 041 state management)
- **OAuth Service**: `src/services/oauthService.ts` (Task 041 API integration)
- **OAuth Types**: `src/types/oauth.ts` (Task 041 type definitions)
- **UI Components**: `src/components/ui/` (Existing component library)

### **Design Patterns & Standards**

- **Component Structure**: Follow existing OAuth component patterns from Task 041
- **State Management**: Extend Zustand store pattern established in Task 041
- **Service Layer**: Use existing service architecture and API client patterns
- **UI Components**: Leverage existing UI component library and design system
- **Testing**: Follow testing patterns established in Task 041

### **OAuth Standards & Best Practices**

- **RFC 6749**: OAuth 2.0 Authorization Framework
- **OpenID Connect**: Identity layer on top of OAuth 2.0
- **OAuth 2.0 Threat Model**: Security considerations and best practices
- **OAuth 2.0 Security Best Practices**: Token management and security guidelines

## 🚀 **Getting Started**

### **Immediate Actions**

1. **Review Task 041 Implementation**: Understand existing OAuth components and patterns
2. **Examine OAuth Types**: Review `src/types/oauth.ts` for extension points
3. **Study OAuth Store**: Analyze `src/stores/oauthStore.ts` for store patterns
4. **Review UI Components**: Understand existing component library usage and patterns

### **Development Setup**

```bash
# Navigate to frontend directory
cd src/apps/frontend

# Start development server
npm run dev

# Run tests
npm run test:run

# Build for production
npm run build
```

### **File Creation Order**

1. **Types**: `src/types/oauthSettings.ts` - Settings-specific type definitions
2. **Store**: `src/stores/oauthSettingsStore.ts` - Settings state management
3. **Service**: `src/services/oauthSettingsService.ts` - Settings API integration
4. **Components**: `src/components/oauth-settings/` directory with all sub-components
5. **Page**: `src/pages/dashboard/oauth-settings.tsx` - Main settings page
6. **Routing**: Update dashboard routing configuration and navigation

### **Development Workflow**

1. **Start with Types**: Define all interfaces and types first
2. **Build Store**: Implement state management with mock data
3. **Create Service**: Build service layer with mock methods
4. **Develop Components**: Build components incrementally with testing
5. **Integration**: Integrate with existing dashboard and OAuth components
6. **Testing**: Comprehensive testing at each phase
7. **Polish**: Final improvements and documentation

## 🎯 **Definition of Done**

### **Code Quality**

- ✅ All components are properly typed with TypeScript
- ✅ Components follow existing design patterns from Task 041
- ✅ Code is properly documented with JSDoc comments
- ✅ No console errors or warnings in development or production

### **Functionality**

- ✅ All OAuth settings categories can be configured
- ✅ Token management operations work correctly and securely
- ✅ Integration controls are functional with bulk operations
- ✅ Analytics display accurate and useful information
- ✅ Security settings are properly enforced and validated

### **Testing**

- ✅ Unit tests pass with >90% coverage for all new code
- ✅ Component tests pass consistently for all settings components
- ✅ Integration tests verify store-service interaction
- ✅ E2E tests validate complete settings workflow

### **User Experience**

- ✅ Settings page is intuitive and easy to navigate
- ✅ All actions provide clear and immediate feedback
- ✅ Design is consistent with existing OAuth interface from Task 041
- ✅ Mobile experience is optimized and touch-friendly
- ✅ Accessibility requirements are met (WCAG 2.1 AA)

### **Integration**

- ✅ Settings page is fully integrated into dashboard routing
- ✅ Sidebar navigation includes OAuth settings link
- ✅ Breadcrumb navigation works correctly
- ✅ Integration with existing OAuth components is seamless

---

**Task Owner**: Frontend Development Team  
**Reviewer**: Architecture Team  
**Due Date**: 2 days from start  
**Priority**: High (Required for complete OAuth management interface)

**Status**: 🚀 **READY TO START**

**Next Steps**: Begin Phase 1 - Foundation setup with OAuth settings types and store implementation.

**Dependencies**: Task 041 (OAuth Connection UI) must be completed before starting this task.
