"""
AI Evaluator Prompts

This module contains all the prompts used by the AIEventEvaluator for calendar event evaluation.
Enhanced with sophisticated prompt architecture and metadata integration.
"""

from typing import Dict, Any, Optional
from datetime import datetime


class AIEvaluatorPrompts:
    """Enhanced prompts for AI event evaluation functionality with sophisticated architecture."""

    @staticmethod
    def create_evaluation_prompt(ai_context: Dict[str, Any]) -> str:
        """
        Create enhanced evaluation prompt for AgentCore with sophisticated architecture.

        Args:
            ai_context: Rich context for the event

        Returns:
            Enhanced formatted prompt string
        """
        event = ai_context['event']
        timing = ai_context['timing']
        recurrence = ai_context['recurrence']
        processing = ai_context['processing']

        # Build enhanced prompt with professional structure
        base_prompt = AIEvaluatorPrompts._build_base_evaluation_prompt()
        event_details = AIEvaluatorPrompts._build_event_details_section(event)
        timing_analysis = AIEvaluatorPrompts._build_timing_analysis_section(timing)
        recurrence_analysis = AIEvaluatorPrompts._build_recurrence_analysis_section(recurrence)
        processing_history = AIEvaluatorPrompts._build_processing_history_section(processing)
        evaluation_guidance = AIEvaluatorPrompts._build_evaluation_guidance()
        response_format = AIEvaluatorPrompts._build_response_format_section()
        professional_guidelines = AIEvaluatorPrompts._build_professional_guidelines()

        enhanced_prompt = f"""
{base_prompt}

{event_details}

{timing_analysis}

{recurrence_analysis}

{processing_history}

{evaluation_guidance}

{response_format}

{professional_guidelines}
"""
        return enhanced_prompt.strip()

    @staticmethod
    def _build_base_evaluation_prompt() -> str:
        """Build the base evaluation prompt structure."""
        current_time = datetime.now()
        
        return f"""
🎯 AI CALENDAR EVENT EVALUATOR

📅 Current time: {current_time.strftime('%Y-%m-%d %H:%M')}

🎯 EVALUATION REQUEST: Determine if calendar event needs attention

📊 EVALUATION CONTEXT:
You are an intelligent calendar assistant with sophisticated decision-making capabilities.
Your task is to evaluate upcoming calendar events and determine which ones require attention,
processing, or action based on context, timing, and user needs.
"""

    @staticmethod
    def _build_event_details_section(event: Dict[str, Any]) -> str:
        """Build the event details section."""
        return f"""
📋 EVENT DETAILS:
• Title: {event['title']}
• Type: {event['type']}
• Priority: {event['priority']}
• Location: {event['location'] or 'Not specified'}
• Start Time: {event['start_time']}
• End Time: {event['end_time'] or 'Not specified'}
• Description: {event['description'] or 'No description'}
"""

    @staticmethod
    def _build_timing_analysis_section(timing: Dict[str, Any]) -> str:
        """Build the timing analysis section."""
        urgency_level = "HIGH" if timing['is_urgent'] else "MEDIUM" if timing['is_soon'] else "LOW"
        
        return f"""
⏰ TIMING ANALYSIS:
• Time until start: {timing['time_until_start_hours']:.1f} hours
• Urgency level: {urgency_level}
• Is urgent: {timing['is_urgent']}
• Is soon: {timing['is_soon']}
• Timing context: {'Immediate attention required' if timing['is_urgent'] else 'Plan ahead' if timing['is_soon'] else 'Future consideration'}
"""

    @staticmethod
    def _build_recurrence_analysis_section(recurrence: Dict[str, Any]) -> str:
        """Build the recurrence analysis section."""
        return f"""
🔄 RECURRENCE ANALYSIS:
• Recurrence hint: {recurrence['hint'] or 'None'}
• Is recurring: {recurrence['is_recurring']}
• Pattern: {recurrence['pattern']}
• Recurrence context: {'Regular event - check if this occurrence needs attention' if recurrence['is_recurring'] else 'One-time event - evaluate based on importance'}
"""

    @staticmethod
    def _build_processing_history_section(processing: Dict[str, Any]) -> str:
        """Build the processing history section."""
        return f"""
📚 PROCESSING HISTORY:
• Status: {processing['status']}
• Last processed: {processing['last_processed'] or 'Never'}
• Days since last processed: {processing['days_since_last_processed'] or 'N/A'}
• Processing context: {'Recently handled - may not need re-processing' if processing.get('days_since_last_processed', 0) < 1 else 'Not recently processed - may need attention'}
"""

    @staticmethod
    def _build_evaluation_guidance() -> str:
        """Build the evaluation guidance section."""
        return """
🎯 EVALUATION GUIDANCE:

🚨 **CRITICAL DECISION FACTORS**:
1. **Event Importance**: Is this event important enough to require attention?
2. **Timing Relevance**: Is the timing appropriate for processing this event?
3. **Recurrence Context**: For recurring events, does this specific occurrence need attention?
4. **Processing History**: Has this event been handled recently and doesn't need re-processing?
5. **User Value**: Would processing this event provide value to the user?

💡 **EVALUATION CRITERIA**:
• **High Priority**: Important meetings, deadlines, appointments, urgent tasks
• **Medium Priority**: Regular meetings, recurring events, planned activities
• **Low Priority**: Personal time, travel time, optional events, low-impact activities
• **Skip**: Already processed, irrelevant, or no action needed

🔄 **RECURRENCE LOGIC**:
• **First occurrence**: Process if important
• **Regular occurrence**: Process if significant changes or new context
• **Recent processing**: Skip if handled within last day
• **Pattern changes**: Process if schedule or context changed

⚖️ **DECISION WEIGHTING**:
• Urgency (40%): How time-sensitive is this event?
• Importance (30%): How critical is this event to the user?
• Context (20%): What additional context is available?
• History (10%): What does processing history tell us?
"""

    @staticmethod
    def _build_response_format_section() -> str:
        """Build the response format section."""
        return """
📋 RESPONSE FORMAT:
Respond with a JSON object containing:
{
    "should_process": true/false,
    "reason": "detailed explanation of decision with specific factors considered",
    "confidence": 0.0-1.0,
    "suggested_actions": ["specific action 1", "specific action 2", "specific action 3"],
    "event_type_analysis": "detailed analysis of event type and specific requirements",
    "priority_score": 0-10,
    "processing_urgency": "immediate|soon|future|skip"
}

🎯 **RESPONSE QUALITY REQUIREMENTS**:
• Provide specific, actionable reasons for your decision
• Include concrete suggested actions that would be helpful
• Give detailed analysis of the event type and requirements
• Assign appropriate priority and urgency scores
• Be confident in your decision-making
"""

    @staticmethod
    def _build_professional_guidelines() -> str:
        """Build professional guidelines section."""
        return """
🎯 **PROFESSIONAL EVALUATION GUIDELINES**:

🚨 **CRITICAL RULES**:
• Make intelligent, context-aware decisions
• Consider all available information and context
• Provide clear, specific reasoning for decisions
• Suggest actionable, helpful actions
• Maintain consistency in evaluation criteria

💡 **EVALUATION QUALITY**:
• Be thorough in your analysis
• Consider both immediate and long-term implications
• Balance urgency with importance
• Account for user preferences and patterns
• Provide detailed, specific reasoning

🔄 **DECISION CONSISTENCY**:
• Apply consistent criteria across similar events
• Consider the broader context and user needs
• Balance efficiency with thoroughness
• Learn from previous evaluation patterns
• Maintain high standards for decision quality
"""

    @staticmethod
    def create_recurrence_analysis_prompt(event_title: str, last_processed: Optional[datetime] = None) -> str:
        """
        Create enhanced prompt for recurrence pattern analysis.

        Args:
            event_title: Event title with recurrence hint
            last_processed: When this event was last processed

        Returns:
            Enhanced formatted prompt string
        """
        current_time = datetime.utcnow()
        time_since_last = None
        if last_processed:
            time_since_last = (current_time - last_processed).total_seconds() / 3600  # hours
        
        base_prompt = AIEvaluatorPrompts._build_recurrence_base_prompt()
        event_analysis = AIEvaluatorPrompts._build_recurrence_event_analysis(event_title, last_processed, time_since_last)
        pattern_guidance = AIEvaluatorPrompts._build_recurrence_pattern_guidance()
        decision_criteria = AIEvaluatorPrompts._build_recurrence_decision_criteria()
        response_format = AIEvaluatorPrompts._build_recurrence_response_format()

        enhanced_prompt = f"""
{base_prompt}

{event_analysis}

{pattern_guidance}

{decision_criteria}

{response_format}
"""
        return enhanced_prompt.strip()

    @staticmethod
    def _build_recurrence_base_prompt() -> str:
        """Build the base recurrence analysis prompt."""
        current_time = datetime.now()
        
        return f"""
🎯 AI RECURRENCE PATTERN ANALYZER

📅 Current time: {current_time.strftime('%Y-%m-%d %H:%M')}

🎯 ANALYSIS REQUEST: Analyze recurring event pattern and determine processing timing

📊 ANALYSIS CONTEXT:
You are an intelligent calendar assistant with sophisticated pattern recognition capabilities.
Your task is to analyze recurring event patterns and determine the optimal timing for processing
each occurrence based on the pattern, context, and processing history.
"""

    @staticmethod
    def _build_recurrence_event_analysis(event_title: str, last_processed: Optional[datetime], time_since_last: Optional[float]) -> str:
        """Build the event analysis section for recurrence."""
        return f"""
📋 EVENT ANALYSIS:
• Event Title: {event_title}
• Last Processed: {last_processed.isoformat() if last_processed else 'Never'}
• Time Since Last Processed: {f"{time_since_last:.1f} hours" if time_since_last else 'N/A'}
• Processing Context: {'Recently processed' if time_since_last and time_since_last < 24 else 'Not recently processed' if time_since_last else 'Never processed'}
"""

    @staticmethod
    def _build_recurrence_pattern_guidance() -> str:
        """Build the pattern guidance section."""
        return """
🔄 PATTERN ANALYSIS GUIDANCE:

🚨 **PATTERN DETECTION**:
• **Daily patterns**: "every day", "daily", "each day", "morning", "evening"
• **Weekly patterns**: "every monday", "weekdays", "weekends", "weekly"
• **Monthly patterns**: "monthly", "first of month", "last day", "monthly"
• **Custom intervals**: "every 2 hours", "every 3 days", "bi-weekly"
• **Time-based**: "at 9am", "during work hours", "after hours"

💡 **PROCESSING TIMING LOGIC**:
• **First occurrence**: Process if important and not recently handled
• **Regular occurrence**: Process if significant time has passed or context changed
• **Recent processing**: Skip if handled within appropriate interval
• **Pattern changes**: Process if schedule or frequency changed
• **Context changes**: Process if event details or importance changed

⚖️ **DECISION FACTORS**:
• **Pattern frequency**: How often does this event occur?
• **Processing interval**: How often should this be processed?
• **Last processing**: When was this last handled?
• **Context relevance**: Is the context still relevant?
• **User value**: Would processing now provide value?
"""

    @staticmethod
    def _build_recurrence_decision_criteria() -> str:
        """Build the decision criteria section."""
        return """
🎯 DECISION CRITERIA:

🚨 **SHOULD PROCESS NOW IF**:
• This is the first occurrence of a new pattern
• Significant time has passed since last processing
• The event context or importance has changed
• The pattern frequency suggests it's time to process
• User value would be provided by processing now

🚫 **SKIP PROCESSING IF**:
• Recently processed within appropriate interval
• Pattern suggests this occurrence doesn't need attention
• Context hasn't changed since last processing
• Processing would provide no additional value
• Event is low priority or optional

💡 **PATTERN-SPECIFIC RULES**:
• **Daily events**: Process if not handled in last 12-24 hours
• **Weekly events**: Process if not handled in last 3-7 days
• **Monthly events**: Process if not handled in last 2-4 weeks
• **Custom intervals**: Process based on specific interval logic
"""

    @staticmethod
    def _build_recurrence_response_format() -> str:
        """Build the response format section for recurrence."""
        return """
📋 RESPONSE FORMAT:
Respond with a JSON object containing:
{
    "pattern": "detailed description of recurrence pattern identified",
    "should_process_now": true/false,
    "reason": "detailed explanation of decision with specific factors",
    "next_occurrence": "when this should be processed next",
    "pattern_confidence": 0.0-1.0,
    "processing_interval": "recommended interval for future processing",
    "pattern_type": "daily|weekly|monthly|custom|unknown"
}

🎯 **RESPONSE QUALITY REQUIREMENTS**:
• Provide specific pattern identification with confidence level
• Give detailed reasoning for processing decision
• Suggest appropriate next processing time
• Recommend processing interval for future occurrences
• Be confident and specific in your analysis
"""

    @staticmethod
    def create_action_suggestion_prompt(ai_context: Dict[str, Any]) -> str:
        """
        Create prompt for suggesting actions for an event.

        Args:
            ai_context: Rich context for the event

        Returns:
            Formatted prompt string
        """
        event = ai_context['event']
        timing = ai_context['timing']

        prompt = f"""
Based on this event, suggest specific actions that would be helpful:

Event: {event['title']}
Type: {event['type']}
Priority: {event['priority']}
Time until start: {timing['time_until_start_hours']:.1f} hours
Is urgent: {timing['is_urgent']}

Suggest 3-5 specific, actionable items that would help with this event.
Focus on practical, useful actions.

Respond with JSON:
{{
    "suggested_actions": ["action1", "action2", "action3"]
}}
"""
        return prompt

    @staticmethod
    def get_evaluation_prompt_template() -> str:
        """
        Get the base template for event evaluation prompts.

        Returns:
            Base template string
        """
        return """
You are an intelligent calendar assistant evaluating whether an upcoming event needs attention.

EVENT DETAILS:
- Title: {title}
- Type: {type}
- Priority: {priority}
- Location: {location}
- Start Time: {start_time}
- End Time: {end_time}
- Description: {description}

TIMING:
- Time until start: {time_until_start_hours:.1f} hours
- Is urgent: {is_urgent}
- Is soon: {is_soon}

RECURRENCE:
- Recurrence hint: {recurrence_hint}
- Is recurring: {is_recurring}
- Pattern: {pattern}

PROCESSING HISTORY:
- Status: {status}
- Last processed: {last_processed}
- Days since last processed: {days_since_last_processed}

EVALUATION TASK:
Determine if this event needs attention and what actions should be taken.

Consider:
1. Is this a recurring event that needs to be processed for this occurrence?
2. Is the event urgent or important enough to require immediate attention?
3. Has this event been handled recently and doesn't need re-processing?
4. What specific actions would be helpful for this event type?

RESPONSE FORMAT:
Respond with a JSON object containing:
{{
    "should_process": true/false,
    "reason": "explanation of decision",
    "confidence": 0.0-1.0,
    "suggested_actions": ["action1", "action2", ...],
    "event_type_analysis": "analysis of event type and requirements"
}}

Focus on intelligent decision-making based on the event context and timing.
"""

    @staticmethod
    def get_recurrence_analysis_template() -> str:
        """
        Get the base template for recurrence analysis prompts.

        Returns:
            Base template string
        """
        return """
Analyze this recurring event pattern:

Event Title: {event_title}
Last Processed: {last_processed}
Current Time: {current_time}

Determine:
1. What is the recurrence pattern?
2. Should this event be processed for the current time?
3. Is this the right time to handle this recurring event?

Respond with JSON:
{{
    "pattern": "description of recurrence pattern",
    "should_process_now": true/false,
    "reason": "explanation",
    "next_occurrence": "when this should be processed next"
}}
"""

    @staticmethod
    def get_action_suggestion_template() -> str:
        """
        Get the base template for action suggestion prompts.

        Returns:
            Base template string
        """
        return """
Based on this event, suggest specific actions that would be helpful:

Event: {title}
Type: {type}
Priority: {priority}
Time until start: {time_until_start_hours:.1f} hours
Is urgent: {is_urgent}

Suggest 3-5 specific, actionable items that would help with this event.
Focus on practical, useful actions.

Respond with JSON:
{{
    "suggested_actions": ["action1", "action2", "action3"]
}}
"""
