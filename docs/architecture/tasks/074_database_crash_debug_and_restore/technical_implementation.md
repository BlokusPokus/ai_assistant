# Technical Implementation Guide - Database Crash Debug and Restore

## 🔧 **Implementation Steps**

### **Step 1: Database Health Analysis**

#### **1.1 Database Connection and Basic Health Check**

```python
# File: scripts/debug_database_health.py
import asyncio
import logging
from sqlalchemy import text
from personal_assistant.database.session import AsyncSessionLocal

async def check_database_health():
    """Comprehensive database health check"""
    logger = logging.getLogger(__name__)

    try:
        async with AsyncSessionLocal() as session:
            # Basic connection test
            result = await session.execute(text('SELECT 1'))
            logger.info("✅ Database connection: OK")

            # Check all tables
            result = await session.execute(text("""
                SELECT table_name,
                       pg_size_pretty(pg_total_relation_size(quote_ident(table_name))) as size
                FROM information_schema.tables
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            tables = result.fetchall()
            logger.info(f"📊 Found {len(tables)} tables")

            # Check critical tables
            critical_tables = ['users', 'roles', 'permissions', 'user_sessions', 'auth_tokens']
            for table in critical_tables:
                result = await session.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar()
                logger.info(f"📋 {table}: {count} records")

    except Exception as e:
        logger.error(f"❌ Database health check failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(check_database_health())
```

#### **1.2 Data Integrity Validation**

```python
# File: scripts/validate_data_integrity.py
import asyncio
from sqlalchemy import text
from personal_assistant.database.session import AsyncSessionLocal

async def validate_data_integrity():
    """Validate data integrity across all tables"""

    integrity_checks = [
        # Check foreign key constraints
        "SELECT COUNT(*) FROM user_roles ur LEFT JOIN users u ON ur.user_id = u.id WHERE u.id IS NULL",
        "SELECT COUNT(*) FROM role_permissions rp LEFT JOIN roles r ON rp.role_id = r.id WHERE r.id IS NULL",
        "SELECT COUNT(*) FROM user_sessions us LEFT JOIN users u ON us.user_id = u.id WHERE u.id IS NULL",

        # Check for orphaned records
        "SELECT COUNT(*) FROM auth_tokens at LEFT JOIN users u ON at.user_id = u.id WHERE u.id IS NULL",
        "SELECT COUNT(*) FROM conversation_states cs LEFT JOIN users u ON cs.user_id = u.id WHERE u.id IS NULL",

        # Check data consistency
        "SELECT COUNT(*) FROM users WHERE email IS NULL OR email = ''",
        "SELECT COUNT(*) FROM roles WHERE name IS NULL OR name = ''",
    ]

    async with AsyncSessionLocal() as session:
        for i, check in enumerate(integrity_checks, 1):
            try:
                result = await session.execute(text(check))
                count = result.scalar()
                if count > 0:
                    print(f"⚠️  Integrity check {i}: Found {count} issues")
                else:
                    print(f"✅ Integrity check {i}: OK")
            except Exception as e:
                print(f"❌ Integrity check {i} failed: {e}")

if __name__ == "__main__":
    asyncio.run(validate_data_integrity())
```

### **Step 2: Authentication System Debug**

#### **2.1 JWT Token System Testing**

```python
# File: scripts/debug_jwt_system.py
import asyncio
from personal_assistant.auth.jwt_service import jwt_service
from personal_assistant.database.session import AsyncSessionLocal
from sqlalchemy import text

async def debug_jwt_system():
    """Debug JWT token generation and validation"""

    # Test with existing user
    async with AsyncSessionLocal() as session:
        result = await session.execute(text("SELECT id, email FROM users LIMIT 1"))
        user = result.fetchone()

        if not user:
            print("❌ No users found in database")
            return

        user_id, email = user
        print(f"🧪 Testing JWT with user: {email} (ID: {user_id})")

        # Test token generation
        try:
            access_token = jwt_service.create_access_token(user_id=user_id)
            print("✅ Access token generation: OK")

            refresh_token = jwt_service.create_refresh_token(user_id=user_id)
            print("✅ Refresh token generation: OK")

        except Exception as e:
            print(f"❌ Token generation failed: {e}")
            return

        # Test token validation
        try:
            payload = jwt_service.validate_token(access_token)
            print(f"✅ Token validation: OK (user_id: {payload.get('user_id')})")
        except Exception as e:
            print(f"❌ Token validation failed: {e}")

        # Test token refresh
        try:
            new_token = jwt_service.refresh_access_token(refresh_token)
            print("✅ Token refresh: OK")
        except Exception as e:
            print(f"❌ Token refresh failed: {e}")

if __name__ == "__main__":
    asyncio.run(debug_jwt_system())
```

