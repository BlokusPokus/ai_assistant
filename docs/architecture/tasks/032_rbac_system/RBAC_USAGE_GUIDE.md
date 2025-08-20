# 🔐 RBAC System Usage Guide

## **📋 Overview**

The Role-Based Access Control (RBAC) system provides comprehensive authorization for the Personal Assistant TDAH platform. This guide explains how to use the RBAC system to protect endpoints, manage roles, and monitor access.

## **🚀 Quick Start**

### **1. Protecting Endpoints with Permissions**

Use permission decorators to protect your FastAPI endpoints:

```python
from personal_assistant.auth.decorators import require_permission, require_role

@router.get("/users/{user_id}")
@require_permission("user", "read")
async def get_user(user_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    """Get user profile - requires 'user:read' permission."""
    return {"user_id": user_id, "message": "User profile"}

@router.post("/users")
@require_permission("user", "write")
async def create_user(user_data: UserCreate, request: Request, db: AsyncSession = Depends(get_db)):
    """Create user - requires 'user:write' permission."""
    return {"message": "User created"}
```

### **2. Protecting Endpoints with Roles**

Use role decorators for role-based protection:

```python
@router.get("/admin/users")
@require_role("administrator")
async def list_all_users(request: Request, db: AsyncSession = Depends(get_db)):
    """List all users - requires 'administrator' role."""
    return {"users": []}

@router.get("/premium/analytics")
@require_premium()
async def get_analytics(request: Request, db: AsyncSession = Depends(get_db)):
    """Get analytics - requires 'premium' or 'administrator' role."""
    return {"analytics": {}}
```

### **3. Ownership-Based Protection**

Protect resources based on ownership:

```python
@router.put("/users/{user_id}")
@require_ownership("user", "write", "user_id")
async def update_user(user_id: int, user_data: UserUpdate, request: Request, db: AsyncSession = Depends(get_db)):
    """Update user - requires ownership and 'user:write' permission."""
    return {"message": "User updated"}
```

## **🔐 Permission System**

### **Permission Format**

Permissions follow the format: `resource_type:action`

- **Resource Types**: `user`, `memory`, `task`, `note`, `event`, `system`, `rbac`
- **Actions**: `read`, `write`, `delete`, `admin`

### **Common Permission Patterns**

```python
# User permissions
@require_user_permission("read")    # user:read
@require_user_permission("write")   # user:write
@require_user_permission("delete")  # user:delete

# Memory permissions
@require_memory_permission("read")  # memory:read
@require_memory_permission("write") # memory:write

# System permissions
@require_system_permission("read")  # system:read
@require_system_permission("admin") # system:admin
```

### **Permission Matrix**

| Resource Type       | User | Premium | Administrator |
| ------------------- | ---- | ------- | ------------- |
| **Own Profile**     | R/W  | R/W     | R/W (all)     |
| **Own Memories**    | R/W  | R/W     | R/W (all)     |
| **Own Tasks**       | R/W  | R/W     | R/W (all)     |
| **System Metrics**  | None | R       | R/W           |
| **User Management** | None | None    | R/W           |
| **RBAC Management** | None | None    | R/W           |

## **👥 Role Management**

### **Available Roles**

1. **user** - Standard user with basic permissions
2. **premium** - Premium user with extended permissions
3. **administrator** - System administrator with full access

### **Role Inheritance**

- **Premium** users inherit all **User** permissions
- **Administrator** users inherit all permissions
- Roles can have parent-child relationships

### **Managing User Roles**

```python
from personal_assistant.auth.permission_service import PermissionService

# Grant role to user
permission_service = PermissionService(db)
success = await permission_service.grant_role(
    user_id=123,
    role_name="premium",
    granted_by=current_user.id,
    is_primary=True
)

# Revoke role from user
success = await permission_service.revoke_role(
    user_id=123,
    role_name="premium",
    revoked_by=current_user.id
)

# Check if user has role
has_role = await permission_service.has_role(user_id=123, role_name="premium")
```

## **📊 Audit Logging**

### **Automatic Logging**

All permission checks are automatically logged with:

- User ID and context
- Resource and action attempted
- Permission granted/denied
- IP address and user agent
- Timestamp

### **Viewing Audit Logs**

```python
# Get audit logs for specific user
logs = await permission_service.get_audit_logs(
    user_id=123,
    start_date=datetime.now() - timedelta(days=7)
)

# Get denied access attempts
denied_logs = await permission_service.get_audit_logs(
    granted=False,
    resource_type="user"
)
```

### **Audit Log API Endpoints**

```bash
# Get audit logs (admin only)
GET /api/v1/rbac/audit-logs

# Filter by user
GET /api/v1/rbac/audit-logs?user_id=123

# Filter by resource type
GET /api/v1/rbac/audit-logs?resource_type=user

# Filter by date range
GET /api/v1/rbac/audit-logs?start_date=2024-01-01&end_date=2024-01-31
```

## **🛠️ API Management**

### **RBAC Management Endpoints**

```bash
# Role Management
POST   /api/v1/rbac/roles                    # Create role (admin)
GET    /api/v1/rbac/roles                    # List roles
GET    /api/v1/rbac/roles/{role_id}         # Get role
PUT    /api/v1/rbac/roles/{role_id}         # Update role (admin)

# User Role Management
POST   /api/v1/rbac/users/{user_id}/roles   # Grant role (admin)
DELETE /api/v1/rbac/users/{user_id}/roles/{role_name}  # Revoke role (admin)
GET    /api/v1/rbac/users/{user_id}/permissions  # Get user permissions

# Permission Management
GET    /api/v1/rbac/permissions              # List permissions

# Audit Logs
GET    /api/v1/rbac/audit-logs              # Get audit logs (admin)
```

