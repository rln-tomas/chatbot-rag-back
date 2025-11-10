"""
Database configuration and session management.
Sets up SQLAlchemy engine and session for MySQL.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Base class for all models (must be defined first for Alembic)
Base = declarative_base()

# Lazy initialization of engine and session
_engine = None
_SessionLocal = None


def get_engine():
    """Get or create the SQLAlchemy engine."""
    global _engine
    if _engine is None:
        from app.core.config import settings
        _engine = create_engine(
            settings.DATABASE_URL,
            pool_pre_ping=True,  # Verify connections before using them
            pool_recycle=3600,   # Recycle connections after 1 hour
            echo=settings.DEBUG,  # Log SQL queries in debug mode
        )
    return _engine


def get_session_local():
    """Get or create the SessionLocal class."""
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=get_engine()
        )
    return _SessionLocal


def get_db():
    """
    Dependency function to get database session.
    Yields a database session and closes it after use.

    Usage:
        @router.get("/endpoint")
        def endpoint(db: Session = Depends(get_db)):
            # Use db here
    """
    SessionLocal = get_session_local()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
