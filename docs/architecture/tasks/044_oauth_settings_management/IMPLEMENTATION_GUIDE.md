# Task 044: OAuth Settings & Management Interface - Implementation Guide

## 📋 **Implementation Overview**

**Task ID**: 044  
**Phase**: 2.4 - User Interface  
**Component**: 2.4.3.2 - OAuth Settings and Management  
**Status**: 🚀 **READY TO START**  
**Effort**: 1-2 days

## 🎯 **What We're Building**

A comprehensive OAuth settings and management interface that provides users with advanced OAuth integration management capabilities, consuming the already-implemented backend OAuth APIs.

## 🏗️ **Architecture Overview**

### **Component Hierarchy**

```
OAuthSettingsPage/
├── OAuthSettingsPage.tsx          # Main page component
├── components/
│   ├── TabNavigation.tsx          # Settings tab navigation
│   ├── IntegrationsTab.tsx        # Integrations management
│   ├── AnalyticsTab.tsx           # Analytics dashboard
│   ├── AuditTab.tsx               # Audit log viewer
│   └── SettingsTab.tsx            # General OAuth settings
├── services/
│   └── oauthSettingsService.ts    # Enhanced OAuth service
└── stores/
    └── oauthSettingsStore.ts      # OAuth settings state management
```

### **Data Flow**

```
User Action → Component → Service → API → Backend → Response → State Update → UI Update
```

## 🚀 **Phase 1: Foundation Setup**

### **Step 1: Create Task Directory Structure**

```bash
# Navigate to frontend components directory
cd src/apps/frontend/src/components/oauth/

# Create OAuth settings directory
mkdir oauth-settings
cd oauth-settings

# Create component files
touch OAuthSettingsPage.tsx
mkdir components
touch components/TabNavigation.tsx
touch components/IntegrationsTab.tsx
touch components/AnalyticsTab.tsx
touch components/AuditTab.tsx
touch components/SettingsTab.tsx

# Create service and store files
mkdir services
touch services/oauthSettingsService.ts
mkdir stores
touch stores/oauthSettingsStore.ts

# Create types file
touch types.ts
```

### **Step 2: Define TypeScript Interfaces**

```typescript
// types.ts
export interface OAuthSettings {
  autoRefreshTokens: boolean;
  refreshThreshold: number; // minutes before expiration
  notifications: {
    tokenExpiry: boolean;
    syncFailures: boolean;
    securityAlerts: boolean;
  };
  security: {
    requireReauthForRevoke: boolean;
    auditLogRetention: number; // days
  };
}

export interface OAuthIntegration {
  id: number;
  provider: string;
  display_name: string;
  status: "active" | "expired" | "revoked";
  is_active: boolean;
  scopes: string[];
  created_at: string;
  last_sync_at?: string;
  expires_at?: string;
  metadata?: Record<string, any>;
}

export interface OAuthAnalytics {
  integrations: {
    total: number;
    active: number;
    expired: number;
    revoked: number;
  };
  providers: Record<
    string,
    {
      count: number;
      active: number;
      expired: number;
    }
  >;
  usage: {
    total_requests: number;
    successful_requests: number;
    failed_requests: number;
    average_response_time: number;
  };
  trends: {
    daily: Array<{ date: string; requests: number; errors: number }>;
    weekly: Array<{ week: string; integrations: number; syncs: number }>;
  };
}

export interface OAuthAuditLog {
  id: number;
  timestamp: string;
  user_id: number;
  action: string;
  provider: string;
  integration_id?: number;
  details: Record<string, any>;
  ip_address?: string;
  user_agent?: string;
}

export interface AuditFilters {
  dateFrom?: string;
  dateTo?: string;
  provider?: string;
  action?: string;
  user_id?: number;
}
```

### **Step 3: Create Enhanced OAuth Service**

