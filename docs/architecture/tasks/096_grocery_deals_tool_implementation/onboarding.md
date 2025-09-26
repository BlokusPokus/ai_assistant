# Task 096: Grocery Deals Tool Implementation - Onboarding

## Context & Current System Analysis

### Existing Architecture

The personal assistant system has a robust tool architecture with:

- **Tool Registry**: Centralized tool management in `src/personal_assistant/tools/__init__.py`
- **Tool Metadata System**: Enhanced metadata in `src/personal_assistant/tools/metadata/` for AI understanding
- **Database Integration**: SQLAlchemy models with async database connections
- **LLM Integration**: Tools interact with Gemini LLM for intelligent responses
- **User Management**: User-specific data and preferences
- **Background Services**: Celery tasks for automated data collection

### Current Grocery System Status

**Task 095 (IGA Grocery Flyer Scraping) is COMPLETED:**

- ✅ **Database Schema**: `grocery_deals` table with IGA product structure
- ✅ **Data Collection**: Automated weekly scraping via Celery tasks
- ✅ **Data Processing**: 312+ valid products processed and stored
- ✅ **Data Cleanup**: Old data cleared before new scrapes
- ✅ **Scheduling**: Weekly automation (Monday 6 AM)

### Available Data Structure

```sql
-- Current grocery_deals table structure
CREATE TABLE grocery_deals (
    id INTEGER PRIMARY KEY,           -- IGA product ID
    name VARCHAR(255) NOT NULL,       -- Product name
    sku VARCHAR(100) NOT NULL,         -- Product SKU
    description TEXT,                  -- Product description
    brand VARCHAR(255),                -- Brand name
    valid_from TIMESTAMP NOT NULL,     -- Deal start date
    valid_to TIMESTAMP NOT NULL,       -- Deal end date
    price_text VARCHAR(100) NOT NULL,  -- Price as text (e.g., "2.99")
    post_price_text VARCHAR(255),     -- Additional price info
    original_price FLOAT,             -- Original price if on sale
    categories JSON,                   -- Product categories array
    web_commission_url TEXT,          -- Product URL
    scraped_at TIMESTAMP NOT NULL,    -- When data was scraped
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Sample Data Available

```json
{
  "id": 958213363,
  "name": "SEEDLESS GREEN GRAPES",
  "sku": "00000_000000000000004022",
  "description": "Product of USA\nCatégorie no 1 Grade",
  "brand": "",
  "valid_from": "2025-09-18T00:00:00-04:00",
  "valid_to": "2025-09-24T23:59:59-04:00",
  "price_text": "2.99",
  "post_price_text": "/lb $6.59/kg Member price",
  "original_price": null,
  "categories": ["Produce", "Scene+"],
  "web_commission_url": "https://www.iga.net/en/product/00000_000000000000004022"
}
```

## Task Objectives

### Primary Goal

Create a comprehensive `grocery_deals_tool` that allows users to intelligently interact with IGA grocery deals data through four core methods:

1. **Search & Discovery**: Find deals by name, category, price
2. **Budget Planning**: Plan meals and shopping within budgets
3. **Deal Analysis**: Compare deals, find best value, calculate savings
4. **User Management**: Manage preferences, alerts, and shopping history

### Success Criteria

- **User Experience**: Intuitive, helpful responses to grocery queries
- **Performance**: < 500ms response time for searches
- **Accuracy**: 99%+ accurate deal information
- **Functionality**: All four core methods working effectively

## Technical Implementation Details

### Tool Architecture Pattern

Following existing tool patterns (like `enhanced_notes_tool`):

```python
# src/personal_assistant/tools/grocery/grocery_deals_tool.py
class GroceryDealsTool:
    def __init__(self):
        self.db_config = db_config
        self.logger = logging.getLogger(__name__)

    def search_deals(self, query: str, category: str = None,
                    max_price: float = None, min_price: float = None) -> str:
        """Search grocery deals with filters."""

    def plan_budget_meals(self, budget: float, meal_type: str = "weekly") -> str:
        """Plan meals within budget using current deals."""

    def analyze_deals(self, deal_ids: List[int], analysis_type: str = "compare") -> str:
        """Analyze deals for best value and comparisons."""

    def manage_deals(self, action: str, user_id: int, **kwargs) -> str:
        """Manage user preferences, alerts, and deal tracking."""
```

### Database Query Strategy

```sql
-- Optimized search query
SELECT id, name, sku, description, brand, price_text,
       post_price_text, original_price, categories, valid_to
FROM grocery_deals
WHERE name ILIKE '%query%'
AND (category IS NULL OR categories @> '["category"]')
AND price_text::numeric BETWEEN COALESCE(min_price, 0) AND COALESCE(max_price, 999999)
AND valid_to > NOW()
ORDER BY price_text::numeric ASC
LIMIT 20;

