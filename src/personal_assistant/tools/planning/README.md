# LLM Planner Tool

## 🎯 Overview

The LLM Planner Tool is an intelligent task planning system that creates step-by-step plans for completing user requests. It uses LLM analysis to provide contextual guidance, tool recommendations, and ADHD-friendly execution strategies. **NEW**: Automatically includes relevant tool guidelines for better execution!

## 🚀 Features

### **Intelligent Planning**

- Analyzes user requests to understand requirements
- Breaks complex tasks into manageable steps
- Recommends appropriate tools for each step
- Provides context-specific guidance

### **🆕 Automatic Tool Guidelines Integration**

- **Automatically detects** which tools are relevant to the task
- **Loads tool guidelines** from markdown files (e.g., `notion_notes_guidelines.md`)
- **Includes best practices** directly in the planning context
- **Provides specific guidance** for tool usage based on guidelines
- **Makes plans actionable** with real tool-specific advice

### **ADHD-Friendly Design**

- Clear, structured step-by-step plans
- Progress tracking and motivation
- Time estimates for each step
- Visual organization with emojis and headers

### **Tool Integration**

- Works with your existing tool registry
- Provides tool-specific guidance
- Considers tool dependencies and capabilities
- Suggests optimal execution order

### **Flexible Planning Styles**

- **ADHD-Friendly**: Motivational, structured, with progress tracking
- **Detailed**: Comprehensive explanations and alternatives
- **Concise**: Brief, action-oriented plans

## 🛠️ Installation & Setup

### **1. Basic Setup**

```python
from .tools.planning import LLMPlannerTool

# Initialize the planner with guidelines path
planner = LLMPlannerTool(guidelines_path="src/personal_assistant/tools")

# Set your LLM client
planner.set_llm_client(your_llm_client)

# Add to tool registry
for tool in planner:
    tool_registry.register_tool(tool)
```

### **2. Guidelines Setup**

The planner automatically looks for guideline files in the format `{tool_name}_guidelines.md`:

```
src/personal_assistant/tools/
├── notes/
│   └── notion_notes_guidelines.md    # ✅ Will be loaded automatically
├── search/
│   └── codebase_search_guidelines.md # ✅ Will be loaded automatically
└── planning/
    └── llm_planner.py                # The planner itself
```

## 📋 Usage Examples

### **Basic Planning with Guidelines**

```python
# Create a plan that automatically includes relevant tool guidelines
plan = await planner.create_intelligent_plan(
    user_request="Help me create a meeting note template",
    planning_style="adhd_friendly",
    include_guidelines=True  # ✅ Automatically includes Notion notes guidelines
)
```

### **Planning with Tool Context and Guidelines**

```python
# Create a plan with detailed tool information AND guidelines
plan = await planner.create_plan_with_tool_context(
    user_request="Create a project note with proper structure",
    tool_registry=your_tool_registry,
    user_context="I'm a project manager organizing team documentation",
    planning_style="detailed",
    include_guidelines=True  # ✅ Includes both tool info and guidelines
)
```

### **Planning Without Guidelines (for comparison)**

```python
# Create a basic plan without tool-specific guidelines
plan = await planner.create_intelligent_plan(
    user_request="Organize my project files",
    planning_style="concise",
    include_guidelines=False  # ❌ No tool guidelines included
)
```

## 🎨 Planning Styles

### **ADHD-Friendly (Default)**

- Uses motivational language with emojis
- Breaks complex steps into smaller sub-steps
- Includes progress indicators and checkboxes
- Provides time estimates for each step
- Uses visual organization with headers and lists
- Includes encouragement and celebration of progress
- **🆕 Automatically includes relevant tool guidelines**

### **Detailed**

- Comprehensive explanations for each step
- Detailed tool parameters and options
- Extensive best practices and tips
- Multiple alternatives and considerations
- Formal, professional language
- **🆕 Rich tool guidelines integration**

### **Concise**

- Brief descriptions for each step
- Essential information only
- Bullet points and short sentences
- Direct, action-oriented language
- **🆕 Focused tool guidance**

## 🔧 Tool Parameters

### **create_intelligent_plan**

- `user_request` (required): The task to plan
- `available_tools` (optional): Comma-separated list of available tools
- `user_context` (optional): Additional context about the user's situation
- `planning_style` (optional): Planning style to use (default: "adhd_friendly")
- **🆕 `include_guidelines` (optional)**: Whether to include tool guidelines (default: True)

### **create_plan_with_tool_context**

- `user_request` (required): The task to plan
- `tool_registry` (required): Your tool registry instance
- `user_context` (optional): Additional context about the user's situation
- `planning_style` (optional): Planning style to use
- **🆕 `include_guidelines` (optional)**: Whether to include tool guidelines (default: True)

## 🆕 Tool Guidelines Integration

### **How It Works**

1. **Task Analysis**: LLM analyzes the user request
2. **🆕 LLM Tool Identification**: LLM intelligently identifies which tools are relevant
3. **Guideline Loading**: Automatically loads relevant tool guidelines
4. **Context Integration**: Includes guidelines in the planning prompt
5. **Enhanced Planning**: LLM creates plans with specific tool guidance

### **🆕 LLM-Driven Tool Selection**

Instead of hardcoded pattern matching, the planner now uses **LLM intelligence** to:

