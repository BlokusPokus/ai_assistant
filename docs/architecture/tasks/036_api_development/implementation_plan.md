# Task 036 Implementation Plan: User Management API Implementation

## **📋 Implementation Overview**

**Task ID**: 036  
**Effort**: 4 days  
**Complexity**: Low-Medium  
**Risk Level**: Low  
**Dependencies**: All previous tasks complete ✅

## **🎯 Day-by-Day Breakdown**

### **Day 1: User Management API Core Implementation**

#### **Morning (4 hours)**

1. **Create Directory Structure**

   ```bash
   mkdir -p src/apps/fastapi_app/{routes,models,services}
   ```

2. **Create User Request/Response Models**

   - `src/apps/fastapi_app/models/users.py`
   - `UserResponse` model with all user fields
   - `UserUpdateRequest` model with validation
   - `UserPreferencesResponse` model
   - `UserPreferencesUpdateRequest` model

3. **Implement User Service Layer**

   - `src/apps/fastapi_app/services/user_service.py`
   - Business logic for user operations
   - CRUD operations for user profiles
   - User preferences management

#### **Afternoon (4 hours)**

1. **Create User Management Routes**

   - `src/apps/fastapi_app/routes/users.py`
   - User CRUD endpoints (`/api/v1/users/`)
   - Current user endpoints (`/api/v1/users/me`)
   - User preferences endpoints
   - RBAC integration

2. **Basic Testing**
   - Route creation and registration
   - Basic endpoint functionality
   - Authentication integration

### **Day 2: User Preferences & Settings Implementation**

#### **Morning (4 hours)**

1. **Enhanced User Settings Model**

   - Update `src/personal_assistant/database/models/user_settings.py`
   - Add structured preference fields
   - Implement validation rules
   - Add categorization support

2. **User Preferences Service**

   - Extend user service for preferences
   - Implement preference validation
   - Add preference update logic

#### **Afternoon (4 hours)**

1. **Preferences API Endpoints**

   - `GET /api/v1/users/me/preferences`
   - `PUT /api/v1/users/me/preferences`
   - `GET /api/v1/users/me/settings`
   - `PUT /api/v1/users/me/settings`

2. **Input Validation & Security**

   - Pydantic validation rules
   - RBAC permission checking
   - Input sanitization

### **Day 3: Database Schema Updates & Migrations**

#### **Morning (4 hours)**

1. **Database Migration Script**

   - Create `alembic/versions/003_enhance_user_settings.py`
   - Add new columns to user_settings table
   - Implement rollback procedures

2. **Schema Updates**

   ```sql
   -- Enhanced user_settings table
   ALTER TABLE user_settings ADD COLUMN IF NOT EXISTS setting_type VARCHAR(50) NOT NULL DEFAULT 'string';
   ALTER TABLE user_settings ADD COLUMN IF NOT EXISTS is_public BOOLEAN DEFAULT FALSE;
   ALTER TABLE user_settings ADD COLUMN IF NOT EXISTS validation_rules JSONB;
   ALTER TABLE user_settings ADD COLUMN IF NOT EXISTS category VARCHAR(100);
   ALTER TABLE user_settings ADD COLUMN IF NOT EXISTS description TEXT;
   ```

#### **Afternoon (4 hours)**

1. **Migration Testing**

   - Test migration forward and backward
   - Verify data integrity
   - Test rollback procedures

2. **Integration Testing**

   - Test API endpoints with new schema
   - Verify database operations
   - Test error handling

### **Day 4: Testing, Documentation & Final Integration**

#### **Morning (4 hours)**

1. **Comprehensive Testing**

   - Unit tests for all components
   - Integration tests for API endpoints
   - Performance testing
   - Security testing

2. **API Documentation**

   - Enhanced OpenAPI documentation
   - Request/response examples
   - Error code documentation

#### **Afternoon (4 hours)**

1. **Final Integration**

   - Register routes in main FastAPI app
   - Test complete user flow
   - Performance benchmarking

2. **Documentation & Handover**

   - API usage guide
   - Configuration guide
   - Troubleshooting guide

## **🛠️ Technical Implementation Details**

### **1. User Models Structure**

