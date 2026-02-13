"""
Day 6: Database Basics + PostgreSQL
=====================================

This module demonstrates:
1. Database connection with SQLAlchemy(database.py)
2. ORM models (models.py)“ORM converts Python objects into SQL rows.”
3. Pydantic schemas (schemas.py)
4. API endpoints (api/routes.py)“Pydantic ensures user data is clean before DB.”
"""
    
# Import FastAPI and dependencies
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

# Import database setup
from database import engine, get_db
# Import ORM models
from models import Base, Student, Teacher, Course
# Import Pydantic schemas
from schemas import (
    StudentCreate, StudentUpdate, StudentResponse,
    TeacherCreate, TeacherResponse,
    CourseCreate, CourseResponse
)

# Create FastAPI app
app = FastAPI(
    title="School Management API - Day 6",
    description="Learn Database Basics with PostgreSQL",
    version="1.0.0"
)

# Enable CORS (Cross-Origin Resource Sharing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ================== Database Setup ==================

@app.on_event("startup")
def startup_event():
    """
    Create database tables on startup.
    In production, use migrations instead!
    why to use migrations? Because they allow you to version control your database schema changes, roll back changes if needed, and manage complex schema evolutions in a collaborative environment. Creating tables directly on startup is not recommended for production applications as it can lead to data loss and lacks the ability to handle schema changes gracefully.

    🏭 Real Production Analogy
    Imagine this situation 👇
    🏦 Bank database is running
    Suddenly backend restarts…
    And the app says:
    “Hmm… let me recreate tables.”
    😨 Danger!
    """
    # Create tables based on models
    Base.metadata.create_all(bind=engine)#SQLAlchemy reads all models and creates tables in PostgreSQL.”
    print("✅ Database tables created successfully!")


# ================== Database Concepts Explanation ==================

@app.get("/")
async def root():
    """
    Day 6 - Database Basics + PostgreSQL
    
    Key Concepts:
    - Database: Organized collection of structured data
    - SQL: Relational databases (tables, rows, columns)
    - NoSQL: Non-relational databases (flexible schema)
    - PostgreSQL: Open-source relational database
    - ORM: Object-Relational Mapping (SQLAlchemy)
    - Pydantic: Data validation and settings management
    """
    return {
        "message": "Welcome to Day 6 - Database Basics + PostgreSQL",
        "topics": [
            "What is a database?",
            "SQL vs NoSQL",
            "Why PostgreSQL?",
            "ORM vs Raw SQL",
            "PostgreSQL Setup",
            "pgAdmin Overview",
            "Create Database & Table"
        ],
        "documentation": "See README.md for detailed concepts"
    }


# ================== SQL Examples (Educational) ==================

@app.get("/sql-examples")
async def sql_examples():
    """
    Common SQL Commands used in PostgreSQL:
    
    CREATE DATABASE:
        CREATE DATABASE school;
    
    CREATE TABLE:
        CREATE TABLE students (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            age INTEGER
        );
    
    INSERT DATA:
        INSERT INTO students (name, email, age)
        VALUES ('John', 'john@example.com', 20);
    
    SELECT DATA:
        SELECT * FROM students;
        SELECT * FROM students WHERE age > 18;
        SELECT name, email FROM students ORDER BY name;
    
    UPDATE DATA:
        UPDATE students SET age = 21 WHERE name = 'John';
    
    DELETE DATA:
        DELETE FROM students WHERE id = 1;
    """
    return {
        "sql_commands": {
            "create_database": "CREATE DATABASE database_name;",
            "create_table": "CREATE TABLE table_name (column1 type, column2 type);",
            "insert": "INSERT INTO table (col1, col2) VALUES (val1, val2);",
            "select": "SELECT * FROM table WHERE condition;",
            "update": "UPDATE table SET col = value WHERE condition;",
            "delete": "DELETE FROM table WHERE condition;",
            "join": "SELECT * FROM t1 JOIN t2 ON t1.id = t2.t1_id;"
        },
        "postgres_commands": {
            "connect": "\\c database_name",
            "list_databases": "\\l",
            "list_tables": "\\dt",
            "describe_table": "\\d table_name"
        }
    }


# ================== ORM vs Raw SQL Comparison ==================

@app.get("/orm-vs-sql")
async def orm_vs_sql():
    """
    ORM vs Raw SQL Comparison:
    
    Raw SQL:
        cursor.execute("SELECT * FROM students WHERE age > 18")
        results = cursor.fetchall()
    
    ORM (SQLAlchemy):
        students = session.query(Student).filter(Student.age > 18).all()
    
    ORM Advantages:
    - Database agnostic (works with PostgreSQL, MySQL, SQLite)
    - Automatic SQL injection prevention
    - Type safety and validation
    - Easier migrations
    - Pythonic syntax
    
    Raw SQL Advantages:
    - Maximum performance
    - Full SQL feature access
    - No abstraction overhead
    """
    return {
        "orm": {
            "pros": [
                "Database agnostic",
                "Automatic SQL injection prevention",
                "Type safety",
                "Easier migrations",
                "Pythonic syntax"
            ],
            "cons": [
                "Learning curve",
                "Potential performance overhead",
                "May not support all database features"
            ],
            "example": "Student.query.filter(Student.age > 18).all()"
        },
        "raw_sql": {
            "pros": [
                "Maximum control and performance",
                "Full SQL feature access",
                "No abstraction layer"
            ],
            "cons": [
                "Database-specific syntax",
                "Manual error handling",
                "SQL injection risk",
                "Harder to maintain"
            ],
            "example": "SELECT * FROM students WHERE age > 18"
        }
    }


# ================== SQL vs NoSQL Comparison ==================

@app.get("/sql-vs-nosql")
async def sql_vs_nosql():
    """
    SQL vs NoSQL Comparison:
    
    SQL (PostgreSQL, MySQL):
    - Tables with rows and columns
    - Fixed schema
    - ACID compliance
    - Complex queries with JOINs
    - Vertical scaling
    
    NoSQL (MongoDB, Redis):
    - Flexible documents/keys
    - Dynamic schema
    - Eventual consistency
    - Simple queries
    - Horizontal scaling
    
    When to use SQL:
    - Complex relationships
    - Data integrity is critical
    - ACID compliance needed
    
    When to use NoSQL:
    - Unstructured/semi-structured data
    - Horizontal scaling needed
    - Fast reads/writes
    """
    return {
        "sql": {
            "examples": ["PostgreSQL", "MySQL", "SQL Server", "SQLite"],
            "structure": "Tables (rows & columns)",
            "schema": "Fixed, predefined",
            "compliance": "ACID",
            "scaling": "Vertical",
            "use_cases": [
                "Financial applications",
                "E-commerce",
                "Enterprise systems"
            ]
        },
        "nosql": {
            "examples": ["MongoDB", "Redis", "Cassandra", "DynamoDB"],
            "structure": "Documents, Key-Value, Graphs",
            "schema": "Dynamic, flexible",
            "compliance": "Eventual consistency",
            "scaling": "Horizontal",
            "use_cases": [
                "Real-time analytics",
                "Caching",
                "Content management"
            ]
        }
    }


# ================== Include API Routes ==================

# Import and include the routes
from api.routes import router as api_router

app.include_router(api_router, prefix="/api")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


#🚨 Common Student Mistakes
# ❌ Forgetting create_all()
# ❌ Forgetting to include router
# ❌ Confusing schemas with models
# ❌ Allowing * CORS in production