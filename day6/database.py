# Database connection configuration
# This file sets up the connection to PostgreSQL using SQLAlchemy

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# IMPORTANT: Before running the app, create the database in PostgreSQL!
# Run this command in VSCode terminal:
#   psql -U postgres -c "CREATE DATABASE day6_db;"
#
# Database URL format: postgresql://username:password@host:port/database_name
# Update the password below to match your PostgreSQL password

SQLALCHEMY_DATABASE_URL = "postgresql://postgres:tara@localhost:5432/day6_db"

# Create engine - handles connection to database
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,  # Check connection before using
    pool_recycle=3600   # Recycle connections after 1 hour
)

# SessionLocal - provides database sessions for our application
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base - used to create database models
Base = declarative_base()

def get_db():
    """
    Dependency function to get database session.
    Yields a database session and closes it after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
