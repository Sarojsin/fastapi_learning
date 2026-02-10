# 🚀 FastAPI - 30 Days Teaching Plan

A comprehensive journey to master FastAPI from basics to deployment.

---

## 📚 Course Overview

| Week | Focus | Duration |
|------|-------|----------|
| Week 1 | Foundations | Days 1-5 |
| Week 2 | Database & CRUD | Days 6-10 |
| Week 3 | Authentication & Security-15 |
| | Days 11 Week 4 | Advanced FastAPI | Days 16-20 |
| Week 5 | Testing, Deployment & Project | Days 21-30 |

---

## 🗓️ Week 1 – Foundations (Days 1-5)

**Goal:** Understand web, APIs, and FastAPI basics

### 📅 Day 1 – Introduction to Web & FastAPI

**Concepts:**
- What is Backend?
- What is API?
- Client-Server Architecture
- REST API basics
- Why FastAPI?
  - Fast
  - Async
  - Auto docs
  - Python type hints

**Practical:**
- Install Python & VS Code
- Create virtual environment
- Install FastAPI & Uvicorn
- First FastAPI app

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello FastAPI"}
```

---

### 📅 Day 2 – Project Structure & Routing

**Concepts:**
- Production vs beginner structure
- What is routing?
- HTTP request flow

**Practical:**
```
app/
 ├── main.py
 ├── api/
 ├── core/
```

- Multiple routes
- GET requests
- Path parameters

```python
@app.get("/students/{id}")
def get_student(id: int):
    return {"student_id": id}
```

---

### 📅 Day 3 – Query Params & Request Types

**Concepts:**
- Path vs Query parameters
- Request lifecycle

**Practical:**
- Query params (`?page=1`)
- Optional params
- Multiple GET routes
- Response formatting

---

### 📅 Day 4 – HTTP Methods Deep Dive

**Concepts:**
- GET, POST, PUT, PATCH, DELETE
- When to use what

**Practical:**
- CRUD without database (list/dict)
- Swagger UI demo
- Status codes (200, 201, 404)

---

### 📅 Day 5 – Request Body & Pydantic

**Concepts:**
- What is Pydantic?
- Why validation matters

**Practical:**
- BaseModel
- POST with request body
- Validation errors
- Auto documentation magic

---

## 🗓️ Week 2 – Database & CRUD (Days 6-10)

**Goal:** Real backend with PostgreSQL

### 📅 Day 6 – Database Basics + PostgreSQL

**Concepts:**
- What is a database?
- SQL vs NoSQL
- Why PostgreSQL?
- ORM vs Raw SQL

**Practical:**
- Install PostgreSQL
- pgAdmin overview
- Create database & table manually

---

### 📅 Day 7 – SQLAlchemy ORM

**Concepts:**
- ORM idea
- Models vs Tables

**Practical:**
- SQLAlchemy setup
- Database connection
- Create User model

```python
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
```

---

### 📅 Day 8 – CRUD with Database

**Concepts:**
- DB session lifecycle
- Dependency Injection (intro)

**Practical:**
- Create user
- Get all users
- Get user by ID
- Delete user

---

### 📅 Day 9 – Dependency Injection (Very Important)

**Concepts:**
- What is dependency injection?
- Why FastAPI uses it

**Practical:**
- Depends()
- DB session dependency
- Clean code refactor

---

### 📅 Day 10 – Error Handling & Responses

**Concepts:**
- HTTPException
- Custom responses

**Practical:**
- 404 handling
- Custom error messages
- Response models

```python
response_model=UserResponse
```

---

## 🗓️ Week 3 – Authentication & Security (Days 11-15)

**Goal:** Teach real-world security

### 📅 Day 11 – Authentication Concepts

**Concepts:**
- Authentication vs Authorization
- Session vs Token
- JWT explained visually

---

### 📅 Day 12 – Password Hashing

**Concepts:**
- Why plain passwords are dangerous
- Hashing vs Encryption

**Practical:**
- passlib
- Hash password
- Verify password

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)
```

---

### 📅 Day 13 – JWT Authentication

**Concepts:**
- JWT structure
- Access token flow

**Practical:**
- Login API
- Token generation
- Protected routes

---

### 📅 Day 14 – OAuth2 & Security Dependencies

**Concepts:**
- OAuth2PasswordBearer
- Security dependencies

**Practical:**
- Secure endpoints
- Current user dependency

---

### 📅 Day 15 – Role-Based Access Control (RBAC)

**Concepts:**
- Admin vs User roles
- Authorization flow

**Practical:**
- Role field in DB
- Admin-only routes

---

## 🗓️ Week 4 – Advanced FastAPI (Days 16-20)

