"""
Database migration script for LTM enhancement features.

This migration adds new fields and tables to support enhanced LTM functionality:
- Enhanced LTMMemory model with new fields
- New related tables for context, relationships, access tracking, and tag management
"""

import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Any

from sqlalchemy import text, MetaData, Table, Column, String, Integer, Float, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)


class LTMEnhancementMigration:
    """Handles migration to enhanced LTM schema"""

    def __init__(self, database_url: str):
        self.database_url = database_url
        self.engine = None
        self.metadata = MetaData()

    async def run_migration(self):
        """Run the complete migration process"""
        try:
            logger.info("Starting LTM enhancement migration...")

            # Create engine and session
            self.engine = create_async_engine(self.database_url)
            async_session = sessionmaker(
                self.engine, class_=AsyncSession, expire_on_commit=False
            )

            async with async_session() as session:
                # Step 1: Add new columns to existing ltm_memories table
                await self._add_new_columns(session)

                # Step 2: Create new tables
                await self._create_new_tables(session)

                # Step 3: Migrate existing data
                await self._migrate_existing_data(session)

                # Step 4: Create indexes for performance
                await self._create_indexes(session)

                # Step 5: Update existing records with default values
                await self._update_existing_records(session)

            logger.info("LTM enhancement migration completed successfully!")

        except Exception as e:
            logger.error(f"Migration failed: {e}")
            raise
        finally:
            if self.engine:
                await self.engine.dispose()

    async def _add_new_columns(self, session: AsyncSession):
        """Add new columns to existing ltm_memories table"""
        logger.info("Adding new columns to ltm_memories table...")

        # List of new columns to add
        new_columns = [
            ("memory_type", "VARCHAR(50)"),
            ("category", "VARCHAR(100)"),
            ("confidence_score", "FLOAT DEFAULT 1.0"),
            ("dynamic_importance", "FLOAT DEFAULT 1.0"),
            ("context_data", "JSONB"),
            ("source_type", "VARCHAR(50)"),
            ("source_id", "VARCHAR(100)"),
            ("created_by", "VARCHAR(50) DEFAULT 'system'"),
            ("last_modified", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"),
            ("access_count", "INTEGER DEFAULT 0"),
            ("last_access_context", "TEXT"),
            ("related_memory_ids", "JSONB"),
            ("parent_memory_id", "INTEGER REFERENCES ltm_memories(id)"),
            ("memory_metadata", "JSONB"),
            ("is_archived", "BOOLEAN DEFAULT FALSE"),
            ("archive_reason", "TEXT")
        ]

        for column_name, column_type in new_columns:
            try:
                # Check if column already exists
                check_sql = text(f"""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'ltm_memories' 
                    AND column_name = '{column_name}'
                """)
                result = await session.execute(check_sql)

                if not result.fetchone():
                    # Add the column
                    add_sql = text(
                        f"ALTER TABLE ltm_memories ADD COLUMN {column_name} {column_type}")
                    await session.execute(add_sql)
                    logger.info(f"Added column: {column_name}")
                else:
                    logger.info(
                        f"Column {column_name} already exists, skipping...")

            except Exception as e:
                logger.warning(f"Could not add column {column_name}: {e}")
                # Continue with other columns

        await session.commit()
        logger.info("Finished adding new columns")

    async def _create_new_tables(self, session: AsyncSession):
        """Create new related tables"""
        logger.info("Creating new related tables...")

        # Create ltm_contexts table
        await self._create_ltm_contexts_table(session)

        # Create ltm_memory_relationships table
        await self._create_ltm_relationships_table(session)

        # Create ltm_memory_access table
        await self._create_ltm_access_table(session)

        # Create ltm_memory_tags table
        await self._create_ltm_tags_table(session)

        await session.commit()
        logger.info("Finished creating new tables")

    async def _create_ltm_contexts_table(self, session: AsyncSession):
        """Create ltm_contexts table"""
        create_sql = text("""
            CREATE TABLE IF NOT EXISTS ltm_contexts (
                id SERIAL PRIMARY KEY,
                memory_id INTEGER NOT NULL REFERENCES ltm_memories(id) ON DELETE CASCADE,
                context_type VARCHAR(50) NOT NULL,
                context_key VARCHAR(100) NOT NULL,
                context_value TEXT,
                confidence FLOAT DEFAULT 1.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await session.execute(create_sql)
        logger.info("Created ltm_contexts table")

    async def _create_ltm_relationships_table(self, session: AsyncSession):
        """Create ltm_memory_relationships table"""
        create_sql = text("""
            CREATE TABLE IF NOT EXISTS ltm_memory_relationships (
                id SERIAL PRIMARY KEY,
                source_memory_id INTEGER NOT NULL REFERENCES ltm_memories(id) ON DELETE CASCADE,
                target_memory_id INTEGER NOT NULL REFERENCES ltm_memories(id) ON DELETE CASCADE,
                relationship_type VARCHAR(50) NOT NULL,
                strength FLOAT DEFAULT 1.0,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(source_memory_id, target_memory_id, relationship_type)
            )
        """)
        await session.execute(create_sql)
        logger.info("Created ltm_memory_relationships table")

    async def _create_ltm_access_table(self, session: AsyncSession):
        """Create ltm_memory_access table"""
        create_sql = text("""
            CREATE TABLE IF NOT EXISTS ltm_memory_access (
                id SERIAL PRIMARY KEY,
                memory_id INTEGER NOT NULL REFERENCES ltm_memories(id) ON DELETE CASCADE,
                access_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                access_context TEXT,
                access_method VARCHAR(50),
                user_query TEXT,
                was_relevant BOOLEAN,
                relevance_score FLOAT
            )
        """)
        await session.execute(create_sql)
        logger.info("Created ltm_memory_access table")

    async def _create_ltm_tags_table(self, session: AsyncSession):
        """Create ltm_memory_tags table"""
        create_sql = text("""
            CREATE TABLE IF NOT EXISTS ltm_memory_tags (
                id SERIAL PRIMARY KEY,
                memory_id INTEGER NOT NULL REFERENCES ltm_memories(id) ON DELETE CASCADE,
                tag_name VARCHAR(100) NOT NULL,
                tag_category VARCHAR(50),
                tag_importance FLOAT DEFAULT 1.0,
                tag_confidence FLOAT DEFAULT 1.0,
                usage_count INTEGER DEFAULT 1,
                first_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(memory_id, tag_name)
            )
        """)
        await session.execute(create_sql)
        logger.info("Created ltm_memory_tags table")

    async def _migrate_existing_data(self, session: AsyncSession):
        """Migrate existing data to new schema"""
        logger.info("Migrating existing data...")

        # Update existing records with default values
        update_sql = text("""
            UPDATE ltm_memories 
            SET 
                memory_type = 'insight',
                category = 'general',
                confidence_score = 1.0,
                dynamic_importance = importance_score::FLOAT,
                created_by = 'system',
                last_modified = created_at,
                access_count = 0,
                is_archived = FALSE
            WHERE memory_type IS NULL
        """)
        await session.execute(update_sql)

        # Migrate existing tags to new tag table
        await self._migrate_existing_tags(session)

        await session.commit()
        logger.info("Finished migrating existing data")

    async def _migrate_existing_tags(self, session: AsyncSession):
        """Migrate existing tags from JSON array to tag table"""
        logger.info("Migrating existing tags...")

        # Get all memories with tags
        select_sql = text(
            "SELECT id, tags FROM ltm_memories WHERE tags IS NOT NULL")
        result = await session.execute(select_sql)
        memories = result.fetchall()

        for memory in memories:
            memory_id = memory[0]
            tags = memory[1] if memory[1] else []

            if isinstance(tags, list):
                for tag in tags:
                    if tag:
                        # Insert into new tag table
                        insert_sql = text("""
                            INSERT INTO ltm_memory_tags 
                            (memory_id, tag_name, tag_category, tag_importance, tag_confidence, usage_count, first_used, last_used)
                            VALUES (:memory_id, :tag_name, 'general', 1.0, 1.0, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                            ON CONFLICT (memory_id, tag_name) DO NOTHING
                        """)
                        await session.execute(insert_sql, {
                            "memory_id": memory_id,
                            "tag_name": str(tag)
                        })

        logger.info(f"Migrated tags for {len(memories)} memories")

    async def _create_indexes(self, session: AsyncSession):
        """Create performance indexes"""
        logger.info("Creating performance indexes...")

        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_ltm_memories_user_id ON ltm_memories(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_ltm_memories_memory_type ON ltm_memories(memory_type)",
            "CREATE INDEX IF NOT EXISTS idx_ltm_memories_category ON ltm_memories(category)",
            "CREATE INDEX IF NOT EXISTS idx_ltm_memories_importance ON ltm_memories(importance_score)",
            "CREATE INDEX IF NOT EXISTS idx_ltm_memories_dynamic_importance ON ltm_memories(dynamic_importance)",
            "CREATE INDEX IF NOT EXISTS idx_ltm_memories_source_type ON ltm_memories(source_type)",
            "CREATE INDEX IF NOT EXISTS idx_ltm_memories_created_at ON ltm_memories(created_at)",
            "CREATE INDEX IF NOT EXISTS idx_ltm_memories_last_accessed ON ltm_memories(last_accessed)",
            "CREATE INDEX IF NOT EXISTS idx_ltm_contexts_memory_id ON ltm_contexts(memory_id)",
            "CREATE INDEX IF NOT EXISTS idx_ltm_contexts_type_key ON ltm_contexts(context_type, context_key)",
            "CREATE INDEX IF NOT EXISTS idx_ltm_relationships_source ON ltm_memory_relationships(source_memory_id)",
            "CREATE INDEX IF NOT EXISTS idx_ltm_relationships_target ON ltm_memory_relationships(target_memory_id)",
            "CREATE INDEX IF NOT EXISTS idx_ltm_access_memory_id ON ltm_memory_access(memory_id)",
            "CREATE INDEX IF NOT EXISTS idx_ltm_access_timestamp ON ltm_memory_access(access_timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_ltm_tags_memory_id ON ltm_memory_tags(memory_id)",
            "CREATE INDEX IF NOT EXISTS idx_ltm_tags_name ON ltm_memory_tags(tag_name)",
            "CREATE INDEX IF NOT EXISTS idx_ltm_tags_category ON ltm_memory_tags(tag_category)"
        ]

        for index_sql in indexes:
            try:
                await session.execute(text(index_sql))
            except Exception as e:
                logger.warning(f"Could not create index: {e}")

        await session.commit()
        logger.info("Finished creating indexes")

    async def _update_existing_records(self, session: AsyncSession):
        """Update existing records with calculated values"""
        logger.info("Updating existing records...")

        # Calculate dynamic importance for existing records
        update_sql = text("""
            UPDATE ltm_memories 
            SET dynamic_importance = importance_score::FLOAT
            WHERE dynamic_importance = 1.0
        """)
        await session.execute(update_sql)

        await session.commit()
        logger.info("Finished updating existing records")


async def run_ltm_enhancement_migration(database_url: str):
    """Convenience function to run the migration"""
    migration = LTMEnhancementMigration(database_url)
    await migration.run_migration()


if __name__ == "__main__":
    # Example usage
    import os

    # Get database URL from environment or use default
    database_url = os.getenv(
        "DATABASE_URL", "postgresql+asyncpg://user:password@localhost/dbname")

    # Run migration
    asyncio.run(run_ltm_enhancement_migration(database_url))
