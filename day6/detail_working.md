# FastAPI Request Flow - Detailed Explanation

This document explains how FastAPI handles HTTP requests from start to finish, with line-by-line execution flow.
---
## 🧠 Big Picture Overview

Think of FastAPI like a **reception desk in a school**:
```
Request arrives (student knocks)
    ↓
Reception checks route register
    ↓
Assigns a teacher (route function)
    ↓
Prepares materials (DB session, schemas)
    ↓
Teacher teaches (business logic)
    ↓
Reception formats answer
    ↓
Response sent back to client
```

---
## Part 1: GET /api/students

### Step 0: Server Already Running
```bash
uvicorn main:app
```

When you run this command:
- FastAPI app is loaded into memory
- All routes are registered
- Database connection system is ready

### Step 1: HTTP Request Arrives
```
Method: GET
Path: /api/students
```

### Step 2: FastAPI Matches the Route
**From `main.py`:**
```python
app.include_router(api_router, prefix="/api")
```

This means: `/api` + `/students` = `/api/students`

**From `routes.py`:**
```python
@router.get("/students", response_model=List[StudentResponse])
async def get_all_students(...):
```

✅ **Route matched** → FastAPI selects `get_all_students()`

### Step 3: Dependency Injection

Before your function runs, FastAPI executes:
```python
db: Session = Depends(get_db)
```

Which runs:
```python
def get_db():
    db = SessionLocal()   # Open DB connection
    yield db              # Give it to the route
```

Result: `db = <Session object>`

### Step 4: Route Function Executes
```python
students = db.query(Student).all()
```

**What happens:**
1. SQLAlchemy builds: `SELECT * FROM students;`
2. PostgreSQL executes the query
3. Result rows come back
4. Converted into ORM objects
5. Stored in `students` variable

### Step 5: Return Statement
```python
return students
```

Function ends here.

### Step 6: Response Model Processing

FastAPI sees `response_model=List[StudentResponse]` and:
1. Takes each Student ORM object
2. Converts to StudentResponse schema
3. Removes hidden fields
4. Converts to JSON

### Step 7: DB Session Closes
```python
finally:
    db.close()
```

> ⚠️ **Important**: Prevents memory leaks

### Step 8: Response Sent to Client

User receives JSON response with student data.
---

## 🔁 GET Flow Summary

```
Client → FastAPI → Router Match → get_db() → get_all_students()
       → db.query().all() → response_model → db.close() → Client
```

---

## Part 2: DELETE /api/students/{id}

### Example Request
```
DELETE /api/students/5
```

### Step 1: Request Arrives
```
Method: DELETE
Path: /api/students/5
```

FastAPI extracts: `student_id = 5`

### Step 2: Route Matching
```python
@router.delete("/students/{student_id}", status_code=204)
async def delete_student(student_id: int, db: Session = Depends(get_db)):
```

✅ Match found

### Step 3: Dependency Injection
```python
db = Depends(get_db)
# → db = SessionLocal()
```

### Step 4: Function Execution

**Line 1 – Fetch student:**
```python
student = db.query(Student).filter(Student.id == student_id).first()
# SQL: SELECT * FROM students WHERE id = 5;
```

**Line 2 – Check existence:**
```python
if student is None:
    raise HTTPException(status_code=404)
```
- If student doesn't exist → function stops, response sent immediately

**Line 3 – Delete object:**
```python
db.delete(student)
```
> ⚠️ Marks row for deletion, but NOT deleted yet

**Line 4 – Commit transaction:**
```python
db.commit()
# SQL: DELETE FROM students WHERE id = 5;
```
> 🔥 Data is permanently removed

**Line 5 – Return None:**
```python
return None
```
> Because `status_code=204` means "Success, but no content"

### Step 5: DB Session Closed
```python
db.close()
```

### Step 6: Response Sent
```
204 No Content
```

---

## 🔁 DELETE Flow Summary
```
Client → FastAPI → Router Match → get_db() → SELECT student
       → DELETE student → COMMIT → db.close() → Client
```

---

## Part 3: POST /api/students (CREATE)

### Example Request

```http
POST /api/students
Content-Type: application/json

{
  "name": "Rahul Sharma",
  "email": "rahul@gmail.com",
  "age": 21
}
```

### Step 1: Request Reaches FastAPI
```
Method: POST
Path: /api/students
Body: JSON data
```

### Step 2: Route Matching
```python
@router.post("/students", response_model=StudentResponse, status_code=201)
async def create_student(student: StudentCreate, db: Session = Depends(get_db)):
```

✅ Route matched → Function selected

### Step 3: Request Body Validation
```python
student: StudentCreate
```

**Internally, FastAPI:**
1. Reads JSON body
2. Passes to StudentCreate schema
3. Pydantic validates:
   - ✅ `name` exists?
   - ✅ `email` exists?
   - ✅ Correct types?
4. If invalid → returns 422
5. If valid → function continues

> 🔥 **Important**: Your function has NOT started yet!

### Step 4: Dependency Injection
```python
db = Depends(get_db)
# → db = SessionLocal()
```

DB session is ready.

### Step 5: Function Execution (Your Code)

**Line 1 – Email existence check:**
```python
existing_student = db.query(Student).filter(Student.email == student.email).first()
# SQL: SELECT * FROM students WHERE email='rahul@gmail.com';
```

**Line 2 – Raise error if email exists:**
```python
if existing_student:
    raise HTTPException(status_code=400)
```
> If email exists → execution stops, response sent immediately

**Line 3 – Create ORM object (NOT DB INSERT):**
```python
new_student = Student(
    name=student.name,
    email=student.email,
    age=student.age
)
```
> ⚠️ This is Python memory only, NOT database yet!