- **Analyze user intent** more accurately
- **Consider context** and workflow requirements
- **Identify tool dependencies** and logical order
- **Prefer tools with guidelines** when available
- **Adapt to new tools** without code changes

### **Tool Identification Process**

```
User Request → LLM Analysis → Tool Selection → Guideline Loading → Enhanced Planning
     ↓              ↓              ↓              ↓              ↓
"I need to create  LLM analyzes   LLM identifies  Planner loads   LLM creates plan
 meeting notes"    the request    relevant tools   guidelines     with specific
                   and context    (e.g., notion_   for those      tool guidance
                   to determine   notes, search)   tools          and best practices
                   are needed
```

### **Supported Tool Types**

The planner automatically detects and includes guidelines for:

- **Note Tools**: `notion_notes`, `create_note`, etc.
- **Search Tools**: `codebase_search`, `grep_search`, etc.
- **File Tools**: `read_file`, `edit_file`, `list_dir`, etc.
- **System Tools**: `run_terminal_cmd`, etc.

### **Guideline File Format**

Guideline files should be named `{tool_name}_guidelines.md` and contain:

- **Overview section** (`## 🎯 Overview`)
- **When to use section** (`## 🚀 When to Use This Tool`)
- **Examples section** (`## 🎨 Note Templates & Use Cases`)
- **Best practices** and usage tips

## 📝 Plan Output Format

The planner creates structured plans with:

- **Step numbers** and clear descriptions
- **Tool recommendations** with specific context
- **Best practices** for each step (from guidelines when available)
- **Expected outcomes** and success criteria
- **Potential challenges** and solutions
- **Progress tracking** indicators
- **Time estimates** for each step
- **Next steps** after completion
- **🆕 Tool-specific guidance** from guidelines

## 🚀 Advanced Features

### **🆕 Automatic Guideline Detection**

- Scans tools directory for guideline files
- Caches guidelines for performance
- Extracts relevant sections automatically
- Integrates guidelines seamlessly into plans

### **Fallback Planning**

- Automatic fallback if LLM fails
- Basic plan structure for any task
- Error handling and recovery

### **Plan Summaries**

- Extract key information from plans
- Quick reference for users
- Progress tracking support

### **Tool Context Integration**

- Detailed tool information from registry
- Tool-specific best practices
- Parameter recommendations
- **🆕 Automatic guideline inclusion**

## 🔍 Use Cases

### **Note Management**

- Creating meeting notes with proper structure
- Organizing project documentation
- Setting up research note systems
- **🆕 Includes Notion note templates and best practices**

### **Information Search**

- Planning search strategies
- Choosing appropriate search tools
- Organizing search results
- **🆕 Includes search tool guidelines and strategies**

### **Project Planning**

- Breaking down complex projects
- Identifying required tools and resources
- Creating execution timelines
- **🆕 Includes project management tool guidance**

### **Learning & Research**

- Planning research activities
- Organizing learning materials
- Creating study schedules
- **🆕 Includes research tool best practices**

## 🎯 Best Practices

### **For Users**

1. **Be specific** about what you want to accomplish
2. **Provide context** about your situation and preferences
3. **Use the planning tool** for complex or multi-step tasks
4. **Follow the plan** step by step for best results
5. **Ask for clarification** if any step is unclear
6. **🆕 Leverage tool guidelines** included in the plan

### **For Developers**

1. **Set the LLM client** before using the planner
2. **Integrate with your tool registry** for best results
3. **Create guideline files** for your tools (`{tool_name}_guidelines.md`)
4. **Handle errors gracefully** with fallback plans
5. **Monitor plan quality** and adjust prompts as needed
6. **Test with different planning styles** to find what works best

## 🚨 Troubleshooting

### **Common Issues**

#### **LLM Client Not Set**

```
ValueError: LLM client not set. Use set_llm_client() first.
```

**Solution**: Set the LLM client before using the planner.

#### **Plan Generation Fails**

**Symptom**: Getting fallback plans instead of custom plans
**Solution**: Check LLM client configuration and network connectivity

#### **Poor Plan Quality**

**Symptom**: Plans are too generic or unhelpful
**Solution**:

- Provide more specific user context
- Use different planning styles
- Adjust the planning prompt template
- **🆕 Ensure guideline files are properly formatted**

#### **🆕 Guidelines Not Loading**

**Symptom**: Plans don't include tool-specific guidance
**Solution**:

- Check that guideline files exist and are named correctly
- Verify file paths and permissions
- Ensure guideline files have proper markdown structure
- Check logs for guideline loading errors

### **Debug Mode**

Enable logging to see detailed information:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🔮 Future Enhancements

- **🆕 Guideline Templates**: Pre-built guideline templates for common tool types
- **Plan Templates**: Pre-built plans for common tasks
- **Plan Execution**: Automatic execution of planned steps
- **Plan Learning**: Improve plans based on user feedback
- **Collaborative Planning**: Multi-user plan creation and sharing
- **Plan Analytics**: Track plan success rates and user satisfaction
- **🆕 Guideline Versioning**: Track and update tool guidelines over time

## 📚 Related Tools

- **Notion Notes Tool**: For note creation and management
- **Search Tools**: For information gathering
- **File Management Tools**: For document organization
- **System Tools**: For command execution
- **🆕 Guideline Files**: For tool-specific best practices

---

_For questions or support, refer to the development team or check the integration examples. The enhanced planner now automatically includes relevant tool guidelines for more actionable plans!_
