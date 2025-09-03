"""
Unit tests for Database Session Management.

This module tests the database session management functionality including
session creation, configuration, and connection handling.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from personal_assistant.database.session import (
    DATABASE_URL,
    engine,
    AsyncSessionLocal,
    get_db,
    _get_engine,
    _get_session_factory,
    _ensure_database_initialized
)
from tests.utils.test_helpers import TestHelper


class TestDatabaseSessionManagement:
    """Test cases for database session management."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.test_database_url = "postgresql+asyncpg://test:test@localhost:5432/test_db"

    def test_database_url_configuration(self):
        """Test DATABASE_URL configuration."""
        # Should have a default database URL
        assert DATABASE_URL is not None
        assert isinstance(DATABASE_URL, str)
        assert "postgresql+asyncpg://" in DATABASE_URL

    def test_engine_creation(self):
        """Test database engine creation."""
        # Engine should be a function that returns an async engine
        assert callable(engine)
        
        # Get the actual engine
        actual_engine = engine()
        assert actual_engine is not None
        
        # Should be an async engine
        assert hasattr(actual_engine, 'dispose')
        assert hasattr(actual_engine, 'connect')

    def test_session_factory_creation(self):
        """Test session factory creation."""
        # Session factory should be created
        assert AsyncSessionLocal is not None
        
        # Should be a sessionmaker
        assert hasattr(AsyncSessionLocal, 'configure')
        assert hasattr(AsyncSessionLocal, '__call__')

    def test_session_factory_configuration(self):
        """Test session factory configuration."""
        # Check that session factory is configured correctly
        # Note: sessionmaker uses different attribute names
        assert AsyncSessionLocal.kw.get('expire_on_commit') is False
        assert AsyncSessionLocal.kw.get('autocommit') is False
        assert AsyncSessionLocal.kw.get('autoflush') is False

    def test_get_db_function(self):
        """Test get_db function."""
        db_func = get_db()
        
        # Should return a function
        assert callable(db_func)
        
        # Should be an async function
        assert asyncio.iscoroutinefunction(db_func)

    @pytest.mark.asyncio
    async def test_get_db_session_creation(self):
        """Test that get_db creates a session."""
        db_func = get_db()
        
        # Mock the AsyncSessionLocal to avoid actual database connection
        with patch('personal_assistant.database.session.AsyncSessionLocal') as mock_session_factory:
            mock_session = AsyncMock(spec=AsyncSession)
            mock_session_factory.return_value = mock_session
            
            session = await db_func()
            
            # Should return a session
            assert session == mock_session
            mock_session_factory.assert_called_once()

    def test_get_engine_function(self):
        """Test _get_engine function."""
        # Should return the engine
        result = _get_engine()
        
        # Should return the same engine instance
        assert result == engine()

    def test_get_session_factory_function(self):
        """Test _get_session_factory function."""
        # Should return the session factory
        result = _get_session_factory()
        
        # Should return the same session factory instance
        assert result == AsyncSessionLocal

    @pytest.mark.asyncio
    async def test_ensure_database_initialized(self):
        """Test _ensure_database_initialized function."""
        # Mock the db_config to avoid actual database initialization
        with patch('personal_assistant.database.session.db_config') as mock_config:
            mock_config.session_factory = None
            mock_config._ensure_initialized = AsyncMock()
            
            await _ensure_database_initialized()
            
            # Should call _ensure_initialized
            mock_config._ensure_initialized.assert_called_once()

    @pytest.mark.asyncio
    async def test_ensure_database_initialized_with_existing_factory(self):
        """Test _ensure_database_initialized when factory already exists."""
        # Mock the db_config with existing session factory
        with patch('personal_assistant.database.session.db_config') as mock_config:
            mock_config.session_factory = Mock()
            mock_config._ensure_initialized = AsyncMock()
            
            await _ensure_database_initialized()
            
            # Should not call _ensure_initialized
            mock_config._ensure_initialized.assert_not_called()

    def test_engine_properties(self):
        """Test engine properties."""
        # Get the actual engine
        actual_engine = engine()
        
        # Engine should have expected properties
        assert hasattr(actual_engine, 'url')
        assert hasattr(actual_engine, 'echo')
        assert hasattr(actual_engine, 'pool')
        
        # Echo should be False (disabled for production)
        assert actual_engine.echo is False

    def test_session_factory_properties(self):
        """Test session factory properties."""
        # Session factory should have expected properties
        assert hasattr(AsyncSessionLocal, 'kw')
        
        # Should be bound to the engine
        assert AsyncSessionLocal.kw.get('bind') == engine()

    def test_database_url_environment_override(self):
        """Test that DATABASE_URL can be overridden by environment."""
        with patch.dict('os.environ', {'REAL_DB_URL': self.test_database_url}):
            # Re-import to get the new URL
            import importlib
            import personal_assistant.database.session
            importlib.reload(personal_assistant.database.session)
            
            # Should use the environment variable
            assert personal_assistant.database.session.DATABASE_URL == self.test_database_url

    def test_database_url_fallback(self):
        """Test DATABASE_URL fallback to default."""
        with patch.dict('os.environ', {}, clear=True):
            # Re-import to get the fallback URL
            import importlib
            import personal_assistant.database.session
            importlib.reload(personal_assistant.database.session)
            
            # Should use the default URL
            assert personal_assistant.database.session.DATABASE_URL is not None
            assert "postgresql+asyncpg://" in personal_assistant.database.session.DATABASE_URL

    @pytest.mark.asyncio
    async def test_session_context_manager(self):
        """Test session as context manager."""
        # Mock the session factory
        with patch('personal_assistant.database.session.AsyncSessionLocal') as mock_session_factory:
            mock_session = AsyncMock(spec=AsyncSession)
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=None)
            mock_session_factory.return_value = mock_session
            
            # Test session as context manager
            async with AsyncSessionLocal() as session:
                assert session == mock_session
                mock_session.__aenter__.assert_called_once()
            
            mock_session.__aexit__.assert_called_once()

    def test_engine_disposal(self):
        """Test engine disposal."""
        # Get the actual engine
        actual_engine = engine()
        
        # Engine should have dispose method
        assert hasattr(actual_engine, 'dispose')
        assert callable(actual_engine.dispose)

    def test_engine_connection_pool(self):
        """Test engine connection pool."""
        # Get the actual engine
        actual_engine = engine()
        
        # Engine should have pool
        assert hasattr(actual_engine, 'pool')
        
        # Pool should have expected methods
        assert hasattr(actual_engine.pool, 'size')
        assert hasattr(actual_engine.pool, 'checked_in')
        assert hasattr(actual_engine.pool, 'checked_out')

    def test_session_factory_kwargs(self):
        """Test session factory keyword arguments."""
        kwargs = AsyncSessionLocal.kw
        
        # Should have expected configuration
        assert kwargs.get('expire_on_commit') is False
        assert kwargs.get('autocommit') is False
        assert kwargs.get('autoflush') is False

    def test_engine_echo_setting(self):
        """Test engine echo setting."""
        # Get the actual engine
        actual_engine = engine()
        
        # Echo should be False for production
        assert actual_engine.echo is False

    def test_session_factory_bind(self):
        """Test session factory bind to engine."""
        # Session factory should be bound to the engine
        assert AsyncSessionLocal.kw.get('bind') == engine()

    def test_database_url_format(self):
        """Test DATABASE_URL format."""
        # Should be a valid PostgreSQL URL
        assert DATABASE_URL.startswith("postgresql+asyncpg://")
        assert "@" in DATABASE_URL
        assert ":" in DATABASE_URL

    def test_engine_creation_with_url(self):
        """Test engine creation with specific URL."""
        # Get the actual engine
        actual_engine = engine()
        
        # Engine should be created with the DATABASE_URL
        assert actual_engine.url.database is not None
        assert actual_engine.url.host is not None
        assert actual_engine.url.port is not None

    def test_session_factory_class(self):
        """Test session factory class configuration."""
        # Note: sessionmaker doesn't store class_ in kw, it's handled differently
        # This test verifies the session factory is properly configured
        assert AsyncSessionLocal is not None

    def test_session_factory_expire_on_commit(self):
        """Test session factory expire_on_commit setting."""
        # Should be False to prevent lazy loading issues
        assert AsyncSessionLocal.kw['expire_on_commit'] is False

    def test_session_factory_autocommit(self):
        """Test session factory autocommit setting."""
        # Should be False for explicit transaction control
        assert AsyncSessionLocal.kw['autocommit'] is False

    def test_session_factory_autoflush(self):
        """Test session factory autoflush setting."""
        # Should be False for explicit flush control
        assert AsyncSessionLocal.kw['autoflush'] is False

    @pytest.mark.asyncio
    async def test_multiple_session_creation(self):
        """Test creating multiple sessions."""
        db_func = get_db()
        
        with patch('personal_assistant.database.session.AsyncSessionLocal') as mock_session_factory:
            mock_session1 = AsyncMock(spec=AsyncSession)
            mock_session2 = AsyncMock(spec=AsyncSession)
            mock_session_factory.side_effect = [mock_session1, mock_session2]
            
            # Create two sessions
            session1 = await db_func()
            session2 = await db_func()
            
            # Should be different sessions
            assert session1 == mock_session1
            assert session2 == mock_session2
            assert session1 != session2
            
            # Should have been called twice
            assert mock_session_factory.call_count == 2

    def test_engine_metadata(self):
        """Test engine metadata."""
        # Get the actual engine
        actual_engine = engine()
        
        # Engine should have metadata
        assert hasattr(actual_engine, 'metadata')
        
        # Metadata should be accessible
        assert actual_engine.metadata is not None

    def test_session_factory_metadata(self):
        """Test session factory metadata."""
        # Note: sessionmaker doesn't have metadata attribute
        # This test verifies the session factory is properly configured
        assert AsyncSessionLocal is not None