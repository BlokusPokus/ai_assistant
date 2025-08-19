# Database Schema Summary

This document provides a comprehensive overview of all database tables and columns extracted from the SQLAlchemy models in the personal assistant codebase.

## Overview

- **Total Tables**: 24
- **Total Columns**: 147
- **Generated**: Programmatically from SQLAlchemy models

## Table Details

### 1. users

**File**: `src/personal_assistant/database/models/users.py`
**Class**: `User`

| Column     | Type     | Constraints      | Notes                      |
| ---------- | -------- | ---------------- | -------------------------- |
| id         | Integer  | PRIMARY KEY      | Auto-generated ID          |
| email      | String   | UNIQUE, NOT NULL | User's email address       |
| full_name  | String   |                  | User's full name           |
| created_at | DateTime |                  | Account creation timestamp |

**Relationships**: `memory_chunks`

### 2. memory_chunks

**File**: `src/personal_assistant/database/models/memory_chunk.py`
**Class**: `MemoryChunk`

| Column     | Type     | Constraints             | Notes                 |
| ---------- | -------- | ----------------------- | --------------------- |
| id         | Integer  | PRIMARY KEY             | Auto-generated ID     |
| user_id    | Integer  | FOREIGN KEY -> users.id | References user       |
| content    | Text     |                         | Memory content        |
| embedding  | JSON     |                         | Vector embedding data |
| created_at | DateTime |                         | Creation timestamp    |

**Relationships**: `meta_entries`, `user`

### 3. memory_metadata

**File**: `src/personal_assistant/database/models/memory_metadata.py`
**Class**: `MemoryMetadata`

| Column   | Type    | Constraints                     | Notes                   |
| -------- | ------- | ------------------------------- | ----------------------- |
| id       | Integer | PRIMARY KEY                     | Auto-generated ID       |
| chunk_id | Integer | FOREIGN KEY -> memory_chunks.id | References memory chunk |
| key      | String  |                                 | Metadata key            |
| value    | String  |                                 | Metadata value          |

**Relationships**: `chunk`

### 4. ai_tasks

**File**: `src/personal_assistant/database/models/ai_tasks.py`
**Class**: `AITask`

| Column                | Type          | Constraints                       | Notes                                         |
| --------------------- | ------------- | --------------------------------- | --------------------------------------------- |
| id                    | Integer       | PRIMARY KEY                       | Auto-generated ID                             |
| user_id               | Integer       | FOREIGN KEY -> users.id, NOT NULL | References user                               |
| title                 | String(255)   | NOT NULL                          | Task title                                    |
| description           | Text          |                                   | Task description                              |
| task_type             | String(50)    | NOT NULL                          | Type: reminder, automated_task, periodic_task |
| schedule_type         | String(20)    | NOT NULL                          | Type: once, daily, weekly, monthly, custom    |
| schedule_config       | JSON          |                                   | Cron expression, interval, etc.               |
| next_run_at           | DateTime      |                                   | Next scheduled run time                       |
| last_run_at           | DateTime      |                                   | Last execution time                           |
| status                | String(20)    |                                   | Status: active, paused, completed, failed     |
| ai_context            | Text          |                                   | Context for AI processing                     |
| notification_channels | ARRAY(String) |                                   | Channels: sms, email, in_app                  |
| created_at            | DateTime      |                                   | Creation timestamp                            |
| updated_at            | DateTime      |                                   | Last update timestamp                         |

### 5. events

**File**: `src/personal_assistant/database/models/events.py`
**Class**: `Event`

| Column                     | Type     | Constraints                           | Notes                                          |
| -------------------------- | -------- | ------------------------------------- | ---------------------------------------------- |
| id                         | Integer  | PRIMARY KEY                           | Auto-generated ID                              |
| user_id                    | Integer  | FOREIGN KEY -> users.id               | References user                                |
| title                      | String   |                                       | Event title                                    |
| description                | String   |                                       | Event description                              |
| start_time                 | DateTime |                                       | Event start time                               |
| end_time                   | DateTime |                                       | Event end time                                 |
| source                     | String   |                                       | Source: assistant                              |
| external_id                | String   |                                       | External system ID                             |
| handled_at                 | DateTime |                                       | When event was handled                         |
| processing_status          | String   |                                       | Status: pending, processing, completed, failed |
| agent_response             | Text     |                                       | AI agent response                              |
| last_checked               | DateTime |                                       | Last check timestamp                           |
| recurrence_pattern_id      | Integer  | FOREIGN KEY -> recurrence_patterns.id | Recurrence pattern reference                   |
| is_recurring               | Boolean  |                                       | Whether event recurs                           |
| parent_event_id            | Integer  | FOREIGN KEY -> events.id              | Parent recurring event                         |
| recurrence_instance_number | Integer  |                                       | Instance number in series                      |

