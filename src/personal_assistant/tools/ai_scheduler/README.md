<!-- # Calendar Scheduler Implementation

This module implements a database-first calendar scheduler that runs every 10 minutes to check for upcoming events and trigger intelligent agent responses.

## Overview

The scheduler follows a database-first approach, meaning it queries the local database for upcoming events instead of relying on external APIs. This provides better performance, offline capability, and simplified testing.

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Celery Beat   │    │  Celery Worker  │    │   Agent Core    │
│   (Scheduler)   │───▶│   (Processor)   │───▶│   (AI Agent)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Redis Queue   │    │   Database      │    │   Event Log     │
│   (Message      │    │   (Events)      │    │   (Processing   │
│    Broker)      │    │                 │    │    History)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Components

### 1. Database Models

- **Event Model** (`database/models/events.py`): Extended with processing status fields
- **EventProcessingLog Model** (`database/models/event_processing_log.py`): Tracks processing history

### 2. Celery Configuration

- **celery_config.py**: Configures Celery with Redis as message broker
- **tasks.py**: Defines background tasks for event processing
- **db_queries.py**: Database query functions for event management

### 3. Scheduler

- **scheduler.py**: Main scheduler class and entry points
- **test_scheduler.py**: Test script for verification

## Features

### Core Functionality

- **Cron Job**: Runs every 10 minutes via Celery Beat
- **Database Queries**: Direct SQL queries for upcoming events
- **Background Processing**: Celery worker handles event processing
- **Agent Integration**: Triggers AgentCore for intelligent responses
- **Error Handling**: Graceful failure handling with retries
- **Status Tracking**: Comprehensive event processing status tracking

### Event Processing Workflow

1. **Query Events**: Find upcoming events in next 2 hours (configurable)
2. **Mark Processing**: Update event status to 'processing'
3. **Agent Processing**: Trigger AgentCore with event context
4. **Status Update**: Mark as 'completed' or 'failed' based on result
5. **Logging**: Track all processing attempts in EventProcessingLog

### Status Management

Events can have the following statuses:

- `pending`: Ready for processing
- `processing`: Currently being processed
- `completed`: Successfully processed
- `failed`: Processing failed (will retry after 1 hour)

## Configuration

### Environment Variables

```bash
# Redis Configuration
REDIS_URL=redis://localhost:6379
CELERY_BROKER_URL=redis://localhost:6379
CELERY_RESULT_BACKEND=redis://localhost:6379

# Scheduler Configuration
SCHEDULER_CHECK_INTERVAL=10  # minutes
EVENT_TIME_WINDOW=2  # hours to look ahead
```

### Database Schema

The Event model has been extended with these fields:

```sql
ALTER TABLE events ADD COLUMN handled_at TIMESTAMP;
ALTER TABLE events ADD COLUMN processing_status VARCHAR(20) DEFAULT 'pending';
ALTER TABLE events ADD COLUMN agent_response TEXT;
ALTER TABLE events ADD COLUMN last_checked TIMESTAMP;
```

## Usage

### Installation

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Install Redis (macOS):

```bash
brew install redis
brew services start redis
```

### Running the Scheduler

#### Option 1: Using the startup script

```bash
# Install dependencies
./scripts/start_calendar_scheduler.sh install

# Run tests
./scripts/start_calendar_scheduler.sh test

# Start the scheduler
./scripts/start_calendar_scheduler.sh start
```

#### Option 2: Manual startup

```bash
# Terminal 1: Start Celery worker
cd agent_core/tools/ai_calendar
python scheduler.py worker

# Terminal 2: Start Celery beat scheduler
cd agent_core/tools/ai_calendar
python scheduler.py beat
```

#### Option 3: Using Celery directly

```bash
# Start worker
celery -A agent_core.tools.ai_calendar.celery_config worker --loglevel=info

# Start beat scheduler
celery -A agent_core.tools.ai_calendar.celery_config beat --loglevel=info
```

### Testing

Run the test script to verify the implementation:

```bash
python agent_core/tools/ai_calendar/test_scheduler.py
```

## Database Queries

### Key Query Functions

- `get_upcoming_events(hours_ahead=2)`: Find events in next N hours
- `mark_event_processing(event_id)`: Mark event as processing
- `mark_event_completed(event_id, response)`: Mark event as completed
- `mark_event_failed(event_id, error)`: Mark event as failed
- `reset_failed_events()`: Reset old failed events for retry

### Example Query

```python
# Get upcoming events
events = await get_upcoming_events(hours_ahead=2)

# Process each event
for event in events:
    await mark_event_processing(event.id)
    # ... process with agent ...
    await mark_event_completed(event.id, agent_response)
```

## Monitoring

### Logs

The scheduler provides comprehensive logging:

- Task execution logs
- Database operation logs
- Error and retry logs
- Agent processing logs

### Status Tracking

- Event processing status in database
- Processing history in EventProcessingLog
- Task execution statistics
- Error tracking and retry counts

## Error Handling

### Retry Logic

- Failed tasks are retried up to 3 times
- Exponential backoff between retries
- Failed events are reset after 1 hour for manual retry

### Graceful Degradation

- Database connection errors are handled gracefully
- Agent processing failures don't stop the scheduler
- Individual event failures don't affect other events

## Benefits of Database-First Approach

1. **Performance**: Direct database queries are faster than API calls
2. **Reliability**: No dependency on external API availability
3. **Offline Capability**: System works without internet connection
4. **Testing**: Easy to test with local database data
5. **Control**: Full control over event data and processing logic

## Future Enhancements

1. **Event Filtering**: Add NLP-based event filtering
2. **Notification System**: Integrate with SMS/email notifications
3. **Advanced Scheduling**: Support for different event types and priorities
4. **Metrics Dashboard**: Web interface for monitoring scheduler status
5. **Event Templates**: Predefined responses for common event types

## Troubleshooting

### Common Issues

1. **Redis Connection**: Ensure Redis is running
2. **Database Connection**: Check database URL and credentials
3. **AgentCore Import**: Verify AgentCore is properly configured
4. **Async/Await**: Ensure proper async handling in Celery tasks

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Manual Testing

Test individual components:

```bash
# Test database queries
python -c "import asyncio; from agent_core.tools.ai_calendar.db_queries import get_upcoming_events; print(asyncio.run(get_upcoming_events()))"

# Test scheduler configuration
python -c "from agent_core.tools.ai_calendar.scheduler import create_scheduler; print(create_scheduler().get_status())"
``` -->