#### **2.2 Session Management Testing**

```python
# File: scripts/debug_session_management.py
import asyncio
from personal_assistant.database.session import AsyncSessionLocal
from sqlalchemy import text
from personal_assistant.auth.session_manager import SessionManager

async def debug_session_management():
    """Debug session management system"""

    session_manager = SessionManager()

    async with AsyncSessionLocal() as session:
        # Check existing sessions
        result = await session.execute(text("""
            SELECT us.id, us.user_id, us.session_token, us.expires_at, us.is_active,
                   u.email
            FROM user_sessions us
            JOIN users u ON us.user_id = u.id
            ORDER BY us.created_at DESC
            LIMIT 5
        """))
        sessions = result.fetchall()

        print(f"📋 Found {len(sessions)} sessions")

        for sess in sessions:
            session_id, user_id, token, expires_at, is_active, email = sess
            print(f"  - Session {session_id}: {email} (Active: {is_active})")

        # Test session creation
        if sessions:
            user_id = sessions[0][1]
            try:
                new_session = await session_manager.create_session(user_id)
                print(f"✅ Session creation: OK (Token: {new_session.session_token[:20]}...)")
            except Exception as e:
                print(f"❌ Session creation failed: {e}")

if __name__ == "__main__":
    asyncio.run(debug_session_management())
```

### **Step 3: API Endpoint Testing**

#### **3.1 Comprehensive API Testing Script**

```python
# File: scripts/test_api_endpoints.py
import asyncio
import httpx
import json
from typing import Dict, List, Tuple

class APITester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = None
        self.auth_token = None

    async def __aenter__(self):
        self.session = httpx.AsyncClient(timeout=10.0)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.aclose()

    async def test_endpoint(self, method: str, endpoint: str,
                          data: Dict = None, headers: Dict = None) -> Tuple[int, Dict]:
        """Test a single API endpoint"""
        url = f"{self.base_url}{endpoint}"

        try:
            if method.upper() == "GET":
                response = await self.session.get(url, headers=headers)
            elif method.upper() == "POST":
                response = await self.session.post(url, json=data, headers=headers)
            elif method.upper() == "PUT":
                response = await self.session.put(url, json=data, headers=headers)
            elif method.upper() == "DELETE":
                response = await self.session.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported method: {method}")

            return response.status_code, response.json() if response.content else {}

        except httpx.TimeoutException:
            return 408, {"error": "Request timeout"}
        except httpx.ConnectError:
            return 503, {"error": "Connection refused"}
        except Exception as e:
            return 500, {"error": str(e)}

    async def test_authentication_flow(self):
        """Test complete authentication flow"""
        print("🔐 Testing Authentication Flow")

        # Test login endpoint
        login_data = {
            "email": "test@example.com",
            "password": "testpassword"
        }

        status, response = await self.test_endpoint("POST", "/api/v1/auth/login", login_data)
        print(f"  Login: {status} - {response}")

        if status == 200 and "access_token" in response:
            self.auth_token = response["access_token"]
            headers = {"Authorization": f"Bearer {self.auth_token}"}

            # Test protected endpoints
            protected_endpoints = [
                ("GET", "/api/v1/users/me"),
                ("GET", "/api/v1/chat/conversations"),
                ("GET", "/api/v1/oauth/providers"),
                ("GET", "/api/v1/analytics/sms/usage"),
            ]

            for method, endpoint in protected_endpoints:
                status, response = await self.test_endpoint(method, endpoint, headers=headers)
                print(f"  {method} {endpoint}: {status}")

        return self.auth_token is not None

    async def test_all_endpoints(self):
        """Test all API endpoints systematically"""
        print("🧪 Testing All API Endpoints")

        # Public endpoints
        public_endpoints = [
            ("GET", "/"),
            ("GET", "/health"),
            ("GET", "/docs"),
        ]

        for method, endpoint in public_endpoints:
            status, response = await self.test_endpoint(method, endpoint)
            print(f"  {method} {endpoint}: {status}")

        # Test authentication flow
        auth_success = await self.test_authentication_flow()

        if not auth_success:
            print("❌ Authentication failed - cannot test protected endpoints")
            return False

        return True

async def main():
    async with APITester() as tester:
        success = await tester.test_all_endpoints()
        if success:
            print("✅ All API tests completed successfully")
        else:
            print("❌ Some API tests failed")

if __name__ == "__main__":
    asyncio.run(main())
```

