"""
Database Mock Implementations

This module provides comprehensive mocks for database operations including
SQLAlchemy sessions, transactions, and database models.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
from unittest.mock import AsyncMock, Mock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool


class MockAsyncSession:
    """Mock implementation for AsyncSession."""
    
    def __init__(self):
        self._data = {}
        self._committed = False
        self._rolled_back = False
        self._closed = False
        self._in_transaction = False
        self._query_results = {}
        self._executed_queries = []
    
    async def __aenter__(self):
        """Async context manager entry."""
        self._in_transaction = True
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if exc_type is not None:
            await self.rollback()
        else:
            await self.commit()
        self._in_transaction = False
        self._closed = True
    
    async def add(self, instance):
        """Mock add operation."""
        if hasattr(instance, 'id'):
            instance.id = len(self._data) + 1
        if hasattr(instance, 'created_at'):
            instance.created_at = datetime.now()
        if hasattr(instance, 'updated_at'):
            instance.updated_at = datetime.now()
        
        self._data[id(instance)] = instance
        return instance
    
    async def add_all(self, instances):
        """Mock add_all operation."""
        for instance in instances:
            await self.add(instance)
        return instances
    
    async def delete(self, instance):
        """Mock delete operation."""
        if id(instance) in self._data:
            del self._data[id(instance)]
        return instance
    
    async def commit(self):
        """Mock commit operation."""
        self._committed = True
        self._rolled_back = False
        return True
    
    async def rollback(self):
        """Mock rollback operation."""
        self._rolled_back = True
        self._committed = False
        self._data.clear()
        return True
    
    async def flush(self):
        """Mock flush operation."""
        return True
    
    async def refresh(self, instance):
        """Mock refresh operation."""
        return instance
    
    async def merge(self, instance):
        """Mock merge operation."""
        await self.add(instance)
        return instance
    
    async def execute(self, statement, parameters=None):
        """Mock execute operation."""
        self._executed_queries.append({
            "statement": str(statement),
            "parameters": parameters,
            "timestamp": datetime.now()
        })
        
        # Return mock result
        return MockResult()
    
    async def scalar(self, statement, parameters=None):
        """Mock scalar operation."""
        self._executed_queries.append({
            "statement": str(statement),
            "parameters": parameters,
            "timestamp": datetime.now()
        })
        
        # Return mock scalar result
        return "mock_scalar_result"
    
    async def scalars(self, statement, parameters=None):
        """Mock scalars operation."""
        self._executed_queries.append({
            "statement": str(statement),
            "parameters": parameters,
            "timestamp": datetime.now()
        })
        
        # Return mock scalars result
        return MockScalarsResult()
    
    def query(self, *entities):
        """Mock query operation."""
        return MockQuery(self, entities)
    
    def get(self, entity, ident):
        """Mock get operation."""
        # Return mock entity instance
        if hasattr(entity, '__name__'):
            mock_instance = Mock()
            mock_instance.id = ident
            mock_instance.__class__ = entity
            return mock_instance
        return None
    
    def begin(self):
        """Mock begin operation."""
        return MockTransaction(self)
    
    def begin_nested(self):
        """Mock begin_nested operation."""
        return MockTransaction(self, nested=True)
    
    def close(self):
        """Mock close operation."""
        self._closed = True
        return True
    
    def is_active(self):
        """Check if session is active."""
        return not self._closed and self._in_transaction
    
    def is_committed(self):
        """Check if session is committed."""
        return self._committed
    
    def is_rolled_back(self):
        """Check if session is rolled back."""
        return self._rolled_back
    
    def get_executed_queries(self):
        """Get list of executed queries."""
        return self._executed_queries.copy()
    
    def clear_executed_queries(self):
        """Clear executed queries list."""
        self._executed_queries.clear()


class MockTransaction:
    """Mock implementation for database transactions."""
    
    def __init__(self, session, nested=False):
        self.session = session
        self.nested = nested
        self._committed = False
        self._rolled_back = False
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if exc_type is not None:
            await self.rollback()
        else:
            await self.commit()
    
    async def commit(self):
        """Mock commit operation."""
        self._committed = True
        return True
    
    async def rollback(self):
        """Mock rollback operation."""
        self._rolled_back = True
        return True
    
    def is_active(self):
        """Check if transaction is active."""
        return not self._committed and not self._rolled_back


class MockQuery:
    """Mock implementation for SQLAlchemy queries."""
    
    def __init__(self, session, entities):
        self.session = session
        self.entities = entities
        self._filters = []
        self._order_by = []
        self._limit_value = None
        self._offset_value = None
        self._join_entities = []
        self._mock_results = []
    
    def filter(self, *criterion):
        """Mock filter operation."""
        self._filters.extend(criterion)
        return self
    
    def filter_by(self, **kwargs):
        """Mock filter_by operation."""
        self._filters.append(kwargs)
        return self
    
    def order_by(self, *criterion):
        """Mock order_by operation."""
        self._order_by.extend(criterion)
        return self
    
    def limit(self, limit):
        """Mock limit operation."""
        self._limit_value = limit
        return self
    
    def offset(self, offset):
        """Mock offset operation."""
        self._offset_value = offset
        return self
    
    def join(self, *props, **kwargs):
        """Mock join operation."""
        self._join_entities.extend(props)
        return self
    
    def outerjoin(self, *props, **kwargs):
        """Mock outerjoin operation."""
        self._join_entities.extend(props)
        return self
    
    def group_by(self, *criterion):
        """Mock group_by operation."""
        return self
    
    def having(self, criterion):
        """Mock having operation."""
        return self
    
    def distinct(self):
        """Mock distinct operation."""
        return self
    
    def count(self):
        """Mock count operation."""
        return len(self._mock_results)
    
    def first(self):
        """Mock first operation."""
        return self._mock_results[0] if self._mock_results else None
    
    def one(self):
        """Mock one operation."""
        if len(self._mock_results) == 1:
            return self._mock_results[0]
        elif len(self._mock_results) == 0:
            raise ValueError("No results found")
        else:
            raise ValueError("Multiple results found")
    
    def one_or_none(self):
        """Mock one_or_none operation."""
        if len(self._mock_results) == 1:
            return self._mock_results[0]
        return None
    
    def all(self):
        """Mock all operation."""
        return self._mock_results.copy()
    
    def scalar(self):
        """Mock scalar operation."""
        if self._mock_results:
            return self._mock_results[0]
        return None
    
    def scalars(self):
        """Mock scalars operation."""
        return MockScalarsResult(self._mock_results)
    
    def set_mock_results(self, results):
        """Set mock results for this query."""
        self._mock_results = results
        return self


class MockResult:
    """Mock implementation for query results."""
    
    def __init__(self, rows=None):
        self.rows = rows or []
        self.rowcount = len(self.rows)
    
    def fetchone(self):
        """Mock fetchone operation."""
        return self.rows[0] if self.rows else None
    
    def fetchall(self):
        """Mock fetchall operation."""
        return self.rows.copy()
    
    def fetchmany(self, size=None):
        """Mock fetchmany operation."""
        if size is None:
            size = 1
        return self.rows[:size]
    
    def scalar(self):
        """Mock scalar operation."""
        if self.rows and len(self.rows) > 0:
            return self.rows[0][0] if isinstance(self.rows[0], (list, tuple)) else self.rows[0]
        return None
    
    def scalars(self):
        """Mock scalars operation."""
        return MockScalarsResult(self.rows)


class MockScalarsResult:
    """Mock implementation for scalars results."""
    
    def __init__(self, rows=None):
        self.rows = rows or []
        self.rowcount = len(self.rows)
    
    def all(self):
        """Mock all operation."""
        return self.rows.copy()
    
    def first(self):
        """Mock first operation."""
        return self.rows[0] if self.rows else None
    
    def one(self):
        """Mock one operation."""
        if len(self.rows) == 1:
            return self.rows[0]
        elif len(self.rows) == 0:
            raise ValueError("No results found")
        else:
            raise ValueError("Multiple results found")
    
    def one_or_none(self):
        """Mock one_or_none operation."""
        if len(self.rows) == 1:
            return self.rows[0]
        return None


class MockAsyncSessionLocal:
    """Mock implementation for AsyncSessionLocal."""
    
    def __init__(self):
        self._sessions = []
        self._current_session = None
    
    def __call__(self):
        """Create new session."""
        session = MockAsyncSession()
        self._sessions.append(session)
        self._current_session = session
        return session
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self()
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._current_session:
            await self._current_session.close()
    
    def get_current_session(self):
        """Get current session."""
        return self._current_session
    
    def get_all_sessions(self):
        """Get all created sessions."""
        return self._sessions.copy()
    
    def clear_sessions(self):
        """Clear all sessions."""
        self._sessions.clear()
        self._current_session = None


class MockEngine:
    """Mock implementation for database engine."""
    
    def __init__(self):
        self._connected = True
        self._transactions = []
        self._queries = []
    
    def connect(self):
        """Mock connect operation."""
        return MockConnection()
    
    def begin(self):
        """Mock begin operation."""
        transaction = MockTransaction(None)
        self._transactions.append(transaction)
        return transaction
    
    def execute(self, statement, parameters=None):
        """Mock execute operation."""
        self._queries.append({
            "statement": str(statement),
            "parameters": parameters,
            "timestamp": datetime.now()
        })
        return MockResult()
    
    def scalar(self, statement, parameters=None):
        """Mock scalar operation."""
        self._queries.append({
            "statement": str(statement),
            "parameters": parameters,
            "timestamp": datetime.now()
        })
        return "mock_scalar_result"
    
    def dispose(self):
        """Mock dispose operation."""
        self._connected = False
        return True
    
    def is_connected(self):
        """Check if engine is connected."""
        return self._connected
    
    def get_queries(self):
        """Get executed queries."""
        return self._queries.copy()
    
    def clear_queries(self):
        """Clear executed queries."""
        self._queries.clear()


class MockConnection:
    """Mock implementation for database connection."""
    
    def __init__(self):
        self._closed = False
        self._in_transaction = False
    
    def execute(self, statement, parameters=None):
        """Mock execute operation."""
        return MockResult()
    
    def scalar(self, statement, parameters=None):
        """Mock scalar operation."""
        return "mock_scalar_result"
    
    def begin(self):
        """Mock begin operation."""
        self._in_transaction = True
        return MockTransaction(None)
    
    def commit(self):
        """Mock commit operation."""
        self._in_transaction = False
        return True
    
    def rollback(self):
        """Mock rollback operation."""
        self._in_transaction = False
        return True
    
    def close(self):
        """Mock close operation."""
        self._closed = True
        return True
    
    def is_closed(self):
        """Check if connection is closed."""
        return self._closed
    
    def is_in_transaction(self):
        """Check if connection is in transaction."""
        return self._in_transaction


class DatabaseMockManager:
    """Manager for all database mocks."""
    
    def __init__(self):
        self.async_session_local = MockAsyncSessionLocal()
        self.engine = MockEngine()
        self._sessions = []
        self._transactions = []
    
    def get_async_session(self):
        """Get async session."""
        session = self.async_session_local()
        self._sessions.append(session)
        return session
    
    def get_engine(self):
        """Get database engine."""
        return self.engine
    
    def create_mock_session(self):
        """Create new mock session."""
        session = MockAsyncSession()
        self._sessions.append(session)
        return session
    
    def create_mock_transaction(self, session=None):
        """Create new mock transaction."""
        transaction = MockTransaction(session)
        self._transactions.append(transaction)
        return transaction
    
    def reset_all_mocks(self):
        """Reset all database mocks."""
        self.async_session_local.clear_sessions()
        self.engine.clear_queries()
        self._sessions.clear()
        self._transactions.clear()
    
    def get_mock_statistics(self):
        """Get mock usage statistics."""
        return {
            "sessions_created": len(self._sessions),
            "transactions_created": len(self._transactions),
            "queries_executed": len(self.engine.get_queries()),
            "active_sessions": len([s for s in self._sessions if s.is_active()]),
            "committed_sessions": len([s for s in self._sessions if s.is_committed()]),
            "rolled_back_sessions": len([s for s in self._sessions if s.is_rolled_back()])
        }


# Global database mock manager instance
db_mock_manager = DatabaseMockManager()


def get_async_session_mock():
    """Get async session mock."""
    return db_mock_manager.get_async_session()


def get_engine_mock():
    """Get database engine mock."""
    return db_mock_manager.get_engine()


def get_async_session_local_mock():
    """Get AsyncSessionLocal mock."""
    return db_mock_manager.async_session_local


def reset_all_database_mocks():
    """Reset all database mocks."""
    db_mock_manager.reset_all_mocks()


def get_database_mock_statistics():
    """Get database mock usage statistics."""
    return db_mock_manager.get_mock_statistics()


# Context managers for easy mocking
class MockDatabaseContext:
    """Context manager for database mocking."""
    
    def __init__(self):
        self.original_session_local = None
        self.original_engine = None
    
    def __enter__(self):
        """Enter context."""
        # Store original values
        self.original_session_local = db_mock_manager.async_session_local
        self.original_engine = db_mock_manager.engine
        
        # Reset mocks
        db_mock_manager.reset_all_mocks()
        
        return db_mock_manager
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context."""
        # Restore original values if needed
        pass


def mock_database():
    """Get database mock context manager."""
    return MockDatabaseContext()
