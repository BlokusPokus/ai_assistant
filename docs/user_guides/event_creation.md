# Event Creation Guide

This guide explains how to create and manage events using the Personal Assistant TDAH system.

## Table of Contents

- [Overview](#overview)
- [Creating Events](#creating-events)
- [Event Types](#event-types)
- [Event Management](#event-management)
- [Calendar Integration](#calendar-integration)
- [Reminders and Notifications](#reminders-and-notifications)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

## Overview

The Personal Assistant system allows you to create and manage events through multiple interfaces:

- **Chat Interface**: Create events through natural language conversation
- **Calendar Integration**: Sync with Google Calendar, Microsoft Outlook, and other providers
- **Direct API**: Use the REST API for programmatic event creation
- **Web Interface**: Use the web dashboard for event management

### Key Features

- **Natural Language Processing**: Create events using conversational commands
- **Multi-Provider Support**: Integration with major calendar providers
- **Smart Scheduling**: AI-powered scheduling suggestions
- **Reminder System**: Automated reminders and notifications
- **Conflict Detection**: Automatic detection of scheduling conflicts
- **Recurring Events**: Support for recurring event patterns

## Creating Events

### Through Chat Interface

The easiest way to create events is through the chat interface using natural language:

#### Basic Event Creation

```
User: "Schedule a meeting with John tomorrow at 2 PM"
Assistant: "I'll create a meeting with John for tomorrow at 2:00 PM. Let me add that to your calendar."

User: "Create a dentist appointment for next Tuesday at 10 AM"
Assistant: "I've scheduled your dentist appointment for Tuesday at 10:00 AM. Would you like me to set a reminder?"

User: "Add a team standup every weekday at 9 AM"
Assistant: "I'll create a recurring team standup meeting for weekdays at 9:00 AM. This will repeat Monday through Friday."
```

#### Advanced Event Creation

```
User: "Schedule a 2-hour project review meeting with the development team next Friday from 2-4 PM in the conference room"
Assistant: "I've created a 2-hour project review meeting with the development team for Friday from 2:00-4:00 PM in the conference room. I've also set up a reminder 30 minutes before the meeting."
```

### Through Web Interface

1. **Navigate to Calendar**: Go to the Calendar section in the web dashboard
2. **Click "New Event"**: Click the "+" button or "New Event" button
3. **Fill Event Details**:
   - **Title**: Event name or description
   - **Date and Time**: Start and end times
   - **Location**: Meeting location or virtual meeting link
   - **Attendees**: Email addresses of participants
   - **Description**: Additional event details
   - **Reminders**: Set reminder notifications
4. **Save Event**: Click "Save" to create the event

### Through API

```bash
# Create a new event
curl -X POST "https://your-domain.com/api/v1/events" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Team Meeting",
    "start_time": "2024-01-15T14:00:00Z",
    "end_time": "2024-01-15T15:00:00Z",
    "location": "Conference Room A",
    "attendees": ["john@example.com", "jane@example.com"],
    "description": "Weekly team standup meeting",
    "reminders": [
      {
        "minutes_before": 15,
        "type": "email"
      }
    ]
  }'
```

## Event Types

### Meeting Events

**Purpose**: Collaborative meetings with multiple participants

**Features**:

- Attendee management
- Meeting room booking
- Virtual meeting links
- Agenda and notes
- Follow-up reminders

**Example**:

```
"Schedule a project kickoff meeting with the design team next Monday at 10 AM for 1 hour in the main conference room"
```

### Appointment Events

**Purpose**: Personal or professional appointments

**Features**:

- Single participant (you)
- Location details
- Preparation reminders
- Travel time calculation

**Example**:

```
"Book a doctor's appointment for next Wednesday at 3 PM"
```

### Task Events

**Purpose**: Time-blocked work sessions

**Features**:

- Focus time blocks
- Task association
- Progress tracking
- Break reminders

**Example**:

```
"Block 2 hours tomorrow morning for writing the project proposal"
```

### Recurring Events

**Purpose**: Events that repeat on a schedule

**Features**:

- Flexible recurrence patterns
- Exception handling
- Automatic scheduling
- Series management

**Example**:

```
"Set up a weekly team standup every Monday at 9 AM"
```

## Event Management

### Editing Events

#### Through Chat

```
User: "Move my meeting with Sarah from tomorrow at 2 PM to 3 PM"
Assistant: "I've rescheduled your meeting with Sarah to tomorrow at 3:00 PM. I'll notify her of the time change."

User: "Change the location of tomorrow's team meeting to the virtual room"
Assistant: "I've updated tomorrow's team meeting to use the virtual meeting room. The meeting link has been sent to all attendees."
```

#### Through Web Interface

1. Click on the event in the calendar view
2. Select "Edit" from the event details
3. Modify the desired fields
4. Click "Save Changes"

### Canceling Events

#### Through Chat

```
User: "Cancel my dentist appointment next Tuesday"
Assistant: "I've canceled your dentist appointment for next Tuesday. Would you like me to help you reschedule?"

User: "Cancel all my meetings for tomorrow"
Assistant: "I've canceled all your meetings for tomorrow. I've also notified all attendees of the cancellations."
```

#### Through Web Interface

1. Click on the event in the calendar view
2. Select "Cancel" from the event details
3. Confirm the cancellation
4. Choose whether to notify attendees

### Event Search and Filtering

#### Through Chat

```
User: "Show me all my meetings this week"
Assistant: "Here are your meetings for this week:
- Monday 9:00 AM: Team Standup
- Tuesday 2:00 PM: Project Review
- Wednesday 10:00 AM: Client Call
- Friday 3:00 PM: Sprint Planning"

User: "What meetings do I have with John this month?"
Assistant: "You have 3 meetings scheduled with John this month:
- January 15th at 2:00 PM: Project Discussion
- January 22nd at 10:00 AM: Status Update
- January 29th at 3:00 PM: Planning Session"
```

## Calendar Integration

### Google Calendar Integration

1. **Connect Google Calendar**:

   - Go to Settings > Integrations
   - Click "Connect Google Calendar"
   - Authorize the application
   - Grant necessary permissions

2. **Sync Settings**:

   - Choose sync direction (one-way or two-way)
   - Select which calendars to sync
   - Set sync frequency

3. **Automatic Sync**:
   - Events created in the Personal Assistant automatically appear in Google Calendar
   - Events created in Google Calendar can be accessed through the Personal Assistant

### Microsoft Outlook Integration

1. **Connect Outlook**:

   - Go to Settings > Integrations
   - Click "Connect Microsoft Outlook"
   - Sign in with your Microsoft account
   - Grant calendar permissions

2. **Calendar Sync**:
   - Events sync bidirectionally
   - Meeting invitations are handled automatically
   - Outlook reminders are preserved

### Other Calendar Providers

The system supports integration with:

- Apple Calendar (via CalDAV)
- Yahoo Calendar
- Any CalDAV-compatible calendar
- Custom calendar systems via API

## Reminders and Notifications

### Reminder Types

#### Email Reminders

- Sent to your registered email address
- Include event details and location
- Can include meeting links and attachments

#### SMS Reminders

- Sent to your registered phone number
- Brief event information
- Quick action buttons (Join, Reschedule, Cancel)

#### Push Notifications

- Mobile app notifications
- Desktop browser notifications
- Real-time alerts

#### In-App Notifications

- Dashboard notifications
- Chat interface alerts
- Calendar view indicators

### Reminder Timing

#### Default Reminders

- **Meetings**: 15 minutes before
- **Appointments**: 30 minutes before
- **Tasks**: 5 minutes before
- **Recurring Events**: 15 minutes before

#### Custom Reminder Settings

```
User: "Set a reminder for my dentist appointment 1 hour before"
Assistant: "I've set a reminder for your dentist appointment 1 hour before the scheduled time."

User: "Remind me about the team meeting 1 day before and 30 minutes before"
Assistant: "I've set two reminders for your team meeting: one day before and 30 minutes before."
```

### Reminder Management

#### Through Chat

```
User: "Show me all my upcoming reminders"
Assistant: "Here are your upcoming reminders:
- Tomorrow 9:00 AM: Team Standup (15 min before)
- Wednesday 2:00 PM: Doctor Appointment (30 min before)
- Friday 10:00 AM: Project Review (1 hour before)"

User: "Cancel the reminder for tomorrow's team meeting"
Assistant: "I've canceled the reminder for tomorrow's team meeting."
```

## Best Practices

### Event Creation Best Practices

1. **Be Specific**: Include all relevant details (time, location, attendees)
2. **Use Clear Titles**: Make event titles descriptive and searchable
3. **Set Appropriate Reminders**: Choose reminder timing based on event importance
4. **Include Context**: Add descriptions for complex events
5. **Consider Travel Time**: Account for travel time between events

### Natural Language Tips

1. **Use Specific Times**: "2 PM" instead of "afternoon"
2. **Include Duration**: "1-hour meeting" instead of just "meeting"
3. **Specify Dates**: "Next Tuesday" or "January 15th"
4. **Mention Attendees**: "with John and Sarah"
5. **Include Location**: "in the conference room" or "via Zoom"

### Calendar Management

1. **Regular Review**: Review your calendar weekly
2. **Buffer Time**: Leave buffer time between events
3. **Consistent Naming**: Use consistent naming conventions
4. **Color Coding**: Use colors to categorize event types
5. **Sync Regularly**: Keep all calendar integrations in sync

### Privacy and Security

1. **Sensitive Information**: Avoid including sensitive details in event titles
2. **Access Control**: Be mindful of who can see your calendar
3. **Data Sharing**: Understand what data is shared with integrated services
4. **Backup**: Regularly backup your calendar data

## Troubleshooting

### Common Issues

#### Event Not Created

**Problem**: Event creation fails or doesn't appear
**Solutions**:

- Check internet connection
- Verify calendar integration is active
- Try creating the event with different wording
- Check for conflicting events

#### Sync Issues

**Problem**: Events don't sync between calendars
**Solutions**:

- Refresh calendar integration
- Check sync settings
- Manually trigger sync
- Contact support if issues persist

#### Reminder Not Received

**Problem**: Reminders not arriving on time
**Solutions**:

- Check notification settings
- Verify email/phone number is correct
- Check spam/junk folders
- Test notification system

#### Time Zone Issues

**Problem**: Events appear at wrong times
**Solutions**:

- Check time zone settings
- Specify time zone in event creation
- Update system time zone
- Verify calendar time zone settings

### Getting Help

#### Through Chat

```
User: "Help me with calendar issues"
Assistant: "I can help you with calendar-related issues. What specific problem are you experiencing?"

User: "My events aren't syncing with Google Calendar"
Assistant: "Let me help you troubleshoot the Google Calendar sync. First, let's check if the integration is still active..."
```

#### Through Support

- **Email Support**: Send detailed issue description to support
- **Documentation**: Check the troubleshooting section in settings
- **Community Forum**: Ask questions in the community forum
- **Video Tutorials**: Watch step-by-step video guides

### Error Messages

#### "Event Creation Failed"

- Check all required fields are filled
- Verify date/time format is correct
- Ensure no scheduling conflicts exist

#### "Calendar Integration Error"

- Re-authenticate calendar connection
- Check API permissions
- Verify calendar access rights

#### "Reminder Setup Failed"

- Check notification preferences
- Verify contact information
- Ensure reminder service is active

This comprehensive event creation guide provides everything you need to effectively create, manage, and maintain events using the Personal Assistant TDAH system.
