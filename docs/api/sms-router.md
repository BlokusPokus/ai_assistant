# 📱 SMS Router API Documentation

## 🎯 **Overview**

The SMS Router API provides endpoints for handling SMS communication through Twilio integration. It manages incoming SMS messages, routes them to the appropriate users, and provides administrative functions for managing phone number mappings and SMS configuration.

## 📍 **Base Path**

All SMS router endpoints are prefixed with `/api/v1/sms-router`

## 🔑 **Endpoints**

### **Webhook Endpoints**

These endpoints handle incoming webhooks from Twilio and are typically called by Twilio, not directly by your application.

---

### **POST /webhook/sms**

Handle incoming SMS webhook from Twilio.

**Content-Type**: `application/x-www-form-urlencoded`

**Form Parameters:**

- `Body` (string, required): SMS message content
- `From` (string, required): Sender's phone number
- `To` (string, required): Recipient's phone number (our Twilio number)
- `MessageSid` (string, required): Twilio message SID

**Response (200 OK):**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>Thank you for your message. I'll process it shortly.</Message>
</Response>
```

**Response Format**: TwiML (Twilio Markup Language) XML

**Error Responses:**

- `400 Bad Request`: Invalid webhook request
- `500 Internal Server Error`: Internal server error

**Example:**

```bash
curl -X POST "http://localhost:8000/api/v1/sms-router/webhook/sms" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "Body=Hello%20world&From=%2B1234567890&To=%2B1987654321&MessageSid=SM1234567890"
```

**Processing Flow:**

1. **Validation**: Webhook request is validated for security
2. **Routing**: SMS is routed to the appropriate user based on phone number
3. **Processing**: Message is processed by the AI agent
4. **Response**: TwiML response is generated and returned

---

### **POST /webhook/delivery-status**

Handle Twilio delivery status webhooks.

**Content-Type**: `application/x-www-form-urlencoded`

**Form Parameters:**

- `MessageSid` (string, required): Twilio message SID
- `MessageStatus` (string, required): Delivery status (delivered, failed, etc.)

**Response (200 OK):**

```json
{
  "status": "success",
  "message": "Delivery status updated"
}
```

**Response Schema:**

- `status` (string): Processing status (success, warning)
- `message` (string): Status message

**Error Responses:**

- `500 Internal Server Error`: Failed to process delivery status

**Example:**

```bash
curl -X POST "http://localhost:8000/api/v1/sms-router/webhook/delivery-status" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "MessageSid=SM1234567890&MessageStatus=delivered"
```

**Delivery Status Values:**

- `queued`: Message is queued for delivery
- `sent`: Message has been sent
- `delivered`: Message was successfully delivered
- `failed`: Message delivery failed
- `undelivered`: Message could not be delivered

---

### **GET /webhook/health**

Health check endpoint for SMS Router webhook service.

**Response (200 OK):**

```json
{
  "status": "healthy",
  "service": "SMS Router Webhook",
  "timestamp": "2024-01-01T00:00:00Z",
  "components": {
    "routing_engine": "healthy",
    "database": "healthy",
    "twilio": "healthy"
  }
}
```

**Response Schema:**

- `status` (string): Overall health status
- `service` (string): Service name
- `timestamp` (string): Health check timestamp
- `components` (object): Individual component statuses

**Error Responses:**

- `500 Internal Server Error`: Health check failed

**Example:**

```bash
curl -X GET "http://localhost:8000/api/v1/sms-router/webhook/health"
```

---

### **GET /webhook/stats**

Get routing engine statistics.

**Response (200 OK):**

```json
{
  "total_messages": 1250,
  "successful_routes": 1200,
  "failed_routes": 50,
  "average_processing_time_ms": 150,
  "last_24_hours": {
    "messages": 45,
    "success_rate": 95.6
  },
  "top_users": [
    {
      "user_id": 1,
      "message_count": 25,
      "phone_number": "+1234567890"
    }
  ]
}
```

**Response Schema:**

- `total_messages` (integer): Total messages processed
- `successful_routes` (integer): Successfully routed messages
- `failed_routes` (integer): Failed route attempts
- `average_processing_time_ms` (integer): Average processing time
- `last_24_hours` (object): Statistics for last 24 hours
- `top_users` (array): Top users by message count

**Error Responses:**

- `500 Internal Server Error`: Failed to get statistics

**Example:**

```bash
curl -X GET "http://localhost:8000/api/v1/sms-router/webhook/stats"
```

### **Admin Endpoints**

These endpoints require admin permissions and provide administrative functions for managing the SMS router service.

---

### **GET /admin/status**

Get comprehensive status of SMS Router Service.

**Headers:**

- `Authorization: Bearer <access_token>` (required)
- **Permission Required**: `system:view_sms_status`

**Response (200 OK):**

```json
{
  "service": "SMS Router Service",
  "status": {
    "status": "healthy",
    "service": "SMS Router Webhook",
    "timestamp": "2024-01-01T00:00:00Z",
    "components": {
      "routing_engine": "healthy",
      "database": "healthy",
      "twilio": "healthy"
    }
  },
  "statistics": {
    "total_messages": 1250,
    "successful_routes": 1200,
    "failed_routes": 50,
    "average_processing_time_ms": 150
  },
  "endpoints": {
    "webhook": "/sms-router/webhook/sms",
    "health": "/sms-router/webhook/health",
    "stats": "/sms-router/webhook/stats"
  }
}
```

**Error Responses:**

- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `500 Internal Server Error`: Internal server error

**Example:**

```bash
curl -X GET "http://localhost:8000/api/v1/sms-router/admin/status" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

