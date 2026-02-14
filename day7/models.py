"""
Day 7: SQLAlchemy ORM - Models
==============================

📚 KEY CONCEPTS FOR STUDENTS:

MODEL vs TABLE:
- Model: Python class that represents a database table
- Table: The actual database structure
- SQLAlchemy automatically creates tables from models

WHY USE MODELS?
- Write Python instead of SQL
- Type safety and IDE autocompletion
- Database agnostic (works with PostgreSQL, MySQL, SQLite)
- Automatic SQL injection protection
- Easy to change database later

STRUCTURE OF A MODEL:
1. Inherit from Base (from database.py)
2. Define __tablename__ (REQUIRED - table name in database)
3. Define columns using Column()
4. Optionally add relationships, constraints, etc.
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from datetime import datetime
from database import Base


class User(Base):
    """
    User Model - represents the 'users' table in the database
    
    🏗️ This Python class becomes a database table!
    
    Table Name: users (specified in __tablename__)
    
    Columns:
    - id: Integer, primary key (unique identifier)
    - name: String(100), cannot be null
    - email: String(100), unique, cannot be null
    - age: Integer, defaults to 5
    - is_active: Boolean, defaults to True
    - created_at: DateTime, auto-set to current time
    - updated_at: DateTime, auto-updates on modification
    
    📝 What SQLAlchemy Creates:
    CREATE TABLE users (
        id INTEGER PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        email VARCHAR(100) NOT NULL UNIQUE,
        age INTEGER DEFAULT 5,
        is_active BOOLEAN DEFAULT 1,
        created_at TIMESTAMP,
        updated_at TIMESTAMP
    );
    """
    
    # REQUIRED: Define the table name
    __tablename__ = "users"
    
    # Column definitions:
    # Column(type, constraints)
    


    # Primary Key - unique identifier for each row
    id = Column(Integer, primary_key=True, index=True)
    
    # String column with max 100 characters
    # nullable=False means this field cannot be empty
    name = Column(String(100), nullable=False)
    
    # Email - must be unique across all users
    email = Column(String(100), nullable=False, unique=True)
    
    # Age - defaults to 5 if not specified
    age = Column(Integer, default=5)
    
    # Boolean - True/False status
    is_active = Column(Boolean, default=True)
    
    # DateTime - stores date and time
    # default=datetime.utcnow sets current time automatically
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # onupdate=datetime.utcnow updates this when row is modified
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Optional: __repr__ method for debugging
    #__repr__ is a special (magic/dunder) method in Python.

    def __repr__(self):
        return f"<User(id={self.id}, name='{self.name}', email='{self.email}')>"

#    🔹 6️⃣ Important Difference: __repr__ vs __str__
#         Method	  Purpose
#        __repr__	  Developer/debug representation
#        __str__	  User-friendly string


# 📚 COMMON COLUMN TYPES:
# =======================
# Integer         - Whole numbers (1, 2, 3, ...)
# String(n)      - Text with max n characters
# Text           - Long text without max length
# Boolean        - True or False
# Float          - Decimal numbers
# DateTime       - Date and time (datetime objects)
# Date           - Date only
# JSON           - JSON data (dict/list)
# Enum           - Fixed set of choices

# 📚 COMMON COLUMN CONSTRAINTS:
# ============================
# primary_key    - Unique identifier (only ONE per table)
# unique         - Value must be unique in the column
# nullable       - False = cannot be empty/None
# default        - Default value if not specified
# index          - Creates database index for faster queries
# onupdate       - Function to call when row is updated


# Additional Examples (commented out):
# ====================================

class Product(Base):
    """Example of a more complex model"""
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)#max length
    price = Column(Integer)  # Store as cents (integer)
    in_stock = Column(Boolean, default=True)
    category = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Order(Base):
    """Example showing foreign key relationship"""
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)  # Foreign key to users
    total_amount = Column(Integer)  # Amount in cents
    status = Column(String(50), default='pending')
    created_at = Column(DateTime, default=datetime.utcnow)
