"""
LTM Tag Selection Prompt Template

This template provides instructions for the LLM on how to select appropriate tags
for Long-Term Memory entries from the predefined tag list.
"""

from typing import List

from ....constants.tags import LTM_TAGS, TAG_CATEGORIES


class LTMTagSelectionPrompt:
    """Prompt template for LTM tag selection."""

    @staticmethod
    def get_tag_selection_instructions() -> str:
        """
        Get the main instructions for tag selection.

        Returns:
            String with tag selection instructions
        """
        return f"""
You must select one or more tags for each LTM memory entry from the following predefined list:

**Available Tags (EXACT LIST - USE ONLY THESE):**
{', '.join(LTM_TAGS)}

**Tag Categories for Reference:**
- Communication: {', '.join(TAG_CATEGORIES['communication'])}
- Actions: {', '.join(TAG_CATEGORIES['actions'])}
- Priority: {', '.join(TAG_CATEGORIES['priority'])}
- Context: {', '.join(TAG_CATEGORIES['context'])}
- Behavior: {', '.join(TAG_CATEGORIES['behavior'])}
- System: {', '.join(TAG_CATEGORIES['system'])}
- Time: {', '.join(TAG_CATEGORIES['time'])}
- General: {', '.join(TAG_CATEGORIES['general'])}

**CRITICAL Tag Selection Rules:**
1. **MANDATORY**: You MUST select at least 1 tag from the EXACT list above
2. **MANDATORY**: You can ONLY use tags from the predefined list - NO EXCEPTIONS
3. **MANDATORY**: All tags must be lowercase and match exactly (e.g., "email", not "Email" or "EMAIL")
4. **RECOMMENDED**: Select 2-4 tags for better categorization
5. **IMPORTANT**: Use specific tags over general ones when possible
6. **CONTEXT**: Consider the content and context when selecting tags

**Common Valid Tags for Email/Education Content:**
- email, education, reading, learning, preference, work, personal, important, general

**Examples:**
- User: "Delete my 2pm meeting" → Tags: delete, meeting
- User: "I prefer to work in the morning" → Tags: preference, work, routine
- User: "This is urgent, please remember" → Tags: urgent, important
- User: "I like using the email tool" → Tags: preference, email, tool_execution
- User: "I received an educational email" → Tags: email, education, reading

**Response Format:**
Return ONLY a comma-separated list of tags, no explanations or additional text.
Example: "email,delete,important"
"""

    @staticmethod
    def get_tag_selection_prompt(content: str, context: str = "") -> str:
        """
        Get a complete prompt for tag selection.

        Args:
            content: The memory content to tag
            context: Optional context about the memory

        Returns:
            Complete prompt string
        """
        instructions = LTMTagSelectionPrompt.get_tag_selection_instructions()

        prompt = f"""
{instructions}

**Memory Content to Tag:**
{content}

{f"**Context:** {context}" if context else ""}

**Your Task:** Select appropriate tags from the predefined list above.

**Tags:**"""

        return prompt

    @staticmethod
    def get_tag_validation_prompt(content: str, proposed_tags: List[str]) -> str:
        """
        Get a prompt for validating proposed tags.

        Args:
            content: The memory content
            proposed_tags: List of proposed tags to validate

        Returns:
            Validation prompt string
        """
        instructions = LTMTagSelectionPrompt.get_tag_selection_instructions()

        prompt = f"""
{instructions}

**Memory Content:**
{content}

**Proposed Tags:**
{', '.join(proposed_tags)}

**Your Task:** Validate these tags and suggest corrections if needed.

**Validation Rules:**
1. Check if all tags are in the allowed list
2. Suggest better tags if the current ones are too general
3. Ensure tags accurately represent the content
4. Recommend additional tags if important aspects are missing

**Response Format:**
Return a comma-separated list of corrected/improved tags.
Example: "email,delete,important,work"
"""

        return prompt

    @staticmethod
    def get_tag_explanation_prompt(content: str, tags: List[str]) -> str:
        """
        Get a prompt for explaining tag choices.

        Args:
            content: The memory content
            tags: The selected tags

        Returns:
            Explanation prompt string
        """
        return f"""
**Memory Content:**
{content}

**Selected Tags:**
{', '.join(tags)}

**Your Task:** Explain why these tags were chosen for this memory.

**Explanation Guidelines:**
1. Explain how each tag relates to the content
2. Describe the categorization logic used
3. Mention any alternative tags that could have been used
4. Explain the importance of proper tagging for LTM retrieval

**Response:** Provide a clear, concise explanation of the tag selection.
"""


# Convenience functions for easy access
def get_tag_selection_instructions() -> str:
    """Get tag selection instructions."""
    return LTMTagSelectionPrompt.get_tag_selection_instructions()


def get_tag_selection_prompt(content: str, context: str = "") -> str:
    """Get a complete tag selection prompt."""
    return LTMTagSelectionPrompt.get_tag_selection_prompt(content, context)


def get_tag_validation_prompt(content: str, proposed_tags: List[str]) -> str:
    """Get a tag validation prompt."""
    return LTMTagSelectionPrompt.get_tag_validation_prompt(content, proposed_tags)
