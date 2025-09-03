"""
Test Execution Time Validator

This module provides comprehensive test execution time validation including
performance benchmarking, timeout detection, and execution time analysis.
"""

import time
import statistics
from typing import Dict, List, Any, Optional, Callable, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import json
from pathlib import Path


@dataclass
class ExecutionTimeMetrics:
    """Represents execution time metrics for a test."""
    test_name: str
    execution_time: float
    timestamp: datetime
    status: str  # "passed", "failed", "skipped"
    category: str  # "unit", "integration", "e2e"
    complexity: str  # "simple", "medium", "complex"
    timeout_threshold: float
    within_threshold: bool


@dataclass
class TestSuiteMetrics:
    """Represents execution time metrics for a test suite."""
    suite_name: str
    total_tests: int
    total_execution_time: float
    average_execution_time: float
    median_execution_time: float
    slowest_test: Optional[ExecutionTimeMetrics]
    fastest_test: Optional[ExecutionTimeMetrics]
    timeout_violations: List[ExecutionTimeMetrics]
    performance_trend: str  # "improving", "stable", "degrading"
    timestamp: datetime


class TestExecutionTimeValidator:
    """Validates test execution times and performance."""
    
    def __init__(self, config_file: str = "test_time_config.json"):
        self.config_file = Path(config_file)
        self.config = self._load_config()
        self.metrics_history = []
        self.current_metrics = []
        
        # Default thresholds
        self.default_thresholds = {
            "unit": 1.0,      # 1 second
            "integration": 5.0,  # 5 seconds
            "e2e": 30.0,     # 30 seconds
            "performance": 10.0  # 10 seconds
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
                "unit": 1.0,      # 1 second
                "integration": 5.0,  # 5 seconds
                "e2e": 30.0,     # 30 seconds
                "performance": 10.0  # 10 seconds
            },
            "trend_analysis_window": 10,  # Number of runs to analyze for trends
            "alert_thresholds": {
                "slow_test_multiplier": 3.0,  # Alert if test is 3x slower than average
                "suite_degradation_threshold": 0.2  # Alert if suite is 20% slower
            },
            "categories": {
                "unit": ["test_", "unit_"],
                "integration": ["integration_", "test_integration_"],
                "e2e": ["e2e_", "test_e2e_"],
                "performance": ["performance_", "benchmark_"]
            }
        }
    
    def save_config(self):
        """Save current configuration to file."""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2, default=str)
        print(f"📄 Test time config saved to {self.config_file}")
    
    def measure_test_execution_time(self, test_func: Callable, test_name: str, 
                                  category: str = "unit") -> ExecutionTimeMetrics:
        """Measure execution time of a single test."""
        start_time = time.time()
        
        try:
            # Execute the test
            result = test_func()
            status = "passed" if result is not False else "failed"
        except Exception as e:
            status = "failed"
            result = None
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Determine complexity based on execution time
        complexity = self._determine_complexity(execution_time, category)
        
        # Get timeout threshold for this category
        timeout_threshold = self.config["thresholds"].get(category, self.default_thresholds[category])
        within_threshold = execution_time <= timeout_threshold
        
        metrics = ExecutionTimeMetrics(
            test_name=test_name,
            execution_time=execution_time,
            timestamp=datetime.now(),
            status=status,
            category=category,
            complexity=complexity,
            timeout_threshold=timeout_threshold,
            within_threshold=within_threshold
        )
        
        self.current_metrics.append(metrics)
        return metrics
    
    def _determine_complexity(self, execution_time: float, category: str) -> str:
        """Determine test complexity based on execution time."""
        thresholds = self.config["thresholds"]
        category_threshold = thresholds.get(category, self.default_thresholds[category])
        
        if execution_time <= category_threshold * 0.3:
            return "simple"
        elif execution_time <= category_threshold * 0.7:
            return "medium"
        else:
            return "complex"
    
    def analyze_test_suite_performance(self, suite_name: str) -> TestSuiteMetrics:
        """Analyze performance of a test suite."""
        if not self.current_metrics:
            return TestSuiteMetrics(
                suite_name=suite_name,
                total_tests=0,
                total_execution_time=0.0,
                average_execution_time=0.0,
                median_execution_time=0.0,
                slowest_test=None,
                fastest_test=None,
                timeout_violations=[],
                performance_trend="stable",
                timestamp=datetime.now()
            )
        
        # Calculate basic metrics
        execution_times = [m.execution_time for m in self.current_metrics]
        total_execution_time = sum(execution_times)
        average_execution_time = statistics.mean(execution_times)
        median_execution_time = statistics.median(execution_times)
        
        # Find slowest and fastest tests
        slowest_test = max(self.current_metrics, key=lambda m: m.execution_time)
        fastest_test = min(self.current_metrics, key=lambda m: m.execution_time)
        
        # Find timeout violations
        timeout_violations = [m for m in self.current_metrics if not m.within_threshold]
        
        # Analyze performance trend
        performance_trend = self._analyze_performance_trend()
        
        suite_metrics = TestSuiteMetrics(
            suite_name=suite_name,
            total_tests=len(self.current_metrics),
            total_execution_time=total_execution_time,
            average_execution_time=average_execution_time,
            median_execution_time=median_execution_time,
            slowest_test=slowest_test,
            fastest_test=fastest_test,
            timeout_violations=timeout_violations,
            performance_trend=performance_trend,
            timestamp=datetime.now()
        )
        
        # Store in history
        self.metrics_history.append(suite_metrics)
        
        return suite_metrics
    
    def _analyze_performance_trend(self) -> str:
        """Analyze performance trend over recent runs."""
        if len(self.metrics_history) < 2:
            return "stable"
        
        # Get recent runs for trend analysis
        window_size = self.config.get("trend_analysis_window", 10)
        recent_runs = self.metrics_history[-window_size:]
        
        if len(recent_runs) < 2:
            return "stable"
        
        # Calculate trend
        first_avg = recent_runs[0].average_execution_time
        last_avg = recent_runs[-1].average_execution_time
        
        change_percent = (last_avg - first_avg) / first_avg if first_avg > 0 else 0
        
        threshold = self.config["alert_thresholds"]["suite_degradation_threshold"]
        
        if change_percent > threshold:
            return "degrading"
        elif change_percent < -threshold:
            return "improving"
        else:
            return "stable"
    
    def validate_execution_times(self) -> Dict[str, Any]:
        """Validate all execution times against thresholds."""
        validation_results = {
            "overall_status": "passed",
            "violations": [],
            "warnings": [],
            "recommendations": [],
            "summary": {}
        }
        
        if not self.current_metrics:
            validation_results["overall_status"] = "no_data"
            return validation_results
        
        # Check for timeout violations
        timeout_violations = [m for m in self.current_metrics if not m.within_threshold]
        if timeout_violations:
            validation_results["overall_status"] = "failed"
            validation_results["violations"].extend([
                {
                    "type": "timeout_violation",
                    "test": violation.test_name,
                    "execution_time": violation.execution_time,
                    "threshold": violation.timeout_threshold,
                    "category": violation.category
                }
                for violation in timeout_violations
            ])
        
        # Check for slow tests (3x slower than average)
        execution_times = [m.execution_time for m in self.current_metrics]
        average_time = statistics.mean(execution_times)
        slow_multiplier = self.config["alert_thresholds"]["slow_test_multiplier"]
        
        slow_tests = [m for m in self.current_metrics 
                     if m.execution_time > average_time * slow_multiplier]
        
        if slow_tests:
            validation_results["warnings"].extend([
                {
                    "type": "slow_test",
                    "test": test.test_name,
                    "execution_time": test.execution_time,
                    "average_time": average_time,
                    "multiplier": test.execution_time / average_time
                }
                for test in slow_tests
            ])
        
        # Generate recommendations
        validation_results["recommendations"] = self._generate_execution_time_recommendations(
            validation_results["violations"], validation_results["warnings"]
        )
        
        # Generate summary
        validation_results["summary"] = {
            "total_tests": len(self.current_metrics),
            "timeout_violations": len(timeout_violations),
            "slow_tests": len(slow_tests),
            "average_execution_time": average_time,
            "total_execution_time": sum(execution_times),
            "categories": self._get_category_summary()
        }
        
        return validation_results
    
    def _generate_execution_time_recommendations(self, violations: List[Dict], warnings: List[Dict]) -> List[str]:
        """Generate recommendations based on execution time analysis."""
        recommendations = []
        
        if violations:
            recommendations.append(f"🚨 {len(violations)} tests exceed timeout thresholds. Consider optimizing or increasing thresholds.")
        
        if warnings:
            recommendations.append(f"⚠️  {len(warnings)} tests are significantly slower than average. Consider performance optimization.")
        
        # Category-specific recommendations
        category_times = {}
        for metric in self.current_metrics:
            if metric.category not in category_times:
                category_times[metric.category] = []
            category_times[metric.category].append(metric.execution_time)
        
        for category, times in category_times.items():
            avg_time = statistics.mean(times)
            threshold = self.config["thresholds"].get(category, self.default_thresholds[category])
            
            if avg_time > threshold * 0.8:
                recommendations.append(f"📊 {category} tests are approaching timeout threshold (avg: {avg_time:.2f}s, threshold: {threshold}s)")
        
        return recommendations
    
    def _get_category_summary(self) -> Dict[str, Any]:
        """Get summary by test category."""
        category_summary = {}
        
        for metric in self.current_metrics:
            if metric.category not in category_summary:
                category_summary[metric.category] = {
                    "count": 0,
                    "total_time": 0.0,
                    "average_time": 0.0,
                    "violations": 0
                }
            
            summary = category_summary[metric.category]
            summary["count"] += 1
            summary["total_time"] += metric.execution_time
            if not metric.within_threshold:
                summary["violations"] += 1
        
        # Calculate averages
        for category, summary in category_summary.items():
            if summary["count"] > 0:
                summary["average_time"] = summary["total_time"] / summary["count"]
        
        return category_summary
    
    def generate_execution_time_report(self) -> str:
        """Generate comprehensive execution time report."""
        if not self.current_metrics:
            return "No execution time data available."
        
        validation = self.validate_execution_times()
        suite_metrics = self.analyze_test_suite_performance("Current Suite")
        
        report = f"""
Test Execution Time Validation Report
====================================

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

OVERALL STATUS: {validation['overall_status'].upper()}

SUMMARY
=======
Total Tests: {validation['summary']['total_tests']}
Total Execution Time: {validation['summary']['total_execution_time']:.2f}s
Average Execution Time: {validation['summary']['average_execution_time']:.2f}s
Timeout Violations: {validation['summary']['timeout_violations']}
Slow Tests: {validation['summary']['slow_tests']}

PERFORMANCE TREND: {suite_metrics.performance_trend.upper()}

CATEGORY BREAKDOWN
==================
"""
        
        for category, summary in validation['summary']['categories'].items():
            report += f"""
{category.upper()} Tests:
  Count: {summary['count']}
  Average Time: {summary['average_time']:.2f}s
  Total Time: {summary['total_time']:.2f}s
  Violations: {summary['violations']}
"""
        
        if validation['violations']:
            report += "\nTIMEOUT VIOLATIONS\n==================\n"
            for violation in validation['violations']:
                report += f"- {violation['test']}: {violation['execution_time']:.2f}s (threshold: {violation['threshold']:.2f}s)\n"
        
        if validation['warnings']:
            report += "\nSLOW TESTS\n==========\n"
            for warning in validation['warnings']:
                report += f"- {warning['test']}: {warning['execution_time']:.2f}s ({warning['multiplier']:.1f}x average)\n"
        
        if validation['recommendations']:
            report += "\nRECOMMENDATIONS\n===============\n"
            for i, recommendation in enumerate(validation['recommendations'], 1):
                report += f"{i}. {recommendation}\n"
        
        return report
    
    def save_execution_time_report(self, filename: str = None):
        """Save execution time report to file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"test_execution_time_report_{timestamp}.txt"
        
        report = self.generate_execution_time_report()
        report_file = Path(filename)
        
        with open(report_file, 'w') as f:
            f.write(report)
        
        print(f"📄 Execution time report saved to {report_file}")
    
    def clear_current_metrics(self):
        """Clear current metrics for new test run."""
        self.current_metrics = []
    
    def get_performance_history(self) -> List[TestSuiteMetrics]:
        """Get performance history."""
        return self.metrics_history


# Global validator instance
execution_time_validator = TestExecutionTimeValidator()


def get_execution_time_validator() -> TestExecutionTimeValidator:
    """Get the global execution time validator."""
    return execution_time_validator


def measure_test_time(test_func: Callable, test_name: str, category: str = "unit") -> ExecutionTimeMetrics:
    """Measure execution time of a test."""
    return execution_time_validator.measure_test_execution_time(test_func, test_name, category)


def validate_test_execution_times() -> Dict[str, Any]:
    """Validate all test execution times."""
    return execution_time_validator.validate_execution_times()


def generate_execution_time_report() -> str:
    """Generate execution time report."""
    return execution_time_validator.generate_execution_time_report()