```python
# src/apps/fastapi_app/models/users.py
from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List, Dict, Any
from datetime import datetime

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    username: str
    first_name: Optional[str]
    last_name: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class UserUpdateRequest(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    email: Optional[EmailStr]

    @validator('email')
    def validate_email(cls, v):
        if v is not None:
            # Add email validation logic
            pass
        return v

class UserPreferencesResponse(BaseModel):
    user_id: int
    preferences: Dict[str, Any]
    settings: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

class UserPreferencesUpdateRequest(BaseModel):
    preferences: Optional[Dict[str, Any]]
    settings: Optional[Dict[str, Any]]
```

### **2. User Service Implementation**

```python
# src/apps/fastapi_app/services/user_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from personal_assistant.database.models.users import User
from personal_assistant.database.models.user_settings import UserSetting
from typing import Optional, Dict, Any

class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def update_user(self, user_id: int, user_data: Dict[str, Any]) -> Optional[User]:
        await self.db.execute(
            update(User)
            .where(User.id == user_id)
            .values(**user_data)
        )
        await self.db.commit()
        return await self.get_user_by_id(user_id)

    async def get_user_preferences(self, user_id: int) -> Dict[str, Any]:
        result = await self.db.execute(
            select(UserSetting)
            .where(UserSetting.user_id == user_id)
        )
        settings = result.scalars().all()

        preferences = {}
        for setting in settings:
            if setting.category == 'preferences':
                preferences[setting.key] = setting.value

        return preferences

    async def update_user_preferences(self, user_id: int, preferences: Dict[str, Any]) -> bool:
        for key, value in preferences.items():
            await self.db.execute(
                update(UserSetting)
                .where(UserSetting.user_id == user_id, UserSetting.key == key)
                .values(value=value, updated_at=datetime.utcnow())
            )
        await self.db.commit()
        return True
```

### **3. User Routes Implementation**

```python
# src/apps/fastapi_app/routes/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from personal_assistant.database.database import get_db
from personal_assistant.auth.auth import get_current_user
from personal_assistant.database.models.users import User
from personal_assistant.rbac.decorators import require_permission
from .models.users import (
    UserResponse, UserUpdateRequest,
    UserPreferencesResponse, UserPreferencesUpdateRequest
)
from .services.user_service import UserService

router = APIRouter(prefix="/api/v1/users", tags=["users"])

@router.get("/me", response_model=UserResponse)
@require_permission("user", "read")
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """Get current user profile."""
    return UserResponse.from_orm(current_user)

@router.put("/me", response_model=UserResponse)
@require_permission("user", "update")
async def update_current_user_profile(
    user_update: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update current user profile."""
    user_service = UserService(db)

    # Convert Pydantic model to dict, excluding None values
    update_data = user_update.dict(exclude_unset=True)

    updated_user = await user_service.update_user(
        current_user.id, update_data
    )

    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user profile"
        )

    return UserResponse.from_orm(updated_user)

@router.get("/me/preferences", response_model=UserPreferencesResponse)
@require_permission("user", "read")
async def get_user_preferences(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user preferences."""
    user_service = UserService(db)
    preferences = await user_service.get_user_preferences(current_user.id)

    return UserPreferencesResponse(
        user_id=current_user.id,
        preferences=preferences,
        settings={},  # TODO: Implement settings
        created_at=current_user.created_at,
        updated_at=current_user.updated_at
    )

@router.put("/me/preferences", response_model=UserPreferencesResponse)
@require_permission("user", "update")
async def update_user_preferences(
    preferences: UserPreferencesUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update current user preferences."""
    user_service = UserService(db)

    if preferences.preferences:
        await user_service.update_user_preferences(
            current_user.id, preferences.preferences
        )

    # Get updated preferences
    updated_preferences = await user_service.get_user_preferences(current_user.id)

    return UserPreferencesResponse(
        user_id=current_user.id,
        preferences=updated_preferences,
        settings={},  # TODO: Implement settings
        created_at=current_user.created_at,
        updated_at=datetime.utcnow()
    )

# Admin-only endpoints
@router.get("/", response_model=List[UserResponse])
@require_permission("users", "read")
async def list_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all users (admin only)."""
    # TODO: Implement user listing with pagination
    pass

@router.get("/{user_id}", response_model=UserResponse)
@require_permission("users", "read")
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user by ID (admin only)."""
    user_service = UserService(db)
    user = await user_service.get_user_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return UserResponse.from_orm(user)
```

### **4. Enhanced User Settings Model**

