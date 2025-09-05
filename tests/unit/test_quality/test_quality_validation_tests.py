"""
Unit tests for quality validation system.

This module tests all quality validation components including
execution time validation, reliability validation, mock realism validation, and error coverage validation.
"""

import pytest
import tempfile
import time
from pathlib import Path
from unittest.mock import Mock, MagicMock, AsyncMock, patch
from datetime import datetime

from tests.quality.test_execution_time_validator import (
    ExecutionTimeValidator, ExecutionTimeMetrics, SuiteMetrics,
    get_execution_time_validator, measure_test_time, validate_test_execution_times,
    generate_execution_time_report
)

from tests.quality.test_reliability_validator import (
    ReliabilityValidator, RunResult, ReliabilityMetrics,
    get_reliability_validator, record_test_run, validate_test_reliability,
    generate_reliability_report
)

from tests.quality.mock_realism_validator import (
    MockRealismValidator, MockBehaviorAnalysis, MockRealismScore,
    get_mock_realism_validator, analyze_mock_behavior, calculate_mock_realism_score,
    validate_mock_realism, generate_mock_quality_report
)

from tests.quality.error_coverage_validator import (
    ErrorCoverageValidator, ErrorScenario, ErrorCoverageMetrics,
    get_error_coverage_validator, scan_file_for_errors, analyze_module_error_coverage,
    validate_error_coverage, generate_error_coverage_report
)


class TestExecutionTimeValidator:
    """Test TestExecutionTimeValidator class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.validator = ExecutionTimeValidator()

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_initialization(self):
        """Test TestExecutionTimeValidator initialization."""
        assert isinstance(self.validator.config, dict)
        assert "thresholds" in self.validator.config
        assert "unit" in self.validator.config["thresholds"]
        assert isinstance(self.validator.metrics_history, list)
        assert isinstance(self.validator.current_metrics, list)

    def test_measure_test_execution_time(self):
        """Test measuring test execution time."""
        def test_func():
            time.sleep(0.1)
            return True
        
        metrics = self.validator.measure_test_execution_time(test_func, "test_function", "unit")
        
        assert metrics.test_name == "test_function"
        assert metrics.execution_time >= 0.1
        assert metrics.status == "passed"
        assert metrics.category == "unit"
        assert metrics.within_threshold is True

    def test_measure_test_execution_time_with_failure(self):
        """Test measuring test execution time with failure."""
        def test_func():
            raise ValueError("Test error")
        
        metrics = self.validator.measure_test_execution_time(test_func, "test_function", "unit")
        
        assert metrics.test_name == "test_function"
        assert metrics.status == "failed"
        assert metrics.category == "unit"

    def test_determine_complexity(self):
        """Test determining test complexity."""
        # Test simple complexity
        complexity = self.validator._determine_complexity(0.1, "unit")
        assert complexity == "simple"
        
        # Test medium complexity
        complexity = self.validator._determine_complexity(0.5, "unit")
        assert complexity == "medium"
        
        # Test complex complexity
        complexity = self.validator._determine_complexity(1.5, "unit")
        assert complexity == "complex"

    def test_analyze_test_suite_performance(self):
        """Test analyzing test suite performance."""
        # Add some test metrics
        self.validator.current_metrics = [
            ExecutionTimeMetrics(
                test_name="test1",
                execution_time=0.5,
                timestamp=datetime.now(),
                status="passed",
                category="unit",
                complexity="medium",
                timeout_threshold=1.0,
                within_threshold=True
            ),
            ExecutionTimeMetrics(
                test_name="test2",
                execution_time=1.5,
                timestamp=datetime.now(),
                status="passed",
                category="unit",
                complexity="complex",
                timeout_threshold=1.0,
                within_threshold=False
            )
        ]
        
        suite_metrics = self.validator.analyze_test_suite_performance("test_suite")
        
        assert suite_metrics.suite_name == "test_suite"
        assert suite_metrics.total_tests == 2
        assert suite_metrics.total_execution_time == 2.0
        assert suite_metrics.average_execution_time == 1.0
        assert len(suite_metrics.timeout_violations) == 1

    def test_validate_execution_times(self):
        """Test validating execution times."""
        # Add some test metrics
        self.validator.current_metrics = [
            ExecutionTimeMetrics(
                test_name="test1",
                execution_time=0.5,
                timestamp=datetime.now(),
                status="passed",
                category="unit",
                complexity="medium",
                timeout_threshold=1.0,
                within_threshold=True
            ),
            ExecutionTimeMetrics(
                test_name="test2",
                execution_time=1.5,
                timestamp=datetime.now(),
                status="passed",
                category="unit",
                complexity="complex",
                timeout_threshold=1.0,
                within_threshold=False
            )
        ]
        
        validation = self.validator.validate_execution_times()
        
        assert "overall_status" in validation
        assert "violations" in validation
        assert "warnings" in validation
        assert "recommendations" in validation
        assert "summary" in validation

    def test_generate_execution_time_report(self):
        """Test generating execution time report."""
        # Add some test metrics
        self.validator.current_metrics = [
            ExecutionTimeMetrics(
                test_name="test1",
                execution_time=0.5,
                timestamp=datetime.now(),
                status="passed",
                category="unit",
                complexity="medium",
                timeout_threshold=1.0,
                within_threshold=True
            )
        ]
        
        report = self.validator.generate_execution_time_report()
        
        assert "Test Execution Time Validation Report" in report
        assert "0.5" in report  # The execution time should be in the report


class TestReliabilityValidator:
    """Test TestReliabilityValidator class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.validator = ReliabilityValidator()

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_initialization(self):
        """Test TestReliabilityValidator initialization."""
        assert isinstance(self.validator.config, dict)
        assert "thresholds" in self.validator.config
        assert "flakiness_threshold" in self.validator.config["thresholds"]
        assert isinstance(self.validator.test_history, dict)
        assert isinstance(self.validator.suite_history, list)

    def test_record_test_run(self):
        """Test recording test run."""
        result = self.validator.record_test_run("test_function", "passed", 0.5)
        
        assert result.test_name == "test_function"
        assert result.status == "passed"
        assert result.execution_time == 0.5
        assert "test_function" in self.validator.test_history

    def test_analyze_test_reliability(self):
        """Test analyzing test reliability."""
        # Record some test runs
        self.validator.record_test_run("test_function", "passed", 0.5)
        self.validator.record_test_run("test_function", "passed", 0.6)
        self.validator.record_test_run("test_function", "failed", 0.7)
        
        metrics = self.validator.analyze_test_reliability("test_function")
        
        assert metrics.test_name == "test_function"
        assert metrics.total_runs == 3
        assert metrics.passed_runs == 2
        assert metrics.failed_runs == 1
        assert metrics.success_rate == 2/3
        assert metrics.failure_rate == 1/3

    def test_calculate_flakiness_score(self):
        """Test calculating flakiness score."""
        # Create mock test runs
        runs = [
            RunResult("test", datetime.now(), "passed", 0.5),
            RunResult("test", datetime.now(), "failed", 0.6),
            RunResult("test", datetime.now(), "passed", 0.7),
            RunResult("test", datetime.now(), "failed", 0.8)
        ]
        
        flakiness_score = self.validator._calculate_flakiness_score(runs)
        
        assert 0.0 <= flakiness_score <= 1.0
        assert flakiness_score > 0.0  # Should be flaky due to status changes

    def test_validate_test_reliability(self):
        """Test validating test reliability."""
        # Record some test runs
        self.validator.record_test_run("test_function", "passed", 0.5)
        self.validator.record_test_run("test_function", "failed", 0.6)
        
        validation = self.validator.validate_test_reliability()
        
        assert "overall_status" in validation
        assert "alerts" in validation
        assert "warnings" in validation
        assert "recommendations" in validation
        assert "summary" in validation

    def test_generate_reliability_report(self):
        """Test generating reliability report."""
        # Record some test runs
        self.validator.record_test_run("test_function", "passed", 0.5)
        self.validator.record_test_run("test_function", "failed", 0.6)
        
        report = self.validator.generate_reliability_report()
        
        assert "Test Reliability Validation Report" in report
        assert "test_function" in report