### **GET /admin/usage**

Get SMS usage logs.

**Headers:**

- `Authorization: Bearer <access_token>` (required)
- **Permission Required**: `system:view_sms_usage`

**Query Parameters:**

- `limit` (integer, optional): Maximum number of logs to return (default: 100, max: 1000)
- `offset` (integer, optional): Number of logs to skip (default: 0)

**Response (200 OK):**

```json
{
  "total": 1250,
  "limit": 100,
  "offset": 0,
  "logs": [
    {
      "id": 1,
      "user_id": 1,
      "phone_number": "+1234567890",
      "direction": "inbound",
      "length": 15,
      "success": true,
      "processing_time_ms": 120,
      "created_at": "2024-01-01T00:00:00Z"
    },
    {
      "id": 2,
      "user_id": 1,
      "phone_number": "+1234567890",
      "direction": "outbound",
      "length": 25,
      "success": true,
      "processing_time_ms": 180,
      "created_at": "2024-01-01T00:01:00Z"
    }
  ]
}
```

**Response Schema:**

- `total` (integer): Total number of usage logs
- `limit` (integer): Requested limit
- `offset` (integer): Requested offset
- `logs` (array): Usage log entries
  - `id` (integer): Log ID
  - `user_id` (integer): User ID
  - `phone_number` (string): Phone number
  - `direction` (string): Message direction (inbound, outbound)
  - `length` (integer): Message length
  - `success` (boolean): Whether processing was successful
  - `processing_time_ms` (integer): Processing time in milliseconds
  - `created_at` (string): Log timestamp

**Error Responses:**

- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `500 Internal Server Error`: Failed to get usage logs

**Example:**

```bash
curl -X GET "http://localhost:8000/api/v1/sms-router/admin/usage?limit=50&offset=0" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

### **GET /admin/phone-mappings**

Get phone number mappings.

**Headers:**

- `Authorization: Bearer <access_token>` (required)
- **Permission Required**: `system:view_phone_mappings`

**Query Parameters:**

- `user_id` (integer, optional): Filter by user ID

**Response (200 OK):**

```json
{
  "mappings": [
    {
      "id": 1,
      "user_id": 1,
      "phone_number": "+1234567890",
      "is_primary": true,
      "is_verified": true,
      "verification_method": "sms",
      "created_at": "2024-01-01T00:00:00Z"
    },
    {
      "id": 2,
      "user_id": 2,
      "phone_number": "+1987654321",
      "is_primary": true,
      "is_verified": false,
      "verification_method": "manual",
      "created_at": "2024-01-01T01:00:00Z"
    }
  ]
}
```

**Response Schema:**

- `mappings` (array): Phone number mappings
  - `id` (integer): Mapping ID
  - `user_id` (integer): User ID
  - `phone_number` (string): Phone number
  - `is_primary` (boolean): Whether this is the primary number
  - `is_verified` (boolean): Whether the number is verified
  - `verification_method` (string): Verification method used
  - `created_at` (string): Creation timestamp

**Error Responses:**

- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `500 Internal Server Error`: Failed to get phone mappings

**Example:**

```bash
curl -X GET "http://localhost:8000/api/v1/sms-router/admin/phone-mappings?user_id=1" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

