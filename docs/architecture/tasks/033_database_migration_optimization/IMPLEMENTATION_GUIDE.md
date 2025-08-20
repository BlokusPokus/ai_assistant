# 🔧 Task 033 Implementation Guide: Database Migration & Optimization

## **📋 Implementation Overview**

This guide provides step-by-step instructions for implementing Task 033: Database Migration & Optimization. The task focuses on three main areas:

1. **Connection Pooling** - Optimize database connections for production
2. **Performance Monitoring** - Add health checks and metrics
3. **Containerization** - Prepare for Docker deployment

---

## **🚀 Phase 1: Connection Pooling Implementation**

### **Step 1.1: Create Enhanced Database Configuration**

#### **1.1.1 Create Database Config Directory**

```bash
mkdir -p src/personal_assistant/config
```

#### **1.1.2 Create Database Configuration File**

Create `src/personal_assistant/config/database.py`:

```python
"""
Enhanced database configuration with connection pooling.

This module provides production-ready database configuration
with connection pooling, health monitoring, and optimization.
"""

import os
import logging
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.pool import QueuePool
from sqlalchemy.orm import sessionmaker
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

class DatabaseConfig:
    """Database configuration with connection pooling."""

    def __init__(self):
        # Connection pool settings
        self.pool_size = int(os.getenv('DB_POOL_SIZE', 20))
        self.max_overflow = int(os.getenv('DB_MAX_OVERFLOW', 30))
        self.pool_timeout = int(os.getenv('DB_POOL_TIMEOUT', 30))
        self.pool_recycle = int(os.getenv('DB_POOL_RECYCLE', 3600))
        self.pool_pre_ping = os.getenv('DB_POOL_PRE_PING', 'true').lower() == 'true'

        # Performance settings
        self.echo = os.getenv('DB_ECHO', 'false').lower() == 'true'
        self.echo_pool = os.getenv('DB_ECHO_POOL', 'false').lower() == 'true'

        # Connection settings
        self.connect_args = {
            'server_settings': {
                'application_name': 'personal_assistant',
                'jit': 'off',  # Disable JIT for better performance
            }
        }

        # Get database URL
        self.database_url = os.getenv(
            "REAL_DB_URL",
            "postgresql+asyncpg://ianleblanc:password@localhost:5432/postgres"
        )

    def create_engine(self):
        """Create async database engine with connection pooling."""
        try:
            engine = create_async_engine(
                self.database_url,
                poolclass=QueuePool,
                pool_size=self.pool_size,
                max_overflow=self.max_overflow,
                pool_timeout=self.pool_timeout,
                pool_recycle=self.pool_recycle,
                pool_pre_ping=self.pool_pre_ping,
                echo=self.echo,
                echo_pool=self.echo_pool,
                connect_args=self.connect_args
            )

            logger.info(f"Database engine created with pool_size={self.pool_size}")
            return engine

        except Exception as e:
            logger.error(f"Failed to create database engine: {e}")
            raise

    def get_pool_stats(self, engine) -> Dict[str, Any]:
        """Get connection pool statistics."""
        if hasattr(engine, 'pool'):
            pool = engine.pool
            return {
                'pool_size': pool.size(),
                'checked_in': pool.checkedin(),
                'checked_out': pool.checkedout(),
                'overflow': pool.overflow(),
                'invalid': pool.invalid()
            }
        return {}

# Global database configuration instance
db_config = DatabaseConfig()

# Create async engine
engine = db_config.create_engine()

# Create async session factory
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

@asynccontextmanager
async def get_db_session():
    """Get database session with proper cleanup."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def get_db() -> AsyncSession:
    """Get database session (for FastAPI dependency injection)."""
    async with get_db_session() as session:
        yield session
```

#### **1.1.3 Update Session Import**

Update `src/personal_assistant/database/session.py`:

```python
"""
Database session management.

This module now imports from the enhanced configuration.
"""

from personal_assistant.config.database import AsyncSessionLocal, get_db, engine

# Re-export for backward compatibility
__all__ = ['AsyncSessionLocal', 'get_db', 'engine']
```

### **Step 1.2: Implement Health Check Endpoints**

#### **1.2.1 Create Monitoring Configuration**

Create `src/personal_assistant/config/monitoring.py`:

