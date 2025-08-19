"""
Internal functions for LLM Planner Tool.

This module contains internal utility functions and helper methods
that are used by the main LLMPlannerTool class.
"""

import logging
import os
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


def load_tool_guidelines(guidelines_path: str, guidelines_cache: Dict[str, str] = None) -> Dict[str, str]:
    """Load available tool guidelines from the guidelines directory."""
    if guidelines_cache:
        return guidelines_cache

    guidelines = {}

    try:
        # Look for guideline files in the tools directory
        for root, dirs, files in os.walk(guidelines_path):
            for file in files:
                if file.endswith('_guidelines.md'):
                    tool_name = file.replace('_guidelines.md', '')
                    file_path = os.path.join(root, file)

                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            guidelines[tool_name] = content
                            logger.info(f"Loaded guidelines for {tool_name}")
                    except Exception as e:
                        logger.warning(
                            f"Could not load guidelines for {tool_name}: {e}")

        return guidelines

    except Exception as e:
        logger.error(f"Error loading tool guidelines: {e}")
        return {}


def identify_relevant_tools_fallback(user_request: str, available_tools: Optional[str] = None) -> List[str]:
    """Fallback tool identification using pattern matching when LLM is not available."""
    request_lower = user_request.lower()
    relevant_tools = []

    # Basic tool detection patterns (fallback only)
    tool_patterns = {
        'notion_notes': ['note', 'notes', 'notion', 'meeting', 'project', 'research', 'create', 'update', 'search'],
        'codebase_search': ['code', 'search', 'find', 'explore', 'understand', 'how does', 'where is'],
        'read_file': ['read', 'file', 'content', 'show me', 'display'],
        'edit_file': ['edit', 'modify', 'change', 'update', 'create file', 'write'],
        'grep_search': ['grep', 'find text', 'search text', 'pattern', 'occurrence'],
        'run_terminal_cmd': ['run', 'execute', 'command', 'install', 'build', 'test', 'terminal'],
        'list_dir': ['list', 'directory', 'folder', 'explore', 'navigate'],
        'file_search': ['find file', 'locate', 'file name', 'search file']
    }

    # Check which tools match the request
    for tool_name, patterns in tool_patterns.items():
        if any(pattern in request_lower for pattern in patterns):
            relevant_tools.append(tool_name)

    # If available_tools is specified, filter to only include those
    if available_tools:
        available_list = [tool.strip() for tool in available_tools.split(',')]
        relevant_tools = [
            tool for tool in relevant_tools if tool in available_list]

    return relevant_tools


def build_tool_identification_prompt(user_request: str, available_tools: Optional[str] = None, available_guidelines: List[str] = None) -> str:
    """Build the prompt for LLM tool identification."""
    prompt = f"""
You are an expert tool selection specialist. Your job is to analyze a user request and identify which tools would be most relevant and useful for completing the task.

## 🎯 USER REQUEST:
{user_request}

## 🛠️ AVAILABLE TOOLS:
{available_tools if available_tools else "All standard tools available (search, notes, files, system operations, etc.)"}

## 📚 AVAILABLE GUIDELINES:
The following tools have detailed guidelines available: {', '.join(available_guidelines) if available_guidelines else 'None'}

## 📋 YOUR TASK:
Analyze the user request and identify 2-4 tools that would be most relevant for completing this task. Consider:

1. **Primary tools** - Essential for the main task
2. **Supporting tools** - Helpful for preparation, research, or follow-up
3. **Tool capabilities** - What each tool can actually do
4. **User workflow** - Logical order of tool usage
5. **Guideline availability** - Tools with detailed guidance are preferred

## 📝 RESPONSE FORMAT:
Respond with ONLY a comma-separated list of tool names, nothing else.

Example responses:
- "notion_notes, codebase_search"
- "read_file, edit_file, run_terminal_cmd"
- "grep_search, notion_notes"

## 🎯 TOOL CATEGORIES:

**Note Management:**
- notion_notes: Create, update, search, and manage structured notes with templates

**Information Search:**
- codebase_search: Semantic search through code and documentation
- grep_search: Pattern-based text search in files
- file_search: Find files by name or pattern

**File Operations:**
- read_file: View file contents
- edit_file: Modify or create files
- list_dir: Explore directory structures

**System Operations:**
- run_terminal_cmd: Execute system commands
- list_dir: Navigate file systems

Now identify the most relevant tools for this request:
"""

    return prompt


