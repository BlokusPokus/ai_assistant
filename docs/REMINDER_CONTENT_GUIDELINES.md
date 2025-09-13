# 📋 Reminder Content Guidelines for AI Task Scheduler

## Database Schema Mapping

Based on the AI tasks table structure:

- `id` - Unique task identifier
- `user_id` - User who owns the reminder
- `title` - Main reminder text (primary content)
- `description` - Additional details/context
- `task_type` - Type: "reminder", "automated_task", "periodic_task"
- `schedule_type` - Frequency: "once", "daily", "weekly", "monthly", "custom"
- `schedule_config` - JSON config for scheduling
- `next_run_at` - When to execute next
- `last_run_at` - When last executed
- `status` - Current status
- `ai_context` - Additional context for AI execution
- `notification_channels` - How to notify user
- `created_at` - Creation timestamp
- `updated_at` - Last update timestamp

## 🎯 Content Guidelines by Column

### **`title` - Primary Reminder Content**

This is the main content users will see. It should be:

#### **✅ EXCELLENT Title Examples:**

- "Call John about the project proposal"
- "Take your 15-minute walk break"
- "Follow up on yesterday's email to Sarah"
- "Review Q4 budget before the meeting"
- "Water the plants in the living room"

#### **❌ POOR Title Examples:**

- "Reminder" (too vague)
- "Don't forget" (negative framing)
- "Do that thing" (unclear)
- "Call someone" (not specific)

#### **Title Best Practices:**

- **Start with action verb**: Call, Review, Take, Follow up
- **Be specific**: Include who, what, when context
- **Keep concise**: 3-8 words ideal
- **Use positive language**: Focus on action, not avoidance

### **`description` - Additional Context**

Provides extra details that help the AI understand the reminder better:

#### **✅ EXCELLENT Description Examples:**

- "This is important for getting the green light on your Q4 initiative"
- "You've been focused for 2 hours - a quick walk will refresh your mind"
- "Check if Sarah responded about the meeting time"
- "You scheduled this for 2pm today"
- "This keeps your plants healthy and your space fresh"

#### **Description Best Practices:**

- **Explain the 'why'**: Why this reminder matters
- **Add timing context**: When it should happen
- **Include motivation**: Benefits of completing the action
- **Provide background**: What led to this reminder
- **Keep encouraging**: Positive, supportive tone

### **`ai_context` - AI Execution Guidance**

Helps the AI understand how to execute the reminder:

#### **✅ EXCELLENT AI Context Examples:**

- "User wants to be reminded to call John about the project proposal. This is important for their Q4 initiative and they've prepared well for this conversation."
- "User needs a gentle nudge to take a break. They've been working for 2 hours and a walk will help them stay focused."
- "User sent an email yesterday and needs to follow up professionally. Quick follow-ups show professionalism."
- "User has a meeting at 3pm and needs to review the budget beforehand to be prepared."

#### **AI Context Best Practices:**

- **Include user intent**: What the user wants to achieve
- **Add emotional context**: How they might be feeling
- **Provide execution guidance**: How the AI should approach this
- **Include motivation**: Why this matters to the user
- **Add personal touches**: Make it feel personal and caring

### **`task_type` - Reminder Classification**

#### **"reminder"** - Simple, one-time notifications

- **Content Focus**: Direct, actionable reminders
- **Tone**: Encouraging, supportive
- **Examples**: "Call John", "Take a break", "Follow up on email"

#### **"periodic_task"** - Recurring reminders

- **Content Focus**: Habit-building, routine maintenance
- **Tone**: Consistent, motivating
- **Examples**: "Daily standup prep", "Weekly team check-in", "Monthly budget review"

#### **"automated_task"** - Complex, AI-executed tasks

- **Content Focus**: Detailed instructions for AI execution
- **Tone**: Professional, comprehensive
- **Examples**: "Analyze last 5 emails and classify them", "Generate weekly productivity report"

### **`schedule_type` - Timing Context**

#### **"once"** - One-time reminders

- **Content**: Include specific timing context
- **Example**: "Call John about the project proposal - you scheduled this for 2pm today"

#### **"daily"** - Daily habits

- **Content**: Focus on habit-building and consistency
- **Example**: "Take your 15-minute walk break - this daily habit keeps you energized"

#### **"weekly"** - Weekly tasks

- **Content**: Emphasize planning and preparation
- **Example**: "Review your week and plan next week's priorities"

#### **"monthly"** - Monthly maintenance

- **Content**: Focus on bigger picture and long-term goals
- **Example**: "Review your monthly goals and adjust your strategy"

### **`notification_channels` - Delivery Context**

