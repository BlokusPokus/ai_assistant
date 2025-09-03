"""
Migration script to add authentication fields to User and AuthToken tables.

This migration adds the necessary fields for JWT authentication,
password management, and account security.
"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "001_add_authentication_fields"
down_revision = None
depends_on = None


def upgrade():
    """Add authentication fields to existing tables."""

    # Add new columns to users table
    op.add_column("users", sa.Column("hashed_password", sa.String(), nullable=True))
    op.add_column(
        "users", sa.Column("is_active", sa.Boolean(), nullable=True, default=True)
    )
    op.add_column(
        "users", sa.Column("is_verified", sa.Boolean(), nullable=True, default=False)
    )
    op.add_column("users", sa.Column("verification_token", sa.String(), nullable=True))
    op.add_column(
        "users", sa.Column("password_reset_token", sa.String(), nullable=True)
    )
    op.add_column(
        "users", sa.Column("password_reset_expires", sa.DateTime(), nullable=True)
    )
    op.add_column("users", sa.Column("last_login", sa.DateTime(), nullable=True))
    op.add_column(
        "users",
        sa.Column("failed_login_attempts", sa.Integer(), nullable=True, default=0),
    )
    op.add_column("users", sa.Column("locked_until", sa.DateTime(), nullable=True))
    op.add_column("users", sa.Column("updated_at", sa.DateTime(), nullable=True))

    # Add new columns to auth_tokens table
    op.add_column(
        "auth_tokens",
        sa.Column("token_type", sa.String(), nullable=True, default="refresh"),
    )
    op.add_column(
        "auth_tokens",
        sa.Column("is_revoked", sa.Boolean(), nullable=True, default=False),
    )
    op.add_column(
        "auth_tokens", sa.Column("last_used_at", sa.DateTime(), nullable=True)
    )

    # Make expires_at not nullable and set default for existing records
    op.execute(
        "UPDATE auth_tokens SET expires_at = created_at + INTERVAL '7 days' WHERE expires_at IS NULL"
    )
    op.alter_column("auth_tokens", "expires_at", nullable=False)

    # Make token unique
    op.create_unique_constraint("uq_auth_tokens_token", "auth_tokens", ["token"])

    # Set default values for existing records
    op.execute(
        "UPDATE users SET is_active = true, is_verified = false, failed_login_attempts = 0"
    )
    op.execute("UPDATE auth_tokens SET token_type = 'refresh', is_revoked = false")

    # Make hashed_password not nullable after setting defaults
    op.alter_column("users", "hashed_password", nullable=False)


def downgrade():
    """Remove authentication fields from tables."""

    # Remove unique constraint
    op.drop_constraint("uq_auth_tokens_token", "auth_tokens", type_="unique")

    # Remove columns from auth_tokens table
    op.drop_column("auth_tokens", "last_used_at")
    op.drop_column("auth_tokens", "is_revoked")
    op.drop_column("auth_tokens", "token_type")

    # Remove columns from users table
    op.drop_column("users", "updated_at")
    op.drop_column("users", "locked_until")
    op.drop_column("users", "failed_login_attempts")
    op.drop_column("users", "last_login")
    op.drop_column("users", "password_reset_expires")
    op.drop_column("users", "password_reset_token")
    op.drop_column("users", "verification_token")
    op.drop_column("users", "is_verified")
    op.drop_column("users", "is_active")
    op.drop_column("users", "hashed_password")
