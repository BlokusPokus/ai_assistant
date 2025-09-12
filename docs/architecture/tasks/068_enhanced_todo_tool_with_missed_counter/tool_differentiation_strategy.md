# Tool Differentiation Strategy

## Problem Statement

The agent has multiple tools that could be confused for similar purposes:

- **Calendar Events** (external calendar management)
- **AI Tasks** (AI-driven automated tasks)
- **Todos** (personal task management)
- **Reminders** (simple notifications)

## Solution: Clear Tool Differentiation Framework

### 1. **Tool Purpose Matrix**

| Tool          | Primary Purpose              | AI Involvement    | User Action Required      | External Integration |
| ------------- | ---------------------------- | ----------------- | ------------------------- | -------------------- |
| **Calendar**  | External calendar management | None              | User manages events       | Microsoft Graph      |
| **AI Tasks**  | AI-driven automation         | Full AI execution | None (AI does work)       | Internal only        |
| **Todos**     | Personal task tracking       | Segmentation only | User completes tasks      | Internal only        |
| **Reminders** | Simple notifications         | None              | User responds to reminder | SMS/Email            |

### 2. **Decision Tree for Tool Selection**

```
User Request Analysis:
├── "Schedule a meeting with John" → Calendar Tool
├── "Remind me to call mom at 3pm" → Reminder Tool
├── "Create a todo to buy groceries" → Todo Tool
├── "Make a list of good emails" → AI Task Tool
└── "Track my daily tasks" → Todo Tool
```

### 3. **Enhanced Tool Descriptions**

#### **Calendar Tool**

- **Clear Purpose**: "Manage external calendar events and meetings"
- **When to Use**: Scheduling meetings, viewing calendar, managing external events
- **AI Role**: None - just CRUD operations
- **Key Differentiator**: "External calendar management only"

#### **AI Task Tool**

- **Clear Purpose**: "Create AI-driven tasks that the assistant will execute automatically"
- **When to Use**: "Make a list of...", "Analyze my...", "Generate a report on..."
- **AI Role**: Full execution - AI does the work
- **Key Differentiator**: "AI does the work for you"

#### **Todo Tool**

- **Clear Purpose**: "Track personal tasks that YOU need to complete"
- **When to Use**: "I need to remember to...", "Track my progress on...", "Break down this task..."
- **AI Role**: Segmentation and analytics only
- **Key Differentiator**: "You complete the tasks, AI helps organize them"

#### **Reminder Tool**

- **Clear Purpose**: "Set simple notifications and alerts"
- **When to Use**: "Remind me to...", "Alert me when...", "Notify me at..."
- **AI Role**: None - just scheduling
- **Key Differentiator**: "Simple notifications only"

### 4. **Enhanced Metadata for Each Tool**

#### **Calendar Tool Metadata**

```yaml
purpose: "External calendar event management"
ai_involvement: "None - CRUD operations only"
user_action: "User manages calendar events"
when_to_use: "Scheduling meetings, viewing calendar, managing external events"
key_phrases:
  ["schedule meeting", "calendar event", "book appointment", "meeting with"]
```

#### **AI Task Tool Metadata**

```yaml
purpose: "AI-driven task automation"
ai_involvement: "Full execution - AI does the work"
user_action: "None - AI completes the task"
when_to_use: "Make lists, analyze data, generate reports, research topics"
key_phrases:
  ["make a list of", "analyze my", "generate a report", "research", "find"]
```

#### **Todo Tool Metadata**

```yaml
purpose: "Personal task tracking and management"
ai_involvement: "Segmentation and analytics only"
user_action: "User completes the tasks"
when_to_use: "Track personal tasks, break down complex tasks, manage productivity"
key_phrases:
  ["I need to", "track my", "remember to", "break down", "manage my tasks"]
```

#### **Reminder Tool Metadata**

```yaml
purpose: "Simple notification and alert system"
ai_involvement: "None - just scheduling"
user_action: "User responds to notifications"
when_to_use: "Set alerts, notifications, simple reminders"
key_phrases: ["remind me to", "alert me", "notify me", "ping me"]
```

### 5. **Implementation Strategy**

#### **Phase 1: Update Tool Descriptions**

- Update each tool's description to clearly state its purpose
- Add "AI Involvement" and "User Action" fields to metadata
- Include key phrases that trigger each tool

#### **Phase 2: Enhanced AI Instructions**

- Add tool selection guidelines to the AI prompt
- Include decision tree logic in the prompt builder
- Add examples of when to use each tool

#### **Phase 3: Tool Selection Validation**

- Add validation logic to prevent tool misuse
- Implement tool selection feedback
- Add tool selection metrics

### 6. **Future Considerations**

#### **Reminder + AI Task Merger**

When reminders and AI tasks are merged:

- **New Tool**: "Smart Tasks"
- **Purpose**: "AI-driven tasks with optional user notifications"
- **AI Involvement**: "Full execution with optional user alerts"
- **User Action**: "Optional - user can be notified of progress"

#### **Tool Selection Examples**

**Correct Tool Selection:**

- "Schedule a meeting with John tomorrow at 2pm" → Calendar
- "Make a list of all my good emails from this week" → AI Task
- "I need to remember to buy groceries this weekend" → Todo
- "Remind me to call mom at 3pm" → Reminder

**Incorrect Tool Selection:**

- "Schedule a meeting" → Todo (wrong - should be Calendar)
- "Make a list of emails" → Todo (wrong - should be AI Task)
- "I need to remember to call mom" → AI Task (wrong - should be Todo)

### 7. **Success Metrics**

- **Tool Selection Accuracy**: >95% correct tool selection
- **User Confusion**: <5% of users ask "why did you use X tool?"
- **Task Completion Rate**: Maintain or improve current rates
- **User Satisfaction**: Positive feedback on tool selection

## Implementation Priority

1. **High Priority**: Update tool descriptions and metadata
2. **Medium Priority**: Add AI selection guidelines
3. **Low Priority**: Add validation and metrics

This strategy ensures clear differentiation and prevents tool confusion while maintaining the unique value of each tool.
