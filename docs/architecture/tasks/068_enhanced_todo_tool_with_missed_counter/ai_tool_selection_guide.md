# AI Tool Selection Guide

## Critical: Tool Differentiation Rules

The agent must choose the correct tool based on the user's intent. Here are the clear rules:

### 🎯 **TODO TOOL** - Personal Task Tracking

**Purpose**: Track tasks that YOU (the user) need to complete
**AI Role**: Helps organize and segment tasks, but YOU do the work

**✅ USE FOR:**

- "I need to remember to buy groceries"
- "Track my progress on the project"
- "Break down this complex task into smaller pieces"
- "I have to complete this report by Friday"
- "Help me organize my daily tasks"
- "What tasks am I missing?"

**❌ DO NOT USE FOR:**

- "Make a list of good emails" → Use AI Task Tool
- "Schedule a meeting with John" → Use Calendar Tool
- "Remind me to call mom at 3pm" → Use Reminder Tool
- "Analyze my productivity patterns" → Use AI Task Tool

---

### 🤖 **AI TASK TOOL** - AI-Driven Automation

**Purpose**: Create tasks that the AI assistant will execute automatically
**AI Role**: AI does the work for you

**✅ USE FOR:**

- "Make a list of all my good emails from this week"
- "Analyze my productivity patterns and give me insights"
- "Generate a report on my spending habits"
- "Research the best restaurants in my area"
- "Find all my overdue invoices"
- "Create a summary of my calendar for this month"

**❌ DO NOT USE FOR:**

- "I need to remember to call mom" → Use Todo Tool
- "Schedule a meeting" → Use Calendar Tool
- "Remind me to take medication" → Use Reminder Tool
- "Track my daily tasks" → Use Todo Tool

---

### 📅 **CALENDAR TOOL** - External Calendar Management

**Purpose**: Manage calendar events and meetings in external calendar systems
**AI Role**: None - just CRUD operations

**✅ USE FOR:**

- "Schedule a meeting with John tomorrow at 2pm"
- "What meetings do I have today?"
- "Book an appointment with the dentist"
- "Create a calendar event for the team meeting"
- "Show me my calendar for next week"

**❌ DO NOT USE FOR:**

- "I need to remember to buy groceries" → Use Todo Tool
- "Make a list of my meetings" → Use AI Task Tool
- "Remind me to call mom" → Use Reminder Tool
- "Track my project tasks" → Use Todo Tool

---

### 🔔 **REMINDER TOOL** - Simple Notifications

**Purpose**: Set simple notifications and alerts
**AI Role**: None - just scheduling notifications

**✅ USE FOR:**

- "Remind me to call mom at 3pm"
- "Alert me when it's time to leave for the meeting"
- "Notify me to take my medication at 8am"
- "Ping me in 30 minutes to check on the project"

**❌ DO NOT USE FOR:**

- "I need to track my grocery shopping" → Use Todo Tool
- "Make a list of reminders" → Use AI Task Tool
- "Schedule a meeting" → Use Calendar Tool
- "Break down this complex task" → Use Todo Tool

---

## Decision Tree

```
User Request Analysis:
├── Contains "make a list of", "analyze", "generate", "research" → AI Task Tool
├── Contains "schedule", "meeting", "appointment", "calendar" → Calendar Tool
├── Contains "remind me to", "alert me", "notify me" → Reminder Tool
├── Contains "I need to", "remember to", "track my", "break down" → Todo Tool
└── Default: Ask for clarification about what they want to accomplish
```

## Key Phrases to Watch For

### AI Task Tool Triggers:

- "Make a list of..."
- "Analyze my..."
- "Generate a report on..."
- "Research..."
- "Find all..."
- "Create a summary of..."
- "What are the best..."
- "Show me insights about..."

### Calendar Tool Triggers:

- "Schedule a meeting"
- "Book an appointment"
- "Create a calendar event"
- "What meetings do I have"
- "Show me my calendar"
- "Add to my calendar"

### Reminder Tool Triggers:

- "Remind me to..."
- "Alert me when..."
- "Notify me to..."
- "Ping me in..."
- "Set a reminder for..."

### Todo Tool Triggers:

- "I need to remember to..."
- "Track my progress on..."
- "Break down this task"
- "I have to complete..."
- "Help me organize my tasks"
- "What tasks am I missing?"

## Common Mistakes to Avoid

1. **"Make a list of my tasks"** → AI Task Tool (not Todo Tool)
2. **"I need to remember to schedule a meeting"** → Todo Tool (not Calendar Tool)
3. **"Remind me to make a list of emails"** → AI Task Tool (not Reminder Tool)
4. **"Track my calendar events"** → AI Task Tool (not Calendar Tool)

## When in Doubt

If the user's intent is unclear, ask clarifying questions:

- "Do you want me to create a task for you to complete, or should I do the work for you?"
- "Are you looking to schedule a calendar event, or track a personal task?"
- "Do you want a simple reminder, or help organizing a complex task?"

This ensures the correct tool is selected and the user gets the help they actually need.
