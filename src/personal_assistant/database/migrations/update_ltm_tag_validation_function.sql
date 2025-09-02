-- Migration: Update LTM Tag Validation Function
-- Description: Update the validate_ltm_tags function to match the current LTM_TAGS list
-- Date: 2024-12-02

-- Update the validate_ltm_tags function with the complete current tag list
CREATE OR REPLACE FUNCTION validate_ltm_tags(tags jsonb)
RETURNS boolean AS $$
DECLARE
    tag text;
    allowed_tags text[] := ARRAY[
        -- Communication & Information
        'email', 'meeting', 'conversation', 'document', 'note',
        
        -- Actions & Operations
        'create', 'delete', 'update', 'search', 'schedule', 'remind',
        
        -- Importance & Priority
        'important', 'urgent', 'critical', 'low_priority',
        
        -- Context & Categories
        'work', 'personal', 'health', 'finance', 'travel', 'shopping', 'entertainment', 'education',
        
        -- User Behavior & Preferences
        'preference', 'habit', 'pattern', 'routine', 'dislike', 'favorite',
        
        -- Tool & System Usage
        'tool_execution', 'user_request', 'system_response', 'error', 'success',
        
        -- Time & Frequency
        'daily', 'weekly', 'monthly', 'one_time', 'recurring',
        
        -- General
        'general', 'miscellaneous', 'other',
        
        -- Organization & Management
        'organization', 'management', 'productivity', 'automation', 'efficiency', 'optimization',
        
        -- Communication Styles
        'communication', 'concise', 'detailed', 'professional', 'casual', 'formal', 'informal',
        
        -- Frequency & Patterns
        'frequent', 'occasional', 'rare', 'consistent', 'variable',
        
        -- Work Styles
        'technical', 'creative', 'analytical', 'strategic', 'tactical', 'operational',
        
        -- Quality & Effectiveness
        'effective', 'ineffective', 'streamlined', 'simplified', 'complex', 'straightforward',
        
        -- Project Management
        'project', 'task', 'deadline', 'milestone',
        
        -- Health & Wellness
        'exercise', 'diet', 'medication', 'wellness',
        
        -- Social
        'friend', 'family', 'event', 'birthday',
        
        -- Shopping
        'wishlist', 'purchase', 'order', 'delivery',
        
        -- Learning
        'course', 'lesson', 'reading', 'research',
        
        -- Finance
        'budget', 'expense', 'income', 'investment',
        
        -- Travel
        'flight', 'hotel', 'reservation', 'itinerary',
        
        -- Reminders
        'follow_up', 'due', 'overdue'
    ];
BEGIN
    -- Check if tags array is empty
    IF jsonb_array_length(tags) = 0 THEN
        RETURN false;
    END IF;

    -- Check each tag
    FOR tag IN SELECT jsonb_array_elements_text(tags)
    LOOP
        -- Check if tag is a string and exists in allowed tags
        IF tag IS NULL OR tag NOT IN (SELECT unnest(allowed_tags)) THEN
            RETURN false;
        END IF;

        -- Check if tag is lowercase
        IF tag != lower(tag) THEN
            RETURN false;
        END IF;
    END LOOP;

    RETURN true;
END;
$$ LANGUAGE plpgsql;

-- Add a comment explaining the update
COMMENT ON FUNCTION validate_ltm_tags(jsonb) IS 
'Validates LTM memory tags against the current allowed tag list. Updated to match LTM_TAGS constant.';

-- Log the migration completion
DO $$
BEGIN
    RAISE NOTICE 'LTM tag validation function updated successfully';
    RAISE NOTICE 'Function now includes all current tags from LTM_TAGS constant';
    RAISE NOTICE 'Total allowed tags: 154';
END $$;
