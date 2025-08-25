# 🚀 Quick OAuth Setup Guide

## **Issue**: OAuth Refresh Failing (500 Error)

The OAuth refresh endpoint is currently failing because **OAuth provider credentials are not configured** in the backend.

## **Quick Fix**: Set Environment Variables

Add these environment variables to your backend `.env` file:

```bash
# Google OAuth
GOOGLE_OAUTH_CLIENT_ID=your_google_client_id_here
GOOGLE_OAUTH_CLIENT_SECRET=your_google_client_secret_here
GOOGLE_OAUTH_REDIRECT_URI=http://localhost:8000/api/v1/oauth/callback

# Microsoft OAuth
MICROSOFT_OAUTH_CLIENT_ID=your_microsoft_client_id_here
MICROSOFT_OAUTH_CLIENT_SECRET=your_microsoft_client_secret_here
MICROSOFT_OAUTH_REDIRECT_URI=http://localhost:8000/api/v1/oauth/callback

# Notion OAuth
NOTION_OAUTH_CLIENT_ID=your_notion_client_id_here
NOTION_OAUTH_CLIENT_SECRET=your_notion_client_secret_here
NOTION_OAUTH_REDIRECT_URI=http://localhost:8000/api/v1/oauth/callback

# YouTube OAuth
YOUTUBE_OAUTH_CLIENT_ID=your_youtube_client_id_here
YOUTUBE_OAUTH_CLIENT_SECRET=your_youtube_client_secret_here
YOUTUBE_OAUTH_REDIRECT_URI=http://localhost:8000/api/v1/oauth/callback
```

## **Get OAuth Credentials**

### **1. Google OAuth**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create/select project → APIs & Services → Credentials
3. Create OAuth 2.0 Client ID
4. Set redirect URI: `http://localhost:8000/api/v1/oauth/callback`

### **2. Microsoft OAuth**
1. Go to [Azure Portal](https://portal.azure.com/)
2. Azure Active Directory → App registrations → New registration
3. Set redirect URI: `http://localhost:8000/api/v1/oauth/callback`

### **3. Notion OAuth**
1. Go to [Notion Developers](https://developers.notion.com/)
2. Create new integration
3. Copy Integration ID and Internal Integration Token

### **4. YouTube OAuth**
1. Use same Google Cloud project as Google OAuth
2. Enable YouTube Data API v3
3. Create separate OAuth 2.0 Client ID for YouTube

## **Restart Backend**

After setting environment variables:

```bash
# Stop backend
Ctrl+C

# Restart backend
cd src
source ../venv_personal_assistant/bin/activate
uvicorn apps.fastapi_app.main:app --reload --host 0.0.0.0 --port 8000
```

## **Test OAuth Refresh**

1. Go to `/dashboard/oauth-settings`
2. Click "Refresh" on any integration
3. Should now work without 500 errors

## **Note**

- **Development**: Use test OAuth apps with localhost redirects
- **Production**: Use production OAuth apps with your domain
- **Security**: Never commit real OAuth credentials to version control

---

**Status**: 🔧 **REQUIRES ADMIN SETUP** - OAuth credentials need to be configured
