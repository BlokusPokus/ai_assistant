"""
Function Analyzer for comprehensive function analysis.

This module provides high-level analysis capabilities that combine
AST parsing with flow building to create complete function analysis.
"""

from typing import Dict, List, Any, Optional, Union
import inspect
import importlib
from .utils.ast_parser import ASTParser, FunctionNode
from .utils.flow_builder import FlowBuilder


class FunctionAnalyzer:
    """Comprehensive function analyzer that combines parsing and flow building."""
    
    def __init__(self):
        self.ast_parser = ASTParser()
        self.flow_builder = FlowBuilder()
    
    def analyze_function(self, func: Union[callable, str], module_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze a function and return comprehensive analysis.
        
        Args:
            func: Function object or function name
            module_path: Module path if func is a string
            
        Returns:
            Complete function analysis including flow structure
        """
        try:
            # Get function object
            if isinstance(func, str):
                if not module_path:
                    raise ValueError("module_path is required when func is a string")
                func_obj = self._import_function(module_path, func)
            else:
                func_obj = func
            
            # Parse the function
            function_node = self.ast_parser.analyze_function(func_obj)
            
            # Build flow structure
            flow_structure = self.flow_builder.build_flow(function_node)
            
            # Generate analysis summary
            analysis = {
                'success': True,
                'function_info': {
                    'name': function_node.name,
                    'line_number': function_node.line_number,
                    'docstring': function_node.docstring,
                    'parameters': function_node.parameters,
                    'return_type': function_node.return_type
                },
                'dependencies': {
                    'function_calls': function_node.calls,
                    'variables_used': function_node.variables,
                    'imports': function_node.imports
                },
                'control_flow': function_node.control_flow,
                'flow_structure': flow_structure,
                'complexity_metrics': {
                    'cyclomatic_complexity': function_node.complexity_score,
                    'function_calls_count': len(function_node.calls),
                    'variables_count': len(function_node.variables),
                    'control_flow_count': len(function_node.control_flow),
                    'imports_count': len(function_node.imports)
                },
                'analysis_metadata': {
                    'total_lines_analyzed': self._estimate_lines(function_node),
                    'has_docstring': function_node.docstring is not None,
                    'has_type_hints': function_node.return_type is not None,
                    'complexity_level': self._get_complexity_level(function_node.complexity_score)
                }
            }
            
            return analysis
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__,
                'message': f"Failed to analyze function: {e}"
            }
    
    def analyze_file(self, file_path: str, function_name: str) -> Dict[str, Any]:
        """
        Analyze a function from a file.
        
        Args:
            file_path: Path to the Python file
            function_name: Name of the function to analyze
            
        Returns:
            Complete function analysis
        """
        try:
            function_node = self.ast_parser.analyze_file(file_path, function_name)
            if not function_node:
                return {
                    'success': False,
                    'error': f"Function '{function_name}' not found in file '{file_path}'",
                    'message': "Function not found"
                }
            
            # Build flow structure
            flow_structure = self.flow_builder.build_flow(function_node)
            
            # Generate analysis
            analysis = {
                'success': True,
                'function_info': {
                    'name': function_node.name,
                    'line_number': function_node.line_number,
                    'docstring': function_node.docstring,
                    'parameters': function_node.parameters,
                    'return_type': function_node.return_type
                },
                'dependencies': {
                    'function_calls': function_node.calls,
                    'variables_used': function_node.variables,
                    'imports': function_node.imports
                },
                'control_flow': function_node.control_flow,
                'flow_structure': flow_structure,
                'complexity_metrics': {
                    'cyclomatic_complexity': function_node.complexity_score,
                    'function_calls_count': len(function_node.calls),
                    'variables_count': len(function_node.variables),
                    'control_flow_count': len(function_node.control_flow),
                    'imports_count': len(function_node.imports)
                },
                'analysis_metadata': {
                    'file_path': file_path,
                    'total_lines_analyzed': self._estimate_lines(function_node),
                    'has_docstring': function_node.docstring is not None,
                    'has_type_hints': function_node.return_type is not None,
                    'complexity_level': self._get_complexity_level(function_node.complexity_score)
                }
            }
            
            return analysis
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__,
                'message': f"Failed to analyze function '{function_name}' from file '{file_path}': {e}"
            }
    
    def _import_function(self, module_path: str, function_name: str):
        """Import function from module path."""
        try:
            module = importlib.import_module(module_path)
            if not hasattr(module, function_name):
                raise AttributeError(f"Function '{function_name}' not found in module '{module_path}'")
            return getattr(module, function_name)
        except ImportError as e:
            raise ImportError(f"Could not import module '{module_path}': {e}")
    
    def _estimate_lines(self, function_node: FunctionNode) -> int:
        """Estimate the number of lines in the function."""
        # This is a rough estimate based on complexity
        base_lines = 2  # Function definition and return
        control_lines = len(function_node.control_flow) * 3  # Rough estimate
        call_lines = len(function_node.calls) * 2  # Rough estimate
        return base_lines + control_lines + call_lines
    
    def _get_complexity_level(self, complexity_score: int) -> str:
        """Get a human-readable complexity level."""
        if complexity_score <= 5:
            return "Low"
        elif complexity_score <= 10:
            return "Medium"
        elif complexity_score <= 20:
            return "High"
        else:
            return "Very High"
    
    def get_analysis_summary(self, analysis: Dict[str, Any]) -> str:
        """
        Get a human-readable summary of the analysis.
        
        Args:
            analysis: Analysis result from analyze_function
            
        Returns:
            Human-readable summary string
        """
        if not analysis.get('success', False):
            return f"Analysis failed: {analysis.get('error', 'Unknown error')}"
        
        func_info = analysis['function_info']
        complexity = analysis['complexity_metrics']
        metadata = analysis['analysis_metadata']
        
        summary = f"""
Function Analysis Summary
========================
Name: {func_info['name']}
Line: {func_info['line_number']}
Parameters: {', '.join(func_info['parameters']) if func_info['parameters'] else 'None'}
Return Type: {func_info['return_type'] or 'Not specified'}

Complexity Metrics:
- Cyclomatic Complexity: {complexity['cyclomatic_complexity']} ({metadata['complexity_level']})
- Function Calls: {complexity['function_calls_count']}
- Variables: {complexity['variables_count']}
- Control Flow Structures: {complexity['control_flow_count']}
- Imports: {complexity['imports_count']}

Code Quality:
- Has Docstring: {'Yes' if metadata['has_docstring'] else 'No'}
- Has Type Hints: {'Yes' if metadata['has_type_hints'] else 'No'}
- Estimated Lines: {metadata['total_lines_analyzed']}

Dependencies:
- Function Calls: {', '.join(analysis['dependencies']['function_calls']) if analysis['dependencies']['function_calls'] else 'None'}
- Variables Used: {', '.join(analysis['dependencies']['variables_used']) if analysis['dependencies']['variables_used'] else 'None'}
- Imports: {', '.join(analysis['dependencies']['imports']) if analysis['dependencies']['imports'] else 'None'}
"""
        return summary.strip()
