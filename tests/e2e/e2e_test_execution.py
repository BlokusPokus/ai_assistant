"""
E2E Test Execution

This module provides comprehensive End-to-End test execution capabilities,
including test orchestration, parallel execution, and result reporting.
"""

import asyncio
import time
import json
import pytest
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import traceback

from tests.e2e.e2e_test_environment import E2ETestEnvironment, E2ETestConfig
from tests.e2e.e2e_test_scenarios import (
    AuthenticationScenarios, TaskManagementScenarios, 
    ToolIntegrationScenarios, MemoryAndLearningScenarios
)


@dataclass
class E2ETestResult:
    """Represents the result of an E2E test execution."""
    test_name: str
    scenario_name: str
    status: str  # "passed", "failed", "skipped", "error"
    execution_time: float
    start_time: datetime
    end_time: datetime
    error_message: Optional[str] = None
    error_traceback: Optional[str] = None
    test_data: Optional[Dict[str, Any]] = None
    performance_metrics: Optional[Dict[str, Any]] = None


@dataclass
class E2ETestSuite:
    """Represents a suite of E2E tests."""
    suite_name: str
    tests: List[E2ETestResult]
    total_tests: int
    passed_tests: int
    failed_tests: int
    skipped_tests: int
    error_tests: int
    total_execution_time: float
    start_time: datetime
    end_time: datetime
    environment_config: E2ETestConfig


@dataclass
class E2ETestReport:
    """Comprehensive E2E test report."""
    report_id: str
    generated_at: datetime
    test_suites: List[E2ETestSuite]
    overall_summary: Dict[str, Any]
    performance_summary: Dict[str, Any]
    coverage_summary: Dict[str, Any]
    recommendations: List[str]


