"""
Test suite for Task 033: Database Migration & Optimization.

This module tests:
- Connection pooling functionality
- Health check endpoints
- Performance optimization features
- Migration management system
- Docker configuration (files created, not runtime tested)

Note: Docker testing is limited to configuration validation.
Actual container runtime testing would require:
- Building Docker images
- Starting containers
- Testing service communication
- Verifying health checks
"""

import pytest
import os
import tempfile
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
from pathlib import Path

# Import the modules we're testing
from personal_assistant.config.database import DatabaseConfig
from personal_assistant.config.monitoring import HealthMonitor, health_monitor
from personal_assistant.config.optimization import DatabaseOptimizer
from personal_assistant.database.migrations.manager import MigrationManager


class TestDatabaseConfig:
    """Test database configuration and connection pooling."""

    @pytest.fixture
    def db_config_instance(self):
        """Create a fresh database config instance for testing."""
        # Mock environment variables
        with patch.dict(os.environ, {
            'DB_POOL_SIZE': '10',
            'DB_MAX_OVERFLOW': '15',
            'DB_POOL_TIMEOUT': '20',
            'DB_POOL_RECYCLE': '1800',
            'DB_POOL_PRE_PING': 'true'
        }):
            return DatabaseConfig()

    def test_database_config_initialization(self, db_config_instance):
        """Test database configuration initialization."""
        assert db_config_instance.pool_size == 10
        assert db_config_instance.max_overflow == 15
        assert db_config_instance.pool_timeout == 20
        assert db_config_instance.pool_recycle == 1800
        assert db_config_instance.pool_pre_ping is True

    def test_environment_variable_defaults(self):
        """Test that environment variables have proper defaults."""
        # Clear environment variables
        with patch.dict(os.environ, {}, clear=True):
            config = DatabaseConfig()
            assert config.pool_size == 20  # Default value
            assert config.max_overflow == 30  # Default value
            assert config.pool_timeout == 30  # Default value

    @pytest.mark.asyncio
    async def test_pool_stats_generation(self, db_config_instance):
        """Test connection pool statistics generation."""
        # Mock the engine pool
        mock_pool = Mock()
        mock_pool.checkedin.return_value = 5
        mock_pool.checkedout.return_value = 3
        mock_pool.overflow.return_value = 1
        mock_pool.invalid.return_value = 0

        # Create a mock engine and set it properly
        mock_engine = Mock()
        mock_engine.pool = mock_pool

        # Set the engine on the db_config_instance
        db_config_instance.engine = mock_engine

        # Ensure the instance thinks it's initialized
        db_config_instance._initialized = True

        pool_stats = await db_config_instance.get_pool_stats()

        assert pool_stats.checked_in == 5
        assert pool_stats.checked_out == 3
        assert pool_stats.overflow == 1
        assert pool_stats.invalid == 0
        assert pool_stats.total_connections == 9
        assert pool_stats.utilization_percentage > 0

    @pytest.mark.asyncio
    async def test_health_check_functionality(self, db_config_instance):
        """Test database health check functionality."""
        # Mock session context
        mock_session = AsyncMock()
        mock_session.execute.return_value = None

        with patch.object(db_config_instance, 'get_session_context') as mock_context:
            mock_context.return_value.__aenter__.return_value = mock_session
            mock_context.return_value.__aexit__.return_value = None

            health_data = await db_config_instance.check_health()

            assert 'status' in health_data
            assert 'response_time' in health_data
            assert 'pool_stats' in health_data
            assert 'performance' in health_data


