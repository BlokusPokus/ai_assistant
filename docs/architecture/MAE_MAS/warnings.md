# RBAC SYSTEM

## SQLAlchemy warnings: About overlapping relationships (these don't affect functionality)

## Pydantic deprecation warnings: About class-based config (will be fixed in future versions)

venv_personal_assistant/lib/python3.11/site-packages/pydantic/\_internal/\_config.py:323
/Users/ianleblanc/Desktop/personal_assistant/venv_personal_assistant/lib/python3.11/site-packages/pydantic/\_internal/\_config.py:323: PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead. Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.11/migration/
warnings.warn(DEPRECATION_MESSAGE, DeprecationWarning)

src/personal_assistant/database/models/base.py:4
/Users/ianleblanc/Desktop/personal_assistant/src/personal_assistant/database/models/base.py:4: MovedIn20Warning: The `declarative_base()` function is now available as sqlalchemy.orm.declarative_base(). (deprecated since: 2.0) (Background on SQLAlchemy 2.0 at: https://sqlalche.me/e/b8d9)
Base = declarative_base()

tests/test_auth/test_rbac_system.py::TestPermissionService::test_get_user_roles
/Users/ianleblanc/Desktop/personal_assistant/src/personal_assistant/auth/permission_service.py:118: SAWarning: relationship 'Role.child_roles' will copy column roles.id to column roles.parent_role_id, which conflicts with relationship(s): 'Role.parent_role' (copies roles.id to roles.parent_role_id). If this is not the intention, consider if these relationships should be linked with back_populates, or if viewonly=True should be applied to one or more if they are read-only. For the less common case that foreign key constraints are partially overlapping, the orm.foreign() annotation can be used to isolate the columns that should be written towards. To silence this warning, add the parameter 'overlaps="parent_role"' to the 'Role.child_roles' relationship. (Background on this warning at: https://sqlalche.me/e/20/qzyx) (This warning originated from the `configure_mappers()` process, which was invoked automatically in response to a user-initiated operation.)
selectinload(Role.permissions)

tests/test_auth/test_rbac_system.py::TestPermissionService::test_get_user_roles
/Users/ianleblanc/Desktop/personal_assistant/src/personal_assistant/auth/permission_service.py:118: SAWarning: relationship 'Permission.roles' will copy column permissions.id to column role_permissions.permission_id, which conflicts with relationship(s): 'Role.permissions' (copies permissions.id to role_permissions.permission_id). If this is not the intention, consider if these relationships should be linked with back_populates, or if viewonly=True should be applied to one or more if they are read-only. For the less common case that foreign key constraints are partially overlapping, the orm.foreign() annotation can be used to isolate the columns that should be written towards. To silence this warning, add the parameter 'overlaps="permissions"' to the 'Permission.roles' relationship. (Background on this warning at: https://sqlalche.me/e/20/qzyx) (This warning originated from the `configure_mappers()` process, which was invoked automatically in response to a user-initiated operation.)
selectinload(Role.permissions)

tests/test_auth/test_rbac_system.py::TestPermissionService::test_get_user_roles
/Users/ianleblanc/Desktop/personal_assistant/src/personal_assistant/auth/permission_service.py:118: SAWarning: relationship 'Permission.roles' will copy column roles.id to column role_permissions.role_id, which conflicts with relationship(s): 'Role.permissions' (copies roles.id to role_permissions.role_id). If this is not the intention, consider if these relationships should be linked with back_populates, or if viewonly=True should be applied to one or more if they are read-only. For the less common case that foreign key constraints are partially overlapping, the orm.foreign() annotation can be used to isolate the columns that should be written towards. To silence this warning, add the parameter 'overlaps="permissions"' to the 'Permission.roles' relationship. (Background on this warning at: https://sqlalche.me/e/20/qzyx) (This warning originated from the `configure_mappers()` process, which was invoked automatically in response to a user-initiated operation.)
selectinload(Role.permissions)
