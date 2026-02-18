"""Database connection and session management."""

import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import text

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@db:5432/marketplace"
)

# For SQLite in-memory databases, use shared cache to allow multiple connections
# to see the same data (important when conftest.py sets DATABASE_URL)
_engine_url = DATABASE_URL
if _engine_url.startswith("sqlite") and ":memory:" in _engine_url:
    if "cache=shared" not in _engine_url:
        separator = "&" if "?" in _engine_url else "?"
        _engine_url = f"{_engine_url}{separator}cache=shared"

engine = create_async_engine(_engine_url, echo=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

# Track if tables have been initialized for SQLite
_sqlite_tables_initialized = False


async def init_sqlite_tables():
    """Initialize tables for SQLite databases (used in local tests)."""
    global _sqlite_tables_initialized
    if _sqlite_tables_initialized:
        return
    
    if not DATABASE_URL.startswith("sqlite"):
        return
    
    _sqlite_tables_initialized = True
    
    async with engine.begin() as conn:
        # Drop old tables that might have wrong schema (from conftest.py or previous runs)
        # These tables use 'status TEXT' instead of 'status_id INTEGER'
        await conn.execute(text("DROP TABLE IF EXISTS order_status_history"))
        await conn.execute(text("DROP TABLE IF EXISTS order_items"))
        await conn.execute(text("DROP TABLE IF EXISTS orders"))
        # Keep users table - schema is compatible
        
        # Create order_statuses table (PostgreSQL-compatible schema)
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS order_statuses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )
        """))
        
        # Insert default statuses (idempotent)
        await conn.execute(text("""
            INSERT OR IGNORE INTO order_statuses (name) VALUES 
            ('created'),
            ('paid'),
            ('cancelled'),
            ('shipped'),
            ('completed')
        """))
        
        # Create users table if not exists
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                created_at TIMESTAMP NOT NULL
            )
        """))
        
        # Create orders table with status_id (PostgreSQL-compatible)
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS orders (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                status_id INTEGER NOT NULL DEFAULT 1,
                total_amount REAL NOT NULL DEFAULT 0.00,
                created_at TIMESTAMP NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (status_id) REFERENCES order_statuses(id)
            )
        """))
        
        # Create order_items table
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS order_items (
                id TEXT PRIMARY KEY,
                order_id TEXT NOT NULL,
                product_name TEXT NOT NULL,
                price REAL NOT NULL,
                quantity INTEGER NOT NULL,
                FOREIGN KEY (order_id) REFERENCES orders(id)
            )
        """))
        
        # Create order_status_history table
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS order_status_history (
                id TEXT PRIMARY KEY,
                order_id TEXT NOT NULL,
                status_id INTEGER NOT NULL,
                changed_at TIMESTAMP NOT NULL,
                FOREIGN KEY (order_id) REFERENCES orders(id),
                FOREIGN KEY (status_id) REFERENCES order_statuses(id)
            )
        """))


async def get_db():
    """Dependency for getting database session."""
    # Initialize tables for SQLite on first connection
    if DATABASE_URL.startswith("sqlite"):
        await init_sqlite_tables()
    
    async with SessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# backend/app/infrastructure/db.py
import asyncpg

class Database:
    def __init__(self):
        self.pool = None

    async def connect(self, dsn="postgresql://postgres:postgres@db:5432/postgres"):
        if not self.pool:
            self.pool = await asyncpg.create_pool(dsn)

    async def disconnect(self):
        if self.pool:
            await self.pool.close()

    async def execute(self, query, *args):
        async with self.pool.acquire() as conn:
            return await conn.execute(query, *args)

    async def fetch(self, query, *args):
        async with self.pool.acquire() as conn:
            return await conn.fetch(query, *args)

    async def fetchrow(self, query, *args):
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(query, *args)

# Global instance
db = Database()
