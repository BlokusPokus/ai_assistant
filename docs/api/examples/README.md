# API Examples

This directory contains comprehensive examples for using the Personal Assistant API. Each example demonstrates real-world usage patterns and best practices.

## Example Categories

### Authentication Examples

- [User Registration and Login](authentication.md) - Complete user onboarding flow
- [MFA Setup and Usage](mfa-examples.md) - Multi-factor authentication examples
- [Session Management](session-examples.md) - Managing user sessions

### User Management Examples

- [Profile Management](user-profile.md) - Updating user profiles and preferences
- [Phone Number Management](phone-management.md) - Adding and verifying phone numbers
- [Admin Operations](admin-operations.md) - Administrative user management

### OAuth Integration Examples

- [Google OAuth Flow](google-oauth.md) - Complete Google integration
- [Microsoft OAuth Flow](microsoft-oauth.md) - Complete Microsoft integration
- [Notion OAuth Flow](notion-oauth.md) - Complete Notion integration
- [YouTube OAuth Flow](youtube-oauth.md) - Complete YouTube integration

### SMS Router Examples

- [SMS Webhook Handling](sms-webhooks.md) - Processing incoming SMS messages
- [Admin SMS Management](sms-admin.md) - Administrative SMS operations
- [Phone Number Mapping](phone-mapping.md) - Managing phone number mappings

### Analytics Examples

- [User Analytics](user-analytics.md) - Retrieving user analytics data
- [Cost Analysis](cost-analysis.md) - Analyzing SMS costs and usage
- [Report Generation](report-generation.md) - Generating usage reports

### RBAC Examples

- [Role Management](role-management.md) - Creating and managing roles
- [Permission Management](permission-management.md) - Managing permissions
- [User Role Assignment](user-roles.md) - Assigning roles to users
- [Audit Logging](audit-logs.md) - Reviewing audit logs

### Chat Examples

- [Basic Chat Flow](chat-basic.md) - Simple chat interactions
- [Advanced Chat Features](chat-advanced.md) - Complex chat scenarios
- [WebSocket Integration](websocket-chat.md) - Real-time chat implementation

## Getting Started

1. **Set up authentication**: Start with the [authentication examples](authentication.md)
2. **Configure your environment**: Use the environment variables from the main API documentation
3. **Test basic functionality**: Try the [basic chat flow](chat-basic.md)
4. **Explore advanced features**: Move on to more complex examples

## Prerequisites

Before running these examples, ensure you have:

- Valid API credentials (client ID and secret)
- Access to the Personal Assistant API endpoint
- Appropriate permissions for the operations you want to test
- Required environment variables configured

## Environment Setup

Create a `.env` file with the following variables:

```bash
# API Configuration
API_BASE_URL=https://api.personalassistant.com
CLIENT_ID=your_client_id
CLIENT_SECRET=your_client_secret

# Database (for local testing)
DATABASE_URL=postgresql://user:password@localhost:5432/personal_assistant

# Redis (for session management)
REDIS_URL=redis://localhost:6379/0

# Twilio (for SMS functionality)
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_PHONE_NUMBER=+1234567890

# OAuth Providers
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
MICROSOFT_CLIENT_ID=your_microsoft_client_id
MICROSOFT_CLIENT_SECRET=your_microsoft_client_secret
NOTION_CLIENT_ID=your_notion_client_id
NOTION_CLIENT_SECRET=your_notion_client_secret
YOUTUBE_CLIENT_ID=your_youtube_client_id
YOUTUBE_CLIENT_SECRET=your_youtube_client_secret
```

## Example Structure

Each example file follows this structure:

1. **Overview**: Brief description of what the example demonstrates
2. **Prerequisites**: Required setup and permissions
3. **Step-by-step instructions**: Detailed implementation steps
4. **Code examples**: Complete code snippets
5. **Expected responses**: Sample API responses
6. **Error handling**: Common errors and solutions
7. **Best practices**: Tips and recommendations

## Testing the Examples

### Using curl

Most examples include curl commands for testing:

```bash
# Example curl command
curl -X POST "https://api.personalassistant.com/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword"
  }'
```

### Using JavaScript/Node.js

Examples include JavaScript implementations:

```javascript
const response = await fetch(
  "https://api.personalassistant.com/api/v1/auth/login",
  {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      email: "user@example.com",
      password: "securepassword",
    }),
  }
);

const data = await response.json();
console.log(data);
```

### Using Python

Python examples are also provided:

```python
import requests

response = requests.post(
    'https://api.personalassistant.com/api/v1/auth/login',
    json={
        'email': 'user@example.com',
        'password': 'securepassword'
    }
)

data = response.json()
print(data)
```

## Common Patterns

### Authentication Flow

1. **Register user** → Get user ID
2. **Login** → Get access token
3. **Use token** → Make authenticated requests
4. **Refresh token** → When token expires

### Error Handling

Always check for errors and handle them appropriately:

```javascript
if (!response.ok) {
  const error = await response.json();
  console.error("API Error:", error.detail);
  throw new Error(error.detail);
}
```

### Rate Limiting

Respect rate limits and implement backoff strategies:

```javascript
const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

if (response.status === 429) {
  const retryAfter = response.headers.get("Retry-After");
  await delay(retryAfter * 1000);
  // Retry the request
}
```

## Support

If you encounter issues with these examples:

1. Check the [API documentation](../README.md) for detailed endpoint information
2. Review the [troubleshooting guide](../../deployment/troubleshooting.md)
3. Ensure your environment variables are correctly configured
4. Verify you have the necessary permissions for the operations

## Contributing

To add new examples:

1. Follow the established structure and format
2. Include complete, runnable code examples
3. Test all examples before submitting
4. Update this README to include your new example
5. Ensure examples follow security best practices