### **Example API Usage**

```bash
# Create a new role
curl -X POST "http://localhost:8000/api/v1/rbac/roles" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "moderator",
    "description": "Content moderator role",
    "parent_role_id": 1
  }'

# Grant role to user
curl -X POST "http://localhost:8000/api/v1/rbac/users/123/roles" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "role_name": "premium",
    "is_primary": true
  }'

# Get user permissions
curl -X GET "http://localhost:8000/api/v1/rbac/users/123/permissions" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## **🔧 Advanced Usage**

### **Custom Permission Checks**

```python
from personal_assistant.auth.permission_service import PermissionService

async def custom_permission_check(user_id: int, resource_id: int, db: AsyncSession):
    """Custom permission logic for complex scenarios."""
    permission_service = PermissionService(db)

    # Check basic permission
    has_permission = await permission_service.check_permission(
        user_id=user_id,
        resource_type="memory",
        action="read"
    )

    if not has_permission:
        return False

    # Additional business logic
    # ... custom checks ...

    return True
```

### **Batch Permission Checking**

```python
async def check_multiple_permissions(user_id: int, permissions: List[tuple], db: AsyncSession):
    """Check multiple permissions efficiently."""
    permission_service = PermissionService(db)
    results = {}

    for resource_type, action in permissions:
        results[f"{resource_type}:{action}"] = await permission_service.check_permission(
            user_id=user_id,
            resource_type=resource_type,
            action=action
        )

    return results
```

### **Permission Caching**

The system automatically caches permission results for 5 minutes:

```python
# Clear cache for specific user
permission_service._clear_user_cache(user_id=123)

# Clear all cache
permission_service.clear_all_cache()
```

## **📝 Best Practices**

### **1. Use Appropriate Permission Levels**

```python
# Good: Specific permission
@require_permission("user", "read")

# Avoid: Too broad
@require_role("administrator")  # Unless really needed
```

### **2. Combine Permissions and Ownership**

```python
# Good: Check both permission and ownership
@require_ownership("memory", "write", "memory_id")

# Avoid: Only checking ownership
# This could allow users to modify others' data if they have the permission
```

### **3. Log Important Operations**

```python
# Log custom operations
await permission_service.log_access_attempt(
    user_id=current_user.id,
    resource_type="custom",
    action="export_data",
    resource_id=None,
    granted=True,
    roles_checked=["premium"],
    ip_address=request.client.host,
    user_agent=request.headers.get("user-agent")
)
```

### **4. Handle Permission Errors Gracefully**

```python
from fastapi import HTTPException, status

@router.get("/protected-resource")
@require_permission("resource", "read")
async def get_protected_resource(request: Request, db: AsyncSession = Depends(get_db)):
    try:
        # Your logic here
        return {"data": "protected content"}
    except Exception as e:
        # Log the error
        logger.error(f"Error accessing protected resource: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
```

## **🧪 Testing**

### **Running RBAC Tests**

```bash
# Run all RBAC tests
pytest tests/test_auth/test_rbac_system.py -v

# Run specific test class
pytest tests/test_auth/test_rbac_system.py::TestPermissionService -v

# Run with coverage
pytest tests/test_auth/test_rbac_system.py --cov=personal_assistant.auth --cov-report=html
```

### **Test Examples**

```python
# Test permission checking
async def test_user_can_read_own_profile():
    # Setup test user with 'user:read' permission
    # Test endpoint access
    # Verify permission granted

# Test role inheritance
async def test_premium_user_inherits_user_permissions():
    # Setup premium user
    # Test access to user-level resources
    # Verify inheritance works
```

## **🚨 Troubleshooting**

### **Common Issues**

1. **Permission Denied Errors**

   - Check if user has the required role
   - Verify permission exists in database
   - Check role inheritance

2. **Cache Issues**

   - Clear user cache: `permission_service._clear_user_cache(user_id)`
   - Clear all cache: `permission_service.clear_all_cache()`

3. **Database Connection Issues**
   - Verify database is running
   - Check connection string
   - Verify RBAC tables exist

### **Debug Mode**

Enable debug logging to troubleshoot permission issues:

```python
import logging
logging.getLogger('personal_assistant.auth').setLevel(logging.DEBUG)
```

### **Health Check**

Check RBAC system health:

```bash
curl http://localhost:8000/api/v1/rbac/health
```

## **📚 Additional Resources**

- **API Documentation**: `/docs` (Swagger UI)
- **Database Schema**: See `src/personal_assistant/database/models/rbac_models.py`
- **Migration Script**: `src/personal_assistant/database/migrations/002_add_rbac_system.sql`
- **Test Suite**: `tests/test_auth/test_rbac_system.py`

## **🔗 Integration Examples**

### **Frontend Integration**

```javascript
// Check user permissions
async function checkPermission(resourceType, action) {
  const response = await fetch(`/api/v1/rbac/users/${userId}/permissions`);
  const { permissions } = await response.json();
  return permissions.includes(`${resourceType}:${action}`);
}

// Show/hide UI elements based on permissions
if (await checkPermission("user", "write")) {
  showEditButton();
} else {
  hideEditButton();
}
```

### **CLI Integration**

```bash
# Assign default roles to existing users
python scripts/assign_default_roles.py

# Check user permissions
python -c "
import asyncio
from personal_assistant.auth.permission_service import PermissionService
from personal_assistant.database.session import AsyncSessionLocal

async def check_user_permissions(user_id):
    async with AsyncSessionLocal() as db:
        service = PermissionService(db)
        permissions = await service.get_user_permissions(user_id)
        print(f'User {user_id} permissions: {permissions}')

asyncio.run(check_user_permissions(1))
"
```

---

**Need Help?** Check the logs, run the health check, or review the test suite for examples of proper usage.
