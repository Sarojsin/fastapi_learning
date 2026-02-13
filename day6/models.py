# Database Models
# Models define the structure of database tables

from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from database import Base


class Student(Base):
    """
    Student model - represents the students table in database
    
    Table name: students
    """
    __tablename__ = "students"
    
    # Primary key - unique identifier for each student
    id = Column(Integer, primary_key=True, index=True)
    
    # Student information
    name = Column(String(100), nullable=False)  # Cannot be empty
    email = Column(String(100), nullable=False, unique=True)  # Must be unique
    age = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Teacher(Base):
    """
    Teacher model - represents the teachers table in database
    """
    __tablename__ = "teachers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    subject = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Course(Base):
    """
    Course model - represents the courses table in database
    """
    __tablename__ = "courses"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(String(500))
    teacher_id = Column(Integer)  # Foreign key to teachers table
    created_at = Column(DateTime, default=datetime.utcnow)


# Summary of SQLAlchemy Column Types:
# - Integer: Whole numbers
# - String(n): Text with max length n
# - DateTime: Date and time
# - Boolean: True/False
# - Float: Decimal numbers
# - Text: Long text without max length
