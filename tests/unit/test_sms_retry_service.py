"""
Unit tests for SMS retry service.

This module tests the SMS retry functionality including:
- Error classification
- Retry service methods
- Retry delay calculations
- Database operations
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta

from src.personal_assistant.sms_router.services.simple_retry_service import SimpleSMSRetryService
from src.personal_assistant.sms_router.services.error_classifier import SMSErrorClassifier, RetryStrategy


class TestSMSErrorClassifier:
    """Test SMS error classification."""

    def test_retryable_error_detection(self):
        """Test detection of retryable errors."""
        assert SMSErrorClassifier.is_retryable('30001') == True
        assert SMSErrorClassifier.is_retryable('30002') == True
        assert SMSErrorClassifier.is_retryable('21211') == False
        assert SMSErrorClassifier.is_retryable('unknown') == False

    def test_retry_delay_calculation(self):
        """Test retry delay calculation."""
        # Exponential backoff
        delay1 = SMSErrorClassifier.calculate_retry_delay('30001', 0)
        delay2 = SMSErrorClassifier.calculate_retry_delay('30001', 1)
        delay3 = SMSErrorClassifier.calculate_retry_delay('30001', 2)

        assert delay1 == 60  # base_delay
        assert delay2 == 120  # base_delay * 2^1
        assert delay3 == 240  # base_delay * 2^2

    def test_linear_backoff_calculation(self):
        """Test linear backoff calculation."""
        # Linear backoff for rate limit errors
        delay1 = SMSErrorClassifier.calculate_retry_delay('30003', 0)
        delay2 = SMSErrorClassifier.calculate_retry_delay('30003', 1)

        assert delay1 == 300  # base_delay * (0 + 1)
        assert delay2 == 600  # base_delay * (1 + 1)

    def test_get_error_description(self):
        """Test error description retrieval."""
        retryable_desc = SMSErrorClassifier.get_error_description('30001')
        non_retryable_desc = SMSErrorClassifier.get_error_description('21211')
        unknown_desc = SMSErrorClassifier.get_error_description('99999')

        assert retryable_desc == 'Temporary network issue'
        assert non_retryable_desc == 'Invalid phone number format'
        assert unknown_desc == 'Unknown error code: 99999'


class TestSimpleSMSRetryService:
    """Test SMS retry service."""

    @pytest.fixture
    def retry_service(self):
        """Create retry service instance."""
        return SimpleSMSRetryService()

    @pytest.mark.asyncio
    async def test_queue_for_retry_retryable_error(self, retry_service):
        """Test queuing retryable errors."""
        with patch('src.personal_assistant.sms_router.services.simple_retry_service._get_session_factory') as mock_factory:
            mock_session = AsyncMock()
            mock_factory.return_value.return_value.__aenter__.return_value = mock_session

            # Mock SMS log
            mock_sms_log = MagicMock()
            mock_sms_log.id = 1
            mock_sms_log.sms_metadata = {}
            mock_session.get.return_value = mock_sms_log

            result = await retry_service.queue_for_retry(
                sms_log_id=1,
                error_code='30001',
                error_message='Temporary network issue'
            )

            assert result == True
            mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_queue_for_retry_non_retryable_error(self, retry_service):
        """Test handling non-retryable errors."""
        result = await retry_service.queue_for_retry(
            sms_log_id=1,
            error_code='21211',
            error_message='Invalid phone number'
        )

        assert result == False

    @pytest.mark.asyncio
    async def test_process_retry_queue(self, retry_service):
        """Test processing retry queue."""
        with patch('src.personal_assistant.sms_router.services.simple_retry_service._get_session_factory') as mock_factory:
            mock_session = AsyncMock()
            mock_factory.return_value.return_value.__aenter__.return_value = mock_session

            # Mock retry entries
            mock_retry = MagicMock()
            mock_retry.id = 1
            mock_retry.status = 'pending'
            mock_retry.retry_count = 0
            mock_retry.max_retries = 3
            mock_retry.phone_number = '+1234567890'
            mock_retry.message_content = 'Test message'

            mock_session.execute.return_value.scalars.return_value.all.return_value = [mock_retry]

            # Mock Twilio service
            with patch.object(retry_service.twilio_service, 'send_sms') as mock_send:
                mock_send.return_value = 'test_message_sid'

                stats = await retry_service.process_retry_queue()

                assert 'processed' in stats
                assert 'successful' in stats
                assert 'failed' in stats
                assert stats['processed'] == 1

    @pytest.mark.asyncio
    async def test_handle_delivery_confirmation(self, retry_service):
        """Test handling delivery confirmation."""
        with patch('src.personal_assistant.sms_router.services.simple_retry_service._get_session_factory') as mock_factory:
            mock_session = AsyncMock()
            mock_factory.return_value.return_value.__aenter__.return_value = mock_session

            # Mock SMS log
            mock_sms_log = MagicMock()
            mock_sms_log.id = 1
            mock_session.execute.return_value.scalar_one_or_none.return_value = mock_sms_log

            result = await retry_service.handle_delivery_confirmation(
                'test_message_sid', 'delivered'
            )

            assert result == True
            mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_cleanup_old_retries(self, retry_service):
        """Test cleanup of old retry records."""
        with patch('src.personal_assistant.sms_router.services.simple_retry_service._get_session_factory') as mock_factory:
            mock_session = AsyncMock()
            mock_factory.return_value.return_value.__aenter__.return_value = mock_session

            # Mock old retry records
            mock_old_retry = MagicMock()
            mock_old_retry.next_retry_at = datetime.utcnow() - timedelta(days=8)
            mock_session.execute.return_value.scalars.return_value.all.return_value = [mock_old_retry]

            count = await retry_service.cleanup_old_retries(days_old=7)

            assert count == 1
            mock_session.commit.assert_called_once()


class TestSMSRetryIntegration:
    """Test SMS retry integration scenarios."""

    @pytest.mark.asyncio
    async def test_retry_flow_success(self):
        """Test complete retry flow with successful retry."""
        retry_service = SimpleSMSRetryService()

        with patch('src.personal_assistant.sms_router.services.simple_retry_service._get_session_factory') as mock_factory:
            mock_session = AsyncMock()
            mock_factory.return_value.return_value.__aenter__.return_value = mock_session

            # Mock SMS log for retry
            mock_sms_log = MagicMock()
            mock_sms_log.id = 1
            mock_sms_log.success = False
            mock_sms_log.retry_count = 0
            mock_sms_log.max_retries = 3
            mock_sms_log.next_retry_at = datetime.utcnow()
            mock_sms_log.phone_number = '+1234567890'
            mock_sms_log.message_content = 'Test message'

            mock_session.execute.return_value.scalars.return_value.all.return_value = [mock_sms_log]

            # Mock successful Twilio send
            with patch.object(retry_service.twilio_service, 'send_sms') as mock_send:
                mock_send.return_value = 'success_message_sid'

                stats = await retry_service.process_retry_queue()

                assert stats['processed'] == 1
                assert stats['successful'] == 1
                assert stats['failed'] == 0
                assert mock_sms_log.success == True
                assert mock_sms_log.twilio_message_sid == 'success_message_sid'

    @pytest.mark.asyncio
    async def test_retry_flow_max_retries_reached(self):
        """Test retry flow when max retries are reached."""
        retry_service = SimpleSMSRetryService()

        with patch('src.personal_assistant.sms_router.services.simple_retry_service._get_session_factory') as mock_factory:
            mock_session = AsyncMock()
            mock_factory.return_value.return_value.__aenter__.return_value = mock_session

            # Mock SMS log at max retries
            mock_sms_log = MagicMock()
            mock_sms_log.id = 1
            mock_sms_log.success = False
            mock_sms_log.retry_count = 2
            mock_sms_log.max_retries = 3
            mock_sms_log.next_retry_at = datetime.utcnow()
            mock_sms_log.phone_number = '+1234567890'
            mock_sms_log.message_content = 'Test message'

            mock_session.execute.return_value.scalars.return_value.all.return_value = [mock_sms_log]

            # Mock failed Twilio send
            with patch.object(retry_service.twilio_service, 'send_sms') as mock_send:
                mock_send.side_effect = Exception("Twilio error")

                stats = await retry_service.process_retry_queue()

                assert stats['processed'] == 1
                assert stats['successful'] == 0
                assert stats['failed'] == 1
                assert mock_sms_log.final_status == 'failed'
                assert mock_sms_log.next_retry_at is None
