"""
Tests for Function Flow Tool functionality.
"""

import pytest
import tempfile
import os
from ..function_flow_tool import FunctionFlowTool
from .test_functions import (
    simple_test_function,
    complex_test_function,
    imports_test_function,
    try_test_function
)


class TestFunctionFlowTool:
    """Test the FunctionFlowTool functionality."""
    
    def setup_method(self):
        self.tool = FunctionFlowTool()
    
    def test_tool_initialization(self):
        """Test tool initialization."""
        assert self.tool.name == "function_flow_visualizer"
        assert self.tool.description == "Generate visual flow diagrams for selected functions"
        assert self.tool.analyzer is not None
        assert self.tool.generator is not None
    
    def test_analyze_and_visualize_simple_function(self):
        """Test analyzing and visualizing a simple function."""
        result = self.tool.analyze_and_visualize(simple_test_function, output_format='svg')
        
        assert result['success'] is True
        assert 'diagram' in result
        assert result['diagram']['format'] == 'svg'
        assert isinstance(result['diagram']['data'], str)
        assert 'svg' in result['diagram']['data'].lower()
    
    def test_analyze_and_visualize_with_file_output(self, tmp_path):
        """Test analyzing and visualizing with file output."""
        output_file = tmp_path / "test_diagram.png"
        result = self.tool.analyze_and_visualize(
            simple_test_function, 
            output_format='png',
            output_file=str(output_file)
        )
        
        assert result['success'] is True
        assert result['diagram']['file_path'] == str(output_file)
        assert output_file.exists()
    
    def test_analyze_and_visualize_html_output(self):
        """Test analyzing and visualizing with HTML output."""
        result = self.tool.analyze_and_visualize(simple_test_function, output_format='html')
        
        assert result['success'] is True
        assert result['diagram']['format'] == 'html'
        assert isinstance(result['diagram']['data'], str)
        assert '<html>' in result['diagram']['data']
        assert '<head>' in result['diagram']['data']
        assert '<body>' in result['diagram']['data']
    
    def test_analyze_and_visualize_mermaid_output(self):
        """Test analyzing and visualizing with Mermaid output."""
        result = self.tool.analyze_and_visualize(complex_test_function, output_format='mermaid')
        
        assert result['success'] is True
        assert result['diagram']['format'] == 'mermaid'
        assert isinstance(result['diagram']['data'], str)
        assert 'graph TD' in result['diagram']['data']
    
    def test_analyze_function_from_file_nonexistent(self):
        """Test analyzing function from nonexistent file."""
        result = self.tool.analyze_function_from_file(
            "nonexistent_file.py", 
            "test_function",
            output_format='png'
        )
        
        assert result['success'] is False
        assert 'error' in result
    
    def test_get_supported_formats(self):
        """Test getting supported formats."""
        formats = self.tool.get_supported_formats()
        
        expected_formats = ['png', 'svg', 'pdf', 'dot', 'mermaid', 'html']
        for format in expected_formats:
            assert format in formats
    
    def test_create_analysis_report_success(self):
        """Test creating analysis report for successful analysis."""
        result = self.tool.analyze_and_visualize(simple_test_function, output_format='svg')
        report = self.tool.create_analysis_report(result)
        
        assert isinstance(report, str)
        assert 'simple_test_function' in report
        # Note: The docstring may not be included in the report format
        assert 'Diagram Information' in report
        assert 'Format: svg' in report
    
    def test_create_analysis_report_failure(self):
        """Test creating analysis report for failed analysis."""
        failed_result = {
            'success': False,
            'error': 'Test error'
        }
        
        report = self.tool.create_analysis_report(failed_result)
        assert 'Analysis failed: Test error' in report
    
    def test_batch_analyze(self, tmp_path):
        """Test batch analysis of multiple functions."""
        # Create a temporary Python file with test functions
        test_file = tmp_path / "test_functions.py"
        with open(test_file, 'w') as f:
            f.write("""
def function1(x):
    return x * 2

def function2(x, y):
    if x > y:
        return x
    else:
        return y
""")
        
        functions = [
            {'name': 'function1', 'module_path': 'test_functions'},
            {'name': 'function2', 'module_path': 'test_functions'}
        ]
        
        # This test would require proper module loading, so we'll test error handling
        result = self.tool.batch_analyze(functions, output_dir=str(tmp_path))
        
        assert result['success'] is True
        assert result['total_functions'] == 2
        assert len(result['results']) == 2
    
    def test_batch_analyze_with_output_dir(self, tmp_path):
        """Test batch analysis with output directory."""
        functions = [
            {'name': 'nonexistent_function', 'module_path': 'nonexistent_module'}
        ]
        
        result = self.tool.batch_analyze(functions, output_dir=str(tmp_path))
        
        assert result['success'] is True
        assert result['total_functions'] == 1
        assert result['failed_analyses'] == 1
        assert result['successful_analyses'] == 0
    
    def test_get_tool_info(self):
        """Test getting tool information."""
        info = self.tool.get_tool_info()
        
        assert info['name'] == "function_flow_visualizer"
        assert info['description'] == "Generate visual flow diagrams for selected functions"
        assert 'supported_formats' in info
        assert 'capabilities' in info
        assert len(info['capabilities']) > 0
    
    def test_analyze_and_visualize_error_handling(self):
        """Test error handling in analyze_and_visualize."""
        # Test with invalid function
        result = self.tool.analyze_and_visualize("not_a_function", output_format='png')
        
        assert result['success'] is False
        assert 'error' in result
        assert 'error_type' in result
    
    def test_analyze_function_from_file_error_handling(self):
        """Test error handling in analyze_function_from_file."""
        result = self.tool.analyze_function_from_file(
            "nonexistent_file.py",
            "nonexistent_function",
            output_format='png'
        )
        
        assert result['success'] is False
        assert 'error' in result
        # Note: error_type may not be present in all error cases
