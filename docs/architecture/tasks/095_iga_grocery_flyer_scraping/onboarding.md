# Onboarding: IGA Grocery Flyer Scraping System

## Context

This task implements a weekly automated system to scrape IGA digital flyer data, process it into clean structured data, and store it in the database for future AI-powered grocery tasks.

## Current System Analysis

### Existing Infrastructure

- **Celery System**: Already configured with Redis broker and Beat scheduler
- **Database**: PostgreSQL with migration system in place
- **Logging**: Structured logging with Loki integration
- **Error Handling**: Comprehensive error handling frameworks
- **Background Tasks**: Existing pattern in `ai_tasks.py` and `sms_tasks.py`

### Relevant Files

- `src/personal_assistant/workers/tasks/ai_tasks.py` - Example of existing Celery tasks
- `src/personal_assistant/workers/tasks/sms_tasks.py` - Example of background service tasks
- `src/personal_assistant/workers/celery_app.py` - Celery configuration and Beat schedule
- `src/personal_assistant/database/models/` - Database model patterns
- `src/personal_assistant/services/` - Background service patterns

## Task Objectives

### Primary Goal

Create a weekly automated system that:

1. Scrapes IGA digital flyer JSON data from `https://www.iga.net/en/flyer/digital_flyer`
2. Processes and cleans the data (extract product name, category, price, dates)
3. Stores clean data in database for future AI features
4. Runs automatically every Monday at 6 AM

### Secondary Goal

Establish foundation for future AI-powered grocery features:

- Budget-based recommendations
- Smart shopping lists
- Deal analysis and alerts

## Technical Requirements

### Data Processing

- Parse JSON and extract relevant fields
- Filter for current deals only (based on valid_from/valid_to)
- Organize by category (Dairy, Fruits, Meat, etc.)
- Remove proprietary content and images
- Validate data quality

### Database Design

- Store processed deals with proper relationships
- Maintain historical data for trend analysis
- Implement data deduplication
- Add indexes for efficient querying

### Error Handling

- Handle API rate limiting
- Implement retry logic for failed requests
- Log errors and send notifications
- Graceful degradation on API changes

## Implementation Approach

### Phase 1: Core Infrastructure

1. Create `grocery_tasks.py` following existing task patterns
2. Implement `GroceryDataService` for data processing
3. Create `GroceryDeal` database model
4. Add weekly schedule to Celery Beat

### Phase 2: Data Processing

1. Implement JSON scraping from IGA endpoint
2. Add data cleaning and validation
3. Implement database storage logic
4. Add error handling and monitoring

### Phase 3: Testing and Monitoring

1. Test end-to-end data flow
2. Monitor task execution and data quality
3. Implement alerting for failures
4. Document API and data structure

## Key Considerations

### Data Privacy

- Only store processed, clean data
- Never expose raw JSON or proprietary content
- Implement data retention policies

### Scalability

- Design for multiple grocery chains in future
- Implement efficient database queries
- Consider data archival strategies

### Reliability

- Implement comprehensive error handling
- Add monitoring and alerting
- Design for API changes and failures

## Success Criteria

- Weekly task runs successfully without errors
- Data is scraped and processed correctly
- Database contains clean, structured grocery data
- Historical data is maintained over time
- Foundation is ready for future AI grocery features

## Questions to Clarify

1. Should we implement data archival for old deals?
2. What's the expected data volume per week?
3. Should we add any data validation rules?
4. Do we need any specific error notifications?

## Next Steps

1. Analyze existing Celery task patterns
2. Design database schema for grocery deals
3. Implement data scraping service
4. Add Celery Beat schedule
5. Test end-to-end functionality
6. Monitor and optimize performance
