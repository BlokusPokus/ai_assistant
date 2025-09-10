#!/usr/bin/env python3
"""
Demo script for Function Flow Visualization Tool.

This script demonstrates the basic functionality of the function flow visualization tool.
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from analysis.function_flow_tool import FunctionFlowTool


def demo_function_1(x, y):
    """Simple function that adds two numbers."""
    return x + y


def demo_function_2(x):
    """Function with control flow."""
    if x > 0:
        for i in range(x):
            if i % 2 == 0:
                print(f"Even number: {i}")
        return x * 2
    else:
        return 0


def demo_function_3(data):
    """Function with exception handling."""
    try:
        result = []
        for item in data:
            if item > 0:
                result.append(item * 2)
            else:
                result.append(0)
        return result
    except Exception as e:
        print(f"Error: {e}")
        return []


def main():
    """Run the demo."""
    print("Function Flow Visualization Tool Demo")
    print("=" * 50)
    
    # Initialize the tool
    tool = FunctionFlowTool()
    
    # Test functions
    test_functions = [
        ("Simple Function", demo_function_1),
        ("Control Flow Function", demo_function_2),
        ("Exception Handling Function", demo_function_3)
    ]
    
    for name, func in test_functions:
        print(f"\nAnalyzing: {name}")
        print("-" * 30)
        
        try:
            # Analyze and visualize
            result = tool.analyze_and_visualize(func, output_format='svg')
            
            if result['success']:
                print("✅ Analysis successful!")
                
                # Print basic info
                func_info = result['function_info']
                print(f"Function: {func_info['name']}")
                print(f"Parameters: {', '.join(func_info['parameters'])}")
                print(f"Return Type: {func_info['return_type'] or 'Not specified'}")
                print(f"Docstring: {func_info['docstring'] or 'None'}")
                
                # Print complexity metrics
                complexity = result['complexity_metrics']
                print(f"Complexity Score: {complexity['cyclomatic_complexity']}")
                print(f"Function Calls: {complexity['function_calls_count']}")
                print(f"Variables: {complexity['variables_count']}")
                print(f"Control Flow Structures: {complexity['control_flow_count']}")
                
                # Print dependencies
                deps = result['dependencies']
                if deps['function_calls']:
                    print(f"Function Calls: {', '.join(deps['function_calls'])}")
                if deps['variables_used']:
                    print(f"Variables Used: {', '.join(deps['variables_used'])}")
                
                # Print flow structure info
                flow_meta = result['flow_structure']['metadata']
                print(f"Flow Nodes: {flow_meta['total_nodes']}")
                print(f"Flow Edges: {flow_meta['total_edges']}")
                
                # Save diagram
                output_file = f"{func.__name__}_flow.svg"
                with open(output_file, 'w') as f:
                    f.write(result['diagram']['data'])
                print(f"Diagram saved to: {output_file}")
                
            else:
                print(f"❌ Analysis failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Error analyzing {name}: {e}")
    
    print("\n" + "=" * 50)
    print("Demo completed!")
    print("\nGenerated files:")
    for name, func in test_functions:
        output_file = f"{func.__name__}_flow.svg"
        if os.path.exists(output_file):
            print(f"  - {output_file}")


if __name__ == "__main__":
    main()
