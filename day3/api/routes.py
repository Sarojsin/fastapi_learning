from fastapi import APIRouter

router = APIRouter()

students = [
    {"id": 1, "name": "Ram"},
    {"id": 2, "name": "Sita"},
    {"id": 3, "name": "Hari"},
]

@router.get("/students")
def get_students(page: int = 1, limit: int = 2):
    start = (page - 1) * limit
    end = start + limit
    return students[start:end]

@router.get("/students/{student_id}")
def get_student(student_id: int):
    for s in students:
        if s["id"] == student_id:
            return s
    return {"error": "Student not found"}
