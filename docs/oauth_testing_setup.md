# OAuth Testing Setup Guide

## 🚀 **Real OAuth Testing Setup**

This guide will help you set up real OAuth credentials to test the OAuth system with actual providers.

## 📋 **Prerequisites**

- Personal Assistant backend running on Port 8000
- OAuth system fully implemented (Task 043 completed)
- Access to OAuth provider developer consoles

## 🔑 **Setting Up OAuth Provider Credentials**

### **1. Google OAuth Setup**

#### **Step 1: Create Google Cloud Project**

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the Google+ API and Google OAuth2 API

#### **Step 2: Configure OAuth Consent Screen**

1. Go to "APIs & Services" > "OAuth consent screen"
2. Choose "External" user type
3. Fill in app information:
   - App name: "Personal Assistant"
   - User support email: Your email
   - Developer contact information: Your email

#### **Step 3: Create OAuth 2.0 Credentials**

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth 2.0 Client IDs"
3. Choose "Web application"
4. Set authorized redirect URIs:
   - `http://localhost:8000/api/v1/oauth/callback`
   - `http://127.0.0.1:8000/api/v1/oauth/callback`
5. Copy the Client ID and Client Secret

#### **Step 4: Update Environment Variables**

```bash
# Add to your .env file or environment
export GOOGLE_OAUTH_CLIENT_ID="your_google_client_id"
export GOOGLE_OAUTH_CLIENT_SECRET="your_google_client_secret"
export GOOGLE_OAUTH_REDIRECT_URI="http://localhost:8000/api/v1/oauth/callback"
```

### **2. Microsoft OAuth Setup**

#### **Step 1: Create Azure App Registration**

