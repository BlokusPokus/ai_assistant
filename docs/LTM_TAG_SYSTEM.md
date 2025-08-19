# LTM Tag System Implementation

This document describes the implementation of the tag system for Long-Term Memory (LTM) in the personal assistant.

## Overview

The LTM tag system provides a centralized, consistent way to categorize and retrieve long-term memories. It ensures that:

1. **Consistency**: All tags come from a predefined list
2. **Validation**: Tags are validated at multiple levels (application, database)
3. **Efficiency**: Optimized database queries using tag-based indexing
4. **Usability**: Clear instructions for LLM tag selection

## Architecture

### 1. Tag Constants (`src/personal_assistant/constants/tags.py`)

The central definition of all allowed tags, organized by categories:

```python
from personal_assistant.constants.tags import LTM_TAGS, TAG_CATEGORIES

# Core tags list
LTM_TAGS = [
    "email", "meeting", "create", "delete", "important",
    "work", "personal", "preference", "tool_execution", ...
]

# Organized by category
TAG_CATEGORIES = {
    "communication": ["email", "meeting", "conversation"],
    "actions": ["create", "delete", "update", "search"],
    "priority": ["important", "urgent", "critical"],
    # ... more categories
}
```

### 2. Tag Utilities (`src/personal_assistant/utils/tag_utils.py`)

Utility functions for tag management:

```python
from personal_assistant.utils.tag_utils import (
    normalize_tags, validate_tags, suggest_tags_for_content
)

# Normalize tags (lowercase, underscores, remove special chars)
normalized = normalize_tags(["Email", "MEETING", "user request"])

# Validate tags against allowed list
valid_tags, invalid_tags = validate_tags(tags)

# Get tag suggestions based on content
suggestions = suggest_tags_for_content("User wants to delete an email")
```

### 3. LTM Tool Integration (`src/personal_assistant/tools/ltm/ltm_tool.py`)

The LTM tool now uses the tag system:

```python
# Tags parameter now shows allowed tags in description
"tags": {
    "type": "string",
    "description": "Comma-separated list of tags from the allowed list: email, meeting, schedule, delete, important, general, user_request, tool_execution... (see full list in constants)"
}
```

### 4. Prompt Templates (`src/personal_assistant/prompts/templates/ltm/tag_selection.py`)

Clear instructions for LLM tag selection:

```python
from personal_assistant.prompts.templates.ltm.tag_selection import get_tag_selection_prompt

prompt = get_tag_selection_prompt(
    content="User wants to delete an important email",
    context="Email management preference"
)
```

### 5. Database Validation (`src/personal_assistant/database/migrations/add_tag_validation.sql`)

Database-level constraints ensure data integrity:

- Tags must be arrays
- Tags must not be empty
- Tags must be strings
- Tags must be lowercase
- Tags must be from allowed list

## Usage Examples

### Creating LTM Memories with Tags

```python
from personal_assistant.tools.ltm.ltm_tool import LTMTool

ltm_tool = LTMTool()

# Create memory with valid tags
result = await ltm_tool.add_memory(
    content="User prefers to work in the morning",
    tags="preference,work,routine",
    importance_score=7,
    context="Work schedule preference"
)

# The system will validate and normalize tags automatically
```

### Tag Validation

```python
from personal_assistant.constants.tags import validate_tags

tags = ["email", "delete", "invalid_tag", "important"]
valid_tags, invalid_tags = validate_tags(tags)

print(f"Valid: {valid_tags}")      # ['email', 'delete', 'important']
print(f"Invalid: {invalid_tags}")  # ['invalid_tag']
```

### Tag Suggestions

```python
from personal_assistant.utils.tag_utils import suggest_tags_for_content

content = "User urgently needs to schedule a meeting with the team"
suggestions = suggest_tags_for_content(content)

print(f"Suggested tags: {suggestions}")
# Output: ['urgent', 'meeting', 'schedule', 'work']
```

### Building Tag Queries

```python
from personal_assistant.utils.tag_utils import build_tag_query

# Build query for OR search
query = build_tag_query(["email", "meeting"], "OR")
# Result: {"tags": ["email", "meeting"], "operator": "OR", "invalid_tags": []}

# Build query for AND search
query = build_tag_query(["work", "important"], "AND")
# Result: {"tags": ["work", "important"], "operator": "AND", "invalid_tags": []}
```

## Database Schema

The LTM memories table includes:

