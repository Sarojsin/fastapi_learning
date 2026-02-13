# Day 6: Database Basics + PostgreSQL

## What is a Database?

A **database** is an organized collection of structured information, or data, typically stored electronically in a computer system. A database is usually controlled by a **Database Management System (DBMS)**.

### Key Concepts:
- **Data**: Raw facts and figures (e.g., names, numbers, dates)
- **Database**: Collection of related data
- **DBMS**: Software to manage databases (PostgreSQL, MySQL, MongoDB, etc.)
- **Schema**: Structure/blueprint of the database

---

## SQL vs NoSQL

### SQL (Relational Databases)

| Aspect | Description |
|--------|-------------|
| **Structure** | Tables with rows and columns |
| **Schema** | Fixed, predefined structure |
| **Relationships** | Uses foreign keys to link tables |
| **Examples** | PostgreSQL, MySQL, SQL Server, SQLite |
| **Language** | Standardized SQL |

**Advantages:**
- ACID compliance (Atomicity, Consistency, Isolation, Durability)
- Strong data integrity
- Complex queries with JOINs
- Mature and well-documented

**Disadvantages:**
- Less flexible schema
- Can be slower for unstructured data
- Vertical scaling

### NoSQL (Non-Relational Databases)

| Aspect | Description |
|--------|-------------|
| **Structure** | Flexible (documents, key-value, graphs, wide-columns) |
| **Schema** | Dynamic, schema-less |
| **Relationships** | Denormalized, embedded documents |
| **Examples** | MongoDB, Redis, Cassandra, DynamoDB |
| **Language** | Varies by database |

**Advantages:**
- Flexible schema
- Horizontal scaling
- Fast for simple queries
- Great for unstructured/semi-structured data

**Disadvantages:**
- Less consistent (eventual consistency)
- Complex queries can be challenging
- Less mature

---

## Why PostgreSQL?

### Key Features:

1. **Open Source**: Free and community-driven
2. **ACID Compliant**: Ensures data integrity
3. **Rich Data Types**: JSON, Array, HStore, PostGIS, etc.
4. **Extensions**: TimescaleDB, Citus, pgvector
5. **Strong SQL Compliance**: Nearly 100% SQL standard
6. **Performance**: Excellent for complex queries
7. **Concurrency**: MVCC (Multi-Version Concurrency Control)
8. **Reliability**: Used by Apple, Instagram, Spotify, NASA

### Use Cases:
- Financial applications
- Geospatial applications (PostGIS)
- Data warehousing
- Web applications
- Scientific research

---

## ORM vs Raw SQL

### Raw SQL

```python
import psycopg2

# Connect to database
conn = psycopg2.connect(
    host="localhost",
    database="school",
    user="postgres",
    password="password"
)

# Execute raw SQL
cursor = conn.cursor()
cursor.execute("SELECT * FROM students WHERE age > 18")
results = cursor.fetchall()

# Close connection
cursor.close()
conn.close()
```

**Advantages:**
- Maximum control and performance
- Full SQL feature access
- No abstraction layer

**Disadvantages:**
- Database-specific syntax
- Manual error handling
- Security risks (SQL injection)
- Harder to maintain

### ORM (Object-Relational Mapping)

```python
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Student(Base):
    __tablename__ = 'students'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    age = Column(Integer)

# Create engine and session
engine = create_engine('postgresql://user:password@localhost/school')
Session = sessionmaker(bind=engine)
session = Session()

# Query using ORM
students = session.query(Student).filter(Student.age > 18).all()
```

**Advantages:**
- Database agnostic
- Automatic SQL injection prevention
- Type safety
- Easier migrations
- Clean, Pythonic code

**Disadvantages:**
- Learning curve
- Potential performance overhead
- May not support all database features

### Popular ORMs for Python:
- **SQLAlchemy**: Most popular, flexible
- **Django ORM**: Built into Django framework
- **Peewee**: Lightweight, simple
- **Tortoise ORM**: Async support

---

## Practical: PostgreSQL Setup

### 1. Installation

**Windows:**
1. Download from https://www.postgresql.org/download/windows/
2. Run the installer
3. Set a password for the postgres user
4. Keep default port: 5432

**Linux (Ubuntu):**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

**macOS:**
```bash
brew install postgresql
brew services start postgresql
```

### 2. pgAdmin Overview

pgAdmin is a web-based administration tool for PostgreSQL.

**Access:**
- Open browser and go to http://localhost:5050
- Login with your pgAdmin credentials

**Key Features:**
- Object browser (databases, schemas, tables)
- Query tool (execute SQL)
- Data export/import
- Backup/restore
- User management
- Performance monitoring

### 3. Create Database & Table Manually

#### Step 1: Create Database

```sql
-- In pgAdmin Query Tool or psql
CREATE DATABASE school;
```

#### Step 2: Connect to Database

```sql
\c school
```

#### Step 3: Create Table

```sql
CREATE TABLE students (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    age INTEGER CHECK (age >= 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Step 4: Insert Data

```sql
INSERT INTO students (name, email, age) 
VALUES ('John Doe', 'john@example.com', 20);

INSERT INTO students (name, email, age) 
VALUES ('Jane Smith', 'jane@example.com', 19);
```

#### Step 5: Query Data

```sql
SELECT * FROM students;
SELECT * FROM students WHERE age > 18;
SELECT name, email FROM students ORDER BY name;
```

#### Step 6: Update Data

```sql
UPDATE students SET age = 21 WHERE name = 'John Doe';
```

#### Step 7: Delete Data

```sql
DELETE FROM students WHERE name = 'Jane Smith';
```

---

## Hands-On: FastAPI + PostgreSQL

### Setup Project

```bash
# Install required packages
pip install sqlalchemy psycopg2-binary
```

### Project Structure
```
day6/
├── main.py
├── api/
│   └── routes.py
├── database.py
├── models.py
└── schemas.py
```

---

## Summary

| Topic | Key Points |
|-------|------------|
| Database | Organized collection of structured data |
| SQL | Relational, structured, ACID compliant |
| NoSQL | Non-relational, flexible schema |
| PostgreSQL | Open source, feature-rich, reliable |
| ORM | Abstraction layer, safer, database agnostic |
| Raw SQL | Maximum control, direct database access |

---

## Next Steps

- Practice creating databases and tables
- Learn SQL queries (SELECT, INSERT, UPDATE, DELETE)
- Understand joins and relationships
- Connect FastAPI to PostgreSQL (Day 7)
