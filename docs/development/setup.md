# Development Setup Guide

This guide covers setting up the Personal Assistant TDAH system for local development.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Environment Setup](#environment-setup)
- [Database Setup](#database-setup)
- [Backend Setup](#backend-setup)
- [Frontend Setup](#frontend-setup)
- [Development Workflow](#development-workflow)
- [Testing Setup](#testing-setup)
- [Debugging](#debugging)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements

- **Operating System**: macOS, Linux, or Windows with WSL2
- **Python**: 3.11 or higher
- **Node.js**: 18 or higher
- **PostgreSQL**: 15 or higher
- **Redis**: 7 or higher
- **Docker**: 20.10+ (optional, for containerized development)
- **Git**: Latest version

### Development Tools

- **IDE**: VS Code (recommended) with extensions:
  - Python
  - Pylance
  - Python Docstring Generator
  - REST Client
  - Docker
- **Terminal**: iTerm2 (macOS) or equivalent
- **Database Client**: pgAdmin, DBeaver, or TablePlus
- **API Testing**: Postman or Insomnia

## Environment Setup

### 1. Clone Repository

```bash
git clone <repository-url>
cd personal_assistant
```

### 2. Python Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

### 3. Node.js Environment

```bash
# Navigate to frontend directory
cd src/apps/frontend

# Install dependencies
npm install

# Return to root directory
cd ../../..
```

### 4. Environment Configuration

```bash
# Copy environment template
cp config/env.example config/development.env

# Edit configuration
nano config/development.env
```

### Required Environment Variables

```bash
# Database
DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/database_name
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=15

# Redis
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Security
JWT_SECRET_KEY=your_jwt_secret_key_here_32_chars_minimum
ENCRYPTION_KEY=your_32_character_encryption_key_here

# External APIs
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
GOOGLE_API_KEY=your_google_api_key
GEMINI_API_KEY=your_gemini_api_key

# OAuth (for development)
GOOGLE_OAUTH_CLIENT_ID=your_google_oauth_client_id
GOOGLE_OAUTH_CLIENT_SECRET=your_google_oauth_client_secret
GOOGLE_OAUTH_REDIRECT_URI=http://localhost:8000/api/oauth/google/callback

MICROSOFT_OAUTH_CLIENT_ID=your_microsoft_oauth_client_id
MICROSOFT_OAUTH_CLIENT_SECRET=your_microsoft_oauth_client_secret
MICROSOFT_OAUTH_REDIRECT_URI=http://localhost:8000/api/oauth/microsoft/callback

NOTION_OAUTH_CLIENT_ID=your_notion_oauth_client_id
NOTION_OAUTH_CLIENT_SECRET=your_notion_oauth_client_secret
NOTION_OAUTH_REDIRECT_URI=http://localhost:8000/api/oauth/notion/callback
```

## Database Setup

### 1. Install PostgreSQL

#### macOS (using Homebrew)

```bash
brew install postgresql@15
brew services start postgresql@15
```

#### Ubuntu/Debian

```bash
sudo apt update
sudo apt install postgresql-15 postgresql-client-15
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

#### Windows

Download and install from [PostgreSQL official website](https://www.postgresql.org/download/windows/)

### 2. Create Database

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE personal_assistant_dev;

# Create user (optional)
CREATE USER dev_user WITH PASSWORD 'dev_password';
GRANT ALL PRIVILEGES ON DATABASE personal_assistant_dev TO dev_user;

# Exit psql
\q
```

### 3. Run Migrations

```bash
# Activate virtual environment
source venv/bin/activate

# Run database migrations
python -m alembic upgrade head

# Verify tables created
psql -U postgres -d personal_assistant_dev -c "\dt"
```

## Backend Setup

### 1. Install Dependencies

```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Install all dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest pytest-asyncio pytest-cov black isort flake8 mypy
```

### 2. Start Backend Services

```bash
# Start Redis (if not running)
redis-server

# Start Celery worker (in separate terminal)
celery -A personal_assistant.workers.celery_app worker --loglevel=info

# Start Celery beat (in separate terminal)
celery -A personal_assistant.workers.celery_app beat --loglevel=info

# Start FastAPI server
uvicorn src.apps.fastapi_app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Verify Backend Setup

```bash
# Check API health
curl http://localhost:8000/health/overall

# Check API documentation
open http://localhost:8000/docs
```

## Frontend Setup

### 1. Install Dependencies

```bash
# Navigate to frontend directory
cd src/apps/frontend

# Install dependencies
npm install

# Install development dependencies
npm install --save-dev @types/node @types/react @types/react-dom
```

### 2. Configure Frontend

```bash
# Create environment file
cp .env.example .env.local

# Edit environment variables
nano .env.local
```

### Frontend Environment Variables

```bash
# API Configuration
VITE_API_URL=http://localhost:8000
VITE_API_VERSION=v1

# Development Settings
VITE_DEBUG=true
VITE_LOG_LEVEL=debug

# OAuth Redirect URIs (for development)
VITE_GOOGLE_OAUTH_REDIRECT_URI=http://localhost:3001/oauth/google/callback
VITE_MICROSOFT_OAUTH_REDIRECT_URI=http://localhost:3001/oauth/microsoft/callback
VITE_NOTION_OAUTH_REDIRECT_URI=http://localhost:3001/oauth/notion/callback
```

### 3. Start Frontend Development Server

```bash
# Start development server
npm run dev

# Or with specific port
npm run dev -- --port 3001
```

### 4. Verify Frontend Setup

```bash
# Check frontend
open http://localhost:3001
```

## Development Workflow

### 1. Daily Development Routine

```bash
# Start development environment
./scripts/dev-start.sh

# Or manually:
# Terminal 1: Redis
redis-server

# Terminal 2: Celery Worker
celery -A personal_assistant.workers.celery_app worker --loglevel=info

# Terminal 3: Celery Beat
celery -A personal_assistant.workers.celery_app beat --loglevel=info

# Terminal 4: FastAPI
uvicorn src.apps.fastapi_app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 5: Frontend
cd src/apps/frontend && npm run dev
```

### 2. Code Quality Tools

```bash
# Format Python code
black src/
isort src/

# Lint Python code
flake8 src/
mypy src/

# Format TypeScript/React code
npm run format

# Lint TypeScript/React code
npm run lint
```

### 3. Database Development

```bash
# Create new migration
python -m alembic revision --autogenerate -m "Description of changes"

# Apply migrations
python -m alembic upgrade head

# Rollback migration
python -m alembic downgrade -1

# Check migration status
python -m alembic current
python -m alembic history
```

### 4. API Development

```bash
# Test API endpoints
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123","full_name":"Test User"}'

# Test with authentication
curl -X GET http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Testing Setup

### 1. Backend Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_auth.py

# Run with coverage
pytest --cov=src --cov-report=html

# Run tests with verbose output
pytest -v
```

### 2. Frontend Testing

```bash
# Navigate to frontend directory
cd src/apps/frontend

# Run unit tests
npm test

# Run tests with coverage
npm run test:coverage

# Run tests in watch mode
npm run test:watch
```

### 3. Integration Testing

```bash
# Run integration tests
pytest tests/integration/

# Run end-to-end tests
npm run test:e2e
```

## Debugging

### 1. Backend Debugging

```python
# Add breakpoints in code
import pdb; pdb.set_trace()

# Or use debugger in VS Code
# Set breakpoints in VS Code and run with debugger
```

### 2. Frontend Debugging

```javascript
// Add breakpoints in browser dev tools
console.log("Debug info:", data);

// Use React DevTools extension
// Install React Developer Tools browser extension
```

### 3. Database Debugging

```sql
-- Enable query logging in PostgreSQL
-- In postgresql.conf:
log_statement = 'all'
log_min_duration_statement = 0

-- Check slow queries
SELECT query, mean_time, calls
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
```

### 4. API Debugging

```bash
# Use API documentation for testing
open http://localhost:8000/docs

# Use Postman or Insomnia for API testing
# Import OpenAPI spec from http://localhost:8000/openapi.json
```

## Troubleshooting

### Common Issues

1. **Database Connection Issues**:

   ```bash
   # Check PostgreSQL status
   sudo systemctl status postgresql

   # Check connection
   psql -U postgres -h localhost -p 5432
   ```

2. **Redis Connection Issues**:

   ```bash
   # Check Redis status
   redis-cli ping

   # Check Redis logs
   tail -f /var/log/redis/redis-server.log
   ```

3. **Port Conflicts**:

   ```bash
   # Check port usage
   netstat -tulpn | grep :8000
   lsof -i :8000
   ```

4. **Python Environment Issues**:

   ```bash
   # Recreate virtual environment
   rm -rf venv
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

5. **Node.js Issues**:

   ```bash
   # Clear npm cache
   npm cache clean --force

   # Delete node_modules and reinstall
   rm -rf node_modules package-lock.json
   npm install
   ```

### Performance Issues

1. **Slow Database Queries**:

   ```bash
   # Check slow queries
   python -c "
   from personal_assistant.database.connection import get_db
   db = next(get_db())
   result = db.execute('SELECT * FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10')
   print(result.fetchall())
   "
   ```

2. **High Memory Usage**:

   ```bash
   # Check memory usage
   ps aux | grep python
   htop
   ```

3. **Slow API Responses**:
   ```bash
   # Check API response times
   curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/health/overall
   ```

### Development Scripts

Create helpful development scripts:

```bash
# scripts/dev-start.sh
#!/bin/bash
echo "Starting development environment..."

# Start Redis
redis-server --daemonize yes

# Start Celery worker
celery -A personal_assistant.workers.celery_app worker --loglevel=info --detach

# Start Celery beat
celery -A personal_assistant.workers.celery_app beat --loglevel=info --detach

# Start FastAPI
uvicorn src.apps.fastapi_app.main:app --reload --host 0.0.0.0 --port 8000 &

# Start Frontend
cd src/apps/frontend && npm run dev &

echo "Development environment started!"
echo "API: http://localhost:8000"
echo "Frontend: http://localhost:3001"
echo "API Docs: http://localhost:8000/docs"
```

```bash
# scripts/dev-stop.sh
#!/bin/bash
echo "Stopping development environment..."

# Stop all processes
pkill -f "uvicorn"
pkill -f "celery"
pkill -f "npm run dev"
pkill -f "redis-server"

echo "Development environment stopped!"
```

This development setup guide provides comprehensive instructions for setting up and running the Personal Assistant TDAH system in a local development environment.
