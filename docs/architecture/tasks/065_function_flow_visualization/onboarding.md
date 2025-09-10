# Onboarding Guide: Function Flow Visualization Tool

## 🎯 **Task Context**

You are implementing a function flow visualization tool that creates visual diagrams showing how selected functions execute, their dependencies, and internal structure. This tool will help developers understand complex code by providing clear visual representations.

## 📚 **Codebase Exploration**

### **1. Current Tools Architecture**

**Location**: `src/personal_assistant/tools/`

**Key Files to Study**:

- `src/personal_assistant/tools/base.py` - Base tool interface
- `src/personal_assistant/tools/__init__.py` - Tool registry
- `src/personal_assistant/tools/notes/enhanced_notes_tool.py` - Example of complex tool
- `src/personal_assistant/tools/ltm/ltm_tool.py` - Example of analysis tool

**Understanding**:

- All tools inherit from `BaseTool`
- Tools are registered in the `__init__.py` file
- Tools have standardized interfaces for execution
- Tools can have complex internal logic and external dependencies

### **2. Frontend Architecture**

**Location**: `src/apps/frontend/src/`

**Key Files to Study**:

- `src/apps/frontend/src/components/` - React components
- `src/apps/frontend/src/types/` - TypeScript type definitions
- `src/apps/frontend/src/utils/` - Utility functions

**Understanding**:

- React-based frontend with TypeScript
- Component-based architecture
- Integration with backend through API calls
- Existing visualization patterns (if any)

### **3. Analysis and Parsing**

**Location**: `src/personal_assistant/`

**Key Areas to Explore**:

- `src/personal_assistant/llm/` - LLM integration patterns
- `src/personal_assistant/rag/` - Analysis and processing patterns
- `src/personal_assistant/memory/` - Data processing patterns

**Understanding**:

- How the system processes and analyzes data
- Existing patterns for code analysis
- Integration with external services

## 🔧 **Technical Implementation Details**

### **Phase 1: Function Analysis Engine**

#### **1.1 AST Parser Implementation**

**File**: `src/personal_assistant/tools/analysis/utils/ast_parser.py`

```python
import ast
import inspect
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

@dataclass
class FunctionNode:
    name: str
    line_number: int
    docstring: Optional[str]
    parameters: List[str]
    return_type: Optional[str]
    calls: List[str]
    variables: List[str]
    control_flow: List[Dict[str, Any]]

class ASTParser:
    def __init__(self):
        self.ast_visitor = FunctionASTVisitor()

    def analyze_function(self, func) -> FunctionNode:
        """Analyze a function and return its structure"""
        source = inspect.getsource(func)
        tree = ast.parse(source)

        # Walk the AST to extract information
        self.ast_visitor.visit(tree)

        return FunctionNode(
            name=func.__name__,
            line_number=func.__code__.co_firstlineno,
            docstring=func.__doc__,
            parameters=list(func.__code__.co_varnames[:func.__code__.co_argcount]),
            return_type=self._get_return_type(func),
            calls=self.ast_visitor.function_calls,
            variables=self.ast_visitor.variables,
            control_flow=self.ast_visitor.control_flow
        )

    def _get_return_type(self, func) -> Optional[str]:
        """Extract return type annotation if available"""
        if hasattr(func, '__annotations__') and 'return' in func.__annotations__:
            return str(func.__annotations__['return'])
        return None

class FunctionASTVisitor(ast.NodeVisitor):
    def __init__(self):
        self.function_calls = []
        self.variables = []
        self.control_flow = []

    def visit_Call(self, node):
        """Visit function calls"""
        if isinstance(node.func, ast.Name):
            self.function_calls.append(node.func.id)
        elif isinstance(node.func, ast.Attribute):
            self.function_calls.append(f"{node.func.value.id}.{node.func.attr}")

        self.generic_visit(node)

    def visit_Assign(self, node):
        """Visit variable assignments"""
        for target in node.targets:
            if isinstance(target, ast.Name):
                self.variables.append(target.id)

        self.generic_visit(node)

    def visit_If(self, node):
        """Visit if statements"""
        self.control_flow.append({
            'type': 'if',
            'condition': ast.unparse(node.test),
            'line': node.lineno
        })
        self.generic_visit(node)

    def visit_For(self, node):
        """Visit for loops"""
        self.control_flow.append({
            'type': 'for',
            'iterator': ast.unparse(node.target),
            'iterable': ast.unparse(node.iter),
            'line': node.lineno
        })
        self.generic_visit(node)

    def visit_While(self, node):
        """Visit while loops"""
        self.control_flow.append({
            'type': 'while',
            'condition': ast.unparse(node.test),
            'line': node.lineno
        })
        self.generic_visit(node)
```

