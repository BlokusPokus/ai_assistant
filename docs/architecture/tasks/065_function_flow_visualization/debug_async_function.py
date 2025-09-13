#!/usr/bin/env python3
"""Debug async function analysis."""

import sys
import os
import inspect
import ast

# Add the analysis module to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Add the main project to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from analysis.utils.ast_parser import ASTParser
from personal_assistant.tools.notes.enhanced_notes_tool import EnhancedNotesTool

def test_async_function():
    """Test function to compare with async function."""
    def simple_function(x, y):
        """Add two numbers."""
        return x + y
    
    return simple_function

async def test_async_function_2():
    """Test async function."""
    def inner_function(x):
        if x > 0:
            return x * 2
        else:
            return 0
    
    return inner_function

def main():
    """Debug async function analysis."""
    print('Debugging Async Function Analysis')
    print('=' * 50)
    
    # Test with regular function
    print('1. Testing regular function:')
    regular_func = test_async_function()
    parser = ASTParser()
    result = parser.analyze_function(regular_func)
    print(f'  Name: {result.name}')
    print(f'  Parameters: {result.parameters}')
    print(f'  Docstring: {result.docstring}')
    print(f'  Calls: {result.calls}')
    print(f'  Variables: {result.variables}')
    print(f'  Control flow: {len(result.control_flow)}')
    print()
    
    # Test with async function
    print('2. Testing async function:')
    async_func = test_async_function_2
    result = parser.analyze_function(async_func)
    print(f'  Name: {result.name}')
    print(f'  Parameters: {result.parameters}')
    print(f'  Docstring: {result.docstring}')
    print(f'  Calls: {result.calls}')
    print(f'  Variables: {result.variables}')
    print(f'  Control flow: {len(result.control_flow)}')
    print()
    
    # Test with the actual create_enhanced_note function
    print('3. Testing create_enhanced_note function:')
    enhanced_notes = EnhancedNotesTool()
    create_func = enhanced_notes.create_enhanced_note
    result = parser.analyze_function(create_func)
    print(f'  Name: {result.name}')
    print(f'  Parameters: {result.parameters}')
    print(f'  Docstring: {result.docstring}')
    print(f'  Calls: {result.calls}')
    print(f'  Variables: {result.variables}')
    print(f'  Control flow: {len(result.control_flow)}')
    print()
    
    # Debug the source code
    print('4. Debugging source code:')
    try:
        source = inspect.getsource(create_func)
        print(f'  Source length: {len(source)} characters')
        print(f'  First 200 chars: {source[:200]}...')
        
        # Parse AST
        tree = ast.parse(source)
        print(f'  AST tree type: {type(tree)}')
        print(f'  AST body length: {len(tree.body)}')
        
        # Find function definition
        for node in ast.walk(tree):
            if isinstance(node, ast.AsyncFunctionDef):
                print(f'  Found async function: {node.name}')
                print(f'  Parameters: {[arg.arg for arg in node.args.args]}')
                print(f'  Body statements: {len(node.body)}')
                break
        else:
            print('  No async function found in AST')
            
    except Exception as e:
        print(f'  Error getting source: {e}')

if __name__ == '__main__':
    main()