def parse_tool_identification_response(response: str) -> List[str]:
    """Parse the LLM response to extract tool names."""
    try:
        # Clean the response and extract tool names
        response_clean = response.strip().lower()

        # Remove common prefixes/suffixes
        response_clean = response_clean.replace('tools:', '').replace(
            'relevant tools:', '').replace('tools needed:', '')
        response_clean = response_clean.replace(
            'tools required:', '').replace('tools:', '').replace('tools', '')

        # Split by common separators
        if ',' in response_clean:
            tools = [tool.strip() for tool in response_clean.split(',')]
        elif ' and ' in response_clean:
            tools = [tool.strip() for tool in response_clean.split(' and ')]
        elif ' ' in response_clean:
            tools = [tool.strip() for tool in response_clean.split()]
        else:
            tools = [response_clean]

        # Clean up tool names and filter valid ones
        valid_tools = []
        for tool in tools:
            tool_clean = tool.strip().replace('_', '').replace('-', '')
            if tool_clean and len(tool_clean) > 2:  # Basic validation
                valid_tools.append(tool_clean)

        return valid_tools[:4]  # Limit to 4 tools maximum

    except Exception as e:
        logger.error(f"Error parsing tool identification response: {e}")
        return []


def extract_relevant_guidelines(tool_names: List[str], guidelines: Dict[str, str], max_length: int = 1000) -> str:
    """Extract relevant sections from tool guidelines."""
    relevant_sections = []

    for tool_name in tool_names:
        if tool_name in guidelines:
            content = guidelines[tool_name]

            # Extract key sections (overview, when to use, examples)
            sections = []

            # Look for overview section
            overview_start = content.find('## 🎯 Overview')
            if overview_start != -1:
                overview_end = content.find('##', overview_start + 1)
                if overview_end == -1:
                    overview_end = len(content)
                overview = content[overview_start:overview_end].strip()
                sections.append(
                    f"### {tool_name.replace('_', ' ').title()} Guidelines:\n{overview}")

            # Look for when to use section
            when_to_use_start = content.find('## 🚀 When to Use This Tool')
            if when_to_use_start != -1:
                when_to_use_end = content.find('##', when_to_use_start + 1)
                if when_to_use_end == -1:
                    when_to_use_end = len(content)
                when_to_use = content[when_to_use_start:when_to_use_end].strip(
                )
                sections.append(
                    f"**When to use {tool_name.replace('_', ' ').title()}:**\n{when_to_use}")

            # Look for examples section
            examples_start = content.find('## 🎨 Note Templates & Use Cases')
            if examples_start != -1:
                examples_end = content.find('##', examples_start + 1)
                if examples_end == -1:
                    examples_end = len(content)
                examples = content[examples_start:examples_end].strip()
                sections.append(
                    f"**Examples for {tool_name.replace('_', ' ').title()}:**\n{examples}")

            if sections:
                tool_guidelines = "\n\n".join(sections)
                # Truncate if too long
                if len(tool_guidelines) > max_length:
                    tool_guidelines = tool_guidelines[:max_length] + "..."
                relevant_sections.append(tool_guidelines)

    if relevant_sections:
        return "\n\n---\n\n".join(relevant_sections)
    else:
        return "No specific tool guidelines available for the identified tools."