#### **1.2 Function Analyzer Service**

**File**: `src/personal_assistant/tools/analysis/function_analyzer.py`

```python
from typing import Dict, List, Any, Optional
from .utils.ast_parser import ASTParser, FunctionNode
from .utils.flow_builder import FlowBuilder

class FunctionAnalyzer:
    def __init__(self):
        self.ast_parser = ASTParser()
        self.flow_builder = FlowBuilder()

    def analyze_function(self, func) -> Dict[str, Any]:
        """Analyze a function and return comprehensive analysis"""
        # Parse the function
        function_node = self.ast_parser.analyze_function(func)

        # Build flow structure
        flow_structure = self.flow_builder.build_flow(function_node)

        # Generate analysis summary
        analysis = {
            'function_info': {
                'name': function_node.name,
                'line_number': function_node.line_number,
                'docstring': function_node.docstring,
                'parameters': function_node.parameters,
                'return_type': function_node.return_type
            },
            'dependencies': {
                'function_calls': function_node.calls,
                'variables_used': function_node.variables,
                'external_imports': self._extract_imports(func)
            },
            'control_flow': function_node.control_flow,
            'flow_structure': flow_structure,
            'complexity_metrics': self._calculate_complexity(function_node)
        }

        return analysis

    def _extract_imports(self, func) -> List[str]:
        """Extract external imports used by the function"""
        # Implementation to extract imports
        pass

    def _calculate_complexity(self, function_node: FunctionNode) -> Dict[str, int]:
        """Calculate complexity metrics for the function"""
        return {
            'cyclomatic_complexity': len(function_node.control_flow) + 1,
            'function_calls': len(function_node.calls),
            'variables': len(function_node.variables),
            'lines_of_code': function_node.line_number  # Simplified
        }
```

### **Phase 2: Flow Generation**

#### **2.1 Flow Builder**

**File**: `src/personal_assistant/tools/analysis/utils/flow_builder.py`

```python
from typing import Dict, List, Any
from dataclasses import dataclass

@dataclass
class FlowNode:
    id: str
    type: str  # 'start', 'end', 'process', 'decision', 'call'
    label: str
    line_number: int
    details: Dict[str, Any]

@dataclass
class FlowEdge:
    from_node: str
    to_node: str
    label: str
    condition: Optional[str] = None

class FlowBuilder:
    def __init__(self):
        self.nodes = []
        self.edges = []

    def build_flow(self, function_node) -> Dict[str, Any]:
        """Build flow structure from function analysis"""
        # Create start node
        start_node = FlowNode(
            id="start",
            type="start",
            label=f"Start: {function_node.name}",
            line_number=function_node.line_number,
            details={}
        )
        self.nodes.append(start_node)

        # Process control flow
        current_node_id = "start"

        for flow_item in function_node.control_flow:
            if flow_item['type'] == 'if':
                # Create decision node
                decision_node = FlowNode(
                    id=f"decision_{flow_item['line']}",
                    type="decision",
                    label=f"If: {flow_item['condition']}",
                    line_number=flow_item['line'],
                    details={'condition': flow_item['condition']}
                )
                self.nodes.append(decision_node)

                # Create edges
                self.edges.append(FlowEdge(
                    from_node=current_node_id,
                    to_node=decision_node.id,
                    label=""
                ))

                current_node_id = decision_node.id

            elif flow_item['type'] == 'for':
                # Create loop node
                loop_node = FlowNode(
                    id=f"loop_{flow_item['line']}",
                    type="process",
                    label=f"For: {flow_item['iterator']} in {flow_item['iterable']}",
                    line_number=flow_item['line'],
                    details={'iterator': flow_item['iterator'], 'iterable': flow_item['iterable']}
                )
                self.nodes.append(loop_node)

                self.edges.append(FlowEdge(
                    from_node=current_node_id,
                    to_node=loop_node.id,
                    label=""
                ))

                current_node_id = loop_node.id

        # Process function calls
        for call in function_node.calls:
            call_node = FlowNode(
                id=f"call_{call}",
                type="call",
                label=f"Call: {call}",
                line_number=0,  # Would need to track line numbers
                details={'function_name': call}
            )
            self.nodes.append(call_node)

            self.edges.append(FlowEdge(
                from_node=current_node_id,
                to_node=call_node.id,
                label=""
            ))

        # Create end node
        end_node = FlowNode(
            id="end",
            type="end",
            label=f"End: {function_node.name}",
            line_number=0,
            details={}
        )
        self.nodes.append(end_node)

        self.edges.append(FlowEdge(
            from_node=current_node_id,
            to_node="end",
            label=""
        ))

        return {
            'nodes': [self._node_to_dict(node) for node in self.nodes],
            'edges': [self._edge_to_dict(edge) for edge in self.edges]
        }

    def _node_to_dict(self, node: FlowNode) -> Dict[str, Any]:
        return {
            'id': node.id,
            'type': node.type,
            'label': node.label,
            'line_number': node.line_number,
            'details': node.details
        }

    def _edge_to_dict(self, edge: FlowEdge) -> Dict[str, Any]:
        return {
            'from': edge.from_node,
            'to': edge.to_node,
            'label': edge.label,
            'condition': edge.condition
        }
```

