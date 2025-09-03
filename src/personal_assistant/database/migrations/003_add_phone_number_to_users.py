"""
Migration script to add phone number field to User table.

This migration adds a phone_number field to the users table for
phone-based authentication and user identification.
"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "003_add_phone_number_to_users"
down_revision = "002_add_rbac_system"
depends_on = None


def upgrade():
    """Add phone number field to users table."""

    # Add phone_number column to users table
    op.add_column(
        "users", sa.Column("phone_number", sa.String(20), nullable=True, unique=True)
    )

    # Create index for phone number lookups
    op.create_index("idx_users_phone_number", "users", ["phone_number"])


def downgrade():
    """Remove phone number field from users table."""

    # Remove index
    op.drop_index("idx_users_phone_number", "users")

    # Remove phone_number column
    op.drop_column("users", "phone_number")
