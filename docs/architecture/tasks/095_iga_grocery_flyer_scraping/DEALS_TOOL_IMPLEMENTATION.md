# IGA Grocery Deals Tool - Implementation Plan

## 🎯 MVP Tool Design (Minimum Viable Product)

### **Core Tool: `grocery_deals_tool`**

```python
class GroceryDealsTool:
    """
    Tool for querying IGA grocery deals and providing shopping assistance.
    """

    def search_deals(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        max_price: Optional[float] = None,
        min_price: Optional[float] = None,
        budget: Optional[float] = None,
        limit: int = 20
    ) -> str:
        """
        Search for grocery deals based on various criteria.

        Args:
            query: Search term (product name, brand, etc.)
            category: Product category (Produce, Meat, Dairy, etc.)
            max_price: Maximum price filter
            min_price: Minimum price filter
            budget: Total budget for multiple items
            limit: Maximum number of results to return
        """

    def get_deal_details(self, deal_id: int) -> str:
        """Get detailed information about a specific deal."""

    def find_budget_deals(self, budget: float, categories: List[str] = None) -> str:
        """Find the best combination of deals within a budget."""

    def get_category_deals(self, category: str, sort_by: str = "price") -> str:
        """Get all deals in a specific category."""

    def get_expiring_deals(self, days: int = 3) -> str:
        """Get deals expiring within specified days."""
```

## 🛠️ Implementation Phases

### **Phase 1: Core Search & Filter (Week 1-2)**

#### **Database Queries Needed:**

```sql
-- Basic deal search
SELECT * FROM grocery_deals
WHERE name ILIKE '%query%'
AND price_text::numeric BETWEEN min_price AND max_price
AND valid_to > NOW()
ORDER BY price_text::numeric ASC
LIMIT limit;

-- Category filtering
SELECT * FROM grocery_deals
WHERE categories @> '["category_name"]'
AND valid_to > NOW()
ORDER BY price_text::numeric ASC;

-- Budget optimization
SELECT * FROM grocery_deals
WHERE price_text::numeric <= budget
AND valid_to > NOW()
ORDER BY price_text::numeric ASC;
```

#### **Features:**

- [ ] **Basic Search**: Search deals by product name
- [ ] **Category Filter**: Filter by grocery categories
- [ ] **Price Range**: Filter by min/max price
- [ ] **Budget Calculator**: Find deals within budget
- [ ] **Expiration Check**: Only show valid deals

### **Phase 2: Advanced Features (Week 3-4)**

#### **Enhanced Queries:**

```sql
-- Deal details with full information
SELECT
    id, name, sku, description, brand,
    price_text, post_price_text, original_price,
    categories, valid_from, valid_to,
    web_commission_url, scraped_at
FROM grocery_deals
WHERE id = deal_id;

-- Expiring deals
SELECT * FROM grocery_deals
WHERE valid_to BETWEEN NOW() AND NOW() + INTERVAL '3 days'
ORDER BY valid_to ASC;

-- Best value deals (price per unit if available)
SELECT *,
    CASE
        WHEN post_price_text LIKE '%/lb%' THEN price_text::numeric / 1
        WHEN post_price_text LIKE '%/kg%' THEN price_text::numeric / 1
        ELSE price_text::numeric
    END as unit_price
FROM grocery_deals
WHERE valid_to > NOW()
ORDER BY unit_price ASC;
```

#### **Features:**

- [ ] **Deal Details**: Full product information
- [ ] **Expiring Alerts**: Deals expiring soon
- [ ] **Best Value**: Sort by value/unit price
- [ ] **Brand Search**: Search by specific brands
- [ ] **Savings Calculator**: Compare deal vs regular price

### **Phase 3: Smart Features (Week 5-6)**

#### **AI-Powered Queries:**

```sql
-- Meal planning suggestions
SELECT * FROM grocery_deals
WHERE categories && ARRAY['Produce', 'Meat', 'Dairy']
AND price_text::numeric <= budget_per_category
ORDER BY categories, price_text::numeric;

-- Similar products
SELECT * FROM grocery_deals
WHERE categories @> (SELECT categories FROM grocery_deals WHERE id = product_id)
AND id != product_id
AND valid_to > NOW()
LIMIT 5;
```

#### **Features:**

- [ ] **Meal Planning**: Suggest deals for specific meals
- [ ] **Similar Products**: Find related deals
- [ ] **Shopping Lists**: Generate lists from deals
- [ ] **Price Trends**: Show if prices are good deals
- [ ] **Category Insights**: Analyze deals by category

## 🔧 Technical Implementation

### **Database Schema Extensions:**