**Line 4 – Add to session:**
```python
db.add(new_student)
```
> "Prepare this object for insertion" → Still NOT saved

**Line 5 – Commit transaction:**
```python
db.commit()
# SQL: INSERT INTO students (name, email, age)
#      VALUES ('Rahul Sharma', 'rahul@gmail.com', 21);
```
> 🎉 Data saved permanently

**Line 6 – Refresh object:**
```python
db.refresh(new_student)
```
> Why? DB-generated ID and timestamps need to be loaded back

**Line 7 – Return response:**
```python
return new_student
```

### Step 6: Response Model Applied
```
Student ORM → StudentResponse → JSON
```

### Step 7: DB Session Closed
```python
db.close()
```

---

## 🔁 POST Flow Summary
```
Client → Route Match → Body Validation (Pydantic) → get_db()
       → Email check → Create ORM object → add()
       → commit() → refresh() → response_model → db.close() → Client
```

---

## Part 4: PUT /api/students/{id} (UPDATE)

### Example Request

```http
PUT /api/students/5
Content-Type: application/json

{
  "name": "Rahul Updated",
  "age": 22
}
```

### Step 1: Request Arrives
```
Method: PUT
Path: /api/students/5
```

FastAPI extracts: `student_id = 5`

### Step 2: Route Match
```python
@router.put("/students/{student_id}")
async def update_student(...)
```

✅ Match found

### Step 3: Request Body Validation

Pydantic validates `StudentUpdate` schema:
- All fields are optional
- Invalid type → 422 error

### Step 4: Dependency Injection

```python
db = get_db()
```

### Step 5: Function Execution

**Line 1 – Fetch existing student:**
```python
student = db.query(Student).filter(Student.id == student_id).first()
# SQL: SELECT * FROM students WHERE id=5;
```

**Line 2 – Not found check:**
```python
if student is None:
    raise HTTPException(status_code=404)
```
> Stops execution if student not found

**Line 3 – Update provided fields only:**
```python
if student_update.name is not None:
    student.name = student_update.name
```
> No SQL executed yet

**Line 4 – Email uniqueness check:**
```python
existing = db.query(Student).filter(
    Student.email == student_update.email,
    Student.id != student_id
).first()
```
> Prevents duplicate email for other users

**Line 5 – Assign new values:**
```python
student.email = student_update.email
student.age = student_update.age
```
> Still Python only

**Line 6 – Commit changes:**
```python
db.commit()
# SQL: UPDATE students
#      SET name='Rahul Updated', age=22
#      WHERE id=5;
```

**Line 7 – Refresh object:**
```python
db.refresh(student)
```
> Gets updated timestamps from DB

**Line 8 – Return updated student:**
```python
return student
```

### Step 6: Response Model Conversion
```
ORM → StudentResponse → JSON
```

### Step 7: DB Session Closed
```python
db.close()
```

---

## 🔁 PUT Flow Summary
```
Client → Route Match → Body Validation → get_db()
       → Fetch student → Update fields → commit()
       → refresh() → response_model → db.close() → Client
```

---

## 📊 POST vs PUT Comparison

| Feature | POST | PUT |
|---------|------|-----|
| Purpose | Create new | Update existing |
| ID needed | ❌ No | ✅ Yes |
| Inserts row | ✅ | ❌ |
| Updates row | ❌ | ✅ |
| Uses commit | ✅ | ✅ |

---

## 🏫 One-Line Teacher Summary

> **"FastAPI first matches the route, then prepares dependencies, runs business logic line-by-line, commits DB changes, formats the response using schemas, and finally cleans up resources."**
---

## 🎯 Why This Explanation Helps Students

Students often think:
> ❌ "FastAPI magically does everything"

Now they can see:
- ✅ Exact execution order
- ✅ Which line runs when
- ✅ Who controls DB lifecycle
- ✅ Why `Depends()` exists

---

## 🎓 Interview-Style Answer

**Q: How does FastAPI handle a POST request end-to-end?**

1. FastAPI receives the HTTP request (method, path, body)
2. Routes are matched against registered paths
3. Pydantic validates the request body against the schema
4. Dependencies are resolved (e.g., database session)
5. Route function executes with validated data
6. Database operations are performed (query, add, commit)
7. Response is formatted using the response_model
8. Resources are cleaned up (DB session closed)
9. JSON response is sent back to client

---

## ⚠️ Common Bugs Students Face

| Bug | Cause | Solution |
|-----|-------|----------|
| 404 Not Found | Route path doesn't match | Check route decorator path |
| 422 Validation Error | Missing/wrong fields | Check request body schema |
| 500 Internal Server Error | DB commit not called | Always call `db.commit()` |
| Memory leaks | DB session not closed | Use `Depends(get_db)` with `yield` |
| Duplicate records | No uniqueness check | Add validation before insert |

---
## 🧩 Visual Request Flow
```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT                                   │
└─────────────────────────┬───────────────────────────────────────┘
                          │ HTTP Request
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FASTAPI                                     │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────┐   │
│  │ Route Match │ → │ Dependencies │ → │ Route Function      │   │
│  └─────────────┘    └─────────────┘    │ (Business Logic)    │   │
│                                        └───────────┬───────────┘   │
└────────────────────────────────────────────────────┼───────────────┘
                                                     │
                                                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                       DATABASE                                   │
│  ┌───────────┐    ┌───────────┐    ┌───────────────────────┐   │
│  │   Query   │ ←  │  Commit   │ ←  │ ORM Object Operations │   │
│  └───────────┘    └───────────┘    └───────────────────────┘   │
└────────────────────────────────────────────────────┬──────────────┘
                                                     │
                                                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                      RESPONSE                                   │
│         JSON → Response Model → Status Code                    │
└─────────────────────────────────────────────────────────────────┘
```