#### **2.2 Diagram Generator**

**File**: `src/personal_assistant/tools/analysis/flow_generator.py`

```python
import graphviz
from typing import Dict, List, Any
from .utils.flow_builder import FlowNode, FlowEdge

class FlowGenerator:
    def __init__(self):
        self.graph = None

    def generate_diagram(self, flow_data: Dict[str, Any], format: str = 'png') -> str:
        """Generate visual diagram from flow data"""
        # Create Graphviz graph
        self.graph = graphviz.Digraph(comment='Function Flow')
        self.graph.attr(rankdir='TB', size='8,6')

        # Add nodes
        for node_data in flow_data['nodes']:
            self._add_node(node_data)

        # Add edges
        for edge_data in flow_data['edges']:
            self._add_edge(edge_data)

        # Generate and return diagram
        return self.graph.pipe(format=format)

    def _add_node(self, node_data: Dict[str, Any]):
        """Add a node to the graph"""
        node_id = node_data['id']
        label = node_data['label']
        node_type = node_data['type']

        # Set node attributes based on type
        if node_type == 'start':
            self.graph.node(node_id, label=label, shape='ellipse', style='filled', fillcolor='lightgreen')
        elif node_type == 'end':
            self.graph.node(node_id, label=label, shape='ellipse', style='filled', fillcolor='lightcoral')
        elif node_type == 'decision':
            self.graph.node(node_id, label=label, shape='diamond', style='filled', fillcolor='lightblue')
        elif node_type == 'call':
            self.graph.node(node_id, label=label, shape='box', style='filled', fillcolor='lightyellow')
        else:
            self.graph.node(node_id, label=label, shape='box')

    def _add_edge(self, edge_data: Dict[str, Any]):
        """Add an edge to the graph"""
        from_node = edge_data['from']
        to_node = edge_data['to']
        label = edge_data['label']
        condition = edge_data.get('condition')

        if condition:
            self.graph.edge(from_node, to_node, label=f"{label}\n{condition}")
        else:
            self.graph.edge(from_node, to_node, label=label)
```

### **Phase 3: Tool Integration**

#### **3.1 Main Tool Implementation**

**File**: `src/personal_assistant/tools/analysis/function_flow_tool.py`

```python
from typing import Dict, Any, Optional
from ..base import BaseTool
from .function_analyzer import FunctionAnalyzer
from .flow_generator import FlowGenerator

class FunctionFlowTool(BaseTool):
    def __init__(self):
        super().__init__()
        self.name = "function_flow_visualizer"
        self.description = "Generate visual flow diagrams for selected functions"
        self.analyzer = FunctionAnalyzer()
        self.generator = FlowGenerator()

    def execute(self, function_name: str, module_path: str, **kwargs) -> Dict[str, Any]:
        """Execute function flow analysis and visualization"""
        try:
            # Import the function
            func = self._import_function(module_path, function_name)

            # Analyze the function
            analysis = self.analyzer.analyze_function(func)

            # Generate diagram
            diagram_data = self.generator.generate_diagram(analysis['flow_structure'])

            return {
                'success': True,
                'function_name': function_name,
                'analysis': analysis,
                'diagram_data': diagram_data,
                'message': f"Successfully analyzed function {function_name}"
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f"Failed to analyze function {function_name}"
            }

    def _import_function(self, module_path: str, function_name: str):
        """Import function from module path"""
        import importlib
        module = importlib.import_module(module_path)
        return getattr(module, function_name)

    def get_supported_formats(self) -> List[str]:
        """Get list of supported export formats"""
        return ['png', 'svg', 'pdf', 'mermaid']

    def export_diagram(self, flow_data: Dict[str, Any], format: str) -> bytes:
        """Export diagram in specified format"""
        return self.generator.generate_diagram(flow_data, format)
```

