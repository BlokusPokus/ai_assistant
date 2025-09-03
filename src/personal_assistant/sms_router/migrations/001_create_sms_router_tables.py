"""Create SMS Router Service tables.

Revision ID: 001_sms_router
Revises: 003_add_phone_number_to_users
Create Date: 2025-01-XX XX:XX:XX.XXXXXX
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "001_sms_router"
down_revision = "003_add_phone_number_to_users"
depends_on = None


def upgrade():
    """Create SMS Router Service tables."""

    # Create sms_router_configs table
    op.create_table(
        "sms_router_configs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("config_key", sa.String(length=100), nullable=False),
        sa.Column("config_value", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("config_key"),
    )

    # Create sms_usage_logs table
    op.create_table(
        "sms_usage_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("phone_number", sa.String(length=20), nullable=False),
        sa.Column("message_direction", sa.String(length=10), nullable=False),
        sa.Column("message_length", sa.Integer(), nullable=False),
        sa.Column("twilio_message_sid", sa.String(length=50), nullable=True),
        sa.Column("processing_time_ms", sa.Integer(), nullable=True),
        sa.Column("success", sa.Boolean(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("metadata", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("twilio_message_sid"),
    )

    # Create user_phone_mappings table
    op.create_table(
        "user_phone_mappings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("phone_number", sa.String(length=20), nullable=False),
        sa.Column("is_primary", sa.Boolean(), nullable=True),
        sa.Column("is_verified", sa.Boolean(), nullable=True),
        sa.Column("verification_method", sa.String(length=50), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create indexes for performance
    op.create_index("idx_sms_usage_logs_user_id", "sms_usage_logs", ["user_id"])
    op.create_index(
        "idx_sms_usage_logs_phone_number", "sms_usage_logs", ["phone_number"]
    )
    op.create_index("idx_sms_usage_logs_created_at", "sms_usage_logs", ["created_at"])
    op.create_index(
        "idx_user_phone_mappings_user_id", "user_phone_mappings", ["user_id"]
    )
    op.create_index(
        "idx_user_phone_mappings_phone_number", "user_phone_mappings", ["phone_number"]
    )
    op.create_index("idx_sms_router_configs_key", "sms_router_configs", ["config_key"])


def downgrade():
    """Drop SMS Router Service tables."""

    # Drop indexes
    op.drop_index("idx_sms_router_configs_key", "sms_router_configs")
    op.drop_index("idx_user_phone_mappings_phone_number", "user_phone_mappings")
    op.drop_index("idx_user_phone_mappings_user_id", "user_phone_mappings")
    op.drop_index("idx_sms_usage_logs_created_at", "sms_usage_logs")
    op.drop_index("idx_sms_usage_logs_phone_number", "sms_usage_logs")
    op.drop_index("idx_sms_usage_logs_user_id", "sms_usage_logs")

    # Drop tables
    op.drop_table("user_phone_mappings")
    op.drop_table("sms_usage_logs")
    op.drop_table("sms_router_configs")
