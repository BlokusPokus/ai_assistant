# Internet Tools Test Suite

This directory contains comprehensive tests for the Internet Tools functionality in the Personal Assistant system.

## Test Structure

### 📁 Test Files

1. **`test_internet_tools.py`** - Main tool functionality tests

   - Tests the 4 main internet tools: web_search, news_articles, wikipedia, image_search
   - Covers tool initialization, parameter validation, and core functionality
   - Tests error handling and edge cases

2. **`test_internet_internal.py`** - Internal function tests

   - Tests validation functions (query, safe_search, max_results, etc.)
   - Tests formatting functions for different result types
   - Tests rate limiting and utility functions

3. **`test_internet_error_handler.py`** - Error handling tests
   - Tests error handler for various error types
   - Tests logging and user-friendly error messages
   - Tests edge cases and boundary conditions

### 🚀 Test Runner

**`run_internet_tests.py`** - Comprehensive test runner script

- Run all tests: `python run_internet_tests.py`
- Show summary: `python run_internet_tests.py --summary`
- Run specific file: `python run_internet_tests.py --file test_internet_tools.py`
- Use subprocess: `python run_internet_tests.py --subprocess`

## Test Coverage

### 🧪 Main Tool Tests (`test_internet_tools.py`)

#### Tool Initialization

- ✅ Tool creation and configuration
- ✅ Parameter validation
- ✅ Tool iteration and access

#### Web Search Tool

- ✅ Successful web searches
- ✅ Query validation failures
- ✅ DuckDuckGo unavailability
- ✅ Rate limit handling
- ✅ Exception handling

#### News Articles Tool

- ✅ News retrieval by category
- ✅ Rate limiting behavior
- ✅ Error handling

#### Wikipedia Tool

- ✅ Topic search functionality
- ✅ Language code validation
- ✅ Summary vs. full content
- ✅ Error scenarios

#### Image Search Tool

- ✅ Image search functionality
- ✅ Safe search controls
- ✅ Result formatting
- ✅ Error handling

#### Edge Cases

- ✅ Minimum/maximum parameters
- ✅ Different language codes
- ✅ Various news categories
- ✅ Tool integration workflows

### 🔧 Internal Function Tests (`test_internet_internal.py`)

#### Rate Limiting

- ✅ Rate limit checks
- ✅ Time-based blocking
- ✅ First request handling

#### Validation Functions

- ✅ Safe search validation
- ✅ Max results validation
- ✅ Language code validation
- ✅ Query and topic validation
- ✅ News and image parameter validation

#### Formatting Functions

- ✅ Web search result formatting
- ✅ Image search result formatting
- ✅ News article response formatting
- ✅ Wikipedia response formatting
- ✅ Empty result handling

#### Data Extraction

- ✅ Search result information extraction
- ✅ Image result information extraction
- ✅ Missing field handling

#### DuckDuckGo Processing

- ✅ Text result processing
- ✅ Image result processing
- ✅ Exception handling

### 🚨 Error Handler Tests (`test_internet_error_handler.py`)

#### Basic Error Handling

- ✅ Different error types (ValueError, ConnectionError, etc.)
- ✅ Different tools (web_search, news_articles, etc.)
- ✅ Parameter logging and error messages

#### Edge Cases

- ✅ Empty/None parameters
- ✅ Complex parameter structures
- ✅ Special characters and unicode
- ✅ Very long error messages
- ✅ Malformed parameter structures

#### Error Recovery

- ✅ Consistent error message format
- ✅ User-friendly error descriptions
- ✅ Proper logging of error details

## Running Tests

### Prerequisites

```bash
# Install pytest
pip install pytest

# Install test dependencies
pip install pytest-asyncio
```

### Quick Start

```bash
# Run all internet tool tests
cd tests/tools
python run_internet_tests.py

# Show test summary
python run_internet_tests.py --summary

# Run specific test file
python run_internet_tests.py --file test_internet_tools.py
```

### Individual Test Files

```bash
# Run main tool tests
pytest test_internet_tools.py -v

# Run internal function tests
pytest test_internet_internal.py -v

# Run error handler tests
pytest test_internet_error_handler.py -v
```

### Pytest Options

```bash
# Verbose output with short tracebacks
pytest -v --tb=short

# Stop on first failure
pytest -x

# Run specific test class
pytest test_internet_tools.py::TestInternetTool -v

# Run specific test method
pytest test_internet_tools.py::TestInternetTool::test_web_search_success -v
```