## 🧪 **Testing Strategy**

### **1. Unit Tests**

**File**: `tests/unit/test_tools/test_function_flow_tool.py`

```python
import pytest
from unittest.mock import Mock, patch
from src.personal_assistant.tools.analysis.function_flow_tool import FunctionFlowTool

class TestFunctionFlowTool:
    def setup_method(self):
        self.tool = FunctionFlowTool()

    def test_analyze_simple_function(self):
        """Test analysis of a simple function"""
        # Mock function
        def simple_function(x, y):
            return x + y

        # Test analysis
        result = self.tool.execute("simple_function", "__main__")

        assert result['success'] is True
        assert 'analysis' in result
        assert 'diagram_data' in result

    def test_analyze_complex_function(self):
        """Test analysis of a complex function with control flow"""
        def complex_function(data):
            if data:
                for item in data:
                    if item > 0:
                        result = item * 2
                    else:
                        result = 0
                return result
            return None

        result = self.tool.execute("complex_function", "__main__")

        assert result['success'] is True
        assert len(result['analysis']['control_flow']) > 0

    def test_error_handling(self):
        """Test error handling for invalid function"""
        result = self.tool.execute("nonexistent_function", "nonexistent_module")

        assert result['success'] is False
        assert 'error' in result
```

### **2. Integration Tests**

**File**: `tests/integration/test_function_flow_integration.py`

```python
import pytest
from src.personal_assistant.tools.analysis.function_flow_tool import FunctionFlowTool

class TestFunctionFlowIntegration:
    def test_end_to_end_workflow(self):
        """Test complete workflow from function selection to diagram generation"""
        tool = FunctionFlowTool()

        # Test with a real function from the codebase
        result = tool.execute("analyze_function", "src.personal_assistant.tools.analysis.function_analyzer")

        assert result['success'] is True
        assert 'diagram_data' in result
        assert len(result['diagram_data']) > 0
```

## 🚀 **Getting Started**

### **1. Environment Setup**

```bash
# Install required dependencies
pip install graphviz
pip install ast-tools

# Install development dependencies
pip install pytest pytest-cov
```

### **2. Development Workflow**

1. **Start with AST Parser**: Implement basic function parsing
2. **Add Flow Builder**: Create flow structure from parsed data
3. **Implement Diagram Generator**: Generate visual representations
4. **Create Tool Interface**: Integrate with existing tool system
5. **Add Frontend Components**: Create interactive visualization
6. **Implement Export Features**: Add multiple export formats

### **3. Testing Approach**

1. **Unit Tests First**: Test each component individually
2. **Integration Tests**: Test complete workflows
3. **Performance Tests**: Test with large, complex functions
4. **User Acceptance Tests**: Test with real-world functions

## 📚 **Key Resources**

### **AST Parsing**

- [Python AST Documentation](https://docs.python.org/3/library/ast.html)
- [AST Visitor Pattern](https://docs.python.org/3/library/ast.html#ast.NodeVisitor)

### **Graph Visualization**

- [Graphviz Documentation](https://graphviz.org/documentation/)
- [Mermaid Documentation](https://mermaid-js.github.io/mermaid/)

### **Frontend Integration**

- [React D3 Integration](https://react-d3-library.com/)
- [Cytoscape.js](https://js.cytoscape.org/) for interactive graphs

## 🔄 **Next Steps**

1. **Review this onboarding guide** and ask questions if needed
2. **Set up development environment** with required dependencies
3. **Start with Phase 1**: Implement AST parser and basic analysis
4. **Create unit tests** for each component
5. **Iterate and improve** based on testing results

---

**Remember**: Start simple and build complexity gradually. Focus on getting basic visualization working first, then add advanced features.
