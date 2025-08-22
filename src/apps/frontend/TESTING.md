# Testing Documentation

## Overview

This document outlines the testing strategy for the Personal Assistant TDAH frontend application, specifically focusing on the Authentication UI implementation (Task 039).

## Current Test Setup

### Test Framework

- **Vitest**: Fast unit test framework
- **React Testing Library**: Testing utilities for React components
- **jsdom**: DOM environment for testing
- **@testing-library/jest-dom**: Custom Jest matchers

### Test Scripts

```bash
# Run tests in watch mode
npm run test

# Run tests once
npm run test:run

# Run tests with UI
npm run test:ui

# Run tests with coverage
npm run test:coverage
```

## Test Structure

```
src/
├── test/
│   ├── setup.ts          # Test environment setup
│   ├── utils.tsx         # Test utilities and custom render
│   └── smoke.test.tsx    # Basic smoke tests
└── components/
    └── auth/
        └── __tests__/    # Component test files (future)
```

## Manual Testing Checklist

Since comprehensive automated tests require complex mocking of React hooks and external dependencies, the following manual testing checklist ensures the authentication UI works correctly:

### 1. Landing Page (`/`)

- [ ] Page loads without errors
- [ ] Navigation shows logo and brand name
- [ ] Hero section displays main call-to-action
- [ ] Features section shows all 6 feature cards
- [ ] CTA section has working buttons
- [ ] Footer displays company information
- [ ] All buttons trigger appropriate actions
- [ ] Responsive design works on different screen sizes

### 2. Login Page (`/login`)

- [ ] Page loads without errors
- [ ] Login form displays correctly
- [ ] Form validation works:
  - [ ] Required field validation
  - [ ] Email format validation
  - [ ] Password length validation
- [ ] Error messages display properly
- [ ] Loading states work during form submission
- [ ] Switch to register form works
- [ ] Back to home button works
- [ ] Form submission handles success/failure

### 3. Registration Page (`/login` - register mode)

- [ ] Registration form displays correctly
- [ ] Form validation works:
  - [ ] Required field validation
  - [ ] Full name length validation
  - [ ] Email format validation
  - [ ] Password strength validation
  - [ ] Password confirmation validation
- [ ] Password strength indicator works
- [ ] Error messages display properly
- [ ] Loading states work during form submission
- [ ] Switch to login form works
- [ ] Form submission handles success/failure

### 4. MFA Setup Page (`/mfa-setup`)

- [ ] Page loads without errors
- [ ] QR code displays correctly
- [ ] Secret key is shown with copy button
- [ ] Backup codes are displayed and can be toggled
- [ ] Copy functionality works for secret key and backup codes
- [ ] Form validation works for 6-digit code
- [ ] Setup completion works
- [ ] Cancel button works
- [ ] Error handling works

### 5. Dashboard Page (`/dashboard`)

- [ ] Page loads without errors (when authenticated)
- [ ] Navigation shows user information
- [ ] Welcome message displays correctly
- [ ] Quick action cards are clickable
- [ ] Recent activity section shows data
- [ ] System status indicators work
- [ ] Logout button works
- [ ] Responsive design works

### 6. Protected Routes

- [ ] Unauthenticated users are redirected to `/login`
- [ ] Authenticated users can access protected routes
- [ ] Public routes redirect authenticated users to `/dashboard`
- [ ] Loading states work during authentication checks

### 7. Authentication Flow

- [ ] User registration creates account successfully
- [ ] User login works with valid credentials
- [ ] JWT tokens are stored in localStorage
- [ ] MFA setup flow works end-to-end
- [ ] Logout clears all authentication data
- [ ] Session persistence works across page reloads

## Future Test Implementation

When ready to implement comprehensive automated tests, follow this approach:

### 1. Component Unit Tests

```typescript
// Example: LoginForm.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import LoginForm from '../LoginForm';

// Mock the auth store
vi.mock('@/stores/authStore', () => ({
  useAuthStore: () => ({
    login: vi.fn(),
    isLoading: false,
    error: null,
    clearError: vi.fn(),
  }),
}));

describe('LoginForm', () => {
  it('renders login form correctly', () => {
    render(<LoginForm />);
    expect(screen.getByLabelText(/email address/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
  });
});
```

### 2. Integration Tests

- Test complete authentication flows
- Test form submission and API integration
- Test routing and navigation

### 3. E2E Tests

- Use Playwright or Cypress for end-to-end testing
- Test complete user journeys
- Test cross-browser compatibility

## Testing Best Practices

### 1. Test Organization

- Group related tests using `describe` blocks
- Use descriptive test names
- Follow AAA pattern (Arrange, Act, Assert)

### 2. Mocking Strategy

- Mock external dependencies (API calls, stores)
- Use realistic mock data
- Avoid over-mocking

### 3. Test Data

- Use factories for creating test data
- Keep test data minimal and focused
- Use meaningful test values

### 4. Assertions

- Test behavior, not implementation
- Use semantic queries (getByRole, getByLabelText)
- Avoid testing implementation details

## Common Testing Patterns

### 1. Form Testing

```typescript
// Test form validation
it('validates required fields', async () => {
  render(<LoginForm />);
  const submitButton = screen.getByRole('button', { name: /sign in/i });
  fireEvent.click(submitButton);

  await waitFor(() => {
    expect(screen.getByText(/email is required/i)).toBeInTheDocument();
  });
});
```

### 2. User Interaction Testing

```typescript
// Test button clicks
it('calls onSuccess when form is submitted', async () => {
  const mockOnSuccess = vi.fn();
  render(<LoginForm onSuccess={mockOnSuccess} />);

  // Fill form and submit
  // ... form interaction code ...

  expect(mockOnSuccess).toHaveBeenCalledTimes(1);
});
```

### 3. Async Testing

```typescript
// Test async operations
it('handles API response', async () => {
  render(<Component />);

  await waitFor(() => {
    expect(screen.getByText(/success/i)).toBeInTheDocument();
  });
});
```

## Troubleshooting

### Common Issues

1. **Hook errors**: Ensure components are wrapped in necessary providers
2. **Mock failures**: Check mock implementations and imports
3. **Async test failures**: Use `waitFor` for async operations
4. **DOM errors**: Ensure jsdom is properly configured

### Debug Tips

- Use `screen.debug()` to inspect rendered output
- Check console for error messages
- Verify mock implementations
- Test components in isolation

## Conclusion

The current testing setup provides a foundation for future test implementation. The manual testing checklist ensures the authentication UI works correctly while the automated test infrastructure is being developed.

Focus on:

1. Manual testing of all user flows
2. Component integration testing
3. Gradual addition of unit tests
4. End-to-end testing for critical paths

This approach ensures code quality and prevents regressions as the application evolves.
