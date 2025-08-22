# """
# Health monitoring for the AI-first calendar scheduler system.

# This module provides comprehensive health monitoring capabilities
# for database, Celery, and Twilio services.
# """

# import logging
# import os
# import time
# from datetime import datetime
# from typing import Any, Dict, Optional

# logger = logging.getLogger(__name__)


# class HealthMonitor:
#     """
#     Monitor system health and performance.

#     This class provides comprehensive health checks for all system
#     components including database, Celery, and external services.
#     """

#     def __init__(self):
#         self.logger = logger
#         self.health_checks = []
#         self.last_check_time = None

#     async def check_system_health(self) -> Dict[str, Any]:
#         """
#         Perform comprehensive health checks.

#         Returns:
#             Dictionary with health status for all components
#         """
#         start_time = time.time()

#         self.logger.info("Starting comprehensive system health check")

#         # Perform all health checks
#         health_status = {
#             'database': await self._check_database_health(),
#             'celery': await self._check_celery_health(),
#             'twilio': await self._check_twilio_health(),
#             'overall': 'healthy',
#             'check_time': datetime.utcnow().isoformat(),
#             'response_time': 0
#         }

#         # Calculate response time
#         health_status['response_time'] = time.time() - start_time

#         # Determine overall health
#         unhealthy_components = []
#         for component, status in health_status.items():
#             if component in ['database', 'celery', 'twilio'] and isinstance(status, dict):
#                 if status.get('status') != 'healthy':
#                     unhealthy_components.append(component)

#         if unhealthy_components:
#             health_status['overall'] = 'unhealthy'
#             health_status['unhealthy_components'] = unhealthy_components
#             self.logger.warning(
#                 f"System health check found unhealthy components: {unhealthy_components}")
#         else:
#             self.logger.info("All system components are healthy")

#         self.last_check_time = datetime.utcnow()

#         return health_status

#     async def _check_database_health(self) -> Dict[str, Any]:
#         """
#         Check database connectivity and performance.

#         Returns:
#             Dictionary with database health status
#         """
#         try:
#             start_time = time.time()

#             # Import database components
#             from sqlalchemy import text

#             from .db_queries import AsyncSessionLocal

#             # Perform simple database query
#             async with AsyncSessionLocal() as session:
#                 result = await session.execute(text("SELECT 1"))
#                 await session.commit()

#             response_time = time.time() - start_time

#             # Check response time
#             if response_time > 5:  # More than 5 seconds
#                 return {
#                     'status': 'degraded',
#                     'response_time': response_time,
#                     'message': 'Database connection slow',
#                     'warning': 'Response time exceeds 5 seconds'
#                 }

#             return {
#                 'status': 'healthy',
#                 'response_time': response_time,
#                 'message': 'Database connection successful'
#             }

#         except Exception as e:
#             self.logger.error(f"Database health check failed: {e}")
#             return {
#                 'status': 'unhealthy',
#                 'error': str(e),
#                 'message': 'Database connection failed'
#             }

#     async def _check_celery_health(self) -> Dict[str, Any]:
#         """
#         Check Celery worker health.

#         Returns:
#             Dictionary with Celery health status
#         """
#         try:
#             # Import Celery components
#             from celery import current_app

#             # Check if Celery workers are running
#             inspect = current_app.control.inspect()
#             active_workers = inspect.active()
#             registered_workers = inspect.registered()

#             if not active_workers:
#                 return {
#                     'status': 'unhealthy',
#                     'message': 'No active Celery workers',
#                     'active_workers': 0,
#                     'registered_workers': len(registered_workers) if registered_workers else 0
#                 }

#             # Count active workers
#             total_active_workers = sum(len(tasks)
#                                        for tasks in active_workers.values())

#             if total_active_workers == 0:
#                 return {
#                     'status': 'degraded',
#                     'message': 'Celery workers are registered but not processing tasks',
#                     'active_workers': len(active_workers),
#                     'registered_workers': len(registered_workers) if registered_workers else 0
#                 }

#             return {
#                 'status': 'healthy',
#                 'message': 'Celery workers are active',
#                 'active_workers': len(active_workers),
#                 'registered_workers': len(registered_workers) if registered_workers else 0,
#                 'total_tasks': total_active_workers
#             }

#         except Exception as e:
#             self.logger.error(f"Celery health check failed: {e}")
#             return {
#                 'status': 'unhealthy',
#                 'error': str(e),
#                 'message': 'Celery health check failed'
#             }

#     async def _check_twilio_health(self) -> Dict[str, Any]:
#         """
#         Check Twilio service health.

