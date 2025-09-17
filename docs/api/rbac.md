# RBAC API

The RBAC (Role-Based Access Control) API provides comprehensive management of roles, permissions, and user access control for the Personal Assistant system.

## Base URL

```
/api/v1/rbac
```

## Authentication

All endpoints require authentication via JWT token in the Authorization header:

```
Authorization: Bearer <jwt_token>
```

## Permission Requirements

Most endpoints require specific permissions:

- **Admin endpoints**: Require admin role
- **Read endpoints**: Require `rbac:read` permission
- **Write endpoints**: Require `rbac:write` permission

## Rate Limiting

- **Read operations**: 200 requests per minute
- **Write operations**: 50 requests per minute
- **Admin operations**: 100 requests per minute

## Role Management Endpoints

### Create Role

Create a new role in the system (administrator only).

**Endpoint**: `POST /roles`

**Request Body**:

```json
{
  "name": "content_manager",
  "description": "Can manage content and moderate user-generated content",
  "parent_role_id": 2
}
```

**Response**:

```json
{
  "id": 5,
  "name": "content_manager",
  "description": "Can manage content and moderate user-generated content",
  "parent_role_id": 2,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

**Required Permissions**: Admin role

**Status Codes**:

- `201 Created`: Role created successfully
- `400 Bad Request`: Role name already exists or invalid data
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Admin role required
- `500 Internal Server Error`: Server error

### List Roles

Get a paginated list of all roles in the system.

**Endpoint**: `GET /roles`

**Query Parameters**:

- `skip` (integer, optional): Number of roles to skip. Default: 0
- `limit` (integer, optional): Maximum number of roles to return. Range: 1-1000. Default: 100

**Response**:

```json
{
  "roles": [
    {
      "id": 1,
      "name": "admin",
      "description": "Full system administrator",
      "parent_role_id": null,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    },
    {
      "id": 2,
      "name": "moderator",
      "description": "Can moderate content and users",
      "parent_role_id": 1,
      "created_at": "2024-01-02T00:00:00Z",
      "updated_at": "2024-01-02T00:00:00Z"
    }
  ],
  "total": 2
}
```

**Required Permissions**: `rbac:read`

### Get Role

Get detailed information about a specific role.

**Endpoint**: `GET /roles/{role_id}`

**Path Parameters**:

- `role_id` (integer): ID of the role to retrieve

**Response**:

```json
{
  "id": 2,
  "name": "moderator",
  "description": "Can moderate content and users",
  "parent_role_id": 1,
  "created_at": "2024-01-02T00:00:00Z",
  "updated_at": "2024-01-02T00:00:00Z"
}
```

**Required Permissions**: `rbac:read`

**Status Codes**:

- `200 OK`: Role found
- `404 Not Found`: Role not found
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions

### Update Role

Update role information (administrator only).

**Endpoint**: `PUT /roles/{role_id}`

**Path Parameters**:

- `role_id` (integer): ID of the role to update

**Request Body**:

```json
{
  "description": "Updated description for the moderator role",
  "parent_role_id": null
}
```

**Response**:

```json
{
  "id": 2,
  "name": "moderator",
  "description": "Updated description for the moderator role",
  "parent_role_id": null,
  "created_at": "2024-01-02T00:00:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

**Required Permissions**: Admin role

## User Role Management Endpoints

### Grant Role to User

Grant a role to a specific user (administrator only).

**Endpoint**: `POST /users/{user_id}/roles`

**Path Parameters**:

- `user_id` (integer): ID of the user receiving the role

**Request Body**:

```json
{
  "role_name": "moderator",
  "is_primary": false,
  "expires_at": "2024-12-31T23:59:59Z"
}
```

**Response**:

```json
{
  "id": 15,
  "user_id": 123,
  "role_name": "moderator",
  "is_primary": false,
  "granted_by": 1,
  "granted_at": "2024-01-15T10:30:00Z",
  "expires_at": "2024-12-31T23:59:59Z"
}
```

**Required Permissions**: Admin role

**Status Codes**:

- `201 Created`: Role granted successfully
- `400 Bad Request`: Invalid role name or user already has role
- `404 Not Found`: User or role not found
- `403 Forbidden`: Admin role required

### Revoke Role from User

Revoke a role from a specific user (administrator only).

**Endpoint**: `DELETE /users/{user_id}/roles/{role_name}`

**Path Parameters**:

- `user_id` (integer): ID of the user losing the role
- `role_name` (string): Name of the role to revoke

**Response**:

```json
{
  "message": "Role 'moderator' revoked from user 123"
}
```

**Required Permissions**: Admin role

**Status Codes**:

- `200 OK`: Role revoked successfully
- `400 Bad Request`: User doesn't have the role
- `404 Not Found`: User or role not found
- `403 Forbidden`: Admin role required

### Get User Permissions

Get all permissions for a user including inherited roles.

**Endpoint**: `GET /users/{user_id}/permissions`

**Path Parameters**:

- `user_id` (integer): ID of the user

**Response**:

```json
{
  "user_id": 123,
  "roles": ["user", "moderator"],
  "permissions": [
    "user:read",
    "user:write",
    "content:read",
    "content:moderate",
    "rbac:read"
  ]
}
```

**Required Permissions**: `rbac:read`

## Permission Management Endpoints

### List Permissions

Get a paginated list of all permissions with optional filtering.

**Endpoint**: `GET /permissions`

**Query Parameters**:

- `skip` (integer, optional): Number of permissions to skip. Default: 0
- `limit` (integer, optional): Maximum number of permissions to return. Range: 1-1000. Default: 100
- `resource_type` (string, optional): Filter by resource type (e.g., "user", "content", "rbac")
- `action` (string, optional): Filter by action (e.g., "read", "write", "delete")

**Response**:

```json
{
  "permissions": [
    {
      "id": 1,
      "name": "user:read",
      "resource_type": "user",
      "action": "read",
      "description": "Read user information",
      "created_at": "2024-01-01T00:00:00Z"
    },
    {
      "id": 2,
      "name": "user:write",
      "resource_type": "user",
      "action": "write",
      "description": "Create and update user information",
      "created_at": "2024-01-01T00:00:00Z"
    },
    {
      "id": 15,
      "name": "content:moderate",
      "resource_type": "content",
      "action": "moderate",
      "description": "Moderate user-generated content",
      "created_at": "2024-01-02T00:00:00Z"
    }
  ],
  "total": 3
}
```

**Required Permissions**: `rbac:read`

**Example with filters**:

```bash
GET /permissions?resource_type=user&action=read&limit=10
```

## Audit Log Endpoints

### Get Audit Logs

Get audit logs with comprehensive filtering options (administrator only).

**Endpoint**: `GET /audit-logs`

**Query Parameters**:

- `user_id` (integer, optional): Filter by specific user ID
- `resource_type` (string, optional): Filter by resource type
- `action` (string, optional): Filter by action
- `granted` (boolean, optional): Filter by permission result (true/false)
- `start_date` (datetime, optional): Filter by start date (ISO format)
- `end_date` (datetime, optional): Filter by end date (ISO format)
- `skip` (integer, optional): Number of logs to skip. Default: 0
- `limit` (integer, optional): Maximum number of logs to return. Range: 1-1000. Default: 100

**Response**:

```json
{
  "logs": [
    {
      "id": 1001,
      "user_id": 123,
      "resource_type": "user",
      "resource_id": 456,
      "action": "read",
      "permission_granted": true,
      "roles_checked": ["user", "moderator"],
      "ip_address": "192.168.1.100",
      "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
      "created_at": "2024-01-15T10:30:00Z"
    },
    {
      "id": 1002,
      "user_id": 789,
      "resource_type": "rbac",
      "resource_id": null,
      "action": "write",
      "permission_granted": false,
      "roles_checked": ["user"],
      "ip_address": "192.168.1.101",
      "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
      "created_at": "2024-01-15T10:25:00Z"
    }
  ],
  "total": 2
}
```

**Required Permissions**: Admin role

**Example queries**:

```bash
# Get logs for a specific user
GET /audit-logs?user_id=123&limit=50

# Get failed permission attempts
GET /audit-logs?granted=false&start_date=2024-01-01T00:00:00Z

# Get logs for specific resource type
GET /audit-logs?resource_type=rbac&action=write
```

## Health Check Endpoint

### RBAC Health Check

Check the health status of the RBAC system.

**Endpoint**: `GET /health`

**Response**:

```json
{
  "status": "healthy",
  "service": "RBAC Management",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0"
}
```

**Authentication**: Not required

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request

```json
{
  "detail": "Role 'admin' already exists"
}
```

### 401 Unauthorized

```json
{
  "detail": "Authentication required"
}
```

### 403 Forbidden

```json
{
  "detail": "Admin role required"
}
```

### 404 Not Found

```json
{
  "detail": "Role with ID 999 not found"
}
```

### 500 Internal Server Error

```json
{
  "detail": "Failed to create role: Database connection error"
}
```

## Usage Examples

### Create a New Role

```bash
curl -X POST "https://api.personalassistant.com/api/v1/rbac/roles" \
  -H "Authorization: Bearer <jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "content_editor",
    "description": "Can create and edit content",
    "parent_role_id": 2
  }'
```

### Grant Role to User

```bash
curl -X POST "https://api.personalassistant.com/api/v1/rbac/users/123/roles" \
  -H "Authorization: Bearer <jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "role_name": "moderator",
    "is_primary": false,
    "expires_at": "2024-12-31T23:59:59Z"
  }'
```

### Get User Permissions

```bash
curl -X GET "https://api.personalassistant.com/api/v1/rbac/users/123/permissions" \
  -H "Authorization: Bearer <jwt_token>"
```

### Get Audit Logs with Filters

```bash
curl -X GET "https://api.personalassistant.com/api/v1/rbac/audit-logs?user_id=123&granted=false&limit=20" \
  -H "Authorization: Bearer <jwt_token>"
```

## Permission Model

The RBAC system uses a hierarchical permission model:

### Resource Types

- `user`: User management operations
- `content`: Content management operations
- `rbac`: Role and permission management
- `system`: System administration operations
- `analytics`: Analytics and reporting operations
- `sms`: SMS router operations

### Actions

- `read`: View/read operations
- `write`: Create/update operations
- `delete`: Delete operations
- `moderate`: Moderation operations
- `admin`: Administrative operations

### Permission Format

Permissions follow the format: `{resource_type}:{action}`

Examples:

- `user:read` - Can read user information
- `content:moderate` - Can moderate content
- `rbac:write` - Can manage roles and permissions
- `system:admin` - Can perform system administration

## Role Hierarchy

Roles can have parent-child relationships:

- **admin**: Top-level administrative role
- **moderator**: Inherits from admin, can moderate content
- **content_manager**: Inherits from moderator, can manage content
- **user**: Base user role with basic permissions

## Security Considerations

1. **Role Inheritance**: Child roles inherit permissions from parent roles
2. **Permission Validation**: All operations are validated against user permissions
3. **Audit Logging**: All permission checks are logged for security auditing
4. **Session Management**: Permissions are cached in user sessions for performance
5. **Expiration**: Roles can have expiration dates for temporary access
6. **Primary Roles**: Users can have one primary role for simplified permission checks

## Data Retention

- **Audit logs**: Retained for 7 years (compliance requirement)
- **Role assignments**: Retained indefinitely until explicitly revoked
- **Permission definitions**: Retained indefinitely for system integrity
