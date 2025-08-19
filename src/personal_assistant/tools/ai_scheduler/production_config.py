"""
Production configuration management for the AI-first calendar scheduler system.

This module provides production-ready configuration management
and validation for deployment.
"""

import logging
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class DatabaseConfig:
    """Database configuration."""
    url: str
    pool_size: int = 10
    max_overflow: int = 20
    echo: bool = False


@dataclass
class CeleryConfig:
    """Celery configuration."""
    broker_url: str
    result_backend: str
    task_serializer: str = 'json'
    result_serializer: str = 'json'
    accept_content: List[str] = None
    timezone: str = 'UTC'
    enable_utc: bool = True


@dataclass
class TwilioConfig:
    """Twilio configuration."""
    account_sid: str
    auth_token: str
    phone_number: str


@dataclass
class MonitoringConfig:
    """Monitoring configuration."""
    log_level: str = 'INFO'
    metrics_enabled: bool = True
    alerting_enabled: bool = True
    health_check_interval: int = 300  # 5 minutes


class ProductionConfig:
    """
    Production configuration management.

    This class manages all production configuration settings
    and provides validation and deployment readiness checks.
    """

    def __init__(self):
        self.logger = logger
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration from environment variables.

        Returns:
            Dictionary with configuration
        """
        return {
            'database': {
                'url': os.getenv('DATABASE_URL'),
                'pool_size': int(os.getenv('DB_POOL_SIZE', '10')),
                'max_overflow': int(os.getenv('DB_MAX_OVERFLOW', '20')),
                'echo': os.getenv('DB_ECHO', 'false').lower() == 'true'
            },
            'celery': {
                'broker_url': os.getenv('CELERY_BROKER_URL'),
                'result_backend': os.getenv('CELERY_RESULT_BACKEND'),
                'task_serializer': 'json',
                'result_serializer': 'json',
                'accept_content': ['json'],
                'timezone': 'UTC',
                'enable_utc': True
            },
            'twilio': {
                'account_sid': os.getenv('TWILIO_ACCOUNT_SID'),
                'auth_token': os.getenv('TWILIO_AUTH_TOKEN'),
                'phone_number': os.getenv('TWILIO_PHONE_NUMBER')
            },
            'monitoring': {
                'log_level': os.getenv('LOG_LEVEL', 'INFO'),
                'metrics_enabled': os.getenv('METRICS_ENABLED', 'true').lower() == 'true',
                'alerting_enabled': os.getenv('ALERTING_ENABLED', 'true').lower() == 'true',
                'health_check_interval': int(os.getenv('HEALTH_CHECK_INTERVAL', '300'))
            },
            'scheduler': {
                'event_time_window': int(os.getenv('EVENT_TIME_WINDOW', '2')),
                'use_ai_evaluation': os.getenv('USE_AI_EVALUATION', 'true').lower() == 'true',
                'execute_actions': os.getenv('EXECUTE_ACTIONS', 'true').lower() == 'true'
            }
        }

    def validate_config(self) -> Dict[str, Any]:
        """
        Validate production configuration.

        Returns:
            Dictionary with validation results
        """
        validation_results = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'missing_required': [],
            'missing_optional': []
        }

        # Required configuration keys
        required_keys = [
            ('database', 'url'),
            ('celery', 'broker_url'),
            ('celery', 'result_backend'),
            ('twilio', 'account_sid'),
            ('twilio', 'auth_token'),
            ('twilio', 'phone_number')
        ]

        # Optional configuration keys
        optional_keys = [
            ('database', 'pool_size'),
            ('database', 'max_overflow'),
            ('monitoring', 'log_level'),
            ('monitoring', 'metrics_enabled'),
            ('monitoring', 'alerting_enabled'),
            ('scheduler', 'event_time_window'),
            ('scheduler', 'use_ai_evaluation'),
            ('scheduler', 'execute_actions')
        ]

        # Check required keys
        for section, key in required_keys:
            value = self._get_nested_value(f"{section}.{key}")
            if not value:
                validation_results['missing_required'].append(
                    f"{section}.{key}")
                validation_results['valid'] = False

        # Check optional keys
        for section, key in optional_keys:
            value = self._get_nested_value(f"{section}.{key}")
            if not value:
                validation_results['missing_optional'].append(
                    f"{section}.{key}")

        # Validate specific configurations
        self._validate_database_config(validation_results)
        self._validate_celery_config(validation_results)
        self._validate_twilio_config(validation_results)
        self._validate_monitoring_config(validation_results)

        return validation_results

    def _get_nested_value(self, key_path: str) -> Optional[Any]:
        """
        Get nested configuration value.

        Args:
            key_path: Dot-separated key path (e.g., 'database.url')

        Returns:
            Configuration value or None
        """
        keys = key_path.split('.')
        value = self.config

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None

        return value

    def _validate_database_config(self, validation_results: Dict[str, Any]):
        """Validate database configuration."""
        db_url = self._get_nested_value('database.url')

        if db_url:
            if not db_url.startswith(('postgresql://', 'postgres://', 'mysql://', 'sqlite://')):
                validation_results['warnings'].append(
                    'Database URL format may be invalid')

            pool_size = self._get_nested_value('database.pool_size')
            if pool_size and (pool_size < 1 or pool_size > 50):
                validation_results['warnings'].append(
                    'Database pool size should be between 1 and 50')

    def _validate_celery_config(self, validation_results: Dict[str, Any]):
        """Validate Celery configuration."""
        broker_url = self._get_nested_value('celery.broker_url')

        if broker_url:
            if not broker_url.startswith(('redis://', 'amqp://', 'sqs://')):
                validation_results['warnings'].append(
                    'Celery broker URL format may be invalid')

    def _validate_twilio_config(self, validation_results: Dict[str, Any]):
        """Validate Twilio configuration."""
        account_sid = self._get_nested_value('twilio.account_sid')
        auth_token = self._get_nested_value('twilio.auth_token')
        phone_number = self._get_nested_value('twilio.phone_number')

        if account_sid and not account_sid.startswith('AC'):
            validation_results['warnings'].append(
                'Twilio Account SID format may be invalid')

        if auth_token and len(auth_token) < 30:
            validation_results['warnings'].append(
                'Twilio Auth Token may be invalid')

        if phone_number and not phone_number.startswith('+'):
            validation_results['warnings'].append(
                'Twilio phone number should start with +')

    def _validate_monitoring_config(self, validation_results: Dict[str, Any]):
        """Validate monitoring configuration."""
        log_level = self._get_nested_value('monitoring.log_level')

        if log_level and log_level not in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
            validation_results['warnings'].append(
                'Invalid log level specified')

    def get_database_config(self) -> DatabaseConfig:
        """
        Get database configuration object.

        Returns:
            DatabaseConfig object
        """
        db_config = self.config['database']
        return DatabaseConfig(
            url=db_config['url'],
            pool_size=db_config['pool_size'],
            max_overflow=db_config['max_overflow'],
            echo=db_config['echo']
        )

    def get_celery_config(self) -> CeleryConfig:
        """
        Get Celery configuration object.

        Returns:
            CeleryConfig object
        """
        celery_config = self.config['celery']
        return CeleryConfig(
            broker_url=celery_config['broker_url'],
            result_backend=celery_config['result_backend'],
            task_serializer=celery_config['task_serializer'],
            result_serializer=celery_config['result_serializer'],
            accept_content=celery_config['accept_content'],
            timezone=celery_config['timezone'],
            enable_utc=celery_config['enable_utc']
        )

    def get_twilio_config(self) -> TwilioConfig:
        """
        Get Twilio configuration object.

        Returns:
            TwilioConfig object
        """
        twilio_config = self.config['twilio']
        return TwilioConfig(
            account_sid=twilio_config['account_sid'],
            auth_token=twilio_config['auth_token'],
            phone_number=twilio_config['phone_number']
        )

    def get_monitoring_config(self) -> MonitoringConfig:
        """
        Get monitoring configuration object.

        Returns:
            MonitoringConfig object
        """
        monitoring_config = self.config['monitoring']
        return MonitoringConfig(
            log_level=monitoring_config['log_level'],
            metrics_enabled=monitoring_config['metrics_enabled'],
            alerting_enabled=monitoring_config['alerting_enabled'],
            health_check_interval=monitoring_config['health_check_interval']
        )

    def is_production_ready(self) -> Dict[str, Any]:
        """
        Check if the system is ready for production deployment.

        Returns:
            Dictionary with production readiness status
        """
        validation_results = self.validate_config()

        readiness = {
            'ready': validation_results['valid'],
            'validation_results': validation_results,
            'recommendations': []
        }

        # Add recommendations based on validation results
        if validation_results['missing_required']:
            readiness['recommendations'].append(
                f"Configure required settings: {', '.join(validation_results['missing_required'])}"
            )

        if validation_results['missing_optional']:
            readiness['recommendations'].append(
                f"Consider configuring optional settings: {', '.join(validation_results['missing_optional'])}"
            )

        if validation_results['warnings']:
            readiness['recommendations'].extend(validation_results['warnings'])

        if validation_results['valid']:
            readiness['recommendations'].append(
                'Configuration is valid for production deployment')

        return readiness

    def get_config_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the current configuration.

        Returns:
            Dictionary with configuration summary
        """
        return {
            'database_configured': bool(self._get_nested_value('database.url')),
            'celery_configured': bool(self._get_nested_value('celery.broker_url')),
            'twilio_configured': bool(self._get_nested_value('twilio.account_sid')),
            'monitoring_enabled': self._get_nested_value('monitoring.metrics_enabled'),
            'ai_evaluation_enabled': self._get_nested_value('scheduler.use_ai_evaluation'),
            'action_execution_enabled': self._get_nested_value('scheduler.execute_actions'),
            'log_level': self._get_nested_value('monitoring.log_level'),
            'event_time_window': self._get_nested_value('scheduler.event_time_window')
        }


def create_production_config() -> ProductionConfig:
    """
    Factory function to create a production config instance.

    Returns:
        ProductionConfig instance
    """
    return ProductionConfig()
