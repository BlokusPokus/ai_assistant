# Memory Storage System - Quick Reference

## Common Operations

### Conversation Management

```python
# Get existing conversation
conversation_id = await get_conversation_id(user_id)

# Create new conversation if none exists
if conversation_id is None:
    conversation_id = await create_new_conversation(user_id)

# Check if conversation should be resumed
if should_resume_conversation(last_timestamp):
    state = await load_state(conversation_id)
else:
    summary = await load_latest_summary(user_id)
    state = AgentState.from_summary(summary)
```

### State Management

```python
# Save state
await save_state(conversation_id, agent_state, user_id)

# Load state (handles errors gracefully)
state = await load_state(conversation_id)

# Check if state was loaded successfully
if state.user_input:
    # State loaded successfully
    pass
else:
    # No state found or corrupted
    pass
```

### Memory Operations

```python
# Store summary
await store_summary(user_id, summary_text)

# Load latest summary
summary = await load_latest_summary(user_id)

# Query long-term memory
memories = await query_ltm(user_id, tags=["important"])

# Add long-term memory entry
await add_ltm_entry(user_id, {
    "content": "Important information",
    "tags": ["work", "urgent"]
})
```

### Logging

```python
# Log agent interaction
await log_agent_interaction(
    user_id=int(user_id),
    user_input="User message",
    agent_response="Agent response",
    tool_called="tool_name",
    tool_output="tool result"
)
```

## Error Handling Patterns

### Safe State Loading

```python
try:
    state = await load_state(conversation_id)
    # State is always valid AgentState object
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    state = AgentState()  # Fallback
```

### Safe Conversation Creation

```python
conversation_id = await get_conversation_id(user_id)
if conversation_id is None:
    try:
        conversation_id = await create_new_conversation(user_id)
    except Exception as e:
        logger.error(f"Failed to create conversation: {e}")
        # Handle error appropriately
```

## Database Schema Reference

### memory_chunks Table

| Column     | Type     | Description          |
| ---------- | -------- | -------------------- |
| id         | Integer  | Primary key          |
| user_id    | Integer  | Foreign key to users |
| content    | Text     | Actual data content  |
| embedding  | Text     | Vector embeddings    |
| created_at | DateTime | Creation timestamp   |

### memory_metadata Table

| Column   | Type    | Description                  |
| -------- | ------- | ---------------------------- |
| id       | Integer | Primary key                  |
| chunk_id | Integer | Foreign key to memory_chunks |
| key      | String  | Metadata key                 |
| value    | String  | Metadata value               |

## Common Metadata Keys

| Key             | Value                     | Description             |
| --------------- | ------------------------- | ----------------------- |
| conversation_id | UUID string               | Conversation identifier |
| type            | "state", "summary", "ltm" | Data type               |
| last_updated    | ISO timestamp             | Last modification time  |
| tag             | String                    | Categorization tag      |

## Troubleshooting

### Common Errors

1. **"column meta_data does not exist"**

   - Use proper joins with memory_metadata table
   - Don't use meta_data-> syntax

2. **"AgentState object has no attribute focus"**

   - Ensure load_state returns AgentState objects
   - Check from_dict method implementation

3. **Database connection errors**
   - Check database configuration
   - Verify connection pool settings

### Debugging Tips

1. Enable debug logging:

   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

2. Check database directly:

   ```sql
   SELECT * FROM memory_chunks WHERE user_id = 123;
   SELECT * FROM memory_metadata WHERE chunk_id = 456;
   ```

3. Monitor error logs for patterns

## Performance Tips

1. **Use proper indexing** on frequently queried fields
2. **Limit query results** when possible
3. **Consider caching** for frequently accessed data
4. **Monitor database performance** regularly

## Best Practices

1. **Always check return values** for None/empty objects
2. **Use try-catch blocks** when calling storage functions
3. **Log errors appropriately** for debugging
4. **Validate data** before storing
5. **Use transactions** for multi-step operations