class E2ETestExecutor:
    """Executes E2E tests with comprehensive orchestration and reporting."""
    
    def __init__(self, config: E2ETestConfig):
        self.config = config
        self.environment = None
        self.test_results = []
        self.logger = self._setup_logging()
        
    def _setup_logging(self) -> logging.Logger:
        """Set up logging for E2E test execution."""
        logger = logging.getLogger('e2e_test_executor')
        logger.setLevel(getattr(logging, self.config.log_level.upper()))
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # Create file handler
        log_file = Path(self.config.test_data_path) / f"e2e_test_execution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        return logger
    
    async def setup_environment(self):
        """Set up the E2E test environment."""
        self.logger.info("Setting up E2E test environment...")
        
        from tests.e2e.e2e_test_environment import E2ETestEnvironment
        self.environment = E2ETestEnvironment(self.config)
        await self.environment.setup()
        
        self.logger.info("E2E test environment setup complete")
    
    async def teardown_environment(self):
        """Tear down the E2E test environment."""
        self.logger.info("Tearing down E2E test environment...")
        
        if self.environment:
            await self.environment.teardown()
        
        self.logger.info("E2E test environment teardown complete")
    
    async def execute_test_suite(self, suite_name: str, test_scenarios: List[Callable]) -> E2ETestSuite:
        """Execute a suite of E2E tests."""
        self.logger.info(f"Executing test suite: {suite_name}")
        
        suite_start_time = datetime.now()
        suite_tests = []
        
        if self.config.parallel_execution:
            # Execute tests in parallel
            suite_tests = await self._execute_tests_parallel(suite_name, test_scenarios)
        else:
            # Execute tests sequentially
            suite_tests = await self._execute_tests_sequential(suite_name, test_scenarios)
        
        suite_end_time = datetime.now()
        total_execution_time = (suite_end_time - suite_start_time).total_seconds()
        
        # Calculate suite statistics
        passed_tests = len([t for t in suite_tests if t.status == "passed"])
        failed_tests = len([t for t in suite_tests if t.status == "failed"])
        skipped_tests = len([t for t in suite_tests if t.status == "skipped"])
        error_tests = len([t for t in suite_tests if t.status == "error"])
        
        test_suite = E2ETestSuite(
            suite_name=suite_name,
            tests=suite_tests,
            total_tests=len(suite_tests),
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            skipped_tests=skipped_tests,
            error_tests=error_tests,
            total_execution_time=total_execution_time,
            start_time=suite_start_time,
            end_time=suite_end_time,
            environment_config=self.config
        )
        
        self.logger.info(f"Test suite {suite_name} completed: {passed_tests}/{len(suite_tests)} tests passed")
        return test_suite
    
    async def _execute_tests_parallel(self, suite_name: str, test_scenarios: List[Callable]) -> List[E2ETestResult]:
        """Execute tests in parallel."""
        self.logger.info(f"Executing {len(test_scenarios)} tests in parallel")
        
        # Create semaphore to limit concurrent tests
        semaphore = asyncio.Semaphore(self.config.max_parallel_tests)
        
        async def execute_single_test(test_scenario: Callable) -> E2ETestResult:
            async with semaphore:
                return await self._execute_single_test(suite_name, test_scenario)
        
        # Execute all tests concurrently
        tasks = [execute_single_test(scenario) for scenario in test_scenarios]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle any exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                error_result = E2ETestResult(
                    test_name=f"test_{i}",
                    scenario_name=test_scenarios[i].__name__,
                    status="error",
                    execution_time=0.0,
                    start_time=datetime.now(),
                    end_time=datetime.now(),
                    error_message=str(result),
                    error_traceback=traceback.format_exc()
                )
                processed_results.append(error_result)
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def _execute_tests_sequential(self, suite_name: str, test_scenarios: List[Callable]) -> List[E2ETestResult]:
        """Execute tests sequentially."""
        self.logger.info(f"Executing {len(test_scenarios)} tests sequentially")
        
        results = []
        for scenario in test_scenarios:
            result = await self._execute_single_test(suite_name, scenario)
            results.append(result)
        
        return results
    
    async def _execute_single_test(self, suite_name: str, test_scenario: Callable) -> E2ETestResult:
        """Execute a single test scenario."""
        test_name = test_scenario.__name__
        scenario_name = getattr(test_scenario, '__doc__', test_name)
        
        self.logger.info(f"Executing test: {test_name}")
        
        start_time = datetime.now()
        start_timestamp = time.time()
        
        try:
            # Execute the test scenario
            if asyncio.iscoroutinefunction(test_scenario):
                result = await test_scenario()
            else:
                result = test_scenario()
            
            end_time = datetime.now()
            execution_time = time.time() - start_timestamp
            
            # Check if test passed (result is not None and no exception was raised)
            status = "passed" if result is not None else "failed"
            
            test_result = E2ETestResult(
                test_name=test_name,
                scenario_name=scenario_name,
                status=status,
                execution_time=execution_time,
                start_time=start_time,
                end_time=end_time,
                test_data=result if isinstance(result, dict) else None,
                performance_metrics=self._collect_performance_metrics()
            )
            
            self.logger.info(f"Test {test_name} completed: {status} ({execution_time:.2f}s)")
            return test_result
            
        except Exception as e:
            end_time = datetime.now()
            execution_time = time.time() - start_timestamp
            
            test_result = E2ETestResult(
                test_name=test_name,
                scenario_name=scenario_name,
                status="failed",
                execution_time=execution_time,
                start_time=start_time,
                end_time=end_time,
                error_message=str(e),
                error_traceback=traceback.format_exc(),
                performance_metrics=self._collect_performance_metrics()
            )
            
            self.logger.error(f"Test {test_name} failed: {str(e)}")
            return test_result
    
    def _collect_performance_metrics(self) -> Dict[str, Any]:
        """Collect performance metrics for the test."""
        if self.environment:
            return self.environment.get_performance_report()
        return {}
    
    async def execute_comprehensive_test_suite(self) -> E2ETestReport:
        """Execute comprehensive E2E test suite."""
        self.logger.info("Starting comprehensive E2E test suite execution")
        
        report_start_time = datetime.now()
        test_suites = []
        
        # Set up environment
        await self.setup_environment()
        
        try:
            # Define test scenarios
            authentication_scenarios = self._get_authentication_scenarios()
            task_management_scenarios = self._get_task_management_scenarios()
            tool_integration_scenarios = self._get_tool_integration_scenarios()
            memory_learning_scenarios = self._get_memory_learning_scenarios()
            
            # Execute test suites
            if authentication_scenarios:
                auth_suite = await self.execute_test_suite("Authentication", authentication_scenarios)
                test_suites.append(auth_suite)
            
            if task_management_scenarios:
                task_suite = await self.execute_test_suite("Task Management", task_management_scenarios)
                test_suites.append(task_suite)
            
            if tool_integration_scenarios:
                tool_suite = await self.execute_test_suite("Tool Integration", tool_integration_scenarios)
                test_suites.append(tool_suite)
            
            if memory_learning_scenarios:
                memory_suite = await self.execute_test_suite("Memory & Learning", memory_learning_scenarios)
                test_suites.append(memory_suite)
            
            # Generate comprehensive report
            report = await self._generate_comprehensive_report(test_suites, report_start_time)
            
            self.logger.info("Comprehensive E2E test suite execution completed")
            return report
            
        finally:
            # Always teardown environment
            await self.teardown_environment()
    
    def _get_authentication_scenarios(self) -> List[Callable]:
        """Get authentication test scenarios."""
        if not self.environment:
            return []
        
        auth_scenarios = AuthenticationScenarios(self.environment)
        return [
            auth_scenarios.complete_user_registration_flow,
            auth_scenarios.user_login_and_session_management,
            auth_scenarios.password_reset_flow
        ]
    
    def _get_task_management_scenarios(self) -> List[Callable]:
        """Get task management test scenarios."""
        if not self.environment:
            return []
        
        task_scenarios = TaskManagementScenarios(self.environment)
        return [
            task_scenarios.complete_task_creation_and_execution,
            task_scenarios.task_scheduling_and_reminders,
            task_scenarios.task_error_handling_and_recovery
        ]
    
    def _get_tool_integration_scenarios(self) -> List[Callable]:
        """Get tool integration test scenarios."""
        if not self.environment:
            return []
        
        tool_scenarios = ToolIntegrationScenarios(self.environment)
        return [
            tool_scenarios.youtube_tool_integration,
            tool_scenarios.notion_integration,
            tool_scenarios.email_tool_integration
        ]
    
    def _get_memory_learning_scenarios(self) -> List[Callable]:
        """Get memory and learning test scenarios."""
        if not self.environment:
            return []
        
        memory_scenarios = MemoryAndLearningScenarios(self.environment)
        return [
            memory_scenarios.memory_storage_and_retrieval,
            memory_scenarios.learning_and_adaptation
        ]
    
    async def _generate_comprehensive_report(self, test_suites: List[E2ETestSuite], start_time: datetime) -> E2ETestReport:
        """Generate comprehensive E2E test report."""
        report_id = f"e2e_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Calculate overall summary
        total_tests = sum(suite.total_tests for suite in test_suites)
        total_passed = sum(suite.passed_tests for suite in test_suites)
        total_failed = sum(suite.failed_tests for suite in test_suites)
        total_skipped = sum(suite.skipped_tests for suite in test_suites)
        total_errors = sum(suite.error_tests for suite in test_suites)
        total_execution_time = sum(suite.total_execution_time for suite in test_suites)
        
        overall_summary = {
            'total_tests': total_tests,
            'passed_tests': total_passed,
            'failed_tests': total_failed,
            'skipped_tests': total_skipped,
            'error_tests': total_errors,
            'pass_rate': (total_passed / total_tests * 100) if total_tests > 0 else 0,
            'total_execution_time': total_execution_time,
            'average_execution_time': total_execution_time / total_tests if total_tests > 0 else 0
        }
        
        # Calculate performance summary
        all_tests = []
        for suite in test_suites:
            all_tests.extend(suite.tests)
        
        execution_times = [test.execution_time for test in all_tests if test.execution_time > 0]
        performance_summary = {
            'fastest_test': min(execution_times) if execution_times else 0,
            'slowest_test': max(execution_times) if execution_times else 0,
            'average_execution_time': sum(execution_times) / len(execution_times) if execution_times else 0,
            'total_execution_time': sum(execution_times),
            'tests_over_threshold': len([t for t in execution_times if t > 30.0])  # 30 second threshold
        }
        
        # Calculate coverage summary
        scenario_coverage = {
            'authentication_scenarios': len([s for s in test_suites if s.suite_name == "Authentication"]),
            'task_management_scenarios': len([s for s in test_suites if s.suite_name == "Task Management"]),
            'tool_integration_scenarios': len([s for s in test_suites if s.suite_name == "Tool Integration"]),
            'memory_learning_scenarios': len([s for s in test_suites if s.suite_name == "Memory & Learning"])
        }
        
        coverage_summary = {
            'total_scenario_categories': len(scenario_coverage),
            'scenarios_executed': sum(scenario_coverage.values()),
            'scenario_coverage': scenario_coverage,
            'coverage_percentage': (sum(scenario_coverage.values()) / len(scenario_coverage) * 100) if scenario_coverage else 0
        }
        
        # Generate recommendations
        recommendations = self._generate_recommendations(overall_summary, performance_summary, test_suites)
        
        report = E2ETestReport(
            report_id=report_id,
            generated_at=datetime.now(),
            test_suites=test_suites,
            overall_summary=overall_summary,
            performance_summary=performance_summary,
            coverage_summary=coverage_summary,
            recommendations=recommendations
        )
        
        # Save report
        await self._save_report(report)
        
        return report
    
    def _generate_recommendations(self, overall_summary: Dict[str, Any], 
                                performance_summary: Dict[str, Any], 
                                test_suites: List[E2ETestSuite]) -> List[str]:
        """Generate recommendations based on test results."""
        recommendations = []
        
        # Pass rate recommendations
        if overall_summary['pass_rate'] < 90:
            recommendations.append(f"🚨 Pass rate is {overall_summary['pass_rate']:.1f}%. Focus on fixing failing tests.")
        elif overall_summary['pass_rate'] < 95:
            recommendations.append(f"⚠️  Pass rate is {overall_summary['pass_rate']:.1f}%. Consider improving test reliability.")
        
        # Performance recommendations
        if performance_summary['tests_over_threshold'] > 0:
            recommendations.append(f"⏱️  {performance_summary['tests_over_threshold']} tests exceed 30-second threshold. Consider optimization.")
        
        if performance_summary['average_execution_time'] > 10:
            recommendations.append("🐌 Average test execution time is high. Consider parallel execution or test optimization.")
        
        # Coverage recommendations
        if overall_summary['total_tests'] < 10:
            recommendations.append("📊 Test coverage is low. Consider adding more test scenarios.")
        
        # Suite-specific recommendations
        for suite in test_suites:
            if suite.failed_tests > 0:
                recommendations.append(f"🔧 {suite.suite_name} suite has {suite.failed_tests} failing tests. Review and fix.")
        
        # General recommendations
        if not recommendations:
            recommendations.append("✅ All tests are performing well. Continue monitoring and maintain quality.")
        
        return recommendations
    
    async def _save_report(self, report: E2ETestReport):
        """Save the test report to file."""
        report_file = Path(self.config.test_data_path) / f"{report.report_id}.json"
        report_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert report to JSON-serializable format
        report_data = {
            'report_id': report.report_id,
            'generated_at': report.generated_at.isoformat(),
            'test_suites': [asdict(suite) for suite in report.test_suites],
            'overall_summary': report.overall_summary,
            'performance_summary': report.performance_summary,
            'coverage_summary': report.coverage_summary,
            'recommendations': report.recommendations
        }
        
        # Convert datetime objects in test suites
        for suite_data in report_data['test_suites']:
            suite_data['start_time'] = suite_data['start_time'].isoformat()
            suite_data['end_time'] = suite_data['end_time'].isoformat()
            for test_data in suite_data['tests']:
                test_data['start_time'] = test_data['start_time'].isoformat()
                test_data['end_time'] = test_data['end_time'].isoformat()
        
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        self.logger.info(f"Test report saved to: {report_file}")
    
    def print_report_summary(self, report: E2ETestReport):
        """Print a summary of the test report."""
        print("\n" + "="*80)
        print("E2E TEST EXECUTION REPORT")
        print("="*80)
        print(f"Report ID: {report.report_id}")
        print(f"Generated: {report.generated_at.strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Overall Summary
        print("OVERALL SUMMARY")
        print("-" * 40)
        print(f"Total Tests: {report.overall_summary['total_tests']}")
        print(f"Passed: {report.overall_summary['passed_tests']}")
        print(f"Failed: {report.overall_summary['failed_tests']}")
        print(f"Skipped: {report.overall_summary['skipped_tests']}")
        print(f"Errors: {report.overall_summary['error_tests']}")
        print(f"Pass Rate: {report.overall_summary['pass_rate']:.1f}%")
        print(f"Total Execution Time: {report.overall_summary['total_execution_time']:.2f}s")
        print()
        
        # Performance Summary
        print("PERFORMANCE SUMMARY")
        print("-" * 40)
        print(f"Fastest Test: {report.performance_summary['fastest_test']:.2f}s")
        print(f"Slowest Test: {report.performance_summary['slowest_test']:.2f}s")
        print(f"Average Execution Time: {report.performance_summary['average_execution_time']:.2f}s")
        print(f"Tests Over 30s: {report.performance_summary['tests_over_threshold']}")
        print()
        
        # Coverage Summary
        print("COVERAGE SUMMARY")
        print("-" * 40)
        print(f"Scenario Categories: {report.coverage_summary['total_scenario_categories']}")
        print(f"Scenarios Executed: {report.coverage_summary['scenarios_executed']}")
        print(f"Coverage: {report.coverage_summary['coverage_percentage']:.1f}%")
        print()
        
        # Test Suites
        print("TEST SUITES")
        print("-" * 40)
        for suite in report.test_suites:
            print(f"{suite.suite_name}:")
            print(f"  Tests: {suite.total_tests}")
            print(f"  Passed: {suite.passed_tests}")
            print(f"  Failed: {suite.failed_tests}")
            print(f"  Execution Time: {suite.total_execution_time:.2f}s")
            print()
        
        # Recommendations
        print("RECOMMENDATIONS")
        print("-" * 40)
        for i, recommendation in enumerate(report.recommendations, 1):
            print(f"{i}. {recommendation}")
        print()
        
        print("="*80)


# Global executor instance
_e2e_executor = None


def get_e2e_executor(config: E2ETestConfig) -> E2ETestExecutor:
    """Get the global E2E test executor."""
    global _e2e_executor
    if _e2e_executor is None:
        _e2e_executor = E2ETestExecutor(config)
    return _e2e_executor


async def run_e2e_tests(config: E2ETestConfig) -> E2ETestReport:
    """Run comprehensive E2E tests."""
    executor = get_e2e_executor(config)
    report = await executor.execute_comprehensive_test_suite()
    executor.print_report_summary(report)
    return report


# Pytest integration
@pytest.fixture(scope="session")
async def e2e_test_executor():
    """Pytest fixture for E2E test executor."""
    config = E2ETestConfig(
        environment="development",
        database_url="sqlite:///e2e_test.db",
        external_services_mocked=True,
        test_data_path="tests/e2e/test_data",
        log_level="INFO",
        timeout_seconds=30,
        retry_attempts=3,
        parallel_execution=True,
        max_parallel_tests=4
    )
    
    executor = E2ETestExecutor(config)
    await executor.setup_environment()
    yield executor
    await executor.teardown_environment()


@pytest.fixture
async def e2e_test_report(e2e_test_executor):
    """Pytest fixture for E2E test report."""
    report = await e2e_test_executor.execute_comprehensive_test_suite()
    return report