**Goal:** Teach why FastAPI is powerful

### 📅 Day 16 – Middleware

**Concepts:**
- What is middleware?
- Use cases

**Practical:**
- Logging middleware
- Request timing
- Simple auth middleware

---

### 📅 Day 17 – Async & Background Tasks

**Concepts:**
- Sync vs Async
- Event loop basics

**Practical:**
- async def
- Background tasks
- Email sending simulation

---

### 📅 Day 18 – File Upload & Static Files

**Concepts:**
- Multipart form data

**Practical:**
- File upload API
- Image saving
- Static file serving

---

### 📅 Day 19 – Pagination, Filtering, Searching

**Concepts:**
- Why pagination matters

**Practical:**
- Limit & offset
- Search query
- Filter APIs

---

### 📅 Day 20 – API Versioning & Clean Architecture

**Concepts:**
- API versioning
- Clean folder structure

**Practical:**
```
api/v1/
api/v2/
```

---

## 🗓️ Week 5 – Testing, Deployment & Project (Days 21-30)

**Goal:** Make students confident & employable

### 📅 Day 21 – Environment Variables

**Concepts:**
- .env files
- Why secrets must be hidden

**Practical:**
- python-dotenv
- Secure DB URL

---

### 📅 Day 22 – Logging & Monitoring

**Concepts:**
- Why logs matter

**Practical:**
- Python logging
- Request logs

---

### 📅 Day 23 – Testing APIs

**Concepts:**
- Unit vs Integration testing

**Practical:**
- pytest
- Test API endpoints

```python
def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
```

---

### 📅 Day 24 – CORS & Frontend Connection

**Concepts:**
- What is CORS?

**Practical:**
- Enable CORS
- Connect with simple frontend

---

### 📅 Day 25 – Deployment Concepts

**Concepts:**
- What is deployment?
- Local vs cloud

**Practical:**
- Uvicorn vs Gunicorn
- Production settings

---

### 📅 Day 26 – Docker Basics (Optional but Powerful)

**Concepts:**
- What is Docker?
- Why backend devs need it

**Practical:**
- Dockerfile
- Run FastAPI in Docker

---

### 📅 Day 27 – Project Planning

**Concepts:**
- How real projects start
- Requirement analysis

**Practical:**
Mini project planning:
- College Management API
- Blog API

---

### 📅 Day 28 – Project Development (Day 1)

**Practical:**
- Auth
- CRUD
- DB integration

---

### 📅 Day 29 – Project Development (Day 2)

**Practical:**
- Roles
- Pagination
- File upload

---

### 📅 Day 30 – Review, Interview Prep & Career Tips

**Concepts:**
- Common interview questions
- API design thinking
- Django vs FastAPI comparison

**Practical:**
- Swagger walkthrough
- Student doubts
- Final polishing

---

## 🎯 Bonus Topics

| Topic | Description |
|-------|-------------|
| CSRF | Cross-Site Request Forgery concepts |
| WebSockets | Real-time communication |
| Redis Caching | Performance optimization |
| Microservices | Intro to microservices architecture |

---

## 📁 Project Structure

```
fastapi-30days/
├── day1/          # Introduction
├── day2/          # Project Structure
├── day3/          # Query Parameters
├── day4/          # HTTP Methods
├── day5/          # Request Body
├── day6/          # Database Basics
├── day7/          # SQLAlchemy ORM
├── day8/          # CRUD Operations
├── day9/          # Dependency Injection
├── day10/         # Error Handling
├── day11-15/      # Authentication & Security
├── day16-20/      # Advanced FastAPI
├── day21-26/      # Testing & Deployment
├── day27-29/      # Project Development
└── day30/         # Review & Interview Prep
```

---

## 🛠️ Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install fastapi uvicorn sqlalchemy psycopg2-binary
```

---

## 🚀 Running the Application

```bash
uvicorn dayX.main:app --reload
```

Access Swagger UI: http://localhost:8000/docs

---

## 📚 Resources

- [FastAPI Official Documentation](https://fastapi.tiangolo.com)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Pydantic Documentation](https://pydantic-docs.helpmanual.io)

---

## 🎓 Learning Tips

1. **Practice daily**: Code along with each day
2. **Don't skip**: Understanding concepts is more important than speed
3. **Build projects**: Apply learning to real scenarios
4. **Debug errors**: Learning to fix bugs is a crucial skill
5. **Read docs**: Official documentation is your best friend

---

## 📝 License

This learning material is created for educational purposes.

---

## ✨ Happy Learning!

> "The only way to learn a new programming language is by writing programs in it." - Dennis Ritchie