def build_planning_prompt(
    user_request: str,
    available_tools: Optional[str],
    user_context: Optional[str],
    planning_style: str,
    tool_guidelines: str = "",
    relevant_tools: List[str] = None,
    style_instructions: str = ""
) -> str:
    """Build the prompt for LLM planning with tool guidelines."""

    # Build tools context
    tools_context = ""
    if relevant_tools:
        tools_context = f"""
## 🎯 RELEVANT TOOLS IDENTIFIED:
The following tools are likely to be useful for this task:
{', '.join(relevant_tools)}

## 📚 TOOL GUIDELINES & BEST PRACTICES:
{tool_guidelines}
"""

    prompt = f"""
You are an expert task planner and productivity consultant specializing in helping users with ADHD and executive function challenges. Your job is to create a clear, actionable plan for completing the user's request.

## 🎯 USER REQUEST:
{user_request}

## 🛠️ AVAILABLE TOOLS:
{available_tools if available_tools else "All standard tools available (search, notes, files, system operations, etc.)"}

## 👤 USER CONTEXT:
{user_context if user_context else "Standard user context - working on personal or professional tasks"}

{tools_context}

## 📋 YOUR TASK:
Create a comprehensive, step-by-step plan that:

1. **Analyzes the request** to understand what needs to be done
2. **Breaks it down** into clear, manageable steps (2-5 steps maximum)
3. **Recommends specific tools** for each step when appropriate
4. **Provides context** for tool usage based on the specific task AND the guidelines above
5. **Considers dependencies** and logical order of operations
6. **Includes best practices** for each step (use the guidelines when available)
7. **Anticipates potential challenges** and suggests solutions
8. **Focuses on ADHD-friendly execution** with clear progress indicators

## 📝 PLAN FORMAT:
Structure your response as a clear, actionable plan with:

- **Step numbers** and clear, concise descriptions
- **Tool recommendations** with specific context and parameters
- **Best practices** for each step (reference the guidelines above)
- **Expected outcomes** and success criteria
- **Potential challenges** and solutions
- **Progress tracking** indicators
- **Next steps** after completion

## 🎨 STYLE GUIDELINES:
{style_instructions}

## 🔍 SPECIAL CONSIDERATIONS:
- If this involves note-taking, consider Notion note best practices and templates
- If this involves searching, suggest the most appropriate search strategy (broad to narrow)
- If this involves file operations, consider organization and naming conventions
- If this involves multiple tools, suggest the most efficient order of operations
- Always consider the user's ADHD needs: clear structure, progress tracking, and motivation
- **IMPORTANT**: Use the tool guidelines above to provide specific, actionable advice for each tool

## 🚀 EXECUTION TIPS:
- Keep each step focused and achievable (5-15 minutes max per step)
- Include clear success criteria for each step
- Suggest breaks between steps if the task is complex
- Provide motivation and encouragement throughout the plan
- Consider parallel execution where possible to save time
- Reference specific guidelines and examples from the tool documentation above

Now create a comprehensive, ADHD-friendly plan for the user's request, incorporating the tool guidelines and best practices:
"""

    return prompt


def get_style_instructions(planning_style: str) -> str:
    """Get style-specific instructions for the planning prompt."""
    styles = {
        "detailed": """
- Use comprehensive explanations for each step
- Include detailed tool parameters and options
- Provide extensive best practices and tips
- Include multiple alternatives and considerations
- Use formal, professional language
""",
        "concise": """
- Keep descriptions brief and to the point
- Focus on essential information only
- Use bullet points and short sentences
- Minimize explanations and examples
- Use direct, action-oriented language
""",
        "adhd_friendly": """
- Use clear, motivational language with emojis
- Break complex steps into smaller sub-steps
- Include progress indicators and checkboxes
- Provide time estimates for each step
- Use visual organization with headers and lists
- Include encouragement and celebration of progress
- Suggest natural break points and rewards
- Use simple, concrete language
"""
    }

    return styles.get(planning_style, styles["adhd_friendly"])


def create_fallback_plan(user_request: str, available_tools: Optional[str]) -> str:
    """Create a basic fallback plan if LLM fails."""
    return f"""
# 📋 Basic Task Plan

## 🎯 Task Analysis
Unable to generate detailed plan due to technical issues. Here's a basic approach:

### Step 1: Understand the Request ✅
- Analyze what you want to accomplish
- Break it down into main components
- **Time estimate**: 2-3 minutes
- **Success criteria**: Clear understanding of the goal

### Step 2: Choose Appropriate Tools 🛠️
- Identify what tools you need for this task
- Consider tool capabilities and limitations
- **Time estimate**: 1-2 minutes
- **Success criteria**: Tool selection made

### Step 3: Execute Step by Step 📝
- Complete each part of the task systematically
- Check progress and adjust as needed
- **Time estimate**: Varies by task complexity
- **Success criteria**: Task completed

### Step 4: Review and Deliver 🎉
- Ensure the task meets your requirements
- Present results clearly
- **Time estimate**: 1-2 minutes
- **Success criteria**: Results delivered successfully

## 🛠️ General Tool Usage
- **Search tools**: Find information and explore topics
- **Note tools**: Organize and store information
- **File tools**: Manage documents and content
- **System tools**: Execute commands and operations

## 💡 Tips for Success
- Take one step at a time
- Celebrate small wins
- Take breaks if needed
- Ask for help if stuck

Please try the planning tool again, or proceed with this basic approach.
"""


