"""
Database migration manager with enhanced safety features.

This module provides:
- Migration tracking and version control
- Rollback capabilities with checksums
- Migration validation and safety checks
- Automated migration application
- Migration documentation generation
"""

import asyncio
import hashlib
import json
import logging
import os
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import MetaData, inspect, text
from sqlalchemy.ext.asyncio import AsyncSession

from personal_assistant.config.database import db_config

logger = logging.getLogger(__name__)


@dataclass
class MigrationRecord:
    """Migration record for tracking applied migrations."""

    id: int
    migration_name: str
    version: str
    checksum: str
    applied_at: datetime
    applied_by: str
    rollback_sql: Optional[str]
    rollback_checksum: Optional[str]
    status: str  # applied, failed, rolled_back
    execution_time_ms: int
    error_message: Optional[str]


@dataclass
class MigrationFile:
    """Migration file information."""

    file_path: Path
    migration_name: str
    version: str
    checksum: str
    rollback_sql: Optional[str]
    rollback_checksum: Optional[str]
    dependencies: List[str]
    description: str


class MigrationManager:
    """Enhanced database migration manager with safety features."""

    def __init__(
        self,
        migrations_dir: str = "src/personal_assistant/database/migrations",
        auto_initialize: bool = False,
    ):
        self.migrations_dir = Path(migrations_dir)
        self.metadata = MetaData()
        self.migration_table_name = "migration_history"
        self._initialized = False

        # Ensure migrations directory exists
        self.migrations_dir.mkdir(parents=True, exist_ok=True)

        # Initialize migration tracking table if requested
        if auto_initialize:
            self._initialize_migration_table()

    def _initialize_migration_table(self):
        """Initialize the migration tracking table."""
        try:
            # Check if we're in an event loop
            try:
                loop = asyncio.get_running_loop()
                # We're in an event loop, create the task
                asyncio.create_task(self._ensure_migration_table())
                self._initialized = True
                logger.info("Migration table initialization started")
            except RuntimeError:
                # No event loop, will initialize when first used
                logger.debug(
                    "No event loop available, migration table will initialize when first used"
                )
                self._initialized = False
        except Exception as e:
            logger.warning(f"Failed to start migration table initialization: {e}")
            self._initialized = False

    async def _ensure_initialized(self):
        """Ensure the migration manager is initialized."""
        if not self._initialized:
            try:
                await self._ensure_migration_table()
                self._initialized = True
            except Exception as e:
                logger.error(f"Failed to initialize migration manager: {e}")
                raise RuntimeError(f"Migration manager not initialized: {e}")

    async def _ensure_migration_table(self):
        """Ensure the migration tracking table exists."""
        try:
            async with db_config.get_session_context() as session:
                # Check if table exists
                check_query = text(
                    """
                    SELECT 1 FROM information_schema.tables 
                    WHERE table_name = :table_name
                """
                )

                result = await session.execute(
                    check_query, {"table_name": self.migration_table_name}
                )

                if not result.fetchone():
                    # Create migration tracking table
                    create_query = text(
                        """
                        CREATE TABLE migration_history (
                            id SERIAL PRIMARY KEY,
                            migration_name VARCHAR(255) NOT NULL,
                            version VARCHAR(50) NOT NULL,
                            checksum VARCHAR(64) NOT NULL,
                            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            applied_by VARCHAR(100) DEFAULT 'system',
                            rollback_sql TEXT,
                            rollback_checksum VARCHAR(64),
                            status VARCHAR(20) DEFAULT 'applied',
                            execution_time_ms INTEGER,
                            error_message TEXT,
                            UNIQUE(migration_name, version)
                        )
                    """
                    )

                    await session.execute(create_query)
                    await session.commit()

                    logger.info("Migration tracking table created successfully")
                else:
                    logger.info("Migration tracking table already exists")

        except Exception as e:
            logger.error(f"Failed to ensure migration table: {e}")

    def _calculate_checksum(self, content: str) -> str:
        """Calculate SHA-256 checksum of content."""
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def _parse_migration_file(self, file_path: Path) -> Optional[MigrationFile]:
        """Parse a migration file and extract metadata."""
        try:
            if not file_path.exists():
                return None

            content = file_path.read_text(encoding="utf-8")

            # Extract migration metadata from SQL comments or filename
            migration_name = file_path.stem
            version = self._extract_version_from_filename(file_path.name)

            # Calculate checksum
            checksum = self._calculate_checksum(content)

            # Try to extract rollback SQL (look for -- ROLLBACK: marker)
            rollback_sql = None
            rollback_checksum = None

            if "-- ROLLBACK:" in content:
                parts = content.split("-- ROLLBACK:")
                if len(parts) > 1:
                    rollback_sql = parts[1].strip()
                    rollback_checksum = self._calculate_checksum(rollback_sql)

            # Extract dependencies from comments
            dependencies = self._extract_dependencies(content)

            # Extract description from comments
            description = self._extract_description(content)

            return MigrationFile(
                file_path=file_path,
                migration_name=migration_name,
                version=version,
                checksum=checksum,
                rollback_sql=rollback_sql,
                rollback_checksum=rollback_checksum,
                dependencies=dependencies,
                description=description,
            )

        except Exception as e:
            logger.error(f"Failed to parse migration file {file_path}: {e}")
            return None

    def _extract_version_from_filename(self, filename: str) -> str:
        """Extract version from migration filename."""
        # Expected format: 001_migration_name.sql or 001_migration_name.py
        parts = filename.split("_", 1)
        if len(parts) > 1 and parts[0].isdigit():
            return parts[0]
        return "unknown"

    def _extract_dependencies(self, content: str) -> List[str]:
        """Extract dependencies from migration file comments."""
        dependencies = []
        lines = content.split("\n")

        for line in lines:
            if line.strip().startswith("-- DEPENDS:"):
                dep_line = line.replace("-- DEPENDS:", "").strip()
                dependencies.extend([d.strip() for d in dep_line.split(",")])

        return dependencies

    def _extract_description(self, content: str) -> str:
        """Extract description from migration file comments."""
        lines = content.split("\n")

        for line in lines:
            if line.strip().startswith("-- DESCRIPTION:"):
                return line.replace("-- DESCRIPTION:", "").strip()

        return "No description provided"

    async def get_pending_migrations(self) -> List[MigrationFile]:
        """Get list of pending migrations that haven't been applied."""
        try:
            await self._ensure_initialized()

            async with db_config.get_session_context() as session:
                # Get applied migrations
                applied_query = text(
                    """
                    SELECT migration_name, version FROM migration_history 
                    WHERE status = 'applied'
                """
                )

                result = await session.execute(applied_query)
                applied_migrations = {
                    (row.migration_name, row.version) for row in result.fetchall()
                }

                # Get all migration files
                migration_files = []
                for file_path in sorted(self.migrations_dir.glob("*.sql")):
                    migration_file = self._parse_migration_file(file_path)
                    if migration_file:
                        # Check if already applied
                        if (
                            migration_file.migration_name,
                            migration_file.version,
                        ) not in applied_migrations:
                            migration_files.append(migration_file)

                # Sort by version and check dependencies
                sorted_migrations = self._sort_migrations_by_dependencies(
                    migration_files
                )

                return sorted_migrations

        except Exception as e:
            logger.error(f"Failed to get pending migrations: {e}")
            return []

    def _sort_migrations_by_dependencies(
        self, migrations: List[MigrationFile]
    ) -> List[MigrationFile]:
        """Sort migrations by dependencies to ensure correct application order."""
        # Simple topological sort for dependencies
        migration_map = {m.migration_name: m for m in migrations}
        sorted_migrations = []
        visited = set()

        def visit(migration: MigrationFile):
            if migration.migration_name in visited:
                return

            # Visit dependencies first
            for dep in migration.dependencies:
                if dep in migration_map:
                    visit(migration_map[dep])

            visited.add(migration.migration_name)
            sorted_migrations.append(migration)

        for migration in migrations:
            visit(migration)

        return sorted_migrations

    async def apply_migration(
        self, migration_file: MigrationFile, user: str = "system"
    ) -> bool:
        """Apply a single migration with safety checks."""
        try:
            await self._ensure_initialized()

            start_time = datetime.now()

            async with db_config.get_session_context() as session:
                # Validate migration hasn't been applied
                check_query = text(
                    """
                    SELECT 1 FROM migration_history 
                    WHERE migration_name = :name AND version = :version
                """
                )

                result = await session.execute(
                    check_query,
                    {
                        "name": migration_file.migration_name,
                        "version": migration_file.version,
                    },
                )

                if result.fetchone():
                    logger.warning(
                        f"Migration {migration_file.migration_name} already applied"
                    )
                    return False

                # Read and validate migration content
                content = migration_file.file_path.read_text(encoding="utf-8")
                current_checksum = self._calculate_checksum(content)

                if current_checksum != migration_file.checksum:
                    logger.error(
                        f"Migration checksum mismatch for {migration_file.migration_name}"
                    )
                    return False

                # Extract SQL statements (remove comments and split by semicolon)
                sql_statements = self._extract_sql_statements(content)

                # Apply migration
                for sql in sql_statements:
                    if sql.strip():
                        await session.execute(text(sql))

                # Record migration
                execution_time = (datetime.now() - start_time).total_seconds() * 1000

                insert_query = text(
                    """
                    INSERT INTO migration_history 
                    (migration_name, version, checksum, applied_by, rollback_sql, rollback_checksum, execution_time_ms)
                    VALUES (:name, :version, :checksum, :user, :rollback_sql, :rollback_checksum, :execution_time)
                """
                )

                await session.execute(
                    insert_query,
                    {
                        "name": migration_file.migration_name,
                        "version": migration_file.version,
                        "checksum": migration_file.checksum,
                        "user": user,
                        "rollback_sql": migration_file.rollback_sql,
                        "rollback_checksum": migration_file.rollback_checksum,
                        "execution_time": int(execution_time),
                    },
                )

                await session.commit()

                logger.info(
                    f"Migration {migration_file.migration_name} applied successfully in {execution_time:.2f}ms"
                )
                return True

        except Exception as e:
            logger.error(
                f"Failed to apply migration {migration_file.migration_name}: {e}"
            )

            # Record failed migration
            try:
                async with db_config.get_session_context() as session:
                    execution_time = (
                        datetime.now() - start_time
                    ).total_seconds() * 1000

                    insert_query = text(
                        """
                        INSERT INTO migration_history 
                        (migration_name, version, checksum, applied_by, execution_time_ms, status, error_message)
                        VALUES (:name, :version, :checksum, :user, :execution_time, 'failed', :error)
                    """
                    )

                    await session.execute(
                        insert_query,
                        {
                            "name": migration_file.migration_name,
                            "version": migration_file.version,
                            "checksum": migration_file.checksum,
                            "user": user,
                            "execution_time": int(execution_time),
                            "error": str(e),
                        },
                    )

                    await session.commit()
            except Exception as record_error:
                logger.error(f"Failed to record failed migration: {record_error}")

            return False

    def _extract_sql_statements(self, content: str) -> List[str]:
        """Extract SQL statements from migration content."""
        # Remove comments
        lines = content.split("\n")
        clean_lines = []

        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith("--"):
                clean_lines.append(line)

        clean_content = "\n".join(clean_lines)

        # Split by semicolon (simple approach)
        statements = [s.strip() for s in clean_content.split(";") if s.strip()]

        return statements

    async def rollback_migration(self, migration_name: str, version: str) -> bool:
        """Rollback a specific migration."""
        try:
            await self._ensure_initialized()

            async with db_config.get_session_context() as session:
                # Get migration record
                get_query = text(
                    """
                    SELECT * FROM migration_history 
                    WHERE migration_name = :name AND version = :version AND status = 'applied'
                """
                )

                result = await session.execute(
                    get_query, {"name": migration_name, "version": version}
                )

                migration_record = result.fetchone()
                if not migration_record:
                    logger.error(f"Migration {migration_name} not found or not applied")
                    return False

                # Check if rollback SQL exists
                if not migration_record.rollback_sql:
                    logger.error(
                        f"No rollback SQL available for migration {migration_name}"
                    )
                    return False

                # Validate rollback checksum
                if migration_record.rollback_checksum:
                    current_rollback_checksum = self._calculate_checksum(
                        migration_record.rollback_sql
                    )
                    if current_rollback_checksum != migration_record.rollback_checksum:
                        logger.error(
                            f"Rollback checksum mismatch for migration {migration_name}"
                        )
                        return False

                # Execute rollback
                await session.execute(text(migration_record.rollback_sql))

                # Update migration status
                update_query = text(
                    """
                    UPDATE migration_history 
                    SET status = 'rolled_back' 
                    WHERE id = :id
                """
                )

                await session.execute(update_query, {"id": migration_record.id})
                await session.commit()

                logger.info(f"Migration {migration_name} rolled back successfully")
                return True

        except Exception as e:
            logger.error(f"Failed to rollback migration {migration_name}: {e}")
            return False

    async def get_migration_status(self) -> Dict[str, Any]:
        """Get comprehensive migration status."""
        try:
            await self._ensure_initialized()

            async with db_config.get_session_context() as session:
                # Get migration statistics
                stats_query = text(
                    """
                    SELECT 
                        status,
                        COUNT(*) as count,
                        AVG(execution_time_ms) as avg_execution_time
                    FROM migration_history 
                    GROUP BY status
                """
                )

                result = await session.execute(stats_query)
                stats = {
                    row.status: {"count": row.count, "avg_time": row.avg_execution_time}
                    for row in result.fetchall()
                }

                # Get recent migrations
                recent_query = text(
                    """
                    SELECT * FROM migration_history 
                    ORDER BY applied_at DESC 
                    LIMIT 10
                """
                )

                result = await session.execute(recent_query)
                recent_migrations = [dict(row._mapping) for row in result.fetchall()]

                # Get pending migrations
                pending_migrations = await self.get_pending_migrations()

                return {
                    "timestamp": datetime.now().isoformat(),
                    "statistics": stats,
                    "recent_migrations": recent_migrations,
                    "pending_migrations": [
                        {
                            "name": m.migration_name,
                            "version": m.version,
                            "description": m.description,
                            "dependencies": m.dependencies,
                        }
                        for m in pending_migrations
                    ],
                    "total_applied": stats.get("applied", {}).get("count", 0),
                    "total_failed": stats.get("failed", {}).get("count", 0),
                    "total_rolled_back": stats.get("rolled_back", {}).get("count", 0),
                }

        except Exception as e:
            logger.error(f"Failed to get migration status: {e}")
            return {"error": str(e)}

    async def apply_all_pending(self, user: str = "system") -> Dict[str, Any]:
        """Apply all pending migrations."""
        try:
            await self._ensure_initialized()

            pending_migrations = await self.get_pending_migrations()

            if not pending_migrations:
                return {
                    "status": "success",
                    "message": "No pending migrations",
                    "applied_count": 0,
                    "failed_count": 0,
                }

            applied_count = 0
            failed_count = 0
            failed_migrations = []

            for migration in pending_migrations:
                logger.info(f"Applying migration: {migration.migration_name}")

                if await self.apply_migration(migration, user):
                    applied_count += 1
                else:
                    failed_count += 1
                    failed_migrations.append(migration.migration_name)

            return {
                "status": "success" if failed_count == 0 else "partial",
                "applied_count": applied_count,
                "failed_count": failed_count,
                "failed_migrations": failed_migrations,
                "total_pending": len(pending_migrations),
            }

        except Exception as e:
            logger.error(f"Failed to apply pending migrations: {e}")
            return {
                "status": "error",
                "error": str(e),
                "applied_count": 0,
                "failed_count": 0,
            }

    def generate_migration_documentation(self) -> str:
        """Generate documentation for all migrations."""
        try:
            migration_files = []

            for file_path in sorted(self.migrations_dir.glob("*.sql")):
                migration_file = self._parse_migration_file(file_path)
                if migration_file:
                    migration_files.append(migration_file)

            # Generate markdown documentation
            doc = "# Database Migration Documentation\n\n"
            doc += f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            doc += f"Total migrations: {len(migration_files)}\n\n"

            for migration in migration_files:
                doc += f"## {migration.migration_name} (v{migration.version})\n\n"
                doc += f"**Description:** {migration.description}\n\n"

                if migration.dependencies:
                    doc += f"**Dependencies:** {', '.join(migration.dependencies)}\n\n"

                doc += f"**File:** {migration.file_path.name}\n\n"
                doc += f"**Checksum:** {migration.checksum}\n\n"

                if migration.rollback_sql:
                    doc += "**Rollback Available:** Yes\n\n"
                else:
                    doc += "**Rollback Available:** No\n\n"

                doc += "---\n\n"

            # Write documentation
            doc_path = self.migrations_dir / "MIGRATION_DOCUMENTATION.md"
            doc_path.write_text(doc, encoding="utf-8")

            logger.info(f"Migration documentation generated: {doc_path}")
            return str(doc_path)

        except Exception as e:
            logger.error(f"Failed to generate migration documentation: {e}")
            return ""


# Global migration manager instance - don't auto-initialize to avoid import issues
migration_manager = MigrationManager(auto_initialize=False)