```sql
CREATE TABLE ltm_memories (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    content TEXT NOT NULL,
    tags JSONB NOT NULL,  -- Array of validated tags
    importance_score INTEGER DEFAULT 1,
    context TEXT,
    created_at TIMESTAMP DEFAULT now(),
    last_accessed TIMESTAMP DEFAULT now()
);

-- Tag validation constraints
ALTER TABLE ltm_memories ADD CONSTRAINT check_tags_is_array
    CHECK (jsonb_typeof(tags) = 'array');

ALTER TABLE ltm_memories ADD CONSTRAINT check_tags_not_empty
    CHECK (jsonb_array_length(tags) > 0);

-- Tag validation trigger
CREATE TRIGGER validate_ltm_tags_trigger
    BEFORE INSERT OR UPDATE ON ltm_memories
    FOR EACH ROW
    EXECUTE FUNCTION validate_ltm_tags_trigger();
```

## LLM Integration

### Tag Selection Instructions

The LLM receives clear instructions:

```
You must select one or more tags for each LTM memory entry from the following predefined list:

Available Tags:
email, meeting, conversation, document, note, create, delete, update, search, schedule, remind, important, urgent, critical, low_priority, work, personal, health, finance, travel, shopping, entertainment, education, preference, habit, pattern, routine, dislike, favorite, tool_execution, user_request, system_response, error, success, daily, weekly, monthly, one_time, recurring, general, miscellaneous, other

Tag Selection Rules:
1. REQUIRED: You MUST select at least 1 tag from the list above
2. REQUIRED: You can ONLY use tags from the predefined list
3. RECOMMENDED: Select 2-4 tags for better categorization
4. IMPORTANT: Use specific tags over general ones when possible
5. CONTEXT: Consider the content and context when selecting tags

Examples:
- User: "Delete my 2pm meeting" → Tags: delete, meeting
- User: "I prefer to work in the morning" → Tags: preference, work, routine
- User: "This is urgent, please remember" → Tags: urgent, important

Response Format:
Return ONLY a comma-separated list of tags, no explanations or additional text.
Example: "email,delete,important"
```

### Using in Prompts

```python
from personal_assistant.prompts.templates.ltm.tag_selection import get_tag_selection_prompt

# For the LLM to select tags
tag_prompt = get_tag_selection_prompt(
    content="User wants to delete an important email from work",
    context="Email management preference"
)

# Send to LLM for tag selection
llm_response = await llm.generate(tag_prompt)
# Expected response: "email,delete,important,work"
```

## Testing

Run the test suite to verify the implementation:

```bash
python test_ltm_tag_system.py
```

This will test:

- Tag constants and categories
- Tag utilities and validation
- LTM tool integration
- Prompt template generation

## Migration

To apply the database changes:

1. **Run the migration script:**

   ```bash
   psql -d your_database -f src/personal_assistant/database/migrations/add_tag_validation.sql
   ```

2. **Verify constraints:**

   ```sql
   -- Check constraints
   SELECT conname, pg_get_constraintdef(oid)
   FROM pg_constraint
   WHERE conrelid = 'ltm_memories'::regclass;

   -- Check triggers
   SELECT tgname, tgrelid::regclass
   FROM pg_trigger
   WHERE tgrelid = 'ltm_memories'::regclass;
   ```

## Benefits

1. **Consistency**: All memories use the same tag vocabulary
2. **Efficiency**: Fast tag-based queries with proper indexing
3. **Validation**: Multiple levels of tag validation
4. **Usability**: Clear instructions for LLM tag selection
5. **Maintainability**: Centralized tag definitions
6. **Scalability**: Easy to add new tags and categories

## Future Enhancements

1. **Tag Analytics**: Track tag usage patterns
2. **Auto-tagging**: ML-based tag suggestions
3. **Tag Hierarchies**: Parent-child tag relationships
4. **Tag Synonyms**: Alternative tag mappings
5. **Tag Scoring**: Relevance scoring for tag suggestions

## Troubleshooting

### Common Issues

1. **Invalid tags error**: Ensure all tags are from the `LTM_TAGS` list
2. **Database constraint violations**: Run the migration script
3. **Import errors**: Check Python path includes `src/` directory
4. **Tag normalization issues**: Verify tag utility functions are working

### Debug Commands

```python
# Check available tags
from personal_assistant.constants.tags import LTM_TAGS
print(f"Available tags: {LTM_TAGS}")

# Validate specific tags
from personal_assistant.constants.tags import validate_tags
valid, invalid = validate_tags(["email", "invalid_tag"])
print(f"Valid: {valid}, Invalid: {invalid}")

# Test tag suggestions
from personal_assistant.utils.tag_utils import suggest_tags_for_content
suggestions = suggest_tags_for_content("test content")
print(f"Suggestions: {suggestions}")
```

## Conclusion

The LTM tag system provides a robust, scalable foundation for categorizing and retrieving long-term memories. It ensures consistency, validates data integrity, and provides clear guidance for LLM tag selection.

For questions or issues, refer to the test script and database migration files for implementation details.