### **Step 4: Frontend Integration Testing**

#### **4.1 Frontend API Service Testing**

```typescript
// File: scripts/test-frontend-integration.ts
import axios from "axios";

class FrontendAPITester {
  private baseURL = "/api/v1";
  private authToken: string | null = null;

  async testAuthenticationFlow(): Promise<boolean> {
    console.log("🔐 Testing Frontend Authentication Flow");

    try {
      // Test login
      const loginResponse = await axios.post(`${this.baseURL}/auth/login`, {
        email: "test@example.com",
        password: "testpassword",
      });

      if (loginResponse.status === 200 && loginResponse.data.access_token) {
        this.authToken = loginResponse.data.access_token;
        console.log("✅ Login successful");

        // Set up axios interceptor
        axios.defaults.headers.common[
          "Authorization"
        ] = `Bearer ${this.authToken}`;

        return true;
      }
    } catch (error: any) {
      console.error("❌ Login failed:", error.response?.data || error.message);
    }

    return false;
  }

  async testProtectedEndpoints(): Promise<void> {
    console.log("🧪 Testing Protected Endpoints");

    const endpoints = [
      "/users/me",
      "/chat/conversations",
      "/oauth/providers",
      "/analytics/sms/usage",
    ];

    for (const endpoint of endpoints) {
      try {
        const response = await axios.get(`${this.baseURL}${endpoint}`);
        console.log(`✅ ${endpoint}: ${response.status}`);
      } catch (error: any) {
        console.error(
          `❌ ${endpoint}: ${error.response?.status} - ${
            error.response?.data?.detail || error.message
          }`
        );
      }
    }
  }

  async testTokenRefresh(): Promise<void> {
    console.log("🔄 Testing Token Refresh");

    try {
      const refreshToken = localStorage.getItem("refresh_token");
      if (!refreshToken) {
        console.log("⚠️  No refresh token found");
        return;
      }

      const response = await axios.post(`${this.baseURL}/auth/refresh`, {
        refresh_token: refreshToken,
      });

      if (response.status === 200) {
        console.log("✅ Token refresh successful");
        this.authToken = response.data.access_token;
      }
    } catch (error: any) {
      console.error(
        "❌ Token refresh failed:",
        error.response?.data || error.message
      );
    }
  }

  async runAllTests(): Promise<void> {
    console.log("🚀 Starting Frontend Integration Tests");

    const authSuccess = await this.testAuthenticationFlow();
    if (!authSuccess) {
      console.log("❌ Authentication failed - stopping tests");
      return;
    }

    await this.testProtectedEndpoints();
    await this.testTokenRefresh();

    console.log("✅ Frontend integration tests completed");
  }
}

// Run tests
const tester = new FrontendAPITester();
tester.runAllTests().catch(console.error);
```

### **Step 5: Database Restoration Scripts**

#### **5.1 Database Schema Validation and Repair**

```python
# File: scripts/repair_database_schema.py
import asyncio
from sqlalchemy import text, MetaData
from personal_assistant.database.session import AsyncSessionLocal
from personal_assistant.database.models import Base

async def repair_database_schema():
    """Repair database schema if needed"""

    async with AsyncSessionLocal() as session:
        # Check if all tables exist
        metadata = MetaData()
        await session.execute(text("SELECT 1"))  # Ensure connection works

        # Get existing tables
        result = await session.execute(text("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
        """))
        existing_tables = {row[0] for row in result.fetchall()}

        # Expected tables from models
        expected_tables = {
            'users', 'roles', 'permissions', 'user_roles', 'role_permissions',
            'user_sessions', 'auth_tokens', 'mfa_configurations', 'security_events',
            'conversation_states', 'conversation_messages', 'memory_context_items',
            'sms_router_configs', 'sms_usage_logs', 'user_phone_mappings',
            'todos', 'tasks', 'ai_tasks', 'reminders', 'events', 'expenses',
            'ltm_memories', 'ltm_contexts', 'ltm_memory_access', 'ltm_memory_relationships',
            'ltm_memory_tags', 'notes', 'grocery_items', 'grocery_deals',
            'grocery_analysis', 'expense_categories', 'recurrence_patterns',
            'event_creation_logs', 'event_processing_log', 'note_sync_log',
            'access_audit_logs', 'task_results'
        }

        missing_tables = expected_tables - existing_tables
        if missing_tables:
            print(f"⚠️  Missing tables: {missing_tables}")
            # Here you would run the appropriate migration scripts
        else:
            print("✅ All expected tables present")

        # Check foreign key constraints
        result = await session.execute(text("""
            SELECT
                tc.table_name,
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM
                information_schema.table_constraints AS tc
                JOIN information_schema.key_column_usage AS kcu
                  ON tc.constraint_name = kcu.constraint_name
                  AND tc.table_schema = kcu.table_schema
                JOIN information_schema.constraint_column_usage AS ccu
                  ON ccu.constraint_name = tc.constraint_name
                  AND ccu.table_schema = tc.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY'
            AND tc.table_schema='public'
        """))

        fk_constraints = result.fetchall()
        print(f"📋 Found {len(fk_constraints)} foreign key constraints")

        # Validate foreign key integrity
        for constraint in fk_constraints:
            table, column, ref_table, ref_column = constraint
            result = await session.execute(text(f"""
                SELECT COUNT(*) FROM {table} t1
                LEFT JOIN {ref_table} t2 ON t1.{column} = t2.{ref_column}
                WHERE t2.{ref_column} IS NULL AND t1.{column} IS NOT NULL
            """))
            orphaned_count = result.scalar()
            if orphaned_count > 0:
                print(f"⚠️  {table}.{column} has {orphaned_count} orphaned records")

if __name__ == "__main__":
    asyncio.run(repair_database_schema())
```

