"""
Day 7: SQLAlchemy ORM - Pydantic Schemas
=========================================

📚 KEY CONCEPTS FOR STUDENTS:

SCHEMA vs MODEL:
- Schema: Defines API data format (Pydantic)
- Model: Defines database table structure (SQLAlchemy)
- They are DIFFERENT but related!

WHY USE SCHEMAS?
1. Validate incoming API data
2. Define what data the API accepts/returns
3. Protect sensitive data (don't expose database internals)
4. Document API structure

SCHEMA WORKFLOW:
    API Request          Schema               Model              Database
    ┌─────────┐          ┌─────────┐          ┌─────────┐        ┌─────────┐
    │  JSON   │ ──────►  │ Validate│ ──────►  │   ORM   │ ─────► │   DB    │
    │         │   Body   │   Data  │          │  Model  │        │         │
    └─────────┘          └─────────┘          └─────────┘        └─────────┘
                              │                   │
                              ▼                   ▼
                         400 Error           Database Error
                         (Bad Request)       (SQL issues)
"""

from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


# ==================== User Schemas ====================

class UserBase(BaseModel):
    """
    Base schema - common fields for all user schemas
    Used as a parent class, not directly in API endpoints
    """
    name: str
    email: EmailStr  # Validates email format
    age: Optional[int] = None  # Optional field, defaults to None


class UserCreate(UserBase):
    """
    Schema for creating a new user
    - Validates incoming data from API requests
    - Does NOT include read-only fields like id, created_at
    """
    pass  # Inherits all fields from UserBase


class UserUpdate(BaseModel):
    """
    Schema for updating a user
    - All fields are optional (partial update)
    - Only provided fields will be updated
    """
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    age: Optional[int] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """
    Schema for user response
    - Includes all fields that should be returned to client
    - Converts database fields to JSON-serializable format
    """
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        """Pydantic config to allow ORM model to be passed directly"""
        from_attributes = True


class UserInDB(UserResponse):
    """
    Schema for user stored in database
    - Same as response (SQLAlchemy handles DB representation)
    - Useful for internal use
    """
    pass


# ==================== Helper Functions ====================

def user_response_from_orm(user) -> dict:#-> this is for type hinting which indicates the function returns a dictionary
    """
    Convert ORM User object to response dictionary
    
    Example:
        # ORM User object (from database)
        user = db.query(User).first()
        
        # Convert to response format
        response = user_response_from_orm(user)
    """
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "age": user.age,
        "is_active": user.is_active,
        "created_at": user.created_at,
        "updated_at": user.updated_at
    }


# ==================== Explanation for Students ====================

"""
📚 SCHEMA EXAMPLES:

1. UserCreate (Input Validation):
   POST /users with body:
   {
       "name": "John Doe",
       "email": "john@example.com",
       "age": 25
   }
   
   Pydantic validates:
   - name is a string ✓
   - email is valid email format ✓
   - age is an integer ✓
   - All required fields present ✓

2. UserResponse (Output Format):
   API returns:
   {
       "id": 1,
       "name": "John Doe",
       "email": "john@example.com",
       "age": 25,
       "is_active": true,
       "created_at": "2024-01-15T10:30:00",
       "updated_at": "2024-01-15T10:30:00"
   }

3. UserUpdate (Partial Update):
   PATCH /users/1 with body:
   {
       "name": "John Updated"
   }
   
   Only name is updated, other fields unchanged.

📚 WHY SEPARATE SCHEMAS?

1. Security: Don't expose internal DB fields in API
2. Validation: Different validation rules for input vs output
3. Flexibility: Easy to add fields without breaking DB
4. Documentation: Schemas auto-generate OpenAPI docs
"""
