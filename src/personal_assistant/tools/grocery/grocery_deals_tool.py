"""
Grocery Deals Tool

This tool provides comprehensive functionality for searching, analyzing, and managing
IGA grocery deals data from the automated scraping system.
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

from personal_assistant.database.session import AsyncSessionLocal
from personal_assistant.database.models.grocery_deals import GroceryDeal
from ..base import Tool


class GroceryDealsTool:
    """
    Tool for querying IGA grocery deals and providing shopping assistance.
    
    This tool provides four core methods:
    1. search_deals() - Search and filter grocery deals
    2. plan_budget_meals() - Budget-based meal planning
    3. analyze_deals() - Deal analysis and comparisons
    4. manage_deals() - User preferences and deal management
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Create tool instances
        self._create_tools()
    
    def _create_tools(self):
        """Create individual tool instances"""
        
        # Search deals tool
        self.search_deals_tool = Tool(
            name="search_deals",
            func=self.search_deals,
            description="Search and filter IGA grocery deals by product name, category, price range, brand, or expiration",
            parameters={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search term for product name (optional)"
                    },
                    "category": {
                        "type": "string",
                        "description": "Filter by category like Produce, Meat, Dairy (optional)"
                    },
                    "max_price": {
                        "type": "number",
                        "description": "Maximum price filter (optional)"
                    },
                    "min_price": {
                        "type": "number",
                        "description": "Minimum price filter (optional)"
                    },
                    "brand": {
                        "type": "string",
                        "description": "Filter by brand name (optional)"
                    },
                    "expiring_soon": {
                        "type": "boolean",
                        "description": "Show deals expiring within 2 days (optional)"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results (default: 20)"
                    }
                }
            }
        )
        
        # Budget meal planning tool
        self.plan_budget_meals_tool = Tool(
            name="plan_budget_meals",
            func=self.plan_budget_meals,
            description="Plan meals within a specified budget using current IGA deals",
            parameters={
                "type": "object",
                "properties": {
                    "budget": {
                        "type": "number",
                        "description": "Total budget for meal planning (required)"
                    },
                    "meal_type": {
                        "type": "string",
                        "description": "Type of meal planning: daily, weekly, monthly (default: weekly)"
                    },
                    "dietary_restrictions": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of dietary restrictions (optional)"
                    },
                    "categories": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Preferred food categories (optional)"
                    }
                },
                "required": ["budget"]
            }
        )
        
        # Deal analysis tool
        self.analyze_deals_tool = Tool(
            name="analyze_deals",
            func=self.analyze_deals,
            description="Analyze IGA deals for best value, comparisons, or savings calculations",
            parameters={
                "type": "object",
                "properties": {
                    "deal_ids": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "Specific deal IDs to analyze (optional)"
                    },
                    "analysis_type": {
                        "type": "string",
                        "enum": ["compare", "best_value", "savings"],
                        "description": "Type of analysis: compare, best_value, savings (default: compare)"
                    },
                    "category": {
                        "type": "string",
                        "description": "Filter by category for analysis (optional)"
                    }
                }
            }
        )
        
        # Deal management tool
        self.manage_deals_tool = Tool(
            name="manage_deals",
            func=self.manage_deals,
            description="Manage user preferences, alerts, and deal tracking for IGA deals",
            parameters={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["set_preference", "get_preferences", "set_alert"],
                        "description": "Action to perform (required)"
                    },
                    "user_id": {
                        "type": "integer",
                        "description": "User ID for preferences (required)"
                    },
                    "deal_id": {
                        "type": "integer",
                        "description": "Deal ID for specific actions (optional)"
                    },
                    "preference_type": {
                        "type": "string",
                        "description": "Type of preference to set (optional)"
                    }
                },
                "required": ["action", "user_id"]
            }
        )
    
    def __iter__(self):
        """Make the tool iterable to return individual tool instances"""
        return iter([
            self.search_deals_tool,
            self.plan_budget_meals_tool,
            self.analyze_deals_tool,
            self.manage_deals_tool
        ])
        
    async def search_deals(
        self, 
        query: str = "deals", 
        category: Optional[str] = None,
        max_price: Optional[float] = None,
        min_price: Optional[float] = None,
        brand: Optional[str] = None,
        expiring_soon: bool = False,
        limit: int = 20,
        user_id: Optional[int] = None
    ) -> str:
        """
        Search grocery deals with various filters.
        
        Args:
            query: Search term for product name (default: "deals" for general search)
            category: Filter by category (Produce, Meat, Dairy, etc.)
            max_price: Maximum price filter
            min_price: Minimum price filter
            brand: Filter by brand name
            expiring_soon: Show only deals expiring within 2 days
            limit: Maximum number of results
            
        Returns:
            Formatted string with search results
        """
        try:
            self.logger.info(f"Searching deals with query: '{query}', category: {category}, max_price: {max_price}")
            
            async with AsyncSessionLocal() as db:
                # Build query
                from sqlalchemy import select, and_, or_, cast, Float, func, case
                from datetime import timedelta
                
                conditions = [GroceryDeal.valid_to > datetime.utcnow()]
                
                # Apply filters
                if query and query != "deals":  # Don't filter by name if query is default "deals"
                    conditions.append(GroceryDeal.name.ilike(f"%{query}%"))
                
                if category:
                    conditions.append(GroceryDeal.categories.contains([category]))
                
                if brand:
                    conditions.append(GroceryDeal.brand.ilike(f"%{brand}%"))
                
                if min_price is not None:
                    conditions.append(cast(GroceryDeal.price_text, Float) >= min_price)
                
                if max_price is not None:
                    conditions.append(cast(GroceryDeal.price_text, Float) <= max_price)
                
                if expiring_soon:
                    # Deals expiring within 2 days
                    cutoff = datetime.utcnow() + timedelta(days=2)
                    conditions.append(GroceryDeal.valid_to <= cutoff)
                
                # Build final query - handle empty price_text values
                db_query = select(GroceryDeal).where(and_(*conditions)).order_by(
                    case(
                        (GroceryDeal.price_text == "", 999999.0),  # Put empty prices last
                        else_=cast(GroceryDeal.price_text, Float)
                    )
                ).limit(limit)
                
                # Execute query
                result = await db.execute(db_query)
                deals = result.scalars().all()
                
                if not deals:
                    return "🔍 No deals found matching your criteria. Try adjusting your search parameters."
                
                # Format results
                result = f"🛒 Found {len(deals)} deals matching your search:\n\n"
                
                for deal in deals:
                    result += f"**{deal.name}**\n"
                    result += f"💰 Price: ${deal.price_text}"
                    if deal.post_price_text:
                        result += f" {deal.post_price_text}"
                    result += "\n"
                    
                    if deal.brand:
                        result += f"🏷️ Brand: {deal.brand}\n"
                    
                    if deal.categories:
                        result += f"📂 Categories: {', '.join(deal.categories)}\n"
                    
                    result += f"⏰ Valid until: {deal.valid_to.strftime('%Y-%m-%d')}\n"
                    
                    if deal.description:
                        result += f"📝 {deal.description}\n"
                    
                    result += "\n---\n\n"
                
                return result
                
        except Exception as e:
            self.logger.error(f"Error searching deals: {e}")
            return f"❌ Error searching deals: {str(e)}"
    
    async def plan_budget_meals(
        self, 
        budget: float, 
        meal_type: str = "weekly",
        dietary_restrictions: Optional[List[str]] = None,
        categories: Optional[List[str]] = None,
        user_id: Optional[int] = None
    ) -> str:
        """
        Plan meals within budget using current deals.
        
        Args:
            budget: Total budget for meal planning
            meal_type: Type of meal planning (daily, weekly, monthly)
            dietary_restrictions: List of dietary restrictions
            categories: Preferred food categories
            
        Returns:
            Formatted meal plan with deals
        """
        try:
            self.logger.info(f"Planning {meal_type} meals with budget: ${budget}")
            
            async with AsyncSessionLocal() as db:
                # Get deals within budget
                from sqlalchemy import select, and_, cast, Float, or_
                
                conditions = [
                    GroceryDeal.valid_to > datetime.utcnow(),
                    GroceryDeal.price_text != "",  # Exclude empty prices
                    cast(GroceryDeal.price_text, Float) <= budget
                ]
                
                # Apply category filter if specified
                if categories:
                    category_conditions = [GroceryDeal.categories.contains([cat]) for cat in categories]
                    conditions.append(or_(*category_conditions))
                
                # Build query
                from sqlalchemy import case
                db_query = select(GroceryDeal).where(and_(*conditions)).order_by(
                    case(
                        (GroceryDeal.price_text == "", 999999.0),  # Put empty prices last
                        else_=cast(GroceryDeal.price_text, Float)
                    )
                )
                
                # Execute query
                result = await db.execute(db_query)
                deals = result.scalars().all()
                
                if not deals:
                    return f"💰 No deals found within your ${budget} budget. Try increasing your budget or adjusting categories."
                
                # Simple budget allocation algorithm
                total_spent = 0
                selected_deals = []
                
                for deal in deals:
                    try:
                        price = float(deal.price_text) if deal.price_text else 0
                        if total_spent + price <= budget:
                            selected_deals.append(deal)
                            total_spent += price
                        else:
                            break
                    except (ValueError, TypeError):
                        # Skip deals with invalid price data
                        continue
                
                # Format meal plan
                result = f"🍽️ **{meal_type.title()} Meal Plan** (Budget: ${budget})\n\n"
                result += f"💰 **Total Cost: ${total_spent:.2f}** (${budget - total_spent:.2f} remaining)\n\n"
                
                if selected_deals:
                    result += "🛒 **Selected Deals:**\n\n"
                    
                    # Group by category
                    category_groups = {}
                    for deal in selected_deals:
                        if deal.categories:
                            for category in deal.categories:
                                if category not in category_groups:
                                    category_groups[category] = []
                                category_groups[category].append(deal)
                                break
                        else:
                            if "Other" not in category_groups:
                                category_groups["Other"] = []
                            category_groups["Other"].append(deal)
                    
                    for category, deals_in_category in category_groups.items():
                        result += f"📂 **{category}**\n"
                        for deal in deals_in_category:
                            result += f"  • {deal.name} - ${deal.price_text}"
                            if deal.post_price_text:
                                result += f" {deal.post_price_text}"
                            result += "\n"
                        result += "\n"
                
                return result
                
        except Exception as e:
            self.logger.error(f"Error planning budget meals: {e}")
            return f"❌ Error planning meals: {str(e)}"
    
    async def analyze_deals(
        self, 
        deal_ids: Optional[List[int]] = None,
        analysis_type: str = "compare",
        category: Optional[str] = None,
        user_id: Optional[int] = None
    ) -> str:
        """
        Analyze deals for best value and comparisons.
        
        Args:
            deal_ids: Specific deal IDs to analyze (if None, analyzes all deals)
            analysis_type: Type of analysis (compare, best_value, savings)
            category: Filter by category for analysis
            
        Returns:
            Formatted analysis results
        """
        try:
            self.logger.info(f"Analyzing deals - type: {analysis_type}, category: {category}")
            
            async with AsyncSessionLocal() as db:
                # Build query
                from sqlalchemy import select, and_
                
                conditions = [GroceryDeal.valid_to > datetime.utcnow()]
                
                if deal_ids:
                    conditions.append(GroceryDeal.id.in_(deal_ids))
                
                if category:
                    conditions.append(GroceryDeal.categories.contains([category]))
                
                # Build query
                db_query = select(GroceryDeal).where(and_(*conditions))
                
                # Execute query
                result = await db.execute(db_query)
                deals = result.scalars().all()
                
                if not deals:
                    return "📊 No deals found for analysis."
                
                if analysis_type == "compare":
                    return self._format_deal_comparison(deals)
                elif analysis_type == "best_value":
                    return self._format_best_value_analysis(deals)
                elif analysis_type == "savings":
                    return self._format_savings_analysis(deals)
                else:
                    return "❌ Invalid analysis type. Use: compare, best_value, or savings"
                
        except Exception as e:
            self.logger.error(f"Error analyzing deals: {e}")
            return f"❌ Error analyzing deals: {str(e)}"
    
    async def manage_deals(
        self, 
        action: str, 
        user_id: int,
        deal_id: Optional[int] = None,
        preference_type: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Manage user preferences, alerts, and deal tracking.
        
        Args:
            action: Action to perform (set_preference, get_preferences, set_alert)
            user_id: User ID for preferences
            deal_id: Deal ID for specific actions
            preference_type: Type of preference to set
            **kwargs: Additional parameters based on action
            
        Returns:
            Formatted response for the action
        """
        try:
            self.logger.info(f"Managing deals - action: {action}, user_id: {user_id}")
            
            if action == "set_preference":
                return f"✅ Preference set for user {user_id}: {preference_type}"
            elif action == "get_preferences":
                return f"📋 User {user_id} preferences: [Preferences would be retrieved from database]"
            elif action == "set_alert":
                return f"🔔 Alert set for user {user_id} on deal {deal_id}"
            else:
                return f"❌ Unknown action: {action}. Available actions: set_preference, get_preferences, set_alert"
                
        except Exception as e:
            self.logger.error(f"Error managing deals: {e}")
            return f"❌ Error managing deals: {str(e)}"
    
    def _format_deal_comparison(self, deals: List[GroceryDeal]) -> str:
        """Format deal comparison analysis."""
        result = "📊 **Deal Comparison Analysis**\n\n"
        
        # Sort by price, filtering out invalid prices
        valid_deals = [deal for deal in deals if deal.price_text and deal.price_text.strip()]
        sorted_deals = sorted(valid_deals, key=lambda x: float(x.price_text))
        
        if sorted_deals:
            result += f"💰 **Price Range:** ${sorted_deals[0].price_text} - ${sorted_deals[-1].price_text}\n"
            valid_prices = [float(d.price_text) for d in valid_deals]
            result += f"📈 **Average Price:** ${sum(valid_prices) / len(valid_prices):.2f}\n\n"
        else:
            result += "❌ No valid price data found for comparison.\n\n"
        
        result += "🏆 **Top 5 Best Value Deals:**\n"
        for i, deal in enumerate(sorted_deals[:5], 1):
            result += f"{i}. {deal.name} - ${deal.price_text}\n"
        
        return result
    
    def _format_best_value_analysis(self, deals: List[GroceryDeal]) -> str:
        """Format best value analysis."""
        result = "🎯 **Best Value Analysis**\n\n"
        
        # Group by category and find best value in each
        category_best = {}
        for deal in deals:
            if deal.categories and deal.price_text and deal.price_text.strip():
                try:
                    deal_price = float(deal.price_text)
                    for category in deal.categories:
                        if category not in category_best:
                            category_best[category] = deal
                        elif deal_price < float(category_best[category].price_text):
                            category_best[category] = deal
                except (ValueError, TypeError):
                    continue
        
        for category, deal in category_best.items():
            result += f"📂 **{category}:** {deal.name} - ${deal.price_text}\n"
        
        return result
    
    def _format_savings_analysis(self, deals: List[GroceryDeal]) -> str:
        """Format savings analysis."""
        result = "💸 **Savings Analysis**\n\n"
        
        # Calculate potential savings
        deals_with_savings = []
        for d in deals:
            if d.original_price and d.price_text and d.price_text.strip():
                try:
                    current_price = float(d.price_text)
                    if d.original_price > current_price:
                        deals_with_savings.append(d)
                except (ValueError, TypeError):
                    continue
        
        if deals_with_savings:
            total_savings = sum(d.original_price - float(d.price_text) for d in deals_with_savings)
            result += f"💰 **Total Potential Savings:** ${total_savings:.2f}\n\n"
            
            result += "🎉 **Top Savings Deals:**\n"
            sorted_savings = sorted(deals_with_savings, key=lambda x: x.original_price - float(x.price_text), reverse=True)
            
            for deal in sorted_savings[:5]:
                savings = deal.original_price - float(deal.price_text)
                result += f"• {deal.name}: Save ${savings:.2f} (${deal.original_price:.2f} → ${deal.price_text})\n"
        else:
            result += "ℹ️ No deals with original prices found for savings calculation.\n"
        
        return result
