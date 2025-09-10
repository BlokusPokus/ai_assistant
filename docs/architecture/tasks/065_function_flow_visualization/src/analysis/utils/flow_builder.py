"""
Flow Builder for creating visual flow diagrams.

This module provides functionality to build flow structures from parsed functions,
creating nodes and edges that represent the execution flow.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from .ast_parser import FunctionNode


@dataclass
class FlowNode:
    """Represents a node in the flow diagram."""
    id: str
    type: str  # 'start', 'end', 'process', 'decision', 'call', 'loop'
    label: str
    line_number: int
    details: Dict[str, Any]
    style: Optional[Dict[str, str]] = None


@dataclass
class FlowEdge:
    """Represents an edge (connection) in the flow diagram."""
    from_node: str
    to_node: str
    label: str
    condition: Optional[str] = None
    style: Optional[Dict[str, str]] = None


class FlowBuilder:
    """Builds flow structures from function analysis."""
    
    def __init__(self):
        self.nodes: List[FlowNode] = []
        self.edges: List[FlowEdge] = []
        self.node_counter = 0
    
    def build_flow(self, function_node: FunctionNode) -> Dict[str, Any]:
        """
        Build flow structure from function analysis.
        
        Args:
            function_node: Parsed function information
            
        Returns:
            Dict containing nodes and edges for visualization
        """
        # Reset state
        self.nodes = []
        self.edges = []
        self.node_counter = 0
        
        # Create start node
        start_node = self._create_start_node(function_node)
        self.nodes.append(start_node)
        
        # Process the function body
        current_node_id = start_node.id
        
        # Process control flow structures
        for flow_item in function_node.control_flow:
            current_node_id = self._process_control_flow_item(flow_item, current_node_id)
        
        # Process function calls
        for call in function_node.calls:
            call_node = self._create_call_node(call)
            self.nodes.append(call_node)
            
            # Connect to call node
            self.edges.append(FlowEdge(
                from_node=current_node_id,
                to_node=call_node.id,
                label="calls"
            ))
            
            # Connect back to main flow
            current_node_id = call_node.id
        
        # Create end node
        end_node = self._create_end_node(function_node)
        self.nodes.append(end_node)
        
        # Connect to end
        self.edges.append(FlowEdge(
            from_node=current_node_id,
            to_node=end_node.id,
            label="returns"
        ))
        
        return {
            'nodes': [self._node_to_dict(node) for node in self.nodes],
            'edges': [self._edge_to_dict(edge) for edge in self.edges],
            'metadata': {
                'function_name': function_node.name,
                'complexity_score': function_node.complexity_score,
                'total_nodes': len(self.nodes),
                'total_edges': len(self.edges)
            }
        }
    
    def _create_start_node(self, function_node: FunctionNode) -> FlowNode:
        """Create the start node for the function."""
        self.node_counter += 1
        return FlowNode(
            id=f"start_{self.node_counter}",
            type="start",
            label=f"Start: {function_node.name}",
            line_number=function_node.line_number,
            details={
                'function_name': function_node.name,
                'parameters': function_node.parameters,
                'return_type': function_node.return_type
            },
            style={
                'shape': 'ellipse',
                'fillcolor': 'lightgreen',
                'style': 'filled'
            }
        )
    
    def _create_end_node(self, function_node: FunctionNode) -> FlowNode:
        """Create the end node for the function."""
        self.node_counter += 1
        return FlowNode(
            id=f"end_{self.node_counter}",
            type="end",
            label=f"End: {function_node.name}",
            line_number=0,
            details={
                'function_name': function_node.name
            },
            style={
                'shape': 'ellipse',
                'fillcolor': 'lightcoral',
                'style': 'filled'
            }
        )
    
    def _create_call_node(self, call_name: str) -> FlowNode:
        """Create a node for a function call."""
        self.node_counter += 1
        return FlowNode(
            id=f"call_{self.node_counter}",
            type="call",
            label=f"Call: {call_name}",
            line_number=0,
            details={
                'function_name': call_name
            },
            style={
                'shape': 'box',
                'fillcolor': 'lightyellow',
                'style': 'filled'
            }
        )
    
    def _process_control_flow_item(self, flow_item: Dict[str, Any], current_node_id: str) -> str:
        """Process a control flow item and return the new current node ID."""
        flow_type = flow_item['type']
        
        if flow_type == 'if':
            return self._process_if_statement(flow_item, current_node_id)
        elif flow_type == 'for':
            return self._process_for_loop(flow_item, current_node_id)
        elif flow_type == 'while':
            return self._process_while_loop(flow_item, current_node_id)
        elif flow_type == 'try':
            return self._process_try_block(flow_item, current_node_id)
        else:
            return current_node_id
    
    def _process_if_statement(self, flow_item: Dict[str, Any], current_node_id: str) -> str:
        """Process an if statement."""
        self.node_counter += 1
        decision_node = FlowNode(
            id=f"decision_{self.node_counter}",
            type="decision",
            label=f"If: {flow_item['condition']}",
            line_number=flow_item['line'],
            details={
                'condition': flow_item['condition'],
                'has_else': flow_item.get('has_else', False)
            },
            style={
                'shape': 'diamond',
                'fillcolor': 'lightblue',
                'style': 'filled'
            }
        )
        
        self.nodes.append(decision_node)
        
        # Connect to decision node
        self.edges.append(FlowEdge(
            from_node=current_node_id,
            to_node=decision_node.id,
            label=""
        ))
        
        # Create true and false paths
        if flow_item.get('has_else', False):
            # True path
            self.edges.append(FlowEdge(
                from_node=decision_node.id,
                to_node=f"true_{self.node_counter}",
                label="True",
                condition="true"
            ))
            
            # False path
            self.edges.append(FlowEdge(
                from_node=decision_node.id,
                to_node=f"false_{self.node_counter}",
                label="False",
                condition="false"
            ))
        
        return decision_node.id
    
    def _process_for_loop(self, flow_item: Dict[str, Any], current_node_id: str) -> str:
        """Process a for loop."""
        self.node_counter += 1
        loop_node = FlowNode(
            id=f"loop_{self.node_counter}",
            type="loop",
            label=f"For: {flow_item['iterator']} in {flow_item['iterable']}",
            line_number=flow_item['line'],
            details={
                'iterator': flow_item['iterator'],
                'iterable': flow_item['iterable']
            },
            style={
                'shape': 'box',
                'fillcolor': 'lightcyan',
                'style': 'filled'
            }
        )
        
        self.nodes.append(loop_node)
        
        # Connect to loop node
        self.edges.append(FlowEdge(
            from_node=current_node_id,
            to_node=loop_node.id,
            label=""
        ))
        
        return loop_node.id
    
    def _process_while_loop(self, flow_item: Dict[str, Any], current_node_id: str) -> str:
        """Process a while loop."""
        self.node_counter += 1
        loop_node = FlowNode(
            id=f"while_{self.node_counter}",
            type="loop",
            label=f"While: {flow_item['condition']}",
            line_number=flow_item['line'],
            details={
                'condition': flow_item['condition']
            },
            style={
                'shape': 'box',
                'fillcolor': 'lightcyan',
                'style': 'filled'
            }
        )
        
        self.nodes.append(loop_node)
        
        # Connect to loop node
        self.edges.append(FlowEdge(
            from_node=current_node_id,
            to_node=loop_node.id,
            label=""
        ))
        
        return loop_node.id
    
    def _process_try_block(self, flow_item: Dict[str, Any], current_node_id: str) -> str:
        """Process a try-except block."""
        self.node_counter += 1
        try_node = FlowNode(
            id=f"try_{self.node_counter}",
            type="process",
            label="Try Block",
            line_number=flow_item['line'],
            details={
                'has_except': flow_item.get('has_except', False),
                'has_finally': flow_item.get('has_finally', False)
            },
            style={
                'shape': 'box',
                'fillcolor': 'lightpink',
                'style': 'filled'
            }
        )
        
        self.nodes.append(try_node)
        
        # Connect to try node
        self.edges.append(FlowEdge(
            from_node=current_node_id,
            to_node=try_node.id,
            label=""
        ))
        
        return try_node.id
    
    def _node_to_dict(self, node: FlowNode) -> Dict[str, Any]:
        """Convert a FlowNode to a dictionary."""
        result = {
            'id': node.id,
            'type': node.type,
            'label': node.label,
            'line_number': node.line_number,
            'details': node.details
        }
        
        if node.style:
            result['style'] = node.style
            
        return result
    
    def _edge_to_dict(self, edge: FlowEdge) -> Dict[str, Any]:
        """Convert a FlowEdge to a dictionary."""
        result = {
            'from': edge.from_node,
            'to': edge.to_node,
            'label': edge.label
        }
        
        if edge.condition:
            result['condition'] = edge.condition
            
        if edge.style:
            result['style'] = edge.style
            
        return result