#### **["sms"]** - Quick, mobile-friendly

- **Content**: Keep very concise, action-focused
- **Example**: "Call John about project proposal - 2pm today! 🚀"

#### **["email"]** - More detailed, desktop-friendly

- **Content**: Can include more context and formatting
- **Example**: "Time to call John about the project proposal. You scheduled this for 2pm today. This is important for getting the green light on your Q4 initiative!"

#### **["push"]** - App notification

- **Content**: Balance between SMS and email
- **Example**: "Call John about project proposal - 2pm today. You've prepared well for this conversation! 💪"

## 📝 Content Templates by Use Case

### **Work/Professional Reminders**

```sql
INSERT INTO ai_tasks (
    user_id, title, description, task_type, schedule_type,
    ai_context, notification_channels
) VALUES (
    126,
    'Call John about the project proposal',
    'You scheduled this for 2pm today. This is important for getting the green light on your Q4 initiative.',
    'reminder',
    'once',
    'User wants to be reminded to call John about the project proposal. This is important for their Q4 initiative and they have prepared well for this conversation. They need encouragement and confidence.',
    '["sms"]'
);
```

### **Personal/Habit Reminders**

```sql
INSERT INTO ai_tasks (
    user_id, title, description, task_type, schedule_type,
    ai_context, notification_channels
) VALUES (
    126,
    'Take your 15-minute walk break',
    'You have been focused for 2 hours. A quick walk will refresh your mind and boost your energy for the afternoon.',
    'reminder',
    'daily',
    'User needs a gentle nudge to take a break. They have been working for 2 hours and a walk will help them stay focused and energized. This is part of their daily wellness routine.',
    '["push"]'
);
```

### **Follow-up Reminders**

```sql
INSERT INTO ai_tasks (
    user_id, title, description, task_type, schedule_type,
    ai_context, notification_channels
) VALUES (
    126,
    'Follow up on yesterday''s email to Sarah',
    'Check if Sarah responded about the meeting time. Quick follow-ups show professionalism and keep projects moving.',
    'reminder',
    'once',
    'User sent an email yesterday and needs to follow up professionally. Quick follow-ups show professionalism and keep projects moving. They want to maintain good communication.',
    '["email"]'
);
```

### **Complex/Automated Tasks**

```sql
INSERT INTO ai_tasks (
    user_id, title, description, task_type, schedule_type,
    ai_context, notification_channels
) VALUES (
    126,
    'Analyze last 5 emails and classify them',
    'Get the last 5 emails and classify each as: should read or should delete. This helps with inbox management.',
    'automated_task',
    'once',
    'User wants to efficiently manage their inbox by having the AI analyze the last 5 emails and provide clear recommendations on which ones to read and which ones to delete. This is a practical inbox management task.',
    '["email"]'
);
```

## 🎯 Content Quality Checklist

### **For `title` Column:**

- [ ] Starts with action verb
- [ ] Specific and clear
- [ ] 3-8 words long
- [ ] Positive language
- [ ] No vague terms

### **For `description` Column:**

- [ ] Explains the 'why'
- [ ] Includes timing context
- [ ] Adds motivation
- [ ] Provides background
- [ ] Encouraging tone

### **For `ai_context` Column:**

- [ ] Includes user intent
- [ ] Adds emotional context
- [ ] Provides execution guidance
- [ ] Includes motivation
- [ ] Personal and caring

### **For `task_type` Column:**

- [ ] Matches content complexity
- [ ] Appropriate for execution method
- [ ] Aligns with user expectations

### **For `schedule_type` Column:**

- [ ] Matches timing needs
- [ ] Appropriate for content type
- [ ] Aligns with user habits

## 🚀 Pro Tips for Database Content

1. **Use JSON for `schedule_config`**: Store timing details, timezone, etc.
2. **Leverage `ai_context`**: This is where you can add personality and motivation
3. **Consider `notification_channels`**: Tailor content length to delivery method
4. **Use `description` strategically**: Add context that helps users understand the reminder
5. **Keep `title` scannable**: Users will see this first, make it count
6. **Update `ai_context` over time**: Learn from user preferences and adjust tone

## 📊 Content Performance Metrics

Track these metrics to improve reminder effectiveness:

- **Completion Rate**: How often users complete the reminded action
- **Response Time**: How quickly users act on reminders
- **User Feedback**: Direct feedback on reminder helpfulness
- **Engagement**: How users interact with different reminder types
- **Channel Effectiveness**: Which notification channels work best for different content types

Remember: The goal is to make reminders feel like helpful nudges from a supportive friend, not nagging notifications from a system! 🎯
