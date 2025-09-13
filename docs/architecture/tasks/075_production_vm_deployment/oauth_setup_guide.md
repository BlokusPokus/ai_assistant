# OAuth Setup Guide - Google & Microsoft Integration

## 🎯 Overview

This guide provides detailed instructions for setting up OAuth 2.0 integration with Google and Microsoft services for the Personal Assistant TDAH application. These integrations are required for calendar, email, and file management functionality.

## 🔑 Prerequisites

- Production domain configured (e.g., `yourdomain.com`)
- SSL certificate installed and working
- Application deployed and accessible via HTTPS

## 🟦 Google OAuth Setup

### **Step 1: Google Cloud Console Setup**

1. **Access Google Cloud Console**

   - Navigate to [Google Cloud Console](https://console.cloud.google.com/)
   - Sign in with your Google account

2. **Create or Select Project**

   ```
   Option A: Create New Project
   - Click "Select a project" → "NEW PROJECT"
   - Project name: "Personal Assistant TDAH"
   - Organization: (optional)
   - Click "CREATE"

   Option B: Use Existing Project
   - Select your existing project from dropdown
   ```

### **Step 2: Enable Required APIs**

Enable the following APIs for your project:

1. **Google Calendar API**

   - Go to "APIs & Services" → "Library"
   - Search for "Google Calendar API"
   - Click on it and press "ENABLE"

2. **Gmail API**

   - Search for "Gmail API"
   - Click on it and press "ENABLE"

3. **Google Drive API**

   - Search for "Google Drive API"
   - Click on it and press "ENABLE"

4. **YouTube Data API v3** (optional)
   - Search for "YouTube Data API v3"
   - Click on it and press "ENABLE"

### **Step 3: Configure OAuth Consent Screen**

1. **Navigate to OAuth Consent Screen**

   - Go to "APIs & Services" → "OAuth consent screen"

2. **Choose User Type**

   ```
   For Development/Testing: Internal
   For Production: External
   ```

3. **App Information**

   ```
   App name: Personal Assistant TDAH
   User support email: your-email@yourdomain.com
   App logo: (optional - upload your app logo)
   ```

4. **App Domain**

   ```
   Application home page: https://yourdomain.com
   Application privacy policy link: https://yourdomain.com/privacy
   Application terms of service link: https://yourdomain.com/terms
   ```

5. **Developer Contact Information**

   ```
   Email addresses: your-email@yourdomain.com
   ```

6. **Scopes Configuration**

   - Click "ADD OR REMOVE SCOPES"
   - Add the following scopes:

   ```
   https://www.googleapis.com/auth/userinfo.email
   https://www.googleapis.com/auth/userinfo.profile
   https://www.googleapis.com/auth/calendar
   https://www.googleapis.com/auth/gmail.readonly
   https://www.googleapis.com/auth/gmail.send
   https://www.googleapis.com/auth/drive.file
   https://www.googleapis.com/auth/youtube.readonly (optional)
   ```

7. **Test Users** (for External apps in testing)
   - Add your test user email addresses
   - These users can access your app during testing phase

### **Step 4: Create OAuth 2.0 Credentials**

1. **Navigate to Credentials**

   - Go to "APIs & Services" → "Credentials"

2. **Create Credentials**

   - Click "CREATE CREDENTIALS" → "OAuth 2.0 Client ID"

3. **Configure OAuth Client**

   ```
   Application type: Web application
   Name: Personal Assistant TDAH Production
   ```

4. **Authorized JavaScript Origins**

   ```
   https://yourdomain.com
   ```

5. **Authorized Redirect URIs**

   ```
   https://yourdomain.com/api/oauth/google/callback
   https://yourdomain.com/oauth/google/callback
   ```

6. **Save and Copy Credentials**
   - Click "CREATE"
   - Copy the Client ID and Client Secret
   - Store them securely (you'll need them for environment variables)

### **Step 5: Domain Verification** (if required)

1. **Search Console Verification**
   - Go to [Google Search Console](https://search.google.com/search-console)
   - Add and verify your domain
   - This may be required for certain API access

## 🟦 Microsoft OAuth Setup

### **Step 1: Azure Portal Access**

1. **Access Azure Portal**

   - Navigate to [Azure Portal](https://portal.azure.com/)
   - Sign in with your Microsoft account

2. **Navigate to Azure Active Directory**
   - Search for "Azure Active Directory" in the search bar
   - Click on "Azure Active Directory"

### **Step 2: App Registration**

1. **Create New App Registration**

   - Go to "App registrations" in the left sidebar
   - Click "New registration"

2. **Configure App Registration**

   ```
   Name: Personal Assistant TDAH Production

   Supported account types:
   ✓ Accounts in any organizational directory (Any Azure AD directory - Multitenant)
     and personal Microsoft accounts (e.g. Skype, Xbox)

   Redirect URI:
   Platform: Web
   Redirect URI: https://yourdomain.com/api/oauth/microsoft/callback
   ```

3. **Register Application**
   - Click "Register"
   - Note down the Application (client) ID

### **Step 3: Configure Authentication**

1. **Add Additional Redirect URIs**

   - Go to "Authentication" in the left sidebar
   - Under "Redirect URIs", add:

   ```
   https://yourdomain.com/oauth/microsoft/callback
   ```

2. **Configure Platform Settings**

   ```
   Access tokens (used for implicit flows): ✓ Checked
   ID tokens (used for implicit and hybrid flows): ✓ Checked
   ```

3. **Advanced Settings**
   ```
   Allow public client flows: No
   ```

### **Step 4: API Permissions**

1. **Navigate to API Permissions**

   - Click "API permissions" in the left sidebar

2. **Add Microsoft Graph Permissions**

   - Click "Add a permission"
   - Select "Microsoft Graph"
   - Choose "Delegated permissions"

3. **Required Permissions**

   ```
   User.Read (usually added by default)
   Calendars.ReadWrite
   Mail.ReadWrite
   Mail.Send
   Files.ReadWrite.All
   offline_access
   ```

4. **Grant Admin Consent** (if required)
   - Click "Grant admin consent for [Your Organization]"
   - This may be required depending on your Azure AD setup

### **Step 5: Certificates & Secrets**

1. **Create Client Secret**

   - Go to "Certificates & secrets"
   - Click "New client secret"

2. **Configure Secret**

   ```
   Description: Personal Assistant TDAH Production Secret
   Expires: 24 months (recommended)
   ```

3. **Copy Secret Value**
   - Click "Add"
   - **IMPORTANT**: Copy the secret value immediately
   - You won't be able to see it again
   - Store it securely

### **Step 6: Branding (Optional)**

1. **Configure App Branding**
   - Go to "Branding"
   - Add your app logo, terms of service, privacy statement

## 🔧 Environment Configuration

### **Update Production Environment Variables**

Add the following to your `docker/.env.prod` file:

```bash
# Google OAuth Configuration
GOOGLE_OAUTH_CLIENT_ID=your_google_client_id.apps.googleusercontent.com
GOOGLE_OAUTH_CLIENT_SECRET=your_google_client_secret_here
GOOGLE_OAUTH_REDIRECT_URI=https://yourdomain.com/api/oauth/google/callback

# Microsoft OAuth Configuration
MICROSOFT_OAUTH_CLIENT_ID=your_microsoft_application_id_here
MICROSOFT_OAUTH_CLIENT_SECRET=your_microsoft_client_secret_here
MICROSOFT_OAUTH_REDIRECT_URI=https://yourdomain.com/api/oauth/microsoft/callback

# Additional OAuth Settings
OAUTH_STATE_SECRET=your_oauth_state_secret_minimum_32_characters
OAUTH_SESSION_TIMEOUT=3600
```

### **Restart Application**

```bash
# Restart the application to load new environment variables
cd /home/deploy/personal_assistant
docker-compose -f docker/docker-compose.prod.yml down
docker-compose -f docker/docker-compose.prod.yml up -d
```

## 🧪 Testing OAuth Integration

### **Test Google OAuth Flow**

1. **Access Authorization URL**

   ```
   https://yourdomain.com/api/oauth/google/authorize?scopes=calendar,gmail
   ```

2. **Expected Flow**

   - Redirects to Google login page
   - User logs in and grants permissions
   - Redirects back to your callback URL
   - Application receives authorization code
   - Exchanges code for access and refresh tokens

3. **Test API Access**
   ```bash
   # Test calendar access (after successful OAuth)
   curl -H "Authorization: Bearer ACCESS_TOKEN" \
        "https://www.googleapis.com/calendar/v3/calendars/primary/events"
   ```

### **Test Microsoft OAuth Flow**

1. **Access Authorization URL**

   ```
   https://yourdomain.com/api/oauth/microsoft/authorize?scopes=calendar,mail
   ```

2. **Expected Flow**

   - Redirects to Microsoft login page
   - User logs in and grants permissions
   - Redirects back to your callback URL
   - Application receives authorization code
   - Exchanges code for access and refresh tokens

3. **Test API Access**
   ```bash
   # Test calendar access (after successful OAuth)
   curl -H "Authorization: Bearer ACCESS_TOKEN" \
        "https://graph.microsoft.com/v1.0/me/calendar/events"
   ```

## 🔍 Troubleshooting

### **Common Google OAuth Issues**

#### **Issue: "redirect_uri_mismatch" Error**

```
Solution:
1. Check that redirect URI in Google Console exactly matches:
   https://yourdomain.com/api/oauth/google/callback
2. Ensure no trailing slashes or extra characters
3. Verify domain is accessible via HTTPS
```

#### **Issue: "access_denied" Error**

```
Solution:
1. Check OAuth consent screen configuration
2. Ensure app is published (for external users)
3. Verify user is added to test users (for testing apps)
4. Check required scopes are properly configured
```

#### **Issue: "invalid_client" Error**

```
Solution:
1. Verify GOOGLE_OAUTH_CLIENT_ID is correct
2. Verify GOOGLE_OAUTH_CLIENT_SECRET is correct
3. Check environment variables are loaded in container
```

### **Common Microsoft OAuth Issues**

#### **Issue: "AADSTS50011: redirect_uri_mismatch"**

```
Solution:
1. Check redirect URI in Azure App Registration:
   https://yourdomain.com/api/oauth/microsoft/callback
2. Ensure URI is exactly as configured
3. Check for case sensitivity
```

#### **Issue: "AADSTS65001: consent_required"**

```
Solution:
1. Verify API permissions are properly configured
2. Grant admin consent if required
3. Check user has permission to consent to applications
```

#### **Issue: "invalid_client" Error**

```
Solution:
1. Verify MICROSOFT_OAUTH_CLIENT_ID is correct
2. Verify MICROSOFT_OAUTH_CLIENT_SECRET is correct and not expired
3. Check client secret expiration date
```

### **Debug OAuth Issues**

#### **Check Application Logs**

```bash
# Check API logs for OAuth errors
docker-compose -f docker/docker-compose.prod.yml logs -f api | grep -i oauth

# Check nginx logs for redirect issues
docker-compose -f docker/docker-compose.prod.yml logs -f nginx | grep -i oauth
```

#### **Verify Environment Variables**

```bash
# Check OAuth environment variables are loaded
docker-compose -f docker/docker-compose.prod.yml exec api env | grep -i oauth
```

#### **Test Callback URLs**

```bash
# Test callback URL accessibility
curl -I https://yourdomain.com/api/oauth/google/callback
curl -I https://yourdomain.com/api/oauth/microsoft/callback
```

## 📋 OAuth Scopes Reference

### **Google Scopes**

| Scope                                              | Purpose                    | Permission Level |
| -------------------------------------------------- | -------------------------- | ---------------- |
| `https://www.googleapis.com/auth/userinfo.email`   | User email address         | Read             |
| `https://www.googleapis.com/auth/userinfo.profile` | User profile info          | Read             |
| `https://www.googleapis.com/auth/calendar`         | Calendar access            | Read/Write       |
| `https://www.googleapis.com/auth/gmail.readonly`   | Read Gmail                 | Read             |
| `https://www.googleapis.com/auth/gmail.send`       | Send emails                | Write            |
| `https://www.googleapis.com/auth/drive.file`       | Drive files created by app | Read/Write       |

### **Microsoft Scopes**

| Scope                 | Purpose         | Permission Level |
| --------------------- | --------------- | ---------------- |
| `User.Read`           | User profile    | Read             |
| `Calendars.ReadWrite` | Calendar access | Read/Write       |
| `Mail.ReadWrite`      | Email access    | Read/Write       |
| `Mail.Send`           | Send emails     | Write            |
| `Files.ReadWrite.All` | OneDrive files  | Read/Write       |
| `offline_access`      | Refresh tokens  | -                |

## 🔒 Security Best Practices

### **OAuth Security Checklist**

- [ ] **Use HTTPS Only**: All OAuth URLs must use HTTPS
- [ ] **Validate State Parameter**: Prevent CSRF attacks
- [ ] **Secure Token Storage**: Store tokens encrypted in database
- [ ] **Token Refresh**: Implement automatic token refresh
- [ ] **Scope Limitation**: Request only necessary scopes
- [ ] **Regular Audits**: Monitor OAuth usage and permissions

### **Token Management**

```bash
# Tokens should be stored encrypted in database
# Implement token refresh before expiration
# Log all OAuth events for security auditing
```

## 📚 Additional Resources

### **Google OAuth Documentation**

- [Google OAuth 2.0 Guide](https://developers.google.com/identity/protocols/oauth2)
- [Google API Scopes](https://developers.google.com/identity/protocols/oauth2/scopes)
- [Google Calendar API](https://developers.google.com/calendar/api/guides/overview)

### **Microsoft OAuth Documentation**

- [Microsoft OAuth 2.0 Guide](https://docs.microsoft.com/en-us/azure/active-directory/develop/v2-oauth2-auth-code-flow)
- [Microsoft Graph Permissions](https://docs.microsoft.com/en-us/graph/permissions-reference)
- [Microsoft Graph API](https://docs.microsoft.com/en-us/graph/overview)

---

This OAuth setup guide ensures proper integration with Google and Microsoft services for your Personal Assistant TDAH application.
