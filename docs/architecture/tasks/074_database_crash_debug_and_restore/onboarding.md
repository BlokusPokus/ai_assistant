# Onboarding Guide - Database Crash Debug and Restore

## 🎯 **Task Overview**

**Task ID**: 074  
**Title**: Database Crash Debug and Restore  
**Status**: 🚀 Ready to Start  
**Priority**: 🔴 Critical  
**Estimated Effort**: 3 days  

## 📋 **Problem Context**

After a database crash, the personal assistant system has lost some functionality. While the database is accessible and contains data, API calls from the frontend are failing, indicating issues with the authentication system and potentially other core components.

## 🔍 **Current System State**

### **✅ What's Working**
- Database connection is functional
- 38 tables are present in the database
- 1 user account exists
- FastAPI server is running
- Basic endpoints (/, /health) are responding

### **❌ What's Broken**
- Authentication system (protected endpoints returning 401)
- JWT token validation may be corrupted
- User sessions likely affected
- Frontend-backend integration failing
- API calls from frontend not working

## 🏗️ **System Architecture Overview**

### **Database Layer**
- **PostgreSQL** with 38 tables
- **SQLAlchemy** ORM with async support
- **Connection pooling** configured
- **Migration system** in place

### **Backend API Layer**
- **FastAPI** application
- **JWT-based authentication**
- **RBAC system** for permissions
- **Session management** with Redis
- **Multiple API modules**: auth, users, chat, OAuth, SMS, analytics

### **Frontend Layer**
- **React** with TypeScript
- **Axios** for API calls
- **JWT token management**
- **Protected routing**
- **Multiple services**: auth, chat, OAuth, profile

## 🛠️ **Available Tools and Scripts**

### **Debugging Scripts** (Ready to Use)
1. **`scripts/debug_database_health.py`** - Comprehensive database health check
2. **`scripts/debug_jwt_system.py`** - JWT token system testing
3. **`scripts/test_api_endpoints.py`** - Complete API endpoint testing

### **Database Tools**
- **Migration manager**: `src/personal_assistant/database/migrations/manager.py`
- **Session management**: `src/personal_assistant/database/session.py`
- **Model definitions**: `src/personal_assistant/database/models/`

### **Authentication System**
- **JWT service**: `src/personal_assistant/auth/jwt_service.py`
- **Session manager**: `src/personal_assistant/auth/session_manager.py`
- **Auth middleware**: `src/apps/fastapi_app/middleware/auth.py`

## 🚀 **Getting Started**

### **Step 1: Environment Setup**
```bash
# Activate virtual environment
source venv_personal_assistant/bin/activate

# Verify database connection
python scripts/debug_database_health.py
```

### **Step 2: Run Initial Diagnostics**
```bash
# Test JWT system
python scripts/debug_jwt_system.py

# Test API endpoints
python scripts/test_api_endpoints.py
```

### **Step 3: Identify Root Cause**
Based on the diagnostic results, identify the specific issues:
- Database integrity problems
- JWT token system failures
- Session management issues
- API endpoint problems

## 📊 **Expected Issues and Solutions**

### **Common Issues After Database Crash**

#### **1. JWT Token System Failure**
- **Symptoms**: 401 errors on protected endpoints
- **Causes**: Corrupted JWT secret, invalid token storage
- **Solution**: Regenerate JWT secrets, clear invalid tokens

#### **2. Session Management Issues**
- **Symptoms**: Users can't stay logged in
- **Causes**: Corrupted session data, Redis connection issues
- **Solution**: Clear session cache, verify Redis connection

#### **3. Database Integrity Problems**
- **Symptoms**: Foreign key constraint violations
- **Causes**: Orphaned records, missing references
- **Solution**: Clean up orphaned data, restore referential integrity

#### **4. API Endpoint Failures**
- **Symptoms**: 500 errors, unexpected responses
- **Causes**: Database query failures, missing data
- **Solution**: Fix queries, restore missing data

## 🔧 **Debugging Workflow**

### **Phase 1: Database Analysis** (Day 1)
1. Run database health check
2. Validate data integrity
3. Check foreign key relationships
4. Identify missing or corrupted data

