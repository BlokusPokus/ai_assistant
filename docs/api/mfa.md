# 🔐 Multi-Factor Authentication (MFA) API Documentation

## 🎯 **Overview**

The Multi-Factor Authentication (MFA) API provides endpoints for setting up and managing TOTP (Time-based One-Time Password) and SMS-based multi-factor authentication. MFA adds an extra layer of security to user accounts by requiring a second form of verification.

## 📍 **Base Path**

All MFA endpoints are prefixed with `/api/v1/mfa`

## 🔑 **Endpoints**

### **TOTP (Time-based One-Time Password) MFA**

TOTP MFA uses authenticator apps like Google Authenticator, Authy, or Microsoft Authenticator.

---

### **POST /setup/totp**

Setup TOTP-based MFA for the current user.

**Headers:**

- `Authorization: Bearer <access_token>` (required)
- **Permission Required**: `user:write`

**Response (200 OK):**

```json
{
  "totp_secret": "JBSWY3DPEHPK3PXP",
  "qr_code": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
  "message": "Scan QR code with your authenticator app, then verify with a token"
}
```

**Response Schema:**

- `totp_secret` (string): Base32-encoded secret for manual entry
- `qr_code` (string): Base64-encoded QR code image
- `message` (string): Instructions for the user

**Error Responses:**

- `400 Bad Request`: TOTP MFA is already enabled
- `401 Unauthorized`: Authentication required
- `500 Internal Server Error`: Failed to setup TOTP

**Example:**

```bash
curl -X POST "http://localhost:8000/api/v1/mfa/setup/totp" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Setup Process:**

1. Call this endpoint to get the QR code and secret
2. Scan QR code with authenticator app or manually enter secret
3. Use the generated token to verify and enable TOTP

---

### **POST /verify/totp**

Verify TOTP token and enable MFA.

**Headers:**

- `Authorization: Bearer <access_token>` (required)

**Request Body:**

```json
{
  "token": "123456"
}
```

**Request Schema:**

- `token` (string, required): 6-digit TOTP token from authenticator app

**Response (200 OK):**

```json
{
  "message": "TOTP MFA enabled successfully",
  "backup_codes": [
    "ABCD-EFGH-IJKL",
    "MNOP-QRST-UVWX",
    "YZAB-CDEF-GHIJ",
    "KLMN-OPQR-STUV",
    "WXYZ-ABCD-EFGH",
    "IJKL-MNOP-QRST",
    "UVWX-YZAB-CDEF",
    "GHIJ-KLMN-OPQR"
  ]
}
```

**Response Schema:**

- `message` (string): Success message
- `backup_codes` (array): List of backup codes for account recovery

**Error Responses:**

- `400 Bad Request`: TOTP not configured or invalid token
- `401 Unauthorized`: Authentication required
- `500 Internal Server Error`: Failed to verify TOTP

**Example:**

```bash
curl -X POST "http://localhost:8000/api/v1/mfa/verify/totp" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "token": "123456"
  }'
```

**Important:** Save the backup codes securely. They can be used to recover access if the authenticator app is lost.

---

### **SMS-based MFA**

SMS MFA sends verification codes via SMS to the user's phone number.

---

### **POST /setup/sms**

Setup SMS-based MFA for the current user.

**Headers:**

- `Authorization: Bearer <access_token>` (required)

**Request Body:**

```json
{
  "phone_number": "+1234567890"
}
```

**Request Schema:**

- `phone_number` (string, required): Phone number for SMS verification

**Response (200 OK):**

```json
{
  "code_id": "sms_verification_123456789",
  "message": "SMS verification code sent to +1234567890"
}
```

**Response Schema:**

- `code_id` (string): Unique identifier for the verification code
- `message` (string): Confirmation message

**Error Responses:**

- `400 Bad Request`: SMS MFA is already enabled
- `401 Unauthorized`: Authentication required
- `429 Too Many Requests`: Too many verification attempts
- `500 Internal Server Error`: Failed to setup SMS MFA

**Example:**

```bash
curl -X POST "http://localhost:8000/api/v1/mfa/setup/sms" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+1234567890"
  }'
