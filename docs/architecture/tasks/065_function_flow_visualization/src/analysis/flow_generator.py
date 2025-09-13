"""
Flow Generator for creating visual diagrams.

This module provides functionality to generate visual diagrams from flow structures
using Graphviz for professional-quality output.
"""

import graphviz
from typing import Dict, List, Any, Optional, Union
import io
import base64


class FlowGenerator:
    """Generates visual diagrams from flow structures."""
    
    def __init__(self, engine: str = 'dot'):
        """
        Initialize the flow generator.
        
        Args:
            engine: Graphviz layout engine ('dot', 'neato', 'fdp', 'sfdp', 'circo', 'twopi')
        """
        self.engine = engine
        self.graph = None
    
    def generate_diagram(self, flow_data: Dict[str, Any], format: str = 'png', 
                        width: Optional[str] = None, height: Optional[str] = None) -> Union[str, bytes]:
        """
        Generate visual diagram from flow data.
        
        Args:
            flow_data: Flow structure containing nodes and edges
            format: Output format ('png', 'svg', 'pdf', 'dot', 'mermaid')
            width: Optional width constraint
            height: Optional height constraint
            
        Returns:
            Diagram data in the specified format
        """
        if format.lower() == 'mermaid':
            return self._generate_mermaid(flow_data)
        
        # Create Graphviz graph
        self.graph = graphviz.Digraph(comment='Function Flow')
        self.graph.attr(rankdir='TB', size='8,6')
        
        # Set size constraints if provided
        if width:
            self.graph.attr(size=f"{width},{height or '6'}")
        
        # Add nodes
        for node_data in flow_data['nodes']:
            self._add_node(node_data)
        
        # Add edges
        for edge_data in flow_data['edges']:
            self._add_edge(edge_data)
        
        # Generate and return diagram
        if format.lower() in ['png', 'pdf']:
            return self.graph.pipe(format=format)
        else:
            return self.graph.pipe(format=format).decode('utf-8')
    
    def generate_diagram_file(self, flow_data: Dict[str, Any], filename: str, 
                            format: str = 'png') -> str:
        """
        Generate diagram and save to file.
        
        Args:
            flow_data: Flow structure containing nodes and edges
            filename: Output filename (without extension)
            format: Output format
            
        Returns:
            Path to the generated file
        """
        if format.lower() == 'mermaid':
            content = self._generate_mermaid(flow_data)
            filepath = f"{filename}.md"
            with open(filepath, 'w') as f:
                f.write(content)
            return filepath
        
        # Create Graphviz graph
        self.graph = graphviz.Digraph(comment='Function Flow')
        self.graph.attr(rankdir='TB', size='8,6')
        
        # Add nodes and edges
        for node_data in flow_data['nodes']:
            self._add_node(node_data)
        
        for edge_data in flow_data['edges']:
            self._add_edge(edge_data)
        
        # Render to file
        return self.graph.render(filename, format=format, cleanup=True)
    
    def _add_node(self, node_data: Dict[str, Any]) -> None:
        """Add a node to the graph with appropriate styling."""
        node_id = node_data['id']
        label = node_data['label']
        node_type = node_data['type']
        style = node_data.get('style', {})
        
        # Set default attributes based on node type
        attrs = {
            'label': label,
            'fontname': 'Arial',
            'fontsize': '10'
        }
        
        # Apply node-specific styling
        if node_type == 'start':
            attrs.update({
                'shape': 'ellipse',
                'style': 'filled',
                'fillcolor': 'lightgreen',
                'fontcolor': 'black'
            })
        elif node_type == 'end':
            attrs.update({
                'shape': 'ellipse',
                'style': 'filled',
                'fillcolor': 'lightcoral',
                'fontcolor': 'black'
            })
        elif node_type == 'decision':
            attrs.update({
                'shape': 'diamond',
                'style': 'filled',
                'fillcolor': 'lightblue',
                'fontcolor': 'black'
            })
        elif node_type == 'call':
            attrs.update({
                'shape': 'box',
                'style': 'filled',
                'fillcolor': 'lightyellow',
                'fontcolor': 'black'
            })
        elif node_type == 'loop':
            attrs.update({
                'shape': 'box',
                'style': 'filled',
                'fillcolor': 'lightcyan',
                'fontcolor': 'black'
            })
        else:
            attrs.update({
                'shape': 'box',
                'style': 'filled',
                'fillcolor': 'lightgray',
                'fontcolor': 'black'
            })
        
        # Override with custom style if provided
        if style:
            attrs.update(style)
        
        # Add the node
        self.graph.node(node_id, **attrs)
    
    def _add_edge(self, edge_data: Dict[str, Any]) -> None:
        """Add an edge to the graph with appropriate styling."""
        from_node = edge_data['from']
        to_node = edge_data['to']
        label = edge_data['label']
        condition = edge_data.get('condition')
        style = edge_data.get('style', {})
        
        # Build edge label
        edge_label = label
        if condition:
            edge_label = f"{label}\n({condition})" if label else condition
        
        # Set default edge attributes
        attrs = {
            'fontname': 'Arial',
            'fontsize': '9'
        }
        
        # Apply condition-specific styling
        if condition == 'true':
            attrs['color'] = 'green'
        elif condition == 'false':
            attrs['color'] = 'red'
        
        # Override with custom style if provided
        if style:
            attrs.update(style)
        
        # Add the edge
        self.graph.edge(from_node, to_node, label=edge_label, **attrs)
    
    def _generate_mermaid(self, flow_data: Dict[str, Any]) -> str:
        """Generate Mermaid diagram format."""
        lines = ["graph TD"]
        
        # Add nodes
        for node_data in flow_data['nodes']:
            node_id = node_data['id']
            label = node_data['label'].replace('"', '\\"')
            node_type = node_data['type']
            
            if node_type == 'start':
                lines.append(f'    {node_id}["{label}"]')
            elif node_type == 'end':
                lines.append(f'    {node_id}["{label}"]')
            elif node_type == 'decision':
                lines.append(f'    {node_id}{{"{label}"}}')
            else:
                lines.append(f'    {node_id}["{label}"]')
        
        # Add edges
        for edge_data in flow_data['edges']:
            from_node = edge_data['from']
            to_node = edge_data['to']
            label = edge_data['label']
            condition = edge_data.get('condition')
            
            if condition:
                edge_label = f"{label} ({condition})" if label else condition
            else:
                edge_label = label
            
            if edge_label:
                lines.append(f'    {from_node} -->|"{edge_label}"| {to_node}')
            else:
                lines.append(f'    {from_node} --> {to_node}')
        
        return '\n'.join(lines)
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported export formats."""
        return ['png', 'svg', 'pdf', 'dot', 'mermaid']
    
    def create_interactive_html(self, flow_data: Dict[str, Any], 
                              title: str = "Function Flow") -> str:
        """
        Create an interactive HTML visualization.
        
        Args:
            flow_data: Flow structure containing nodes and edges
            title: Title for the HTML page
            
        Returns:
            HTML content as string
        """
        # Generate SVG for embedding
        svg_content = self.generate_diagram(flow_data, format='svg')
        
        html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <title>{title}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .diagram {{
            text-align: center;
            margin: 20px 0;
        }}
        .metadata {{
            margin-top: 20px;
            padding: 15px;
            background-color: #f8f9fa;
            border-radius: 4px;
        }}
        .metadata h3 {{
            margin-top: 0;
            color: #333;
        }}
        .metadata-item {{
            margin: 5px 0;
        }}
        .metadata-label {{
            font-weight: bold;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{title}</h1>
        <div class="diagram">
            {svg_content}
        </div>
        <div class="metadata">
            <h3>Function Analysis</h3>
            <div class="metadata-item">
                <span class="metadata-label">Function Name:</span> {flow_data.get('metadata', {}).get('function_name', 'Unknown')}
            </div>
            <div class="metadata-item">
                <span class="metadata-label">Complexity Score:</span> {flow_data.get('metadata', {}).get('complexity_score', 0)}
            </div>
            <div class="metadata-item">
                <span class="metadata-label">Total Nodes:</span> {flow_data.get('metadata', {}).get('total_nodes', 0)}
            </div>
            <div class="metadata-item">
                <span class="metadata-label">Total Edges:</span> {flow_data.get('metadata', {}).get('total_edges', 0)}
            </div>
        </div>
    </div>
</body>
</html>
"""
        return html_template
