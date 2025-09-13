"""
Main Function Flow Tool for generating visual flow diagrams.

This module provides the main tool interface for function flow visualization,
combining analysis and diagram generation capabilities.
"""

from typing import Dict, Any, Optional, Union, List
import os
import tempfile
from .function_analyzer import FunctionAnalyzer
from .flow_generator import FlowGenerator


class FunctionFlowTool:
    """Main tool for function flow visualization."""
    
    def __init__(self):
        self.name = "function_flow_visualizer"
        self.description = "Generate visual flow diagrams for selected functions"
        self.analyzer = FunctionAnalyzer()
        self.generator = FlowGenerator()
    
    def analyze_and_visualize(self, func: Union[callable, str], 
                            module_path: Optional[str] = None,
                            output_format: str = 'png',
                            output_file: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze a function and generate a visual diagram.
        
        Args:
            func: Function object or function name
            module_path: Module path if func is a string
            output_format: Output format ('png', 'svg', 'pdf', 'mermaid', 'html')
            output_file: Optional output file path
            
        Returns:
            Analysis result with diagram data
        """
        try:
            # Analyze the function
            analysis = self.analyzer.analyze_function(func, module_path)
            
            if not analysis.get('success', False):
                return analysis
            
            # Generate diagram
            flow_data = analysis['flow_structure']
            
            if output_format.lower() == 'html':
                diagram_data = self.generator.create_interactive_html(flow_data)
            else:
                diagram_data = self.generator.generate_diagram(flow_data, output_format)
            
            # Save to file if requested
            if output_file:
                self._save_diagram(diagram_data, output_file, output_format)
            
            # Add diagram data to analysis
            analysis['diagram'] = {
                'format': output_format,
                'data': diagram_data,
                'file_path': output_file if output_file else None
            }
            
            return analysis
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__,
                'message': f"Failed to analyze and visualize function: {e}"
            }
    
    def analyze_function_from_file(self, file_path: str, function_name: str,
                                 output_format: str = 'png',
                                 output_file: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze a function from a file and generate a visual diagram.
        
        Args:
            file_path: Path to the Python file
            function_name: Name of the function to analyze
            output_format: Output format ('png', 'svg', 'pdf', 'mermaid', 'html')
            output_file: Optional output file path
            
        Returns:
            Analysis result with diagram data
        """
        try:
            # Analyze the function
            analysis = self.analyzer.analyze_file(file_path, function_name)
            
            if not analysis.get('success', False):
                return analysis
            
            # Generate diagram
            flow_data = analysis['flow_structure']
            
            if output_format.lower() == 'html':
                diagram_data = self.generator.create_interactive_html(flow_data)
            else:
                diagram_data = self.generator.generate_diagram(flow_data, output_format)
            
            # Save to file if requested
            if output_file:
                self._save_diagram(diagram_data, output_file, output_format)
            
            # Add diagram data to analysis
            analysis['diagram'] = {
                'format': output_format,
                'data': diagram_data,
                'file_path': output_file if output_file else None
            }
            
            return analysis
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__,
                'message': f"Failed to analyze and visualize function '{function_name}' from file '{file_path}': {e}"
            }
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported export formats."""
        return self.generator.get_supported_formats() + ['html']
    
    def create_analysis_report(self, analysis: Dict[str, Any]) -> str:
        """
        Create a comprehensive analysis report.
        
        Args:
            analysis: Analysis result from analyze_and_visualize
            
        Returns:
            Formatted analysis report
        """
        if not analysis.get('success', False):
            return f"Analysis failed: {analysis.get('error', 'Unknown error')}"
        
        # Get summary from analyzer
        summary = self.analyzer.get_analysis_summary(analysis)
        
        # Add diagram information
        diagram_info = analysis.get('diagram', {})
        if diagram_info:
            summary += f"\n\nDiagram Information:\n"
            summary += f"Format: {diagram_info.get('format', 'Unknown')}\n"
            if diagram_info.get('file_path'):
                summary += f"Saved to: {diagram_info['file_path']}\n"
            else:
                summary += f"Diagram data available in memory\n"
        
        return summary
    
    def _save_diagram(self, diagram_data: Union[str, bytes], 
                     output_file: str, format: str) -> None:
        """Save diagram data to file."""
        mode = 'w' if isinstance(diagram_data, str) else 'wb'
        with open(output_file, mode) as f:
            f.write(diagram_data)
    
    def batch_analyze(self, functions: List[Dict[str, str]], 
                     output_dir: str = None) -> Dict[str, Any]:
        """
        Analyze multiple functions in batch.
        
        Args:
            functions: List of dicts with 'name' and 'module_path' keys
            output_dir: Optional output directory for diagrams
            
        Returns:
            Batch analysis results
        """
        results = {
            'success': True,
            'total_functions': len(functions),
            'successful_analyses': 0,
            'failed_analyses': 0,
            'results': []
        }
        
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        for i, func_info in enumerate(functions):
            try:
                func_name = func_info['name']
                module_path = func_info['module_path']
                
                # Determine output file
                output_file = None
                if output_dir:
                    output_file = os.path.join(output_dir, f"{func_name}_flow.png")
                
                # Analyze function
                result = self.analyze_and_visualize(
                    func_name, 
                    module_path, 
                    output_format='png',
                    output_file=output_file
                )
                
                results['results'].append({
                    'function_name': func_name,
                    'module_path': module_path,
                    'success': result.get('success', False),
                    'output_file': output_file,
                    'error': result.get('error') if not result.get('success') else None
                })
                
                if result.get('success'):
                    results['successful_analyses'] += 1
                else:
                    results['failed_analyses'] += 1
                    
            except Exception as e:
                results['results'].append({
                    'function_name': func_info.get('name', 'unknown'),
                    'module_path': func_info.get('module_path', 'unknown'),
                    'success': False,
                    'output_file': None,
                    'error': str(e)
                })
                results['failed_analyses'] += 1
        
        return results
    
    def get_tool_info(self) -> Dict[str, Any]:
        """Get information about this tool."""
        return {
            'name': self.name,
            'description': self.description,
            'supported_formats': self.get_supported_formats(),
            'capabilities': [
                'Function analysis using AST parsing',
                'Visual flow diagram generation',
                'Multiple export formats',
                'Batch processing',
                'Interactive HTML output',
                'Complexity analysis',
                'Dependency mapping'
            ]
        }
