"""
Tests for Flow Generator functionality.
"""

import pytest
from ..flow_generator import FlowGenerator


class TestFlowGenerator:
    """Test the FlowGenerator functionality."""
    
    def setup_method(self):
        self.generator = FlowGenerator()
    
    def test_flow_generator_initialization(self):
        """Test FlowGenerator initialization."""
        generator = FlowGenerator()
        assert generator.engine == 'dot'
        assert generator.graph is None
        
        generator_custom = FlowGenerator(engine='neato')
        assert generator_custom.engine == 'neato'
    
    def test_get_supported_formats(self):
        """Test getting supported formats."""
        formats = self.generator.get_supported_formats()
        expected_formats = ['png', 'svg', 'pdf', 'dot', 'mermaid']
        
        for format in expected_formats:
            assert format in formats
    
    def test_generate_diagram_simple(self):
        """Test generating a simple diagram."""
        flow_data = {
            'nodes': [
                {
                    'id': 'start_1',
                    'type': 'start',
                    'label': 'Start: test_function',
                    'line_number': 1,
                    'details': {'function_name': 'test_function'},
                    'style': {'shape': 'ellipse', 'fillcolor': 'lightgreen'}
                },
                {
                    'id': 'end_2',
                    'type': 'end',
                    'label': 'End: test_function',
                    'line_number': 0,
                    'details': {'function_name': 'test_function'},
                    'style': {'shape': 'ellipse', 'fillcolor': 'lightcoral'}
                }
            ],
            'edges': [
                {
                    'from': 'start_1',
                    'to': 'end_2',
                    'label': 'returns'
                }
            ],
            'metadata': {
                'function_name': 'test_function',
                'complexity_score': 1,
                'total_nodes': 2,
                'total_edges': 1
            }
        }
        
        # Test PNG generation
        result = self.generator.generate_diagram(flow_data, format='png')
        assert isinstance(result, bytes)
        assert len(result) > 0
        
        # Test SVG generation
        result = self.generator.generate_diagram(flow_data, format='svg')
        assert isinstance(result, str)
        assert 'svg' in result.lower()
    
    def test_generate_diagram_with_control_flow(self):
        """Test generating a diagram with control flow."""
        flow_data = {
            'nodes': [
                {
                    'id': 'start_1',
                    'type': 'start',
                    'label': 'Start: complex_function',
                    'line_number': 1,
                    'details': {'function_name': 'complex_function'},
                    'style': {'shape': 'ellipse', 'fillcolor': 'lightgreen'}
                },
                {
                    'id': 'decision_2',
                    'type': 'decision',
                    'label': 'If: x > 0',
                    'line_number': 2,
                    'details': {'condition': 'x > 0', 'has_else': True},
                    'style': {'shape': 'diamond', 'fillcolor': 'lightblue'}
                },
                {
                    'id': 'call_3',
                    'type': 'call',
                    'label': 'Call: print',
                    'line_number': 0,
                    'details': {'function_name': 'print'},
                    'style': {'shape': 'box', 'fillcolor': 'lightyellow'}
                },
                {
                    'id': 'end_4',
                    'type': 'end',
                    'label': 'End: complex_function',
                    'line_number': 0,
                    'details': {'function_name': 'complex_function'},
                    'style': {'shape': 'ellipse', 'fillcolor': 'lightcoral'}
                }
            ],
            'edges': [
                {
                    'from': 'start_1',
                    'to': 'decision_2',
                    'label': ''
                },
                {
                    'from': 'decision_2',
                    'to': 'call_3',
                    'label': 'True',
                    'condition': 'true'
                },
                {
                    'from': 'call_3',
                    'to': 'end_4',
                    'label': 'returns'
                }
            ],
            'metadata': {
                'function_name': 'complex_function',
                'complexity_score': 3,
                'total_nodes': 4,
                'total_edges': 3
            }
        }
        
        result = self.generator.generate_diagram(flow_data, format='svg')
        assert isinstance(result, str)
        assert 'svg' in result.lower()
        assert 'complex_function' in result
    
    def test_generate_mermaid(self):
        """Test generating Mermaid format."""
        flow_data = {
            'nodes': [
                {
                    'id': 'start_1',
                    'type': 'start',
                    'label': 'Start: test_function',
                    'line_number': 1,
                    'details': {}
                },
                {
                    'id': 'end_2',
                    'type': 'end',
                    'label': 'End: test_function',
                    'line_number': 0,
                    'details': {}
                }
            ],
            'edges': [
                {
                    'from': 'start_1',
                    'to': 'end_2',
                    'label': 'returns'
                }
            ],
            'metadata': {}
        }
        
        result = self.generator.generate_diagram(flow_data, format='mermaid')
        assert isinstance(result, str)
        assert 'graph TD' in result
        assert 'start_1' in result
        assert 'end_2' in result
    
    def test_create_interactive_html(self):
        """Test creating interactive HTML."""
        flow_data = {
            'nodes': [
                {
                    'id': 'start_1',
                    'type': 'start',
                    'label': 'Start: test_function',
                    'line_number': 1,
                    'details': {}
                },
                {
                    'id': 'end_2',
                    'type': 'end',
                    'label': 'End: test_function',
                    'line_number': 0,
                    'details': {}
                }
            ],
            'edges': [
                {
                    'from': 'start_1',
                    'to': 'end_2',
                    'label': 'returns'
                }
            ],
            'metadata': {
                'function_name': 'test_function',
                'complexity_score': 1,
                'total_nodes': 2,
                'total_edges': 1
            }
        }
        
        html = self.generator.create_interactive_html(flow_data, title="Test Function Flow")
        
        assert isinstance(html, str)
        assert '<html>' in html
        assert '<head>' in html
        assert '<body>' in html
        assert 'Test Function Flow' in html
        assert 'test_function' in html
        assert 'svg' in html.lower()
    
    def test_generate_diagram_file(self, tmp_path):
        """Test generating diagram and saving to file."""
        flow_data = {
            'nodes': [
                {
                    'id': 'start_1',
                    'type': 'start',
                    'label': 'Start: test_function',
                    'line_number': 1,
                    'details': {}
                },
                {
                    'id': 'end_2',
                    'type': 'end',
                    'label': 'End: test_function',
                    'line_number': 0,
                    'details': {}
                }
            ],
            'edges': [
                {
                    'from': 'start_1',
                    'to': 'end_2',
                    'label': 'returns'
                }
            ],
            'metadata': {}
        }
        
        # Test PNG file generation
        file_path = tmp_path / "test_diagram"
        result_path = self.generator.generate_diagram_file(flow_data, str(file_path), format='png')
        
        assert result_path.endswith('.png')
        assert file_path.with_suffix('.png').exists()
    
    def test_generate_mermaid_file(self, tmp_path):
        """Test generating Mermaid file."""
        flow_data = {
            'nodes': [
                {
                    'id': 'start_1',
                    'type': 'start',
                    'label': 'Start: test_function',
                    'line_number': 1,
                    'details': {}
                },
                {
                    'id': 'end_2',
                    'type': 'end',
                    'label': 'End: test_function',
                    'line_number': 0,
                    'details': {}
                }
            ],
            'edges': [
                {
                    'from': 'start_1',
                    'to': 'end_2',
                    'label': 'returns'
                }
            ],
            'metadata': {}
        }
        
        file_path = tmp_path / "test_diagram"
        result_path = self.generator.generate_diagram_file(flow_data, str(file_path), format='mermaid')
        
        assert result_path.endswith('.md')
        assert file_path.with_suffix('.md').exists()
        
        # Check file content
        with open(result_path, 'r') as f:
            content = f.read()
            assert 'graph TD' in content
            assert 'start_1' in content
