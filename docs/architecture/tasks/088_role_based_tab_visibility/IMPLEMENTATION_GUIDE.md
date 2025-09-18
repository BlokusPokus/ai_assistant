# 🔐 Role-Based Tab Visibility - Implementation Guide

## **🎯 Overview**

This guide provides step-by-step instructions for implementing role-based tab visibility in the frontend, ensuring users only see tabs and can make API calls appropriate for their role and permissions.

## **📋 Prerequisites**

- ✅ RBAC system implemented (Task 032)
- ✅ Frontend role utilities available (`roleUtils.ts`)
- ✅ Backend API protection in place
- ✅ User authentication working

## **🚀 Implementation Steps**

### **Step 1: Update TabNavigation Component**

**File**: `src/apps/frontend/src/components/oauth-settings/components/TabNavigation.tsx`

```typescript
import React from "react";
import { useAuthStore } from "../../../stores/authStore";
import { isPremium, isAdmin } from "../../../utils/roleUtils";

interface TabNavigationProps {
  activeTab: string;
  onTabChange: (tab: string) => void;
}

// Define tabs with their permission requirements
const allTabs = [
  { id: "integrations", name: "Integrations", icon: "🔗", requiredRole: null },
  { id: "analytics", name: "Analytics", icon: "📊", requiredRole: "premium" },
  {
    id: "audit",
    name: "Audit Logs",
    icon: "📋",
    requiredRole: "administrator",
  },
  { id: "settings", name: "Settings", icon: "⚙️", requiredRole: null },
];

export const TabNavigation: React.FC<TabNavigationProps> = ({
  activeTab,
  onTabChange,
}) => {
  const { user } = useAuthStore();

  // Filter tabs based on user permissions
  const getVisibleTabs = () => {
    if (!user) return allTabs;

    return allTabs.filter((tab) => {
      switch (tab.requiredRole) {
        case "premium":
          return isPremium(user);
        case "administrator":
          return isAdmin(user);
        case null:
        case undefined:
          return true; // Public tabs
        default:
          return false;
      }
    });
  };

  const visibleTabs = getVisibleTabs();

  // If current active tab is not visible, switch to first visible tab
  React.useEffect(() => {
    if (user && !visibleTabs.find((tab) => tab.id === activeTab)) {
      onTabChange(visibleTabs[0]?.id || "integrations");
    }
  }, [user, visibleTabs, activeTab, onTabChange]);

  return (
    <div className="border-b border-gray-200">
      <nav className="-mb-px flex space-x-8 px-4 sm:px-0">
        {visibleTabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => onTabChange(tab.id)}
            className={`
              whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm
              ${
                activeTab === tab.id
                  ? "border-blue-500 text-blue-600"
                  : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
              }
            `}
          >
            <span className="mr-2">{tab.icon}</span>
            {tab.name}
          </button>
        ))}
      </nav>
    </div>
  );
};
```

### **Step 2: Update OAuthSettingsPage Component**

**File**: `src/apps/frontend/src/components/oauth-settings/OAuthSettingsPage.tsx`