```python
"""
Database monitoring and health checks.

This module provides health check endpoints and performance metrics
for the database layer.
"""

import time
import logging
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from .database import get_db, db_config, engine

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/health", tags=["health"])

@router.get("/database")
async def database_health(db: AsyncSession = Depends(get_db)):
    """Check database connectivity and health."""
    start_time = time.time()

    try:
        # Test basic connectivity
        result = await db.execute(text("SELECT 1 as health_check"))
        health_check = result.scalar()

        # Get pool statistics
        pool_stats = db_config.get_pool_stats(engine)

        # Calculate response time
        response_time = (time.time() - start_time) * 1000

        return {
            "status": "healthy",
            "database": "connected",
            "response_time_ms": round(response_time, 2),
            "pool_stats": pool_stats,
            "timestamp": time.time()
        }

    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
            "response_time_ms": (time.time() - start_time) * 1000,
            "timestamp": time.time()
        }

@router.get("/database/pool")
async def database_pool_status():
    """Get detailed connection pool status."""
    try:
        pool_stats = db_config.get_pool_stats(engine)

        # Calculate pool utilization
        total_connections = pool_stats.get('pool_size', 0)
        active_connections = pool_stats.get('checked_out', 0)
        utilization = (active_connections / total_connections * 100) if total_connections > 0 else 0

        return {
            "status": "success",
            "pool_stats": pool_stats,
            "utilization_percent": round(utilization, 2),
            "timestamp": time.time()
        }

    except Exception as e:
        logger.error(f"Failed to get pool status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/database/performance")
async def database_performance_metrics(db: AsyncSession = Depends(get_db)):
    """Get database performance metrics."""
    start_time = time.time()

    try:
        # Test query performance
        result = await db.execute(text("SELECT COUNT(*) FROM users"))
        user_count = result.scalar()

        # Test RBAC table performance
        result = await db.execute(text("SELECT COUNT(*) FROM roles"))
        role_count = result.scalar()

        response_time = (time.time() - start_time) * 1000

        return {
            "status": "success",
            "metrics": {
                "user_count": user_count,
                "role_count": role_count,
                "query_response_time_ms": round(response_time, 2)
            },
            "timestamp": time.time()
        }

    except Exception as e:
        logger.error(f"Failed to get performance metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

#### **1.2.2 Add Health Routes to Main App**

Update `src/apps/fastapi_app/main.py`:

```python
# Add this import
from personal_assistant.config.monitoring import router as health_router

# Add this line after other router includes
app.include_router(health_router)
```

---

## **🚀 Phase 2: Performance Optimization**

### **Step 2.1: Create Performance Optimization Module**

#### **2.1.1 Create Optimization Configuration**

Create `src/personal_assistant/config/optimization.py`:

```python
"""
Database performance optimization configuration.

This module provides performance tuning settings and optimization
strategies for the database layer.
"""

import os
import logging
from typing import Dict, Any, List
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

