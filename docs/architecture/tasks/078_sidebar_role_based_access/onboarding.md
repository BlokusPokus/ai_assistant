# Sidebar Role-Based Access Control - Onboarding

## Task Context

**Task ID**: 078  
**Task Name**: Implement Role-Based Access Control for Sidebar Navigation  
**Priority**: Medium  
**Estimated Time**: 3-5 hours

## Problem Statement

The sidebar navigation currently shows all menu items to all users regardless of their role or permissions. This includes admin-only features like "Admin Analytics" that should only be visible to users with administrator privileges. Users without admin access see navigation items they cannot use, creating confusion and a poor user experience.

## Current State Analysis

### Backend RBAC Implementation ✅

- **Complete RBAC System**: `src/personal_assistant/database/migrations/002_add_rbac_system.sql`

  - Roles: `user`, `premium`, `administrator`
  - Permissions: Granular permissions for resources and actions
  - User-Role associations with audit trail
  - Access audit logging

- **Permission Service**: `src/personal_assistant/auth/permission_service.py`

  - Role-based permission checking
  - Hierarchical role inheritance
  - Audit logging for access decisions

- **API Endpoints**: `src/apps/fastapi_app/routes/rbac.py`

  - Role management endpoints
  - Permission checking endpoints
  - User role assignment endpoints

- **Decorators**: `src/personal_assistant/auth/decorators.py`
  - `@require_permission(resource, action)`
  - `@require_role(role_name)`
  - `@require_admin()` - requires administrator role

### Frontend Issues ❌

- **No Role-Based Filtering**: Sidebar shows all items to all users
- **No Permission Checking**: Frontend doesn't check user roles/permissions
- **Admin Items Visible**: "Admin Analytics" visible to non-admin users
- **No Role Context**: User roles not available in frontend state

### Current Sidebar Structure (`src/apps/frontend/src/components/dashboard/Sidebar.tsx`)

```typescript
const navigationItems = [
  { label: "Dashboard", href: "/dashboard", icon: Brain },
  { label: "Chat", href: "/dashboard/chat", icon: MessageSquare },
  { label: "Calendar", href: "/dashboard/calendar", icon: Calendar },
  { label: "Notes", href: "/dashboard/notes", icon: FileText },
  { label: "Integrations", href: "/dashboard/integrations", icon: Link },
  { label: "Phone Number", href: "/dashboard/phone-management", icon: Phone },
  { label: "OAuth Settings", href: "/dashboard/oauth-settings", icon: Key },
  { label: "SMS Analytics", href: "/dashboard/sms-analytics", icon: BarChart3 },
  {
    label: "Admin Analytics",
    href: "/dashboard/admin-analytics",
    icon: Shield,
  }, // ❌ Admin only
  { label: "Profile", href: "/dashboard/profile", icon: User },
  { label: "Settings", href: "/dashboard/settings", icon: Settings },
  { label: "Security", href: "/dashboard/security", icon: Shield },
];
```

### User Authentication State (`src/apps/frontend/src/stores/authStore.ts`)

- **Current User Data**: Basic user info (id, email, full_name, etc.)
- **Missing Role Data**: No roles or permissions in user state
- **No Permission Context**: Frontend can't check user permissions

## Technical Requirements

### Backend API Integration

- **User Roles Endpoint**: Need endpoint to get current user's roles and permissions
- **Permission Checking**: Frontend needs to check specific permissions
- **Role Context**: User roles must be available in frontend state

### Frontend Changes Needed

1. **Extend User State**: Add roles and permissions to auth store
2. **Permission Service**: Create frontend permission checking utility
3. **Navigation Filtering**: Filter sidebar items based on user permissions
4. **Route Protection**: Protect admin routes from unauthorized access
5. **Role-Based UI**: Show/hide UI elements based on user roles

### Permission Mapping

```typescript
// Navigation items and required permissions
const navigationPermissions = {
  Dashboard: ["user:read"],
  Chat: ["user:read"],
  Calendar: ["event:read"],
  Notes: ["note:read"],
  Integrations: ["user:read"],
  "Phone Number": ["user:read"],
  "OAuth Settings": ["user:write"],
  "SMS Analytics": ["user:read"],
  "Admin Analytics": ["system:admin"], // Admin only
  Profile: ["user:read"],
  Settings: ["user:write"],
  Security: ["user:write"],
};
```

## Implementation Plan

### Phase 1: Backend API Enhancement

1. **Create User Roles Endpoint**: `GET /users/me/roles`

   - Return user's roles and permissions
   - Include role hierarchy information
   - Cache permissions for performance

2. **Extend User Response Model**: Add roles and permissions to user data
   - Update `UserResponse` model
   - Include permission list in auth responses

### Phase 2: Frontend State Management

1. **Extend Auth Store**: Add roles and permissions to user state

   - Update `AuthState` interface
   - Store roles/permissions after login
   - Add permission checking methods

2. **Create Permission Service**: `src/apps/frontend/src/services/permissionService.ts`
   - `hasPermission(resource, action)` method
   - `hasRole(roleName)` method
   - `hasAnyRole(roleNames)` method
   - `canAccessRoute(routePath)` method

### Phase 3: Navigation Filtering

1. **Update Sidebar Component**: Filter navigation items based on permissions

   - Add permission checking to navigation items
   - Hide items user doesn't have access to
   - Show role-based indicators

2. **Update Navigation Menu**: Pass filtered items to navigation component
   - Remove unauthorized items
   - Maintain navigation structure

### Phase 4: Route Protection

1. **Create Role-Based Route Guard**: `src/apps/frontend/src/components/auth/RoleBasedRoute.tsx`

   - Check user permissions before rendering
   - Redirect unauthorized users
   - Show access denied message

2. **Update App Routes**: Protect admin routes
   - Wrap admin routes with role-based protection
   - Add fallback for unauthorized access

### Phase 5: Testing & Validation

1. **Test with Different Roles**: Verify navigation filtering
2. **Test Route Protection**: Ensure unauthorized access is blocked
3. **Test Permission Changes**: Verify UI updates with role changes

## Dependencies

### Backend Dependencies ✅

- RBAC system is fully implemented
- Permission service is working
- Role-based decorators are available

### Frontend Dependencies

- Existing auth store pattern
- React Router for route protection
- Existing UI components

## Success Criteria

1. **Role-Based Navigation**: Sidebar only shows items user has access to
2. **Admin Protection**: Admin-only items hidden from non-admin users
3. **Route Security**: Unauthorized users cannot access protected routes
4. **Permission Context**: User roles/permissions available throughout app
5. **Dynamic Updates**: Navigation updates when user roles change

## Risk Assessment

### Low Risk

- Backend RBAC is complete and tested
- Frontend changes are isolated to navigation components
- No breaking changes to existing functionality

### Medium Risk

- Permission checking performance
- Complex role hierarchy handling
- Route protection edge cases

### Mitigation

- Cache permissions in frontend state
- Use efficient permission checking algorithms
- Add comprehensive error handling
- Test thoroughly with different role combinations

## Questions for Clarification

1. Should we implement granular permission checking or just role-based filtering?
2. Do we need to show role indicators in the UI (e.g., "Admin" badge)?
3. Should we implement permission caching or check on every navigation?
4. Do we need to handle role changes during user session?

## Next Steps

1. Create user roles API endpoint
2. Extend frontend auth state with roles/permissions
3. Implement permission service
4. Update sidebar with role-based filtering
5. Add route protection for admin features
6. Test with different user roles

---

**Note**: This task focuses on implementing role-based access control for the sidebar navigation. The backend RBAC system is already complete and functional.
