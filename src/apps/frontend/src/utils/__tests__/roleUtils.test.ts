import { describe, it, expect } from 'vitest';
import {
  hasRole,
  isAdmin,
  isPremium,
  hasPermission,
  getFilteredNavigationItems,
} from '../roleUtils';

// Mock user data for testing
const mockUser = {
  id: 1,
  email: 'test@example.com',
  roles: [
    { id: 1, name: 'user' },
    { id: 2, name: 'premium' },
  ],
  permissions: [
    { id: 1, resource_type: 'user', action: 'read' },
    { id: 2, resource_type: 'user', action: 'write' },
    { id: 3, resource_type: 'system', action: 'read' },
  ],
};

const mockAdminUser = {
  id: 2,
  email: 'admin@example.com',
  roles: [
    { id: 1, name: 'user' },
    { id: 2, name: 'premium' },
    { id: 3, name: 'administrator' },
  ],
  permissions: [
    { id: 1, resource_type: 'user', action: 'read' },
    { id: 2, resource_type: 'user', action: 'write' },
    { id: 3, resource_type: 'system', action: 'read' },
    { id: 4, resource_type: 'system', action: 'admin' },
    { id: 5, resource_type: 'rbac', action: 'read' },
  ],
};

const mockBasicUser = {
  id: 3,
  email: 'basic@example.com',
  roles: [{ id: 1, name: 'user' }],
  permissions: [
    { id: 1, resource_type: 'user', action: 'read' },
    { id: 2, resource_type: 'user', action: 'write' },
  ],
};

describe('roleUtils', () => {
  describe('hasRole', () => {
    it('returns true when user has the specified role', () => {
      expect(hasRole(mockUser, 'premium')).toBe(true);
      expect(hasRole(mockUser, 'user')).toBe(true);
    });

    it('returns false when user does not have the specified role', () => {
      expect(hasRole(mockUser, 'administrator')).toBe(false);
    });

    it('returns false when user has no roles', () => {
      const userWithoutRoles = { ...mockUser, roles: [] };
      expect(hasRole(userWithoutRoles, 'user')).toBe(false);
    });

    it('returns false when user is null', () => {
      expect(hasRole(null as any, 'user')).toBe(false);
    });
  });

  describe('isAdmin', () => {
    it('returns true for admin user', () => {
      expect(isAdmin(mockAdminUser)).toBe(true);
    });

    it('returns false for non-admin user', () => {
      expect(isAdmin(mockUser)).toBe(false);
      expect(isAdmin(mockBasicUser)).toBe(false);
    });

    it('returns false when user is null', () => {
      expect(isAdmin(null as any)).toBe(false);
    });
  });

  describe('isPremium', () => {
    it('returns true for premium user', () => {
      expect(isPremium(mockUser)).toBe(true);
    });

    it('returns true for admin user (admin inherits premium)', () => {
      expect(isPremium(mockAdminUser)).toBe(true);
    });

    it('returns false for basic user', () => {
      expect(isPremium(mockBasicUser)).toBe(false);
    });

    it('returns false when user is null', () => {
      expect(isPremium(null as any)).toBe(false);
    });
  });

  describe('hasPermission', () => {
    it('returns true when user has the specified permission', () => {
      expect(hasPermission(mockUser, 'user', 'read')).toBe(true);
      expect(hasPermission(mockUser, 'user', 'write')).toBe(true);
    });

    it('returns false when user does not have the specified permission', () => {
      expect(hasPermission(mockUser, 'system', 'admin')).toBe(false);
    });

    it('returns false when user has no permissions', () => {
      const userWithoutPermissions = { ...mockUser, permissions: [] };
      expect(hasPermission(userWithoutPermissions, 'user', 'read')).toBe(false);
    });

    it('returns false when user is null', () => {
      expect(hasPermission(null as any, 'user', 'read')).toBe(false);
    });
  });

  describe('getFilteredNavigationItems', () => {
    it('returns all items for admin user', () => {
      const items = getFilteredNavigationItems(mockAdminUser);
      expect(items).toHaveLength(12); // All navigation items
      expect(items.some(item => item.label === 'SMS Analytics')).toBe(true);
      expect(items.some(item => item.label === 'Admin Analytics')).toBe(true);
    });

    it('returns premium items for premium user', () => {
      const items = getFilteredNavigationItems(mockUser);
      expect(items.some(item => item.label === 'SMS Analytics')).toBe(true);
      expect(items.some(item => item.label === 'Admin Analytics')).toBe(false);
    });

    it('returns only public items for basic user', () => {
      const items = getFilteredNavigationItems(mockBasicUser);
      expect(items.some(item => item.label === 'SMS Analytics')).toBe(false);
      expect(items.some(item => item.label === 'Admin Analytics')).toBe(false);
    });

    it('returns only public items when user is null', () => {
      const items = getFilteredNavigationItems(null);
      // Should return all items with requiredRole: null
      expect(items.length).toBeGreaterThan(0);
      expect(items.every(item => item.requiredRole === null)).toBe(true);
    });
  });
});
