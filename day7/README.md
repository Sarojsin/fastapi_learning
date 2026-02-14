# Day 7: SQLAlchemy ORM

## What is ORM?

**ORM (Object-Relational Mapping)** is a technique that lets you query and manipulate data from a database using an **object-oriented paradigm**. Instead of writing raw SQL queries, you work with Python objects.

### Analogy 🏠

Think of ORM as a **translator** between two languages:

```
Python World 🌍                    Database World 🗄️
┌─────────────────┐               ┌─────────────────┐
│   Python Code   │  ◄─────────►  │   SQL Database  │
│                 │    ORM        │                 │
│  User(name=     │    Magic      │  SELECT * FROM  │
│   "John",       │               │  users WHERE    │
│   age=25)       │               │  name='John';   │
└─────────────────┘               └─────────────────┘
```

### Why Use ORM?

| Raw SQL | ORM (SQLAlchemy) |
|---------|------------------|
| `SELECT * FROM users WHERE age > 18` | `User.query.filter(User.age > 18).all()` |
| `INSERT INTO users (name) VALUES ('John')` | `user = User(name='John'); db.add(user)` |
| `DELETE FROM users WHERE id = 1` | `db.delete(user)` |
| Database-specific syntax | Works with PostgreSQL, MySQL, SQLite, etc. |
| Manual SQL injection protection | Automatic protection |
| String-based queries | Type-safe, IDE autocompletion |

---

## Models vs Tables

This is a fundamental concept students often confuse!

### Table (Database World)
- **Physical storage** in the database
- Contains rows and columns
- Created when you run migrations
- Exists in your PostgreSQL/MySQL database
- **Schema**: `CREATE TABLE users (id INT, name VARCHAR(100));`

### Model (Python World)
- **Python class** that represents a table
- Defines structure using Column objects
- Used in your Python code
- **Magic**: SQLAlchemy translates model → table automatically
- **Schema**: `class User(Base): id = Column(Integer); name = Column(String)`

### Visual Representation

```
┌─────────────────────────────────────────────────────────────┐
│                    DATABASE                                 │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                  Table: users                       │    │
│  │  ┌────┬────────┬─────┬─────────────────────────┐    │    │
│  │  │ id │  name  │ age │       created_at        │    │    │
│  │  ├────┼────────┼─────┼─────────────────────────┤    │    │
│  │  │ 1  │ John   │ 25  │ 2024-01-15 10:30:00     │    │    │
│  │  │ 2  │ Jane   │ 22  │ 2024-01-16 14:20:00     │    │    │
│  │  │ 3  │ Bob    │ 30  │ 2024-01-17 09:15:00     │    │    │
│  │  └────┴────────┴─────┴─────────────────────────┘    │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                            ▲
                            │ ORM Mapping
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    PYTHON CODE                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                 Model: User                         │    │
│  │  ┌─────────────────────────────────────────────┐    │    │
│  │  │ class User(Base):                           │    │    │
│  │  │     __tablename__ = 'users'                 │    │    │
│  │  │     id = Column(Integer, primary_key=True)  │    │    │
│  │  │     name = Column(String(100))              │    │    │
│  │  │     created_at = Column(DateTime)           │    │    │
│  │  │     age = Column(Integer)                   │    │    │
│  │  └─────────────────────────────────────────────┘    │    │
│  │                                                │    │    │
│  │  user = User(name="John", age=25)  # Python obj│    │    │
│  │  db.add(user)  # → INSERT INTO users...        │    │    │
│  │                                                │    │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### Key Difference Summary

| Aspect | Table | Model |
|--------|-------|-------|
| **World** | Database | Python |
| **Language** | SQL | Python |
| **Definition** | DDL (CREATE TABLE) | Python Class |
| **Instance** | Row (data) | Object |
| **Access** | SQL queries | Method calls |
| **Created by** | Database engine | SQLAlchemy |

---
## SQLAlchemy Core Components

### 1. Engine
The **engine** is the starting point for any SQLAlchemy application. It manages the database connection pool.

```python
from sqlalchemy import create_engine

# Create engine - manages connections
engine = create_engine("postgresql://user:pass@localhost/dbname")
```

### 2. Declarative Base
The **Base** class is used to create all your ORM models. It uses the **Declarative System**.

```python
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
```

### 3. Session
A **Session** is the means by which all Python-Database interaction is orchestrated.

```python
from sqlalchemy.orm import sessionmaker

SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()
```

### 4. Column Types

| SQLAlchemy Type | Python Type | Database Type | Use Case |
|-----------------|-------------|----------------|----------|
| `Integer` | `int` | INT | Whole numbers |
| `String(n)` | `str` | VARCHAR(n) | Text with max length |
| `Text` | `str` | TEXT | Long text |
| `Boolean` | `bool` | BOOLEAN | True/False |
| `Float` | `float` | FLOAT | Decimal numbers |
| `DateTime` | `datetime` | TIMESTAMP | Date and time |
| `Date` | `date` | DATE | Date only |
| `JSON` | `dict/list` | JSON | Structured data |
| `Enum` | `str/enum` | ENUM | Fixed choices |

### 5. Column Arguments

```python
class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)  # Primary key
    name = Column(String(100))              # String with max 100 chars
    email = Column(String(100), unique=True)  # Must be unique
    age = Column(Integer, nullable=False)   # Cannot be null
    status = Column(String, default='active')  # Default value
    created_at = Column(DateTime, default=datetime.utcnow)  # Auto-set
```

---

## Creating Your First Model

### Step 1: Define the Model

```python
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    """
    User model - represents the users table
    
    📝 Note: This is Python code, NOT SQL!
    SQLAlchemy will generate the SQL for us.
    """
    __tablename__ = 'users'  # Table name in database
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    age = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
```

### Step 2: What SQLAlchemy Generates

When you run `Base.metadata.create_all(bind=engine)`, SQLAlchemy creates this SQL:

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    age INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Step 3: Using the Model

```python
# Create a new user (Python object)
new_user = User(name="John Doe", email="john@example.com", age=25)

# Add to database
session.add(new_user)
session.commit()  # Save to database

# Query all users
all_users = session.query(User).all()

# Query with filter
adults = session.query(User).filter(User.age >= 18).all()

# Get by ID
user = session.query(User).get(1)

# Update
user.age = 26
session.commit()

# Delete
session.delete(user)
session.commit()
```

---

## Hands-On: Complete User Management API

### Project Structure
```
day7/
├── main.py           # FastAPI app with educational endpoints
├── database.py       # Database connection setup
├── models.py         # User model definition
├── schemas.py        # Pydantic schemas
├── api/
│   └── routes.py     # API endpoints
└── README.md         # This file
```

---

## Common Student Mistakes 🚨

1. **❌ Forgetting `__tablename__`**
   ```python
   # Wrong: Will cause error
   class User(Base):
       id = Column(Integer, primary_key=True)
   
   # Correct:
   class User(Base):
       __tablename__ = 'users'
       id = Column(Integer, primary_key=True)
   ```

2. **❌ Confusing Model with Schema**
   - **Model**: Database structure (SQLAlchemy)
   - **Schema**: API data validation (Pydantic)
   - They serve different purposes!

3. **❌ Forgetting to Commit**
   ```python
   # Wrong: Data not saved
   session.add(user)
   # ... nothing happens
   
   # Correct:
   session.add(user)
   session.commit()  # Save to database
   ```

4. **❌ Not Closing Sessions**
   ```python
   # Wrong: Connection leak
   session = SessionLocal()
   # ... use session
   # session never closed
   
   # Correct: Use dependency
   def get_db():
       db = SessionLocal()
       try:
           yield db
       finally:
           db.close()
   ```

5. **❌ Primary Key Confusion**
   ```python
   # Wrong: Multiple primary keys
   id = Column(Integer)
   id2 = Column(Integer, primary_key=True)
   
   # Correct: Only ONE primary key
   id = Column(Integer, primary_key=True)
   ```

---

## Summary
| Concept | Description |
|---------|-------------|
| **ORM** | Object-Relational Mapping - translates Python objects to SQL |
| **Model** | Python class representing a database table |
| **Table** | Physical database structure with rows and columns |
| **SQLAlchemy** | Popular Python ORM library |
| **Base** | Declarative base class for all models |
| **Engine** | Manages database connections |
| **Session** | Interface for database operations |

---

## Next Steps

- Practice creating different models
- Learn about relationships (Foreign Keys)
- Understand migrations with Alembic
- Build complex queries with filters and joins
