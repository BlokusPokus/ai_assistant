# Onboarding: Interactive SMS Onboarding Flow

## 🎯 **Task Context**

You are implementing an interactive, progressive onboarding flow for unregistered users who text the personal assistant phone number. This replaces the current static "not registered" messages with an engaging, step-by-step experience that guides users from initial contact to account creation.

## 📱 **Current State Analysis**

### **Existing SMS Systems**

The codebase has two SMS handling systems:

1. **Basic Twilio Service** (`/twilio/sms`)

   - Location: `src/personal_assistant/communication/twilio_integration/twilio_client.py`
   - Current message: Long, detailed welcome with phone formatting
   - Handles: `_create_helpful_guidance_response()`

2. **SMS Router Service** (`/sms_router/sms`)
   - Location: `src/personal_assistant/sms_router/services/response_formatter.py`
   - Current message: Short, simple "not registered" message
   - Handles: `format_unknown_user_response()`

### **Current User Experience**

```
User texts: "Hello"
Bot responds: "Welcome! Your phone number is not yet registered with our service. Please visit our website to sign up and start using your personal assistant."
```

**Problems:**

- ❌ Static, non-interactive
- ❌ No engagement or value demonstration
- ❌ Requires users to leave SMS
- ❌ High abandonment rate

## 🎯 **Target State**

### **Progressive Onboarding Flow**

```
Step 1: Welcome → Step 2: Feature Overview → Step 3: Account Creation → Step 4: Confirmation
```

### **Interactive User Journey**

```
User: "Hello"
Bot: "Hi! I'm your AI assistant. I can help with tasks, reminders, and more.
     Would you like to:
     A) See what I can do
     B) Get started now
     C) Learn more"

User: "A"
Bot: "I can help you with:
     📝 Create and manage tasks
     📅 Set reminders and events
     📧 Manage emails
     📊 Track your productivity
     And much more!

     Ready to get started? Reply 'YES' to create your account."

User: "YES"
Bot: "Great! Let's get you set up quickly.

     What's your email address? I'll send you a signup link."

User: "user@example.com"
Bot: "Thanks! I've sent a signup link to user@example.com.

     Once you complete signup, text me back and I'll help you get started with your first task!"
```

## 🏗 **Technical Architecture**

### **Core Components**

1. **OnboardingConversationManager**

   - Manages conversation state and flow progression
   - Handles user input parsing and validation
   - Coordinates with other services

2. **OnboardingResponseFormatter**

   - Generates contextual messages for each step
   - Handles message formatting and length optimization
   - Manages fallback responses

3. **EmailCollectionService**

   - Validates email addresses
   - Generates signup links
   - Integrates with email service

4. **OnboardingSessionStorage**
   - Stores temporary conversation state
   - Handles session cleanup and expiration
   - Provides quick lookups by phone number

### **Database Schema**

```sql
CREATE TABLE sms_onboarding_sessions (
    id SERIAL PRIMARY KEY,
    phone_number VARCHAR(20) NOT NULL,
    current_step VARCHAR(50) NOT NULL,
    collected_data JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP DEFAULT (NOW() + INTERVAL '1 hour')
);
```

### **Integration Points**

- **SMS Router Service**: Primary integration point
- **User Registration System**: For account creation
- **Email Service**: For sending signup links
- **Database**: For session state storage

## 🔍 **Key Files to Understand**

### **SMS Router System** (Primary Focus)

- `src/personal_assistant/sms_router/services/routing_engine.py`
  - Main routing logic
  - Calls `format_unknown_user_response()` for unregistered users
- `src/personal_assistant/sms_router/services/response_formatter.py`

  - Current `format_unknown_user_response()` method
  - **This is where you'll integrate the new onboarding flow**

- `src/apps/fastapi_app/routes/sms_router/webhooks.py`
  - Webhook endpoint that receives SMS from Twilio
  - Calls routing engine

### **User Identification**

- `src/personal_assistant/sms_router/services/user_identification.py`
  - Identifies users by phone number
  - Returns `None` for unregistered users

### **Email System** (For Integration)

- `src/personal_assistant/communication/email_service.py`
  - Existing email sending capabilities
  - Will be used for signup link delivery