### 6. recurrence_patterns

**File**: `src/personal_assistant/database/models/recurrence_patterns.py`
**Class**: `RecurrencePattern`

| Column          | Type     | Constraints | Notes                            |
| --------------- | -------- | ----------- | -------------------------------- |
| id              | Integer  | PRIMARY KEY | Auto-generated ID                |
| frequency       | String   | NOT NULL    | Recurrence frequency             |
| interval        | Integer  |             | Interval between occurrences     |
| weekdays        | ARRAY    |             | Days of week for weekly patterns |
| end_date        | DateTime |             | End date for pattern             |
| max_occurrences | Integer  |             | Maximum number of occurrences    |
| created_at      | DateTime |             | Creation timestamp               |

### 7. expenses

**File**: `src/personal_assistant/database/models/expenses.py`
**Class**: `Expense`

| Column      | Type     | Constraints                          | Notes               |
| ----------- | -------- | ------------------------------------ | ------------------- |
| id          | Integer  | PRIMARY KEY                          | Auto-generated ID   |
| user_id     | Integer  | FOREIGN KEY -> users.id              | References user     |
| amount      | Numeric  |                                      | Expense amount      |
| category_id | Integer  | FOREIGN KEY -> expense_categories.id | Expense category    |
| description | String   |                                      | Expense description |
| created_at  | DateTime |                                      | Creation timestamp  |

### 8. expense_categories

**File**: `src/personal_assistant/database/models/expense_category.py`
**Class**: `ExpenseCategory`

| Column | Type    | Constraints | Notes             |
| ------ | ------- | ----------- | ----------------- |
| id     | Integer | PRIMARY KEY | Auto-generated ID |
| name   | String  | NOT NULL    | Category name     |

### 9. grocery_items

**File**: `src/personal_assistant/database/models/grocery_items.py`
**Class**: `GroceryItem`

| Column   | Type     | Constraints             | Notes              |
| -------- | -------- | ----------------------- | ------------------ |
| id       | Integer  | PRIMARY KEY             | Auto-generated ID  |
| user_id  | Integer  | FOREIGN KEY -> users.id | References user    |
| name     | String   |                         | Item name          |
| quantity | String   |                         | Item quantity      |
| added_at | DateTime |                         | When added to list |

### 10. grocery_deals

**File**: `src/personal_assistant/database/models/grocery_deals.py`
**Class**: `GroceryDeal`

| Column     | Type     | Constraints | Notes              |
| ---------- | -------- | ----------- | ------------------ |
| id         | Integer  | PRIMARY KEY | Auto-generated ID  |
| source     | String   |             | Deal source        |
| title      | String   |             | Deal title         |
| price      | String   |             | Deal price         |
| image_url  | String   |             | Deal image URL     |
| flyer_date | Date     |             | Flyer date         |
| created_at | DateTime |             | Creation timestamp |

### 11. grocery_analysis

**File**: `src/personal_assistant/database/models/grocery_analysis.py`
**Class**: `GroceryAnalysis`

| Column     | Type     | Constraints             | Notes              |
| ---------- | -------- | ----------------------- | ------------------ |
| id         | Integer  | PRIMARY KEY             | Auto-generated ID  |
| user_id    | Integer  | FOREIGN KEY -> users.id | References user    |
| analysis   | JSON     |                         | Analysis results   |
| created_at | DateTime |                         | Creation timestamp |

### 12. notes

**File**: `src/personal_assistant/database/models/notes.py`
**Class**: `Note`

| Column      | Type     | Constraints             | Notes               |
| ----------- | -------- | ----------------------- | ------------------- |
| id          | Integer  | PRIMARY KEY             | Auto-generated ID   |
| user_id     | Integer  | FOREIGN KEY -> users.id | References user     |
| title       | String   |                         | Note title          |
| content     | String   |                         | Note content        |
| created_at  | DateTime |                         | Creation timestamp  |
| last_synced | DateTime |                         | Last sync timestamp |

