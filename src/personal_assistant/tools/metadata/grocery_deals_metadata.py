"""
Grocery Deals Tool Metadata

This module provides enhanced metadata for the grocery deals tool to improve AI understanding.
"""

from .ai_enhancements import AIEnhancementManager, EnhancementPriority
from .tool_metadata import (
    ToolCategory,
    ToolComplexity,
    ToolExample,
    ToolMetadata,
    ToolUseCase,
)


def create_grocery_deals_tool_metadata() -> ToolMetadata:
    """Create comprehensive metadata for the grocery deals tool."""

    # Define use cases for the grocery deals tool
    use_cases = [
        ToolUseCase(
            name="Search for Produce Deals",
            description="Find fresh produce deals within a specific price range",
            example_request="Find all fruit deals under $3",
            example_parameters={
                "query": "fruit",
                "category": "Produce",
                "max_price": 3.00
            },
            expected_outcome="List of fruit deals under $3 with prices, categories, and validity",
            success_indicators=["deals_found", "price_filtered", "category_matched", "results_formatted"],
            failure_modes=["no_deals_found", "invalid_price_format", "category_mismatch", "database_error"],
            prerequisites=["valid_search_query", "price_range_specified", "category_exists"]
        ),
        ToolUseCase(
            name="Budget Meal Planning",
            description="Plan meals within a specified budget using current deals",
            example_request="Plan a weekly meal plan with a $50 budget",
            example_parameters={
                "budget": 50.00,
                "meal_type": "weekly",
                "categories": ["Produce", "Meat", "Dairy"]
            },
            expected_outcome="Weekly meal plan with selected deals within budget, cost breakdown",
            success_indicators=["budget_respected", "deals_selected", "cost_calculated", "plan_formatted"],
            failure_modes=["budget_exceeded", "no_suitable_deals", "calculation_error", "formatting_issue"],
            prerequisites=["realistic_budget", "valid_meal_type", "available_deals"]
        ),
        ToolUseCase(
            name="Deal Comparison Analysis",
            description="Compare deals across products or categories for best value",
            example_request="Compare all meat deals to find the best value",
            example_parameters={
                "analysis_type": "compare",
                "category": "Meat"
            },
            expected_outcome="Comparison analysis showing price ranges, averages, and top value deals",
            success_indicators=["analysis_completed", "comparison_clear", "value_identified", "results_ranked"],
            failure_modes=["insufficient_data", "analysis_failed", "comparison_unclear", "ranking_error"],
            prerequisites=["multiple_deals_available", "valid_category", "price_data_complete"]
        ),
        ToolUseCase(
            name="Savings Analysis",
            description="Calculate potential savings from deals with original prices",
            example_request="Show me the biggest savings available this week",
            example_parameters={
                "analysis_type": "savings"
            },
            expected_outcome="Savings analysis showing total potential savings and top saving deals",
            success_indicators=["savings_calculated", "total_computed", "top_deals_identified", "analysis_complete"],
            failure_modes=["no_original_prices", "calculation_error", "data_incomplete", "analysis_failed"],
            prerequisites=["deals_with_original_prices", "valid_price_data", "sufficient_deals"]
        ),
        ToolUseCase(
            name="Brand-Specific Search",
            description="Find deals for specific brands or products",
            example_request="Find all deals for President's Choice products",
            example_parameters={
                "query": "President's Choice",
                "brand": "President's Choice"
            },
            expected_outcome="List of President's Choice deals with prices and validity",
            success_indicators=["brand_deals_found", "brand_filtered", "results_accurate", "formatting_clear"],
            failure_modes=["brand_not_found", "no_deals_available", "filter_error", "display_issue"],
            prerequisites=["brand_exists", "brand_deals_available", "valid_search_term"]
        ),
        ToolUseCase(
            name="Expiring Deals Alert",
            description="Find deals that are expiring soon to take advantage of them",
            example_request="Show me deals expiring in the next 2 days",
            example_parameters={
                "expiring_soon": True
            },
            expected_outcome="List of deals expiring within 2 days with urgency indicators",
            success_indicators=["expiring_deals_found", "urgency_clear", "deadline_visible", "actionable_info"],
            failure_modes=["no_expiring_deals", "date_calculation_error", "urgency_unclear", "info_incomplete"],
            prerequisites=["deals_near_expiration", "valid_date_range", "urgency_threshold_set"]
        ),
        ToolUseCase(
            name="Category-Based Shopping",
            description="Find deals within specific food categories for targeted shopping",
            example_request="Find all dairy deals for my weekly shopping",
            example_parameters={
                "category": "Dairy"
            },
            expected_outcome="Comprehensive list of dairy deals with prices and product details",
            success_indicators=["category_deals_found", "category_accurate", "details_complete", "shopping_ready"],
            failure_modes=["category_empty", "deals_misclassified", "details_missing", "formatting_poor"],
            prerequisites=["category_exists", "deals_in_category", "valid_category_name"]
        ),
        ToolUseCase(
            name="Price Range Shopping",
            description="Find deals within a specific price range for budget shopping",
            example_request="Find deals between $2 and $5 for my budget shopping",
            example_parameters={
                "min_price": 2.00,
                "max_price": 5.00
            },
            expected_outcome="List of deals within the specified price range, sorted by value",
            success_indicators=["price_range_respected", "deals_within_range", "value_sorted", "budget_friendly"],
            failure_modes=["no_deals_in_range", "price_filter_failed", "range_invalid", "sorting_error"],
            prerequisites=["realistic_price_range", "deals_in_range", "valid_price_data"]
        )
    ]

    # Define examples for the tool
    examples = [
        ToolExample(
            description="Search for deals by product name",
            user_request="Find deals for chicken",
            parameters={"query": "chicken"},
            expected_result="List of chicken deals with prices, brands, and validity dates"
        ),
        ToolExample(
            description="Plan meals within a budget",
            user_request="Plan a $30 weekly meal plan",
            parameters={"budget": 30.00, "meal_type": "weekly"},
            expected_result="Weekly meal plan with selected deals, total cost, and remaining budget"
        ),
        ToolExample(
            description="Find deals in specific categories",
            user_request="Show me all produce deals",
            parameters={"category": "Produce"},
            expected_result="List of produce deals with prices and product details"
        ),
        ToolExample(
            description="Find deals within a price range",
            user_request="Find deals under $4",
            parameters={"max_price": 4.00},
            expected_result="List of deals under $4, sorted by price"
        ),
        ToolExample(
            description="Analyze deals for best value",
            user_request="Analyze all meat deals for best value",
            parameters={"analysis_type": "best_value", "category": "Meat"},
            expected_result="Best value analysis showing top deals in each meat category"
        )
    ]

    # Create AI enhancements
    ai_enhancements = create_grocery_deals_ai_enhancements()

    return ToolMetadata(
        tool_name="grocery_deals_tool",
        description="Search, analyze, and manage IGA grocery deals for intelligent shopping assistance",
        complexity=ToolComplexity.MODERATE,
        category=ToolCategory.INFORMATION,
        use_cases=use_cases,
        examples=examples,
        prerequisites=[
            "grocery_deals_database_available",
            "valid_deal_data",
            "user_authentication",
            "price_data_complete"
        ],
        parameter_guidance={
            "search_deals": "Search for deals by product name, category, price range, or brand",
            "plan_budget_meals": "Plan meals within a specified budget using current deals",
            "analyze_deals": "Analyze deals for best value, comparisons, or savings",
            "manage_deals": "Manage user preferences, alerts, and deal tracking"
        },
        ai_instructions="Use intelligent search with fuzzy matching, provide budget optimization suggestions, analyze deals for best value, and manage user preferences effectively",
        common_mistakes=[
            "Not validating price formats before filtering",
            "Ignoring deal expiration dates",
            "Not handling empty search results gracefully",
            "Failing to provide alternative suggestions when no deals found"
        ],
        best_practices=[
            "Always filter by deal validity (valid_to > now)",
            "Provide clear error messages for invalid inputs",
            "Sort results by price for better user experience",
            "Include deal expiration information in responses"
        ]
    )


