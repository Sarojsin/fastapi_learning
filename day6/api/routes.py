"""
API Routes - Day 6
==================

CRUD operations for Student management using:
- SQLAlchemy ORM (database/models.py)
- Pydantic Schemas (schemas.py)
- PostgreSQL Database
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import Student
from schemas import StudentCreate, StudentUpdate, StudentResponse

router = APIRouter()


# ================== Student CRUD Operations ==================

@router.get("/students", response_model=List[StudentResponse])#When someone sends a GET request to /students, run the function below.
async def get_all_students(db: Session = Depends(get_db)):# return gar cha db = <Session object>
    """
    GET all students from the database.
    
    Equivalent SQL:
        SELECT * FROM students;
    
    ORM Query:
        db.query(Student).all()
    """
    students = db.query(Student).all()# mathi ko line execute   huncha SQLAlchemy builds SQL:
# SELECT * FROM students;
# PostgreSQL executes it
# Result rows come back
# Converted into ORM objects
# Stored in students
    return students


@router.get("/students/{student_id}", response_model=StudentResponse)
async def get_student_by_id(student_id: int, db: Session = Depends(get_db)):
    """
    GET a single student by ID.
    
    Equivalent SQL:
        SELECT * FROM students WHERE id = {student_id};
    """
    student = db.query(Student).filter(Student.id == student_id).first()
    
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    
    return student


@router.post("/students", response_model=StudentResponse, status_code=201)
async def create_student(student: StudentCreate, db: Session = Depends(get_db)):
    """
    CREATE a new student.
    
    Steps:
    1. Create Student ORM model instance
    2. Add to database session
    3. Commit the transaction
    4. Refresh to get generated fields (id, created_at)
    
    Equivalent SQL:
        INSERT INTO students (name, email, age)
        VALUES ('{name}', '{email}', {age});

     **what actually happens:
        JSON body is read
        Passed to StudentCreate schema
        Pydantic checks:
        name exists?
        email exists?
        correct types?
        If invalid ❌ → FastAPI returns 422
        If valid ✅ → function continues
    """
    # Check if email already exists
    existing_student = db.query(Student).filter(Student.email == student.email).first()
    if existing_student:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new student instance
    new_student = Student(#This is ONLY Python memory, NOT database.
        name=student.name,
        email=student.email,
        age=student.age
    )
    
    # Add and commit to database
    db.add(new_student)#Prepare this object for insertion”
    db.commit()
    db.refresh(new_student)  # Get the auto-generated id and timestamps
    
    return new_student


@router.put("/students/{student_id}", response_model=StudentResponse)
async def update_student(
    student_id: int, 
    student_update: StudentUpdate, 
    db: Session = Depends(get_db)
):
    """
    UPDATE an existing student.
    
    Equivalent SQL:
        UPDATE students 
        SET name = '{name}', email = '{email}', age = {age}
        WHERE id = {student_id};
    """
    student = db.query(Student).filter(Student.id == student_id).first()
    
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Update fields if provided
    if student_update.name is not None:
        student.name = student_update.name
    if student_update.email is not None:
        # Check if new email is taken by another student
        existing = db.query(Student).filter(
            Student.email == student_update.email, 
            Student.id != student_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")
        student.email = student_update.email
    if student_update.age is not None:
        student.age = student_update.age
    
    db.commit()
    db.refresh(student)
    
    return student


@router.delete("/students/{student_id}", status_code=204)
async def delete_student(student_id: int, db: Session = Depends(get_db)):
    """
    DELETE a student by ID.
    
    Equivalent SQL:
        DELETE FROM students WHERE id = {student_id};
    
    Returns: 204 No Content (successful deletion)
    """
    student = db.query(Student).filter(Student.id == student_id).first()
    
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    
    db.delete(student)
    db.commit()
    
    return None


# ================== Database Query Examples ==================

@router.get("/students/filter/age/{min_age}")
async def get_students_by_min_age(min_age: int, db: Session = Depends(get_db)):
    """
    Filter students by minimum age.
    
    Equivalent SQL:
        SELECT * FROM students WHERE age >= {min_age};
    
    ORM Query:
        db.query(Student).filter(Student.age >= min_age).all()
    """
    students = db.query(Student).filter(Student.age >= min_age).all()
    return students


@router.get("/students/count")
async def count_students(db: Session = Depends(get_db)):
    """
    Count total students.
    
    Equivalent SQL:
        SELECT COUNT(*) FROM students;
    """
    count = db.query(Student).count()
    return {"total_students": count}


# ================== SQL vs ORM Syntax Comparison ==================

@router.get("/sql-comparison")
async def sql_comparison(db: Session = Depends(get_db)):
    """
    SQL vs ORM Syntax Comparison:
    
    1. SELECT ALL:
       SQL: SELECT * FROM students;
       ORM: db.query(Student).all()
    
    2. SELECT WITH FILTER:
       SQL: SELECT * FROM students WHERE age > 18;
       ORM: db.query(Student).filter(Student.age > 18).all()
    
    3. SELECT SINGLE:
       SQL: SELECT * FROM students WHERE id = 1;
       ORM: db.query(Student).filter(Student.id == 1).first()
    
    4. INSERT:
       SQL: INSERT INTO students (name, age) VALUES ('John', 20);
       ORM: db.add(Student(name='John', age=20)); db.commit()
    
    5. UPDATE:
       SQL: UPDATE students SET age = 21 WHERE id = 1;
       ORM: student.age = 21; db.commit()
    
    6. DELETE:
       SQL: DELETE FROM students WHERE id = 1;
       ORM: db.delete(student); db.commit()
    """
    return {
        "operation": "SQL vs ORM Comparison",
        "select_all": {
            "sql": "SELECT * FROM students;",
            "orm": "db.query(Student).all()"
        },
        "select_filter": {
            "sql": "SELECT * FROM students WHERE age > 18;",
            "orm": "db.query(Student).filter(Student.age > 18).all()"
        },
        "select_single": {
            "sql": "SELECT * FROM students WHERE id = 1;",
            "orm": "db.query(Student).filter(Student.id == 1).first()"
        },
        "insert": {
            "sql": "INSERT INTO students (name, age) VALUES ('John', 20);",
            "orm": "db.add(Student(name='John', age=20)); db.commit()"
        },
        "update": {
            "sql": "UPDATE students SET age = 21 WHERE id = 1;",
            "orm": "student.age = 21; db.commit()"
        },
        "delete": {
            "sql": "DELETE FROM students WHERE id = 1;",
            "orm": "db.delete(student); db.commit()"
        }
    }
