"""
Task Failure Alerting System

Monitors task execution and sends alerts for failures,
performance issues, and system problems.
"""

import json
import logging
import smtplib
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from enum import Enum
from typing import Any, Dict, List, Optional, Union

import requests

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertChannel(Enum):
    """Available alert channels."""

    EMAIL = "email"
    SLACK = "slack"
    WEBHOOK = "webhook"
    LOG = "log"
    CONSOLE = "console"


@dataclass
class AlertRule:
    """Defines when and how to send alerts."""

    name: str
    condition: str  # e.g., "task_failure", "performance_degradation", "system_issue"
    threshold: float
    window: timedelta
    channels: List[AlertChannel]
    severity: AlertSeverity = AlertSeverity.WARNING
    message_template: str = ""
    enabled: bool = True
    cooldown: timedelta = timedelta(minutes=5)  # Prevent alert spam
    last_triggered: Optional[datetime] = None


@dataclass
class Alert:
    """Represents an alert instance."""

    id: str
    rule_name: str
    severity: AlertSeverity
    message: str
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)
    acknowledged: bool = False
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None


class AlertManager:
    """Manages task execution alerts and notifications."""

    def __init__(self, initialize_defaults: bool = True):
        """Initialize the alert manager."""
        self.rules: List[AlertRule] = []
        self.alert_history: List[Alert] = []
        self.lock = threading.Lock()
        self.logger = logging.getLogger(__name__)
        self.alert_counter = 0
        self.enabled = True
        self.config = {}

        # Initialize channels
        self._initialize_channels()

        # Initialize default rules only if requested
        if initialize_defaults:
            self._initialize_default_rules()

    def add_rule(self, rule: AlertRule) -> bool:
        """Add a new alert rule."""
        try:
            with self.lock:
                # Check for duplicate rule names
                if any(r.name == rule.name for r in self.rules):
                    self.logger.warning(f"Rule with name '{rule.name}' already exists")
                    return False

                self.rules.append(rule)
                self.logger.info(f"Added alert rule: {rule.name}")
                return True

        except Exception as e:
            self.logger.error(f"Error adding alert rule: {e}")
            return False

    def remove_rule(self, rule_name: str) -> bool:
        """Remove an alert rule."""
        try:
            with self.lock:
                original_count = len(self.rules)
                self.rules = [r for r in self.rules if r.name != rule_name]

                if len(self.rules) < original_count:
                    self.logger.info(f"Removed alert rule: {rule_name}")
                    return True
                else:
                    self.logger.warning(f"Alert rule not found: {rule_name}")
                    return False

        except Exception as e:
            self.logger.error(f"Error removing alert rule: {e}")
            return False

    def check_alerts(self, metrics: Dict[str, Any]) -> List[Alert]:
        """Check if any alert conditions are met and return triggered alerts."""
        if not self.enabled:
            return []

        try:
            triggered_alerts = []

            with self.lock:
                for rule in self.rules:
                    if not rule.enabled:
                        continue

                    # Check cooldown
                    if (
                        rule.last_triggered
                        and datetime.utcnow() - rule.last_triggered < rule.cooldown
                    ):
                        continue

                    if self._evaluate_rule(rule, metrics):
                        alert = self._create_alert(rule, metrics)
                        if alert:
                            triggered_alerts.append(alert)
                            rule.last_triggered = datetime.utcnow()

                            # Send alert through configured channels
                            self._send_alert(alert, rule.channels)

            return triggered_alerts

        except Exception as e:
            self.logger.error(f"Error checking alerts: {e}")
            return []

    def acknowledge_alert(self, alert_id: str, user: str) -> bool:
        """Acknowledge an alert."""
        try:
            with self.lock:
                for alert in self.alert_history:
                    if alert.id == alert_id:
                        alert.acknowledged = True
                        alert.acknowledged_by = user
                        alert.acknowledged_at = datetime.utcnow()
                        self.logger.info(f"Alert {alert_id} acknowledged by {user}")
                        return True

                self.logger.warning(f"Alert {alert_id} not found")
                return False

        except Exception as e:
            self.logger.error(f"Error acknowledging alert: {e}")
            return False

    def get_active_alerts(self) -> List[Alert]:
        """Get all active (unacknowledged) alerts."""
        try:
            with self.lock:
                return [alert for alert in self.alert_history if not alert.acknowledged]

        except Exception as e:
            self.logger.error(f"Error getting active alerts: {e}")
            return []

    def get_alert_history(self, hours: int = 24) -> List[Alert]:
        """Get alert history for the specified time period."""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)

            with self.lock:
                return [
                    alert
                    for alert in self.alert_history
                    if alert.timestamp > cutoff_time
                ]

        except Exception as e:
            self.logger.error(f"Error getting alert history: {e}")
            return []

    def get_alert_summary(self) -> Dict[str, Any]:
        """Get a summary of alert statistics."""
        try:
            with self.lock:
                total_alerts = len(self.alert_history)
                active_alerts = len(
                    [a for a in self.alert_history if not a.acknowledged]
                )

                severity_counts = {}
                for alert in self.alert_history:
                    severity = alert.severity.value
                    severity_counts[severity] = severity_counts.get(severity, 0) + 1

                return {
                    "total_alerts": total_alerts,
                    "active_alerts": active_alerts,
                    "acknowledged_alerts": total_alerts - active_alerts,
                    "severity_distribution": severity_counts,
                    "rules_count": len(self.rules),
                    "enabled_rules": len([r for r in self.rules if r.enabled]),
                }

        except Exception as e:
            self.logger.error(f"Error getting alert summary: {e}")
            return {}

    def cleanup_old_alerts(self, max_age_hours: int = 168):  # 1 week default
        """Clean up old alert history."""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
            original_count = len(self.alert_history)

            with self.lock:
                self.alert_history = [
                    alert
                    for alert in self.alert_history
                    if alert.timestamp > cutoff_time
                ]

            cleaned_count = original_count - len(self.alert_history)
            if cleaned_count > 0:
                self.logger.info(f"Cleaned up {cleaned_count} old alerts")

        except Exception as e:
            self.logger.error(f"Error cleaning up old alerts: {e}")

    def reset(self):
        """Reset the alert manager state."""
        try:
            with self.lock:
                self.rules.clear()
                self.alert_history.clear()
                self.alert_counter = 0
                self.logger.info("Alert manager reset")

        except Exception as e:
            self.logger.error(f"Error resetting alert manager: {e}")

    def _initialize_default_rules(self):
        """Initialize default alert rules."""
        try:
            default_rules = [
                AlertRule(
                    name="high_task_failure_rate",
                    condition="task_failure_rate",
                    threshold=0.1,  # 10% failure rate
                    window=timedelta(minutes=15),
                    channels=[AlertChannel.LOG, AlertChannel.CONSOLE],
                    severity=AlertSeverity.WARNING,
                    message_template="Task failure rate is {rate:.1%} over the last {window} minutes",
                ),
                AlertRule(
                    name="critical_task_failure_rate",
                    condition="task_failure_rate",
                    threshold=0.25,  # 25% failure rate
                    window=timedelta(minutes=15),
                    channels=[
                        AlertChannel.LOG,
                        AlertChannel.CONSOLE,
                        AlertChannel.EMAIL,
                    ],
                    severity=AlertSeverity.CRITICAL,
                    message_template="CRITICAL: Task failure rate is {rate:.1%} over the last {window} minutes",
                ),
                AlertRule(
                    name="high_memory_usage",
                    condition="memory_usage",
                    threshold=0.9,  # 90% memory usage
                    window=timedelta(minutes=5),
                    channels=[AlertChannel.LOG, AlertChannel.CONSOLE],
                    severity=AlertSeverity.WARNING,
                    message_template="High memory usage: {memory_percent:.1%}",
                ),
                AlertRule(
                    name="high_cpu_usage",
                    condition="cpu_usage",
                    threshold=0.9,  # 90% CPU usage
                    window=timedelta(minutes=5),
                    channels=[AlertChannel.LOG, AlertChannel.CONSOLE],
                    severity=AlertSeverity.WARNING,
                    message_template="High CPU usage: {cpu_percent:.1%}",
                ),
                AlertRule(
                    name="queue_backlog",
                    condition="queue_length",
                    threshold=100,  # 100 tasks in queue
                    window=timedelta(minutes=5),
                    channels=[AlertChannel.LOG, AlertChannel.CONSOLE],
                    severity=AlertSeverity.WARNING,
                    message_template="Queue backlog detected: {queue_length} tasks in {queue_name}",
                ),
            ]

            for rule in default_rules:
                self.add_rule(rule)

        except Exception as e:
            self.logger.error(f"Error initializing default alert rules: {e}")

    def _initialize_channels(self):
        """Initialize alert channels."""
        try:
            # Email configuration
            self.email_config = self.config.get("email", {})

            # Slack configuration
            self.slack_config = self.config.get("slack", {})

            # Webhook configuration
            self.webhook_config = self.config.get("webhook", {})

            self.logger.info("Alert channels initialized")

        except Exception as e:
            self.logger.error(f"Error initializing alert channels: {e}")

    def _evaluate_rule(self, rule: AlertRule, metrics: Dict[str, Any]) -> bool:
        """Evaluate if an alert rule condition is met."""
        try:
            if rule.condition == "task_failure_rate":
                return self._evaluate_failure_rate(rule, metrics)
            elif rule.condition == "memory_usage":
                return self._evaluate_memory_usage(rule, metrics)
            elif rule.condition == "cpu_usage":
                return self._evaluate_cpu_usage(rule, metrics)
            elif rule.condition == "queue_length":
                return self._evaluate_queue_length(rule, metrics)
            elif rule.condition == "system_issue":
                return self._evaluate_system_issue(rule, metrics)
            else:
                self.logger.warning(f"Unknown alert condition: {rule.condition}")
                return False

        except Exception as e:
            self.logger.error(f"Error evaluating rule {rule.name}: {e}")
            return False

    def _evaluate_failure_rate(self, rule: AlertRule, metrics: Dict[str, Any]) -> bool:
        """Evaluate task failure rate condition."""
        try:
            failed_tasks = metrics.get("failed_tasks", 0)
            total_tasks = metrics.get("total_tasks", 0)

            if total_tasks == 0:
                return False

            failure_rate = failed_tasks / total_tasks
            return failure_rate >= rule.threshold

        except Exception as e:
            self.logger.error(f"Error evaluating failure rate: {e}")
            return False

    def _evaluate_memory_usage(self, rule: AlertRule, metrics: Dict[str, Any]) -> bool:
        """Evaluate memory usage condition."""
        try:
            memory_percent = metrics.get("memory_percent", 0)
            return memory_percent >= rule.threshold

        except Exception as e:
            self.logger.error(f"Error evaluating memory usage: {e}")
            return False

    def _evaluate_cpu_usage(self, rule: AlertRule, metrics: Dict[str, Any]) -> bool:
        """Evaluate CPU usage condition."""
        try:
            cpu_percent = metrics.get("cpu_percent", 0)
            return cpu_percent >= rule.threshold

        except Exception as e:
            self.logger.error(f"Error evaluating CPU usage: {e}")
            return False

    def _evaluate_queue_length(self, rule: AlertRule, metrics: Dict[str, Any]) -> bool:
        """Evaluate queue length condition."""
        try:
            queue_lengths = metrics.get("queue_lengths", {})
            for queue_name, length in queue_lengths.items():
                if length >= rule.threshold:
                    return True
            return False

        except Exception as e:
            self.logger.error(f"Error evaluating queue length: {e}")
            return False

    def _evaluate_system_issue(self, rule: AlertRule, metrics: Dict[str, Any]) -> bool:
        """Evaluate system issue condition."""
        try:
            # This is a catch-all for various system issues
            # Implement based on your specific needs
            return False

        except Exception as e:
            self.logger.error(f"Error evaluating system issue: {e}")
            return False

    def _create_alert(
        self, rule: AlertRule, metrics: Dict[str, Any]
    ) -> Optional[Alert]:
        """Create an alert instance."""
        try:
            self.alert_counter += 1
            alert_id = f"alert_{self.alert_counter}_{int(time.time())}"

            # Format message using template
            message = self._format_message(rule.message_template, rule, metrics)

            alert = Alert(
                id=alert_id,
                rule_name=rule.name,
                severity=rule.severity,
                message=message,
                timestamp=datetime.utcnow(),
                metadata={
                    "condition": rule.condition,
                    "threshold": rule.threshold,
                    "metrics": metrics,
                },
            )

            # Add to history
            self.alert_history.append(alert)

            return alert

        except Exception as e:
            self.logger.error(f"Error creating alert: {e}")
            return None

    def _format_message(
        self, template: str, rule: AlertRule, metrics: Dict[str, Any]
    ) -> str:
        """Format alert message using template and metrics."""
        try:
            if not template:
                return f"Alert triggered: {rule.condition} exceeded threshold {rule.threshold}"

            # Simple template formatting - can be enhanced with a proper template engine
            formatted = template

            # Replace common placeholders
            if (
                "{rate}" in formatted
                and "failed_tasks" in metrics
                and "total_tasks" in metrics
            ):
                total = metrics.get("total_tasks", 0)
                failed = metrics.get("failed_tasks", 0)
                rate = failed / total if total > 0 else 0
                formatted = formatted.replace("{rate}", f"{rate:.1%}")

            if "{window}" in formatted:
                window_minutes = int(rule.window.total_seconds() / 60)
                formatted = formatted.replace("{window}", f"{window_minutes} minutes")

            if "{memory_percent}" in formatted:
                memory_percent = metrics.get("memory_percent", 0)
                formatted = formatted.replace(
                    "{memory_percent}", f"{memory_percent:.1%}"
                )

            if "{cpu_percent}" in formatted:
                cpu_percent = metrics.get("cpu_percent", 0)
                formatted = formatted.replace("{cpu_percent}", f"{cpu_percent:.1%}")

            if "{queue_length}" in formatted:
                queue_lengths = metrics.get("queue_lengths", {})
                max_length = max(queue_lengths.values()) if queue_lengths else 0
                formatted = formatted.replace("{queue_length}", str(max_length))

            if "{queue_name}" in formatted:
                queue_lengths = metrics.get("queue_lengths", {})
                if queue_lengths:
                    max_queue = max(queue_lengths.items(), key=lambda x: x[1])[0]
                    formatted = formatted.replace("{queue_name}", max_queue)

            return formatted

        except Exception as e:
            self.logger.error(f"Error formatting message: {e}")
            return (
                f"Alert triggered: {rule.condition} exceeded threshold {rule.threshold}"
            )

    def _send_alert(self, alert: Alert, channels: List[AlertChannel]):
        """Send alert through configured channels."""
        try:
            for channel in channels:
                try:
                    if channel == AlertChannel.LOG:
                        self._send_log_alert(alert)
                    elif channel == AlertChannel.CONSOLE:
                        self._send_console_alert(alert)
                    elif channel == AlertChannel.EMAIL:
                        self._send_email_alert(alert)
                    elif channel == AlertChannel.SLACK:
                        self._send_slack_alert(alert)
                    elif channel == AlertChannel.WEBHOOK:
                        self._send_webhook_alert(alert)
                    else:
                        self.logger.warning(f"Unknown alert channel: {channel}")

                except Exception as e:
                    self.logger.error(f"Error sending alert through {channel}: {e}")

        except Exception as e:
            self.logger.error(f"Error sending alert: {e}")

    def _send_log_alert(self, alert: Alert):
        """Send alert to log."""
        log_level = {
            AlertSeverity.INFO: logging.INFO,
            AlertSeverity.WARNING: logging.WARNING,
            AlertSeverity.ERROR: logging.ERROR,
            AlertSeverity.CRITICAL: logging.CRITICAL,
        }.get(alert.severity, logging.WARNING)

        self.logger.log(
            log_level, f"ALERT [{alert.severity.value.upper()}]: {alert.message}"
        )

    def _send_console_alert(self, alert: Alert):
        """Send alert to console."""
        severity_color = {
            AlertSeverity.INFO: "\033[94m",  # Blue
            AlertSeverity.WARNING: "\033[93m",  # Yellow
            AlertSeverity.ERROR: "\033[91m",  # Red
            AlertSeverity.CRITICAL: "\033[95m",  # Magenta
        }.get(alert.severity, "\033[93m")

        reset_color = "\033[0m"
        timestamp = alert.timestamp.strftime("%Y-%m-%d %H:%M:%S")

        print(
            f"{severity_color}[{timestamp}] ALERT [{alert.severity.value.upper()}]: {alert.message}{reset_color}"
        )

    def _send_email_alert(self, alert: Alert):
        """Send alert via email."""
        try:
            if not self.email_config:
                self.logger.warning("Email configuration not available")
                return

            # Email configuration
            smtp_server = self.email_config.get("smtp_server")
            smtp_port = self.email_config.get("smtp_port", 587)
            username = self.email_config.get("username")
            password = self.email_config.get("password")
            from_email = self.email_config.get("from_email")
            to_emails = self.email_config.get("to_emails", [])

            if not all([smtp_server, username, password, from_email, to_emails]):
                self.logger.warning("Incomplete email configuration")
                return

            # Create message
            msg = MIMEMultipart()
            msg["From"] = from_email
            msg["To"] = ", ".join(to_emails)
            msg[
                "Subject"
            ] = f"ALERT: {alert.severity.value.upper()} - {alert.rule_name}"

            body = f"""
Alert Details:
==============
Severity: {alert.severity.value.upper()}
Rule: {alert.rule_name}
Message: {alert.message}
Timestamp: {alert.timestamp}
Alert ID: {alert.id}

System Status:
==============
{json.dumps(alert.metadata.get('metrics', {}), indent=2)}
            """

            msg.attach(MIMEText(body, "plain"))

            # Send email
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(username, password)
                server.send_message(msg)

            self.logger.info(f"Email alert sent for {alert.id}")

        except Exception as e:
            self.logger.error(f"Error sending email alert: {e}")

    def _send_slack_alert(self, alert: Alert):
        """Send alert via Slack."""
        try:
            if not self.slack_config:
                self.logger.warning("Slack configuration not available")
                return

            webhook_url = self.slack_config.get("webhook_url")
            if not webhook_url:
                self.logger.warning("Slack webhook URL not configured")
                return

            # Slack message formatting
            color = {
                AlertSeverity.INFO: "#36a64f",  # Green
                AlertSeverity.WARNING: "#ffcc00",  # Yellow
                AlertSeverity.ERROR: "#ff0000",  # Red
                AlertSeverity.CRITICAL: "#8b0000",  # Dark Red
            }.get(alert.severity, "#ffcc00")

            payload = {
                "attachments": [
                    {
                        "color": color,
                        "title": f"🚨 ALERT: {alert.severity.value.upper()}",
                        "text": alert.message,
                        "fields": [
                            {"title": "Rule", "value": alert.rule_name, "short": True},
                            {
                                "title": "Severity",
                                "value": alert.severity.value.upper(),
                                "short": True,
                            },
                            {
                                "title": "Timestamp",
                                "value": alert.timestamp.strftime(
                                    "%Y-%m-%d %H:%M:%S UTC"
                                ),
                                "short": True,
                            },
                            {"title": "Alert ID", "value": alert.id, "short": True},
                        ],
                        "footer": "Personal Assistant Background Task System",
                    }
                ]
            }

            response = requests.post(webhook_url, json=payload, timeout=10)
            response.raise_for_status()

            self.logger.info(f"Slack alert sent for {alert.id}")

        except Exception as e:
            self.logger.error(f"Error sending Slack alert: {e}")

    def _send_webhook_alert(self, alert: Alert):
        """Send alert via webhook."""
        try:
            if not self.webhook_config:
                self.logger.warning("Webhook configuration not available")
                return

            webhook_url = self.webhook_config.get("url")
            if not webhook_url:
                self.logger.warning("Webhook URL not configured")
                return

            # Prepare payload
            payload = {
                "alert_id": alert.id,
                "rule_name": alert.rule_name,
                "severity": alert.severity.value,
                "message": alert.message,
                "timestamp": alert.timestamp.isoformat(),
                "metadata": alert.metadata,
            }

            # Send webhook
            headers = self.webhook_config.get("headers", {})
            timeout = self.webhook_config.get("timeout", 10)

            response = requests.post(
                webhook_url, json=payload, headers=headers, timeout=timeout
            )
            response.raise_for_status()

            self.logger.info(f"Webhook alert sent for {alert.id}")

        except Exception as e:
            self.logger.error(f"Error sending webhook alert: {e}")


# Global alert manager instance
_alert_manager: Optional[AlertManager] = None


def get_alert_manager(config: Optional[Dict[str, Any]] = None) -> AlertManager:
    """Get the global alert manager instance."""
    global _alert_manager
    if _alert_manager is None:
        _alert_manager = AlertManager(config)
    return _alert_manager


def check_alerts(metrics: Dict[str, Any]) -> List[Alert]:
    """Check if any alert conditions are met."""
    return get_alert_manager().check_alerts(metrics)


def add_alert_rule(rule: AlertRule) -> bool:
    """Add a new alert rule."""
    return get_alert_manager().add_rule(rule)