-- Budget optimization query
SELECT *, price_text::numeric as price_numeric
FROM grocery_deals
WHERE price_text::numeric <= budget
AND valid_to > NOW()
ORDER BY price_text::numeric ASC;
```

### Integration Points

- **Tool Registry**: Register in `src/personal_assistant/tools/__init__.py`
- **Tool Metadata**: Create comprehensive metadata in `src/personal_assistant/tools/metadata/grocery_deals_metadata.py`
- **Database**: Use existing `db_config` and `GroceryDeal` model
- **LLM Integration**: Format responses for Gemini LLM consumption
- **User Context**: Access user preferences and history

### Tool Metadata System

The system includes a comprehensive metadata system that helps the AI understand and use tools effectively:

**Existing Metadata Files:**

- `note_metadata.py` - Enhanced metadata for note tools
- `email_metadata.py` - Email tool metadata
- `todo_metadata.py` - Todo tool metadata
- `ai_task_metadata.py` - AI task tool metadata

**Metadata Components:**

- **Use Cases**: Specific scenarios and examples
- **Parameters**: Expected inputs and outputs
- **Success Indicators**: How to measure success
- **Failure Modes**: Common failure scenarios
- **Complexity**: Tool complexity level
- **Category**: Tool categorization

**Required for Grocery Deals Tool:**

- Create `grocery_deals_metadata.py` following existing patterns
- Define use cases for all four methods
- Add example requests and parameters
- Define success/failure indicators
- Set appropriate complexity and category

## Implementation Phases

### Phase 1: Foundation (Days 1-2)

- [ ] Create tool class structure
- [ ] Implement database connection
- [ ] Add basic error handling
- [ ] Create tool registration

### Phase 2: Core Search (Days 3-4)

- [ ] Implement `search_deals()` method
- [ ] Add category filtering
- [ ] Implement price range filtering
- [ ] Add fuzzy search capabilities

### Phase 3: Budget Planning (Days 5-6)

- [ ] Implement `plan_budget_meals()` method
- [ ] Add budget optimization algorithms
- [ ] Create meal planning integration
- [ ] Add dietary restriction filtering

### Phase 4: Analysis & Management (Days 7-8)

- [ ] Implement `analyze_deals()` method
- [ ] Add `manage_deals()` method
- [ ] Create user preference storage
- [ ] Add deal alert system

### Phase 5: Testing & Optimization (Days 9-10)

- [ ] Comprehensive testing
- [ ] Performance optimization
- [ ] User experience refinement
- [ ] Documentation completion

## Key Considerations

### Data Quality

- **Validity Checking**: Only show deals where `valid_to > NOW()`
- **Price Parsing**: Handle `price_text` conversion to numeric values
- **Category Handling**: Parse JSON categories array for filtering
- **Error Handling**: Graceful handling of missing or invalid data

### Performance Optimization

- **Database Indexes**: Add indexes for common search patterns
- **Query Optimization**: Use efficient SQL queries
- **Caching**: Consider caching for frequently accessed data
- **Pagination**: Limit results to prevent large responses

### User Experience

- **Response Formatting**: Clear, readable deal information
- **Error Messages**: Helpful error messages for invalid inputs
- **Context Awareness**: Remember user preferences across sessions
- **Accessibility**: Ensure responses work with screen readers

### Security & Privacy

- **User Data**: Protect user preferences and shopping history
- **Input Validation**: Validate all user inputs
- **SQL Injection**: Use parameterized queries
- **Data Access**: Ensure proper user data isolation

## Testing Strategy

### Unit Tests

- [ ] Test each method with various inputs
- [ ] Test database query performance
- [ ] Test error handling scenarios
- [ ] Test edge cases (empty results, invalid inputs)

### Integration Tests

- [ ] Test tool registration and initialization
- [ ] Test database connectivity
- [ ] Test end-to-end user workflows
- [ ] Test performance under load

### User Acceptance Tests

- [ ] Test with real user scenarios
- [ ] Validate search accuracy
- [ ] Test budget planning effectiveness
- [ ] Validate deal analysis usefulness

## Success Metrics

### Technical Metrics

- **Response Time**: < 500ms for search queries
- **Accuracy**: 99%+ accurate deal information
- **Uptime**: 99.9% availability
- **Error Rate**: < 1% error rate

### User Metrics

- **Search Queries**: 100+ searches per day
- **Budget Calculations**: 50+ budget plans per day
- **User Satisfaction**: 4.5+ star rating
- **Return Usage**: 70%+ users return weekly

### Business Metrics

- **Deal Conversion**: 30%+ of searched deals lead to store visits
- **User Savings**: Average $20+ saved per user per week
- **Store Traffic**: 15%+ increase in IGA store visits

## Risk Mitigation

### Technical Risks

- **Database Performance**: Implement proper indexing and query optimization
- **Search Accuracy**: Use PostgreSQL full-text search with ranking
- **Budget Algorithm**: Start with simple algorithms, iterate based on feedback

### Business Risks

- **User Adoption**: Focus on core value propositions, conduct user testing
- **Data Quality**: Implement data validation and error handling
- **Competition**: Focus on unique value propositions (budget planning, analysis)

## Dependencies

### Completed Dependencies

- ✅ **Task 095**: IGA Grocery Flyer Scraping System
- ✅ **Database Schema**: `grocery_deals` table
- ✅ **Data Collection**: Automated weekly scraping
- ✅ **Tool Architecture**: Existing tool patterns and infrastructure

### External Dependencies

- **PostgreSQL**: Database with full-text search capabilities
- **Python Libraries**: `sqlalchemy`, `asyncpg`, `fuzzywuzzy`
- **IGA Data**: Reliable data source (automated via Task 095)

## Next Steps

1. **Review Existing Code**: Study `enhanced_notes_tool.py` for patterns
2. **Database Analysis**: Examine current `grocery_deals` data
3. **Tool Structure**: Create base `GroceryDealsTool` class
4. **Method Implementation**: Implement each of the four core methods
5. **Testing**: Comprehensive testing of all functionality
6. **Integration**: Register tool and test with LLM
7. **Documentation**: Complete user documentation

This onboarding provides comprehensive context for implementing a powerful grocery deals tool that will provide real value to users while driving business for IGA stores.
