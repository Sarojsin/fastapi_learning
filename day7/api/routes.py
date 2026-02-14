"""
Day 7: SQLAlchemy ORM - API Routes
==================================

📚 KEY CONCEPTS FOR STUDENTS:

ORM QUERY PATTERNS:

1. Create (INSERT):
   new_user = User(name="John", email="john@example.com")
   db.add(new_user)
   db.commit()

2. Read (SELECT):
   # Get all users
   users = db.query(User).all()
   
   # Get one user by ID
   user = db.query(User).filter(User.id == 1).first()
   
   # Get with conditions
   adults = db.query(User).filter(User.age >= 18).all()

3. Update:
   user = db.query(User).filter(User.id == 1).first()
   user.name = "New Name"
   db.commit()

4. Delete:
   user = db.query(User).filter(User.id == 1).first()
   db.delete(user)
   db.commit()

IMPORTANT:
- Always use db.commit() to save changes!
- Always use db.close() or context manager!
- Use .first() to get only the first result!
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

# Import database setup
from database import get_db, Base, engine

# Import ORM model
from models import User

# Import Pydantic schemas
from schemas import UserCreate, UserUpdate, UserResponse

# Create router
router = APIRouter()

# ==================== ORM Operations ====================

@router.post("/users/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user in the database
    
    📝 What happens:
    1. Pydantic validates user data from request body
    2. Create User ORM object with validated data
    3. Add to database session (not saved yet!)
    4. Commit to save to database
    5. Return created user
    """
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    # Create User ORM object
    db_user = User(
        name=user.name,
        email=user.email,
        age=user.age
    )
    
    # Add to session (not saved yet!)
    db.add(db_user)
    
    # Commit to save (this is when SQL is executed!)
    db.commit()
    
    # Refresh to get auto-generated fields (id, created_at)
    db.refresh(db_user)
    
    return db_user


@router.get("/users/", response_model=List[UserResponse])
def read_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """
    Get all users with pagination
    
    📝 Query Parameters:
    - skip: Number of users to skip (for pagination)
    - limit: Maximum number of users to return
    
    📝 What happens:
    1. Query User model
    2. Apply offset (skip) and limit
    3. Return list of users
    """
    users = db.query(User).offset(skip).limit(limit).all()
    return users


@router.get("/users/{user_id}", response_model=UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db)):
    """
    Get a single user by ID
    
    📝 What happens:
    1. Query User with filter on id
    2. .first() gets first result or None
    3. If not found, raise 404 error
    """
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    return user


@router.put("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    """
    Update a user completely (PUT)
    
    📝 All fields must be provided
    """
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update all fields (all required in PUT)
    user.name = user_update.name  # type: ignore
    user.email = user_update.email  # type: ignore
    user.age = user_update.age  # type: ignore
    
    db.commit()
    db.refresh(user)
    return user


@router.patch("/users/{user_id}", response_model=UserResponse)
def partial_update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    """
    Update a user partially (PATCH)
    
    📝 Only provided fields are updated
    """
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update only provided fields
    update_data = user_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    return user


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """
    Delete a user
    
    📝 Returns 204 No Content on success
    """
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(user)
    db.commit()
    return None


# ==================== Educational Endpoints ====================

@router.get("/orm-examples")
def orm_examples(db: Session = Depends(get_db)):
    """
    Educational endpoint showing common ORM operations
    """
    return {
        "create": {
            "description": "Create a new user",
            "code": "user = User(name='John', email='john@example.com'); db.add(user); db.commit()"
        },
        "read_all": {
            "description": "Get all users",
            "code": "db.query(User).all()"
        },
        "read_filter": {
            "description": "Get users matching condition",
            "code": "db.query(User).filter(User.age >= 18).all()"
        },
        "read_one": {
            "description": "Get one user by ID",
            "code": "db.query(User).filter(User.id == 1).first()"
        },
        "update": {
            "description": "Update a user",
            "code": "user.name = 'New Name'; db.commit()"
        },
        "delete": {
            "description": "Delete a user",
            "code": "db.delete(user); db.commit()"
        }
    }


@router.get("/model-vs-table")
def model_vs_table_explanation():
    """
    Educational endpoint explaining Model vs Table
    """
    return {
        "model": {
            "what": "Python class",
            "world": "Python code",
            "example": "class User(Base): __tablename__ = 'users'"
        },
        "table": {
            "what": "Database structure",
            "world": "Database",
            "example": "CREATE TABLE users (id INTEGER PRIMARY KEY);"
        },
        "relationship": "SQLAlchemy automatically creates tables from models"
    }


# ==================== Initialize Database ====================

@router.on_event("startup")
def startup_event():
    """
    Create database tables on startup
    """
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created!")
