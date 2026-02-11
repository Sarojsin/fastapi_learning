from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class Student(BaseModel):
    name: str
    age: int

students = []
student_id = 1

@router.get("/students")
def get_students():
    return students

@router.post("/students")
def create_student(student: Student):
    global student_id
    new_student = {
        "id": student_id,
        "name": student.name,
        "age": student.age
    }
    students.append(new_student)
    student_id += 1
    return new_student

@router.put("/students/{id}")
def update_student(id: int, student: Student):
    for s in students:
        if s["id"] == id:
            s["name"] = student.name
            s["age"] = student.age
            return s
    return {"error": "Student not found"}

@router.delete("/students/{id}")
def delete_student(id: int):
    for s in students:
        if s["id"] == id:
            students.remove(s)
            return {"message": "Student deleted"}
    return {"error": "Student not found"}