class DatabaseOptimizer:
    """Database performance optimization utilities."""

    def __init__(self):
        self.optimization_enabled = os.getenv('DB_OPTIMIZATION_ENABLED', 'true').lower() == 'true'
        self.query_timeout = int(os.getenv('DB_QUERY_TIMEOUT', 30))
        self.max_query_time = int(os.getenv('DB_MAX_QUERY_TIME', 100))

    async def analyze_table_performance(self, db: AsyncSession, table_name: str) -> Dict[str, Any]:
        """Analyze table performance and suggest optimizations."""
        try:
            # Get table statistics
            result = await db.execute(text(f"""
                SELECT
                    schemaname,
                    tablename,
                    n_tup_ins as inserts,
                    n_tup_upd as updates,
                    n_tup_del as deletes,
                    n_live_tup as live_rows,
                    n_dead_tup as dead_rows,
                    last_vacuum,
                    last_autovacuum,
                    last_analyze,
                    last_autoanalyze
                FROM pg_stat_user_tables
                WHERE tablename = :table_name
            """), {"table_name": table_name})

            stats = result.fetchone()

            if not stats:
                return {"error": f"Table {table_name} not found"}

            # Analyze index usage
            index_result = await db.execute(text(f"""
                SELECT
                    indexname,
                    idx_scan as scans,
                    idx_tup_read as tuples_read,
                    idx_tup_fetch as tuples_fetched
                FROM pg_stat_user_indexes
                WHERE tablename = :table_name
            """), {"table_name": table_name})

            indexes = index_result.fetchall()

            return {
                "table_name": table_name,
                "statistics": dict(stats._mapping) if stats else {},
                "indexes": [dict(idx._mapping) for idx in indexes],
                "recommendations": self._generate_recommendations(stats, indexes)
            }

        except Exception as e:
            logger.error(f"Failed to analyze table {table_name}: {e}")
            return {"error": str(e)}

    def _generate_recommendations(self, stats, indexes) -> List[str]:
        """Generate optimization recommendations based on statistics."""
        recommendations = []

        if stats:
            # Check for table bloat
            if stats.n_dead_tup and stats.n_live_tup:
                dead_ratio = stats.n_dead_tup / (stats.n_live_tup + stats.n_dead_tup)
                if dead_ratio > 0.1:  # More than 10% dead tuples
                    recommendations.append("Consider running VACUUM to clean up dead tuples")

            # Check for missing statistics
            if not stats.last_analyze:
                recommendations.append("Table statistics are outdated, consider running ANALYZE")

        # Check index usage
        unused_indexes = [idx for idx in indexes if idx.idx_scan == 0]
        if unused_indexes:
            recommendations.append(f"Found {len(unused_indexes)} unused indexes that could be removed")

        return recommendations

    async def optimize_queries(self, db: AsyncSession) -> Dict[str, Any]:
        """Run query optimization and return recommendations."""
        try:
            # Get slow queries
            result = await db.execute(text("""
                SELECT
                    query,
                    calls,
                    total_time,
                    mean_time,
                    rows
                FROM pg_stat_statements
                ORDER BY mean_time DESC
                LIMIT 10
            """))

            slow_queries = result.fetchall()

            return {
                "status": "success",
                "slow_queries": [dict(q._mapping) for q in slow_queries],
                "recommendations": self._generate_query_recommendations(slow_queries)
            }

        except Exception as e:
            logger.error(f"Failed to optimize queries: {e}")
            return {"error": str(e)}

    def _generate_query_recommendations(self, slow_queries) -> List[str]:
        """Generate query optimization recommendations."""
        recommendations = []

        for query in slow_queries:
            if query.mean_time > self.max_query_time:
                recommendations.append(f"Query with mean time {query.mean_time}ms exceeds threshold")

        return recommendations

# Global optimizer instance
db_optimizer = DatabaseOptimizer()
```

### **Step 2.2: Enhance Migration System**

#### **2.2.1 Create Migration Manager**

Create `src/personal_assistant/database/migrations/manager.py`:

```python
"""
Migration management system.

This module provides a robust migration system with rollback
capabilities and data integrity validation.
"""

import os
import logging
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

logger = logging.getLogger(__name__)