## Test Data

### Sample Results

The tests use mock data that simulates real API responses:

#### Web Search Results

```python
sample_web_search_results = [
    {
        "title": "Test Result 1",
        "link": "https://example1.com",
        "body": "This is the first test result about the search query."
    },
    {
        "title": "Test Result 2",
        "link": "https://example2.com",
        "body": "This is the second test result with more details."
    }
]
```

#### Image Search Results

```python
sample_image_search_results = [
    {
        "title": "Test Image 1",
        "link": "https://example1.com/image1.jpg",
        "image": "https://example1.com/image1.jpg",
        "thumbnail": "https://example1.com/thumb1.jpg"
    }
]
```

### Mock Dependencies

Tests use comprehensive mocking to isolate the code under test:

- **DuckDuckGo Client**: Mocked to avoid external API calls
- **Logging**: Mocked to avoid test output noise
- **Environment Variables**: Mocked for consistent test environment
- **Time Functions**: Mocked for rate limiting tests

## Test Categories

### ✅ Unit Tests

- Individual function testing
- Parameter validation
- Return value verification
- Error condition handling

### 🔄 Integration Tests

- Tool workflow testing
- Multiple tool interaction
- Rate limiting across tools
- Error recovery scenarios

### 🚨 Error Handling Tests

- Exception scenarios
- Invalid input handling
- User-friendly error messages
- Logging verification

### 🎯 Edge Case Tests

- Boundary conditions
- Extreme parameter values
- Malformed data handling
- Resource constraints

## Best Practices

### Test Organization

- Each test class focuses on a specific component
- Test methods have descriptive names
- Fixtures provide reusable test data
- Mocking isolates units under test

### Assertion Strategy

- Test one concept per test method
- Use descriptive assertion messages
- Verify both positive and negative cases
- Check error conditions and edge cases

### Mocking Strategy

- Mock external dependencies
- Use realistic mock data
- Verify mock interactions
- Test error scenarios with mocks

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure `src` directory is in Python path
2. **Mock Failures**: Check mock setup and expectations
3. **Async Test Issues**: Use `@pytest.mark.asyncio` decorator
4. **Path Issues**: Use relative paths from test directory

### Debug Mode

```bash
# Run with debug output
pytest -v -s --tb=long

# Run single test with debug
pytest test_internet_tools.py::TestInternetTool::test_web_search_success -v -s
```

## Contributing

### Adding New Tests

1. **Follow naming convention**: `test_<functionality>_<scenario>`
2. **Use descriptive docstrings**: Explain what the test verifies
3. **Mock external dependencies**: Avoid real API calls
4. **Test edge cases**: Include boundary conditions and error scenarios

### Test Data

1. **Use realistic data**: Mock data should resemble real API responses
2. **Include edge cases**: Test with empty, null, and extreme values
3. **Maintain consistency**: Use consistent data structures across tests

### Error Testing

1. **Test all error paths**: Verify error handling for each failure mode
2. **Check error messages**: Ensure user-friendly error descriptions
3. **Verify logging**: Confirm errors are properly logged

## Performance

### Test Execution Time

- **Unit tests**: < 1 second per test
- **Integration tests**: < 5 seconds per test
- **Full test suite**: < 30 seconds total

### Optimization Tips

- Use `@pytest.fixture(scope="session")` for expensive setup
- Mock time-consuming operations
- Avoid real network calls
- Use efficient assertion methods

## Coverage Goals

- **Line coverage**: > 95%
- **Branch coverage**: > 90%
- **Function coverage**: 100%
- **Error path coverage**: 100%

## Dependencies

### Required Packages

```
pytest>=7.0.0
pytest-asyncio>=0.21.0
```

### Optional Packages

```
pytest-cov>=4.0.0      # Coverage reporting
pytest-mock>=3.10.0    # Enhanced mocking
pytest-xdist>=3.0.0    # Parallel test execution
```

## Support

For questions or issues with the test suite:

1. Check the test output for specific error messages
2. Review the test data and mock setup
3. Verify Python path and import statements
4. Check pytest version compatibility

---

**Last Updated**: December 2024  
**Test Suite Version**: 1.0.0  
**Coverage Target**: 95%+ line coverage

