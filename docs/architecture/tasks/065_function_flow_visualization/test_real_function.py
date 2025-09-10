#!/usr/bin/env python3
"""Test the function flow visualization tool with a real function."""

import sys
import os

# Add the analysis module to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Add the main project to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from analysis.function_flow_tool import FunctionFlowTool
from personal_assistant.tools.notes.enhanced_notes_tool import EnhancedNotesTool

def main():
    """Test with the create_enhanced_note function."""
    print('Function Flow Visualization Tool - Real Function Test')
    print('=' * 60)
    
    try:
        # Create the tool
        tool = FunctionFlowTool()
        
        # Get the create_enhanced_note function
        enhanced_notes = EnhancedNotesTool()
        create_enhanced_note_func = enhanced_notes.create_enhanced_note
        
        print('Analyzing create_enhanced_note function...')
        print('-' * 40)
        
        # Analyze and visualize the function
        result = tool.analyze_and_visualize(
            create_enhanced_note_func,
            output_format='svg',
            output_file='create_enhanced_note_flow.svg'
        )
        
        if result['success']:
            print('✅ Analysis successful!')
            print(f'Function: {result["function_info"]["name"]}')
            print(f'Parameters: {result["function_info"]["parameters"]}')
            print(f'Return Type: {result["function_info"]["return_type"]}')
            docstring = result["function_info"]["docstring"]
            if docstring:
                print(f'Docstring: {docstring[:100]}...')
            else:
                print('Docstring: None')
            print(f'Complexity Score: {result["complexity_metrics"]["cyclomatic_complexity"]}')
            print(f'Function Calls: {len(result["dependencies"]["function_calls"])}')
            print(f'Variables: {len(result["dependencies"]["variables_used"])}')
            print(f'Control Flow Structures: {len(result["control_flow"])}')
            print(f'Flow Nodes: {len(result["flow_structure"]["nodes"])}')
            print(f'Flow Edges: {len(result["flow_structure"]["edges"])}')
            print(f'Diagram saved to: {result["diagram"]["file_path"]}')
            
            print('\nFunction Calls:')
            for call in result['dependencies']['function_calls']:
                print(f'  • {call}')
            
            print('\nControl Flow Structures:')
            for cf in result['control_flow']:
                print(f'  • {cf["type"]} - {cf.get("condition", "N/A")}')
            
            print('\nFlow Structure:')
            print('Nodes:')
            for node in result['flow_structure']['nodes']:
                print(f'  • {node["id"]}: {node["label"]}')
            
            print('Edges:')
            for edge in result['flow_structure']['edges']:
                print(f'  • {edge["from"]} -> {edge["to"]}')
                
        else:
            print('❌ Analysis failed!')
            print(f'Error: {result["error"]}')
            
    except Exception as e:
        print(f'❌ Error during analysis: {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
