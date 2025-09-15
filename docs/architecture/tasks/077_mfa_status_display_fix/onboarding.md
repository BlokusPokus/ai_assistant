# MFA Status Display Fix - Onboarding

## Task Context

**Task ID**: 077  
**Task Name**: Fix MFA Status Display in Frontend  
**Priority**: Medium  
**Estimated Time**: 2-4 hours

## Problem Statement

The frontend currently displays hardcoded "MFA Enabled" messages in multiple components without actually checking the real MFA status from the backend API. This creates a misleading user experience where users see "MFA Enabled" even when they haven't actually set up two-factor authentication.

## Current State Analysis

### Backend MFA Implementation ✅

- **Complete TOTP Service**: `src/personal_assistant/auth/mfa_service.py`

  - TOTP secret generation using `pyotp.random_base32()`
  - QR code generation for authenticator apps
  - Token verification with time window tolerance
  - Backup codes generation (8-character alphanumeric)
  - Device trust management (30-day expiration)

- **API Endpoints**: `src/apps/fastapi_app/routes/mfa.py`

  - `POST /mfa/setup/totp` - Setup TOTP MFA
  - `POST /mfa/verify/totp` - Verify TOTP token
  - `GET /mfa/status` - Get MFA status (returns `MFAStatusResponse`)
  - `POST /mfa/disable` - Disable MFA

- **Database Schema**: `src/personal_assistant/database/models/mfa_models.py`
  - `mfa_configurations` table with TOTP secrets, backup codes, trusted devices
  - `user_sessions` table for session tracking
  - `security_events` table for audit logging

### Frontend Issues ❌

- **Hardcoded Status**: Multiple components show "MFA Enabled" without API calls
- **No Real Status Check**: Frontend doesn't call `/mfa/status` endpoint
- **Misleading UI**: Users see "MFA Enabled" even when MFA is not configured

### Affected Components

1. **`src/apps/frontend/src/components/profile/SecuritySettings.tsx`** (lines 59-70)

   - Shows hardcoded "MFA is currently enabled" message
   - Uses undefined `mfaMethod` variable

2. **`src/apps/frontend/src/components/dashboard/UserProfileCard.tsx`** (line 51)

   - Shows hardcoded "MFA Enabled" status

3. **`src/apps/frontend/src/pages/DashboardPage.tsx`** (line 160)
   - Shows hardcoded "MFA Enabled" in system status

## Technical Requirements

### API Integration

- **Endpoint**: `GET /api/v1/mfa/status`
- **Response Model**: `MFAStatusResponse`
  ```typescript
  {
    totp_enabled: boolean,
    sms_enabled: boolean,
    phone_number: string | null,
    backup_codes_count: number,
    trusted_devices_count: number
  }
  ```

### Frontend Changes Needed

1. **Create MFA Service**: `src/apps/frontend/src/services/mfaService.ts`

   - `getMFAStatus()` method
   - `setupTOTP()` method
   - `verifyTOTP()` method
   - `disableMFA()` method

2. **Update Components**:

   - Replace hardcoded text with real API data
   - Add loading states
   - Add error handling
   - Show setup flow when MFA is disabled

3. **Add MFA Setup Flow**:
   - QR code display
   - Token verification
   - Backup codes display

## Implementation Plan

### Phase 1: API Service Layer

1. Create `mfaService.ts` with API integration
2. Add proper TypeScript interfaces
3. Handle authentication headers
4. Add error handling and loading states

### Phase 2: Component Updates

1. Update `SecuritySettings.tsx` to use real MFA status
2. Update `UserProfileCard.tsx` to show actual status
3. Update `DashboardPage.tsx` to reflect real MFA state
4. Add conditional rendering based on MFA status

### Phase 3: MFA Setup Flow

1. Create MFA setup component
2. Integrate QR code display
3. Add token verification form
4. Handle backup codes display

### Phase 4: Testing & Validation

1. Test with MFA disabled
2. Test with MFA enabled
3. Test setup flow
4. Verify error handling

## Dependencies

### Backend Dependencies ✅

- MFA service is fully implemented
- API endpoints are working
- Database schema is in place

### Frontend Dependencies

- Existing API service pattern (`src/apps/frontend/src/services/api.ts`)
- React hooks for state management
- Existing UI components (Card, Button, Input, etc.)

## Success Criteria

1. **Accurate Status Display**: Frontend shows real MFA status from API
2. **Setup Flow**: Users can enable MFA through the UI
3. **Error Handling**: Proper error states and loading indicators
4. **User Experience**: Clear indication of MFA status and setup options
5. **No Hardcoded Text**: All MFA status text comes from API data

## Risk Assessment

### Low Risk

- Backend MFA implementation is complete and tested
- API endpoints are working
- Frontend changes are isolated to display components

### Medium Risk

- Authentication token handling in frontend
- Error state management
- User experience during MFA setup

### Mitigation

- Use existing API service patterns
- Add comprehensive error handling
- Test thoroughly with different MFA states

## Questions for Clarification

1. Should we implement the full MFA setup flow in this task, or just fix the status display?
2. Do we need to handle SMS MFA in addition to TOTP?
3. Should we add MFA status to the user profile/settings page?
4. Do we need to handle MFA during login flow, or just status display?

## Next Steps

1. Create MFA service layer
2. Update affected components
3. Test with different MFA states
4. Add MFA setup flow if needed
5. Validate user experience

---

**Note**: This task focuses on fixing the misleading MFA status display. The backend MFA implementation is already complete and functional.
