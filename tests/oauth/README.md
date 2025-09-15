# OAuth Testing Suite

This directory contains comprehensive tests for the OAuth integration system, which is the main use case of the Personal Assistant application.

## Test Structure

```
tests/oauth/
├── conftest.py                    # Shared test fixtures and configuration
├── test_runner.py                 # Test runner script
├── test_token_service.py          # Token service tests
├── test_providers/                # Provider-specific tests
│   ├── test_google_provider.py    # Google OAuth provider tests
│   └── test_notion_provider.py    # Notion OAuth provider tests
├── agent_oauth/                   # Agent-OAuth integration tests
│   ├── test_enhanced_notes_tool.py # Enhanced notes tool OAuth tests
│   └── test_notion_client_factory.py # Notion client factory tests
├── e2e_oauth/                     # End-to-end OAuth flow tests
│   └── test_complete_oauth_flow.py # Complete OAuth journey tests
└── security_oauth/                # OAuth security tests
    ├── test_token_encryption.py   # Token encryption security tests
    └── test_user_isolation.py     # User isolation security tests
```

## Running Tests

### Run All OAuth Tests

```bash
python tests/oauth/test_runner.py
```

### Run Specific Test Categories

```bash
# Provider tests
pytest tests/oauth/test_providers/ -v

# Agent integration tests
pytest tests/agent_oauth/ -v

# End-to-end tests
pytest tests/e2e_oauth/ -v

# Security tests
pytest tests/security_oauth/ -v

# Token service tests
pytest tests/oauth/test_token_service.py -v
```

### Run Individual Test Files

```bash
# Google provider tests
pytest tests/oauth/test_providers/test_google_provider.py -v

# Enhanced notes tool tests
pytest tests/agent_oauth/test_enhanced_notes_tool.py -v

# Token encryption tests
pytest tests/security_oauth/test_token_encryption.py -v
```

## Test Coverage

### Provider Tests

- **Google Provider**: Authorization URL generation, token exchange, user info retrieval, token validation, token revocation
- **Notion Provider**: Similar to Google provider with Notion-specific endpoints
- **Microsoft Provider**: (To be implemented)
- **YouTube Provider**: (To be implemented)

### Token Service Tests

- Token encryption/decryption
- Token storage and retrieval
- Token refresh logic
- Token expiration handling
- Concurrent token operations
- Error handling

### Agent Integration Tests

- **Enhanced Notes Tool**: User-specific Notion client creation, note creation with OAuth, user isolation, token refresh during tool execution
- **Notion Client Factory**: User client creation, caching, workspace validation, error handling

### End-to-End Tests

- Complete OAuth journey from initiation to agent usage
- Multi-provider OAuth flows
- Token refresh scenarios
- Error handling throughout the flow
- Concurrent user operations

### Security Tests

- **Token Encryption**: Uniqueness, different tokens, special characters, performance, thread safety
- **User Isolation**: Token isolation, integration isolation, client factory isolation, agent tool isolation, concurrent operations

## Test Fixtures

The `conftest.py` file provides shared fixtures for:

- Database sessions
- OAuth manager instances
- Service instances (token, integration, security, consent)
- Mock OAuth providers
- Mock user data and tokens
- Mock OAuth integrations and states
- Mock client instances (Notion, Google Calendar, Gmail, YouTube, Microsoft Graph)
- OAuth test configuration
- Mock OAuth states

## Test Data

Tests use mock data to avoid requiring actual OAuth credentials:

- Mock OAuth applications for each provider
- Test accounts and sandbox environments
- Mock OAuth provider responses
- Test database with OAuth schema

## Security Considerations

Tests validate:

- Token encryption at rest
- User data isolation
- State validation and CSRF protection
- Token security and uniqueness
- Concurrent operation safety
- Thread safety of encryption operations

## Performance Testing

Tests include performance validation for:

- Token encryption/decryption speed
- Concurrent OAuth operations
- Memory usage during token operations
- Thread safety under load

## Error Handling

Tests cover error scenarios:

- Invalid OAuth credentials
- Expired tokens
- Network failures
- Provider API errors
- Database errors
- Invalid state tokens
- Cross-user access attempts

## Dependencies

Tests require:

- pytest
- pytest-asyncio
- unittest.mock
- sqlalchemy
- cryptography (for token encryption)

## Continuous Integration

These tests are designed to run in CI/CD pipelines and provide:

- Comprehensive coverage reporting
- Performance benchmarks
- Security validation
- Error scenario testing
- User isolation verification

## Maintenance

When adding new OAuth providers or features:

1. Add provider-specific tests in `test_providers/`
2. Add agent integration tests in `agent_oauth/`
3. Add end-to-end flow tests in `e2e_oauth/`
4. Add security tests in `security_oauth/`
5. Update fixtures in `conftest.py` if needed
6. Update this README with new test coverage