### **POST /admin/phone-mappings**

Create a new phone number mapping.

**Headers:**

- `Authorization: Bearer <access_token>` (required)
- **Permission Required**: `system:manage_phone_mappings`

**Query Parameters:**

- `user_id` (integer, required): User ID
- `phone_number` (string, required): Phone number to add
- `is_primary` (boolean, optional): Whether this is the primary number (default: false)
- `verification_method` (string, optional): Verification method (default: "manual")

**Response (200 OK):**

```json
{
  "message": "Phone mapping created successfully",
  "user_id": 1,
  "phone_number": "+1234567890"
}
```

**Error Responses:**

- `400 Bad Request`: Failed to create phone mapping
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `500 Internal Server Error`: Failed to create phone mapping

**Example:**

```bash
curl -X POST "http://localhost:8000/api/v1/sms-router/admin/phone-mappings?user_id=1&phone_number=%2B1234567890&is_primary=true&verification_method=sms" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

### **DELETE /admin/phone-mappings/{mapping_id}**

Delete a phone number mapping.

**Headers:**

- `Authorization: Bearer <access_token>` (required)
- **Permission Required**: `system:manage_phone_mappings`

**Path Parameters:**

- `mapping_id` (integer, required): Mapping ID

**Response (200 OK):**

```json
{
  "message": "Phone mapping deleted successfully",
  "mapping_id": 1
}
```

**Error Responses:**

- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Phone mapping not found
- `500 Internal Server Error`: Failed to delete phone mapping

**Example:**

```bash
curl -X DELETE "http://localhost:8000/api/v1/sms-router/admin/phone-mappings/1" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

### **GET /admin/config**

Get SMS Router configuration.

**Headers:**

- `Authorization: Bearer <access_token>` (required)
- **Permission Required**: `system:view_sms_config`

**Response (200 OK):**

```json
{
  "configs": [
    {
      "key": "max_message_length",
      "value": "1600",
      "description": "Maximum SMS message length",
      "is_active": true,
      "updated_at": "2024-01-01T00:00:00Z"
    },
    {
      "key": "retry_attempts",
      "value": "3",
      "description": "Number of retry attempts for failed messages",
      "is_active": true,
      "updated_at": "2024-01-01T00:00:00Z"
    },
    {
      "key": "processing_timeout_ms",
      "value": "30000",
      "description": "Message processing timeout in milliseconds",
      "is_active": true,
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

**Response Schema:**

- `configs` (array): Configuration entries
  - `key` (string): Configuration key
  - `value` (string): Configuration value
  - `description` (string): Configuration description
  - `is_active` (boolean): Whether configuration is active
  - `updated_at` (string): Last update timestamp

**Error Responses:**

- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `500 Internal Server Error`: Failed to get configuration

**Example:**

```bash
curl -X GET "http://localhost:8000/api/v1/sms-router/admin/config" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

### **POST /admin/config**

Update SMS Router configuration.

**Headers:**

- `Authorization: Bearer <access_token>` (required)
- **Permission Required**: `system:manage_sms_config`

**Query Parameters:**

- `config_key` (string, required): Configuration key
- `config_value` (string, required): Configuration value
- `description` (string, optional): Configuration description

**Response (200 OK):**

```json
{
  "message": "Configuration updated successfully",
  "key": "max_message_length"
}
```

