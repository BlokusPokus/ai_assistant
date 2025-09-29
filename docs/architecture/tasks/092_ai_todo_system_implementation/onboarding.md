# AI Todo System Implementation - Onboarding

## Context Analysis

You are implementing an AI todo management system based on the sophisticated todo tracking capabilities found in AI coding assistants. This system needs to differentiate itself from user todos while providing intelligent task management for the personal assistant.

## Key Information Discovered

### AI Todo Management Prompt Structure

The AI coding assistant uses a comprehensive todo management system with these characteristics:

**When to Use:**

- Complex multi-step tasks (3+ distinct steps)
- Non-trivial tasks requiring careful planning
- User explicitly requests todo list
- User provides multiple tasks (numbered/comma-separated)
- After receiving new instructions - capture requirements as todos
- After completing tasks - mark complete and add follow-ups
- When starting new tasks - mark as in_progress (ideally only one at a time)

**When NOT to Use:**

- Single, straightforward tasks
- Trivial tasks with no organizational benefit
- Tasks completable in < 3 trivial steps
- Purely conversational/informational requests
- Don't add testing tasks unless requested

**Task States:**

- `pending`: Not yet started
- `in_progress`: Currently working on
- `completed`: Finished successfully
- `cancelled`: No longer needed

**Task Management Rules:**

- Update status in real-time
- Mark complete IMMEDIATELY after finishing
- Only ONE task in_progress at a time
- Complete current tasks before starting new ones
- Create specific, actionable items
- Break complex tasks into manageable steps
- Use clear, descriptive names

**Advanced Features:**

- Task dependencies with prerequisite relationships
- Parallel execution for independent tasks
- Minimum 2 tasks per list requirement
- Merge logic for existing todos
- Proactive task creation based on complexity analysis

## System Architecture Requirements

### Database Schema Differences

AI todos need additional fields beyond standard user todos:

- `dependencies` (JSON array of task IDs)
- `auto_generated` (boolean flag)
- `complexity_score` (integer for task complexity)
- `parallel_executable` (boolean for parallel processing)
- `parent_request_id` (links to original user request)
- `ai_session_id` (tracks AI session context)

### Backend API Requirements

- Dependency resolution logic
- Parallel execution support
- Status update webhooks
- Integration with existing todo system
- AI-specific endpoints for auto-generation

### Frontend Component Requirements

- Visual distinction from user todos
- Dependency visualization (graph/tree view)
- Real-time status updates
- Parallel execution indicators
- AI session context display

## Implementation Strategy

### Phase 1: Analysis & Design

- Study existing todo system implementation
- Design AI todo database schema
- Plan API endpoint structure
- Design frontend component architecture

### Phase 2: Backend Development

- Create AI todos database table
- Implement dependency resolution logic
- Build API endpoints for AI todo management
- Add parallel execution support

### Phase 3: Frontend Development

- Create AI todo dashboard components
- Implement dependency visualization
- Add real-time status updates
- Integrate with existing todo interface

### Phase 4: Integration & Testing

- Connect AI todo system with personal assistant workflow
- Test dependency management
- Verify parallel execution
- Ensure proper separation from user todos

## Key Files to Study

1. **AI Prompt Source**: `src/personal_assistant/prompts/templates/cursor_prompt.md`

   - Lines 385-533 contain the complete todo management system
   - Study the `todo_write` function specification
   - Understand the decision logic for when to create todos

2. **Existing Todo System**: `src/apps/frontend/src/components/todos/`

   - `TodoTab.tsx` - Main todo interface
   - `TodoList.tsx` - Todo list component
   - `TodoItem.tsx` - Individual todo item
   - `TodoForm.tsx` - Todo creation form

3. **Backend API**: `src/apps/fastapi_app/routes/todos.py`

   - Study existing todo API endpoints
   - Understand current data models
   - Plan AI todo extensions

4. **Database Schema**: `database/schemas/`
   - Review current todo table structure
   - Plan AI todo table additions
   - Consider migration strategy

## Critical Success Factors

1. **Clear Separation**: AI todos must be visually and functionally distinct from user todos
2. **Dependency Management**: Implement robust prerequisite handling
3. **Real-time Updates**: Status changes must be immediate and visible
4. **Parallel Execution**: Independent tasks should run simultaneously
5. **Proactive Creation**: System should automatically create todos for complex requests
6. **Integration**: Seamless integration with existing personal assistant workflow

## Questions to Resolve

1. How should AI todos be visually distinguished from user todos?
2. What level of dependency complexity should be supported?
3. How should parallel execution be handled in the UI?
4. Should AI todos be editable by users or read-only?
5. How should AI session context be maintained?
6. What happens to AI todos when the session ends?

## Next Steps

1. Complete analysis of existing todo system
2. Design AI todo database schema
3. Plan API endpoint structure
4. Create frontend component mockups
5. Begin implementation with backend development
6. Test and iterate on the system

## Resources

- AI Todo Management Prompt: Lines 385-533 in cursor_prompt.md
- Onboarding Template: `docs/architecture/tasks/onboard.md`
- Existing Todo Implementation: `src/apps/frontend/src/components/todos/`
- Database Schemas: `database/schemas/`
- Backend API: `src/apps/fastapi_app/routes/todos.py`
