from fastapi import APIRouter

router = APIRouter()

@router.get("/students")
def get_students():
    db_students=[
        {"id": 1, "name": "saroj"},
        {"id": 2, "name": " sagar"}
    ]
    return db_students

@router.get("/teachers")
def get_teachers():
    return [
        {"id": 1, "name": "Mr.thapa"},
        {"id": 2, "name": "Ms.dhami"}
    ]
