# Contributing Guide

This guide outlines how to contribute to the Personal Assistant TDAH system project.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Process](#development-process)
- [Code Standards](#code-standards)
- [Testing Requirements](#testing-requirements)
- [Documentation Standards](#documentation-standards)
- [Pull Request Process](#pull-request-process)
- [Issue Reporting](#issue-reporting)
- [Code Review Guidelines](#code-review-guidelines)
- [Release Process](#release-process)

## Getting Started

### Prerequisites

- Read the [Development Setup Guide](setup.md)
- Familiarize yourself with the [Architecture Documentation](../architecture/README.md)
- Review the [API Documentation](../api/README.md)

### Development Environment

1. **Fork the Repository**: Fork the repository on GitHub
2. **Clone Your Fork**: Clone your fork locally
3. **Set Up Development Environment**: Follow the [Development Setup Guide](setup.md)
4. **Create a Branch**: Create a feature branch for your changes

```bash
# Fork the repository on GitHub, then:
git clone https://github.com/YOUR_USERNAME/personal_assistant.git
cd personal_assistant
git checkout -b feature/your-feature-name
```

## Development Process

### 1. Planning

Before starting development:

- [ ] **Check Existing Issues**: Look for related issues or discussions
- [ ] **Create Issue**: Create an issue describing the feature or bug fix
- [ ] **Discuss Approach**: Discuss the implementation approach in the issue
- [ ] **Get Approval**: Get approval from maintainers before starting

### 2. Development Workflow

```bash
# 1. Update your fork
git fetch upstream
git checkout main
git merge upstream/main

# 2. Create feature branch
git checkout -b feature/your-feature-name

# 3. Make changes and commit
git add .
git commit -m "feat: add new feature"

# 4. Push to your fork
git push origin feature/your-feature-name

# 5. Create pull request
# Go to GitHub and create a pull request
```

### 3. Commit Message Format

Use conventional commit messages:

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

**Types**:

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples**:

```
feat(auth): add MFA support for user authentication

fix(api): resolve database connection timeout issue

docs(api): update authentication endpoint documentation

test(auth): add unit tests for MFA verification
```

## Code Standards

### Python Code Standards

#### Formatting

- Use **Black** for code formatting
- Use **isort** for import sorting
- Maximum line length: 88 characters

```bash
# Format code
black src/
isort src/
```

#### Linting

- Use **flake8** for linting
- Use **mypy** for type checking

```bash
# Lint code
flake8 src/
mypy src/
```

#### Code Style

- Follow PEP 8 guidelines
- Use type hints for all functions
- Write docstrings for all public functions and classes
- Use meaningful variable and function names

```python
# Good example
def authenticate_user(email: str, password: str) -> Optional[User]:
    """
    Authenticate a user with email and password.

    Args:
        email: User's email address
        password: User's password

    Returns:
        User object if authentication successful, None otherwise

    Raises:
        AuthenticationError: If authentication fails
    """
    # Implementation here
    pass
```

### TypeScript/React Code Standards

#### Formatting

- Use **Prettier** for code formatting
- Use **ESLint** for linting

```bash
# Format code
npm run format

# Lint code
npm run lint
```

#### Code Style

- Use TypeScript for all components
- Use functional components with hooks
- Follow React best practices
- Use meaningful component and variable names

```typescript
// Good example
interface UserProfileProps {
  userId: string;
  onUpdate: (user: User) => void;
}

const UserProfile: React.FC<UserProfileProps> = ({ userId, onUpdate }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchUser(userId)
      .then(setUser)
      .finally(() => setLoading(false));
  }, [userId]);

  if (loading) return <LoadingSpinner />;
  if (!user) return <ErrorMessage message="User not found" />;

  return (
    <div className="user-profile">
      <h1>{user.fullName}</h1>
      <p>{user.email}</p>
    </div>
  );
};
```

### Database Standards

#### Migrations

- Use Alembic for database migrations
- Write reversible migrations when possible
- Include both upgrade and downgrade functions
- Test migrations on development database

```python
# Migration example
def upgrade():
    # Add new column
    op.add_column('users', sa.Column('phone_number', sa.String(20), nullable=True))

    # Create index
    op.create_index('idx_users_phone', 'users', ['phone_number'])

def downgrade():
    # Remove index
    op.drop_index('idx_users_phone', 'users')

    # Remove column
    op.drop_column('users', 'phone_number')
```

#### Models

- Use SQLAlchemy models
- Include proper relationships and constraints
- Use appropriate data types
- Add indexes for frequently queried columns

```python
# Model example
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False, index=True)
    full_name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    conversations = relationship("ConversationState", back_populates="user")
```

## Testing Requirements

### Backend Testing

#### Unit Tests

- Write unit tests for all business logic
- Aim for 80%+ code coverage
- Use pytest and pytest-asyncio

```python
# Test example
import pytest
from unittest.mock import Mock, patch
from personal_assistant.services.auth import AuthService

class TestAuthService:
    @pytest.fixture
    def auth_service(self):
        return AuthService()

    @pytest.mark.asyncio
    async def test_authenticate_user_success(self, auth_service):
        # Arrange
        email = "test@example.com"
        password = "password123"

        # Act
        result = await auth_service.authenticate_user(email, password)

        # Assert
        assert result is not None
        assert result.email == email
```

#### Integration Tests

- Test API endpoints
- Test database interactions
- Test external service integrations

```python
# Integration test example
import pytest
from httpx import AsyncClient
from personal_assistant.apps.fastapi_app.main import app

@pytest.mark.asyncio
async def test_user_registration():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/api/v1/auth/register", json={
            "email": "test@example.com",
            "password": "password123",
            "full_name": "Test User"
        })

        assert response.status_code == 201
        assert "access_token" in response.json()
```

### Frontend Testing

#### Unit Tests

- Test React components
- Test utility functions
- Use Jest and React Testing Library

```typescript
// Test example
import { render, screen, fireEvent } from "@testing-library/react";
import { UserProfile } from "./UserProfile";

describe("UserProfile", () => {
  it("renders user information correctly", () => {
    const mockUser = {
      id: "1",
      fullName: "John Doe",
      email: "john@example.com",
    };

    render(<UserProfile userId="1" onUpdate={jest.fn()} />);

    expect(screen.getByText("John Doe")).toBeInTheDocument();
    expect(screen.getByText("john@example.com")).toBeInTheDocument();
  });
});
```

#### E2E Tests

- Test complete user workflows
- Use Playwright or Cypress

```typescript
// E2E test example
import { test, expect } from "@playwright/test";

test("user can register and login", async ({ page }) => {
  await page.goto("/register");

  await page.fill('[data-testid="email"]', "test@example.com");
  await page.fill('[data-testid="password"]', "password123");
  await page.fill('[data-testid="full-name"]', "Test User");

  await page.click('[data-testid="register-button"]');

  await expect(page).toHaveURL("/dashboard");
  await expect(page.locator('[data-testid="welcome-message"]')).toContainText(
    "Welcome, Test User"
  );
});
```

## Documentation Standards

### Code Documentation

#### Python Docstrings

- Use Google-style docstrings
- Document all public functions and classes
- Include type information and examples

```python
def send_sms(phone_number: str, message: str, user_id: int) -> bool:
    """
    Send SMS message to specified phone number.

    Args:
        phone_number: Recipient's phone number in E.164 format
        message: SMS message content (max 160 characters)
        user_id: ID of user sending the SMS

    Returns:
        True if SMS sent successfully, False otherwise

    Raises:
        ValidationError: If phone number format is invalid
        TwilioError: If SMS service fails

    Example:
        >>> send_sms("+1234567890", "Hello World", 123)
        True
    """
    pass
```

#### TypeScript Documentation

- Use JSDoc comments
- Document all public functions and components

````typescript
/**
 * Sends SMS message to specified phone number
 * @param phoneNumber - Recipient's phone number in E.164 format
 * @param message - SMS message content (max 160 characters)
 * @param userId - ID of user sending the SMS
 * @returns Promise that resolves to true if SMS sent successfully
 * @throws {ValidationError} If phone number format is invalid
 * @throws {TwilioError} If SMS service fails
 *
 * @example
 * ```typescript
 * const success = await sendSMS("+1234567890", "Hello World", 123);
 * console.log(success); // true
 * ```
 */
async function sendSMS(
  phoneNumber: string,
  message: string,
  userId: number
): Promise<boolean> {
  // Implementation here
}
````

### API Documentation

- Update OpenAPI specifications for new endpoints
- Include request/response examples
- Document error codes and messages

### README Updates

- Update relevant README files
- Include setup instructions for new features
- Document configuration changes

## Pull Request Process

### Before Submitting

- [ ] **Run Tests**: Ensure all tests pass
- [ ] **Code Quality**: Run linting and formatting tools
- [ ] **Documentation**: Update relevant documentation
- [ ] **Self Review**: Review your own code
- [ ] **Test Coverage**: Ensure adequate test coverage

### Pull Request Template

```markdown
## Description

Brief description of changes

## Type of Change

- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing

- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] E2E tests pass
- [ ] Manual testing completed

## Checklist

- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] No breaking changes (or documented)

## Related Issues

Closes #123
```

### Review Process

1. **Automated Checks**: CI/CD pipeline runs tests and checks
2. **Code Review**: At least one maintainer reviews the code
3. **Testing**: Reviewer tests the changes
4. **Approval**: Maintainer approves the PR
5. **Merge**: PR is merged into main branch

## Issue Reporting

### Bug Reports

Use the bug report template:

```markdown
## Bug Description

Clear description of the bug

## Steps to Reproduce

1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

## Expected Behavior

What you expected to happen

## Actual Behavior

What actually happened

## Environment

- OS: [e.g. macOS, Ubuntu]
- Browser: [e.g. Chrome, Firefox]
- Version: [e.g. 1.0.0]

## Additional Context

Any other context about the problem
```

### Feature Requests

Use the feature request template:

```markdown
## Feature Description

Clear description of the feature

## Use Case

Why is this feature needed?

## Proposed Solution

How should this feature work?

## Alternatives

Any alternative solutions considered

## Additional Context

Any other context about the feature request
```

## Code Review Guidelines

### For Reviewers

- **Be Constructive**: Provide helpful feedback
- **Be Specific**: Point out exact issues
- **Be Respectful**: Maintain professional tone
- **Be Thorough**: Check for security, performance, and maintainability issues

### Review Checklist

- [ ] **Functionality**: Does the code work as intended?
- [ ] **Tests**: Are there adequate tests?
- [ ] **Documentation**: Is documentation updated?
- [ ] **Performance**: Are there performance implications?
- [ ] **Security**: Are there security concerns?
- [ ] **Maintainability**: Is the code maintainable?
- [ ] **Standards**: Does the code follow project standards?

### For Authors

- **Respond Promptly**: Address review comments quickly
- **Be Open**: Accept constructive criticism
- **Ask Questions**: Clarify unclear feedback
- **Learn**: Use reviews as learning opportunities

## Release Process

### Version Numbering

Use semantic versioning (SemVer):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Steps

1. **Update Version**: Update version numbers in relevant files
2. **Update Changelog**: Document changes in CHANGELOG.md
3. **Create Release Branch**: Create release branch from main
4. **Testing**: Run full test suite
5. **Create Tag**: Create git tag for the release
6. **Deploy**: Deploy to staging and production
7. **Announce**: Announce release to users

### Changelog Format

```markdown
## [1.2.0] - 2024-01-15

### Added

- New MFA authentication feature
- SMS routing improvements
- Enhanced analytics dashboard

### Changed

- Updated OAuth integration flow
- Improved error handling

### Fixed

- Fixed database connection timeout issue
- Resolved SMS delivery status tracking

### Security

- Updated dependencies to address security vulnerabilities
```

## Community Guidelines

### Code of Conduct

- **Be Respectful**: Treat everyone with respect
- **Be Inclusive**: Welcome contributors from all backgrounds
- **Be Collaborative**: Work together constructively
- **Be Professional**: Maintain professional communication

### Getting Help

- **Documentation**: Check existing documentation first
- **Issues**: Search existing issues for similar problems
- **Discussions**: Use GitHub Discussions for questions
- **Maintainers**: Contact maintainers for urgent issues

### Recognition

Contributors are recognized in:

- CONTRIBUTORS.md file
- Release notes
- Project documentation

Thank you for contributing to the Personal Assistant TDAH system!