```sql
-- Add indexes for better performance
CREATE INDEX IF NOT EXISTS idx_grocery_deals_name_search ON grocery_deals USING GIN(to_tsvector('english', name));
CREATE INDEX IF NOT EXISTS idx_grocery_deals_price ON grocery_deals(price_text::numeric);
CREATE INDEX IF NOT EXISTS idx_grocery_deals_validity ON grocery_deals(valid_from, valid_to);

-- Add computed columns for better queries
ALTER TABLE grocery_deals ADD COLUMN price_numeric NUMERIC GENERATED ALWAYS AS (price_text::numeric) STORED;
ALTER TABLE grocery_deals ADD COLUMN is_valid BOOLEAN GENERATED ALWAYS AS (valid_to > NOW()) STORED;
```

### **API Endpoints:**

```python
# FastAPI endpoints for the tool
@app.get("/api/v1/grocery-deals/search")
async def search_deals(
    query: Optional[str] = None,
    category: Optional[str] = None,
    max_price: Optional[float] = None,
    min_price: Optional[float] = None,
    budget: Optional[float] = None,
    limit: int = 20
):
    """Search grocery deals with filters."""

@app.get("/api/v1/grocery-deals/{deal_id}")
async def get_deal_details(deal_id: int):
    """Get detailed information about a specific deal."""

@app.get("/api/v1/grocery-deals/budget/{budget}")
async def find_budget_deals(budget: float, categories: List[str] = None):
    """Find best deals within budget."""
```

## 📊 Sample Tool Responses

### **Search Example:**

```
🔍 Found 15 deals matching "chicken":

🍗 MEAT DEALS:
• Fresh Chicken Breast - $4.99/lb (Regular: $6.99) - Save 29%
• Whole Chicken - $2.49/lb (Regular: $3.99) - Save 38%
• Chicken Thighs - $3.99/lb (Regular: $5.49) - Save 27%

Valid until: September 24, 2025
Total savings: $8.50
```

### **Budget Example:**

```
💰 BEST DEALS FOR $50 BUDGET:

🥬 PRODUCE ($15):
• Bananas - $0.99/lb
• Apples - $1.49/lb
• Spinach - $2.99

🥩 MEAT ($20):
• Chicken Breast - $4.99/lb
• Ground Beef - $5.99/lb

🥛 DAIRY ($10):
• Milk - $3.99
• Eggs - $2.99

🍞 PANTRY ($5):
• Bread - $1.99
• Rice - $2.99

Total: $49.90 (Under budget!)
```

### **Category Example:**

```
🥬 PRODUCE DEALS (12 items):

FRUITS:
• Bananas - $0.99/lb
• Apples - $1.49/lb
• Oranges - $1.99/lb

VEGETABLES:
• Spinach - $2.99
• Carrots - $1.49/lb
• Potatoes - $0.99/lb

Valid until: September 24, 2025
```

## 🎯 Success Metrics

### **User Engagement:**

- **Search Queries**: Number of searches per day
- **Deal Views**: How many deals users view
- **Budget Calculations**: Usage of budget features
- **Category Browsing**: Most popular categories

### **Business Impact:**

- **Deal Conversion**: Deals leading to store visits
- **User Savings**: Actual money saved
- **Store Traffic**: Increased IGA visits
- **Customer Satisfaction**: User feedback scores

### **Technical Performance:**

- **Search Speed**: < 500ms response time
- **Data Accuracy**: 99%+ accuracy
- **Uptime**: 99.9% availability
- **Error Rate**: < 1% error rate

## 🚀 Future Enhancements

### **Advanced Features:**

- [ ] **Price History**: Track price changes over time
- [ ] **Predictive Pricing**: Predict when items will go on sale
- [ ] **Personalization**: AI-powered recommendations
- [ ] **Social Features**: Share deals with friends
- [ ] **Mobile App**: Dedicated mobile application

### **Integration Features:**

- [ ] **Calendar Sync**: Add deal expiration to calendar
- [ ] **Banking Integration**: Track grocery spending
- [ ] **Delivery Integration**: Connect with delivery services
- [ ] **Loyalty Programs**: Integrate with Scene+ rewards

---

## 📋 Implementation Checklist

### **Week 1:**

- [ ] Set up database indexes
- [ ] Implement basic search functionality
- [ ] Create category filtering
- [ ] Add price range filtering
- [ ] Test with sample data

### **Week 2:**

- [ ] Implement budget calculator
- [ ] Add deal details endpoint
- [ ] Create expiration checking
- [ ] Add brand search
- [ ] Performance optimization

### **Week 3:**

- [ ] Implement meal planning features
- [ ] Add similar products functionality
- [ ] Create shopping list generation
- [ ] Add price comparison
- [ ] User testing

### **Week 4:**

- [ ] Implement advanced analytics
- [ ] Add trend analysis
- [ ] Create user insights
- [ ] Performance monitoring
- [ ] Documentation

This implementation plan provides a clear roadmap for building a powerful grocery deals tool that will provide real value to users while driving business for IGA stores.
