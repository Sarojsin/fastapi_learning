from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from typing import Optional, List
from datetime import datetime
from enum import Enum

router = APIRouter()

# ============ PYDANTIC MODEL DEFINITIONS ============

class Address(BaseModel):
    """Nested Pydantic model for address"""
    street: str
    city: str
    state: str
    zip_code: str
    country: str = "USA"


class Grade(str, Enum):
    """Enum for student grades"""
    FRESHMAN = "freshman"
    SOPHOMORE = "sophomore"
    JUNIOR = "junior"
    SENIOR = "senior"


class StudentRequest(BaseModel):
    """Deep dive into Pydantic - Request model with advanced validation"""
    
    # Basic fields with Field() for additional metadata
    name: str = Field(..., min_length=2, max_length=100, description="Student's full name")
    age: int = Field(..., ge=5, le=100, description="Student's age")
    email: EmailStr = Field(..., description="Valid email address")
    
    # Optional field with default value
    address: Optional[Address] = Field(default=None, description="Student's address")
    
    # List of items
    courses: List[str] = Field(default_factory=list, description="Enrolled courses")
    
    # Enum field
    grade: Optional[Grade] = Field(default=None, description="Academic grade level")
    
    # Datetime field
    enrollment_date: datetime = Field(default_factory=datetime.now, description="Date of enrollment")
    
    # Boolean with description
    is_active: bool = Field(default=True, description="Whether student is currently active")
    
    # Field validation using field_validator
    @field_validator('name')
    @classmethod
    def name_must_contain_space(cls, v):
        if ' ' not in v:
            raise ValueError('Name must contain at least one space')
        return v.title()
    
    @field_validator('courses')
    @classmethod
    def courses_must_not_be_empty(cls, v):
        if not v:
            raise ValueError('At least one course must be enrolled')
        return v
    
    # Model configuration
    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "name": "John Doe",
                "age": 20,
                "email": "john.doe@example.com",
                "address": {
                    "street": "123 Main St",
                    "city": "Boston",
                    "state": "MA",
                    "zip_code": "02101"
                },
                "courses": ["Math", "Physics", "Computer Science"],
                "grade": "sophomore"
            }
        }
    )


class StudentResponse(BaseModel):
    """Response model - what gets returned to the client"""
    id: int
    name: str
    age: int
    email: EmailStr
    grade: Optional[Grade] = None
    is_active: bool
    
    model_config = ConfigDict(from_attributes=True)


class UpdateStudentRequest(BaseModel):
    """Partial update model - all fields are optional"""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    age: Optional[int] = Field(None, ge=5, le=100)
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Jane Doe",
                "age": 21
            }
        }
    )


# In-memory database simulation
students_db = []
student_id_counter = 1


# ============ ROUTES ============

@router.get("/students", response_model=List[StudentResponse])
def get_students():
    """Get all students from the database"""
    return students_db


@router.get("/students/{student_id}", response_model=StudentResponse)
def get_student(student_id: int):
    """Get a specific student by ID"""
    for student in students_db:
        if student.id == student_id:
            return student
    raise HTTPException(status_code=404, detail="Student not found")


@router.post("/students", response_model=StudentResponse, status_code=201)
def create_student(student: StudentRequest):
    """Create a new student with full request body validation"""
    global student_id_counter
    
    # Create response object
    student_response = StudentResponse(
        id=student_id_counter,
        name=student.name,
        age=student.age,
        email=student.email,
        grade=student.grade,
        is_active=student.is_active
    )
    
    students_db.append(student_response)
    student_id_counter += 1
    
    return student_response


@router.put("/students/{student_id}", response_model=StudentResponse)
def update_student(student_id: int, student_update: UpdateStudentRequest):
    """Update a student with partial request body"""
    for i, student in enumerate(students_db):
        if student.id == student_id:
            # Update only provided fields
            update_data = student_update.model_dump(exclude_unset=True)
            updated_student = student.model_copy(update=update_data)
            students_db[i] = updated_student
            return updated_student
    
    raise HTTPException(status_code=404, detail="Student not found")


@router.patch("/students/{student_id}", response_model=StudentResponse)
def patch_student(student_id: int, student_patch: UpdateStudentRequest):
    """Patch a student - alternative partial update"""
    return update_student(student_id, student_patch)


@router.delete("/students/{student_id}", status_code=204)
def delete_student(student_id: int):
    """Delete a student"""
    for i, student in enumerate(students_db):
        if student.id == student_id:
            del students_db[i]
            return None
    
    raise HTTPException(status_code=404, detail="Student not found")


# ============ ADVANCED REQUEST BODY EXAMPLES ============

@router.post("/students/bulk")
def create_bulk_students(students: List[StudentRequest]):
    """Create multiple students at once"""
    global student_id_counter
    
    created_students = []
    for student in students:
        student_response = StudentResponse(
            id=student_id_counter,
            name=student.name,
            age=student.age,
            email=student.email,
            grade=student.grade,
            is_active=student.is_active
        )
        students_db.append(student_response)
        created_students.append(student_response)
        student_id_counter += 1
    
    return {"message": f"Created {len(created_students)} students", "students": created_students}


@router.post("/students/with-address")
def create_student_with_address(student: StudentRequest):
    """Create student demonstrating nested model parsing"""
    global student_id_counter
    
    # Access nested address data
    if student.address:
        full_address = f"{student.address.street}, {student.address.city}, {student.address.state} {student.address.zip_code}"
    student_response = StudentResponse(
        id=student_id_counter,
        name=student.name,
        age=student.age,
        email=student.email,
        grade=student.grade,
        is_active=student.is_active
    )
    
    students_db.append(student_response)
    student_id_counter += 1
    return student_response
