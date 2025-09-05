"""
Integration tests for SMS Router Service.

These tests verify that all components work together correctly.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from personal_assistant.sms_router.services.routing_engine import SMSRoutingEngine
from personal_assistant.sms_router.services.user_identification import UserIdentificationService
from personal_assistant.sms_router.services.message_processor import MessageProcessor
from personal_assistant.sms_router.services.response_formatter import ResponseFormatter


class TestSMSRouterIntegration:
    """Test SMS Router service integration."""

    @pytest.fixture
    def mock_user_info(self):
        """Mock user information."""
        return {
            'id': 1,
            'email': 'test@example.com',
            'full_name': 'Test User',
            'is_active': True,
            'phone_number': '+15551234567',
            'source': 'primary'
        }

    @pytest.fixture
    def routing_engine(self):
        """Create SMS routing engine instance."""
        return SMSRoutingEngine()

    @pytest.mark.asyncio
    async def test_routing_engine_initialization(self, routing_engine):
        """Test that routing engine initializes correctly."""
        assert routing_engine.user_identification is not None
        assert routing_engine.message_processor is not None
        assert routing_engine.response_formatter is not None
        assert routing_engine.agent_integration is not None

        # Check initial statistics
        assert routing_engine.total_messages_processed == 0
        assert routing_engine.successful_routes == 0
        assert routing_engine.failed_routes == 0
        assert routing_engine.average_processing_time == 0.0

    @pytest.mark.asyncio
    async def test_health_check(self, routing_engine):
        """Test routing engine health check."""
        # Skip this test in CI environment as it requires real database connection
        import os
        if os.getenv('GITHUB_ACTIONS') or os.getenv('CI'):
            pytest.skip("Skipping health check test in CI environment - requires real database connection")
        
        health_status = await routing_engine.health_check()

        assert 'status' in health_status
        assert 'timestamp' in health_status
        assert 'database' in health_status
        assert 'services' in health_status
        assert 'statistics' in health_status

        # Check services status
        services = health_status['services']
        assert 'user_identification' in services
        assert 'message_processor' in services
        assert 'response_formatter' in services
        assert 'agent_integration' in services

    @pytest.mark.asyncio
    async def test_routing_stats(self, routing_engine):
        """Test routing engine statistics."""
        # Skip this test as it requires real database connection
        # This is an integration test that should be run with proper database setup
        pytest.skip("Skipping test that requires real database connection - should be run in integration environment")

    @pytest.mark.asyncio
    async def test_user_identification_service(self):
        """Test user identification service."""
        service = UserIdentificationService()

        # Test with a mock phone number (should return None since no user exists)
        result = await service.identify_user_by_phone("+15551234567")

        # Should return None since no user exists in test database
        # In a real scenario, this would return user info
        assert result is None or isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_message_processor(self):
        """Test message processor service."""
        processor = MessageProcessor()

        user_info = {
            'id': 1,
            'email': 'test@example.com',
            'full_name': 'Test User',
            'is_active': True
        }

        # Test basic message processing
        result = await processor.process_message("Hello world", user_info)

        assert 'processed' in result
        assert 'cleaned_message' in result
        assert 'spam_score' in result
        assert 'command_info' in result

        # Check that message was processed
        assert result['processed'] is True
        assert result['cleaned_message'] == "Hello world"
        assert result['spam_score'] == 0.0

    @pytest.mark.asyncio
    async def test_response_formatter(self):
        """Test response formatter service."""
        formatter = ResponseFormatter()

        user_info = {
            'id': 1,
            'email': 'test@example.com',
            'full_name': 'Test User',
            'is_active': True
        }

        # Test basic response formatting
        response = formatter.format_response(
            "Hello from your assistant!", user_info)

        # Should return a TwiML response
        assert response is not None
        assert hasattr(response, 'to_xml')

        # Test error response formatting
        error_response = formatter.format_error_response(
            "+15551234567", "Test error")
        assert error_response is not None

    @pytest.mark.asyncio
    async def test_end_to_end_sms_processing(self, routing_engine, mock_user_info):
        """Test end-to-end SMS processing (mocked)."""
        # Mock the user identification to return our test user
        routing_engine.user_identification.identify_user_by_phone = AsyncMock(
            return_value=mock_user_info)

        # Mock the agent integration to return a simple response
        routing_engine.agent_integration.process_with_agent = AsyncMock(
            return_value="Hello! I'm your assistant.")

        # Test SMS routing
        response = await routing_engine.route_sms("+15551234567", "Hello", "test_message_sid")

        # Should return a formatted response
        assert response is not None

        # Check that statistics were updated
        assert routing_engine.total_messages_processed == 1
        assert routing_engine.successful_routes == 1
        assert routing_engine.failed_routes == 0
        assert routing_engine.average_processing_time > 0

    @pytest.mark.asyncio
    async def test_error_handling(self, routing_engine):
        """Test error handling in routing engine."""
        # Mock user identification to raise an exception
        routing_engine.user_identification.identify_user_by_phone = AsyncMock(
            side_effect=Exception("Database error"))

        # Test SMS routing with error
        response = await routing_engine.route_sms("+15551234567", "Hello", "test_message_sid")

        # Should return an error response
        assert response is not None

        # Check that error statistics were updated
        assert routing_engine.total_messages_processed == 1
        assert routing_engine.successful_routes == 0
        assert routing_engine.failed_routes == 1

    @pytest.mark.asyncio
    async def test_spam_detection(self, routing_engine, mock_user_info):
        """Test spam detection in routing engine."""
        # Mock user identification
        routing_engine.user_identification.identify_user_by_phone = AsyncMock(
            return_value=mock_user_info)

        # Mock message processor to detect spam
        routing_engine.message_processor.process_message = AsyncMock(return_value={
            'processed': True,
            'cleaned_message': 'FREE MONEY! CLICK NOW!',
            'spam_score': 0.8,
            'is_spam': True,
            'command_info': None
        })

        # Test SMS routing with spam
        response = await routing_engine.route_sms("+15551234567", "FREE MONEY! CLICK NOW!", "test_message_sid")

        # Should return a spam response
        assert response is not None

        # Check that message was processed but marked as spam
        assert routing_engine.total_messages_processed == 1
        assert routing_engine.successful_routes == 0  # Not successful due to spam
        assert routing_engine.failed_routes == 0  # Not failed, just blocked

    @pytest.mark.asyncio
    async def test_command_processing(self, routing_engine, mock_user_info):
        """Test command processing in routing engine."""
        # Mock user identification
        routing_engine.user_identification.identify_user_by_phone = AsyncMock(
            return_value=mock_user_info)

        # Mock message processor to detect command
        routing_engine.message_processor.process_message = AsyncMock(return_value={
            'processed': True,
            'cleaned_message': '/help',
            'spam_score': 0.0,
            'is_spam': False,
            'command_info': {
                'command': 'help',
                'args': '',
                'pattern': '/help'
            }
        })

        # Mock agent integration to handle command
        routing_engine.agent_integration.process_with_agent = AsyncMock(
            return_value="Available commands: /help, /status, /info")

        # Test SMS routing with command
        response = await routing_engine.route_sms("+15551234567", "/help", "test_message_sid")

        # Should return a response
        assert response is not None

        # Check that message was processed successfully
        assert routing_engine.total_messages_processed == 1
        assert routing_engine.successful_routes == 1
        assert routing_engine.failed_routes == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
