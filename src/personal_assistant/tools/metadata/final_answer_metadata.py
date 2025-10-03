"""
Final Answer Tool Metadata

This module provides enhanced metadata for final answers to improve AI understanding
and response quality when providing final answers to users.
"""

from .ai_enhancements import AIEnhancement, AIEnhancementManager, EnhancementPriority, EnhancementType
from .tool_metadata import (
    ToolCategory,
    ToolComplexity,
    ToolExample,
    ToolMetadata,
    ToolUseCase,
)


def create_final_answer_metadata() -> ToolMetadata:
    """Create comprehensive metadata for final answers."""

    # Define use cases for final answers
    use_cases = [
        ToolUseCase(
            name="Information Response",
            description="Provide clear, comprehensive answers to user questions",
            example_request="What's the weather like today?",
            example_parameters={
                "query": "weather today",
                "location": "current location",
                "format": "detailed"
            },
            expected_outcome="Clear weather information with current conditions and forecast",
            success_indicators=["accurate_data", "clear_format", "actionable_info"],
            failure_modes=["outdated_info", "unclear_response", "missing_details"],
            prerequisites=[
                "accurate information",
                "clear communication",
                "user context understanding"
            ],
        ),
        ToolUseCase(
            name="Action Confirmation",
            description="Confirm completed actions and provide next steps",
            example_request="I've sent the email, what's next?",
            example_parameters={
                "action": "email_sent",
                "status": "completed",
                "next_steps": "follow_up"
            },
            expected_outcome="Confirmation of action completion with clear next steps",
            success_indicators=["action_confirmed", "next_steps_provided", "clear_guidance"],
            failure_modes=["unclear_confirmation", "missing_next_steps", "confusing_guidance"],
            prerequisites=["action verification", "workflow knowledge", "clear communication"],
        ),
        ToolUseCase(
            name="Problem Resolution",
            description="Provide solutions and troubleshooting guidance",
            example_request="My email isn't sending, what should I do?",
            example_parameters={
                "problem": "email_sending_failed",
                "context": "user_frustration",
                "urgency": "high"
            },
            expected_outcome="Clear troubleshooting steps and solution guidance",
            success_indicators=["problem_identified", "solution_provided", "steps_clear"],
            failure_modes=["unclear_problem", "no_solution", "confusing_steps"],
            prerequisites=["technical knowledge", "problem analysis", "solution expertise"],
        ),
        ToolUseCase(
            name="Educational Response",
            description="Explain concepts and provide learning guidance",
            example_request="How does email authentication work?",
            example_parameters={
                "topic": "email_authentication",
                "level": "intermediate",
                "format": "educational"
            },
            expected_outcome="Clear explanation with examples and practical applications",
            success_indicators=["concept_explained", "examples_provided", "practical_applications"],
            failure_modes=["overly_complex", "missing_examples", "unclear_explanations"],
            prerequisites=["subject expertise", "teaching ability", "clear communication"],
        ),
        ToolUseCase(
            name="Status Update",
            description="Provide current status and progress information",
            example_request="What's the status of my project?",
            example_parameters={
                "project": "current_project",
                "status": "in_progress",
                "details": "comprehensive"
            },
            expected_outcome="Clear project status with progress details and timeline",
            success_indicators=["status_clear", "progress_detailed", "timeline_provided"],
            failure_modes=["outdated_status", "unclear_progress", "missing_timeline"],
            prerequisites=["project knowledge", "status tracking", "timeline awareness"],
        ),
        ToolUseCase(
            name="SMS Response",
            description="Provide concise, well-formatted responses optimized for SMS display",
            example_request="Send me a quick update on the weather",
            example_parameters={
                "format": "sms_optimized",
                "length": "concise",
                "display": "mobile_friendly"
            },
            expected_outcome="Short, clear response that looks good on mobile SMS interface",
            success_indicators=["concise_format", "mobile_optimized", "clear_structure"],
            failure_modes=["too_long", "poor_formatting", "mobile_unfriendly"],
            prerequisites=["SMS formatting knowledge", "mobile display awareness", "concise communication"],
        ),
    ]

    # Define examples for final answers
    examples = [
        ToolExample(
            description="Providing current weather conditions",
            user_request="What's the weather like today?",
            parameters={"query": "weather today", "format": "detailed"},
            expected_result="Today's weather is partly cloudy with a high of 72°F and a low of 58°F. There's a 20% chance of rain this afternoon. Perfect weather for outdoor activities!",
            notes="Direct response with complete information and encouraging tone"
        ),
        ToolExample(
            description="Confirming email sending completion",
            user_request="I've sent the email to John about the meeting",
            parameters={"action": "email_sent", "status": "completed"},
            expected_result="Great! Your email to John about the meeting has been sent successfully. You should receive a delivery confirmation shortly. Consider following up in 24-48 hours if you don't hear back.",
            notes="Confirmation with next steps and helpful suggestion"
        ),
        ToolExample(
            description="Explaining technical concepts clearly",
            user_request="How does email authentication work?",
            parameters={"topic": "email_authentication", "level": "intermediate"},
            expected_result="Email authentication uses protocols like SPF, DKIM, and DMARC to verify that emails are legitimate. SPF checks if the sending server is authorized, DKIM adds a digital signature, and DMARC combines both to prevent spoofing. This helps protect against phishing and spam.",
            notes="Clear explanation with technical accuracy and practical context"
        ),
        ToolExample(
            description="Providing troubleshooting guidance",
            user_request="My email isn't sending, what should I do?",
            parameters={"problem": "email_sending_failed", "urgency": "high"},
            expected_result="Let's troubleshoot this step by step. First, check your internet connection. Then verify the recipient's email address is correct. If it's still not working, try sending a test email to yourself. If that works, the issue might be with the recipient's server. Would you like me to help you check these steps?",
            notes="Step-by-step troubleshooting with offers of help"
        ),
        ToolExample(
            description="Concise weather information optimized for SMS",
            user_request="What's the weather like today?",
            parameters={"format": "sms_optimized", "length": "concise"},
            expected_result="☀️ Today: 72°F, partly cloudy\n🌧️ 20% chance of rain\nPerfect for outdoor activities!",
            notes="SMS format with emojis, line breaks, and essential info only"
        ),
        ToolExample(
            description="Brief status update for SMS",
            user_request="How's my project going?",
            parameters={"format": "sms_optimized", "type": "status_update"},
            expected_result="📊 Project Status:\n✅ Phase 1: Complete\n🔄 Phase 2: 75% done\n📅 Due: Next Friday\nAll on track! 🎯",
            notes="SMS format with bullet points, emojis, and encouraging tone"
        ),
    ]

    # Create AI enhancements for final answers
    enhancement_manager = AIEnhancementManager()
    
    # Quality validation enhancement
    quality_validation = AIEnhancement(
        enhancement_id="final_answer_quality_validation",
        tool_name="final_answer",
        enhancement_type=EnhancementType.VALIDATION,
        priority=EnhancementPriority.CRITICAL,
        title="Final Answer Quality Validation",
        description="Ensure final answers meet quality standards",
        ai_instructions="Always start with a clear, direct statement addressing the user's request. Provide comprehensive information without process language. Use natural, conversational language - like talking to a knowledgeable friend. Include actionable insights or clear conclusions. Avoid technical jargon unless necessary. Ensure the response is complete and addresses all aspects of the question",
        examples=[
            {"good": "Today's weather is sunny with a high of 75°F...", "bad": "I'll check the weather for you... (process language)"}
        ],
        trigger_conditions=[
            "User asks a question requiring a final answer",
            "No tools are needed for the response"
        ],
        success_criteria=[
            "Direct response to user question",
            "Clear and conversational tone", 
            "Complete information provided",
            "Actionable insights included"
        ],
        failure_handling=[
            "If response is unclear, ask for clarification",
            "If information is incomplete, provide what's available and note limitations",
            "If tone is too formal, adjust to be more conversational"
        ]
    )
    enhancement_manager.register_enhancement(quality_validation)

    # Style enhancement
    style_enhancement = AIEnhancement(
        enhancement_id="final_answer_style_enhancement",
        tool_name="final_answer",
        enhancement_type=EnhancementType.CONVERSATIONAL_GUIDANCE,
        priority=EnhancementPriority.HIGH,
        title="Final Answer Style Enhancement",
        description="Apply conversational and helpful tone to final answers",
        ai_instructions="Use warm, friendly language that makes the user feel supported. Be encouraging and positive when appropriate. Use 'you' and 'your' to make responses personal. Include helpful context and additional insights. End with encouraging or actionable statements when relevant",
        examples=[
            {"good": "You're all set! Your email has been sent successfully.", "bad": "Email sent. (too brief and impersonal)"}
        ],
        trigger_conditions=[
            "Providing final answer to user",
            "User needs encouragement or support"
        ],
        success_criteria=[
            "Warm and friendly tone",
            "Personal and encouraging language",
            "Helpful additional context",
            "Positive and supportive ending"
        ],
        failure_handling=[
            "If tone is too cold, add warmth and encouragement",
            "If response lacks personal touch, use 'you' and 'your'",
            "If ending is abrupt, add helpful next steps or encouragement"
        ]
    )
    enhancement_manager.register_enhancement(style_enhancement)

    # User experience optimization
    ux_optimization = AIEnhancement(
        enhancement_id="final_answer_ux_optimization",
        tool_name="final_answer",
        enhancement_type=EnhancementType.CONVERSATIONAL_GUIDANCE,
        priority=EnhancementPriority.HIGH,
        title="Final Answer User Experience Optimization",
        description="Optimize final answers for maximum user satisfaction",
        ai_instructions="Anticipate follow-up questions and address them proactively. Provide relevant additional information that might be helpful. Use clear formatting and structure for easy reading. Include practical tips or suggestions when relevant. Make the response actionable and useful",
        examples=[
            {"good": "Your email is sent! You should receive a delivery confirmation shortly. Pro tip: Consider setting up email tracking for important messages.", "bad": "Email sent. (no additional value)"}
        ],
        trigger_conditions=[
            "Providing final answer to user",
            "User might need additional guidance"
        ],
        success_criteria=[
            "Proactive information provided",
            "Clear formatting and structure",
            "Practical tips included",
            "Response is actionable and useful"
        ],
        failure_handling=[
            "If missing proactive information, add helpful context",
            "If formatting is poor, restructure for clarity",
            "If no practical tips, add relevant suggestions",
            "If not actionable, provide next steps"
        ]
    )
    enhancement_manager.register_enhancement(ux_optimization)

    # SMS formatting optimization
    sms_formatting = AIEnhancement(
        enhancement_id="final_answer_sms_formatting",
        tool_name="final_answer",
        enhancement_type=EnhancementType.CONVERSATIONAL_GUIDANCE,
        priority=EnhancementPriority.HIGH,
        title="SMS Formatting Optimization",
        description="Format final answers for optimal SMS display and mobile readability",
        ai_instructions="Keep responses concise - aim for 1-3 lines maximum. Use emojis strategically to convey meaning and break up text. Use bullet points (•) or checkmarks (✅) for lists. Break long information into short, scannable lines. Use line breaks (\\n) to separate key information. Avoid long paragraphs - use single-line statements. Include only essential information - skip unnecessary details. Use symbols and emojis to make information more visual and engaging. NEVER use markdown formatting (* **text**, # headers, etc.) - SMS only supports plain text.",
        examples=[
            {"good": "☀️ Today: 72°F, partly cloudy\\n🌧️ 20% chance of rain\\nPerfect for outdoor activities!", "bad": "The weather today is partly cloudy with a high temperature of 72 degrees Fahrenheit and a low of 58 degrees. There is a 20% chance of rain this afternoon, which makes it perfect weather for outdoor activities. (too long, no formatting)"}
        ],
        trigger_conditions=[
            "SMS context detected",
            "Mobile display optimization needed"
        ],
        success_criteria=[
            "Concise and scannable format",
            "Strategic emoji usage",
            "Clear line breaks and structure",
            "Mobile-optimized display",
            "Essential information only"
        ],
        failure_handling=[
            "If too long, shorten to essential information only",
            "If no visual formatting, add emojis and symbols",
            "If dense format, add line breaks and structure",
            "If missing key info, prioritize most important details",
            "If desktop-style, optimize for mobile reading"
        ]
    )
    enhancement_manager.register_enhancement(sms_formatting)

    # Create the final answer metadata
    metadata = ToolMetadata(
        tool_name="final_answer",
        tool_version="1.0.0",
        description="Provide high-quality final answers to users with enhanced response quality and user experience",
        category=ToolCategory.INFORMATION,
        complexity=ToolComplexity.MODERATE,
        use_cases=use_cases,
        examples=examples,
        ai_instructions="""Start with a clear, direct statement addressing the user's request. Provide comprehensive information without process language. Always conclude with actionable insights or clear conclusions. Use natural, conversational language - like talking to a knowledgeable friend. Include helpful context and additional information when relevant. Be encouraging and positive when appropriate. Anticipate follow-up questions and address them proactively. NEVER say "Based on the search results..." in final answers. NEVER say "I will provide a summary..." in final answers. ALWAYS end with genuine, helpful answers that feel personal and caring. FINAL ANSWER: Must be clean and direct from tool results. FINAL ANSWER: Clean, direct, professional response. Give final answers as if you're a knowledgeable friend. For SMS responses: Keep concise (1-3 lines), use emojis strategically, use line breaks for readability. For SMS responses: Use bullet points and symbols to make information scannable and mobile-friendly. For SMS responses: NEVER use markdown formatting (* **text**, # headers, etc.) - use plain text only.""",
        common_mistakes=[
            "Process language used",
            "Incomplete information", 
            "Unclear or confusing response",
            "Missing actionable insights",
            "Cold or impersonal tone",
            "Poor user experience",
            "Too long for SMS display",
            "No visual formatting",
            "Dense paragraph format",
            "Missing key information",
            "Desktop-style formatting"
        ],
        best_practices=[
            "Direct response to user question",
            "Clear and conversational tone", 
            "Complete information provided",
            "Actionable insights included",
            "Helpful additional context",
            "Positive user experience",
            "Concise and scannable format",
            "Strategic emoji usage",
            "Clear line breaks and structure",
            "Mobile-optimized display",
            "Essential information only"
        ],
        prerequisites=[
            "Accurate information available",
            "Clear understanding of user request",
            "Contextual awareness",
            "Quality response standards",
            "SMS formatting knowledge",
            "Mobile display awareness",
            "Concise communication"
        ]
    )

    return metadata


def get_final_answer_metadata() -> ToolMetadata:
    """Get the final answer metadata."""
    return create_final_answer_metadata()


# Export the metadata for easy access
FINAL_ANSWER_METADATA = create_final_answer_metadata()
