"""
Tests for AST Parser functionality.
"""

import pytest
import ast
from ..utils.ast_parser import ASTParser, FunctionNode, FunctionASTVisitor
from .test_functions import (
    simple_test_function,
    complex_test_function,
    imports_test_function,
    try_test_function
)


class TestFunctionASTVisitor:
    """Test the AST visitor functionality."""
    
    def test_visit_call(self):
        """Test function call detection."""
        visitor = FunctionASTVisitor()
        
        # Create a simple call node
        call_node = ast.Call(
            func=ast.Name(id='print', ctx=ast.Load()),
            args=[ast.Constant(value='hello')],
            keywords=[]
        )
        
        visitor.visit(call_node)
        assert 'print' in visitor.function_calls
    
    def test_visit_assign(self):
        """Test variable assignment detection."""
        visitor = FunctionASTVisitor()
        
        # Create an assignment node
        assign_node = ast.Assign(
            targets=[ast.Name(id='x', ctx=ast.Store())],
            value=ast.Constant(value=42)
        )
        
        visitor.visit(assign_node)
        assert 'x' in visitor.variables
    
    def test_visit_if(self):
        """Test if statement detection."""
        visitor = FunctionASTVisitor()
        
        # Create an if node
        if_node = ast.If(
            test=ast.Compare(
                left=ast.Name(id='x', ctx=ast.Load()),
                ops=[ast.Lt()],
                comparators=[ast.Constant(value=10)]
            ),
            body=[],
            orelse=[]
        )
        
        visitor.visit(if_node)
        assert len(visitor.control_flow) == 1
        assert visitor.control_flow[0]['type'] == 'if'
        assert visitor.complexity_score == 2  # 1 for function + 1 for if
    
    def test_visit_for(self):
        """Test for loop detection."""
        visitor = FunctionASTVisitor()
        
        # Create a for loop node
        for_node = ast.For(
            target=ast.Name(id='i', ctx=ast.Store()),
            iter=ast.Call(
                func=ast.Name(id='range', ctx=ast.Load()),
                args=[ast.Constant(value=10)],
                keywords=[]
            ),
            body=[],
            orelse=[]
        )
        
        visitor.visit(for_node)
        assert len(visitor.control_flow) == 1
        assert visitor.control_flow[0]['type'] == 'for'
        assert visitor.control_flow[0]['iterator'] == 'i'
        assert visitor.complexity_score == 3  # 1 for function + 1 for for + 1 for range call


class TestASTParser:
    """Test the main AST parser functionality."""
    
    def setup_method(self):
        self.parser = ASTParser()
    
    def test_analyze_simple_function(self):
        """Test analysis of a simple function."""
        result = self.parser.analyze_function(simple_test_function)
        
        assert isinstance(result, FunctionNode)
        assert result.name == 'simple_test_function'
        assert result.parameters == ['x', 'y']
        assert result.docstring == 'Add two numbers.'
        assert result.complexity_score == 1  # Just the function itself
    
    def test_analyze_function_with_control_flow(self):
        """Test analysis of a function with control flow."""
        result = self.parser.analyze_function(complex_test_function)
        
        assert result.name == 'complex_test_function'
        assert result.parameters == ['x']
        assert len(result.control_flow) == 3  # if, for, if
        assert 'print' in result.calls
        assert 'range' in result.calls
        # Note: 'i' is not tracked as a variable because it's a for loop target, not an assignment
        assert result.complexity_score >= 4  # function + if + for + if
    
    def test_analyze_function_with_exceptions(self):
        """Test analysis of a function with exception handling."""
        result = self.parser.analyze_function(try_test_function)
        
        assert result.name == 'try_test_function'
        assert len(result.control_flow) == 1  # try block
        assert result.control_flow[0]['type'] == 'try'
        assert result.control_flow[0]['has_except'] is True
        assert result.control_flow[0]['has_finally'] is True
    
    def test_analyze_function_with_imports(self):
        """Test analysis of a function that uses imports."""
        result = self.parser.analyze_function(imports_test_function)
        
        assert result.name == 'imports_test_function'
        assert 'os' in result.imports
        assert 'datetime.datetime' in result.imports
        assert 'os.path.join' in result.calls
    
    def test_analyze_function_error_handling(self):
        """Test error handling for invalid functions."""
        # Test with a non-function object
        result = self.parser.analyze_function("not_a_function")
        
        assert result.name == 'unknown'
        assert result.parameters == []
        assert result.complexity_score == 1


class TestFunctionNode:
    """Test the FunctionNode dataclass."""
    
    def test_function_node_creation(self):
        """Test creating a FunctionNode."""
        node = FunctionNode(
            name="test_function",
            line_number=10,
            docstring="Test function",
            parameters=["x", "y"],
            return_type="int",
            calls=["print", "len"],
            variables=["x", "y", "result"],
            control_flow=[{"type": "if", "condition": "x > 0"}],
            imports=["os"],
            complexity_score=5
        )
        
        assert node.name == "test_function"
        assert node.line_number == 10
        assert node.docstring == "Test function"
        assert node.parameters == ["x", "y"]
        assert node.return_type == "int"
        assert node.calls == ["print", "len"]
        assert node.variables == ["x", "y", "result"]
        assert len(node.control_flow) == 1
        assert node.imports == ["os"]
        assert node.complexity_score == 5
