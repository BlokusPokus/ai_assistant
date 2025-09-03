# Test Execution Guide

## Overview

This guide provides comprehensive instructions for executing tests in the Personal Assistant application, including different test types, execution options, and troubleshooting.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Test Execution Commands](#test-execution-commands)
3. [Test Categories](#test-categories)
4. [Coverage Analysis](#coverage-analysis)
5. [Performance Testing](#performance-testing)
6. [Quality Validation](#quality-validation)
7. [Parallel Execution](#parallel-execution)
8. [Continuous Integration](#continuous-integration)
9. [Troubleshooting](#troubleshooting)
10. [Best Practices](#best-practices)

## Quick Start

### Prerequisites

1. **Activate Virtual Environment**:

   ```bash
   source venv_personal_assistant/bin/activate
   ```

2. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   pip install -r requirements-test.txt
   ```

3. **Verify Installation**:
   ```bash
   python -m pytest --version
   ```

### Basic Test Execution

```bash
# Run all tests
python -m pytest

# Run tests with verbose output
python -m pytest -v

# Run tests with coverage
python -m pytest --cov=src --cov-report=html

# Run specific test file
python -m pytest tests/unit/test_auth/test_password_service.py

# Run specific test function
python -m pytest tests/unit/test_auth/test_password_service.py::test_hash_password
```

## Test Execution Commands

### Basic Commands

```bash
# Run all tests
python -m pytest

# Run with verbose output
python -m pytest -v

# Run with detailed output
python -m pytest -v -s

# Run with full traceback
python -m pytest --tb=long

# Run with short traceback
python -m pytest --tb=short

# Run with no traceback
python -m pytest --tb=no
```

### Coverage Commands

```bash
# Run with coverage
python -m pytest --cov=src

# Run with coverage and HTML report
python -m pytest --cov=src --cov-report=html

# Run with coverage and terminal report
python -m pytest --cov=src --cov-report=term-missing

# Run with coverage and JSON report
python -m pytest --cov=src --cov-report=json

# Run with coverage and XML report
python -m pytest --cov=src --cov-report=xml
```

### Performance Commands

```bash
# Run performance tests
python -m pytest tests/unit/test_performance/ -v

# Run with benchmarking
python -m pytest --benchmark-only

# Run with benchmark comparison
python -m pytest --benchmark-compare

# Run with benchmark histogram
python -m pytest --benchmark-histogram
```

### Parallel Execution

```bash
# Run tests in parallel (auto-detect CPU cores)
python -m pytest -n auto

# Run tests in parallel (specific number of workers)
python -m pytest -n 4

# Run tests in parallel with load balancing
python -m pytest -n auto --dist=load
```

### Quality Validation

```bash
# Run quality validation tests
python -m pytest tests/unit/test_quality/ -v

# Run coverage analysis
python -m pytest tests/coverage/ -v

# Run mock validation
python -m pytest tests/unit/test_mocks/ -v
```

## Test Categories

### Unit Tests

```bash
# Run all unit tests
python -m pytest tests/unit/

# Run specific unit test category
python -m pytest tests/unit/test_auth/
python -m pytest tests/unit/test_database/
python -m pytest tests/unit/test_tools/
python -m pytest tests/unit/test_utilities/
```

### Integration Tests

```bash
# Run all integration tests
python -m pytest tests/integration/

# Run specific integration test
python -m pytest tests/integration/test_api_integration.py
```

### End-to-End Tests

```bash
# Run all E2E tests
python -m pytest tests/e2e/

# Run specific E2E test
python -m pytest tests/e2e/test_user_workflow.py
```

### Performance Tests

```bash
# Run performance tests
python -m pytest tests/unit/test_performance/

# Run with performance monitoring
python -m pytest tests/unit/test_performance/ --benchmark-only
```

### Quality Validation Tests

```bash
# Run quality validation tests
python -m pytest tests/unit/test_quality/

# Run coverage analysis tests
python -m pytest tests/coverage/

# Run mock validation tests
python -m pytest tests/unit/test_mocks/
```

## Coverage Analysis

### Basic Coverage

```bash
# Run coverage analysis
python -m pytest --cov=src --cov-report=html --cov-report=term-missing

# Run coverage for specific module
python -m pytest --cov=src.personal_assistant.auth --cov-report=html

# Run coverage with threshold
python -m pytest --cov=src --cov-fail-under=80
```

### Advanced Coverage

```bash
# Run coverage with branch analysis
python -m pytest --cov=src --cov-branch --cov-report=html

# Run coverage with source analysis
python -m pytest --cov=src --cov-report=html --cov-report=term-missing --cov-report=xml

# Run coverage analysis tests
python -m pytest tests/coverage/ -v
```

### Coverage Reports

```bash
# Generate HTML coverage report
python -m pytest --cov=src --cov-report=html
open htmlcov/index.html

# Generate JSON coverage report
python -m pytest --cov=src --cov-report=json
cat coverage.json

# Generate XML coverage report
python -m pytest --cov=src --cov-report=xml
cat coverage.xml
```

## Performance Testing

### Basic Performance

```bash
# Run performance tests
python -m pytest tests/unit/test_performance/ -v

# Run with timing
python -m pytest tests/unit/test_performance/ -v --durations=10

# Run slowest tests first
python -m pytest tests/unit/test_performance/ -v --durations=0
```

### Benchmarking

```bash
# Run benchmarks
python -m pytest --benchmark-only

# Run benchmarks with comparison
python -m pytest --benchmark-compare

# Run benchmarks with histogram
python -m pytest --benchmark-histogram

# Run benchmarks with statistics
python -m pytest --benchmark-stats
```

### Performance Monitoring

```bash
# Run with performance monitoring
python -m pytest tests/unit/test_performance/ --benchmark-only -v

# Run with memory profiling
python -m pytest tests/unit/test_performance/ --profile

# Run with CPU profiling
python -m pytest tests/unit/test_performance/ --profile-svg
```

## Quality Validation

### Execution Time Validation

```bash
# Run execution time validation
python -m pytest tests/unit/test_quality/test_quality_validation_tests.py::TestTestExecutionTimeValidator -v

# Run with timing analysis
python -m pytest tests/unit/test_quality/ -v --durations=10
```

### Reliability Validation

```bash
# Run reliability validation
python -m pytest tests/unit/test_quality/test_quality_validation_tests.py::TestTestReliabilityValidator -v

# Run with repeat testing
python -m pytest tests/unit/test_quality/ -v --count=5
```

### Mock Realism Validation

```bash
# Run mock realism validation
python -m pytest tests/unit/test_quality/test_quality_validation_tests.py::TestMockRealismValidator -v

# Run mock validation tests
python -m pytest tests/unit/test_mocks/ -v
```

### Error Coverage Validation

```bash
# Run error coverage validation
python -m pytest tests/unit/test_quality/test_quality_validation_tests.py::TestErrorCoverageValidator -v

# Run error scenario tests
python -m pytest tests/unit/test_quality/ -v -k "error"
```

## Parallel Execution

### Basic Parallel Execution

```bash
# Run tests in parallel (auto-detect)
python -m pytest -n auto

# Run tests in parallel (4 workers)
python -m pytest -n 4

# Run tests in parallel (8 workers)
python -m pytest -n 8
```

### Advanced Parallel Execution

```bash
# Run with load balancing
python -m pytest -n auto --dist=load

# Run with work stealing
python -m pytest -n auto --dist=worksteal

# Run with specific distribution
python -m pytest -n auto --dist=each
```

### Parallel Execution with Coverage

```bash
# Run parallel tests with coverage
python -m pytest -n auto --cov=src --cov-report=html

# Run parallel tests with coverage and threshold
python -m pytest -n auto --cov=src --cov-fail-under=80
```

## Continuous Integration

### GitHub Actions

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.11
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-test.txt
      - name: Run tests
        run: python -m pytest --cov=src --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v1
```

### Local CI Simulation

```bash
# Run full test suite (CI simulation)
python -m pytest --cov=src --cov-report=xml --cov-fail-under=80 -n auto

# Run with quality validation
python -m pytest --cov=src --cov-report=xml --cov-fail-under=80 -n auto tests/unit/test_quality/ -v

# Run with performance validation
python -m pytest --cov=src --cov-report=xml --cov-fail-under=80 -n auto tests/unit/test_performance/ --benchmark-only
```

## Troubleshooting

### Common Issues

#### 1. Import Errors

**Problem**: `ModuleNotFoundError: No module named 'pytest_asyncio'`

**Solution**:

```bash
# Activate virtual environment
source venv_personal_assistant/bin/activate

# Install missing dependencies
pip install pytest-asyncio
```

#### 2. Test Failures

**Problem**: Tests failing unexpectedly

**Solution**:

```bash
# Run with verbose output
python -m pytest -v -s --tb=long

# Run specific failing test
python -m pytest tests/unit/test_auth/test_password_service.py::test_hash_password -v -s

# Run with debugging
python -m pytest -v -s --tb=long --pdb
```

#### 3. Coverage Issues

**Problem**: Coverage not being generated

**Solution**:

```bash
# Check coverage configuration
python -m pytest --cov=src --cov-report=term-missing

# Verify source path
python -m pytest --cov=src.personal_assistant --cov-report=html

# Check coverage files
ls -la htmlcov/
```

#### 4. Performance Issues

**Problem**: Tests running slowly

**Solution**:

```bash
# Run with parallel execution
python -m pytest -n auto

# Run with timing analysis
python -m pytest --durations=10

# Run slowest tests first
python -m pytest --durations=0
```

#### 5. Mock Issues

**Problem**: Mocks not working correctly

**Solution**:

```bash
# Run mock validation tests
python -m pytest tests/unit/test_mocks/ -v

# Run with mock debugging
python -m pytest -v -s --tb=long tests/unit/test_mocks/
```

### Debug Mode

```bash
# Run with debugging
python -m pytest -v -s --tb=long --pdb

# Run specific test with debugging
python -m pytest tests/unit/test_auth/test_password_service.py::test_hash_password -v -s --pdb

# Run with breakpoints
python -m pytest -v -s --tb=long --pdb --pdbcls=IPython.terminal.debugger:Pdb
```

### Environment Debugging

```bash
# Check Python environment
python --version
which python

# Check installed packages
pip list | grep pytest

# Check virtual environment
echo $VIRTUAL_ENV

# Check test configuration
python -m pytest --collect-only
```

## Best Practices

### 1. Test Execution

- **Use Virtual Environment**: Always activate virtual environment before running tests
- **Run Tests Regularly**: Run tests frequently during development
- **Use Parallel Execution**: Use parallel execution for faster test runs
- **Monitor Performance**: Keep track of test execution time

### 2. Coverage Analysis

- **Set Coverage Thresholds**: Use coverage thresholds to ensure quality
- **Generate Reports**: Generate HTML reports for detailed analysis
- **Monitor Trends**: Track coverage trends over time
- **Focus on Quality**: High coverage doesn't guarantee quality

### 3. Performance Testing

- **Set Performance Baselines**: Establish performance baselines
- **Monitor Trends**: Track performance trends over time
- **Use Benchmarking**: Use benchmarking for performance-critical tests
- **Optimize Slow Tests**: Optimize tests that take too long

### 4. Quality Validation

- **Run Quality Tests**: Run quality validation tests regularly
- **Monitor Test Reliability**: Keep track of test reliability
- **Validate Mock Quality**: Ensure mocks are realistic
- **Check Error Coverage**: Validate error handling coverage

### 5. Continuous Integration

- **Automate Testing**: Set up automated testing in CI/CD
- **Use Coverage Reports**: Include coverage reports in CI
- **Monitor Test Results**: Monitor test results and trends
- **Fail Fast**: Configure CI to fail fast on test failures

## Test Execution Scripts

### Basic Test Script

```bash
#!/bin/bash
# run_tests.sh

echo "Running Personal Assistant Tests..."

# Activate virtual environment
source venv_personal_assistant/bin/activate

# Run tests with coverage
python -m pytest --cov=src --cov-report=html --cov-report=term-missing -v

echo "Tests completed. Coverage report available in htmlcov/index.html"
```

### Performance Test Script

```bash
#!/bin/bash
# run_performance_tests.sh

echo "Running Performance Tests..."

# Activate virtual environment
source venv_personal_assistant/bin/activate

# Run performance tests
python -m pytest tests/unit/test_performance/ --benchmark-only -v

echo "Performance tests completed."
```

### Quality Validation Script

```bash
#!/bin/bash
# run_quality_validation.sh

echo "Running Quality Validation..."

# Activate virtual environment
source venv_personal_assistant/bin/activate

# Run quality validation tests
python -m pytest tests/unit/test_quality/ -v

echo "Quality validation completed."
```

### Full Test Suite Script

```bash
#!/bin/bash
# run_full_test_suite.sh

echo "Running Full Test Suite..."

# Activate virtual environment
source venv_personal_assistant/bin/activate

# Run all tests with coverage and quality validation
python -m pytest \
  --cov=src \
  --cov-report=html \
  --cov-report=term-missing \
  --cov-fail-under=80 \
  -n auto \
  -v

echo "Full test suite completed."
```

## Conclusion

This guide provides comprehensive instructions for executing tests in the Personal Assistant application. By following these guidelines, you can:

1. **Run Tests Effectively**: Execute tests efficiently with appropriate options
2. **Analyze Coverage**: Generate and analyze test coverage reports
3. **Monitor Performance**: Track test performance and identify slow tests
4. **Validate Quality**: Ensure test quality and reliability
5. **Troubleshoot Issues**: Resolve common test execution problems

Remember to:

- Always use the virtual environment
- Run tests regularly during development
- Monitor test performance and coverage
- Use parallel execution for faster test runs
- Validate test quality and reliability