class TestMockRealismValidator:
    """Test MockRealismValidator class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.validator = MockRealismValidator()

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_initialization(self):
        """Test MockRealismValidator initialization."""
        assert isinstance(self.validator.config, dict)
        assert "scoring_weights" in self.validator.config
        assert "realism_thresholds" in self.validator.config
        assert isinstance(self.validator.mock_analyses, dict)
        assert isinstance(self.validator.mock_scores, dict)

    def test_analyze_mock_behavior(self):
        """Test analyzing mock behavior."""
        mock = Mock()
        mock.return_value = "test_result"
        mock.side_effect = None
        mock.call_count = 0
        
        # Call the mock
        result = mock("arg1", "arg2", key="value")
        
        analysis = self.validator.analyze_mock_behavior(mock, "test_mock", "generic")
        
        assert analysis.mock_name == "test_mock"
        assert analysis.mock_type == "generic"
        assert analysis.call_count == 1
        assert len(analysis.call_args) == 1
        assert "test_result" in analysis.return_values

    def test_calculate_realism_score(self):
        """Test calculating realism score."""
        # First analyze mock behavior
        mock = Mock()
        mock.return_value = "test_result"
        mock("arg1", "arg2")
        
        self.validator.analyze_mock_behavior(mock, "test_mock", "generic")
        
        score = self.validator.calculate_realism_score("test_mock", "generic")
        
        assert score.mock_name == "test_mock"
        assert 0.0 <= score.overall_score <= 1.0
        assert 0.0 <= score.behavior_score <= 1.0
        assert 0.0 <= score.data_score <= 1.0
        assert 0.0 <= score.interaction_score <= 1.0
        assert 0.0 <= score.error_handling_score <= 1.0
        assert 0.0 <= score.performance_score <= 1.0

    def test_calculate_behavior_score(self):
        """Test calculating behavior score."""
        analysis = MockBehaviorAnalysis(
            mock_name="test_mock",
            mock_type="generic",
            call_count=1,
            call_args=[("arg1", "arg2")],
            call_kwargs=[{"key": "value"}],
            return_values=["test_result"],
            side_effects=[],
            exceptions_raised=[],
            async_calls=0,
            sync_calls=1
        )
        
        score = self.validator._calculate_behavior_score(analysis, "generic")
        
        assert 0.0 <= score <= 1.0

    def test_validate_mock_realism(self):
        """Test validating mock realism."""
        # First analyze and score a mock
        mock = Mock()
        mock.return_value = "test_result"
        mock("arg1", "arg2")
        
        self.validator.analyze_mock_behavior(mock, "test_mock", "generic")
        self.validator.calculate_realism_score("test_mock", "generic")
        
        validation = self.validator.validate_mock_realism()
        
        assert "overall_status" in validation
        assert "issues" in validation
        assert "recommendations" in validation
        assert "summary" in validation

    def test_generate_mock_quality_report(self):
        """Test generating mock quality report."""
        # First analyze and score a mock
        mock = Mock()
        mock.return_value = "test_result"
        mock("arg1", "arg2")
        
        self.validator.analyze_mock_behavior(mock, "test_mock", "generic")
        self.validator.calculate_realism_score("test_mock", "generic")
        
        report = self.validator.generate_mock_quality_report()
        
        assert "Mock Realism Validation Report" in report
        assert "test_mock" in report


class TestErrorCoverageValidator:
    """Test ErrorCoverageValidator class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.validator = ErrorCoverageValidator()

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_initialization(self):
        """Test ErrorCoverageValidator initialization."""
        assert isinstance(self.validator.config, dict)
        assert "error_patterns" in self.validator.config
        assert "coverage_thresholds" in self.validator.config
        assert isinstance(self.validator.error_scenarios, list)
        assert isinstance(self.validator.coverage_metrics, dict)

    def test_scan_file_for_errors(self):
        """Test scanning file for errors."""
        # Create a temporary test file
        test_file = Path(self.temp_dir) / "test_file.py"
        test_file.write_text("""
def test_function():
    try:
        result = risky_operation()
    except ValueError as e:
        raise RuntimeError("Something went wrong")
    
    if result is None:
        raise AttributeError("Result is None")
    
    return result
""")
        
        error_scenarios = self.validator.scan_file_for_errors(str(test_file))
        
        assert len(error_scenarios) > 0
        assert any(e.error_type == "RuntimeError" for e in error_scenarios)
        assert any(e.error_type == "AttributeError" for e in error_scenarios)

    def test_analyze_module_error_coverage(self):
        """Test analyzing module error coverage."""
        # Create a temporary test file
        test_file = Path(self.temp_dir) / "test_module.py"
        test_file.write_text("""
def test_function():
    try:
        result = risky_operation()
    except ValueError as e:
        raise RuntimeError("Something went wrong")
    
    if result is None:
        raise AttributeError("Result is None")
    
    return result
""")
        
        metrics = self.validator.analyze_module_error_coverage(str(test_file))
        
        assert metrics.module_name == str(test_file)
        assert metrics.total_errors > 0
        assert metrics.coverage_percentage >= 0.0
        assert metrics.coverage_percentage <= 100.0

    def test_validate_error_coverage(self):
        """Test validating error coverage."""
        # Create a temporary test file and analyze it
        test_file = Path(self.temp_dir) / "test_module.py"
        test_file.write_text("""
def test_function():
    try:
        result = risky_operation()
    except ValueError as e:
        raise RuntimeError("Something went wrong")
    
    if result is None:
        raise AttributeError("Result is None")
    
    return result
""")
        
        self.validator.analyze_module_error_coverage(str(test_file))
        
        validation = self.validator.validate_error_coverage()
        
        assert "overall_status" in validation
        assert "violations" in validation
        assert "warnings" in validation
        assert "recommendations" in validation
        assert "summary" in validation

    def test_generate_error_coverage_report(self):
        """Test generating error coverage report."""
        # Create a temporary test file and analyze it
        test_file = Path(self.temp_dir) / "test_module.py"
        test_file.write_text("""
def test_function():
    try:
        result = risky_operation()
    except ValueError as e:
        raise RuntimeError("Something went wrong")
    
    if result is None:
        raise AttributeError("Result is None")
    
    return result
""")
        
        self.validator.analyze_module_error_coverage(str(test_file))
        
        report = self.validator.generate_error_coverage_report()
        
        assert "Error Coverage Validation Report" in report
        assert "test_module.py" in report


