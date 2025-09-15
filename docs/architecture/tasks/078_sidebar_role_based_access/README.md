# Task 078: Implement Role-Based Access Control for Sidebar Navigation

## Overview

This task implements proper role-based access control for the sidebar navigation, ensuring that users only see menu items they have permission to access. Currently, all users see admin-only features like "Admin Analytics" regardless of their role.

## Problem

The sidebar shows all navigation items to all users, including admin-only features. This creates confusion and poor user experience when users see features they cannot access.

## Solution

Implement role-based filtering for sidebar navigation items and add route protection for admin-only features.

## Files to Modify

### Backend

- `src/apps/fastapi_app/routes/users.py` - Add user roles endpoint
- `src/apps/fastapi_app/models/users.py` - Extend user response model

### Frontend

- `src/apps/frontend/src/stores/authStore.ts` - Add roles/permissions to state
- `src/apps/frontend/src/components/dashboard/Sidebar.tsx` - Filter navigation items
- `src/apps/frontend/src/components/navigation/NavigationMenu.tsx` - Handle filtered items
- `src/apps/frontend/src/App.tsx` - Add route protection

### New Files

- `src/apps/frontend/src/services/permissionService.ts` - Permission checking utility
- `src/apps/frontend/src/components/auth/RoleBasedRoute.tsx` - Route protection component
- `src/apps/frontend/src/types/rbac.ts` - RBAC type definitions

## Implementation Steps

1. **Backend API Enhancement**

   - Create `GET /users/me/roles` endpoint
   - Extend user response with roles and permissions
   - Add permission caching for performance

2. **Frontend State Management**

   - Add roles/permissions to auth store
   - Create permission service utility
   - Add permission checking methods

3. **Navigation Filtering**

   - Update sidebar to filter items by permissions
   - Hide unauthorized navigation items
   - Maintain navigation structure

4. **Route Protection**

   - Create role-based route guard component
   - Protect admin routes from unauthorized access
   - Add fallback for unauthorized users

5. **Testing**
   - Test with different user roles
   - Verify navigation filtering works
   - Test route protection

## Permission Mapping

```typescript
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

## Acceptance Criteria

- [ ] Sidebar only shows items user has access to
- [ ] Admin-only items hidden from non-admin users
- [ ] Unauthorized users cannot access protected routes
- [ ] User roles/permissions available throughout app
- [ ] Navigation updates when user roles change
- [ ] Proper error handling for permission checks

## Dependencies

- Backend RBAC system (✅ Complete)
- Permission service (✅ Working)
- Frontend auth store (✅ Existing)

## Estimated Time

3-5 hours

## Priority

Medium - Improves user experience and security