class TestHealthMonitor:
    """Test health monitoring functionality."""

    @pytest.fixture
    def health_monitor_instance(self):
        """Create a fresh health monitor instance."""
        return HealthMonitor()

    @pytest.mark.asyncio
    async def test_database_health_monitoring(self, health_monitor_instance):
        """Test database health monitoring."""
        # Mock the database config with proper async methods
        mock_db_config = AsyncMock()
        mock_db_config.check_health.return_value = {
            'status': 'healthy',
            'response_time': 0.05,
            'pool_stats': {'utilization_percentage': 75.0},
            'performance': {'slow_query_threshold': 0.1}
        }

        with patch('personal_assistant.config.monitoring.db_config', mock_db_config):
            health_data = await health_monitor_instance.get_database_health()

            assert health_data['status'] == 'healthy'
            assert health_data['service'] == 'database'
            assert 'timestamp' in health_data

    @pytest.mark.asyncio
    async def test_pool_status_monitoring(self, health_monitor_instance):
        """Test connection pool status monitoring."""
        # Mock the database config with proper async methods
        mock_db_config = AsyncMock()
        mock_db_config.get_pool_stats.return_value = Mock(
            pool_size=20,
            max_overflow=30,
            checked_in=15,
            checked_out=5,
            overflow=0,
            invalid=0,
            total_connections=20,
            utilization_percentage=25.0,
            last_updated=datetime.now()
        )

        mock_db_config.get_performance_metrics.return_value = {
            'current_metrics': {'pool_utilization': 25.0},
            'pool_configuration': {'pool_size': 20}
        }

        with patch('personal_assistant.config.monitoring.db_config', mock_db_config):
            pool_data = await health_monitor_instance.get_pool_status()

            assert pool_data['service'] == 'database_pool'
            assert 'pool_statistics' in pool_data
            assert 'performance_metrics' in pool_data

    @pytest.mark.asyncio
    async def test_overall_health_aggregation(self, health_monitor_instance):
        """Test overall health status aggregation."""
        # Mock individual health checks with proper async methods
        mock_db_config = AsyncMock()
        mock_db_config.check_health.return_value = {
            'status': 'healthy', 'response_time': 0.05}
        mock_db_config.get_pool_stats.return_value = Mock(
            pool_size=20,
            max_overflow=30,
            checked_in=15,
            checked_out=5,
            overflow=0,
            invalid=0,
            total_connections=20,
            utilization_percentage=75.0,
            last_updated=datetime.now()
        )
        mock_db_config.get_performance_metrics.return_value = {
            'thresholds': {'slow_query_threshold': 0.1}
        }

        with patch('personal_assistant.config.monitoring.db_config', mock_db_config):
            overall_health = await health_monitor_instance.get_overall_health()

            assert overall_health['status'] == 'healthy'
            assert 'services' in overall_health
            assert 'performance_summary' in overall_health

    def test_health_history_management(self, health_monitor_instance):
        """Test health history management."""
        # Add some test data
        test_health_data = {'status': 'healthy',
                            'timestamp': '2024-01-01T00:00:00'}
        health_monitor_instance._add_to_history(test_health_data)

        assert len(health_monitor_instance.health_history) == 1

        # Test history retrieval - the timestamp is in the past, so it should be filtered out
        # Let's add a recent entry instead
        recent_health_data = {'status': 'healthy',
                              'timestamp': datetime.now().isoformat()}
        health_monitor_instance._add_to_history(recent_health_data)

        history = health_monitor_instance.get_health_history(hours=24)
        assert len(history) == 1  # Only the recent one should be returned


class TestDatabaseOptimizer:
    """Test database optimization functionality."""

    @pytest.fixture
    def optimizer_instance(self):
        """Create a fresh optimizer instance."""
        return DatabaseOptimizer()

    def test_performance_thresholds(self, optimizer_instance):
        """Test performance threshold configuration."""
        assert optimizer_instance.performance_thresholds['slow_query_threshold_ms'] == 100
        assert optimizer_instance.performance_thresholds['table_bloat_threshold'] == 20.0
        assert optimizer_instance.performance_thresholds['index_usage_threshold'] == 10.0
        assert optimizer_instance.performance_thresholds['connection_pool_efficiency'] == 80.0

    @pytest.mark.asyncio
    async def test_table_performance_analysis(self, optimizer_instance):
        """Test table performance analysis."""
        # Mock session and query results
        mock_session = AsyncMock()
        mock_result = Mock()
        mock_result.fetchall.return_value = [
            Mock(
                tablename='test_table',
                live_rows=1000,
                dead_rows=100,
                last_vacuum=datetime.now() - timedelta(days=5),
                last_analyze=datetime.now() - timedelta(days=3)
            )
        ]

        mock_session.execute.return_value = mock_result

        # Mock size query
        mock_size_result = Mock()
        mock_size_result.fetchall.return_value = [
            Mock(
                tablename='test_table',
                size_bytes=1024 * 1024,  # 1MB
                table_size_bytes=512 * 1024,  # 512KB
                index_size_bytes=512 * 1024  # 512KB
            )
        ]

        with patch.object(mock_session, 'execute') as mock_execute:
            mock_execute.side_effect = [mock_result, mock_size_result]

            table_performance = await optimizer_instance.analyze_table_performance(mock_session)

            assert len(table_performance) == 1
            assert table_performance[0].table_name == 'test_table'
            # 100/1000 * 100
            assert table_performance[0].bloat_percentage == 10.0

    @pytest.mark.asyncio
    async def test_index_usage_analysis(self, optimizer_instance):
        """Test index usage analysis."""
        mock_session = AsyncMock()
        mock_result = Mock()
        mock_result.fetchall.return_value = [
            Mock(
                indexname='test_index',
                tablename='test_table',
                scans=100,
                tuples_read=1000,
                tuples_fetched=500,
                size_bytes=1024 * 1024  # 1MB
            )
        ]

        mock_session.execute.return_value = mock_result

        index_usage = await optimizer_instance.analyze_index_usage(mock_session)

        assert len(index_usage) == 1
        assert index_usage[0].index_name == 'test_index'
        assert index_usage[0].table_name == 'test_table'
        assert index_usage[0].usage_percentage > 0

    @pytest.mark.asyncio
    async def test_optimization_recommendations(self, optimizer_instance):
        """Test optimization recommendations generation."""
        # Mock the analysis methods
        with patch.object(optimizer_instance, 'analyze_table_performance') as mock_table_analysis, \
                patch.object(optimizer_instance, 'analyze_index_usage') as mock_index_analysis, \
                patch.object(optimizer_instance, 'analyze_query_performance') as mock_query_analysis:

            mock_table_analysis.return_value = [
                Mock(
                    table_name='test_table',
                    bloat_percentage=25.0,
                    last_vacuum=datetime.now() - timedelta(days=10)
                )
            ]

            mock_index_analysis.return_value = [
                Mock(
                    index_name='test_index',
                    table_name='test_table',
                    efficiency_score=30.0
                )
            ]

            mock_query_analysis.return_value = []

            mock_session = AsyncMock()
            recommendations = await optimizer_instance.get_optimization_recommendations(mock_session)

            assert 'tables' in recommendations
            assert 'indexes' in recommendations
            assert 'queries' in recommendations
            assert 'maintenance' in recommendations
            assert recommendations['priority'] in ['low', 'medium', 'high']


