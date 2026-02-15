"""
Day 10: Database Setup with SQLAlchemy
========================================

CONCEPTUAL BREAKDOWN:
--------------------
SQLAlchemy is a SQL toolkit that provides:
1. ORM (Object-Relational Mapping): Convert Python objects to database tables
2. SQL Expression Language: Write SQL in Python syntax
3. Connection Pooling: Efficiently manage database connections

Think of it as a TRANSLATOR:
- You speak Python (objects, classes)
- SQLAlchemy translates to SQL (tables, queries)
- Database understands and executes

KEY CONCEPTS:
- Engine: The connection to your database
- Session: A conversations with the database
- Base: Parent class for all your models
- Model: A Python class that maps to a database table

DATABASE TYPES:
- SQLite: File-based, great for learning (no server needed)
- PostgreSQL: Production-grade, most popular for FastAPI
- MySQL: Another popular production choice

ANALOGY - The Library:
- Database = The entire library building
- Table = A specific section (books, magazines, DVDs)
- Row = One item in that section (one book)
- Column = An attribute of that item (title, author, ISBN)
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# ============================================================
# DATABASE CONFIGURATION
# ============================================================

# SQLite database URL (creates a file called 'coffee_shop.db')
# In production, this would be: "postgresql://user:password@localhost/dbname"
DATABASE_URL = "sqlite:///./coffee_shop.db"

# Create the engine - this manages connections to the database
# connect_args={"check_same_thread": False is ONLY needed for SQLite
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=True  # Set to False in production to hide SQL logs
)

# SessionLocal is a factory for creating new Session objects
# Each request gets its own session (dependency injection coming in routes!)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class - all our models will inherit from this
Base = declarative_base()


# ============================================================
# HELPER FUNCTION: Database Session Dependency
# ============================================================
"""
This function will be used as a FastAPI dependency!
It provides a clean database session for each request.
"""

def get_db():
    """
    DEPENDENCY: Provides a database session.
    
    This is the pattern you'll use in EVERY FastAPI project:
    1. Open a session
    2. Yield it to the endpoint
    3. Close it when done (even if there's an error!)
    
    Usage in routes:
        @app.get("/")
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    
    Context Manager Alternative:
        with get_db() as db:
            return db.query(Item).all()
    
    Why the try/finally?
    - finally ensures the session ALWAYS closes
    - Even if your endpoint raises an error
    - Prevents memory leaks and connection pool exhaustion
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============================================================
# INITIALIZE DATABASE
# ============================================================
"""
Call this function once at app startup to create all tables!
"""

def init_db():
    """
    Create all database tables defined in our models.
    
    In production, you might use Alembic migrations instead.
    Alembic is like "Git for your database" - tracks schema changes.
    
    For learning: This function is fine!
    For production: Use migrations to avoid data loss!
    """
    # Import models here to avoid circular imports
    # (models.py imports from database.py, so we import models at runtime)
    from models import Customer, Product, Order
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("✅ Database initialized! Tables created.")
