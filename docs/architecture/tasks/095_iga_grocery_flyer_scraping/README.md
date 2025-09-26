# Task 095: IGA Grocery Flyer Scraping System

## Overview

This task implements a weekly automated system to scrape IGA digital flyer data, process it into clean structured data, and store it in the database for future AI-powered grocery tasks.

## Problem Statement

Users need access to current grocery deals and pricing information to make informed shopping decisions. Currently, there's no automated way to collect and process grocery flyer data, limiting the ability to create AI-powered grocery planning features.

## Solution

Create a comprehensive grocery data collection system that:

- Scrapes IGA digital flyer JSON data weekly
- Processes and cleans the data
- Clears old data before each scrape (deals only valid 7 days)
- Stores clean data in database
- Provides foundation for future AI features

## Architecture

### Data Flow

```
IGA API → Celery Task → Background Service → Clear Old Data → Store New Data
                                                      ↓
                                            (Fresh Data Available for AI Tasks)
```

### Components

- **Celery Task**: Weekly automated scraping
- **Background Service**: Data processing and cleaning
- **Database Model**: Structured storage for grocery deals
- **Celery Beat**: Scheduled execution

## Implementation

### Phase 1: Core Infrastructure

1. Create Celery task for IGA data scraping
2. Implement GroceryDataService for data processing
3. Create GroceryDeal database model
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

## Files Created/Modified

### New Files

- `src/personal_assistant/workers/tasks/grocery_tasks.py`
- `src/personal_assistant/services/grocery_service.py`
- `src/personal_assistant/database/migrations/008_update_grocery_deals_schema.sql`
- `src/personal_assistant/database/migrations/008_update_grocery_deals_schema_rollback.sql`

### Modified Files

- `src/personal_assistant/database/models/grocery_deals.py` (update schema)
- `src/personal_assistant/workers/celery_app.py` (add weekly schedule)

## Database Schema

```python
class GroceryDeal:
    id: int  # IGA product ID
    name: str  # Product name
    sku: str  # Product SKU
    description: str  # Product description
    valid_from: datetime  # Deal start date
    valid_to: datetime  # Deal end date
    categories: List[str]  # Product categories (Produce, Scene+, etc.)
    price_text: str  # Price as text (e.g., "2.99")
    post_price_text: str  # Price details (e.g., "/lb $6.59/kg Member price")
    original_price: Optional[float]  # Original price if on sale
    brand: str  # Product brand
    web_commission_url: str  # Product URL
    scraped_at: datetime  # When data was scraped
    created_at: datetime
    updated_at: datetime
```

## Success Metrics

- [ ] Weekly task runs successfully without errors
- [ ] Data is scraped and processed correctly
- [ ] Database contains clean, structured grocery data
- [ ] Historical data is maintained over time
- [ ] System handles API errors gracefully
- [ ] Foundation is ready for future AI grocery features

## Future Enhancements

- Support for multiple grocery chains
- AI-powered grocery planning features
- Budget-based recommendations
- Smart shopping list generation
- Price trend analysis
- Deal alert notifications

## Getting Started

1. Review the task documentation in `TASK.md`
2. Follow the onboarding guide in `onboarding.md`
3. Use the implementation checklist in `CHECKLIST.md`
4. Start with Phase 1: Core Infrastructure Setup

## Notes

This task focuses on the data collection foundation. Future tasks will build AI-powered features on top of this data, such as budget-based grocery recommendations and smart shopping list generation.
