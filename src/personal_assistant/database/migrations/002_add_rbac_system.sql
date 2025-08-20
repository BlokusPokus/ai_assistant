-- Migration: Add RBAC System Tables
-- Version: 002
-- Description: Creates tables for Role-Based Access Control (RBAC) system
-- Date: December 2024

-- Create RBAC tables
CREATE TABLE IF NOT EXISTS roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    parent_role_id INTEGER REFERENCES roles(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS permissions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    action VARCHAR(50) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS role_permissions (
    id SERIAL PRIMARY KEY,
    role_id INTEGER REFERENCES roles(id) ON DELETE CASCADE,
    permission_id INTEGER REFERENCES permissions(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(role_id, permission_id)
);

CREATE TABLE IF NOT EXISTS user_roles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    role_id INTEGER REFERENCES roles(id) ON DELETE CASCADE,
    is_primary BOOLEAN DEFAULT FALSE,
    granted_by INTEGER REFERENCES users(id),
    granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NULL,
    UNIQUE(user_id, role_id)
);

CREATE TABLE IF NOT EXISTS access_audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    resource_type VARCHAR(50) NOT NULL,
    resource_id INTEGER NULL,
    action VARCHAR(50) NOT NULL,
    permission_granted BOOLEAN NOT NULL,
    roles_checked TEXT[],
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add RBAC fields to users table
ALTER TABLE users ADD COLUMN IF NOT EXISTS default_role_id INTEGER REFERENCES roles(id);
ALTER TABLE users ADD COLUMN IF NOT EXISTS role_assigned_at TIMESTAMP;
ALTER TABLE users ADD COLUMN IF NOT EXISTS role_assigned_by INTEGER REFERENCES users(id);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_roles_name ON roles(name);
CREATE INDEX IF NOT EXISTS idx_roles_parent_role_id ON roles(parent_role_id);
CREATE INDEX IF NOT EXISTS idx_permissions_resource_action ON permissions(resource_type, action);
CREATE INDEX IF NOT EXISTS idx_permissions_name ON permissions(name);
CREATE INDEX IF NOT EXISTS idx_role_permissions_role_id ON role_permissions(role_id);
CREATE INDEX IF NOT EXISTS idx_role_permissions_permission_id ON role_permissions(permission_id);
CREATE INDEX IF NOT EXISTS idx_user_roles_user_id ON user_roles(user_id);
CREATE INDEX IF NOT EXISTS idx_user_roles_role_id ON user_roles(role_id);
CREATE INDEX IF NOT EXISTS idx_user_roles_is_primary ON user_roles(is_primary);
CREATE INDEX IF NOT EXISTS idx_access_audit_logs_user_id ON access_audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_access_audit_logs_created_at ON access_audit_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_access_audit_logs_resource_type ON access_audit_logs(resource_type);
CREATE INDEX IF NOT EXISTS idx_access_audit_logs_action ON access_audit_logs(action);

-- Create triggers for updated_at
CREATE OR REPLACE FUNCTION update_roles_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_roles_updated_at
    BEFORE UPDATE ON roles
    FOR EACH ROW
    EXECUTE FUNCTION update_roles_updated_at();

-- Insert initial roles
INSERT INTO roles (name, description) VALUES
('user', 'Standard user with basic permissions'),
('premium', 'Premium user with extended permissions'),
('administrator', 'System administrator with full access')
ON CONFLICT (name) DO NOTHING;

-- Insert initial permissions
INSERT INTO permissions (name, resource_type, action, description) VALUES
-- User permissions
('user:read', 'user', 'read', 'Read user profile'),
('user:write', 'user', 'write', 'Write user profile'),
('user:delete', 'user', 'delete', 'Delete user account'),

-- Memory permissions
('memory:read', 'memory', 'read', 'Read user memories'),
('memory:write', 'memory', 'write', 'Write user memories'),
('memory:delete', 'memory', 'delete', 'Delete user memories'),

-- Task permissions
('task:read', 'task', 'read', 'Read user tasks'),
('task:write', 'task', 'write', 'Write user tasks'),
('task:delete', 'task', 'delete', 'Delete user tasks'),

-- Note permissions
('note:read', 'note', 'read', 'Read user notes'),
('note:write', 'note', 'write', 'Write user notes'),
('note:delete', 'note', 'delete', 'Delete user notes'),

-- Event permissions
('event:read', 'event', 'read', 'Read user events'),
('event:write', 'event', 'write', 'Write user events'),
('event:delete', 'event', 'delete', 'Delete user events'),

-- System permissions
('system:read', 'system', 'read', 'Read system information'),
('system:write', 'system', 'write', 'Write system configuration'),
('system:admin', 'system', 'admin', 'Full system administration'),

-- RBAC permissions
('rbac:read', 'rbac', 'read', 'Read RBAC information'),
('rbac:write', 'rbac', 'write', 'Manage RBAC roles and permissions'),
('rbac:admin', 'rbac', 'admin', 'Full RBAC administration')
ON CONFLICT (name) DO NOTHING;

-- Assign permissions to roles
-- User role permissions
INSERT INTO role_permissions (role_id, permission_id) 
SELECT r.id, p.id FROM roles r, permissions p 
WHERE r.name = 'user' AND p.name IN (
    'user:read', 'user:write',
    'memory:read', 'memory:write',
    'task:read', 'task:write',
    'note:read', 'note:write',
    'event:read', 'event:write'
)
ON CONFLICT (role_id, permission_id) DO NOTHING;

-- Premium role permissions (inherits user + additional)
INSERT INTO role_permissions (role_id, permission_id) 
SELECT r.id, p.id FROM roles r, permissions p 
WHERE r.name = 'premium' AND p.name IN (
    'user:read', 'user:write',
    'memory:read', 'memory:write', 'memory:delete',
    'task:read', 'task:write', 'task:delete',
    'note:read', 'note:write', 'note:delete',
    'event:read', 'event:write', 'event:delete',
    'system:read'
)
ON CONFLICT (role_id, permission_id) DO NOTHING;

-- Administrator role permissions (all permissions)
INSERT INTO role_permissions (role_id, permission_id) 
SELECT r.id, p.id FROM roles r, permissions p 
WHERE r.name = 'administrator'
ON CONFLICT (role_id, permission_id) DO NOTHING;

-- Add comments for documentation
COMMENT ON TABLE roles IS 'User roles with hierarchical permissions for RBAC system';
COMMENT ON TABLE permissions IS 'Granular permissions for resources and actions';
COMMENT ON TABLE role_permissions IS 'Many-to-many relationship between roles and permissions';
COMMENT ON TABLE user_roles IS 'User-role associations with audit trail';
COMMENT ON TABLE access_audit_logs IS 'Audit trail for all access decisions and permission checks';

COMMENT ON COLUMN roles.name IS 'Unique role identifier (user, premium, administrator)';
COMMENT ON COLUMN roles.parent_role_id IS 'Parent role for inheritance (NULL for top-level roles)';
COMMENT ON COLUMN permissions.resource_type IS 'Type of resource (user, memory, task, note, event, system, rbac)';
COMMENT ON COLUMN permissions.action IS 'Action allowed on resource (read, write, delete, admin)';
COMMENT ON COLUMN user_roles.is_primary IS 'Whether this is the user''s primary role';
COMMENT ON COLUMN user_roles.granted_by IS 'User ID who granted this role (NULL for self-assignment)';
COMMENT ON COLUMN access_audit_logs.roles_checked IS 'Array of role names that were checked for this access attempt';
COMMENT ON COLUMN access_audit_logs.permission_granted IS 'Whether permission was granted (true) or denied (false)'; 