```typescript
// services/oauthSettingsService.ts
import { api } from "../../services/api";
import {
  OAuthSettings,
  OAuthIntegration,
  OAuthAnalytics,
  OAuthAuditLog,
  AuditFilters,
} from "../types";

export class OAuthSettingsService {
  // Existing OAuth methods (from current oauthService)
  async getProviders() {
    const response = await api.get("/oauth/providers");
    return response.data;
  }

  async getIntegrations(params?: { provider?: string; active_only?: boolean }) {
    const response = await api.get("/oauth/integrations", { params });
    return response.data;
  }

  async refreshTokens(integrationId: number) {
    const response = await api.post(
      `/oauth/integrations/${integrationId}/refresh`
    );
    return response.data;
  }

  async revokeIntegration(integrationId: number, reason?: string) {
    const response = await api.delete(`/oauth/integrations/${integrationId}`, {
      data: { reason },
    });
    return response.data;
  }

  async getStatus() {
    const response = await api.get("/oauth/status");
    return response.data;
  }

  async syncIntegrations() {
    const response = await api.post("/oauth/integrations/sync");
    return response.data;
  }

  // New methods for settings management
  async getSettings(): Promise<OAuthSettings> {
    // For now, return default settings
    // In the future, this could fetch from a dedicated settings endpoint
    return {
      autoRefreshTokens: true,
      refreshThreshold: 30,
      notifications: {
        tokenExpiry: true,
        syncFailures: true,
        securityAlerts: true,
      },
      security: {
        requireReauthForRevoke: true,
        auditLogRetention: 90,
      },
    };
  }

  async updateSettings(settings: Partial<OAuthSettings>): Promise<void> {
    // For now, just log the settings update
    // In the future, this could save to a settings endpoint
    console.log("Updating OAuth settings:", settings);
  }

  async getAnalytics(timeRange: string = "7d"): Promise<OAuthAnalytics> {
    // Use existing status endpoint and enhance with time-based data
    const status = await this.getStatus();

    // Transform status data into analytics format
    return {
      integrations: {
        total: status.integrations.total || 0,
        active: status.integrations.active || 0,
        expired: status.integrations.expired || 0,
        revoked: status.integrations.revoked || 0,
      },
      providers: status.integrations.providers || {},
      usage: {
        total_requests: 0, // Would come from analytics endpoint
        successful_requests: 0,
        failed_requests: 0,
        average_response_time: 0,
      },
      trends: {
        daily: [], // Would come from analytics endpoint
        weekly: [],
      },
    };
  }

  async getAuditLogs(filters: AuditFilters = {}): Promise<OAuthAuditLog[]> {
    // For now, return mock audit data
    // In the future, this would come from an audit endpoint
    return [
      {
        id: 1,
        timestamp: new Date().toISOString(),
        user_id: 1,
        action: "integration_created",
        provider: "google",
        integration_id: 1,
        details: { scopes: ["calendar.readonly"] },
        ip_address: "192.168.1.1",
        user_agent: "Mozilla/5.0...",
      },
      // Add more mock audit entries...
    ];
  }

  async exportData(
    format: "csv" | "json",
    filters?: AuditFilters
  ): Promise<string> {
    const data = await this.getAuditLogs(filters);

    if (format === "json") {
      return JSON.stringify(data, null, 2);
    } else {
      // Simple CSV conversion
      const headers = ["ID", "Timestamp", "Action", "Provider", "Details"];
      const rows = data.map((log) => [
        log.id,
        log.timestamp,
        log.action,
        log.provider,
        JSON.stringify(log.details),
      ]);

      return [headers, ...rows]
        .map((row) => row.map((cell) => `"${cell}"`).join(","))
        .join("\n");
    }
  }
}

export const oauthSettingsService = new OAuthSettingsService();
```

### **Step 4: Create OAuth Settings Store**

