"""Database setup.

SQLite is used by default. Set the DATABASE_URL environment variable to
use PostgreSQL instead, e.g.:

    DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/tickets
"""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./tickets.db")

# check_same_thread is only needed for SQLite (used by FastAPI's threadpool).
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """FastAPI dependency that yields a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