```typescript
import React, { useState, useEffect } from "react";
import { TabNavigation } from "./components/TabNavigation";
import { IntegrationsTab } from "./components/IntegrationsTab";
import { AnalyticsTab } from "./components/AnalyticsTab";
import { AuditTab } from "./components/AuditTab";
import { SettingsTab } from "./components/SettingsTab";
import { useOAuthSettingsStore } from "../../stores/oauthSettingsStore";
import { useAuthStore } from "../../stores/authStore";
import { isPremium, isAdmin } from "../../utils/roleUtils";

export const OAuthSettingsPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState("integrations");
  const { user } = useAuthStore();
  const {
    loadSettings,
    loadIntegrations,
    loadAnalytics,
    loadAuditLogs,
    loading,
    error,
  } = useOAuthSettingsStore();

  useEffect(() => {
    // Load initial data
    loadSettings();
    loadIntegrations();
  }, [loadSettings, loadIntegrations]);

  const handleTabChange = (tab: string) => {
    setActiveTab(tab);

    // Load tab-specific data with permission checks
    switch (tab) {
      case "analytics":
        if (isPremium(user) || isAdmin(user)) {
          loadAnalytics();
        }
        break;
      case "audit":
        if (isAdmin(user)) {
          loadAuditLogs();
        }
        break;
      default:
        break;
    }
  };

  const renderTabContent = () => {
    // Check permissions before rendering tabs
    switch (activeTab) {
      case "integrations":
        return <IntegrationsTab />;
      case "analytics":
        if (isPremium(user) || isAdmin(user)) {
          return <AnalyticsTab />;
        }
        return <AccessDeniedTab feature="Analytics" requiredRole="Premium" />;
      case "audit":
        if (isAdmin(user)) {
          return <AuditTab />;
        }
        return (
          <AccessDeniedTab feature="Audit Logs" requiredRole="Administrator" />
        );
      case "settings":
        return <SettingsTab />;
      default:
        return <IntegrationsTab />;
    }
  };

  if (loading && !activeTab) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">OAuth Settings</h1>
        <p className="mt-2 text-gray-600">
          Manage your OAuth integrations and settings
        </p>
      </div>

      {error && (
        <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg
                className="h-5 w-5 text-red-400"
                viewBox="0 0 20 20"
                fill="currentColor"
              >
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                  clipRule="evenodd"
                />
              </svg>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">Error</h3>
              <div className="mt-2 text-sm text-red-700">
                <p>{error}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      <TabNavigation activeTab={activeTab} onTabChange={handleTabChange} />

      <div className="mt-6">{renderTabContent()}</div>
    </div>
  );
};

// Access Denied Component
const AccessDeniedTab: React.FC<{ feature: string; requiredRole: string }> = ({
  feature,
  requiredRole,
}) => (
  <div className="text-center py-12">
    <div className="mx-auto h-12 w-12 text-gray-400">
      <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
        />
      </svg>
    </div>
    <h3 className="mt-2 text-sm font-medium text-gray-900">Access Denied</h3>
    <p className="mt-1 text-sm text-gray-500">
      You need {requiredRole} access to view {feature}.
    </p>
  </div>
);
```

### **Step 3: Update AnalyticsTab Component**

**File**: `src/apps/frontend/src/components/oauth-settings/components/AnalyticsTab.tsx`

```typescript
import React, { useState, useEffect } from "react";
import { useOAuthSettingsStore } from "../../../stores/oauthSettingsStore";
import { useAuthStore } from "../../../stores/authStore";
import { isPremium, isAdmin } from "../../../utils/roleUtils";
import { Select } from "@/components/ui";

const timeRanges = [
  { value: "1d", label: "Last 24 Hours" },
  { value: "7d", label: "Last 7 Days" },
  { value: "30d", label: "Last 30 Days" },
  { value: "90d", label: "Last 90 Days" },
];

export const AnalyticsTab: React.FC = () => {
  const { user } = useAuthStore();
  const { analytics, loading, loadAnalytics } = useOAuthSettingsStore();
  const [timeRange, setTimeRange] = useState("7d");
  const [error, setError] = useState<string | null>(null);

  // Check permissions before loading data
  useEffect(() => {
    if (!isPremium(user) && !isAdmin(user)) {
      setError("Insufficient permissions to view analytics");
      return;
    }

    loadAnalytics().catch((err) => {
      if (err.status === 403) {
        setError("You do not have permission to access analytics data");
      } else {
        setError("Failed to load analytics data");
      }
    });
  }, [loadAnalytics, user]);

  const handleTimeRangeChange = (newTimeRange: string) => {
    setTimeRange(newTimeRange);
  };

  // Show access denied if user doesn't have permission
  if (!isPremium(user) && !isAdmin(user)) {
    return (
      <div className="text-center py-12">
        <div className="mx-auto h-12 w-12 text-gray-400">
          <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
            />
          </svg>
        </div>
        <h3 className="mt-2 text-sm font-medium text-gray-900">
          Access Denied
        </h3>
        <p className="mt-1 text-sm text-gray-500">
          You need Premium access to view analytics.
        </p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-accent"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <div className="mx-auto h-12 w-12 text-red-400">
          <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
        </div>
        <h3 className="mt-2 text-sm font-medium text-gray-900">Error</h3>
        <p className="mt-1 text-sm text-gray-500">{error}</p>
      </div>
    );
  }

  if (!analytics) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">No analytics data available</p>
      </div>
    );
  }

  // Rest of the component remains the same...
  return <div className="px-4 sm:px-0">{/* Existing analytics content */}</div>;
};
```

### **Step 4: Update AuditTab Component**

**File**: `src/apps/frontend/src/components/oauth-settings/components/AuditTab.tsx`