```typescript
// stores/oauthSettingsStore.ts
import { create } from "zustand";
import { oauthSettingsService } from "../services/oauthSettingsService";
import {
  OAuthSettings,
  OAuthIntegration,
  OAuthAnalytics,
  OAuthAuditLog,
  AuditFilters,
} from "../types";

interface OAuthSettingsStore {
  // State
  settings: OAuthSettings | null;
  integrations: OAuthIntegration[];
  analytics: OAuthAnalytics | null;
  auditLogs: OAuthAuditLog[];
  loading: boolean;
  error: string | null;

  // Actions
  loadSettings: () => Promise<void>;
  updateSettings: (settings: Partial<OAuthSettings>) => Promise<void>;
  loadIntegrations: (params?: {
    provider?: string;
    active_only?: boolean;
  }) => Promise<void>;
  refreshIntegration: (id: number) => Promise<void>;
  revokeIntegration: (id: number, reason?: string) => Promise<void>;
  loadAnalytics: (timeRange?: string) => Promise<void>;
  loadAuditLogs: (filters?: AuditFilters) => Promise<void>;
  exportData: (
    format: "csv" | "json",
    filters?: AuditFilters
  ) => Promise<string>;
  clearError: () => void;
}

export const useOAuthSettingsStore = create<OAuthSettingsStore>((set, get) => ({
  // Initial state
  settings: null,
  integrations: [],
  analytics: null,
  auditLogs: [],
  loading: false,
  error: null,

  // Actions
  loadSettings: async () => {
    try {
      set({ loading: true, error: null });
      const settings = await oauthSettingsService.getSettings();
      set({ settings, loading: false });
    } catch (error) {
      set({
        error:
          error instanceof Error ? error.message : "Failed to load settings",
        loading: false,
      });
    }
  },

  updateSettings: async (settings: Partial<OAuthSettings>) => {
    try {
      set({ loading: true, error: null });
      await oauthSettingsService.updateSettings(settings);

      // Update local state
      const currentSettings = get().settings;
      if (currentSettings) {
        set({
          settings: { ...currentSettings, ...settings },
          loading: false,
        });
      }
    } catch (error) {
      set({
        error:
          error instanceof Error ? error.message : "Failed to update settings",
        loading: false,
      });
    }
  },

  loadIntegrations: async (params) => {
    try {
      set({ loading: true, error: null });
      const integrations = await oauthSettingsService.getIntegrations(params);
      set({ integrations, loading: false });
    } catch (error) {
      set({
        error:
          error instanceof Error
            ? error.message
            : "Failed to load integrations",
        loading: false,
      });
    }
  },

  refreshIntegration: async (id: number) => {
    try {
      set({ loading: true, error: null });
      await oauthSettingsService.refreshTokens(id);

      // Reload integrations to get updated status
      await get().loadIntegrations();
    } catch (error) {
      set({
        error:
          error instanceof Error ? error.message : "Failed to refresh tokens",
        loading: false,
      });
    }
  },

  revokeIntegration: async (id: number, reason?: string) => {
    try {
      set({ loading: true, error: null });
      await oauthSettingsService.revokeIntegration(id, reason);

      // Remove from local state
      const currentIntegrations = get().integrations;
      set({
        integrations: currentIntegrations.filter(
          (integration) => integration.id !== id
        ),
        loading: false,
      });
    } catch (error) {
      set({
        error:
          error instanceof Error
            ? error.message
            : "Failed to revoke integration",
        loading: false,
      });
    }
  },

  loadAnalytics: async (timeRange = "7d") => {
    try {
      set({ loading: true, error: null });
      const analytics = await oauthSettingsService.getAnalytics(timeRange);
      set({ analytics, loading: false });
    } catch (error) {
      set({
        error:
          error instanceof Error ? error.message : "Failed to load analytics",
        loading: false,
      });
    }
  },

  loadAuditLogs: async (filters = {}) => {
    try {
      set({ loading: true, error: null });
      const auditLogs = await oauthSettingsService.getAuditLogs(filters);
      set({ auditLogs, loading: false });
    } catch (error) {
      set({
        error:
          error instanceof Error ? error.message : "Failed to load audit logs",
        loading: false,
      });
    }
  },

  exportData: async (format: "csv" | "json", filters?: AuditFilters) => {
    try {
      set({ loading: true, error: null });
      const data = await oauthSettingsService.exportData(format, filters);
      set({ loading: false });
      return data;
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : "Failed to export data",
        loading: false,
      });
      throw error;
    }
  },

  clearError: () => set({ error: null }),
}));
```

