"""
Test Reliability Validator

This module provides comprehensive test reliability validation including
flaky test detection, consistency analysis, and reliability metrics.
"""

import statistics
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import json
from pathlib import Path
from collections import defaultdict, Counter


@dataclass
class RunResult:
    """Represents the result of a single test run."""
    test_name: str
    timestamp: datetime
    status: str  # "passed", "failed", "skipped", "error"
    execution_time: float
    error_message: Optional[str] = None
    retry_count: int = 0


@dataclass
class ReliabilityMetrics:
    """Represents reliability metrics for a test."""
    test_name: str
    total_runs: int
    passed_runs: int
    failed_runs: int
    skipped_runs: int
    error_runs: int
    success_rate: float
    failure_rate: float
    flakiness_score: float  # 0-1, higher means more flaky
    average_execution_time: float
    execution_time_variance: float
    last_failure: Optional[datetime]
    consecutive_failures: int
    consecutive_passes: int
    reliability_trend: str  # "improving", "stable", "degrading"


@dataclass
class TestSuiteReliabilityMetrics:
    """Represents reliability metrics for a test suite."""
    suite_name: str
    total_tests: int
    total_runs: int
    overall_success_rate: float
    flaky_tests: List[ReliabilityMetrics]
    stable_tests: List[ReliabilityMetrics]
    unreliable_tests: List[ReliabilityMetrics]
    average_flakiness_score: float
    reliability_trend: str
    timestamp: datetime