## 🚀 **Implementation Strategy**

### **Phase 1: Core Flow**

1. Create database migration for onboarding sessions
2. Implement conversation state management
3. Create response formatter for onboarding messages
4. Integrate with SMS router's unknown user handling

### **Phase 2: Email Integration**

1. Implement email collection and validation
2. Generate signup links
3. Send confirmation emails
4. Handle email-related errors

### **Phase 3: Testing & Optimization**

1. Comprehensive testing of conversation flow
2. Performance optimization
3. Error handling improvements
4. Analytics integration

## 🎨 **Design Principles**

### **Message Design**

- **Length**: Keep under 160 characters when possible
- **Clarity**: Make next steps obvious
- **Engagement**: Use emojis and friendly tone
- **Progression**: Clear flow from step to step

### **User Experience**

- **Immediate Value**: Show capabilities before requiring signup
- **Low Friction**: Minimize steps to conversion
- **Fallback Handling**: Graceful degradation for unexpected inputs
- **Personalization**: Use phone number formatting for better UX

## 🔧 **Technical Considerations**

### **Performance Requirements**

- SMS response time < 2 seconds
- Database query performance < 100ms
- Session cleanup efficiency > 99%

### **Security Considerations**

- Temporary session data should expire
- Email validation to prevent abuse
- Rate limiting to prevent spam
- Input sanitization for all user inputs

### **Scalability**

- Session storage optimization
- Database indexing for quick lookups
- Cleanup mechanisms for expired sessions
- Monitoring and alerting

## 📊 **Success Metrics**

### **Primary KPIs**

- **Conversion Rate**: % of unregistered users who complete signup
- **Engagement Rate**: % of users who respond to initial message
- **Time to Conversion**: Average time from first contact to signup

### **Secondary Metrics**

- Drop-off points in the flow
- Email collection success rate
- Session cleanup efficiency
- Error rates and types

## 🧪 **Testing Strategy**

### **Unit Tests**

- Test each conversation step
- Test input parsing and validation
- Test email validation
- Test session management

### **Integration Tests**

- Test complete onboarding flow
- Test database operations
- Test email sending
- Test SMS response formatting

### **End-to-End Tests**

- Test with real phone numbers
- Test with various user inputs
- Test error scenarios
- Test session expiration

## 🚨 **Common Pitfalls to Avoid**

1. **Message Length**: Don't exceed SMS character limits
2. **State Management**: Don't lose conversation context
3. **Error Handling**: Don't leave users stuck in broken flows
4. **Performance**: Don't slow down SMS responses
5. **Security**: Don't store sensitive data in sessions
6. **Cleanup**: Don't forget to clean up expired sessions

## 🔄 **Integration with Existing Systems**

### **SMS Router Integration**

The main integration point is in `ResponseFormatter.format_unknown_user_response()`:

```python
def format_unknown_user_response(self, phone_number: str) -> MessagingResponse:
    """Format response for unknown phone numbers with interactive onboarding."""
    response = MessagingResponse()

    # Get interactive onboarding message
    onboarding_message = await self.onboarding_manager.handle_unregistered_user(
        phone_number, "start"
    )

    response.message(onboarding_message)
    return response
```

### **User Registration Integration**

After email collection, generate signup links that integrate with existing user registration system.

### **Email Service Integration**

Use existing email service to send signup links and confirmations.

## 📚 **Additional Resources**

### **Related Tasks**

- Task 071: SMS Retry Functionality (recently completed)
- Task 045: SMS Router Service (foundation)
- Task 046: Enhanced Twilio Service (alternative system)

### **Documentation**

- SMS Router Service documentation
- User Registration System documentation
- Email Service documentation
- Database schema documentation

## 🎯 **Next Steps**

1. **Review Current Implementation**: Understand existing SMS systems
2. **Design Database Schema**: Plan session storage structure
3. **Implement Core Components**: Start with conversation manager
4. **Integrate with SMS Router**: Update unknown user handling
5. **Test and Iterate**: Comprehensive testing and optimization

Remember: The goal is to create an engaging, interactive experience that converts unregistered users into registered users through a smooth, step-by-step onboarding process.
