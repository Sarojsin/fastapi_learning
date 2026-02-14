"""
Day 7: SQLAlchemy ORM
=====================

📚 LEARNING OBJECTIVES:
1. Understand ORM (Object-Relational Mapping)
2. Learn the difference between Models and Tables
3. Set up SQLAlchemy with FastAPI
4. Create and use database models
5. Perform CRUD operations with ORM

📚 KEY CONCEPTS COVERED:
- What is ORM and why use it
- Model vs Table (CRITICAL CONCEPT)
- SQLAlchemy setup
- Creating database models
- ORM query patterns (CRUD operations)

🚀 Run with: uvicorn main:app --reload
📖 Docs at: http://localhost:8000/docs
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import database setup
from database import get_db, init_db

# Import API routes
from api.routes import router as api_router


# Create FastAPI app
app = FastAPI(
    title="Day 7: SQLAlchemy ORM",
    description="""
    # Day 7 - SQLAlchemy ORM Learning Journey 🚀
    
    ## What You'll Learn:
    - 🎯 What is ORM and why it matters
    - 🏗️ Models vs Tables (the key difference!)
    - 🔧 SQLAlchemy setup and configuration
    - 📊 Creating database models
    - 💬 Performing CRUD operations with ORM
    
    ## ORM Analogy:
    Think of ORM as a **translator** that converts:
    - Python objects ↔ Database rows
    - Python classes ↔ Database tables
    - Method calls ↔ SQL queries
    
    ## Why Use ORM?
    | Raw SQL | ORM |
    |---------|-----|
    | `SELECT * FROM users` | `User.query.all()` |
    | `INSERT INTO users...` | `db.add(user)` |
    | Database specific | Database agnostic |
    | SQL injection risk | Automatic protection |
    """,
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== Educational Endpoints ====================

@app.get("/", tags=["Welcome"])
async def root():
    """
    Welcome endpoint with Day 7 overview
    """
    return {
        "message": "🎉 Welcome to Day 7 - SQLAlchemy ORM!",
        "topic": "ORM (Object-Relational Mapping)",
        "key_concepts": [
            {
                "concept": "ORM",
                "explanation": "Technique to convert Python objects to database rows",
                "analogy": "A translator between Python and SQL languages"
            },
            {
                "concept": "Model",
                "explanation": "Python class representing a database table",
                "example": "class User(Base): ..."
            },
            {
                "concept": "Table",
                "explanation": "Physical database structure storing data",
                "example": "CREATE TABLE users (id INT PRIMARY KEY);"
            },
            {
                "concept": "Session",
                "explanation": "Workspace for database operations",
                "example": "db = SessionLocal(); db.add(user); db.commit()"
            }
        ],
        "endpoints": {
            "documentation": "/docs",
            "orm_examples": "/api/orm-examples",
            "model_vs_table": "/api/model-vs-table",
            "users": "/api/users/"
        }
    }


@app.get("/concepts", tags=["Concepts"])
async def concepts():
    """
    Educational endpoint explaining core concepts
    """
    return {
        "orm": {
            "full_name": "Object-Relational Mapping",
            "what": "Technique that converts data between incompatible type systems (Python objects ↔ SQL databases)",
            "benefits": [
                "Write Python instead of SQL",
                "Database agnostic (works with PostgreSQL, MySQL, SQLite)",
                "Type safety and IDE autocompletion",
                "Automatic SQL injection protection",
                "Easier to maintain and refactor"
            ],
            "popular_python_orms": [
                "SQLAlchemy (most popular, flexible)",
                "Django ORM (built into Django)",
                "Peewee (lightweight)",
                "Tortoise ORM (async support)"
            ]
        },
        "model_vs_table": {
            "model": {
                "world": "Python",
                "type": "Class",
                "location": "In your Python code",
                "example": "class User(Base): id = Column(Integer, primary_key=True)"
            },
            "table": {
                "world": "Database",
                "type": "Table Structure",
                "location": "In your database server",
                "example": "CREATE TABLE users (id INTEGER PRIMARY KEY);"
            },
            "relationship": "SQLAlchemy automatically creates tables from models!"
        },
        "sqlalchemy_components": {
            "engine": "Manages database connections and SQL generation",
            "session": "Provides interface for database operations",
            "base": "Base class for all ORM models",
            "model": "Python class that maps to a database table",
            "column": "Defines a field/attribute in the table"
        }
    }


@app.get("/sqlalchemy-setup", tags=["Setup"])
async def sqlalchemy_setup():
    """
    Educational endpoint explaining SQLAlchemy setup
    """
    return {
        "step_1_engine": {
            "code": "engine = create_engine('postgresql://user:pass@localhost/dbname')",
            "purpose": "Create connection to database",
            "analogy": "Opening a phone line to the database"
        },
        "step_2_base": {
            "code": "Base = declarative_base()",
            "purpose": "Create base class for all models",
            "analogy": "Creating a template for all database tables"
        },
        "step_3_session": {
            "code": "SessionLocal = sessionmaker(bind=engine)",
            "purpose": "Create session factory",
            "analogy": "Creating a factory that makes database workspaces"
        },
        "step_4_model": {
            "code": "class User(Base): __tablename__ = 'users'; id = Column(Integer, primary_key=True)",
            "purpose": "Define a database model",
            "analogy": "Designing the blueprint for a table"
        },
        "step_5_create_tables": {
            "code": "Base.metadata.create_all(bind=engine)",
            "purpose": "Create all tables in database",
            "analogy": "Building all the tables in the database"
        }
    }


@app.get("/orm-patterns", tags=["Patterns"])
async def orm_patterns():
    """
    Educational endpoint showing ORM patterns
    """
    return {
        "create": {
            "operation": "INSERT INTO users...",
            "orm_pattern": "user = User(name='John'); db.add(user); db.commit()",
            "explanation": "Create object, add to session, commit to save"
        },
        "read_all": {
            "operation": "SELECT * FROM users",
            "orm_pattern": "db.query(User).all()",
            "explanation": "Query all users from database"
        },
        "read_filter": {
            "operation": "SELECT * FROM users WHERE age > 18",
            "orm_pattern": "db.query(User).filter(User.age > 18).all()",
            "explanation": "Query with conditions using Python syntax"
        },
        "read_one": {
            "operation": "SELECT * FROM users WHERE id = 1 LIMIT 1",
            "orm_pattern": "db.query(User).filter(User.id == 1).first()",
            "explanation": "Get first matching result or None"
        },
        "read_by_id": {
            "operation": "SELECT * FROM users WHERE id = 1",
            "orm_pattern": "db.query(User).get(1)",
            "explanation": "Get by primary key directly"
        },
        "update": {
            "operation": "UPDATE users SET name='New' WHERE id=1",
            "orm_pattern": "user.name = 'New'; db.commit()",
            "explanation": "Modify object attributes, commit to save"
        },
        "delete": {
            "operation": "DELETE FROM users WHERE id=1",
            "orm_pattern": "db.delete(user); db.commit()",
            "explanation": "Delete object from database"
        }
    }


@app.get("/common-mistakes", tags=["Tips"])
async def common_mistakes():
    """
    Common mistakes students make with ORM
    """
    return {
        "mistakes": [
            {
                "mistake": "Forgetting to commit",
                "wrong_code": "db.add(user)  # Data not saved!",
                "right_code": "db.add(user); db.commit()",
                "explanation": "Changes are only saved when you commit!"
            },
            {
                "mistake": "Not using .first() for single results",
                "wrong_code": "user = db.query(User).filter(id=1)",
                "right_code": "user = db.query(User).filter(id=1).first()",
                "explanation": "Without .first(), you get a Query object, not a user!"
            },
            {
                "mistake": "Confusing model with schema",
                "wrong_code": "Using Pydantic schema where ORM model is needed",
                "right_code": "Use User model for DB operations, UserSchema for API",
                "explanation": "Models are for DB, Schemas are for API validation"
            },
            {
                "mistake": "Not closing sessions",
                "wrong_code": "session = SessionLocal(); ... # never closed",
                "right_code": "Use get_db() dependency or context manager",
                "explanation": "Always close sessions to prevent connection leaks"
            },
            {
                "mistake": "Forgetting __tablename__",
                "wrong_code": "class User(Base): id = Column(...)",
                "right_code": "class User(Base): __tablename__ = 'users'; id = Column(...)",
                "explanation": "__tablename__ is required for every model!"
            }
        ]
    }


# ==================== Include API Routes ====================

# Include the API routes with /api prefix
app.include_router(api_router, prefix="/api")


# ==================== Initialize Database ====================

@app.on_event("startup")
def startup():
    """
    Initialize database on startup
    """
    print("🚀 Starting Day 7 - SQLAlchemy ORM...")
    print("📦 Initializing database...")
    init_db()
    print("✅ Database initialized!")
    print("📖 Documentation: http://localhost:8000/docs")
    print("🎉 Ready to explore ORM!")


# ==================== Run with uvicorn ====================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