class TestMigrationManager:
    """Test migration management functionality."""

    @pytest.fixture
    def temp_migrations_dir(self):
        """Create a temporary migrations directory for testing."""
        temp_dir = tempfile.mkdtemp()
        migrations_dir = Path(temp_dir) / "migrations"
        migrations_dir.mkdir()

        # Create a test migration file
        test_migration = migrations_dir / "001_test_migration.sql"
        test_migration.write_text("""
        -- DESCRIPTION: Test migration for testing
        -- DEPENDS: 
        
        CREATE TABLE test_table (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100)
        );
        
        -- ROLLBACK:
        DROP TABLE test_table;
        """)

        yield str(migrations_dir)

        # Cleanup
        import shutil
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def migration_manager_instance(self, temp_migrations_dir):
        """Create a migration manager instance with temp directory."""
        return MigrationManager(temp_migrations_dir)

    def test_migration_file_parsing(self, migration_manager_instance, temp_migrations_dir):
        """Test migration file parsing."""
        migrations_dir = Path(temp_migrations_dir)
        migration_file = migrations_dir / "001_test_migration.sql"

        parsed_migration = migration_manager_instance._parse_migration_file(
            migration_file)

        assert parsed_migration is not None
        assert parsed_migration.migration_name == "001_test_migration"
        assert parsed_migration.version == "001"
        assert parsed_migration.description == "Test migration for testing"
        assert parsed_migration.rollback_sql is not None
        assert "DROP TABLE test_table" in parsed_migration.rollback_sql

    def test_checksum_calculation(self, migration_manager_instance):
        """Test checksum calculation."""
        test_content = "CREATE TABLE test (id INT);"
        checksum = migration_manager_instance._calculate_checksum(test_content)

        assert len(checksum) == 64  # SHA-256 hex length
        assert isinstance(checksum, str)

    def test_dependency_extraction(self, migration_manager_instance):
        """Test dependency extraction from migration files."""
        test_content = """
        -- DESCRIPTION: Test migration
        -- DEPENDS: 001_base_migration, 002_user_table
        
        CREATE TABLE test_table (id INT);
        """

        dependencies = migration_manager_instance._extract_dependencies(
            test_content)

        assert "001_base_migration" in dependencies
        assert "002_user_table" in dependencies
        assert len(dependencies) == 2

    def test_description_extraction(self, migration_manager_instance):
        """Test description extraction from migration files."""
        test_content = """
        -- DESCRIPTION: This is a test migration description
        
        CREATE TABLE test_table (id INT);
        """

        description = migration_manager_instance._extract_description(
            test_content)

        assert description == "This is a test migration description"

    def test_sql_statement_extraction(self, migration_manager_instance):
        """Test SQL statement extraction from migration content."""
        test_content = """
        -- This is a comment
        CREATE TABLE test_table (id INT);
        
        -- Another comment
        INSERT INTO test_table VALUES (1);
        """

        statements = migration_manager_instance._extract_sql_statements(
            test_content)

        assert len(statements) == 2
        assert "CREATE TABLE test_table (id INT)" in statements[0]
        assert "INSERT INTO test_table VALUES (1)" in statements[1]

    def test_migration_sorting_by_dependencies(self, migration_manager_instance):
        """Test migration sorting by dependencies."""
        # Create mock migration files
        migration1 = Mock()
        migration1.migration_name = "001_base"
        migration1.dependencies = []

        migration2 = Mock()
        migration2.migration_name = "002_user"
        migration2.dependencies = ["001_base"]

        migration3 = Mock()
        migration3.migration_name = "003_profile"
        migration3.dependencies = ["002_user"]

        migrations = [migration3, migration1, migration2]  # Out of order

        sorted_migrations = migration_manager_instance._sort_migrations_by_dependencies(
            migrations)

        # Should be sorted by dependencies
        assert sorted_migrations[0].migration_name == "001_base"
        assert sorted_migrations[1].migration_name == "002_user"
        assert sorted_migrations[2].migration_name == "003_profile"