## 🎨 **Phase 2: Component Implementation**

### **Step 5: Create Main OAuth Settings Page**

```typescript
// OAuthSettingsPage.tsx
import React, { useState, useEffect } from "react";
import { TabNavigation } from "./components/TabNavigation";
import { IntegrationsTab } from "./components/IntegrationsTab";
import { AnalyticsTab } from "./components/AnalyticsTab";
import { AuditTab } from "./components/AuditTab";
import { SettingsTab } from "./components/SettingsTab";
import { useOAuthSettingsStore } from "./stores/oauthSettingsStore";

export const OAuthSettingsPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState("integrations");
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

    // Load tab-specific data
    switch (tab) {
      case "analytics":
        loadAnalytics();
        break;
      case "audit":
        loadAuditLogs();
        break;
      default:
        break;
    }
  };

  const renderTabContent = () => {
    switch (activeTab) {
      case "integrations":
        return <IntegrationsTab />;
      case "analytics":
        return <AnalyticsTab />;
      case "audit":
        return <AuditTab />;
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
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        {/* Page Header */}
        <div className="px-4 py-6 sm:px-0">
          <div className="border-b border-gray-200 pb-4">
            <h1 className="text-3xl font-bold text-gray-900">
              OAuth Settings & Management
            </h1>
            <p className="mt-2 text-sm text-gray-600">
              Manage your OAuth integrations, monitor performance, and configure
              security settings.
            </p>
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div className="mb-6 px-4 sm:px-0">
            <div className="bg-red-50 border border-red-200 rounded-md p-4">
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
                  <h3 className="text-sm font-medium text-red-800">
                    Error loading OAuth settings
                  </h3>
                  <div className="mt-2 text-sm text-red-700">{error}</div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Tab Navigation */}
        <TabNavigation activeTab={activeTab} onTabChange={handleTabChange} />

        {/* Tab Content */}
        <div className="mt-6">{renderTabContent()}</div>
      </div>
    </div>
  );
};
```

### **Step 6: Create Tab Navigation Component**

```typescript
// components/TabNavigation.tsx
import React from "react";

interface TabNavigationProps {
  activeTab: string;
  onTabChange: (tab: string) => void;
}

const tabs = [
  { id: "integrations", name: "Integrations", icon: "🔗" },
  { id: "analytics", name: "Analytics", icon: "📊" },
  { id: "audit", name: "Audit Logs", icon: "📋" },
  { id: "settings", name: "Settings", icon: "⚙️" },
];

export const TabNavigation: React.FC<TabNavigationProps> = ({
  activeTab,
  onTabChange,
}) => {
  return (
    <div className="border-b border-gray-200">
      <nav className="-mb-px flex space-x-8 px-4 sm:px-0">
        {tabs.map((tab) => (
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

### **Step 7: Create Integrations Tab Component**

```typescript
// components/IntegrationsTab.tsx
import React, { useState } from "react";
import { useOAuthSettingsStore } from "../stores/oauthSettingsStore";
import { OAuthIntegration } from "../types";

