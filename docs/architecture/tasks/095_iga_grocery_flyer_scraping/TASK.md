# Task 095: IGA Grocery Flyer Scraping System

## Summary

Implement a weekly automated system to scrape IGA digital flyer data, process it into clean structured data, and store it in the database for future AI-powered grocery tasks.

## Problem Statement

Users need access to current grocery deals and pricing information to make informed shopping decisions. Currently, there's no automated way to collect and process grocery flyer data, limiting the ability to create AI-powered grocery planning features.

## Solution Design

Create a comprehensive grocery data collection system with:

- Weekly automated scraping of IGA digital flyer JSON data
- Data processing and cleaning pipeline
- Database storage for historical grocery deal data
- Foundation for future AI-powered grocery features

## Implementation Plan

### Phase 1: Data Collection Infrastructure

1. **Celery Task Creation**

   - Create `grocery_tasks.py` for weekly IGA data scraping
   - Implement error handling and retry logic
   - Add logging and monitoring

2. **Background Service**

   - Create `GroceryDataService` for data processing
   - Implement JSON parsing and data cleaning
   - Handle data validation and filtering

3. **Database Model**

   - Create `GroceryDeal` model for storing processed data
   - Design schema for product information, pricing, and validity
   - Add indexes for efficient querying

4. **Celery Beat Schedule**
   - Add weekly schedule to `celery_app.py`
   - Configure task to run every Monday at 6 AM
   - Ensure proper error handling and notifications

### Phase 2: Data Processing Pipeline

1. **JSON Scraping**

   - Fetch data from IGA digital flyer endpoint
   - Handle rate limiting and API errors
   - Implement data validation

2. **Data Cleaning**

   - Extract relevant fields from IGA JSON: id, name, sku, description, valid_from, valid_to, categories, price_text, post_price_text, original_price, brand, web_commission_url
   - Filter for current deals only (based on valid_from/valid_to timestamps)
   - Organize by category (Produce, Scene+, etc.)
   - Remove proprietary content (images, coupons, internal fields)

3. **Database Storage**
   - Clear existing data before each scrape (deals only valid 7 days)
   - Store processed deals with proper relationships
   - Implement data deduplication
   - No historical data retention (fresh data each week)

### Data Cleanup Strategy

Since IGA deals are only valid for 7 days, we implement a **complete data refresh** approach:

- **Before each scrape**: Clear all existing data from `grocery_deals` table
- **After scraping**: Store only the new week's deals
- **Benefits**:
  - Prevents stale data accumulation
  - Ensures only current deals are available
  - Simplifies data management
  - Reduces database storage requirements

### Phase 3: Foundation for AI Features

1. **Data Structure**

   - Design schema to support future AI tasks
   - Include fields for budget calculations
   - Add metadata for deal analysis

2. **API Endpoints**
   - Create endpoints for data access
   - Implement filtering and search capabilities
   - Add data export functionality

## Technical Architecture

### Components

```
IGA API → Celery Task → Background Service → Clear Old Data → Store New Data
                                                      ↓
                                            (Fresh Data Available for AI Tasks)
```

### IGA API Details

- **Endpoint**: `https://www.iga.net/en/flyer/digital_flyer`
- **Data Format**: JSON array of product objects
- **Update Frequency**: Weekly (typically Monday)
- **Data Structure**: Each product contains ~25 fields, we extract only ~12 relevant fields

### Sample Data Structure

```json
{
  "id": 958213363,
  "name": "SEEDLESS GREEN GRAPES",
  "sku": "00000_000000000000004022",
  "description": "Product of USA\nCatégorie no 1 Grade",
  "valid_from": "2025-09-18",
  "valid_to": "2025-09-24",
  "categories": ["Produce", "Scene+"],
  "price_text": "2.99",
  "post_price_text": "/lb $6.59/kg Member price",
  "original_price": null,
  "brand": "",
  "web_commission_url": "https://www.iga.net/en/product/00000_000000000000004022"
}
```

### File Structure

```
src/personal_assistant/
├── workers/tasks/
│   └── grocery_tasks.py          # NEW: Weekly IGA scraping task
├── services/
│   └── grocery_service.py        # NEW: Data processing service
├── database/models/
│   └── grocery_deals.py         # MODIFY: Update existing model
├── database/migrations/
│   ├── 008_update_grocery_deals_schema.sql        # NEW: Schema migration
│   └── 008_update_grocery_deals_schema_rollback.sql # NEW: Rollback migration
└── workers/
    └── celery_app.py            # MODIFY: Add weekly schedule
```

### Database Schema

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

## Risks and Mitigation

1. **API Changes**: IGA may change their JSON structure
   - Mitigation: Implement robust error handling and monitoring
2. **Rate Limiting**: API may have usage limits
   - Mitigation: Implement proper delays and retry logic
3. **Data Quality**: Raw data may be inconsistent
   - Mitigation: Implement comprehensive data validation
4. **Storage Growth**: Database may grow large over time
   - Mitigation: Implement data archival and cleanup strategies

## Dependencies

- Existing Celery infrastructure
- Database migration system
- Logging and monitoring systems
- Error handling frameworks

## Future Enhancements

- Support for multiple grocery chains
- AI-powered grocery planning features
- Budget-based recommendations
- Smart shopping list generation
- Price trend analysis
- Deal alert notifications

## Implementation Checklist

- [ ] Create Celery task for IGA data scraping
- [ ] Implement GroceryDataService for data processing
- [ ] Create GroceryDeal database model
- [ ] Add weekly schedule to Celery Beat
- [ ] Implement error handling and logging
- [ ] Add data validation and cleaning
- [ ] Test end-to-end data flow
- [ ] Monitor task execution and data quality
- [ ] Document API and data structure
- [ ] Prepare foundation for AI features

## Notes

This task focuses on the data collection foundation. Future tasks will build AI-powered features on top of this data, such as budget-based grocery recommendations and smart shopping list generation.
