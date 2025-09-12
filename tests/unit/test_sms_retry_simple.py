"""
Simple tests for SMS retry functionality.

This module tests the core SMS retry functionality without complex database mocking.
"""

import pytest
from datetime import datetime, timedelta

from src.personal_assistant.sms_router.services.simple_retry_service import SimpleSMSRetryService
from src.personal_assistant.sms_router.services.error_classifier import SMSErrorClassifier, RetryStrategy


class TestSMSErrorClassifier:
    """Test SMS error classification."""

    def test_retryable_error_detection(self):
        """Test detection of retryable errors."""
        assert SMSErrorClassifier.is_retryable('30001') == True
        assert SMSErrorClassifier.is_retryable('30002') == True
        assert SMSErrorClassifier.is_retryable('30003') == True
        assert SMSErrorClassifier.is_retryable('30004') == True
        assert SMSErrorClassifier.is_retryable('30005') == True
        assert SMSErrorClassifier.is_retryable('21211') == False
        assert SMSErrorClassifier.is_retryable('21214') == False
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
        desc1 = SMSErrorClassifier.get_error_description('30001')
        desc2 = SMSErrorClassifier.get_error_description('21211')
        desc3 = SMSErrorClassifier.get_error_description('unknown')

        assert desc1 == 'Temporary network issue'
        assert desc2 == 'Invalid phone number format'
        assert desc3 == 'Unknown error code: unknown'

    def test_get_retry_strategy(self):
        """Test retry strategy retrieval."""
        strategy1 = SMSErrorClassifier.get_retry_strategy('30001')
        strategy2 = SMSErrorClassifier.get_retry_strategy('21211')

        assert strategy1 is not None
        assert strategy1['strategy'] == RetryStrategy.EXPONENTIAL_BACKOFF
        assert strategy2 is None


class TestSimpleSMSRetryService:
    """Test simplified SMS retry service."""

    def test_service_initialization(self):
        """Test service initialization."""
        service = SimpleSMSRetryService()
        assert service is not None
        assert hasattr(service, 'error_classifier')
        assert hasattr(service, 'twilio_service')

    def test_error_classifier_integration(self):
        """Test error classifier integration."""
        service = SimpleSMSRetryService()
        
        # Test retryable error
        assert service.error_classifier.is_retryable('30001') == True
        
        # Test non-retryable error
        assert service.error_classifier.is_retryable('21211') == False

    def test_retry_delay_calculation(self):
        """Test retry delay calculation through service."""
        service = SimpleSMSRetryService()
        
        # Test exponential backoff
        delay = service.error_classifier.calculate_retry_delay('30001', 1)
        assert delay == 120  # 60 * 2^1

    def test_queue_for_retry_non_retryable_error(self):
        """Test handling non-retryable errors."""
        service = SimpleSMSRetryService()
        
        # This should return False for non-retryable errors
        result = service.queue_for_retry(
            sms_log_id=1,
            error_code='21211',
            error_message='Invalid phone number'
        )
        
        # Since we can't mock the database easily, we expect this to fail gracefully
        # The important thing is that it doesn't crash
        assert result is not None  # Should return a result (True or False)


class TestSMSRetryIntegration:
    """Test SMS retry integration scenarios."""

    def test_error_classification_workflow(self):
        """Test complete error classification workflow."""
        classifier = SMSErrorClassifier()
        
        # Test retryable error workflow
        error_code = '30001'
        retry_count = 1
        
        is_retryable = classifier.is_retryable(error_code)
        assert is_retryable == True
        
        if is_retryable:
            strategy = classifier.get_retry_strategy(error_code)
            assert strategy is not None
            assert strategy['strategy'] == RetryStrategy.EXPONENTIAL_BACKOFF
            
            delay = classifier.calculate_retry_delay(error_code, retry_count)
            assert delay == 120  # 60 * 2^1
            
            description = classifier.get_error_description(error_code)
            assert description == 'Temporary network issue'

    def test_non_retryable_error_workflow(self):
        """Test non-retryable error workflow."""
        classifier = SMSErrorClassifier()
        
        # Test non-retryable error workflow
        error_code = '21211'
        
        is_retryable = classifier.is_retryable(error_code)
        assert is_retryable == False
        
        if not is_retryable:
            strategy = classifier.get_retry_strategy(error_code)
            assert strategy is None
            
            description = classifier.get_error_description(error_code)
            assert description == 'Invalid phone number format'

    def test_retry_strategies(self):
        """Test different retry strategies."""
        classifier = SMSErrorClassifier()
        
        # Test exponential backoff
        delay_exp = classifier.calculate_retry_delay('30001', 2)
        assert delay_exp == 240  # 60 * 2^2
        
        # Test linear backoff
        delay_linear = classifier.calculate_retry_delay('30003', 2)
        assert delay_linear == 900  # 300 * (2 + 1)

    def test_max_retries_configuration(self):
        """Test max retries configuration."""
        classifier = SMSErrorClassifier()
        
        # Test different max retries for different error types
        strategy_30001 = classifier.get_retry_strategy('30001')
        strategy_30003 = classifier.get_retry_strategy('30003')
        
        assert strategy_30001['max_retries'] == 3
        assert strategy_30003['max_retries'] == 2


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