def create_grocery_deals_ai_enhancements() -> AIEnhancementManager:
    """Create AI enhancements for the grocery deals tool."""
    
    enhancements = AIEnhancementManager()
    
    # Search enhancement
    from .ai_enhancements import AIEnhancement, EnhancementType
    search_enhancement = AIEnhancement(
        enhancement_id="search_intelligence",
        tool_name="grocery_deals_tool",
        enhancement_type=EnhancementType.PARAMETER_SUGGESTION,
        priority=EnhancementPriority.HIGH,
        title="Intelligent Search Enhancement",
        description="Intelligent search with fuzzy matching and category suggestions",
        ai_instructions="Use fuzzy matching for product names, suggest similar categories if exact match not found, understand price ranges and suggest alternatives, recognize brand names and variations"
    )
    enhancements.register_enhancement(search_enhancement)
    
    # Budget planning enhancement
    budget_enhancement = AIEnhancement(
        enhancement_id="budget_optimization",
        tool_name="grocery_deals_tool",
        enhancement_type=EnhancementType.WORKFLOW_SUGGESTION,
        priority=EnhancementPriority.HIGH,
        title="Budget Optimization Enhancement",
        description="Smart budget allocation and meal planning",
        ai_instructions="Balance budget across food categories, consider nutritional value in meal planning, account for seasonal availability, suggest bulk buying opportunities"
    )
    enhancements.register_enhancement(budget_enhancement)
    
    # Analysis enhancement
    analysis_enhancement = AIEnhancement(
        enhancement_id="deal_intelligence",
        tool_name="grocery_deals_tool",
        enhancement_type=EnhancementType.VALIDATION,
        priority=EnhancementPriority.MEDIUM,
        title="Deal Intelligence Enhancement",
        description="Advanced deal analysis and value assessment",
        ai_instructions="Calculate price per unit for better value assessment, identify price trends and patterns, maximize savings opportunities, provide smart product comparisons"
    )
    enhancements.register_enhancement(analysis_enhancement)
    
    # User experience enhancement
    ux_enhancement = AIEnhancement(
        enhancement_id="shopping_assistance",
        tool_name="grocery_deals_tool",
        enhancement_type=EnhancementType.CONVERSATIONAL_GUIDANCE,
        priority=EnhancementPriority.MEDIUM,
        title="Shopping Assistance Enhancement",
        description="Personalized shopping assistance and recommendations",
        ai_instructions="Learn user preferences and shopping patterns, suggest deals based on user history, generate optimized shopping lists, provide proactive deal notifications"
    )
    enhancements.register_enhancement(ux_enhancement)
    
    return enhancements


# Export the metadata creation function
grocery_deals_metadata = create_grocery_deals_tool_metadata()
grocery_deals_ai_enhancements = create_grocery_deals_ai_enhancements()
