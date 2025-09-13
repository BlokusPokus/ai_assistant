"""
Tests for Flow Builder functionality.
"""

import pytest
from ..utils.flow_builder import FlowBuilder, FlowNode, FlowEdge
from ..utils.ast_parser import FunctionNode


class TestFlowNode:
    """Test the FlowNode dataclass."""
    
    def test_flow_node_creation(self):
        """Test creating a FlowNode."""
        node = FlowNode(
            id="test_node",
            type="process",
            label="Test Node",
            line_number=10,
            details={"key": "value"},
            style={"color": "red"}
        )
        
        assert node.id == "test_node"
        assert node.type == "process"
        assert node.label == "Test Node"
        assert node.line_number == 10
        assert node.details == {"key": "value"}
        assert node.style == {"color": "red"}


class TestFlowEdge:
    """Test the FlowEdge dataclass."""
    
    def test_flow_edge_creation(self):
        """Test creating a FlowEdge."""
        edge = FlowEdge(
            from_node="start",
            to_node="end",
            label="process",
            condition="true",
            style={"color": "blue"}
        )
        
        assert edge.from_node == "start"
        assert edge.to_node == "end"
        assert edge.label == "process"
        assert edge.condition == "true"
        assert edge.style == {"color": "blue"}


class TestFlowBuilder:
    """Test the FlowBuilder functionality."""
    
    def setup_method(self):
        self.builder = FlowBuilder()
    
    def test_build_flow_simple_function(self):
        """Test building flow for a simple function."""
        function_node = FunctionNode(
            name="simple_function",
            line_number=1,
            docstring="Simple function",
            parameters=["x"],
            return_type="int",
            calls=[],
            variables=["x"],
            control_flow=[],
            imports=[],
            complexity_score=1
        )
        
        result = self.builder.build_flow(function_node)
        
        assert 'nodes' in result
        assert 'edges' in result
        assert 'metadata' in result
        
        # Should have start and end nodes
        node_ids = [node['id'] for node in result['nodes']]
        assert any('start' in node_id for node_id in node_ids)
        assert any('end' in node_id for node_id in node_ids)
        
        # Should have at least one edge connecting start to end
        assert len(result['edges']) >= 1
    
    def test_build_flow_with_control_flow(self):
        """Test building flow for a function with control flow."""
        function_node = FunctionNode(
            name="complex_function",
            line_number=1,
            docstring="Complex function",
            parameters=["x"],
            return_type="int",
            calls=["print"],
            variables=["x", "i"],
            control_flow=[
                {"type": "if", "condition": "x > 0", "line": 2, "has_else": False},
                {"type": "for", "iterator": "i", "iterable": "range(x)", "line": 3}
            ],
            imports=[],
            complexity_score=3
        )
        
        result = self.builder.build_flow(function_node)
        
        # Should have start, end, decision, loop, and call nodes
        node_types = [node['type'] for node in result['nodes']]
        assert 'start' in node_types
        assert 'end' in node_types
        assert 'decision' in node_types
        assert 'loop' in node_types
        assert 'call' in node_types
        
        # Should have multiple edges
        assert len(result['edges']) > 1
    
    def test_build_flow_with_function_calls(self):
        """Test building flow for a function with function calls."""
        function_node = FunctionNode(
            name="function_with_calls",
            line_number=1,
            docstring="Function with calls",
            parameters=[],
            return_type="str",
            calls=["print", "len", "str.upper"],
            variables=["result"],
            control_flow=[],
            imports=[],
            complexity_score=4
        )
        
        result = self.builder.build_flow(function_node)
        
        # Should have call nodes for each function call
        call_nodes = [node for node in result['nodes'] if node['type'] == 'call']
        assert len(call_nodes) == 3
        
        # Should have edges connecting the calls
        assert len(result['edges']) >= 3
    
    def test_build_flow_with_try_except(self):
        """Test building flow for a function with try-except."""
        function_node = FunctionNode(
            name="function_with_try",
            line_number=1,
            docstring="Function with try-except",
            parameters=[],
            return_type="str",
            calls=[],
            variables=["x"],
            control_flow=[
                {"type": "try", "line": 2, "has_except": True, "has_finally": False}
            ],
            imports=[],
            complexity_score=2
        )
        
        result = self.builder.build_flow(function_node)
        
        # Should have a try node
        try_nodes = [node for node in result['nodes'] if node['type'] == 'process' and 'Try' in node['label']]
        assert len(try_nodes) == 1
        
        # Check try node details
        try_node = try_nodes[0]
        assert try_node['details']['has_except'] is True
        assert try_node['details']['has_finally'] is False
    
    def test_node_to_dict(self):
        """Test converting FlowNode to dictionary."""
        node = FlowNode(
            id="test",
            type="process",
            label="Test",
            line_number=1,
            details={"key": "value"},
            style={"color": "red"}
        )
        
        result = self.builder._node_to_dict(node)
        
        assert result['id'] == "test"
        assert result['type'] == "process"
        assert result['label'] == "Test"
        assert result['line_number'] == 1
        assert result['details'] == {"key": "value"}
        assert result['style'] == {"color": "red"}
    
    def test_edge_to_dict(self):
        """Test converting FlowEdge to dictionary."""
        edge = FlowEdge(
            from_node="start",
            to_node="end",
            label="process",
            condition="true",
            style={"color": "blue"}
        )
        
        result = self.builder._edge_to_dict(edge)
        
        assert result['from'] == "start"
        assert result['to'] == "end"
        assert result['label'] == "process"
        assert result['condition'] == "true"
        assert result['style'] == {"color": "blue"}
    
    def test_create_start_node(self):
        """Test creating a start node."""
        function_node = FunctionNode(
            name="test_function",
            line_number=10,
            docstring="Test",
            parameters=["x"],
            return_type="int",
            calls=[],
            variables=[],
            control_flow=[],
            imports=[],
            complexity_score=1
        )
        
        start_node = self.builder._create_start_node(function_node)
        
        assert start_node.type == "start"
        assert "test_function" in start_node.label
        assert start_node.line_number == 10
        assert start_node.details['function_name'] == "test_function"
        assert start_node.details['parameters'] == ["x"]
        assert start_node.details['return_type'] == "int"
    
    def test_create_end_node(self):
        """Test creating an end node."""
        function_node = FunctionNode(
            name="test_function",
            line_number=10,
            docstring="Test",
            parameters=[],
            return_type=None,
            calls=[],
            variables=[],
            control_flow=[],
            imports=[],
            complexity_score=1
        )
        
        end_node = self.builder._create_end_node(function_node)
        
        assert end_node.type == "end"
        assert "test_function" in end_node.label
        assert end_node.details['function_name'] == "test_function"
    
    def test_create_call_node(self):
        """Test creating a call node."""
        call_node = self.builder._create_call_node("print")
        
        assert call_node.type == "call"
        assert "print" in call_node.label
        assert call_node.details['function_name'] == "print"