class ReliabilityValidator:
    """Validates test reliability and detects flaky tests."""
    
    def __init__(self, config_file: str = "test_reliability_config.json"):
        self.config_file = Path(config_file)
        self.config = self._load_config()
        self.test_history = defaultdict(list)  # test_name -> List[RunResult]
        self.suite_history = []
        
        # Default thresholds
        self.default_thresholds = {
            "flakiness_threshold": 0.1,  # 10% failure rate considered flaky
            "unreliable_threshold": 0.3,  # 30% failure rate considered unreliable
            "min_runs_for_analysis": 5,  # Minimum runs needed for reliable analysis
            "trend_analysis_window": 10,  # Number of recent runs to analyze trends
            "consecutive_failure_threshold": 3  # Alert after 3 consecutive failures
        }
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create defaults."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Failed to load config from {self.config_file}: {e}")
        
        return {
            "thresholds": {
                "flakiness_threshold": 0.1,  # 10% failure rate considered flaky
                "unreliable_threshold": 0.3,  # 30% failure rate considered unreliable
                "min_runs_for_analysis": 5,  # Minimum runs needed for reliable analysis
                "trend_analysis_window": 10,  # Number of recent runs to analyze trends
                "consecutive_failure_threshold": 3  # Alert after 3 consecutive failures
            },
            "categories": {
                "unit": {"expected_success_rate": 0.99},
                "integration": {"expected_success_rate": 0.95},
                "e2e": {"expected_success_rate": 0.90},
                "performance": {"expected_success_rate": 0.95}
            },
            "alert_settings": {
                "enable_flaky_detection": True,
                "enable_trend_analysis": True,
                "enable_consecutive_failure_alerts": True
            }
        }
    
    def save_config(self):
        """Save current configuration to file."""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2, default=str)
        print(f"📄 Test reliability config saved to {self.config_file}")
    
    def record_test_run(self, test_name: str, status: str, execution_time: float, 
                       error_message: str = None, retry_count: int = 0) -> RunResult:
        """Record the result of a test run."""
        result = RunResult(
            test_name=test_name,
            timestamp=datetime.now(),
            status=status,
            execution_time=execution_time,
            error_message=error_message,
            retry_count=retry_count
        )
        
        self.test_history[test_name].append(result)
        return result
    
    def analyze_test_reliability(self, test_name: str) -> ReliabilityMetrics:
        """Analyze reliability metrics for a specific test."""
        if test_name not in self.test_history:
            return ReliabilityMetrics(
                test_name=test_name,
                total_runs=0,
                passed_runs=0,
                failed_runs=0,
                skipped_runs=0,
                error_runs=0,
                success_rate=0.0,
                failure_rate=0.0,
                flakiness_score=0.0,
                average_execution_time=0.0,
                execution_time_variance=0.0,
                last_failure=None,
                consecutive_failures=0,
                consecutive_passes=0,
                reliability_trend="stable"
            )
        
        runs = self.test_history[test_name]
        
        # Count runs by status
        status_counts = Counter(run.status for run in runs)
        total_runs = len(runs)
        passed_runs = status_counts.get("passed", 0)
        failed_runs = status_counts.get("failed", 0)
        skipped_runs = status_counts.get("skipped", 0)
        error_runs = status_counts.get("error", 0)
        
        # Calculate rates
        success_rate = passed_runs / total_runs if total_runs > 0 else 0.0
        failure_rate = (failed_runs + error_runs) / total_runs if total_runs > 0 else 0.0
        
        # Calculate flakiness score (0-1, higher means more flaky)
        flakiness_score = self._calculate_flakiness_score(runs)
        
        # Calculate execution time metrics
        execution_times = [run.execution_time for run in runs]
        average_execution_time = statistics.mean(execution_times) if execution_times else 0.0
        execution_time_variance = statistics.variance(execution_times) if len(execution_times) > 1 else 0.0
        
        # Find last failure
        last_failure = None
        for run in reversed(runs):
            if run.status in ["failed", "error"]:
                last_failure = run.timestamp
                break
        
        # Calculate consecutive failures and passes
        consecutive_failures, consecutive_passes = self._calculate_consecutive_counts(runs)
        
        # Analyze reliability trend
        reliability_trend = self._analyze_reliability_trend(runs)
        
        return ReliabilityMetrics(
            test_name=test_name,
            total_runs=total_runs,
            passed_runs=passed_runs,
            failed_runs=failed_runs,
            skipped_runs=skipped_runs,
            error_runs=error_runs,
            success_rate=success_rate,
            failure_rate=failure_rate,
            flakiness_score=flakiness_score,
            average_execution_time=average_execution_time,
            execution_time_variance=execution_time_variance,
            last_failure=last_failure,
            consecutive_failures=consecutive_failures,
            consecutive_passes=consecutive_passes,
            reliability_trend=reliability_trend
        )
    
    def _calculate_flakiness_score(self, runs: List[RunResult]) -> float:
        """Calculate flakiness score for a test."""
        if len(runs) < 2:
            return 0.0
        
        # Flakiness is based on inconsistency in results
        status_changes = 0
        for i in range(1, len(runs)):
            if runs[i].status != runs[i-1].status:
                status_changes += 1
        
        # Normalize by number of runs
        flakiness_score = status_changes / (len(runs) - 1)
        
        # Also consider failure rate
        failure_rate = sum(1 for run in runs if run.status in ["failed", "error"]) / len(runs)
        
        # Combine both factors
        combined_score = (flakiness_score * 0.6) + (failure_rate * 0.4)
        
        return min(1.0, combined_score)
    
    def _calculate_consecutive_counts(self, runs: List[RunResult]) -> Tuple[int, int]:
        """Calculate consecutive failures and passes."""
        if not runs:
            return 0, 0
        
        # Start from the most recent run
        consecutive_failures = 0
        consecutive_passes = 0
        
        for run in reversed(runs):
            if run.status in ["failed", "error"]:
                consecutive_failures += 1
            elif run.status == "passed":
                consecutive_passes += 1
            else:
                break  # Stop counting on skipped or other statuses
        
        return consecutive_failures, consecutive_passes
    
    def _analyze_reliability_trend(self, runs: List[RunResult]) -> str:
        """Analyze reliability trend over recent runs."""
        if len(runs) < 5:
            return "stable"
        
        # Get recent runs for trend analysis
        window_size = self.config["thresholds"]["trend_analysis_window"]
        recent_runs = runs[-window_size:] if len(runs) >= window_size else runs
        
        # Calculate success rate for first and second half
        mid_point = len(recent_runs) // 2
        first_half = recent_runs[:mid_point]
        second_half = recent_runs[mid_point:]
        
        first_half_success_rate = sum(1 for run in first_half if run.status == "passed") / len(first_half)
        second_half_success_rate = sum(1 for run in second_half if run.status == "passed") / len(second_half)
        
        # Determine trend
        change = second_half_success_rate - first_half_success_rate
        threshold = 0.1  # 10% change threshold
        
        if change > threshold:
            return "improving"
        elif change < -threshold:
            return "degrading"
        else:
            return "stable"
    
    def analyze_suite_reliability(self, suite_name: str) -> TestSuiteReliabilityMetrics:
        """Analyze reliability metrics for a test suite."""
        if not self.test_history:
            return TestSuiteReliabilityMetrics(
                suite_name=suite_name,
                total_tests=0,
                total_runs=0,
                overall_success_rate=0.0,
                flaky_tests=[],
                stable_tests=[],
                unreliable_tests=[],
                average_flakiness_score=0.0,
                reliability_trend="stable",
                timestamp=datetime.now()
            )
        
        # Analyze all tests
        test_metrics = []
        for test_name in self.test_history.keys():
            metrics = self.analyze_test_reliability(test_name)
            test_metrics.append(metrics)
        
        # Calculate overall metrics
        total_tests = len(test_metrics)
        total_runs = sum(metrics.total_runs for metrics in test_metrics)
        total_passed = sum(metrics.passed_runs for metrics in test_metrics)
        overall_success_rate = total_passed / total_runs if total_runs > 0 else 0.0
        
        # Categorize tests
        flakiness_threshold = self.config["thresholds"]["flakiness_threshold"]
        unreliable_threshold = self.config["thresholds"]["unreliable_threshold"]
        
        flaky_tests = [m for m in test_metrics if m.failure_rate > flakiness_threshold and m.failure_rate <= unreliable_threshold]
        unreliable_tests = [m for m in test_metrics if m.failure_rate > unreliable_threshold]
        stable_tests = [m for m in test_metrics if m.failure_rate <= flakiness_threshold]
        
        # Calculate average flakiness score
        average_flakiness_score = statistics.mean([m.flakiness_score for m in test_metrics]) if test_metrics else 0.0
        
        # Analyze overall reliability trend
        reliability_trend = self._analyze_suite_reliability_trend(test_metrics)
        
        suite_metrics = TestSuiteReliabilityMetrics(
            suite_name=suite_name,
            total_tests=total_tests,
            total_runs=total_runs,
            overall_success_rate=overall_success_rate,
            flaky_tests=flaky_tests,
            stable_tests=stable_tests,
            unreliable_tests=unreliable_tests,
            average_flakiness_score=average_flakiness_score,
            reliability_trend=reliability_trend,
            timestamp=datetime.now()
        )
        
        self.suite_history.append(suite_metrics)
        return suite_metrics
    
    def _analyze_suite_reliability_trend(self, test_metrics: List[ReliabilityMetrics]) -> str:
        """Analyze overall reliability trend for the suite."""
        if len(test_metrics) < 2:
            return "stable"
        
        # Count tests by trend
        trend_counts = Counter(metrics.reliability_trend for metrics in test_metrics)
        
        # Determine overall trend
        if trend_counts.get("improving", 0) > trend_counts.get("degrading", 0):
            return "improving"
        elif trend_counts.get("degrading", 0) > trend_counts.get("improving", 0):
            return "degrading"
        else:
            return "stable"
    
    def validate_test_reliability(self) -> Dict[str, Any]:
        """Validate test reliability and generate recommendations."""
        validation_results = {
            "overall_status": "passed",
            "alerts": [],
            "warnings": [],
            "recommendations": [],
            "summary": {}
        }
        
        if not self.test_history:
            validation_results["overall_status"] = "no_data"
            return validation_results
        
        # Analyze all tests
        test_metrics = []
        for test_name in self.test_history.keys():
            metrics = self.analyze_test_reliability(test_name)
            test_metrics.append(metrics)
        
        # Check for alerts and warnings
        flakiness_threshold = self.config["thresholds"]["flakiness_threshold"]
        unreliable_threshold = self.config["thresholds"]["unreliable_threshold"]
        consecutive_failure_threshold = self.config["thresholds"]["consecutive_failure_threshold"]
        
        for metrics in test_metrics:
            # Check for unreliable tests
            if metrics.failure_rate > unreliable_threshold:
                validation_results["alerts"].append({
                    "type": "unreliable_test",
                    "test": metrics.test_name,
                    "failure_rate": metrics.failure_rate,
                    "total_runs": metrics.total_runs
                })
            
            # Check for flaky tests
            elif metrics.failure_rate > flakiness_threshold:
                validation_results["warnings"].append({
                    "type": "flaky_test",
                    "test": metrics.test_name,
                    "failure_rate": metrics.failure_rate,
                    "flakiness_score": metrics.flakiness_score
                })
            
            # Check for consecutive failures
            if metrics.consecutive_failures >= consecutive_failure_threshold:
                validation_results["alerts"].append({
                    "type": "consecutive_failures",
                    "test": metrics.test_name,
                    "consecutive_failures": metrics.consecutive_failures,
                    "last_failure": metrics.last_failure
                })
        
        # Determine overall status
        if validation_results["alerts"]:
            validation_results["overall_status"] = "failed"
        elif validation_results["warnings"]:
            validation_results["overall_status"] = "warning"
        
        # Generate recommendations
        validation_results["recommendations"] = self._generate_reliability_recommendations(
            validation_results["alerts"], validation_results["warnings"], test_metrics
        )
        
        # Generate summary
        validation_results["summary"] = {
            "total_tests": len(test_metrics),
            "total_runs": sum(m.total_runs for m in test_metrics),
            "overall_success_rate": sum(m.passed_runs for m in test_metrics) / sum(m.total_runs for m in test_metrics) if test_metrics else 0.0,
            "flaky_tests": len([m for m in test_metrics if m.failure_rate > flakiness_threshold and m.failure_rate <= unreliable_threshold]),
            "unreliable_tests": len([m for m in test_metrics if m.failure_rate > unreliable_threshold]),
            "stable_tests": len([m for m in test_metrics if m.failure_rate <= flakiness_threshold]),
            "average_flakiness_score": statistics.mean([m.flakiness_score for m in test_metrics]) if test_metrics else 0.0
        }
        
        return validation_results
    
    def _generate_reliability_recommendations(self, alerts: List[Dict], warnings: List[Dict], 
                                            test_metrics: List[ReliabilityMetrics]) -> List[str]:
        """Generate recommendations based on reliability analysis."""
        recommendations = []
        
        if alerts:
            unreliable_count = len([a for a in alerts if a["type"] == "unreliable_test"])
            consecutive_count = len([a for a in alerts if a["type"] == "consecutive_failures"])
            
            if unreliable_count > 0:
                recommendations.append(f"🚨 {unreliable_count} tests are unreliable (failure rate > 30%). Immediate attention required.")
            
            if consecutive_count > 0:
                recommendations.append(f"🚨 {consecutive_count} tests have consecutive failures. Check for environmental issues.")
        
        if warnings:
            flaky_count = len([w for w in warnings if w["type"] == "flaky_test"])
            if flaky_count > 0:
                recommendations.append(f"⚠️  {flaky_count} tests are flaky (failure rate 10-30%). Consider improving test stability.")
        
        # Trend-based recommendations
        degrading_tests = [m for m in test_metrics if m.reliability_trend == "degrading"]
        if degrading_tests:
            recommendations.append(f"📉 {len(degrading_tests)} tests show degrading reliability. Monitor closely.")
        
        # High variance recommendations
        high_variance_tests = [m for m in test_metrics if m.execution_time_variance > 1.0]
        if high_variance_tests:
            recommendations.append(f"⏱️  {len(high_variance_tests)} tests have high execution time variance. Consider performance optimization.")
        
        return recommendations
    
    def generate_reliability_report(self) -> str:
        """Generate comprehensive reliability report."""
        if not self.test_history:
            return "No reliability data available."
        
        validation = self.validate_test_reliability()
        suite_metrics = self.analyze_suite_reliability("Current Suite")
        
        report = f"""
Test Reliability Validation Report
==================================

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

OVERALL STATUS: {validation['overall_status'].upper()}

SUMMARY
=======
Total Tests: {validation['summary']['total_tests']}
Total Runs: {validation['summary']['total_runs']}
Overall Success Rate: {validation['summary']['overall_success_rate']:.1%}
Stable Tests: {validation['summary']['stable_tests']}
Flaky Tests: {validation['summary']['flaky_tests']}
Unreliable Tests: {validation['summary']['unreliable_tests']}
Average Flakiness Score: {validation['summary']['average_flakiness_score']:.3f}

RELIABILITY TREND: {suite_metrics.reliability_trend.upper()}

ALERTS
======
"""
        
        if validation['alerts']:
            for alert in validation['alerts']:
                report += f"- {alert['type'].replace('_', ' ').title()}: {alert['test']}\n"
        else:
            report += "No alerts.\n"
        
        if validation['warnings']:
            report += "\nWARNINGS\n========\n"
            for warning in validation['warnings']:
                report += f"- {warning['type'].replace('_', ' ').title()}: {warning['test']}\n"
        
        if validation['recommendations']:
            report += "\nRECOMMENDATIONS\n===============\n"
            for i, recommendation in enumerate(validation['recommendations'], 1):
                report += f"{i}. {recommendation}\n"
        
        return report
    
    def save_reliability_report(self, filename: str = None):
        """Save reliability report to file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"test_reliability_report_{timestamp}.txt"
        
        report = self.generate_reliability_report()
        report_file = Path(filename)
        
        with open(report_file, 'w') as f:
            f.write(report)
        
        print(f"📄 Reliability report saved to {report_file}")
    
    def clear_test_history(self):
        """Clear test history for new analysis."""
        self.test_history.clear()
        self.suite_history.clear()


# Global validator instance
reliability_validator = ReliabilityValidator()


def get_reliability_validator() -> ReliabilityValidator:
    """Get the global reliability validator."""
    return reliability_validator


def record_test_run(test_name: str, status: str, execution_time: float, 
                   error_message: str = None, retry_count: int = 0) -> RunResult:
    """Record a test run result."""
    return reliability_validator.record_test_run(test_name, status, execution_time, error_message, retry_count)


def validate_test_reliability() -> Dict[str, Any]:
    """Validate test reliability."""
    return reliability_validator.validate_test_reliability()


def generate_reliability_report() -> str:
    """Generate reliability report."""
    return reliability_validator.generate_reliability_report()
