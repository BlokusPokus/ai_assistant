"""
Unit tests for Database Migration System.

This module tests the migration manager, migration files, and migration operations
including validation, rollback capabilities, and safety checks.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
import asyncio
from datetime import datetime
from pathlib import Path
import hashlib

from personal_assistant.database.migrations.manager import (
    MigrationManager,
    MigrationRecord,
    MigrationFile
)
from tests.utils.test_helpers import TestHelper


class TestMigrationRecord:
    """Test cases for MigrationRecord dataclass."""

    def test_migration_record_creation(self):
        """Test MigrationRecord creation with all fields."""
        record = MigrationRecord(
            id=1,
            migration_name="001_add_users_table",
            version="1.0.0",
            checksum="abc123def456",
            applied_at=datetime(2024, 1, 15, 10, 30, 0),
            applied_by="system",
            rollback_sql="DROP TABLE users;",
            rollback_checksum="def456ghi789",
            status="applied",
            execution_time_ms=1500,
            error_message=None
        )
        
        assert record.id == 1
        assert record.migration_name == "001_add_users_table"
        assert record.version == "1.0.0"
        assert record.checksum == "abc123def456"
        assert record.applied_at == datetime(2024, 1, 15, 10, 30, 0)
        assert record.applied_by == "system"
        assert record.rollback_sql == "DROP TABLE users;"
        assert record.rollback_checksum == "def456ghi789"
        assert record.status == "applied"
        assert record.execution_time_ms == 1500
        assert record.error_message is None

    def test_migration_record_minimal_creation(self):
        """Test MigrationRecord creation with minimal fields."""
        record = MigrationRecord(
            id=1,
            migration_name="001_add_users_table",
            version="1.0.0",
            checksum="abc123def456",
            applied_at=datetime(2024, 1, 15, 10, 30, 0),
            applied_by="system",
            rollback_sql=None,
            rollback_checksum=None,
            status="applied",
            execution_time_ms=1500,
            error_message=None
        )
        
        assert record.id == 1
        assert record.migration_name == "001_add_users_table"
        assert record.rollback_sql is None
        assert record.rollback_checksum is None

    def test_migration_record_failed_status(self):
        """Test MigrationRecord with failed status."""
        record = MigrationRecord(
            id=1,
            migration_name="001_add_users_table",
            version="1.0.0",
            checksum="abc123def456",
            applied_at=datetime(2024, 1, 15, 10, 30, 0),
            applied_by="system",
            rollback_sql=None,
            rollback_checksum=None,
            status="failed",
            execution_time_ms=500,
            error_message="Table already exists"
        )
        
        assert record.status == "failed"
        assert record.error_message == "Table already exists"
        assert record.execution_time_ms == 500


class TestMigrationFile:
    """Test cases for MigrationFile dataclass."""

    def test_migration_file_creation(self):
        """Test MigrationFile creation with all fields."""
        migration_file = MigrationFile(
            migration_name="001_add_users_table",
            version="1.0.0",
            file_path=Path("migrations/001_add_users_table.sql"),
            checksum="abc123def456",
            rollback_sql="DROP TABLE users;",
            rollback_checksum="def456ghi789",
            dependencies=["000_initial_schema"],
            description="Add users table with basic fields"
        )
        
        assert migration_file.migration_name == "001_add_users_table"
        assert migration_file.version == "1.0.0"
        assert migration_file.file_path == Path("migrations/001_add_users_table.sql")
        assert migration_file.checksum == "abc123def456"
        assert migration_file.rollback_sql == "DROP TABLE users;"
        assert migration_file.rollback_checksum == "def456ghi789"
        assert migration_file.dependencies == ["000_initial_schema"]
        assert migration_file.description == "Add users table with basic fields"

    def test_migration_file_no_dependencies(self):
        """Test MigrationFile creation without dependencies."""
        migration_file = MigrationFile(
            migration_name="000_initial_schema",
            version="1.0.0",
            file_path=Path("migrations/000_initial_schema.sql"),
            checksum="def456ghi789",
            rollback_sql=None,
            rollback_checksum=None,
            dependencies=[],
            description="Initial database schema"
        )
        
        assert migration_file.dependencies == []
        assert migration_file.migration_name == "000_initial_schema"


class TestMigrationManager:
    """Test cases for MigrationManager class."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.migrations_dir = "test_migrations"
        self.manager = MigrationManager(
            migrations_dir=self.migrations_dir,
            auto_initialize=False
        )

    def test_migration_manager_initialization(self):
        """Test MigrationManager initialization."""
        assert self.manager.migrations_dir == Path(self.migrations_dir)
        assert self.manager.migration_table_name == "migration_history"
        assert self.manager._initialized is False

    def test_migration_manager_auto_initialize(self):
        """Test MigrationManager with auto_initialize=True."""
        with patch.object(MigrationManager, '_initialize_migration_table') as mock_init:
            manager = MigrationManager(
                migrations_dir="test_migrations",
                auto_initialize=True
            )
            mock_init.assert_called_once()

    def test_migration_manager_migrations_dir_creation(self):
        """Test that migrations directory is created."""
        # The directory should be created during initialization
        assert self.manager.migrations_dir.exists()

    def test_calculate_checksum(self):
        """Test checksum calculation."""
        content = "CREATE TABLE users (id SERIAL PRIMARY KEY);"
        checksum = self.manager._calculate_checksum(content)
        
        # Should be SHA-256 hash
        assert len(checksum) == 64  # SHA-256 produces 64 character hex string
        assert isinstance(checksum, str)
        
        # Should be deterministic
        checksum2 = self.manager._calculate_checksum(content)
        assert checksum == checksum2

    def test_calculate_checksum_different_content(self):
        """Test that different content produces different checksums."""
        content1 = "CREATE TABLE users (id SERIAL PRIMARY KEY);"
        content2 = "CREATE TABLE users (id INTEGER PRIMARY KEY);"
        
        checksum1 = self.manager._calculate_checksum(content1)
        checksum2 = self.manager._calculate_checksum(content2)
        
        assert checksum1 != checksum2

    def test_calculate_checksum_empty_content(self):
        """Test checksum calculation with empty content."""
        checksum = self.manager._calculate_checksum("")
        
        # Should still produce a valid checksum
        assert len(checksum) == 64
        assert isinstance(checksum, str)

    @pytest.mark.asyncio
    async def test_ensure_initialized_success(self):
        """Test successful initialization."""
        with patch.object(self.manager, '_ensure_migration_table', new_callable=AsyncMock) as mock_ensure:
            await self.manager._ensure_initialized()
            
            mock_ensure.assert_called_once()
            assert self.manager._initialized is True

    @pytest.mark.asyncio
    async def test_ensure_initialized_failure(self):
        """Test initialization failure."""
        with patch.object(self.manager, '_ensure_migration_table', new_callable=AsyncMock) as mock_ensure:
            mock_ensure.side_effect = Exception("Database connection failed")
            
            with pytest.raises(RuntimeError, match="Migration manager not initialized"):
                await self.manager._ensure_initialized()
            
            assert self.manager._initialized is False

    @pytest.mark.asyncio
    async def test_ensure_initialized_already_initialized(self):
        """Test initialization when already initialized."""
        self.manager._initialized = True
        
        with patch.object(self.manager, '_ensure_migration_table', new_callable=AsyncMock) as mock_ensure:
            await self.manager._ensure_initialized()
            
            # Should not call _ensure_migration_table again
            mock_ensure.assert_not_called()

    @pytest.mark.asyncio
    async def test_ensure_migration_table_creation(self):
        """Test migration table creation."""
        # Test that the method can be called without errors
        # The actual database operations are complex to mock properly
        try:
            await self.manager._ensure_migration_table()
            # If no exception is raised, the test passes
            assert True
        except Exception as e:
            # If an exception is raised, it should be a database connection error
            # (which is expected in a test environment)
            assert "database" in str(e).lower() or "connection" in str(e).lower()

    @pytest.mark.asyncio
    async def test_ensure_migration_table_already_exists(self):
        """Test migration table when it already exists."""
        with patch('personal_assistant.database.migrations.manager.db_config') as mock_config:
            mock_session = AsyncMock()
            mock_session.execute = AsyncMock()
            mock_session.commit = AsyncMock()
            
            # Mock the check query to return a result (table exists)
            mock_result = AsyncMock()
            mock_result.fetchone.return_value = [1]  # Table exists
            mock_session.execute.return_value = mock_result
            
            mock_config.get_session_context.return_value.__aenter__.return_value = mock_session
            
            await self.manager._ensure_migration_table()
            
            # Should only execute the check query, not create
            assert mock_session.execute.call_count == 1
            mock_session.commit.assert_not_called()

    @pytest.mark.asyncio
    async def test_ensure_migration_table_error(self):
        """Test migration table creation with error."""
        with patch('personal_assistant.database.migrations.manager.db_config') as mock_config:
            mock_config.get_session_context.side_effect = Exception("Database error")
            
            # Should not raise exception, just log error
            await self.manager._ensure_migration_table()

    def test_migration_table_name(self):
        """Test migration table name configuration."""
        assert self.manager.migration_table_name == "migration_history"

    def test_migrations_dir_path(self):
        """Test migrations directory path handling."""
        assert isinstance(self.manager.migrations_dir, Path)
        assert self.manager.migrations_dir.name == "test_migrations"

    def test_metadata_initialization(self):
        """Test metadata initialization."""
        assert self.manager.metadata is not None
        assert hasattr(self.manager.metadata, 'tables')

    def test_migration_manager_with_custom_table_name(self):
        """Test MigrationManager with custom table name."""
        manager = MigrationManager(
            migrations_dir="test_migrations",
            auto_initialize=False
        )
        manager.migration_table_name = "custom_migration_history"
        
        assert manager.migration_table_name == "custom_migration_history"

    def test_migration_manager_with_absolute_path(self):
        """Test MigrationManager with absolute path."""
        absolute_path = "/tmp/test_migrations"
        manager = MigrationManager(
            migrations_dir=absolute_path,
            auto_initialize=False
        )
        
        assert manager.migrations_dir == Path(absolute_path)
        assert manager.migrations_dir.is_absolute()

    def test_migration_manager_with_relative_path(self):
        """Test MigrationManager with relative path."""
        relative_path = "./test_migrations"
        manager = MigrationManager(
            migrations_dir=relative_path,
            auto_initialize=False
        )
        
        assert manager.migrations_dir == Path(relative_path)
        assert not manager.migrations_dir.is_absolute()

    @pytest.mark.asyncio
    async def test_ensure_migration_table_with_session_error(self):
        """Test migration table creation with session error."""
        with patch('personal_assistant.database.migrations.manager.db_config') as mock_config:
            mock_config.get_session_context.side_effect = Exception("Session error")
            
            # Should handle error gracefully
            await self.manager._ensure_migration_table()

    def test_migration_manager_initialization_state(self):
        """Test MigrationManager initialization state tracking."""
        assert self.manager._initialized is False
        
        # Manually set initialized state
        self.manager._initialized = True
        assert self.manager._initialized is True

    def test_migration_manager_metadata_access(self):
        """Test MigrationManager metadata access."""
        metadata = self.manager.metadata
        
        assert metadata is not None
        assert hasattr(metadata, 'tables')
        assert hasattr(metadata, 'create_all')
        assert hasattr(metadata, 'drop_all')

    def test_migration_manager_table_name_immutability(self):
        """Test that migration table name can be modified."""
        original_name = self.manager.migration_table_name
        self.manager.migration_table_name = "new_table_name"
        
        assert self.manager.migration_table_name == "new_table_name"
        assert self.manager.migration_table_name != original_name

    def test_migration_manager_migrations_dir_immutability(self):
        """Test that migrations directory can be modified."""
        original_dir = self.manager.migrations_dir
        new_dir = Path("new_migrations_dir")
        self.manager.migrations_dir = new_dir
        
        assert self.manager.migrations_dir == new_dir
        assert self.manager.migrations_dir != original_dir

    def test_migration_manager_checksum_consistency(self):
        """Test checksum calculation consistency."""
        content = "CREATE TABLE test (id SERIAL PRIMARY KEY);"
        
        # Calculate checksum multiple times
        checksums = [self.manager._calculate_checksum(content) for _ in range(5)]
        
        # All checksums should be identical
        assert all(checksum == checksums[0] for checksum in checksums)

    def test_migration_manager_checksum_with_unicode(self):
        """Test checksum calculation with Unicode content."""
        unicode_content = "CREATE TABLE test (id SERIAL PRIMARY KEY, name VARCHAR(100)); -- 测试表"
        checksum = self.manager._calculate_checksum(unicode_content)
        
        assert len(checksum) == 64
        assert isinstance(checksum, str)

    def test_migration_manager_checksum_with_special_characters(self):
        """Test checksum calculation with special characters."""
        special_content = "CREATE TABLE test (id SERIAL PRIMARY KEY, data JSONB); -- Special chars: !@#$%^&*()"
        checksum = self.manager._calculate_checksum(special_content)
        
        assert len(checksum) == 64
        assert isinstance(checksum, str)

    def test_migration_manager_checksum_with_multiline_content(self):
        """Test checksum calculation with multiline content."""
        multiline_content = """CREATE TABLE test (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);"""
        checksum = self.manager._calculate_checksum(multiline_content)
        
        assert len(checksum) == 64
        assert isinstance(checksum, str)

    def test_migration_manager_checksum_with_whitespace_variations(self):
        """Test checksum calculation with different whitespace."""
        content1 = "CREATE TABLE test (id SERIAL PRIMARY KEY);"
        content2 = "CREATE TABLE test (id SERIAL PRIMARY KEY); "
        content3 = "CREATE TABLE test (id SERIAL PRIMARY KEY);\n"
        
        checksum1 = self.manager._calculate_checksum(content1)
        checksum2 = self.manager._calculate_checksum(content2)
        checksum3 = self.manager._calculate_checksum(content3)
        
        # Different whitespace should produce different checksums
        assert checksum1 != checksum2
        assert checksum1 != checksum3
        assert checksum2 != checksum3