def build_enhanced_planning_prompt(
    user_request: str,
    tools_text: str,
    user_context: Optional[str],
    relevant_tools: List[str],
    tool_guidelines: str,
    planning_style: str,
    style_instructions: str
) -> str:
    """Build enhanced prompt with tool details and guidelines."""
    enhanced_prompt = f"""
You are an expert task planner with access to these specific tools:

## 🛠️ AVAILABLE TOOLS:
{tools_text}

## 🎯 USER REQUEST:
{user_request}

## 👤 USER CONTEXT:
{user_context if user_context else "Standard user context - working on personal or professional tasks"}

## 🎯 RELEVANT TOOLS IDENTIFIED:
The following tools are likely to be useful for this task:
{', '.join(relevant_tools) if relevant_tools else 'No specific tools identified'}

## 📚 TOOL GUIDELINES & BEST PRACTICES:
{tool_guidelines if tool_guidelines else 'No specific tool guidelines available for the identified tools.'}

## 📋 YOUR TASK:
Create a detailed plan that:

1. **Analyzes the request** to understand requirements
2. **Selects the most appropriate tools** from the available list above
3. **Provides specific tool usage guidance** with parameters and context
4. **Considers tool dependencies** and optimal execution order
5. **Includes best practices** for each tool based on the task AND guidelines above
6. **Anticipates challenges** and suggests alternatives
7. **Creates a clear workflow** that's easy to follow
8. **Focuses on ADHD-friendly execution** with clear progress indicators

## 📝 PLAN REQUIREMENTS:
- Use ONLY the tools listed above
- Provide specific tool names and parameters
- Explain WHY each tool is chosen for each step
- Include error handling and fallback options
- Consider efficiency and user experience
- Keep steps manageable (2-5 steps maximum)
- Include time estimates and progress tracking
- **IMPORTANT**: Reference the tool guidelines above for specific best practices

## 🎨 STYLE: {planning_style.upper()}
{style_instructions}

## 🔍 SPECIAL CONSIDERATIONS:
- If this involves note-taking, consider Notion note best practices and templates
- If this involves searching, suggest the most appropriate search strategy (broad to narrow)
- If this involves file operations, consider organization and naming conventions
- If this involves multiple tools, suggest the most efficient order of operations
- Always consider the user's ADHD needs: clear structure, progress tracking, and motivation
- **Use the tool guidelines above** to provide specific, actionable advice for each tool

Now create a comprehensive, tool-specific plan incorporating the guidelines and best practices:
"""

    return enhanced_prompt


def get_planning_summary(plan: str) -> str:
    """Extract a summary of the plan for quick reference."""
    try:
        # Extract step numbers and titles
        lines = plan.split('\n')
        summary_lines = []

        for line in lines:
            if line.strip().startswith('### Step') or line.strip().startswith('## 🎯'):
                summary_lines.append(line.strip())
            elif line.strip().startswith('- **') and 'Time estimate' in line:
                summary_lines.append(line.strip())

        if summary_lines:
            return "## 📋 Plan Summary:\n" + "\n".join(summary_lines)
        else:
            return "## 📋 Plan Summary:\nPlan created successfully. Follow the steps above."

    except Exception as e:
        logger.error(f"Error creating plan summary: {e}")
        return "## 📋 Plan Summary:\nPlan created successfully."


def format_tool_info_for_prompt(tool_schemas: Dict) -> str:
    """Format tool information for inclusion in planning prompts."""
    tools_info = []
    for name, info in tool_schemas.items():
        description = info.get('description', 'No description available')
        # Truncate long descriptions
        if len(description) > 100:
            description = description[:100] + "..."
        tools_info.append(f"• **{name}**: {description}")

    return "\n".join(tools_info)