```typescript
import React, { useState } from "react";
import { useOAuthSettingsStore } from "../../../stores/oauthSettingsStore";
import { useAuthStore } from "../../../stores/authStore";
import { isAdmin } from "../../../utils/roleUtils";
import type { AuditFilters } from "../../../services/oauthSettingsService";
import { Select } from "@/components/ui";

export const AuditTab: React.FC = () => {
  const { user } = useAuthStore();
  const { auditLogs, loading, loadAuditLogs, exportData } =
    useOAuthSettingsStore();
  const [filters, setFilters] = useState<AuditFilters>({});
  const [exportFormat, setExportFormat] = useState<"csv" | "json">("csv");
  const [error, setError] = useState<string | null>(null);

  // Check permissions before loading data
  React.useEffect(() => {
    if (!isAdmin(user)) {
      setError("Insufficient permissions to view audit logs");
      return;
    }

    loadAuditLogs().catch((err) => {
      if (err.status === 403) {
        setError("You do not have permission to access audit logs");
      } else {
        setError("Failed to load audit logs");
      }
    });
  }, [loadAuditLogs, user]);

  const handleExport = async () => {
    if (!isAdmin(user)) {
      setError("Insufficient permissions to export audit logs");
      return;
    }

    try {
      const data = await exportData(exportFormat, filters);
      // Existing export logic...
    } catch (error) {
      if (error.status === 403) {
        setError("You do not have permission to export audit logs");
      } else {
        console.error("Export failed:", error);
        setError("Export failed");
      }
    }
  };

  // Show access denied if user doesn't have permission
  if (!isAdmin(user)) {
    return (
      <div className="text-center py-12">
        <div className="mx-auto h-12 w-12 text-gray-400">
          <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
            />
          </svg>
        </div>
        <h3 className="mt-2 text-sm font-medium text-gray-900">
          Access Denied
        </h3>
        <p className="mt-1 text-sm text-gray-500">
          You need Administrator access to view audit logs.
        </p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <div className="mx-auto h-12 w-12 text-red-400">
          <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
        </div>
        <h3 className="mt-2 text-sm font-medium text-gray-900">Error</h3>
        <p className="mt-1 text-sm text-gray-500">{error}</p>
      </div>
    );
  }

  // Rest of the component remains the same...
  return <div className="px-4 sm:px-0">{/* Existing audit content */}</div>;
};
```

### **Step 5: Update SMS Analytics Page**

**File**: `src/apps/frontend/src/pages/dashboard/SMSAnalyticsPage.tsx`

```typescript
import React, { useState, useEffect } from "react";
import { useAuthStore } from "../../stores/authStore";
import { isPremium, isAdmin } from "../../utils/roleUtils";
import { SMSAnalyticsPanel } from "../../components/admin/SMSAnalyticsPanel";

export const SMSAnalyticsPage: React.FC = () => {
  const { user } = useAuthStore();
  const [error, setError] = useState<string | null>(null);

  // Check permissions
  useEffect(() => {
    if (!isPremium(user) && !isAdmin(user)) {
      setError("Insufficient permissions to view SMS analytics");
    }
  }, [user]);

  // Show access denied if user doesn't have permission
  if (!isPremium(user) && !isAdmin(user)) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="text-center py-12">
          <div className="mx-auto h-12 w-12 text-gray-400">
            <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
              />
            </svg>
          </div>
          <h3 className="mt-2 text-sm font-medium text-gray-900">
            Access Denied
          </h3>
          <p className="mt-1 text-sm text-gray-500">
            You need Premium access to view SMS analytics.
          </p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="text-center py-12">
          <div className="mx-auto h-12 w-12 text-red-400">
            <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          </div>
          <h3 className="mt-2 text-sm font-medium text-gray-900">Error</h3>
          <p className="mt-1 text-sm text-gray-500">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">SMS Analytics</h1>
        <p className="mt-2 text-gray-600">
          View and analyze your SMS usage and performance
        </p>
      </div>

      <SMSAnalyticsPanel />
    </div>
  );
};
```

### **Step 6: Update Admin Analytics Page**

**File**: `src/apps/frontend/src/pages/dashboard/AdminAnalyticsPage.tsx`