1. Go to [Azure Portal](https://portal.azure.com/)
2. Navigate to "Azure Active Directory" > "App registrations"
3. Click "New registration"
4. Fill in details:
   - Name: "Personal Assistant"
   - Supported account types: "Accounts in this organizational directory only"
   - Redirect URI: Web > `http://localhost:8000/api/v1/oauth/callback`

#### **Step 2: Get Client Credentials**

1. From the app overview, copy the "Application (client) ID"
2. Go to "Certificates & secrets"
3. Create a new client secret and copy the value

#### **Step 3: Configure API Permissions**

1. Go to "API permissions"
2. Add permissions:
   - Microsoft Graph > Delegated > User.Read
   - Microsoft Graph > Delegated > Calendars.Read
   - Microsoft Graph > Delegated > Files.Read

#### **Step 4: Update Environment Variables**

```bash
export MICROSOFT_OAUTH_CLIENT_ID="your_azure_client_id"
export MICROSOFT_OAUTH_CLIENT_SECRET="your_azure_client_secret"
export MICROSOFT_OAUTH_REDIRECT_URI="http://localhost:8000/api/v1/oauth/callback"
```

### **3. Notion OAuth Setup**

#### **Step 1: Create Notion Integration**

1. Go to [Notion Developers](https://developers.notion.com/)
2. Click "New integration"
3. Fill in details:
   - Name: "Personal Assistant"
   - Associated workspace: Select your workspace
   - Capabilities: Read content, Update content

#### **Step 2: Get Integration Credentials**

1. Copy the "Internal Integration Token"
2. Note the "Integration ID"

#### **Step 3: Update Environment Variables**

```bash
export NOTION_OAUTH_CLIENT_ID="your_notion_integration_id"
export NOTION_OAUTH_CLIENT_SECRET="your_notion_integration_token"
export NOTION_OAUTH_REDIRECT_URI="http://localhost:8000/api/v1/oauth/callback"
```

### **4. YouTube OAuth Setup**

#### **Step 1: Create Google Cloud Project (Same as Google OAuth)**

1. Use the same Google Cloud project from Google OAuth setup
2. Enable YouTube Data API v3

#### **Step 2: Create OAuth 2.0 Credentials for YouTube**

1. Go to "APIs & Services" > "Credentials"
2. Create another OAuth 2.0 Client ID
3. Set redirect URI: `http://localhost:8000/api/v1/oauth/callback`

#### **Step 3: Update Environment Variables**

```bash
export YOUTUBE_OAUTH_CLIENT_ID="your_youtube_client_id"
export YOUTUBE_OAUTH_CLIENT_SECRET="your_youtube_client_secret"
export YOUTUBE_OAUTH_REDIRECT_URI="http://localhost:8000/api/v1/oauth/callback"
```

## 🧪 **Testing the OAuth System**

### **Step 1: Start the Backend**

```bash
# Activate virtual environment
source venv_personal_assistant/bin/activate

# Start the FastAPI backend
cd src/apps/fastapi_app
python main.py
```

### **Step 2: Test OAuth Endpoints**

#### **Test OAuth Providers Endpoint**

```bash
# Get available OAuth providers
curl -X GET "http://localhost:8000/api/v1/oauth/providers" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

#### **Test OAuth Flow Initiation**

```bash
# Initiate Google OAuth flow
curl -X POST "http://localhost:8000/api/v1/oauth/initiate" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "google",
    "scopes": ["openid", "email", "profile"],
    "redirect_uri": "http://localhost:8000/api/v1/oauth/callback"
  }'
```

### **Step 3: Complete OAuth Flow**

1. **Get Authorization URL**: The initiate endpoint returns an authorization URL
2. **User Authorization**: Open the URL in browser, user logs in and grants permissions
3. **Callback Handling**: OAuth provider redirects to your callback URL with authorization code
4. **Token Exchange**: Backend exchanges code for access/refresh tokens
5. **Integration Creation**: OAuth integration is created in database

### **Step 4: Test OAuth Integration**

#### **Get User Integrations**

```bash
curl -X GET "http://localhost:8000/api/v1/oauth/integrations" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

#### **Get OAuth Status**

```bash
curl -X GET "http://localhost:8000/api/v1/oauth/status" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## 🔍 **Testing Scenarios**

### **Scenario 1: Complete OAuth Flow**

1. User initiates OAuth flow with Google
2. User authorizes the application
3. Verify tokens are stored and encrypted
4. Verify integration is created in database

### **Scenario 2: Token Refresh**

1. Wait for access token to expire (or manually expire it)
2. Test token refresh functionality
3. Verify new tokens are generated

### **Scenario 3: Multiple Providers**

1. Test OAuth flow with different providers
2. Verify each provider creates separate integrations
3. Test provider-specific functionality

### **Scenario 4: Error Handling**

1. Test with invalid authorization codes
2. Test with expired state tokens
3. Test with revoked permissions

## 🐛 **Debugging OAuth Issues**

### **Common Issues and Solutions**

#### **1. Redirect URI Mismatch**

- **Error**: "redirect_uri_mismatch"
- **Solution**: Ensure redirect URI in OAuth app matches exactly

#### **2. Invalid Client ID/Secret**

- **Error**: "invalid_client"
- **Solution**: Verify environment variables are set correctly

#### **3. State Token Issues**

- **Error**: "invalid_state"
- **Solution**: Check state token generation and validation

#### **4. Scope Issues**

- **Error**: "invalid_scope"
- **Solution**: Verify requested scopes are valid for the provider

### **Debug Commands**

```bash
# Check environment variables
env | grep OAUTH

# Check backend logs
tail -f logs/oauth.log

# Test database connection
python -c "from src.personal_assistant.database.session import AsyncSessionLocal; print('DB connection OK')"
```

## 📊 **Monitoring and Validation**

### **Check Database Tables**

```sql
-- Check OAuth integrations
SELECT * FROM oauth_integrations;

-- Check OAuth tokens
SELECT * FROM oauth_tokens;

-- Check OAuth audit logs
SELECT * FROM oauth_audit_logs;
```

### **Check Application Logs**

```bash
# Monitor OAuth-related logs
grep "oauth" logs/app.log

# Check for errors
grep "ERROR" logs/app.log | grep "oauth"
```

## 🎯 **Success Criteria**

Your OAuth system is working correctly when:

✅ **OAuth Flow**: Users can complete OAuth flows with all providers  
✅ **Token Storage**: Access and refresh tokens are encrypted and stored  
✅ **Integration Management**: OAuth integrations are created and managed  
✅ **Security**: State validation and CSRF protection work correctly  
✅ **Error Handling**: Invalid requests are handled gracefully  
✅ **Audit Logging**: All OAuth operations are logged for security

## 🚀 **Next Steps After Testing**

1. **Production Deployment**: Update redirect URIs for production domain
2. **Security Review**: Validate OAuth security measures
3. **Performance Testing**: Test with multiple concurrent OAuth flows
4. **Frontend Integration**: Connect OAuth system to user interface
5. **Monitoring**: Set up alerts for OAuth failures and security events

---

**Note**: Always test with test accounts first before using production accounts. OAuth credentials should be kept secure and never committed to version control.