class TestIntegration:
    """Integration tests for the complete system."""

    @pytest.mark.asyncio
    async def test_health_endpoint_integration(self):
        """Test that health endpoints work together."""
        # Mock database config with proper async methods
        mock_db_config = AsyncMock()
        mock_db_config.check_health.return_value = {
            'status': 'healthy',
            'response_time': 0.05,
            'pool_stats': {'utilization_percentage': 75.0}
        }

        mock_db_config.get_pool_stats.return_value = Mock(
            pool_size=20,
            max_overflow=30,
            checked_in=15,
            checked_out=5,
            overflow=0,
            invalid=0,
            total_connections=20,
            utilization_percentage=75.0,
            last_updated=datetime.now()
        )

        mock_db_config.get_performance_metrics.return_value = {
            'thresholds': {'slow_query_threshold': 0.1}
        }

        with patch('personal_assistant.config.monitoring.db_config', mock_db_config):
            # Test overall health
            overall_health = await health_monitor.get_overall_health()

            assert overall_health['status'] == 'healthy'
            assert 'services' in overall_health
            assert 'performance_summary' in overall_health

    def test_migration_documentation_generation(self):
        """Test migration documentation generation."""
        # Create a temporary directory for this test
        temp_dir = tempfile.mkdtemp()
        migrations_dir = Path(temp_dir) / "migrations"
        migrations_dir.mkdir()

        try:
            # Create a test migration file
            test_migration = migrations_dir / "001_test_migration.sql"
            test_migration.write_text("""
            -- DESCRIPTION: Test migration for testing
            -- DEPENDS: 
            
            CREATE TABLE test_table (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100)
            );
            
            -- ROLLBACK:
            DROP TABLE test_table;
            """)

            manager = MigrationManager(str(migrations_dir))

            doc_path = manager.generate_migration_documentation()

            assert doc_path != ""
            assert Path(doc_path).exists()

            # Check content
            doc_content = Path(doc_path).read_text()
            assert "Database Migration Documentation" in doc_content
            assert "001_test_migration" in doc_content

        finally:
            # Cleanup
            import shutil
            shutil.rmtree(temp_dir)


# Performance and stress tests
class TestPerformance:
    """Performance and stress tests."""

    @pytest.mark.asyncio
    async def test_connection_pool_efficiency(self):
        """Test connection pool efficiency under load."""
        # This would require a real database connection
        # For now, we'll test the logic
        config = DatabaseConfig()

        # Test pool size configuration
        assert config.pool_size >= 10
        assert config.max_overflow >= 10

        # Test timeout configuration
        assert config.pool_timeout >= 10
        assert config.pool_recycle >= 300

    def test_health_monitoring_performance(self):
        """Test health monitoring performance."""
        monitor = HealthMonitor()

        # Test history management performance
        start_time = datetime.now()

        for i in range(1000):
            monitor._add_to_history(
                {'test': i, 'timestamp': datetime.now().isoformat()})

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # Should complete in reasonable time
        assert duration < 1.0  # Less than 1 second for 1000 operations

        # Test history retrieval performance
        start_time = datetime.now()
        history = monitor.get_health_history(hours=24)
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        assert duration < 0.1  # Less than 100ms for history retrieval


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
