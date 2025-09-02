"""
Unit tests for LTMAnalytics class

Tests the analytics and insights functionality for the LTM system.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
from collections import defaultdict

from personal_assistant.memory.ltm_optimization.analytics import LTMAnalytics
from personal_assistant.memory.ltm_optimization.config import EnhancedLTMConfig
from personal_assistant.types.state import AgentState


class TestLTMAnalytics:
    """Test cases for LTMAnalytics class"""

    @pytest.fixture
    def analytics(self):
        """Create a fresh analytics instance for each test"""
        config = EnhancedLTMConfig()
        config.analytics_sampling_rate = 1.0  # 100% sampling for testing
        config.performance_metrics_enabled = True
        analytics = LTMAnalytics(config)

        # Ensure deterministic sampling for tests
        analytics._should_sample_event = lambda: True

        return analytics

    @pytest.fixture
    def sample_memory_data(self):
        """Sample memory data for testing"""
        return {
            'memory_type': 'conversation',
            'category': 'user_preference',
            'importance_score': 7,
            'confidence_score': 0.8,
            'tags': ['preference', 'user'],
            'content': 'User prefers concise responses'
        }

    @pytest.fixture
    def sample_retrieval_data(self):
        """Sample retrieval data for testing"""
        return {
            'query_type': 'semantic_search',
            'retrieval_time': 0.15,
            'result_count': 5,
            'quality_score': 0.85
        }

    @pytest.fixture
    def sample_quality_data(self):
        """Sample quality assessment data for testing"""
        return {
            'memory_id': 123,
            'quality_score': 0.9,
            'assessment_type': 'llm_validation'
        }

    @pytest.fixture
    def sample_pattern_data(self):
        """Sample usage pattern data for testing"""
        return {
            'pattern_type': 'tool_usage',
            'pattern_data': {
                'tool_name': 'calendar',
                'frequency': 5,
                'success_rate': 0.9
            }
        }

    @pytest.fixture
    def sample_integration_data(self):
        """Sample state integration data for testing"""
        return {
            'integration_type': 'state_coordination',
            'success': True,
            'performance_metrics': {
                'response_time': 0.1,
                'memory_count': 3
            }
        }

    def test_init(self, analytics):
        """Test analytics initialization"""
        assert analytics.config is not None
        assert analytics.sampling_rate == 1.0
        assert analytics.performance_metrics_enabled is True
        assert isinstance(analytics.memory_creation_data, defaultdict)
        assert isinstance(analytics.retrieval_performance_data, defaultdict)
        assert isinstance(analytics.quality_metrics_data, defaultdict)
        assert isinstance(analytics.usage_patterns_data, defaultdict)
        assert isinstance(analytics.state_integration_data, defaultdict)

    def test_should_sample_event(self, analytics):
        """Test event sampling logic"""
        # Since we overrode the method in the fixture, it should always return True
        assert analytics._should_sample_event() is True

        # Test the original method by creating a new instance
        config = EnhancedLTMConfig()
        config.analytics_sampling_rate = 0.0
        test_analytics = LTMAnalytics(config)

        # With 0% sampling rate, should return False
        assert test_analytics._should_sample_event() is False

    @pytest.mark.asyncio
    async def test_record_memory_creation_event(self, analytics, sample_memory_data):
        """Test recording memory creation events"""
        user_id = 1

        # Record event
        await analytics.record_memory_creation_event(user_id, sample_memory_data, 0.05)

        # Verify data was recorded
        assert len(analytics.memory_creation_data[user_id]) == 1

        event = analytics.memory_creation_data[user_id][0]
        assert event['user_id'] == user_id
        assert event['memory_type'] == 'conversation'
        assert event['category'] == 'user_preference'
        assert event['importance_score'] == 7
        assert event['confidence_score'] == 0.8
        assert event['creation_time'] == 0.05
        assert event['tags_count'] == 2
        # "User prefers concise responses" is 30 characters
        assert event['content_length'] == 30

    @pytest.mark.asyncio
    async def test_record_retrieval_event(self, analytics, sample_retrieval_data):
        """Test recording retrieval events"""
        user_id = 1

        # Record event
        await analytics.record_retrieval_event(
            user_id,
            'semantic_search',
            0.15,
            5,
            0.85
        )

        # Verify data was recorded
        assert len(analytics.retrieval_performance_data[user_id]) == 1

        event = analytics.retrieval_performance_data[user_id][0]
        assert event['user_id'] == user_id
        assert event['query_type'] == 'semantic_search'
        assert event['retrieval_time'] == 0.15
        assert event['result_count'] == 5
        assert event['quality_score'] == 0.85

    @pytest.mark.asyncio
    async def test_record_quality_assessment(self, analytics, sample_quality_data):
        """Test recording quality assessments"""
        user_id = 1

        # Record event
        await analytics.record_quality_assessment(
            user_id,
            sample_quality_data['memory_id'],
            sample_quality_data['quality_score'],
            sample_quality_data['assessment_type']
        )

        # Verify data was recorded
        assert len(analytics.quality_metrics_data[user_id]) == 1

        event = analytics.quality_metrics_data[user_id][0]
        assert event['user_id'] == user_id
        assert event['memory_id'] == 123
        assert event['quality_score'] == 0.9
        assert event['assessment_type'] == 'llm_validation'

    @pytest.mark.asyncio
    async def test_record_usage_pattern(self, analytics, sample_pattern_data):
        """Test recording usage patterns"""
        user_id = 1

        # Record event
        await analytics.record_usage_pattern(
            user_id,
            sample_pattern_data['pattern_type'],
            sample_pattern_data['pattern_data']
        )

        # Verify data was recorded
        assert len(analytics.usage_patterns_data[user_id]) == 1

        event = analytics.usage_patterns_data[user_id][0]
        assert event['user_id'] == user_id
        assert event['pattern_type'] == 'tool_usage'
        assert event['pattern_data']['tool_name'] == 'calendar'

    @pytest.mark.asyncio
    async def test_record_state_integration_event(self, analytics, sample_integration_data):
        """Test recording state integration events"""
        user_id = 1

        # Record event
        await analytics.record_state_integration_event(
            user_id,
            sample_integration_data['integration_type'],
            sample_integration_data['success'],
            sample_integration_data['performance_metrics']
        )

        # Verify data was recorded
        assert len(analytics.state_integration_data[user_id]) == 1

        event = analytics.state_integration_data[user_id][0]
        assert event['user_id'] == user_id
        assert event['integration_type'] == 'state_coordination'
        assert event['success'] is True
        assert event['performance_metrics']['response_time'] == 0.1

    @pytest.mark.asyncio
    async def test_get_memory_creation_metrics_empty(self, analytics):
        """Test memory creation metrics with no data"""
        metrics = await analytics.get_memory_creation_metrics()

        assert 'timestamp' in metrics
        assert 'overall_metrics' in metrics
        assert 'user_metrics' in metrics
        assert 'trends' in metrics
        assert 'recommendations' in metrics

        overall = metrics['overall_metrics']
        assert overall['total_memories_created'] == 0
        assert overall['memories_by_type'] == {}
        assert overall['memories_by_category'] == {}

    @pytest.mark.asyncio
    async def test_get_memory_creation_metrics_with_data(self, analytics, sample_memory_data):
        """Test memory creation metrics with sample data"""
        user_id = 1

        # Add some sample data
        await analytics.record_memory_creation_event(user_id, sample_memory_data)
        await analytics.record_memory_creation_event(user_id, {
            **sample_memory_data,
            'memory_type': 'fact',
            'importance_score': 5
        })

        # Get metrics
        metrics = await analytics.get_memory_creation_metrics()

        overall = metrics['overall_metrics']
        assert overall['total_memories_created'] == 2
        assert overall['memories_by_type']['conversation'] == 1
        assert overall['memories_by_type']['fact'] == 1
        assert overall['average_importance'] == 6.0
        assert overall['average_confidence'] == 0.8

    @pytest.mark.asyncio
    async def test_get_memory_creation_metrics_user_specific(self, analytics, sample_memory_data):
        """Test user-specific memory creation metrics"""
        user_id = 1

        # Add sample data
        await analytics.record_memory_creation_event(user_id, sample_memory_data)

        # Get user-specific metrics
        metrics = await analytics.get_memory_creation_metrics(user_id)

        user_metrics = metrics['user_metrics']
        assert user_metrics['user_id'] == user_id
        assert user_metrics['total_memories'] == 1
        assert user_metrics['memories_by_type']['conversation'] == 1
        assert user_metrics['average_importance'] == 7.0

    @pytest.mark.asyncio
    async def test_get_retrieval_performance_stats_empty(self, analytics):
        """Test retrieval performance stats with no data"""
        stats = await analytics.get_retrieval_performance_stats()

        assert 'timestamp' in stats
        assert 'overall_performance' in stats
        assert 'user_performance' in stats
        assert 'performance_trends' in stats
        assert 'optimization_opportunities' in stats

        overall = stats['overall_performance']
        assert overall['total_retrievals'] == 0
        assert overall['average_retrieval_time'] == 0.0

    @pytest.mark.asyncio
    async def test_get_retrieval_performance_stats_with_data(self, analytics):
        """Test retrieval performance stats with sample data"""
        user_id = 1

        # Add sample data
        await analytics.record_retrieval_event(user_id, 'semantic_search', 0.1, 3, 0.8)
        await analytics.record_retrieval_event(user_id, 'tag_search', 0.2, 5, 0.9)

        # Get stats
        stats = await analytics.get_retrieval_performance_stats()

        overall = stats['overall_performance']
        assert overall['total_retrievals'] == 2
        assert overall['average_retrieval_time'] == pytest.approx(0.15)
        assert overall['retrieval_by_type']['semantic_search'] == 1
        assert overall['retrieval_by_type']['tag_search'] == 1

    @pytest.mark.asyncio
    async def test_get_quality_assessment_metrics_empty(self, analytics):
        """Test quality assessment metrics with no data"""
        metrics = await analytics.get_quality_assessment_metrics()

        assert 'timestamp' in metrics
        assert 'overall_quality' in metrics
        assert 'user_quality' in metrics
        assert 'quality_trends' in metrics
        assert 'improvement_suggestions' in metrics

        overall = metrics['overall_quality']
        assert overall['total_assessments'] == 0
        assert overall['average_quality_score'] == 0.0

    @pytest.mark.asyncio
    async def test_get_quality_assessment_metrics_with_data(self, analytics):
        """Test quality assessment metrics with sample data"""
        user_id = 1

        # Add sample data
        await analytics.record_quality_assessment(user_id, 1, 0.9, 'llm_validation')
        await analytics.record_quality_assessment(user_id, 2, 0.7, 'human_review')

        # Get metrics
        metrics = await analytics.get_quality_assessment_metrics()

        overall = metrics['overall_quality']
        assert overall['total_assessments'] == 2
        assert overall['average_quality_score'] == 0.8
        assert overall['quality_by_type']['llm_validation']['count'] == 1
        assert overall['quality_by_type']['human_review']['count'] == 1

    @pytest.mark.asyncio
    async def test_get_usage_pattern_insights_empty(self, analytics):
        """Test usage pattern insights with no data"""
        insights = await analytics.get_usage_pattern_insights()

        assert 'timestamp' in insights
        assert 'overall_patterns' in insights
        assert 'user_patterns' in insights
        assert 'pattern_analysis' in insights
        assert 'behavioral_insights' in insights

        overall = insights['overall_patterns']
        assert overall['pattern_categories'] == {}
        assert overall['common_patterns'] == {}

    @pytest.mark.asyncio
    async def test_get_usage_pattern_insights_with_data(self, analytics, sample_pattern_data):
        """Test usage pattern insights with sample data"""
        user_id = 1

        # Add sample data
        await analytics.record_usage_pattern(
            user_id,
            sample_pattern_data['pattern_type'],
            sample_pattern_data['pattern_data']
        )

        # Get insights
        insights = await analytics.get_usage_pattern_insights()

        overall = insights['overall_patterns']
        assert overall['pattern_categories']['tool_usage'] == 1

    @pytest.mark.asyncio
    async def test_get_state_ltm_integration_metrics_empty(self, analytics):
        """Test state-LTM integration metrics with no data"""
        metrics = await analytics.get_state_ltm_integration_metrics()

        assert 'timestamp' in metrics
        assert 'integration_efficiency' in metrics
        assert 'coordination_metrics' in metrics
        assert 'state_ltm_synergy' in metrics
        assert 'optimization_recommendations' in metrics

        efficiency = metrics['integration_efficiency']
        assert efficiency['total_integration_events'] == 0
        assert efficiency['success_rate'] == 0.0

    @pytest.mark.asyncio
    async def test_get_state_ltm_integration_metrics_with_data(self, analytics, sample_integration_data):
        """Test state-LTM integration metrics with sample data"""
        user_id = 1

        # Add sample data
        await analytics.record_state_integration_event(
            user_id,
            sample_integration_data['integration_type'],
            sample_integration_data['success'],
            sample_integration_data['performance_metrics']
        )

        # Get metrics
        metrics = await analytics.get_state_ltm_integration_metrics()

        efficiency = metrics['integration_efficiency']
        assert efficiency['total_integration_events'] == 1
        assert efficiency['success_rate'] == 1.0
        assert efficiency['efficiency_by_type']['state_coordination']['success_rate'] == 1.0

    @pytest.mark.asyncio
    async def test_calculate_percentile(self, analytics):
        """Test percentile calculation"""
        values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

        # median (average of 5 and 6 for 10 elements)
        assert analytics._calculate_percentile(values, 50) == 5.5
        assert analytics._calculate_percentile(values, 90) == 9
        assert analytics._calculate_percentile(values, 95) == 10
        assert analytics._calculate_percentile(values, 100) == 10

        # Test with empty list
        assert analytics._calculate_percentile([], 50) == 0.0

    @pytest.mark.asyncio
    async def test_calculate_active_hours(self, analytics):
        """Test active hours calculation"""
        # Create sample memories with different hours
        memories = [
            {'timestamp': '2024-01-01T09:00:00'},
            {'timestamp': '2024-01-01T14:00:00'},
            {'timestamp': '2024-01-01T09:00:00'},  # Duplicate hour
            {'timestamp': '2024-01-01T16:00:00'},
            {'timestamp': '2024-01-01T14:00:00'},  # Duplicate hour
        ]

        active_hours = analytics._calculate_active_hours(memories)

        # Should return most common hours (9 and 14 appear twice, 16 appears once)
        assert 9 in active_hours
        assert 14 in active_hours
        assert len(active_hours) <= 5  # Max 5 hours returned

    @pytest.mark.asyncio
    async def test_data_storage_limits(self, analytics, sample_memory_data):
        """Test that data storage is limited to prevent memory issues"""
        user_id = 1

        # Test the limit logic step by step
        # Add exactly 1000 events first
        for i in range(1000):
            await analytics.record_memory_creation_event(user_id, sample_memory_data)

        # Should have exactly 1000 events
        assert len(analytics.memory_creation_data[user_id]) == 1000

        # Add one more event to trigger the limit
        await analytics.record_memory_creation_event(user_id, sample_memory_data)

        # Should now be limited to 500 (last 500 elements)
        assert len(analytics.memory_creation_data[user_id]) == 500

        # Latest event should still be there
        latest_event = analytics.memory_creation_data[user_id][-1]
        assert latest_event is not None

    @pytest.mark.asyncio
    async def test_error_handling_in_metrics_calculation(self, analytics):
        """Test error handling in metrics calculation"""
        # Mock a method to raise an exception
        with patch.object(analytics, '_calculate_overall_memory_metrics', side_effect=Exception("Test error")):
            metrics = await analytics.get_memory_creation_metrics()

            # Should return empty dict on error
            assert metrics == {}

    @pytest.mark.asyncio
    async def test_recommendations_generation(self, analytics, sample_memory_data):
        """Test that recommendations are generated based on metrics"""
        user_id = 1

        # Add data that should trigger recommendations
        await analytics.record_memory_creation_event(user_id, {
            **sample_memory_data,
            'importance_score': 2,  # Low importance
            'confidence_score': 0.3  # Low confidence
        })

        metrics = await analytics.get_memory_creation_metrics()

        # Should have recommendations
        assert len(metrics['recommendations']) > 0

        # Check for specific recommendations
        recommendations_text = ' '.join(metrics['recommendations']).lower()
        assert 'importance' in recommendations_text or 'confidence' in recommendations_text

    @pytest.mark.asyncio
    async def test_optimization_opportunities_identification(self, analytics):
        """Test identification of optimization opportunities"""
        user_id = 1

        # Add slow retrieval data
        await analytics.record_retrieval_event(user_id, 'semantic_search', 2.0, 3, 0.5)

        stats = await analytics.get_retrieval_performance_stats()

        # Should identify optimization opportunities
        assert len(stats['optimization_opportunities']) > 0

        opportunities_text = ' '.join(
            stats['optimization_opportunities']).lower()
        assert 'optimizing' in opportunities_text or 'performance' in opportunities_text

    @pytest.mark.asyncio
    async def test_quality_improvement_suggestions(self, analytics):
        """Test quality improvement suggestions generation"""
        user_id = 1

        # Add low quality data
        await analytics.record_quality_assessment(user_id, 1, 0.3, 'llm_validation')

        metrics = await analytics.get_quality_assessment_metrics()

        # Should have improvement suggestions
        assert len(metrics['improvement_suggestions']) > 0

        suggestions_text = ' '.join(metrics['improvement_suggestions']).lower()
        assert 'improve' in suggestions_text or 'quality' in suggestions_text

    @pytest.mark.asyncio
    async def test_integration_optimization_recommendations(self, analytics):
        """Test integration optimization recommendations"""
        user_id = 1

        # Add failed integration data
        await analytics.record_state_integration_event(
            user_id,
            'state_coordination',
            False,  # Failed
            {}
        )

        metrics = await analytics.get_state_ltm_integration_metrics()

        # Should have optimization recommendations
        assert len(metrics['optimization_recommendations']) > 0

        recommendations_text = ' '.join(
            metrics['optimization_recommendations']).lower()
        assert 'optimize' in recommendations_text or 'success rate' in recommendations_text

    @pytest.mark.asyncio
    async def test_behavioral_insights_generation(self, analytics, sample_pattern_data):
        """Test behavioral insights generation"""
        user_id = 1

        # Add pattern data
        await analytics.record_usage_pattern(
            user_id,
            sample_pattern_data['pattern_type'],
            sample_pattern_data['pattern_data']
        )

        insights = await analytics.get_usage_pattern_insights()

        # Should have behavioral insights
        assert len(insights['behavioral_insights']) > 0

        insights_text = ' '.join(insights['behavioral_insights']).lower()
        assert 'pattern' in insights_text or 'usage' in insights_text

    @pytest.mark.asyncio
    async def test_coordination_metrics_calculation(self, analytics):
        """Test coordination metrics calculation"""
        user_id = 1

        # Add coordination events
        await analytics.record_state_integration_event(
            user_id,
            'state_ltm_coordination',
            True,
            {}
        )
        await analytics.record_state_integration_event(
            user_id,
            'memory_coordination',
            False,
            {}
        )

        metrics = await analytics.get_state_ltm_integration_metrics()

        coordination = metrics['coordination_metrics']
        assert coordination['coordination_events'] == 2
        assert coordination['coordination_success_rate'] == 0.5

    @pytest.mark.asyncio
    async def test_multiple_users_data_aggregation(self, analytics, sample_memory_data):
        """Test that data from multiple users is properly aggregated"""
        # Add data for multiple users
        await analytics.record_memory_creation_event(1, sample_memory_data)
        await analytics.record_memory_creation_event(2, sample_memory_data)
        await analytics.record_memory_creation_event(3, sample_memory_data)

        metrics = await analytics.get_memory_creation_metrics()

        # Should aggregate data from all users
        assert metrics['overall_metrics']['total_memories_created'] == 3

        # Individual user data should be separate
        user1_metrics = await analytics.get_memory_creation_metrics(1)
        assert user1_metrics['user_metrics']['total_memories'] == 1

    @pytest.mark.asyncio
    async def test_timestamp_handling(self, analytics, sample_memory_data):
        """Test timestamp handling and recent activity calculations"""
        user_id = 1

        # Mock datetime before recording the event
        with patch('personal_assistant.memory.ltm_optimization.analytics.datetime') as mock_datetime:
            # Create a fixed reference time
            base_time = datetime(2024, 1, 1, 12, 0, 0)
            mock_datetime.now.return_value = base_time
            mock_datetime.fromisoformat = datetime.fromisoformat

            # Add data with mocked timestamp
            await analytics.record_memory_creation_event(user_id, sample_memory_data)

            # Now mock time to be 25 hours later
            mock_datetime.now.return_value = base_time + timedelta(hours=25)

            metrics = await analytics.get_memory_creation_metrics(user_id)
            user_metrics = metrics['user_metrics']

            # Recent activity should show 0 memories in last 24h
            assert user_metrics['recent_activity']['memories_last_24h'] == 0

    @pytest.mark.asyncio
    async def test_config_integration(self, analytics):
        """Test that analytics properly uses configuration settings"""
        # Test with different config values
        config = EnhancedLTMConfig()
        config.analytics_sampling_rate = 0.5
        config.performance_metrics_enabled = False

        new_analytics = LTMAnalytics(config)

        assert new_analytics.sampling_rate == 0.5
        assert new_analytics.performance_metrics_enabled is False

    @pytest.mark.asyncio
    async def test_extract_common_patterns(self, analytics):
        """Test common pattern extraction"""
        pattern_data_list = [
            {'tool': 'calendar', 'frequency': 5},
            {'tool': 'email', 'frequency': 3},
            {'tool': 'calendar', 'frequency': 2}
        ]

        common_patterns = analytics._extract_common_patterns(pattern_data_list)

        assert 'pattern_summary' in common_patterns
        assert 'frequency_analysis' in common_patterns
        assert isinstance(common_patterns, dict)

    @pytest.mark.asyncio
    async def test_error_logging(self, analytics, caplog):
        """Test that errors are properly logged"""
        # Force an error by passing invalid data
        await analytics.record_memory_creation_event(1, None)

        # Should log error
        assert "Error recording memory creation event" in caplog.text

    @pytest.mark.asyncio
    async def test_async_methods_return_types(self, analytics):
        """Test that all async methods return proper types"""
        # Test all main methods return dictionaries
        memory_metrics = await analytics.get_memory_creation_metrics()
        assert isinstance(memory_metrics, dict)

        retrieval_stats = await analytics.get_retrieval_performance_stats()
        assert isinstance(retrieval_stats, dict)

        quality_metrics = await analytics.get_quality_assessment_metrics()
        assert isinstance(quality_metrics, dict)

        usage_insights = await analytics.get_usage_pattern_insights()
        assert isinstance(usage_insights, dict)

        integration_metrics = await analytics.get_state_ltm_integration_metrics()
        assert isinstance(integration_metrics, dict)

    @pytest.mark.asyncio
    async def test_data_persistence_across_calls(self, analytics, sample_memory_data):
        """Test that data persists across multiple method calls"""
        user_id = 1

        # Record data
        await analytics.record_memory_creation_event(user_id, sample_memory_data)

        # Call metrics multiple times
        metrics1 = await analytics.get_memory_creation_metrics()
        metrics2 = await analytics.get_memory_creation_metrics()

        # Data should be consistent
        assert metrics1['overall_metrics']['total_memories_created'] == 1
        assert metrics2['overall_metrics']['total_memories_created'] == 1

        # Same data should be returned
        assert metrics1['overall_metrics'] == metrics2['overall_metrics']