### 13. tasks

**File**: `src/personal_assistant/database/models/tasks.py`
**Class**: `Task`

| Column       | Type     | Constraints             | Notes              |
| ------------ | -------- | ----------------------- | ------------------ |
| id           | Integer  | PRIMARY KEY             | Auto-generated ID  |
| user_id      | Integer  | FOREIGN KEY -> users.id | References user    |
| task_name    | String   |                         | Task name          |
| status       | String   |                         | Task status        |
| scheduled_at | DateTime |                         | Scheduled time     |
| created_at   | DateTime |                         | Creation timestamp |

### 14. reminders

**File**: `src/personal_assistant/database/models/reminders.py`
**Class**: `Reminder`

| Column     | Type     | Constraints             | Notes                     |
| ---------- | -------- | ----------------------- | ------------------------- |
| id         | Integer  | PRIMARY KEY             | Auto-generated ID         |
| user_id    | Integer  | FOREIGN KEY -> users.id | References user           |
| message    | String   | NOT NULL                | Reminder message          |
| remind_at  | DateTime | NOT NULL                | When to remind            |
| created_at | DateTime |                         | Creation timestamp        |
| sent       | Boolean  |                         | Whether reminder was sent |

### 15. ltm_memories

**File**: `src/personal_assistant/database/models/ltm_memory.py`
**Class**: `LTMMemory`

| Column           | Type     | Constraints                       | Notes                 |
| ---------------- | -------- | --------------------------------- | --------------------- |
| id               | Integer  | PRIMARY KEY                       | Auto-generated ID     |
| user_id          | Integer  | FOREIGN KEY -> users.id, NOT NULL | References user       |
| content          | Text     | NOT NULL                          | Memory content        |
| tags             | JSON     | NOT NULL                          | Memory tags           |
| importance_score | Integer  |                                   | Importance rating     |
| context          | Text     |                                   | Memory context        |
| created_at       | DateTime |                                   | Creation timestamp    |
| last_accessed    | DateTime |                                   | Last access timestamp |

### 16. agent_logs

**File**: `src/personal_assistant/database/models/agent_logs.py`
**Class**: `AgentLog`

| Column         | Type     | Constraints             | Notes                   |
| -------------- | -------- | ----------------------- | ----------------------- |
| id             | Integer  | PRIMARY KEY             | Auto-generated ID       |
| user_id        | Integer  | FOREIGN KEY -> users.id | References user         |
| user_input     | String   |                         | User input              |
| agent_response | String   |                         | AI agent response       |
| tool_called    | String   |                         | Tool that was called    |
| tool_output    | String   |                         | Tool output             |
| memory_used    | JSON     |                         | Memory used in response |
| timestamp      | DateTime |                         | Interaction timestamp   |

### 17. auth_tokens

**File**: `src/personal_assistant/database/models/auth_tokens.py`
**Class**: `AuthToken`

| Column     | Type     | Constraints             | Notes                |
| ---------- | -------- | ----------------------- | -------------------- |
| id         | Integer  | PRIMARY KEY             | Auto-generated ID    |
| user_id    | Integer  | FOREIGN KEY -> users.id | References user      |
| token      | String   | NOT NULL                | Authentication token |
| expires_at | DateTime |                         | Token expiration     |
| created_at | DateTime |                         | Creation timestamp   |

### 18. user_settings

**File**: `src/personal_assistant/database/models/user_settings.py`
**Class**: `UserSetting`

| Column  | Type    | Constraints             | Notes             |
| ------- | ------- | ----------------------- | ----------------- |
| id      | Integer | PRIMARY KEY             | Auto-generated ID |
| user_id | Integer | FOREIGN KEY -> users.id | References user   |
| key     | String  | NOT NULL                | Setting key       |
| value   | String  |                         | Setting value     |

### 19. event_creation_logs

**File**: `src/personal_assistant/database/models/event_creation_logs.py`
**Class**: `EventCreationLog`

| Column         | Type     | Constraints             | Notes                    |
| -------------- | -------- | ----------------------- | ------------------------ |
| id             | Integer  | PRIMARY KEY             | Auto-generated ID        |
| user_id        | Integer  | FOREIGN KEY -> users.id | References user          |
| user_input     | Text     |                         | User input text          |
| parsed_details | JSON     |                         | Parsed event details     |
| created_events | Integer  |                         | Number of events created |
| errors         | Text     |                         | Any errors encountered   |
| created_at     | DateTime |                         | Creation timestamp       |

