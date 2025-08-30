# NotionPagesTool Tests

This directory contains comprehensive tests for the `NotionPagesTool` class, which provides 8 main functions for managing Notion note pages.

## 🧪 Test Coverage

The tests cover all 8 functions of the NotionPagesTool:

### 1. **create_note_page**

- ✅ Successful note creation with all parameters
- ✅ Error handling for missing title
- ✅ Error handling for missing content
- ✅ Error handling for API failures

### 2. **read_note_page**

- ✅ Reading by page ID
- ✅ Reading by page title
- ✅ Error handling for non-existent pages
- ✅ Error handling for API failures

### 3. **update_note_page**

- ✅ Updating content only
- ✅ Updating properties only
- ✅ Updating both content and properties
- ✅ Error handling for API failures

### 4. **delete_note_page**

- ✅ Successful page deletion (archiving)
- ✅ Error handling for API failures

### 5. **search_notes**

- ✅ Search by query string
- ✅ Search with category filter
- ✅ Search with tags filter
- ✅ Search with no results
- ✅ Error handling for API failures

### 6. **get_table_of_contents**

- ✅ Getting TOC with pages
- ✅ Getting TOC when empty
- ✅ Error handling for API failures

### 7. **create_link**

- ✅ Successful link creation between pages
- ✅ Error handling for non-existent target pages
- ✅ Error handling for API failures

### 8. **get_backlinks**

- ✅ Finding pages that link to a specific page
- ✅ Handling cases with no backlinks
- ✅ Error handling for API failures

## 🚀 Running the Tests

### Prerequisites

1. **Install pytest**: `pip install pytest pytest-asyncio pytest-cov`
2. **Install dependencies**: Make sure all project dependencies are installed
3. **Environment setup**: Tests use mocked environment variables

### Quick Start

```bash
# Run all tests
python run_notion_tests.py

# List all available tests
python run_notion_tests.py list

# Run a specific test
python run_notion_tests.py run test_create_note_page_success

# Get help
python run_notion_tests.py help
```

### Using pytest directly

```bash
# Run all tests with coverage
pytest test_notion_pages_tool.py -v --cov=personal_assistant.tools.notion_pages --cov-report=html

# Run specific test
pytest test_notion_pages_tool.py::TestNotionPagesTool::test_create_note_page_success -v

# Run tests with specific markers
pytest test_notion_pages_tool.py -m unit -v
```

## 📁 Test Files

- **`test_notion_pages_tool.py`** - Main test suite for NotionPagesTool
- **`conftest.py`** - Pytest configuration and common fixtures
- **`run_notion_tests.py`** - Test runner script with additional features

## 🔧 Test Configuration

### Fixtures

The tests use several fixtures to provide consistent test data:

- **`mock_notion_client`** - Mocked Notion API client
- **`notion_tool`** - NotionPagesTool instance with mocked dependencies
- **`sample_page_data`** - Sample Notion page data structure
- **`sample_blocks_data`** - Sample Notion blocks data structure

### Mocking Strategy

- **External APIs**: All Notion API calls are mocked
- **Dependencies**: Internal dependencies are patched where needed
- **Error scenarios**: Exceptions are simulated to test error handling

## 📊 Test Results

### Expected Output

When tests pass successfully, you should see:

```
🧪 Running NotionPagesTool Tests...
==================================================
test_notion_pages_tool.py::TestNotionPagesTool::test_tool_initialization PASSED
test_notion_pages_tool.py::TestNotionPagesTool::test_create_note_page_success PASSED
...
==================================================
📊 Test Results Summary:
Exit Code: 0
✅ All tests passed!
```

### Coverage Report

The tests generate coverage reports showing:

- **Line coverage** for the NotionPagesTool class
- **Missing lines** that need additional testing
- **HTML report** in the `htmlcov/` directory

## 🐛 Troubleshooting

### Common Issues

1. **Import errors**: Make sure the `src/` directory is in your Python path
2. **Missing dependencies**: Install `pytest`, `pytest-asyncio`, and `pytest-cov`
3. **Async test failures**: Ensure `pytest-asyncio` is properly configured

### Debug Mode

To run tests with more verbose output:

```bash
pytest test_notion_pages_tool.py -v -s --tb=long
```

### Running Individual Test Classes

```bash
# Run only initialization tests
pytest test_notion_pages_tool.py::TestNotionPagesTool::test_tool_initialization -v

# Run only CRUD operation tests
pytest test_notion_pages_tool.py -k "create or read or update or delete" -v
```

## 🔄 Adding New Tests

When adding new functionality to NotionPagesTool:

1. **Add test methods** to the `TestNotionPagesTool` class
2. **Follow naming convention**: `test_<function_name>_<scenario>`
3. **Use appropriate markers**: `@pytest.mark.asyncio` for async tests
4. **Mock external dependencies**: Don't make real API calls in tests
5. **Test error scenarios**: Include tests for failure cases

### Example Test Structure

```python
@pytest.mark.asyncio
async def test_new_function_success(self, notion_tool, mock_notion_client):
    """Test successful execution of new function"""
    # Setup mocks
    mock_notion_client.some_method.return_value = expected_result

    # Execute function
    result = await notion_tool.new_function(param1, param2)

    # Verify result
    assert "success" in result.lower()

    # Verify mocks were called correctly
    mock_notion_client.some_method.assert_called_once_with(expected_params)
```

## 📈 Performance Considerations

- **Test isolation**: Each test runs independently
- **Mock efficiency**: Mocks are lightweight and fast
- **Async handling**: Tests use `pytest-asyncio` for proper async support
- **Coverage analysis**: Coverage reports help identify untested code

## 🤝 Contributing

When contributing to the tests:

1. **Maintain coverage**: Aim for >90% line coverage
2. **Follow patterns**: Use existing test structure and naming conventions
3. **Document changes**: Update this README when adding new test categories
4. **Test edge cases**: Include tests for boundary conditions and error scenarios

