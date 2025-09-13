"""
AST Parser for function flow analysis.

This module provides functionality to parse Python functions using the AST module,
extracting function structure, dependencies, and control flow information.
"""

import ast
import inspect
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass


@dataclass
class FunctionNode:
    """Represents a parsed function with all its structural information."""
    name: str
    line_number: int
    docstring: Optional[str]
    parameters: List[str]
    return_type: Optional[str]
    calls: List[str]
    variables: List[str]
    control_flow: List[Dict[str, Any]]
    imports: List[str]
    complexity_score: int


class FunctionASTVisitor(ast.NodeVisitor):
    """AST visitor to extract function information from parsed code."""
    
    def __init__(self):
        self.function_calls: List[str] = []
        self.variables: List[str] = []
        self.control_flow: List[Dict[str, Any]] = []
        self.imports: List[str] = []
        self.complexity_score: int = 1  # Start with 1 for the function itself
        
    def visit_Call(self, node: ast.Call) -> None:
        """Visit function calls and extract call information."""
        call_name = self._get_call_name(node)
        if call_name:
            self.function_calls.append(call_name)
        
        # Increase complexity for function calls
        self.complexity_score += 1
        
        self.generic_visit(node)
    
    def visit_Assign(self, node: ast.Assign) -> None:
        """Visit variable assignments and extract variable names."""
        for target in node.targets:
            if isinstance(target, ast.Name):
                self.variables.append(target.id)
            elif isinstance(target, ast.Tuple):
                # Handle tuple unpacking: a, b = something
                for elt in target.elts:
                    if isinstance(elt, ast.Name):
                        self.variables.append(elt.id)
        
        self.generic_visit(node)
    
    def visit_If(self, node: ast.If) -> None:
        """Visit if statements and extract control flow information."""
        condition = self._get_condition_string(node.test)
        self.control_flow.append({
            'type': 'if',
            'condition': condition,
            'line': getattr(node, 'lineno', 0),
            'has_else': node.orelse is not None and len(node.orelse) > 0
        })
        
        # Increase complexity for if statements
        self.complexity_score += 1
        
        self.generic_visit(node)
    
    def visit_For(self, node: ast.For) -> None:
        """Visit for loops and extract control flow information."""
        iterator = self._get_target_string(node.target)
        iterable = self._get_expression_string(node.iter)
        
        self.control_flow.append({
            'type': 'for',
            'iterator': iterator,
            'iterable': iterable,
            'line': getattr(node, 'lineno', 0)
        })
        
        # Increase complexity for for loops
        self.complexity_score += 1
        
        self.generic_visit(node)
    
    def visit_While(self, node: ast.While) -> None:
        """Visit while loops and extract control flow information."""
        condition = self._get_condition_string(node.test)
        
        self.control_flow.append({
            'type': 'while',
            'condition': condition,
            'line': getattr(node, 'lineno', 0)
        })
        
        # Increase complexity for while loops
        self.complexity_score += 1
        
        self.generic_visit(node)
    
    def visit_Try(self, node: ast.Try) -> None:
        """Visit try-except blocks and extract control flow information."""
        self.control_flow.append({
            'type': 'try',
            'line': getattr(node, 'lineno', 0),
            'has_except': len(node.handlers) > 0,
            'has_finally': node.finalbody is not None and len(node.finalbody) > 0
        })
        
        # Increase complexity for try-except blocks
        self.complexity_score += 1
        
        self.generic_visit(node)
    
    def visit_Import(self, node: ast.Import) -> None:
        """Visit import statements."""
        for alias in node.names:
            self.imports.append(alias.name)
        
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Visit from-import statements."""
        module = node.module or ''
        for alias in node.names:
            if module:
                self.imports.append(f"{module}.{alias.name}")
            else:
                self.imports.append(alias.name)
        
        self.generic_visit(node)
    
    def visit_Return(self, node: ast.Return) -> None:
        """Visit return statements."""
        # Visit the return value expression
        if node.value:
            self.visit(node.value)
        
        self.generic_visit(node)
    
    def visit_Expr(self, node: ast.Expr) -> None:
        """Visit expression statements."""
        # Visit the expression value
        if node.value:
            self.visit(node.value)
        
        self.generic_visit(node)
    
    def _get_call_name(self, node: ast.Call) -> Optional[str]:
        """Extract the name of a function call."""
        if isinstance(node.func, ast.Name):
            return node.func.id
        elif isinstance(node.func, ast.Attribute):
            # Handle method calls like obj.method()
            value = self._get_expression_string(node.func.value)
            return f"{value}.{node.func.attr}"
        elif isinstance(node.func, ast.Call):
            # Handle chained calls like func()()
            return "chained_call"
        return None
    
    def _get_condition_string(self, node: ast.expr) -> str:
        """Convert a condition node to a string representation."""
        try:
            return ast.unparse(node)
        except:
            return "complex_condition"
    
    def _get_expression_string(self, node: ast.expr) -> str:
        """Convert an expression node to a string representation."""
        try:
            return ast.unparse(node)
        except:
            return "complex_expression"
    
    def _get_target_string(self, node: ast.expr) -> str:
        """Convert a target node to a string representation."""
        try:
            return ast.unparse(node)
        except:
            return "complex_target"


class ASTParser:
    """Main AST parser for analyzing Python functions."""
    
    def __init__(self):
        self.ast_visitor = FunctionASTVisitor()
    
    def analyze_function(self, func) -> FunctionNode:
        """
        Analyze a function and return its structure.
        
        Args:
            func: The function object to analyze
            
        Returns:
            FunctionNode: Complete function analysis
        """
        try:
            # Get function source code
            source = inspect.getsource(func)
            
            # Fix indentation issues for class methods
            lines = source.split('\n')
            if lines and lines[0].startswith('    '):
                # Remove common indentation
                min_indent = min(len(line) - len(line.lstrip()) for line in lines if line.strip())
                if min_indent > 0:
                    lines = [line[min_indent:] if line.strip() else line for line in lines]
                    source = '\n'.join(lines)
            
            # Parse the AST
            tree = ast.parse(source)
            
            # Reset visitor state
            self.ast_visitor = FunctionASTVisitor()
            
            # Find the function definition and visit its body
            function_found = False
            for node in ast.walk(tree):
                if (isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and 
                    node.name == func.__name__):
                    function_found = True
                    # Visit the function body
                    for stmt in node.body:
                        self.ast_visitor.visit(stmt)
                    break
            
            if not function_found:
                # If no function definition found, visit the entire tree
                self.ast_visitor.visit(tree)
            
            # Extract function metadata
            function_name = func.__name__
            line_number = func.__code__.co_firstlineno
            docstring = func.__doc__
            
            # Get parameters from function signature
            sig = inspect.signature(func)
            parameters = list(sig.parameters.keys())
            
            # Get return type annotation
            return_type = self._get_return_type(func)
            
            # Remove duplicates and sort
            calls = sorted(list(set(self.ast_visitor.function_calls)))
            variables = sorted(list(set(self.ast_visitor.variables)))
            imports = sorted(list(set(self.ast_visitor.imports)))
            
            return FunctionNode(
                name=function_name,
                line_number=line_number,
                docstring=docstring,
                parameters=parameters,
                return_type=return_type,
                calls=calls,
                variables=variables,
                control_flow=self.ast_visitor.control_flow,
                imports=imports,
                complexity_score=self.ast_visitor.complexity_score
            )
            
        except Exception as e:
            # Return a minimal FunctionNode if parsing fails
            return FunctionNode(
                name=getattr(func, '__name__', 'unknown'),
                line_number=0,
                docstring=None,
                parameters=[],
                return_type=None,
                calls=[],
                variables=[],
                control_flow=[],
                imports=[],
                complexity_score=1
            )
    
    def _get_return_type(self, func) -> Optional[str]:
        """Extract return type annotation if available."""
        if hasattr(func, '__annotations__') and 'return' in func.__annotations__:
            return str(func.__annotations__['return'])
        return None
    
    def analyze_file(self, file_path: str, function_name: str) -> Optional[FunctionNode]:
        """
        Analyze a function from a file.
        
        Args:
            file_path: Path to the Python file
            function_name: Name of the function to analyze
            
        Returns:
            FunctionNode or None if function not found
        """
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("module", file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            if hasattr(module, function_name):
                func = getattr(module, function_name)
                return self.analyze_function(func)
            
        except Exception as e:
            print(f"Error analyzing file {file_path}: {e}")
            
        return None