class TestGlobalFunctions:
    """Test global quality validation functions."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_get_execution_time_validator(self):
        """Test getting global execution time validator."""
        validator = get_execution_time_validator()
        assert isinstance(validator, ExecutionTimeValidator)

    def test_get_reliability_validator(self):
        """Test getting global reliability validator."""
        validator = get_reliability_validator()
        assert isinstance(validator, ReliabilityValidator)

    def test_get_mock_realism_validator(self):
        """Test getting global mock realism validator."""
        validator = get_mock_realism_validator()
        assert isinstance(validator, MockRealismValidator)

    def test_get_error_coverage_validator(self):
        """Test getting global error coverage validator."""
        validator = get_error_coverage_validator()
        assert isinstance(validator, ErrorCoverageValidator)

    def test_measure_test_time(self):
        """Test global measure_test_time function."""
        def test_func():
            return True
        
        metrics = measure_test_time(test_func, "test_function", "unit")
        
        assert metrics.test_name == "test_function"
        assert metrics.status == "passed"
        assert metrics.category == "unit"

    def test_record_test_run(self):
        """Test global record_test_run function."""
        result = record_test_run("test_function", "passed", 0.5)
        
        assert result.test_name == "test_function"
        assert result.status == "passed"
        assert result.execution_time == 0.5

    def test_analyze_mock_behavior(self):
        """Test global analyze_mock_behavior function."""
        mock = Mock()
        mock.return_value = "test_result"
        mock("arg1", "arg2")
        
        analysis = analyze_mock_behavior(mock, "test_mock", "generic")
        
        assert analysis.mock_name == "test_mock"
        assert analysis.mock_type == "generic"
        assert analysis.call_count == 1

    def test_scan_file_for_errors(self):
        """Test global scan_file_for_errors function."""
        # Create a temporary test file
        test_file = Path(self.temp_dir) / "test_file.py"
        test_file.write_text("""