```

---

### **POST /verify/sms**

Verify SMS code and enable MFA.

**Headers:**

- `Authorization: Bearer <access_token>` (required)

**Request Body:**

```json
{
  "code_id": "sms_verification_123456789",
  "code": "123456"
}
```

**Request Schema:**

- `code_id` (string, required): Verification code ID from setup response
- `code` (string, required): 6-digit SMS verification code

**Response (200 OK):**

```json
{
  "message": "SMS MFA enabled successfully"
}
```

**Error Responses:**

- `400 Bad Request`: SMS MFA not configured or invalid code
- `401 Unauthorized`: Authentication required
- `500 Internal Server Error`: Failed to verify SMS MFA

**Example:**

```bash
curl -X POST "http://localhost:8000/api/v1/mfa/verify/sms" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "code_id": "sms_verification_123456789",
    "code": "123456"
  }'
```

---

### **Backup Codes**

Backup codes provide an alternative way to authenticate when the primary MFA method is unavailable.

---

### **POST /verify/backup**

Verify backup code for account recovery.

**Headers:**

- `Authorization: Bearer <access_token>` (required)

**Request Body:**

```json
{
  "code": "ABCD-EFGH-IJKL"
}
```

**Request Schema:**

- `code` (string, required): Backup code from the list provided during TOTP setup

**Response (200 OK):**

```json
{
  "message": "Backup code verified successfully"
}
```

**Error Responses:**

- `400 Bad Request`: No backup codes configured or invalid code
- `401 Unauthorized`: Authentication required
- `500 Internal Server Error`: Failed to verify backup code

**Example:**

```bash
curl -X POST "http://localhost:8000/api/v1/mfa/verify/backup" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "code": "ABCD-EFGH-IJKL"
  }'
```

**Important:** Backup codes are single-use. After using one, it cannot be used again.

---

### **MFA Management**

---

### **GET /status**

Get MFA status for the current user.

**Headers:**

- `Authorization: Bearer <access_token>` (required)
- **Permission Required**: `user:read`

**Response (200 OK):**

```json
{
  "totp_enabled": true,
  "sms_enabled": false,
  "phone_number": "+1234567890",
  "backup_codes_count": 8,
  "trusted_devices_count": 2
}
```

**Response Schema:**

- `totp_enabled` (boolean): Whether TOTP MFA is enabled
- `sms_enabled` (boolean): Whether SMS MFA is enabled
- `phone_number` (string, nullable): Phone number for SMS MFA
- `backup_codes_count` (integer): Number of remaining backup codes
- `trusted_devices_count` (integer): Number of trusted devices

**Error Responses:**

- `401 Unauthorized`: Authentication required
- `500 Internal Server Error`: Failed to get MFA status

**Example:**

```bash
curl -X GET "http://localhost:8000/api/v1/mfa/status" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

### **POST /disable**

Disable MFA for the current user.

**Headers:**

- `Authorization: Bearer <access_token>` (required)
- **Permission Required**: `user:write`

**Request Body:**

```json
{
  "method": "totp",
  "password": "SecurePassword123!"
}
```

**Request Schema:**

- `method` (string, required): MFA method to disable ("totp" or "sms")
- `password` (string, required): User's password for confirmation

**Response (200 OK):**

```json
{
  "message": "TOTP MFA disabled successfully"
}
```

**Error Responses:**

- `400 Bad Request`: MFA not configured or invalid method
- `401 Unauthorized`: Authentication required
- `500 Internal Server Error`: Failed to disable MFA

**Example:**

```bash
curl -X POST "http://localhost:8000/api/v1/mfa/disable" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "method": "totp",
    "password": "SecurePassword123!"
  }'
```

---

### **POST /regenerate-backup-codes**

Regenerate backup codes for the current user.

**Headers:**

- `Authorization: Bearer <access_token>` (required)

**Response (200 OK):**

