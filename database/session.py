from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv(
    "REAL_DB_URL") or "postgresql+asyncpg://ianleblanc:password@localhost:5432/postgres"

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
)

# Create async session factory
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)
