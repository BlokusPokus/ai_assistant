/**
 * Role and Permission utility functions for RBAC
 */

import type { User } from '@/types';

/**
 * Check if user has a specific role
 */
export function hasRole(user: User | null, roleName: string): boolean {
  if (!user || !user.roles) return false;
  return user.roles.some(role => role.name === roleName);
}

/**
 * Check if user has administrator role
 */
export function isAdmin(user: User | null): boolean {
  return hasRole(user, 'administrator');
}

/**
 * Check if user has premium role
 */
export function isPremium(user: User | null): boolean {
  return hasRole(user, 'premium') || isAdmin(user);
}

/**
 * Check if user has a specific permission
 */
export function hasPermission(
  user: User | null,
  resourceType: string,
  action: string
): boolean {
  if (!user || !user.permissions) return false;
  return user.permissions.some(
    permission =>
      permission.resource_type === resourceType && permission.action === action
  );
}

/**
 * Check if user has any of the specified permissions
 */
export function hasAnyPermission(
  user: User,
  permissions: Array<{ resourceType: string; action: string }>
): boolean {
  return permissions.some(perm =>
    hasPermission(user, perm.resourceType, perm.action)
  );
}

/**
 * Check if user has all of the specified permissions
 */
export function hasAllPermissions(
  user: User,
  permissions: Array<{ resourceType: string; action: string }>
): boolean {
  return permissions.every(perm =>
    hasPermission(user, perm.resourceType, perm.action)
  );
}

/**
 * Get user's primary role name
 */
export function getPrimaryRoleName(user: User): string {
  return user.primary_role?.name || user.roles?.[0]?.name || 'user';
}

/**
 * Get all role names for a user
 */
export function getRoleNames(user: User): string[] {
  return user.roles?.map(role => role.name) || [];
}

/**
 * Check if user can access admin features
 */
export function canAccessAdminFeatures(user: User): boolean {
  return (
    hasPermission(user, 'system', 'admin') ||
    hasPermission(user, 'rbac', 'admin') ||
    isAdmin(user)
  );
}

/**
 * Check if user can access SMS analytics
 */
export function canAccessSMSAnalytics(user: User): boolean {
  return (
    hasPermission(user, 'system', 'view_sms_analytics') ||
    hasPermission(user, 'user', 'read_sms_analytics') ||
    isAdmin(user)
  );
}

/**
 * Check if user can access OAuth settings
 */
export function canAccessOAuthSettings(user: User): boolean {
  return (
    hasPermission(user, 'system', 'write') ||
    hasPermission(user, 'user', 'write') ||
    isPremium(user) ||
    hasRole(user, 'user') // Basic users can access OAuth settings
  );
}

/**
 * Check if user can access integrations
 */
export function canAccessIntegrations(user: User): boolean {
  return (
    hasPermission(user, 'system', 'write') ||
    hasPermission(user, 'user', 'write') ||
    isPremium(user) ||
    hasRole(user, 'user') // Basic users can access integrations
  );
}

/**
 * Get dashboard navigation items based on user permissions
 * Note: This function returns the navigation items without icons.
 * The icons should be handled in the component that uses this function.
 */
export function getFilteredNavigationItems(user: User | null) {
  const allItems = [
    {
      label: 'Dashboard',
      href: '/dashboard',
      requiredRole: null,
    },
    {
      label: 'Chat',
      href: '/dashboard/chat',
      requiredRole: null,
    },
    {
      label: 'Calendar',
      href: '/dashboard/calendar',
      requiredRole: null,
    },
    {
      label: 'Notes',
      href: '/dashboard/notes',
      requiredRole: null,
    },
    {
      label: 'Phone Number',
      href: '/dashboard/phone-management',
      requiredRole: null,
    },
    {
      label: 'Profile',
      href: '/dashboard/profile',
      requiredRole: null,
    },
    {
      label: 'Settings',
      href: '/dashboard/settings',
      requiredRole: null,
    },
    {
      label: 'Security',
      href: '/dashboard/security',
      requiredRole: null,
    },

    // Available to all users
    {
      label: 'Integrations',
      href: '/dashboard/integrations',
      requiredRole: null,
    },
    {
      label: 'OAuth Settings',
      href: '/dashboard/oauth-settings',
      requiredRole: null,
    },
    {
      label: 'SMS Analytics',
      href: '/dashboard/sms-analytics',
      requiredRole: 'premium',
    },

    // Admin-only features
    {
      label: 'Admin Analytics',
      href: '/dashboard/admin-analytics',
      requiredRole: 'administrator',
    },
  ];

  return allItems.filter(item => {
    if (!item.requiredRole) return true; // Public items

    switch (item.requiredRole) {
      case 'premium':
        return isPremium(user);
      case 'administrator':
        return isAdmin(user);
      default:
        return hasRole(user, item.requiredRole);
    }
  });
}

/**
 * Check if user can access a specific route
 */
export function canAccessRoute(user: User, route: string): boolean {
  const routePermissions: Record<string, () => boolean> = {
    '/dashboard/admin-analytics': () => isAdmin(user),
    '/dashboard/sms-analytics': () => canAccessSMSAnalytics(user),
    '/dashboard/oauth-settings': () => canAccessOAuthSettings(user),
    '/dashboard/integrations': () => canAccessIntegrations(user),
  };

  const permissionCheck = routePermissions[route];
  return permissionCheck ? permissionCheck() : true; // Default to true for public routes
}