export const IntegrationsTab: React.FC = () => {
  const { integrations, loading, refreshIntegration, revokeIntegration } =
    useOAuthSettingsStore();

  const [selectedIntegrations, setSelectedIntegrations] = useState<number[]>(
    []
  );
  const [showRevokeDialog, setShowRevokeDialog] = useState<number | null>(null);
  const [revokeReason, setRevokeReason] = useState("");

  const handleSelectIntegration = (integrationId: number) => {
    setSelectedIntegrations((prev) =>
      prev.includes(integrationId)
        ? prev.filter((id) => id !== integrationId)
        : [...prev, integrationId]
    );
  };

  const handleSelectAll = () => {
    if (selectedIntegrations.length === integrations.length) {
      setSelectedIntegrations([]);
    } else {
      setSelectedIntegrations(integrations.map((i) => i.id));
    }
  };

  const handleBulkRefresh = async () => {
    for (const integrationId of selectedIntegrations) {
      await refreshIntegration(integrationId);
    }
    setSelectedIntegrations([]);
  };

  const handleBulkRevoke = async () => {
    for (const integrationId of selectedIntegrations) {
      await revokeIntegration(integrationId, "Bulk revocation");
    }
    setSelectedIntegrations([]);
  };

  const handleRevoke = async (integrationId: number) => {
    await revokeIntegration(integrationId, revokeReason);
    setShowRevokeDialog(null);
    setRevokeReason("");
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "active":
        return "bg-green-100 text-green-800";
      case "expired":
        return "bg-yellow-100 text-yellow-800";
      case "revoked":
        return "bg-red-100 text-red-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="px-4 sm:px-0">
      {/* Bulk Actions */}
      {selectedIntegrations.length > 0 && (
        <div className="mb-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <span className="text-sm text-blue-800">
              {selectedIntegrations.length} integration(s) selected
            </span>
            <div className="flex space-x-3">
              <button
                onClick={handleBulkRefresh}
                className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-blue-700 bg-blue-100 hover:bg-blue-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                🔄 Refresh All
              </button>
              <button
                onClick={handleBulkRevoke}
                className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-red-700 bg-red-100 hover:bg-red-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
              >
                🗑️ Revoke All
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Integrations Table */}
      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        <div className="px-4 py-5 sm:px-6 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h3 className="text-lg leading-6 font-medium text-gray-900">
              OAuth Integrations
            </h3>
            <div className="flex items-center space-x-3">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={
                    selectedIntegrations.length === integrations.length &&
                    integrations.length > 0
                  }
                  onChange={handleSelectAll}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="ml-2 text-sm text-gray-700">Select All</span>
              </label>
            </div>
          </div>
        </div>

        <ul className="divide-y divide-gray-200">
          {integrations.map((integration) => (
            <li key={integration.id} className="px-4 py-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    checked={selectedIntegrations.includes(integration.id)}
                    onChange={() => handleSelectIntegration(integration.id)}
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500 mr-3"
                  />

                  <div className="flex-shrink-0">
                    <div className="h-10 w-10 rounded-full bg-gray-300 flex items-center justify-center">
                      <span className="text-lg">
                        {integration.provider.charAt(0).toUpperCase()}
                      </span>
                    </div>
                  </div>

                  <div className="ml-4">
                    <div className="flex items-center">
                      <p className="text-sm font-medium text-gray-900">
                        {integration.display_name || integration.provider}
                      </p>
                      <span
                        className={`ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(
                          integration.status
                        )}`}
                      >
                        {integration.status}
                      </span>
                    </div>
                    <div className="mt-1 flex items-center text-sm text-gray-500">
                      <span>Provider: {integration.provider}</span>
                      <span className="mx-2">•</span>
                      <span>Scopes: {integration.scopes.join(", ")}</span>
                      <span className="mx-2">•</span>
                      <span>
                        Created:{" "}
                        {new Date(integration.created_at).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => refreshIntegration(integration.id)}
                    className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                  >
                    🔄 Refresh
                  </button>
                  <button
                    onClick={() => setShowRevokeDialog(integration.id)}
                    className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-red-700 bg-red-100 hover:bg-red-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                  >
                    🗑️ Revoke
                  </button>
                </div>
              </div>
            </li>
          ))}
        </ul>
      </div>

      {/* Revoke Confirmation Dialog */}
      {showRevokeDialog && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                Revoke OAuth Integration
              </h3>
              <p className="text-sm text-gray-500 mb-4">
                Are you sure you want to revoke this OAuth integration? This
                action cannot be undone.
              </p>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Reason (optional)
                </label>
                <textarea
                  value={revokeReason}
                  onChange={(e) => setRevokeReason(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  rows={3}
                  placeholder="Enter reason for revocation..."
                />
              </div>
              <div className="flex justify-end space-x-3">
                <button
                  onClick={() => setShowRevokeDialog(null)}
                  className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  onClick={() => handleRevoke(showRevokeDialog)}
                  className="px-4 py-2 border border-transparent rounded-md text-sm font-medium text-white bg-red-600 hover:bg-red-700"
                >
                  Revoke
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
```

## 📊 **Phase 3: Analytics & Advanced Features**

### **Step 8: Create Analytics Tab Component**

```typescript
// components/AnalyticsTab.tsx
import React, { useState } from "react";
import { useOAuthSettingsStore } from "../stores/oauthSettingsStore";

const timeRanges = [
  { value: "1d", label: "Last 24 Hours" },
  { value: "7d", label: "Last 7 Days" },
  { value: "30d", label: "Last 30 Days" },
  { value: "90d", label: "Last 90 Days" },
];

export const AnalyticsTab: React.FC = () => {
  const { analytics, loading, loadAnalytics } = useOAuthSettingsStore();
  const [timeRange, setTimeRange] = useState("7d");

  React.useEffect(() => {
    loadAnalytics(timeRange);
  }, [timeRange, loadAnalytics]);

  const handleTimeRangeChange = (newTimeRange: string) => {
    setTimeRange(newTimeRange);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
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

  return (
    <div className="px-4 sm:px-0">
      {/* Time Range Selector */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Time Range
        </label>
        <div className="flex space-x-2">
          {timeRanges.map((range) => (
            <button
              key={range.value}
              onClick={() => handleTimeRangeChange(range.value)}
              className={`px-3 py-2 text-sm font-medium rounded-md ${
                timeRange === range.value
                  ? "bg-blue-100 text-blue-700 border border-blue-300"
                  : "bg-white text-gray-700 border border-gray-300 hover:bg-gray-50"
              }`}
            >
              {range.label}
            </button>
          ))}
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-blue-500 rounded-md flex items-center justify-center">
                  <span className="text-white text-sm font-bold">🔗</span>
                </div>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Total Integrations
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {analytics.integrations.total}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-green-500 rounded-md flex items-center justify-center">
                  <span className="text-white text-sm font-bold">✅</span>
                </div>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Active Integrations
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {analytics.integrations.active}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-yellow-500 rounded-md flex items-center justify-center">
                  <span className="text-white text-sm font-bold">⚠️</span>
                </div>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Expired Integrations
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {analytics.integrations.expired}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-red-500 rounded-md flex items-center justify-center">
                  <span className="text-white text-sm font-bold">❌</span>
                </div>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Revoked Integrations
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {analytics.integrations.revoked}
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Provider Distribution */}
      <div className="bg-white shadow rounded-lg mb-8">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
            Provider Distribution
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {Object.entries(analytics.providers).map(([provider, stats]) => (
              <div key={provider} className="text-center">
                <div className="text-2xl font-bold text-gray-900">
                  {stats.count}
                </div>
                <div className="text-sm text-gray-500 capitalize">
                  {provider}
                </div>
                <div className="text-xs text-gray-400">
                  {stats.active} active, {stats.expired} expired
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Usage Metrics */}
      {analytics.usage && (
        <div className="bg-white shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
              Usage Metrics
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900">
                  {analytics.usage.total_requests}
                </div>
                <div className="text-sm text-gray-500">Total Requests</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">
                  {analytics.usage.successful_requests}
                </div>
                <div className="text-sm text-gray-500">Successful</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-red-600">
                  {analytics.usage.failed_requests}
                </div>
                <div className="text-sm text-gray-500">Failed</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">
                  {analytics.usage.average_response_time}ms
                </div>
                <div className="text-sm text-gray-500">Avg Response</div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
```

## 🔧 **Phase 4: Integration & Testing**

### **Step 9: Add Route to Dashboard Navigation**

```typescript
// In your dashboard navigation configuration
const dashboardRoutes = [
  // ... existing routes
  {
    path: "/dashboard/oauth/settings",
    element: <OAuthSettingsPage />,
    label: "OAuth Settings",
    icon: "oauth-settings",
    description: "Manage OAuth integrations and settings",
  },
  // ... other routes
];
```

### **Step 10: Create Remaining Tab Components**

You'll need to create the `AuditTab.tsx` and `SettingsTab.tsx` components following similar patterns. Here's a basic structure for the Audit Tab:

```typescript
// components/AuditTab.tsx
import React, { useState } from "react";
import { useOAuthSettingsStore } from "../stores/oauthSettingsStore";
import { AuditFilters } from "../types";

export const AuditTab: React.FC = () => {
  const { auditLogs, loading, loadAuditLogs, exportData } =
    useOAuthSettingsStore();
  const [filters, setFilters] = useState<AuditFilters>({});
  const [exportFormat, setExportFormat] = useState<"csv" | "json">("csv");

  const handleExport = async () => {
    try {
      const data = await exportData(exportFormat, filters);

      // Create and download file
      const blob = new Blob([data], {
        type: exportFormat === "csv" ? "text/csv" : "application/json",
      });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `oauth-audit-${
        new Date().toISOString().split("T")[0]
      }.${exportFormat}`;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error("Export failed:", error);
    }
  };

  // ... rest of component implementation
};
```

## 🧪 **Testing Implementation**

### **Step 11: Create Unit Tests**

```typescript
// __tests__/OAuthSettingsPage.test.tsx
import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { OAuthSettingsPage } from "../OAuthSettingsPage";
import { useOAuthSettingsStore } from "../stores/oauthSettingsStore";

// Mock the store
jest.mock("../stores/oauthSettingsStore");

describe("OAuthSettingsPage", () => {
  const mockStore = {
    loadSettings: jest.fn(),
    loadIntegrations: jest.fn(),
    loadAnalytics: jest.fn(),
    loadAuditLogs: jest.fn(),
    loading: false,
    error: null,
  };

  beforeEach(() => {
    (useOAuthSettingsStore as jest.Mock).mockReturnValue(mockStore);
  });

  it("renders OAuth settings page", () => {
    render(<OAuthSettingsPage />);
    expect(screen.getByText("OAuth Settings & Management")).toBeInTheDocument();
  });

  it("loads initial data on mount", () => {
    render(<OAuthSettingsPage />);
    expect(mockStore.loadSettings).toHaveBeenCalled();
    expect(mockStore.loadIntegrations).toHaveBeenCalled();
  });

  // Add more tests...
});
```

## 🚀 **Deployment & Final Steps**

### **Step 12: Final Integration**

1. **Import Components**: Ensure all components are properly imported in your main app
2. **Route Configuration**: Add the OAuth settings route to your dashboard navigation
3. **Styling**: Apply your design system classes and ensure consistency
4. **Error Handling**: Test error scenarios and edge cases
5. **Mobile Testing**: Verify responsive design on different screen sizes

### **Step 13: Performance Optimization**

1. **Lazy Loading**: Implement lazy loading for analytics data
2. **Memoization**: Use React.memo and useMemo for expensive operations
3. **Debouncing**: Add debouncing for search and filter inputs
4. **Pagination**: Implement pagination for large datasets

### **Step 14: Documentation**

1. **Component Documentation**: Document all component props and usage
2. **API Integration**: Document how the frontend consumes backend APIs
3. **User Guide**: Create user documentation for the OAuth settings interface
4. **Troubleshooting**: Document common issues and solutions

---

## 🎯 **Success Criteria**

- [ ] Users can access OAuth settings page from dashboard
- [ ] All existing OAuth APIs are properly consumed
- [ ] Token refresh functionality works correctly
- [ ] Integration deactivation is functional
- [ ] Analytics data is displayed accurately
- [ ] Export functionality works as expected
- [ ] Mobile responsive design implemented
- [ ] Accessibility compliance achieved

## 📚 **Additional Resources**

- **React Documentation**: https://react.dev/
- **TypeScript Handbook**: https://www.typescriptlang.org/docs/
- **Tailwind CSS**: https://tailwindcss.com/docs
- **Zustand**: https://github.com/pmndrs/zustand

---

**Task 044 is ready for implementation!** 🚀

This guide provides a comprehensive foundation for building the OAuth settings and management interface. Follow the phases step-by-step, and you'll have a fully functional OAuth management system that integrates seamlessly with your existing backend APIs.
