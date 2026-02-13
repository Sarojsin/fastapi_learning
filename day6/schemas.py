# Pydantic Schemas
# Schemas define the structure of data for API requests and responses

from pydantic import BaseModel
from datetime import datetime
from typing import Optional
 

# ================== Student Schemas ==================

class StudentBase(BaseModel):
    """Base schema with common fields"""
    name: str
    email: str          
    age: Optional[int] = None


class StudentCreate(StudentBase):
    """Schema for creating a new student"""
    pass


class StudentUpdate(BaseModel):
    """Schema for updating a student - all fields optional"""
    name: Optional[str] = None
    email: Optional[str] = None
    age: Optional[int] = None


class StudentResponse(StudentBase):
    """Schema for student response - includes id and timestamps"""
    id: int
    # created_at: datetime
    # updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True  # Allows reading from ORM models

# Which schema should we use for login?=New schema — not StudentBase
#One schema = one purpose Login has a different purpose than create / update / response.“You don’t fill your full biodata just to enter the college gate.”
# ================== Teacher Schemas ==================

class TeacherBase(BaseModel):
    """Base schema for teacher"""
    name: str
    subject: str
    email: str


class TeacherCreate(TeacherBase):
    """Schema for creating a new teacher"""
    pass


class TeacherResponse(TeacherBase):
    """Schema for teacher response"""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# ================== Course Schemas ==================

class CourseBase(BaseModel):
    """Base schema for course"""
    title: str
    description: Optional[str] = None
    teacher_id: Optional[int] = None


class CourseCreate(CourseBase):
    """Schema for creating a new course"""
    pass


class CourseResponse(CourseBase):
    """Schema for course response"""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# ================== SQL vs ORM vs Pydantic ==================
#
# SQL (Raw):
#   - Direct database queries
#   - Maximum control
#   - Database-specific syntax
#
# ORM (SQLAlchemy Models):
#   - Python classes representing database tables
#   - Database-agnostic
#   - Type safety
#
# Pydantic Schemas:
#   - Data validation
#   - API request/response format
#   - Documentation (OpenAPI)
#
# Data Flow:
#   API Request (JSON) -> Pydantic Schema (Validation) -> ORM Model (Database) -> SQL (Storage)