### 20. event_processing_log

**File**: `src/personal_assistant/database/models/event_processing_log.py`
**Class**: `EventProcessingLog`

| Column            | Type     | Constraints              | Notes                |
| ----------------- | -------- | ------------------------ | -------------------- |
| id                | Integer  | PRIMARY KEY              | Auto-generated ID    |
| event_id          | Integer  | FOREIGN KEY -> events.id | References event     |
| processed_at      | DateTime |                          | Processing timestamp |
| agent_response    | Text     |                          | AI agent response    |
| processing_status | String   |                          | Processing status    |
| error_message     | Text     |                          | Error message if any |

### 21. note_sync_log

**File**: `src/personal_assistant/database/models/note_sync_log.py`
**Class**: `NoteSyncLog`

| Column      | Type     | Constraints             | Notes             |
| ----------- | -------- | ----------------------- | ----------------- |
| id          | Integer  | PRIMARY KEY             | Auto-generated ID |
| user_id     | Integer  | FOREIGN KEY -> users.id | References user   |
| note_id     | Integer  | FOREIGN KEY -> notes.id | References note   |
| synced_at   | DateTime |                         | Sync timestamp    |
| sync_status | String   |                         | Sync status       |

### 22. budget_sync_log

**File**: `src/personal_assistant/database/models/budget_sync_log.py`
**Class**: `BudgetSyncLog`

| Column      | Type     | Constraints             | Notes             |
| ----------- | -------- | ----------------------- | ----------------- |
| id          | Integer  | PRIMARY KEY             | Auto-generated ID |
| user_id     | Integer  | FOREIGN KEY -> users.id | References user   |
| synced_at   | DateTime |                         | Sync timestamp    |
| sync_status | String   |                         | Sync status       |

### 23. calendar_sync_log

**File**: `src/personal_assistant/database/models/calendar_sync_log.py`
**Class**: `CalendarSyncLog`

| Column      | Type     | Constraints             | Notes             |
| ----------- | -------- | ----------------------- | ----------------- |
| id          | Integer  | PRIMARY KEY             | Auto-generated ID |
| user_id     | Integer  | FOREIGN KEY -> users.id | References user   |
| synced_at   | DateTime |                         | Sync timestamp    |
| sync_status | String   |                         | Sync status       |

### 24. task_results

**File**: `src/personal_assistant/database/models/task_results.py`
**Class**: `TaskResult`

| Column       | Type     | Constraints             | Notes                |
| ------------ | -------- | ----------------------- | -------------------- |
| id           | Integer  | PRIMARY KEY             | Auto-generated ID    |
| task_id      | Integer  | FOREIGN KEY -> tasks.id | References task      |
| result       | JSON     |                         | Task result data     |
| completed_at | DateTime |                         | Completion timestamp |

## Key Relationships

1. **users** is the central table with most other tables referencing it via `user_id`
2. **memory_chunks** and **memory_metadata** work together for memory storage
3. **events** can reference **recurrence_patterns** for recurring events
4. **expenses** reference **expense_categories** for categorization
5. **ai_tasks** provide AI-powered task management
6. **ltm_memories** store long-term memory with tagging

## Data Types Used

- **Integer**: IDs, foreign keys, counts
- **String**: Names, titles, descriptions, status values
- **Text**: Longer content, descriptions
- **DateTime**: Timestamps, scheduled times
- **JSON**: Flexible data storage (embeddings, configurations, analysis results)
- **Boolean**: True/false flags
- **Numeric**: Financial amounts
- **Date**: Date-only values
- **ARRAY**: PostgreSQL arrays for multiple values

## Generated Files

The extraction script generated three output files:

1. `database_schema_report_v2.txt` - Human-readable report
2. `database_schema_ddl_v2.sql` - SQL DDL statements
3. `database_schema_v2.json` - Structured JSON representation

This schema represents a comprehensive personal assistant system with capabilities for:

- User management and authentication
- Memory storage and retrieval
- Task and reminder management
- Event scheduling and recurrence
- Financial tracking
- Grocery management
- Note taking and synchronization
- AI-powered task automation
- Comprehensive logging and monitoring
