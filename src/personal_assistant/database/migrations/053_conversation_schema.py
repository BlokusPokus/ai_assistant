"""
Migration 053: Create Normalized Conversation Schema

This migration creates the new normalized database schema for conversation states,
replacing the JSON blob approach with proper relational tables.

Tables Created:
- conversation_states: Core conversation state data
- conversation_messages: Individual conversation messages
- memory_context_items: Memory context items
- Enhanced memory_metadata: Universal metadata storage

Migration Strategy:
1. Create new tables
2. Add indexes and constraints
3. Preserve existing data in memory_chunks
4. Enable gradual migration
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '053_conversation_schema'
# Update this to your previous migration
down_revision = '052_state_management_optimization'
branch_labels = None
depends_on = None


def upgrade():
    """Create new normalized conversation schema"""

    # Create conversation_states table
    op.create_table('conversation_states',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('conversation_id', sa.String(
                        length=255), nullable=False),
                    sa.Column('user_id', sa.Integer(), nullable=False),
                    sa.Column('user_input', sa.Text(), nullable=True),
                    sa.Column('focus_areas', sa.JSON(), nullable=True),
                    sa.Column('step_count', sa.Integer(), nullable=True),
                    sa.Column('last_tool_result', sa.JSON(), nullable=True),
                    sa.Column('created_at', sa.DateTime(
                        timezone=True), nullable=True),
                    sa.Column('updated_at', sa.DateTime(
                        timezone=True), nullable=True),
                    sa.ForeignKeyConstraint(
                        ['user_id'], ['users.id'], ondelete='CASCADE'),
                    sa.PrimaryKeyConstraint('id')
                    )

    # Create conversation_messages table
    op.create_table('conversation_messages',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('conversation_id', sa.String(
                        length=255), nullable=False),
                    sa.Column('role', sa.String(length=50), nullable=False),
                    sa.Column('content', sa.Text(), nullable=True),
                    sa.Column('message_type', sa.String(
                        length=50), nullable=True),
                    sa.Column('tool_name', sa.String(
                        length=100), nullable=True),
                    sa.Column('tool_success', sa.String(
                        length=10), nullable=True),
                    sa.Column('timestamp', sa.DateTime(
                        timezone=True), nullable=True),
                    sa.Column('metadata', sa.JSON(), nullable=True),
                    sa.ForeignKeyConstraint(['conversation_id'], [
                        'conversation_states.conversation_id'], ondelete='CASCADE'),
                    sa.PrimaryKeyConstraint('id')
                    )

    # Create memory_context_items table
    op.create_table('memory_context_items',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('conversation_id', sa.String(
                        length=255), nullable=False),
                    sa.Column('source', sa.String(length=50), nullable=False),
                    sa.Column('content', sa.Text(), nullable=True),
                    sa.Column('relevance_score', sa.Float(), nullable=True),
                    sa.Column('context_type', sa.String(
                        length=50), nullable=True),
                    sa.Column('original_role', sa.String(
                        length=50), nullable=True),
                    sa.Column('focus_area', sa.String(
                        length=100), nullable=True),
                    sa.Column('preference_type', sa.String(
                        length=100), nullable=True),
                    sa.Column('timestamp', sa.DateTime(
                        timezone=True), nullable=True),
                    sa.Column('metadata', sa.JSON(), nullable=True),
                    sa.ForeignKeyConstraint(['conversation_id'], [
                        'conversation_states.conversation_id'], ondelete='CASCADE'),
                    sa.PrimaryKeyConstraint('id')
                    )

    # Enhance memory_metadata table
    op.add_column('memory_metadata', sa.Column(
        'table_name', sa.String(length=50), nullable=True))
    op.add_column('memory_metadata', sa.Column(
        'record_id', sa.Integer(), nullable=True))
    op.add_column('memory_metadata', sa.Column(
        'created_at', sa.DateTime(timezone=True), nullable=True))

    # Create indexes for performance
    op.create_index('idx_conversation_id', 'conversation_states', [
                    'conversation_id'], unique=True)
    op.create_index('idx_conversation_user', 'conversation_states', [
                    'user_id', 'created_at'])
    op.create_index('idx_conversation_focus',
                    'conversation_states', ['focus_areas'])
    op.create_index('idx_conversation_updated',
                    'conversation_states', ['updated_at'])

    op.create_index('idx_message_conversation_role',
                    'conversation_messages', ['conversation_id', 'role'])
    op.create_index('idx_message_timestamp', 'conversation_messages', [
                    'conversation_id', 'timestamp'])
    op.create_index('idx_message_type',
                    'conversation_messages', ['message_type'])
    op.create_index('idx_message_tool', 'conversation_messages', [
                    'tool_name', 'tool_success'])

    op.create_index('idx_context_conversation_source',
                    'memory_context_items', ['conversation_id', 'source'])
    op.create_index('idx_context_relevance', 'memory_context_items', [
                    'conversation_id', 'relevance_score'])
    op.create_index('idx_context_type',
                    'memory_context_items', ['context_type'])
    op.create_index('idx_context_focus',
                    'memory_context_items', ['focus_area'])
    op.create_index('idx_context_timestamp',
                    'memory_context_items', ['timestamp'])

    op.create_index('idx_metadata_table_record',
                    'memory_metadata', ['table_name', 'record_id'])
    op.create_index('idx_metadata_key_value',
                    'memory_metadata', ['key', 'value'])
    op.create_index('idx_metadata_created', 'memory_metadata', ['created_at'])

    # Set default values for existing memory_metadata records
    op.execute(
        "UPDATE memory_metadata SET table_name = 'memory_chunks' WHERE table_name IS NULL")
    op.execute(
        "UPDATE memory_metadata SET record_id = chunk_id WHERE record_id IS NULL")
    op.execute(
        "UPDATE memory_metadata SET created_at = NOW() WHERE created_at IS NULL")

    # Make new columns NOT NULL after setting defaults
    op.alter_column('memory_metadata', 'table_name', nullable=False)
    op.alter_column('memory_metadata', 'record_id', nullable=False)
    op.alter_column('memory_metadata', 'created_at', nullable=False)


def downgrade():
    """Rollback to previous schema"""

    # Drop indexes
    op.drop_index('idx_metadata_created', 'memory_metadata')
    op.drop_index('idx_metadata_key_value', 'memory_metadata')
    op.drop_index('idx_metadata_table_record', 'memory_metadata')

    op.drop_index('idx_context_timestamp', 'memory_context_items')
    op.drop_index('idx_context_focus', 'memory_context_items')
    op.drop_index('idx_context_type', 'memory_context_items')
    op.drop_index('idx_context_relevance', 'memory_context_items')
    op.drop_index('idx_context_conversation_source', 'memory_context_items')

    op.drop_index('idx_message_tool', 'conversation_messages')
    op.drop_index('idx_message_type', 'conversation_messages')
    op.drop_index('idx_message_timestamp', 'conversation_messages')
    op.drop_index('idx_message_conversation_role', 'conversation_messages')

    op.drop_index('idx_conversation_updated', 'conversation_states')
    op.drop_index('idx_conversation_focus', 'conversation_states')
    op.drop_index('idx_conversation_user', 'conversation_states')
    op.drop_index('idx_conversation_id', 'conversation_states')

    # Drop new columns from memory_metadata
    op.drop_column('memory_metadata', 'created_at')
    op.drop_column('memory_metadata', 'record_id')
    op.drop_column('memory_metadata', 'table_name')

    # Drop new tables
    op.drop_table('memory_context_items')
    op.drop_table('conversation_messages')
    op.drop_table('conversation_states')


def data_migration():
    """Migrate existing data from memory_chunks to new schema"""

    # This function will be called separately to migrate existing data
    # It's not part of the schema migration to avoid blocking the upgrade

    # Example migration logic:
    # 1. Extract conversation data from existing memory_chunks
    # 2. Parse JSON content to extract conversation structure
    # 3. Insert into new normalized tables
    # 4. Preserve existing metadata relationships

    pass