#### **5.2 Data Recovery and Cleanup**

```python
# File: scripts/recover_and_cleanup_data.py
import asyncio
from sqlalchemy import text
from personal_assistant.database.session import AsyncSessionLocal

async def recover_and_cleanup_data():
    """Recover and cleanup data after database crash"""

    async with AsyncSessionLocal() as session:
        # Clean up invalid sessions
        result = await session.execute(text("""
            DELETE FROM user_sessions
            WHERE expires_at < NOW() OR user_id NOT IN (SELECT id FROM users)
        """))
        print(f"🧹 Cleaned up {result.rowcount} invalid sessions")

        # Clean up invalid auth tokens
        result = await session.execute(text("""
            DELETE FROM auth_tokens
            WHERE expires_at < NOW() OR user_id NOT IN (SELECT id FROM users)
        """))
        print(f"🧹 Cleaned up {result.rowcount} invalid auth tokens")

        # Clean up orphaned conversation data
        result = await session.execute(text("""
            DELETE FROM conversation_messages
            WHERE conversation_id NOT IN (SELECT conversation_id FROM conversation_states)
        """))
        print(f"🧹 Cleaned up {result.rowcount} orphaned conversation messages")

        # Clean up orphaned memory context items
        result = await session.execute(text("""
            DELETE FROM memory_context_items
            WHERE conversation_id NOT IN (SELECT conversation_id FROM conversation_states)
        """))
        print(f"🧹 Cleaned up {result.rowcount} orphaned memory context items")

        # Update user settings with defaults if missing
        result = await session.execute(text("""
            INSERT INTO user_settings (user_id, settings_key, settings_value, created_at)
            SELECT u.id, 'default_preferences', '{}', NOW()
            FROM users u
            LEFT JOIN user_settings us ON u.id = us.user_id AND us.settings_key = 'default_preferences'
            WHERE us.id IS NULL
        """))
        print(f"🔧 Added default settings for {result.rowcount} users")

        # Commit all changes
        await session.commit()
        print("✅ Data recovery and cleanup completed")

if __name__ == "__main__":
    asyncio.run(recover_and_cleanup_data())
```

## 🚀 **Execution Plan**

### **Day 1: Database Analysis and Authentication Fix**

1. Run database health check scripts
2. Validate data integrity
3. Debug and fix JWT token system
4. Test session management
5. Run API endpoint tests

### **Day 2: API Restoration and Frontend Integration**

1. Fix any remaining API issues
2. Test frontend integration
3. Validate OAuth system
4. Test chat functionality
5. Verify analytics endpoints

### **Day 3: System Validation and Testing**

1. Run comprehensive system tests
2. Performance validation
3. Security checks
4. End-to-end testing
5. Documentation updates

## 📊 **Monitoring and Validation**

### **Success Metrics**

- All API endpoints return correct status codes
- Authentication flow works end-to-end
- Frontend can successfully make API calls
- Database queries perform within acceptable limits
- No critical errors in system logs

### **Rollback Plan**

- Database backup before any changes
- Git commit before modifications
- Ability to restore from backup
- Emergency contact procedures

---

**Implementation Status**: 🚀 **READY TO START**  
**Estimated Time**: 3 days  
**Risk Level**: Medium (with proper backups)  
**Dependencies**: None