def test_function():
    raise ValueError("Test error")
""")
        
        error_scenarios = scan_file_for_errors(str(test_file))
        
        assert len(error_scenarios) > 0
        assert any(e.error_type == "ValueError" for e in error_scenarios)


class TestIntegration:
    """Test integration of all quality validation components."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_comprehensive_quality_validation_workflow(self):
        """Test comprehensive quality validation workflow."""
        # Test execution time validation
        def test_func():
            time.sleep(0.1)
            return True
        
        execution_metrics = measure_test_time(test_func, "test_function", "unit")
        assert execution_metrics.test_name == "test_function"
        
        # Test reliability validation
        reliability_result = record_test_run("test_function", "passed", 0.5)
        assert reliability_result.test_name == "test_function"
        
        # Test mock realism validation
        mock = Mock()
        mock.return_value = "test_result"
        mock("arg1", "arg2")
        
        mock_analysis = analyze_mock_behavior(mock, "test_mock", "generic")
        assert mock_analysis.mock_name == "test_mock"
        
        # Calculate mock realism score to ensure data is available for report
        from tests.quality.mock_realism_validator import calculate_mock_realism_score
        mock_score = calculate_mock_realism_score("test_mock", "generic")
        assert mock_score.mock_name == "test_mock"
        
        # Test error coverage validation
        test_file = Path(self.temp_dir) / "test_file.py"
        test_file.write_text("""
def test_function():
    raise ValueError("Test error")
""")
        
        error_scenarios = scan_file_for_errors(str(test_file))
        assert len(error_scenarios) > 0
        
        # Analyze module error coverage to ensure data is available for report
        from tests.quality.error_coverage_validator import analyze_module_error_coverage
        error_metrics = analyze_module_error_coverage(str(test_file))
        assert error_metrics.module_name == str(test_file)
        
        # Test validation functions
        execution_validation = validate_test_execution_times()
        assert "overall_status" in execution_validation
        
        reliability_validation = validate_test_reliability()
        assert "overall_status" in reliability_validation
        
        mock_validation = validate_mock_realism()
        assert "overall_status" in mock_validation
        
        error_validation = validate_error_coverage()
        assert "overall_status" in error_validation
        
        # Test report generation
        execution_report = generate_execution_time_report()
        assert "Test Execution Time Validation Report" in execution_report
        
        reliability_report = generate_reliability_report()
        assert "Test Reliability Validation Report" in reliability_report
        
        mock_report = generate_mock_quality_report()
        assert "Mock Realism Validation Report" in mock_report
        
        error_report = generate_error_coverage_report()
        assert "Error Coverage Validation Report" in error_report
        
        # Verify all components work together
        assert True  # Test completed successfully