#         Returns:
#             Dictionary with Twilio health status
#         """
#         try:
#             # Check if Twilio credentials are configured
#             account_sid = os.getenv('TWILIO_ACCOUNT_SID')
#             auth_token = os.getenv('TWILIO_AUTH_TOKEN')
#             phone_number = os.getenv('TWILIO_PHONE_NUMBER')

#             if not all([account_sid, auth_token, phone_number]):
#                 return {
#                     'status': 'unhealthy',
#                     'message': 'Twilio credentials not configured',
#                     'missing_credentials': [
#                         'TWILIO_ACCOUNT_SID' if not account_sid else None,
#                         'TWILIO_AUTH_TOKEN' if not auth_token else None,
#                         'TWILIO_PHONE_NUMBER' if not phone_number else None
#                     ]
#                 }

#             # Import Twilio client
#             from twilio.rest import Client

#             # Create client and check account status
#             client = Client(account_sid, auth_token)
#             account = client.api.accounts(account_sid).fetch()

#             # Check account status
#             if account.status != 'active':
#                 return {
#                     'status': 'unhealthy',
#                     'message': f'Twilio account status: {account.status}',
#                     'account_status': account.status
#                 }

#             return {
#                 'status': 'healthy',
#                 'message': 'Twilio service is available',
#                 'account_status': account.status,
#                 'account_name': account.friendly_name
#             }

#         except Exception as e:
#             self.logger.error(f"Twilio health check failed: {e}")
#             return {
#                 'status': 'unhealthy',
#                 'error': str(e),
#                 'message': 'Twilio service check failed'
#             }

#     async def get_health_summary(self) -> Dict[str, Any]:
#         """
#         Get a summary of system health.

#         Returns:
#             Dictionary with health summary
#         """
#         health_status = await self.check_system_health()

#         # Extract key information
#         summary = {
#             'overall_status': health_status['overall'],
#             'check_time': health_status['check_time'],
#             'response_time': health_status['response_time'],
#             'components': {}
#         }

#         # Add component status
#         for component in ['database', 'celery', 'twilio']:
#             if component in health_status and isinstance(health_status[component], dict):
#                 summary['components'][component] = {
#                     'status': health_status[component].get('status', 'unknown'),
#                     'message': health_status[component].get('message', 'No message'),
#                     'response_time': health_status[component].get('response_time', 0)
#                 }

#         # Add unhealthy components if any
#         if health_status['overall'] == 'unhealthy':
#             summary['unhealthy_components'] = health_status.get(
#                 'unhealthy_components', [])

#         return summary

#     async def get_health_history(self, hours: int = 24) -> Dict[str, Any]:
#         """
#         Get health check history for the specified time period.

#         Args:
#             hours: Number of hours to look back

#         Returns:
#             Dictionary with health history
#         """
#         # For now, return basic history info
#         # In a real implementation, this would query a database or cache
#         return {
#             'period_hours': hours,
#             'total_checks': 0,  # Would be calculated from stored history
#             'healthy_checks': 0,
#             'unhealthy_checks': 0,
#             'average_response_time': 0,
#             'last_check': self.last_check_time.isoformat() if self.last_check_time else None
#         }

#     def get_health_recommendations(self, health_status: Dict[str, Any]) -> list[str]:
#         """
#         Get recommendations based on health status.

#         Args:
#             health_status: Current health status

#         Returns:
#             List of recommendations
#         """
#         recommendations = []

#         # Check overall health
#         if health_status.get('overall') == 'unhealthy':
#             recommendations.append(
#                 'System is unhealthy - investigate immediately')

#         # Check individual components
#         for component in ['database', 'celery', 'twilio']:
#             if component in health_status and isinstance(health_status[component], dict):
#                 status = health_status[component].get('status')
#                 response_time = health_status[component].get(
#                     'response_time', 0)

#                 if status == 'unhealthy':
#                     recommendations.append(
#                         f'{component.title()} is unhealthy - check configuration and connectivity')
#                 elif status == 'degraded':
#                     recommendations.append(
#                         f'{component.title()} performance is degraded - monitor closely')

#                 if response_time > 5:
#                     recommendations.append(
#                         f'{component.title()} response time is slow ({response_time:.2f}s)')

#         # Check response time
#         overall_response_time = health_status.get('response_time', 0)
#         if overall_response_time > 10:
#             recommendations.append(
#                 f'Overall health check is slow ({overall_response_time:.2f}s)')

#         if not recommendations:
#             recommendations.append(
#                 'System health is good - no immediate action needed')

#         return recommendations


# def create_health_monitor() -> HealthMonitor:
#     """
#     Factory function to create a health monitor instance.

#     Returns:
#         HealthMonitor instance
#     """
#     return HealthMonitor()