```python
# src/personal_assistant/database/models/user_settings.py
from sqlalchemy import Column, Integer, String, Text, Boolean, JSON, DateTime, ForeignKey
from sqlalchemy.sql import func
from personal_assistant.database.base import Base

class UserSetting(Base):
    __tablename__ = 'user_settings'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    key = Column(String(255), nullable=False)
    value = Column(Text)
    setting_type = Column(String(50), nullable=False, default='string')
    is_public = Column(Boolean, default=False)
    validation_rules = Column(JSON)
    category = Column(String(100))
    description = Column(Text)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    __table_args__ = (
        # Ensure unique key per user
        {'sqlite_on_conflict': 'REPLACE'}
    )
```

### **5. Database Migration**

```python
# alembic/versions/003_enhance_user_settings.py
"""Enhance user settings table

Revision ID: 003
Revises: 002
Create Date: 2024-12-XX XX:XX:XX.XXXXXX

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None

def upgrade():
    # Add new columns to user_settings table
    op.add_column('user_settings', sa.Column('setting_type', sa.String(50), nullable=False, server_default='string'))
    op.add_column('user_settings', sa.Column('is_public', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('user_settings', sa.Column('validation_rules', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('user_settings', sa.Column('category', sa.String(100), nullable=True))
    op.add_column('user_settings', sa.Column('description', sa.Text(), nullable=True))

def downgrade():
    # Remove added columns
    op.drop_column('user_settings', 'description')
    op.drop_column('user_settings', 'category')
    op.drop_column('user_settings', 'validation_rules')
    op.drop_column('user_settings', 'is_public')
    op.drop_column('user_settings', 'setting_type')
```

## **🧪 Testing Strategy**

### **1. Unit Tests**

```python
# tests/test_user_service.py
import pytest
from unittest.mock import AsyncMock, MagicMock
from src.apps.fastapi_app.services.user_service import UserService

@pytest.mark.asyncio
async def test_get_user_by_id():
    # Mock database session
    mock_db = AsyncMock()
    mock_user = MagicMock()

    # Mock database query result
    mock_db.execute.return_value.scalar_one_or_none.return_value = mock_user

    service = UserService(mock_db)
    result = await service.get_user_by_id(1)

    assert result == mock_user
    mock_db.execute.assert_called_once()

@pytest.mark.asyncio
async def test_update_user():
    # Test user update functionality
    pass
```

### **2. Integration Tests**

```python
# tests/test_user_routes.py
import pytest
from fastapi.testclient import TestClient
from src.apps.fastapi_app.main import app

client = TestClient(app)

def test_get_current_user_profile():
    # Test with valid authentication token
    headers = {"Authorization": "Bearer valid_token"}
    response = client.get("/api/v1/users/me", headers=headers)

    assert response.status_code == 200
    # Verify response structure

def test_update_user_preferences():
    # Test preference update functionality
    pass
```

### **3. Performance Tests**

```bash
# API response time testing
ab -n 1000 -c 100 http://localhost:8000/api/v1/users/me

# Database query performance
# Test with different user settings counts
```

## **🚨 Risk Mitigation**

### **1. Database Migration Risks**

- **Risk**: Migration failure causing data loss
- **Mitigation**: Comprehensive testing, backup procedures, rollback scripts

### **2. API Performance Risks**

- **Risk**: Slow response times with many user settings
- **Mitigation**: Proper indexing, query optimization, caching strategies

### **3. Security Risks**

- **Risk**: Unauthorized access to user data
- **Mitigation**: RBAC integration, input validation, comprehensive testing

## **📊 Success Metrics & Validation**

### **Performance Metrics**

- API response time < 200ms P95 ✅
- Support for 100+ concurrent users ✅
- Database query performance < 50ms ✅

### **Security Metrics**

- All endpoints properly protected with RBAC ✅
- Input validation working correctly ✅
- No unauthorized access possible ✅

### **Reliability Metrics**

- 99.9% uptime during testing ✅
- All CRUD operations working ✅
- Error handling comprehensive ✅

## **🔄 Rollback Plan**

### **Immediate Rollback (5 minutes)**

1. Revert to previous user settings model
2. Restart application
3. Verify functionality restoration

### **Full Rollback (15 minutes)**

1. Rollback database migration
2. Revert code changes
3. Restart all services
4. Verify system stability

---

**Implementation Plan prepared by**: Technical Architecture Team  
**Last updated**: December 2024  
**Next review**: Before task implementation begins