class MigrationManager:
    """Manages database migrations with rollback support."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.migrations_table = "schema_migrations"

    async def ensure_migrations_table(self):
        """Ensure the migrations tracking table exists."""
        try:
            await self.db.execute(text(f"""
                CREATE TABLE IF NOT EXISTS {self.migrations_table} (
                    id SERIAL PRIMARY KEY,
                    version VARCHAR(255) UNIQUE NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    checksum VARCHAR(64),
                    rollback_sql TEXT
                )
            """))
            await self.db.commit()
            logger.info("Migrations table ensured")
        except Exception as e:
            logger.error(f"Failed to create migrations table: {e}")
            await self.db.rollback()
            raise

    async def get_applied_migrations(self) -> List[Dict[str, Any]]:
        """Get list of applied migrations."""
        try:
            result = await self.db.execute(text(f"""
                SELECT version, name, applied_at, checksum
                FROM {self.migrations_table}
                ORDER BY applied_at
            """))

            migrations = []
            for row in result.fetchall():
                migrations.append({
                    'version': row.version,
                    'name': row.name,
                    'applied_at': row.applied_at,
                    'checksum': row.checksum
                })

            return migrations

        except Exception as e:
            logger.error(f"Failed to get applied migrations: {e}")
            return []

    async def apply_migration(self, version: str, name: str, sql: str, rollback_sql: str = None):
        """Apply a migration with rollback support."""
        try:
            # Check if migration already applied
            existing = await self.db.execute(text(f"""
                SELECT version FROM {self.migrations_table} WHERE version = :version
            """), {"version": version})

            if existing.fetchone():
                logger.info(f"Migration {version} already applied, skipping")
                return

            # Apply migration
            await self.db.execute(text(sql))

            # Record migration
            await self.db.execute(text(f"""
                INSERT INTO {self.migrations_table} (version, name, rollback_sql)
                VALUES (:version, :name, :rollback_sql)
            """), {
                "version": version,
                "name": name,
                "rollback_sql": rollback_sql
            })

            await self.db.commit()
            logger.info(f"Migration {version} applied successfully")

        except Exception as e:
            logger.error(f"Failed to apply migration {version}: {e}")
            await self.db.rollback()
            raise

    async def rollback_migration(self, version: str):
        """Rollback a specific migration."""
        try:
            # Get migration details
            result = await self.db.execute(text(f"""
                SELECT name, rollback_sql FROM {self.migrations_table}
                WHERE version = :version
            """), {"version": version})

            migration = result.fetchone()
            if not migration:
                raise ValueError(f"Migration {version} not found")

            if not migration.rollback_sql:
                raise ValueError(f"Migration {version} has no rollback SQL")

            # Execute rollback
            await self.db.execute(text(migration.rollback_sql))

            # Remove migration record
            await self.db.execute(text(f"""
                DELETE FROM {self.migrations_table} WHERE version = :version
            """), {"version": version})

            await self.db.commit()
            logger.info(f"Migration {version} rolled back successfully")

        except Exception as e:
            logger.error(f"Failed to rollback migration {version}: {e}")
            await self.db.rollback()
            raise

    async def validate_migration(self, version: str, sql: str) -> bool:
        """Validate migration SQL before applying."""
        try:
            # Basic SQL validation
            if not sql.strip():
                return False

            # Check for dangerous operations
            dangerous_keywords = ['DROP DATABASE', 'TRUNCATE', 'DELETE FROM']
            sql_upper = sql.upper()

            for keyword in dangerous_keywords:
                if keyword in sql_upper:
                    logger.warning(f"Migration {version} contains potentially dangerous operation: {keyword}")
                    return False

            return True

        except Exception as e:
            logger.error(f"Failed to validate migration {version}: {e}")
            return False
```

---

## **🚀 Phase 3: Containerization Preparation**

### **Step 3.1: Create Docker Configuration**

#### **3.1.1 Create Multi-stage Dockerfile**

Create `docker/Dockerfile`:

```dockerfile
# Multi-stage Dockerfile for Personal Assistant API
FROM python:3.11-slim as builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.11-slim as runtime

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd --create-home --shell /bin/bash app

# Set work directory
WORKDIR /app

# Copy Python packages from builder
COPY --from=builder /root/.local /home/app/.local

# Copy application code
COPY src/ ./src/

# Set ownership
RUN chown -R app:app /app

# Switch to non-root user
USER app

# Add local bin to PATH
ENV PATH=/home/app/.local/bin:$PATH

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/database || exit 1

# Run application
CMD ["python", "-m", "uvicorn", "src.apps.fastapi_app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### **3.1.2 Create Docker Compose Configuration**

Create `docker/docker-compose.yml`:

```yaml
version: "3.8"

services:
  app:
    build:
      context: ..
      dockerfile: docker/Dockerfile
    ports:
      - "8000:8000"
    environment:
      - REAL_DB_URL=postgresql+asyncpg://postgres:password@postgres:5432/postgres
      - DB_POOL_SIZE=20
      - DB_MAX_OVERFLOW=30
      - DB_POOL_TIMEOUT=30
      - PA_LOG_LEVEL=INFO
    depends_on:
      - postgres
      - redis
    volumes:
      - ../logs:/app/logs
    restart: unless-stopped

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=postgres
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./postgres/init:/docker-entrypoint-initdb.d
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
```

#### **3.1.3 Create .dockerignore File**

Create `.dockerignore`:

```dockerignore
# Git
.git
.gitignore

# Python
__pycache__
*.pyc
*.pyo
*.pyd
.Python
env
pip-log.txt
pip-delete-this-directory.txt
.tox
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.log
.git
.mypy_cache
.pytest_cache
.hypothesis

# Virtual environments
venv/
venv_personal_assistant/
ENV/
env/
.venv/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Documentation
docs/
*.md
README*

# Logs
logs/
*.log

# Tests
tests/
pytest.ini

# Development
scripts/
setup.py
setup_dev.py
```

---

## **🧪 Testing & Validation**

### **Step 4.1: Test Connection Pooling**

#### **4.1.1 Test Database Health Endpoints**

```bash
# Test database health
curl http://localhost:8000/health/database

# Test pool status
curl http://localhost:8000/health/database/pool

# Test performance metrics
curl http://localhost:8000/health/database/performance
```

#### **4.1.2 Test Connection Pool Efficiency**

```python
# Test script to verify connection pooling
import asyncio
import time
from personal_assistant.config.database import get_db

async def test_connection_pool():
    """Test connection pool efficiency."""
    start_time = time.time()

    # Create multiple concurrent connections
    tasks = []
    for i in range(50):
        task = asyncio.create_task(test_single_connection(i))
        tasks.append(task)

    # Wait for all tasks to complete
    await asyncio.gather(*tasks)

    end_time = time.time()
    print(f"Completed 50 concurrent connections in {end_time - start_time:.2f} seconds")

async def test_single_connection(task_id):
    """Test a single database connection."""
    async with get_db() as db:
        result = await db.execute("SELECT 1 as test")
        await result.fetchone()
        print(f"Task {task_id} completed")

# Run test
asyncio.run(test_connection_pool())
```

### **Step 4.2: Test Docker Configuration**

#### **4.2.1 Build and Run Docker Container**

```bash
# Build image
docker build -f docker/Dockerfile -t personal-assistant:latest .

# Run container
docker run -p 8000:8000 --env-file .env personal-assistant:latest

# Test health endpoint
curl http://localhost:8000/health/database
```

#### **4.2.2 Test Docker Compose**

```bash
# Start all services
cd docker
docker-compose up -d

# Check service status
docker-compose ps

# Test application
curl http://localhost:8000/health/database

# View logs
docker-compose logs app
```

---

## **📊 Performance Validation**

### **Step 5.1: Baseline Performance Measurement**

#### **5.1.1 Measure Current Performance**

```python
import asyncio
import time
from personal_assistant.config.database import get_db

async def measure_performance():
    """Measure current database performance."""
    async with get_db() as db:
        # Test RBAC queries
        start_time = time.time()

        # Test user roles query
        result = await db.execute("""
            SELECT u.email, r.name as role_name
            FROM users u
            JOIN user_roles ur ON u.id = ur.user_id
            JOIN roles r ON ur.role_id = r.id
            LIMIT 100
        """)
        users = await result.fetchall()

        query_time = (time.time() - start_time) * 1000
        print(f"RBAC query completed in {query_time:.2f}ms")
        print(f"Retrieved {len(users)} user-role mappings")

        return query_time

# Run performance test
asyncio.run(measure_performance())
```

### **Step 5.2: Post-Optimization Validation**

#### **5.2.1 Verify Performance Improvements**

```python
async def validate_optimizations():
    """Validate that optimizations improved performance."""
    # Test connection pool efficiency
    pool_stats = await get_pool_stats()
    utilization = (pool_stats['checked_out'] / pool_stats['pool_size']) * 100

    print(f"Connection pool utilization: {utilization:.2f}%")

    # Test query performance
    query_time = await measure_performance()

    # Verify improvements
    assert query_time < 100, f"Query time {query_time}ms exceeds 100ms threshold"
    assert utilization > 80, f"Pool utilization {utilization}% below 80% threshold"

    print("✅ All performance optimizations validated!")
```

---

## **🚀 Deployment Checklist**

### **Pre-Deployment**

- [ ] Connection pooling configured and tested
- [ ] Health check endpoints functional
- [ ] Performance metrics collected
- [ ] Docker containers built and tested
- [ ] Migration system validated

### **Deployment**

- [ ] Database configuration updated
- [ ] Health monitoring active
- [ ] Performance baseline established
- [ ] Containers deployed successfully
- [ ] All endpoints responding correctly

### **Post-Deployment**

- [ ] Performance monitoring active
- [ ] Connection pool efficiency > 80%
- [ ] Query response time < 100ms
- [ ] Health checks passing
- [ ] Documentation updated

---

## **📚 Additional Resources**

### **Connection Pooling Best Practices**

- Start with conservative pool sizes
- Monitor pool utilization and adjust
- Set appropriate timeouts
- Implement connection health checks

### **Performance Optimization Tips**

- Use database indexes effectively
- Monitor slow queries
- Implement query caching where appropriate
- Regular database maintenance

### **Containerization Best Practices**

- Multi-stage builds for smaller images
- Non-root user for security
- Health checks for monitoring
- Environment-specific configurations

---

**This implementation guide provides a comprehensive path to transform your database layer from development-ready to production-ready.** 🚀