**Error Responses:**

- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `500 Internal Server Error`: Failed to update configuration

**Example:**

```bash
curl -X POST "http://localhost:8000/api/v1/sms-router/admin/config?config_key=max_message_length&config_value=1600&description=Maximum%20SMS%20message%20length" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

## 🔒 **Security Features**

### **Webhook Security**

- **Twilio Validation**: Webhook requests are validated using Twilio signatures
- **IP Whitelisting**: Optional IP whitelisting for webhook endpoints
- **Rate Limiting**: Protection against webhook abuse
- **Request Validation**: Form parameters are validated and sanitized

### **Admin Security**

- **Authentication Required**: All admin endpoints require valid JWT tokens
- **Permission-Based Access**: Granular permissions for different admin functions
- **Audit Logging**: All admin operations are logged for audit purposes
- **Data Validation**: All input data is validated and sanitized

### **Phone Number Security**

- **User Isolation**: Phone numbers are isolated per user
- **Verification**: Phone numbers can be verified via SMS
- **Primary Number**: Only one primary number per user
- **Secure Storage**: Phone numbers are stored securely

## 🔄 **SMS Routing Flow**

### **Incoming SMS Process**

1. **Webhook**: Twilio sends SMS webhook to `/webhook/sms`
2. **Validation**: Webhook request is validated for security
3. **User Identification**: Phone number is mapped to user
4. **Routing**: SMS is routed to user's AI agent
5. **Processing**: AI agent processes the message
6. **Response**: TwiML response is generated and returned

### **Outgoing SMS Process**

1. **Generation**: AI agent generates response message
2. **Routing**: Message is routed through SMS router
3. **Delivery**: Message is sent via Twilio
4. **Status Tracking**: Delivery status is tracked via webhooks
5. **Retry Logic**: Failed messages are retried automatically

## 📱 **Twilio Integration**

### **Webhook Configuration**

- **SMS Webhook**: `https://yourapp.com/api/v1/sms-router/webhook/sms`
- **Status Webhook**: `https://yourapp.com/api/v1/sms-router/webhook/delivery-status`
- **Method**: POST
- **Content-Type**: `application/x-www-form-urlencoded`

### **TwiML Responses**

The SMS webhook returns TwiML (Twilio Markup Language) responses:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>Thank you for your message. I'll process it shortly.</Message>
</Response>
```

### **Supported TwiML Elements**

- `<Message>`: Send SMS response
- `<Say>`: Text-to-speech (for voice calls)
- `<Redirect>`: Redirect to another webhook
- `<Pause>`: Wait before next action

## 🚨 **Error Handling**

All endpoints return consistent error responses:

```json
{
  "detail": "Error message",
  "error_code": "ERROR_CODE",
  "status": "error",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### **Common Error Codes**

- `SMS_ROUTING_FAILED`: Failed to route SMS to user
- `PHONE_NUMBER_NOT_FOUND`: Phone number not mapped to any user
- `TWILIO_WEBHOOK_INVALID`: Invalid Twilio webhook request
- `MESSAGE_PROCESSING_FAILED`: Failed to process SMS message
- `CONFIGURATION_ERROR`: SMS router configuration error

## 🧪 **Testing**

### **Webhook Testing**

Use tools like ngrok to expose your local server for webhook testing:

```bash
# Install ngrok
npm install -g ngrok

# Expose local server
ngrok http 8000

# Use ngrok URL in Twilio webhook configuration
# https://abc123.ngrok.io/api/v1/sms-router/webhook/sms
```

### **Admin Testing**

Use the provided examples with curl or any HTTP client. The API also provides interactive documentation at `/docs` (Swagger UI) for testing endpoints directly in the browser.

### **Twilio Testing**

- **Test Numbers**: Use Twilio test numbers for development
- **Sandbox**: Use Twilio sandbox for testing
- **Webhook Logs**: Check Twilio webhook logs for debugging

---

**This SMS Router API provides comprehensive SMS communication capabilities through Twilio integration, enabling secure multi-user SMS routing and administrative management.**
