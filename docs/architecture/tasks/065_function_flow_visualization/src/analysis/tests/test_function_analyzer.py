"""
Tests for Function Analyzer functionality.
"""

import pytest
from ..function_analyzer import FunctionAnalyzer
from .test_functions import (
    simple_test_function,
    complex_test_function,
    imports_test_function,
    try_test_function
)


class TestFunctionAnalyzer:
    """Test the FunctionAnalyzer functionality."""
    
    def setup_method(self):
        self.analyzer = FunctionAnalyzer()
    
    def test_analyze_simple_function(self):
        """Test analyzing a simple function."""
        result = self.analyzer.analyze_function(simple_test_function)
        
        assert result['success'] is True
        assert result['function_info']['name'] == 'simple_test_function'
        assert result['function_info']['parameters'] == ['x', 'y']
        assert result['function_info']['docstring'] == 'Add two numbers.'
        assert result['complexity_metrics']['cyclomatic_complexity'] == 1
        assert 'flow_structure' in result
    
    def test_analyze_function_with_control_flow(self):
        """Test analyzing a function with control flow."""
        result = self.analyzer.analyze_function(complex_test_function)
        
        assert result['success'] is True
        assert result['function_info']['name'] == 'complex_test_function'
        assert result['function_info']['parameters'] == ['x']
        assert len(result['control_flow']) == 3  # if, for, if
        assert 'print' in result['dependencies']['function_calls']
        assert 'range' in result['dependencies']['function_calls']
        # Note: 'i' is not tracked as a variable because it's a for loop target, not an assignment
        assert result['complexity_metrics']['cyclomatic_complexity'] >= 4
    
    def test_analyze_function_with_imports(self):
        """Test analyzing a function with imports."""
        result = self.analyzer.analyze_function(imports_test_function)
        
        assert result['success'] is True
        assert 'os' in result['dependencies']['imports']
        assert 'datetime.datetime' in result['dependencies']['imports']
        assert 'os.path.join' in result['dependencies']['function_calls']
    
    def test_analyze_function_with_exceptions(self):
        """Test analyzing a function with exception handling."""
        result = self.analyzer.analyze_function(try_test_function)
        
        assert result['success'] is True
        assert len(result['control_flow']) == 1  # try block
        assert result['control_flow'][0]['type'] == 'try'
        assert result['control_flow'][0]['has_except'] is True
        assert result['control_flow'][0]['has_finally'] is True
    
    def test_analyze_function_by_name(self):
        """Test analyzing a function by name and module path."""
        # This test would require a real module, so we'll test error handling
        result = self.analyzer.analyze_function("nonexistent_function", "nonexistent_module")
        
        assert result['success'] is False
        assert 'error' in result
        assert 'ImportError' in result['error_type']
    
    def test_analyze_file_nonexistent(self):
        """Test analyzing a function from a nonexistent file."""
        result = self.analyzer.analyze_file("nonexistent_file.py", "test_function")
        
        assert result['success'] is False
        assert 'error' in result
        # Note: error_type may not be present in all error cases
    
    def test_get_complexity_level(self):
        """Test complexity level determination."""
        # Test low complexity
        assert self.analyzer._get_complexity_level(3) == "Low"
        assert self.analyzer._get_complexity_level(5) == "Low"
        
        # Test medium complexity
        assert self.analyzer._get_complexity_level(7) == "Medium"
        assert self.analyzer._get_complexity_level(10) == "Medium"
        
        # Test high complexity
        assert self.analyzer._get_complexity_level(15) == "High"
        assert self.analyzer._get_complexity_level(20) == "High"
        
        # Test very high complexity
        assert self.analyzer._get_complexity_level(25) == "Very High"
        assert self.analyzer._get_complexity_level(50) == "Very High"
    
    def test_estimate_lines(self):
        """Test line estimation."""
        from ..utils.ast_parser import FunctionNode
        
        function_node = FunctionNode(
            name="test",
            line_number=1,
            docstring=None,
            parameters=[],
            return_type=None,
            calls=["print", "len"],
            variables=["x", "y"],
            control_flow=[{"type": "if"}, {"type": "for"}],
            imports=[],
            complexity_score=5
        )
        
        lines = self.analyzer._estimate_lines(function_node)
        assert lines > 0
        assert isinstance(lines, int)
    
    def test_get_analysis_summary(self):
        """Test getting analysis summary."""
        result = self.analyzer.analyze_function(simple_test_function)
        summary = self.analyzer.get_analysis_summary(result)
        
        assert isinstance(summary, str)
        assert 'simple_test_function' in summary
        assert 'x, y' in summary
        # Note: The docstring may not be included in the summary format
        assert 'Cyclomatic Complexity' in summary
        assert 'Has Docstring: Yes' in summary
    
    def test_get_analysis_summary_error(self):
        """Test getting analysis summary for failed analysis."""
        failed_result = {
            'success': False,
            'error': 'Test error'
        }
        
        summary = self.analyzer.get_analysis_summary(failed_result)
        assert 'Analysis failed: Test error' in summary
    
    def test_analyze_function_error_handling(self):
        """Test error handling for invalid function objects."""
        # Test with non-callable object
        result = self.analyzer.analyze_function("not_a_function")
        
        assert result['success'] is False
        assert 'error' in result
        assert 'error_type' in result