```typescript
import React, { useState, useEffect } from "react";
import { useAuthStore } from "../../stores/authStore";
import { isAdmin } from "../../utils/roleUtils";

export const AdminAnalyticsPage: React.FC = () => {
  const { user } = useAuthStore();
  const [error, setError] = useState<string | null>(null);

  // Check permissions
  useEffect(() => {
    if (!isAdmin(user)) {
      setError("Insufficient permissions to view admin analytics");
    }
  }, [user]);

  // Show access denied if user doesn't have permission
  if (!isAdmin(user)) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="text-center py-12">
          <div className="mx-auto h-12 w-12 text-gray-400">
            <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
              />
            </svg>
          </div>
          <h3 className="mt-2 text-sm font-medium text-gray-900">
            Access Denied
          </h3>
          <p className="mt-1 text-sm text-gray-500">
            You need Administrator access to view admin analytics.
          </p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="text-center py-12">
          <div className="mx-auto h-12 w-12 text-red-400">
            <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          </div>
          <h3 className="mt-2 text-sm font-medium text-gray-900">Error</h3>
          <p className="mt-1 text-sm text-gray-500">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Admin Analytics</h1>
        <p className="mt-2 text-gray-600">
          System-wide analytics and monitoring
        </p>
      </div>

      {/* Admin analytics content */}
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-lg font-medium text-gray-900 mb-4">
          System Overview
        </h2>
        <p className="text-gray-600">
          Admin analytics content will be implemented here.
        </p>
      </div>
    </div>
  );
};
```

### **Step 7: Extend Role Utils (Optional)**

**File**: `src/apps/frontend/src/utils/roleUtils.ts`

Add new utility functions if needed:

```typescript
/**
 * Check if user can access OAuth analytics
 */
export function canAccessOAuthAnalytics(user: User): boolean {
  return isPremium(user) || isAdmin(user);
}

/**
 * Check if user can access audit logs
 */
export function canAccessAuditLogs(user: User): boolean {
  return isAdmin(user);
}

/**
 * Check if user can access SMS analytics
 */
export function canAccessSMSAnalytics(user: User): boolean {
  return isPremium(user) || isAdmin(user);
}

/**
 * Check if user can access admin analytics
 */
export function canAccessAdminAnalytics(user: User): boolean {
  return isAdmin(user);
}
```

## **🧪 Testing**

### **Test Cases**

1. **User Role Test**:

   - Login as user role
   - Verify only basic tabs are visible
   - Verify API calls are blocked for restricted endpoints

2. **Premium Role Test**:

   - Login as premium role
   - Verify analytics tabs are visible
   - Verify SMS analytics is accessible

3. **Admin Role Test**:

   - Login as admin role
   - Verify all tabs are visible
   - Verify all features are accessible

4. **Role Change Test**:
   - Change user role dynamically
   - Verify tabs update in real-time
   - Verify API access changes

### **Manual Testing Steps**

1. **Create Test Users**:

   ```sql
   -- Create users with different roles
   INSERT INTO users (email, password_hash, is_active) VALUES
   ('user@test.com', 'hash', true),
   ('premium@test.com', 'hash', true),
   ('admin@test.com', 'hash', true);

   -- Assign roles
   INSERT INTO user_roles (user_id, role_id, is_primary) VALUES
   (1, 1, true), -- user role
   (2, 2, true), -- premium role
   (3, 3, true); -- admin role
   ```

2. **Test Tab Visibility**:

   - Login as each user type
   - Navigate to OAuth Settings
   - Verify correct tabs are visible

3. **Test API Protection**:
   - Try to access restricted endpoints
   - Verify 403 responses are handled gracefully

## **✅ Completion Checklist**

- [ ] TabNavigation component updated with role filtering
- [ ] OAuthSettingsPage updated with permission checks
- [ ] AnalyticsTab updated with permission validation
- [ ] AuditTab updated with permission validation
- [ ] SMSAnalyticsPage updated with permission checks
- [ ] AdminAnalyticsPage updated with permission checks
- [ ] Error handling implemented for all components
- [ ] Access denied UI implemented
- [ ] Testing completed with all user roles
- [ ] Performance verified (no impact on load times)

## **🚨 Common Issues & Solutions**

### **Issue 1: Tabs Not Updating on Role Change**

**Solution**: Ensure `useEffect` dependencies include user object and implement proper re-rendering.

### **Issue 2: API Calls Still Made Despite Permission Check**

**Solution**: Add permission checks before making API calls, not just in error handling.

### **Issue 3: Performance Issues**

**Solution**: Memoize permission checks and avoid checking on every render.

### **Issue 4: Inconsistent Permission Logic**

**Solution**: Use centralized permission functions from `roleUtils.ts` consistently.

## **📚 References**

- [RBAC System Documentation](../032_rbac_system/README.md)
- [Frontend Architecture](../../FRONTEND_ARCHITECTURE_DIAGRAM.md)
- [Role Utils Implementation](../../../src/apps/frontend/src/utils/roleUtils.ts)