```json
{
  "message": "Backup codes regenerated successfully",
  "backup_codes": [
    "ABCD-EFGH-IJKL",
    "MNOP-QRST-UVWX",
    "YZAB-CDEF-GHIJ",
    "KLMN-OPQR-STUV",
    "WXYZ-ABCD-EFGH",
    "IJKL-MNOP-QRST",
    "UVWX-YZAB-CDEF",
    "GHIJ-KLMN-OPQR"
  ]
}
```

**Response Schema:**

- `message` (string): Success message
- `backup_codes` (array): New list of backup codes

**Error Responses:**

- `400 Bad Request`: TOTP MFA must be enabled to use backup codes
- `401 Unauthorized`: Authentication required
- `500 Internal Server Error`: Failed to regenerate backup codes

**Example:**

```bash
curl -X POST "http://localhost:8000/api/v1/mfa/regenerate-backup-codes" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Important:** Regenerating backup codes invalidates all previous backup codes.

## 🔒 **Security Features**

### **TOTP Security**

- **Time Window**: 30-second time windows for token validation
- **Clock Skew**: Handles minor clock differences between server and device
- **Rate Limiting**: Prevents brute force attacks on verification codes
- **Secret Storage**: TOTP secrets are encrypted and stored securely

### **SMS Security**

- **Code Expiry**: Verification codes expire after 10 minutes
- **Rate Limiting**: Limits on SMS sending to prevent abuse
- **Phone Validation**: Phone numbers are validated before sending codes
- **Code Randomization**: 6-digit random codes for security

### **Backup Codes**

- **Single Use**: Each backup code can only be used once
- **Secure Generation**: Cryptographically secure random generation
- **Limited Count**: Limited number of backup codes (8 by default)
- **Regeneration**: Ability to regenerate codes when needed

### **Account Recovery**

- **Multiple Methods**: TOTP, SMS, and backup codes for recovery
- **Password Confirmation**: Password required for disabling MFA
- **Security Logging**: All MFA events are logged for security auditing

## 🔄 **MFA Setup Flow**

### **TOTP Setup Process**

1. **Setup**: Call `/setup/totp` to get QR code and secret
2. **Scan**: Scan QR code with authenticator app or enter secret manually
3. **Verify**: Call `/verify/totp` with the generated token
4. **Backup**: Save the provided backup codes securely
5. **Enable**: TOTP MFA is now enabled for the account

### **SMS Setup Process**

1. **Setup**: Call `/setup/sms` with phone number
2. **Receive**: Receive SMS with verification code
3. **Verify**: Call `/verify/sms` with the received code
4. **Enable**: SMS MFA is now enabled for the account

### **Login with MFA**

1. **Login**: Use regular login endpoint
2. **MFA Required**: If MFA is enabled, response includes `mfa_required: true`
3. **Verify**: Use appropriate verification endpoint (TOTP, SMS, or backup)
4. **Access**: Full access granted after successful MFA verification

## 📱 **Supported Authenticator Apps**

- **Google Authenticator**: Available for iOS and Android
- **Microsoft Authenticator**: Available for iOS and Android
- **Authy**: Available for iOS, Android, and desktop
- **1Password**: Available for iOS, Android, and desktop
- **LastPass Authenticator**: Available for iOS and Android

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

- `MFA_ALREADY_ENABLED`: MFA method is already enabled
- `MFA_NOT_CONFIGURED`: MFA method is not configured
- `INVALID_TOKEN`: Invalid TOTP or SMS verification code
- `INVALID_BACKUP_CODE`: Invalid backup code
- `RATE_LIMIT_EXCEEDED`: Too many verification attempts
- `PHONE_NUMBER_INVALID`: Invalid phone number format

## 🧪 **Testing**

Use the provided examples with curl or any HTTP client. The API also provides interactive documentation at `/docs` (Swagger UI) for testing endpoints directly in the browser.

### **Testing TOTP**

1. Use a TOTP testing tool or authenticator app
2. Generate tokens using the secret from `/setup/totp`
3. Test verification with the generated tokens

### **Testing SMS**

1. Use a valid phone number for testing
2. Check SMS delivery (in development, codes may be logged)
3. Test verification with received codes

---

**This MFA API provides comprehensive multi-factor authentication with TOTP, SMS, and backup code support, ensuring secure access to user accounts.**
