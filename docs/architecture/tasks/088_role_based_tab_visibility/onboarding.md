# Onboarding: Role-Based Tab Visibility Implementation

## **🎯 Task Context**

You are implementing role-based tab visibility for the Personal Assistant TDAH platform. This task ensures that users only see tabs and can make API calls appropriate for their role and permissions.

## **📋 Current System State**

### **RBAC System (✅ Complete)**

The RBAC system is fully implemented with:

- **Roles**: `user`, `premium`, `administrator`
- **Permissions**: Resource-action based (`user:read`, `system:admin`, etc.)
- **Database**: Complete RBAC tables with relationships
- **Backend**: Permission decorators and service working

### **Frontend Current State**

- **Sidebar Navigation**: ✅ Already implements role-based filtering
- **Route Protection**: ✅ Protected routes with role checks
- **Tab Components**: ❌ OAuth Settings tabs show all tabs regardless of role
- **API Calls**: ❌ Frontend doesn't prevent unauthorized API calls

## **🔍 Key Files to Understand**

### **1. RBAC Models** (`src/personal_assistant/database/models/rbac_models.py`)

```python
class Role(Base):
    name: str  # 'user', 'premium', 'administrator'
    description: str
    parent_role_id: int  # Hierarchical roles

class Permission(Base):
    name: str  # 'user:read', 'system:admin'
    resource_type: str  # 'user', 'system', 'rbac'
    action: str  # 'read', 'write', 'admin'

class UserRole(Base):
    user_id: int
    role_id: int
    is_primary: bool
```

### **2. Role Utils** (`src/apps/frontend/src/utils/roleUtils.ts`)

```typescript
// Key functions already implemented:
hasRole(user: User, roleName: string): boolean
isAdmin(user: User): boolean
isPremium(user: User): boolean
hasPermission(user: User, resourceType: string, action: string): boolean
getFilteredNavigationItems(user: User): NavigationItem[]
```

### **3. Tab Components** (`src/apps/frontend/src/components/oauth-settings/`)

- `TabNavigation.tsx` - Currently shows all tabs
- `AnalyticsTab.tsx` - Needs permission check
- `AuditTab.tsx` - Needs permission check
- `SettingsTab.tsx` - Basic user access
- `IntegrationsTab.tsx` - Basic user access

## **🎯 Implementation Strategy**

### **Phase 1: Tab Filtering**

1. **Update TabNavigation.tsx**:

   - Filter tabs based on user permissions
   - Use existing `roleUtils.ts` functions
   - Handle role changes dynamically

2. **Permission Matrix**:
   ```typescript
   const tabPermissions = {
     integrations: () => true, // All users
     analytics: () => isPremium(user) || isAdmin(user),
     audit: () => isAdmin(user),
     settings: () => true, // All users
   };
   ```

### **Phase 2: API Call Protection**

1. **Add Permission Checks**:

   - Check permissions before API calls
   - Handle 403 responses gracefully
   - Show appropriate error messages

2. **API Endpoints to Protect**:
   - `/api/v1/oauth/analytics` - Premium+ only
   - `/api/v1/oauth/audit-logs` - Admin only
   - `/api/v1/analytics/sms` - Premium+ only
   - `/api/v1/analytics/admin` - Admin only

### **Phase 3: Component Updates**

1. **Individual Tab Components**:
   - Add permission checks at component level
   - Show fallback UI for unauthorized access
   - Handle loading states

## **🔧 Technical Implementation**

### **Tab Filtering Pattern**

```typescript
// In TabNavigation.tsx
const getVisibleTabs = (user: User) => {
  return tabs.filter((tab) => {
    switch (tab.id) {
      case "analytics":
        return isPremium(user) || isAdmin(user);
      case "audit":
        return isAdmin(user);
      default:
        return true;
    }
  });
};
```

### **API Call Protection Pattern**

```typescript
// Before making API calls
const canAccessAnalytics = () => {
  return isPremium(user) || isAdmin(user);
};

if (!canAccessAnalytics()) {
  setError("Insufficient permissions");
  return;
}
```

### **Error Handling Pattern**

```typescript
// Handle 403 responses
const handleApiError = (error: any) => {
  if (error.status === 403) {
    setError("You do not have permission to access this feature");
  }
};
```

## **🧪 Testing Strategy**

### **Test Scenarios**

1. **User Role**: Should see only basic tabs
2. **Premium Role**: Should see analytics tabs
3. **Admin Role**: Should see all tabs including audit
4. **Role Changes**: Tabs should update dynamically
5. **API Calls**: Unauthorized calls should be prevented

### **Test Users**

- Create test users with different roles
- Test permission changes in real-time
- Verify API endpoint restrictions

## **📚 Key Concepts**

### **Permission Format**

- `resource_type:action` (e.g., `user:read`, `system:admin`)
- Resource types: `user`, `system`, `rbac`, `analytics`
- Actions: `read`, `write`, `delete`, `admin`

### **Role Hierarchy**

- `administrator` > `premium` > `user`
- Premium inherits user permissions
- Admin inherits all permissions

### **Frontend-Backend Sync**

- Frontend should mirror backend permissions
- Both should use same permission checking logic
- API calls should be protected on both sides

## **🚨 Common Pitfalls**

1. **Permission Mismatch**: Frontend and backend permissions must match
2. **Role Changes**: Handle dynamic role updates
3. **Error Handling**: Don't expose sensitive error details
4. **Performance**: Don't check permissions on every render
5. **User Experience**: Provide clear feedback for access denied

## **🔗 Related Documentation**

- [RBAC System](../032_rbac_system/README.md)
- [Frontend Architecture](../../FRONTEND_ARCHITECTURE_DIAGRAM.md)
- [API Documentation](../../api/rbac.md)
- [Role Utils Implementation](../../../src/apps/frontend/src/utils/roleUtils.ts)

## **🎯 Success Metrics**

- ✅ All tabs show/hide based on user role
- ✅ API calls are protected and handled gracefully
- ✅ No performance impact on page load
- ✅ Clear user feedback for access denied
- ✅ Dynamic updates when role changes
