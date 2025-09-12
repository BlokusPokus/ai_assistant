-- Migration: Create todos table with missed counter and segmentation features
-- Created: 2024-12-19
-- Description: Creates the todos table for enhanced task management with behavioral tracking

-- Create todos table
CREATE TABLE todos (
    -- Primary key
    id SERIAL PRIMARY KEY,
    
    -- User relationship
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Basic todo fields
    title VARCHAR(255) NOT NULL,
    description TEXT,
    due_date TIMESTAMP,
    done_date TIMESTAMP,
    priority VARCHAR(20) DEFAULT 'medium' CHECK (priority IN ('high', 'medium', 'low')),
    category VARCHAR(50),
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'completed', 'cancelled')),
    
    -- Missed counter fields
    missed_count INTEGER DEFAULT 0 NOT NULL CHECK (missed_count >= 0),
    last_missed_at TIMESTAMP,
    
    -- Segmentation fields
    is_segmented BOOLEAN DEFAULT FALSE NOT NULL,
    parent_task_id INTEGER REFERENCES todos(id) ON DELETE SET NULL,
    segmentation_triggered_at TIMESTAMP,
    
    -- Analytics fields
    completion_patterns JSONB,
    user_insights JSONB,
    segmentation_suggestions JSONB,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX idx_todos_user_id ON todos(user_id);
CREATE INDEX idx_todos_status ON todos(status);
CREATE INDEX idx_todos_due_date ON todos(due_date);
CREATE INDEX idx_todos_missed_count ON todos(missed_count);
CREATE INDEX idx_todos_is_segmented ON todos(is_segmented);
CREATE INDEX idx_todos_parent_task_id ON todos(parent_task_id);
CREATE INDEX idx_todos_user_missed ON todos(user_id, missed_count);
CREATE INDEX idx_todos_priority ON todos(priority);
CREATE INDEX idx_todos_category ON todos(category);
CREATE INDEX idx_todos_created_at ON todos(created_at);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_todos_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to automatically update updated_at
CREATE TRIGGER trigger_update_todos_updated_at
    BEFORE UPDATE ON todos
    FOR EACH ROW
    EXECUTE FUNCTION update_todos_updated_at();

-- Add comments for documentation
COMMENT ON TABLE todos IS 'Enhanced todo management with missed counter and auto-segmentation features';
COMMENT ON COLUMN todos.missed_count IS 'Number of times this todo has been missed (overdue)';
COMMENT ON COLUMN todos.is_segmented IS 'Whether this todo has been automatically segmented into subtasks';
COMMENT ON COLUMN todos.parent_task_id IS 'Reference to parent todo if this is a subtask';
COMMENT ON COLUMN todos.completion_patterns IS 'JSON data for behavioral analytics';
COMMENT ON COLUMN todos.user_insights IS 'Generated insights and recommendations for this todo';
COMMENT ON COLUMN todos.segmentation_suggestions IS 'LLM-generated suggestions for task breakdown';

-- Insert sample data for testing (optional)
-- INSERT INTO todos (user_id, title, description, due_date, priority, category, status) VALUES
-- (1, 'Complete project proposal', 'Write and submit the Q4 project proposal', NOW() + INTERVAL '3 days', 'high', 'work', 'pending'),
-- (1, 'Grocery shopping', 'Buy ingredients for weekend cooking', NOW() + INTERVAL '1 day', 'medium', 'personal', 'pending'),
-- (1, 'Exercise routine', '30-minute workout session', NOW() + INTERVAL '2 hours', 'low', 'health', 'pending');
