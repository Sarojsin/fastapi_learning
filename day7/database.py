"""
Day 7: SQLAlchemy ORM - Database Connection
============================================

This file sets up the database connection using SQLAlchemy.

📚 KEY CONCEPTS FOR STUDENTS:

1. Engine: The starting point for SQLAlchemy
   - Manages database connections
   - Handles connection pooling
   - Translates Python to SQL

2. SessionLocal: Creates database sessions
   - A session is like a temporary workspace
   - All operations happen within a session
   - Must be committed to save changes

3. Base: The declarative base class
   - All models inherit from this
   - Tracks all model classes
   - Used to create database tables
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Database URL format:
# postgresql://username:password@host:port/database_name
#
# For development/testing, we can use SQLite:
# sqlite:///./day7.db (creates a file called day7.db)
#
# PostgreSQL (production):
# postgresql://postgres:password@localhost:5432/day7_db

# Using SQLite for easy setup (no PostgreSQL required!)
SQLALCHEMY_DATABASE_URL = "sqlite:///./day7.db"

# For PostgreSQL (uncomment if you have PostgreSQL installed):
# SQLALCHEMY_DATABASE_URL = "postgresql://postgres:tara@localhost:5432/day7_db"

# Create the SQLAlchemy engine
# The engine is responsible for managing database connections
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    # These options are for SQLite:
    connect_args={"check_same_thread": False}
    # For PostgreSQL, use:
    # pool_pre_ping=True,  # Check connection before using
    # pool_recycle=3600   # Recycle connections after 1 hour
)

# Create SessionLocal class
# This is a factory for creating new database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
# All ORM models will inherit from this
Base = declarative_base()

def get_db():
    """
    Dependency function to get database session.
    
    📝 Why use this pattern?
    - Ensures sessions are properly closed
    - Prevents connection leaks
    - Works with FastAPI's dependency injection
    
    Usage in FastAPI:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database by creating all tables.
    
    📝 Note: In production, use Alembic migrations instead!
    Migrations allow you to:
    - Version control schema changes
    - Rollback if something goes wrong
    - Apply changes incrementally
    """
    # Import all models to ensure they're registered
    from models import User ,Product,Order
    
    # Create all tables defined in models
    Base.metadata.create_all(bind=engine)
    print("✅ Database initialized! Tables created.")


if __name__ == "__main__":
    # Run this to initialize the database
    init_db()