### **Phase 2: Authentication Debug** (Day 1-2)
1. Test JWT token generation
2. Verify token validation
3. Check session management
4. Test authentication flow

### **Phase 3: API Restoration** (Day 2)
1. Fix identified API issues
2. Test all endpoints
3. Verify response formats
4. Check error handling

### **Phase 4: Frontend Integration** (Day 2-3)
1. Test frontend API calls
2. Verify token refresh
3. Check error handling
4. Test complete workflows

### **Phase 5: System Validation** (Day 3)
1. Run comprehensive tests
2. Verify performance
3. Check security
4. Document fixes

## 📚 **Key Files to Understand**

### **Database Models**
- `src/personal_assistant/database/models/users.py` - User management
- `src/personal_assistant/database/models/rbac.py` - Roles and permissions
- `src/personal_assistant/database/models/sessions.py` - Session management

### **Authentication System**
- `src/personal_assistant/auth/jwt_service.py` - JWT token handling
- `src/personal_assistant/auth/session_manager.py` - Session management
- `src/apps/fastapi_app/middleware/auth.py` - Authentication middleware

### **API Endpoints**
- `src/apps/fastapi_app/routes/auth.py` - Authentication endpoints
- `src/apps/fastapi_app/routes/users.py` - User management
- `src/apps/fastapi_app/routes/chat.py` - Chat functionality

### **Frontend Services**
- `src/apps/frontend/src/services/api.ts` - API client configuration
- `src/apps/frontend/src/services/auth.ts` - Authentication service
- `src/apps/frontend/src/services/chatApi.ts` - Chat API service

## 🚨 **Critical Success Factors**

### **Must Fix**
1. **Authentication system** - Users must be able to log in
2. **Protected endpoints** - Must return proper responses
3. **Frontend integration** - API calls must work
4. **Data integrity** - Database must be consistent

### **Nice to Have**
1. **Performance optimization** - Fast response times
2. **Error handling** - Graceful error messages
3. **Logging** - Comprehensive debug information
4. **Monitoring** - System health indicators

## 📝 **Documentation Requirements**

### **Deliverables**
1. **Database Health Report** - Analysis of database state
2. **Authentication Fix Report** - Details of auth system repairs
3. **API Restoration Report** - Status of endpoint fixes
4. **Integration Test Results** - Frontend-backend validation
5. **System Performance Report** - Performance metrics

### **Code Documentation**
- Document all fixes made
- Update configuration if needed
- Add comments for complex debugging logic
- Update README files if necessary

## 🔄 **Testing Strategy**

### **Unit Tests**
- Database model validation
- JWT token system tests
- API endpoint tests
- Service layer tests

### **Integration Tests**
- Database connection tests
- API integration tests
- Frontend service tests
- End-to-end workflow tests

### **Performance Tests**
- Database query performance
- API response time tests
- Memory usage monitoring
- Load testing

## 🚀 **Next Steps**

1. **Start with database health check** - Run `scripts/debug_database_health.py`
2. **Test JWT system** - Run `scripts/debug_jwt_system.py`
3. **Test API endpoints** - Run `scripts/test_api_endpoints.py`
4. **Identify root cause** - Analyze results and determine fixes needed
5. **Implement fixes** - Follow the technical implementation guide
6. **Validate fixes** - Re-run tests to ensure everything works
7. **Document results** - Update documentation with fixes made

## 📞 **Support and Resources**

### **Key Documentation**
- [Database Schema Summary](../../database/DATABASE_SCHEMA_SUMMARY.md)
- [Authentication System Guide](../030_core_authentication_service/README.md)
- [API Development Guide](../036_api_development/README.md)
- [Frontend Integration Guide](../../FRONTEND_BACKEND_INTEGRATION.md)

### **Configuration Files**
- `config/development.env` - Development configuration
- `src/personal_assistant/config/settings.py` - Application settings
- `src/personal_assistant/config/database.py` - Database configuration

---

**Ready to start debugging!** 🚀

Remember: Take it step by step, document everything, and don't hesitate to ask questions if you encounter unexpected issues.
