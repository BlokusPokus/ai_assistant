-- Rollback Migration: Drop todos table
-- Created: 2024-12-19
-- Description: Removes the todos table and all related objects

-- Drop trigger first
DROP TRIGGER IF EXISTS trigger_update_todos_updated_at ON todos;

-- Drop function
DROP FUNCTION IF EXISTS update_todos_updated_at();

-- Drop table (this will also drop all indexes and constraints)
DROP TABLE IF EXISTS todos CASCADE;

-- Note: This will permanently delete all todo data
-- Make sure to backup data before running this rollback script
