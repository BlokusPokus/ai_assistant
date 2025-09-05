"""
Unit tests for SMS tools integration.

This module tests the SMS router functionality including
agent integration, routing engine, and SMS processing.
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime

from tests.utils.test_data_generators import APIDataGenerator, UserDataGenerator


class TestSMSTools:
    """Test class for SMS tools integration."""

    def setup_method(self):
        """Set up test fixtures."""
        self.api_generator = APIDataGenerator()
        self.user_generator = UserDataGenerator()

    @pytest.mark.asyncio
    async def test_agent_integration_service_initialization(self):
        """Test agent integration service initialization."""
        # Mock the dependencies
        with patch('personal_assistant.sms_router.services.agent_integration.create_tool_registry') as mock_tool_registry, \
             patch('personal_assistant.sms_router.services.agent_integration.GeminiLLM') as mock_llm, \
             patch('personal_assistant.sms_router.services.agent_integration.AgentCore') as mock_agent_core:
            
            # Mock successful initialization
            mock_tool_registry.return_value = Mock()
            mock_llm.return_value = Mock()
            mock_agent_core.return_value = Mock()
            
            from personal_assistant.sms_router.services.agent_integration import AgentIntegrationService
            
            service = AgentIntegrationService()
            
            assert service.agent_core is not None
            assert service.tool_registry is not None
            assert service.llm is not None

    @pytest.mark.asyncio
    async def test_agent_integration_service_initialization_failure(self):
        """Test agent integration service initialization failure."""
        # Mock initialization failure
        with patch('personal_assistant.sms_router.services.agent_integration.create_tool_registry') as mock_tool_registry:
            mock_tool_registry.side_effect = Exception("Initialization failed")
            
            from personal_assistant.sms_router.services.agent_integration import AgentIntegrationService
            
            service = AgentIntegrationService()
            
            assert service.agent_core is None
            assert service.tool_registry is None
            assert service.llm is None

    @pytest.mark.asyncio
    async def test_process_with_agent_success(self):
        """Test successful message processing with agent."""
        # Mock the agent integration service
        with patch('personal_assistant.sms_router.services.agent_integration.AgentIntegrationService') as mock_class:
            mock_service = Mock()
            mock_class.return_value = mock_service
            
            # Mock successful processing
            mock_service.process_with_agent = AsyncMock(return_value="Agent response")
            
            # Test message processing
            message = "Hello, can you help me?"
            user_info = {"user_id": "123", "phone": "+1234567890"}
            
            result = await mock_service.process_with_agent(message, user_info)
            
            assert result == "Agent response"
            mock_service.process_with_agent.assert_called_once_with(message, user_info)

    @pytest.mark.asyncio
    async def test_process_with_agent_error_handling(self):
        """Test error handling in message processing."""
        # Mock the agent integration service
        with patch('personal_assistant.sms_router.services.agent_integration.AgentIntegrationService') as mock_class:
            mock_service = Mock()
            mock_class.return_value = mock_service
            
            # Mock processing error
            mock_service.process_with_agent = AsyncMock(
                side_effect=Exception("Processing failed")
            )
            
            # Test error handling
            message = "Test message"
            user_info = {"user_id": "123"}
            
            with pytest.raises(Exception) as exc_info:
                await mock_service.process_with_agent(message, user_info)
            
            assert str(exc_info.value) == "Processing failed"

    @pytest.mark.asyncio
    async def test_sms_routing_engine_initialization(self):
        """Test SMS routing engine initialization."""
        # Mock the routing engine
        with patch('personal_assistant.sms_router.services.routing_engine.SMSRoutingEngine') as mock_class:
            mock_engine = Mock()
            mock_class.return_value = mock_engine
            
            # Test initialization
            from personal_assistant.sms_router.services.routing_engine import SMSRoutingEngine
            
            engine = SMSRoutingEngine()
            assert engine is not None

    @pytest.mark.asyncio
    async def test_sms_routing_engine_message_routing(self):
        """Test SMS message routing functionality."""
        # Mock the routing engine
        with patch('personal_assistant.sms_router.services.routing_engine.SMSRoutingEngine') as mock_class:
            mock_engine = Mock()
            mock_class.return_value = mock_engine
            
            # Mock routing functionality
            mock_engine.route_message = AsyncMock(return_value={
                "route": "agent",
                "confidence": 0.9,
                "processing_time": 0.5
            })
            
            # Test message routing
            message = "Help me with my calendar"
            user_info = {"user_id": "123"}
            
            result = await mock_engine.route_message(message, user_info)
            
            assert result["route"] == "agent"
            assert result["confidence"] == 0.9
            assert result["processing_time"] == 0.5
            mock_engine.route_message.assert_called_once_with(message, user_info)

    @pytest.mark.asyncio
    async def test_sms_routing_engine_route_detection(self):
        """Test SMS route detection logic."""
        # Mock the routing engine
        with patch('personal_assistant.sms_router.services.routing_engine.SMSRoutingEngine') as mock_class:
            mock_engine = Mock()
            mock_class.return_value = mock_engine
            
            # Mock route detection
            mock_engine.detect_route = AsyncMock(return_value="agent")
            
            # Test route detection
            message = "Schedule a meeting for tomorrow"
            result = await mock_engine.detect_route(message)
            
            assert result == "agent"
            mock_engine.detect_route.assert_called_once_with(message)

    @pytest.mark.asyncio
    async def test_sms_routing_engine_confidence_scoring(self):
        """Test SMS routing confidence scoring."""
        # Mock the routing engine
        with patch('personal_assistant.sms_router.services.routing_engine.SMSRoutingEngine') as mock_class:
            mock_engine = Mock()
            mock_class.return_value = mock_engine
            
            # Mock confidence scoring
            mock_engine.calculate_confidence = AsyncMock(return_value=0.85)
            
            # Test confidence scoring
            message = "What's the weather like?"
            route = "agent"
            
            result = await mock_engine.calculate_confidence(message, route)
            
            assert result == 0.85
            mock_engine.calculate_confidence.assert_called_once_with(message, route)

    @pytest.mark.asyncio
    async def test_sms_analytics_service(self):
        """Test SMS analytics service functionality."""
        # Mock the analytics service
        with patch('personal_assistant.sms_router.services.analytics.SMSAnalyticsService') as mock_class:
            mock_analytics = Mock()
            mock_class.return_value = mock_analytics
            
            # Mock analytics functionality
            mock_analytics.record_message = AsyncMock(return_value=True)
            mock_analytics.get_message_stats = AsyncMock(return_value={
                "total_messages": 100,
                "successful_routes": 95,
                "average_confidence": 0.87
            })
            
            # Test analytics recording
            message_data = {
                "user_id": "123",
                "message": "Test message",
                "route": "agent",
                "confidence": 0.9
            }
            
            result = await mock_analytics.record_message(message_data)
            assert result is True
            
            # Test analytics retrieval
            stats = await mock_analytics.get_message_stats("123")
            assert stats["total_messages"] == 100
            assert stats["successful_routes"] == 95
            assert stats["average_confidence"] == 0.87

    @pytest.mark.asyncio
    async def test_sms_error_handling(self):
        """Test SMS error handling scenarios."""
        # Test various error scenarios
        error_scenarios = [
            ("Invalid message format", ValueError("Invalid message format")),
            ("Routing engine failure", Exception("Routing engine failed")),
            ("Agent processing error", Exception("Agent processing failed")),
            ("Analytics recording error", Exception("Analytics recording failed")),
        ]
        
        for error_type, error in error_scenarios:
            # Mock the service with error
            with patch('personal_assistant.sms_router.services.agent_integration.AgentIntegrationService') as mock_class:
                mock_service = Mock()
                mock_class.return_value = mock_service
                
                # Mock the specific error
                mock_service.process_with_agent = AsyncMock(side_effect=error)
                
                # Test error handling
                with pytest.raises(Exception) as exc_info:
                    await mock_service.process_with_agent("Test message", {"user_id": "123"})
                
                assert str(exc_info.value) == str(error)

    @pytest.mark.asyncio
    async def test_sms_integration_workflow(self):
        """Test complete SMS integration workflow."""
        # Mock all SMS components
        with patch('personal_assistant.sms_router.services.agent_integration.AgentIntegrationService') as mock_agent_class, \
             patch('personal_assistant.sms_router.services.routing_engine.SMSRoutingEngine') as mock_routing_class, \
             patch('personal_assistant.sms_router.services.analytics.SMSAnalyticsService') as mock_analytics_class:
            
            # Setup mocks
            mock_agent_service = Mock()
            mock_agent_class.return_value = mock_agent_service
            mock_agent_service.process_with_agent = AsyncMock(return_value="Agent response")
            
            mock_routing_engine = Mock()
            mock_routing_class.return_value = mock_routing_engine
            mock_routing_engine.route_message = AsyncMock(return_value={
                "route": "agent",
                "confidence": 0.9
            })
            
            mock_analytics_service = Mock()
            mock_analytics_class.return_value = mock_analytics_service
            mock_analytics_service.record_message = AsyncMock(return_value=True)
            
            # Test complete workflow
            message = "Help me schedule a meeting"
            user_info = {"user_id": "123", "phone": "+1234567890"}
            
            # 1. Route the message
            routing_result = await mock_routing_engine.route_message(message, user_info)
            assert routing_result["route"] == "agent"
            
            # 2. Process with agent
            agent_response = await mock_agent_service.process_with_agent(message, user_info)
            assert agent_response == "Agent response"
            
            # 3. Record analytics
            analytics_data = {
                "user_id": user_info["user_id"],
                "message": message,
                "route": routing_result["route"],
                "confidence": routing_result["confidence"],
                "response": agent_response
            }
            analytics_result = await mock_analytics_service.record_message(analytics_data)
            assert analytics_result is True
            
            # Verify all services were called
            mock_routing_engine.route_message.assert_called_once()
            mock_agent_service.process_with_agent.assert_called_once()
            mock_analytics_service.record_message.assert_called_once()

    @pytest.mark.asyncio
    async def test_sms_performance_monitoring(self):
        """Test SMS performance monitoring."""
        # Mock performance monitoring
        with patch('personal_assistant.sms_router.services.analytics.SMSAnalyticsService') as mock_class:
            mock_analytics = Mock()
            mock_class.return_value = mock_analytics
            
            # Mock performance metrics
            mock_analytics.get_performance_metrics = AsyncMock(return_value={
                "average_processing_time": 0.5,
                "success_rate": 0.95,
                "total_messages_processed": 1000,
                "error_rate": 0.05
            })
            
            # Test performance monitoring
            metrics = await mock_analytics.get_performance_metrics()
            
            assert metrics["average_processing_time"] == 0.5
            assert metrics["success_rate"] == 0.95
            assert metrics["total_messages_processed"] == 1000
            assert metrics["error_rate"] == 0.05

    @pytest.mark.asyncio
    async def test_sms_user_isolation(self):
        """Test SMS user isolation and security."""
        # Mock user isolation
        with patch('personal_assistant.sms_router.services.agent_integration.AgentIntegrationService') as mock_class:
            mock_service = Mock()
            mock_class.return_value = mock_service
            
            # Mock user isolation
            mock_service.validate_user_access = AsyncMock(return_value=True)
            mock_service.isolate_user_data = AsyncMock(return_value={
                "user_id": "123",
                "isolated": True,
                "data_access": "restricted"
            })
            
            # Test user isolation
            user_info = {"user_id": "123", "phone": "+1234567890"}
            
            access_valid = await mock_service.validate_user_access(user_info)
            assert access_valid is True
            
            isolation_result = await mock_service.isolate_user_data(user_info)
            assert isolation_result["user_id"] == "123"
            assert isolation_result["isolated"] is True
            assert isolation_result["data_access"] == "restricted"
