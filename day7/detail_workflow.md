# Day 7: SQLAlchemy ORM - Route Workflow

This document explains the complete workflow for each User API endpoint.

---

## Table of Contents
1. [POST /api/users/ - Create User](#post-apiusers---create-user)
2. [GET /api/users/ - List Users](#get-apiusers---list-users)
3. [GET /api/users/{user_id} - Get User by ID](#get-apiusersuser_id---get-user-by-id)
4. [PUT /api/users/{user_id} - Update User (Full)](#put-apiusersuser_id---update-user-full)
5. [PATCH /api/users/{user_id} - Update User (Partial)](#patch-apiusersuser_id---update-user-partial)
6. [DELETE /api/users/{user_id} - Delete User](#delete-apiusersuser_id---delete-user)

---

## POST /api/users/ - Create User

### Purpose
Create a new user in the database.

### Request Flow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Client    │     │   FastAPI   │     │   Pydantic  │     │  SQLAlchemy │
│             │     │             │     │   Schema    │     │    ORM      │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                   │                   │
       │  POST /users      │                   │                   │
       │  Body: {         │                   │                   │
       │    name: "John", │                   │                   │
       │    email: "...", │                   │                   │
       │    age: 25       │                   │                   │
       │  }               │                   │                   │
       │─────────────────►│                   │                   │
       │                   │                   │                   │
       │                   │  Validate JSON   │                   │
       │                   │  against UserCreate│                  │
       │                   │───────────────────│                   │
       │                   │                   │                   │
       │                   │  Validated data  │                   │
       │                   │  name="John"     │                   │
       │                   │  email="..."      │                   │
       │                   │  age=25           │                   │
       │                   │◄──────────────────│                   │
       │                   │                   │                   │
       │                   │  Check if email   │                   │
       │                   │  already exists   │                   │
       │                   │───────────────────────────────►      │
       │                   │                   │                   │
       │                   │  Email found?    │                   │
       │                   │◄───────────────────────────────►      │
       │                   │                   │                   │
       │   If exists:      │                   │                   │
       │   400 Error       │                   │                   │
       │◄──────────────────│                   │                   │
       │                   │                   │                   │
       │                   │  Create User obj │                   │
       │                   │  user = User(     │                   │
       │                   │    name="John",   │                   │
       │                   │    email="...",   │                   │
       │                   │    age=25         │                   │
       │                   │  )                │                   │
       │                   │──────────────────►│                   │
       │                   │                   │  db.add(user)     │
       │                   │                   │──────────────────►│
       │                   │                   │                   │
       │                   │                   │  db.commit()      │
       │                   │                   │──────────────────►│
       │                   │                   │   INSERT INTO     │
       │                   │                   │   users...        │
       │                   │                   │◄──────────────────│
       │                   │                   │                   │
       │                   │                   │  db.refresh(user) │
       │                   │                   │──────────────────►│
       │                   │                   │                   │
       │                   │  User created     │                   │
       │                   │  id=1, created_at│   ◄───────────────│
       │                   │  =...            │                   │
       │                   │◄──────────────────│                   │
       │                   │                   │                   │
       │  201 Created      │                   │                   │
       │  Body: {         │                   │                   │
       │    id: 1,        │                   │                   │
       │    name: "John", │                   │                   │
       │    ...          │                   │                   │
       │  }               │                   │                   │
       │◄──────────────────│                   │                   │
       │                   │                   │                   │
```

### Code Implementation

```python
@router.post("/users/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user in the database
    """
    # Step 1: Check if email already exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Step 2: Create User ORM object
    db_user = User(
        name=user.name,
        email=user.email,
        age=user.age
    )
    
    # Step 3: Add to session (not saved yet!)
    db.add(db_user)
    
    # Step 4: Commit to save (executes INSERT SQL)
    db.commit()
    
    # Step 5: Refresh to get auto-generated fields
    db.refresh(db_user)
    
    # Step 6: Return created user
    return db_user
```

### Request Example

```bash
curl -X POST "http://localhost:8000/api/users/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "age": 25
  }'
```

### Response Example

```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "age": 25,
  "is_active": true,
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:00"
}
```

---

## GET /api/users/ - List Users

### Purpose
Retrieve all users from the database with pagination.

### Request Flow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Client    │     │   FastAPI   │     │  SQLAlchemy │     │  Database   │
│             │     │             │     │    ORM      │     │             │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                   │                   │
       │  GET /users?      │                   │                   │
       │  skip=0&limit=10 │                   │                   │
       │─────────────────►│                   │                   │
       │                   │                   │                   │
       │                   │  Query all users  │                   │
       │                   │  with pagination  │                   │
       │                   │──────────────────►│                   │
       │                   │                   │                   │
       │                   │                   │  SELECT * FROM    │
       │                   │                   │  users LIMIT 10  │
       │                   │                   │  OFFSET 0         │
       │                   │                   │──────────────────►│
       │                   │                   │                   │
       │                   │                   │  List of users    │
       │                   │                   │  [{id:1, name:"J"},│
       │                   │                   │   {id:2, name:"A"}]│
       │                   │                   │◄──────────────────│
       │                   │                   │                   │
       │                   │  Return user list │                   │
       │                   │◄──────────────────│                   │
       │                   │                   │                   │
       │  200 OK          │                   │                   │
       │  Body: [{...}]   │                   │                   │
       │◄──────────────────│                   │                   │
```

### Code Implementation

```python
@router.get("/users/", response_model=List[UserResponse])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Get all users with pagination
    
    Query Parameters:
    - skip: Number of users to skip (default: 0)
    - limit: Maximum users to return (default: 100)
    """
    # Step 1: Query User model
    # Step 2: Apply offset (skip) for pagination
    # Step 3: Apply limit for pagination
    # Step 4: Get all results as list
    users = db.query(User).offset(skip).limit(limit).all()
    return users
```

### Request Examples

```bash
# Get first 10 users
curl "http://localhost:8000/api/users/?skip=0&limit=10"

# Get next 10 users (page 2)
curl "http://localhost:8000/api/users/?skip=10&limit=10"

# Get all users
curl "http://localhost:8000/api/users/"
```

### Response Example

```json
[
  {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "age": 25,
    "is_active": true,
    "created_at": "2024-01-15T10:30:00",
    "updated_at": "2024-01-15T10:30:00"
  },
  {
    "id": 2,
    "name": "Jane Smith",
    "email": "jane@example.com",
    "age": 22,
    "is_active": true,
    "created_at": "2024-01-16T14:20:00",
    "updated_at": "2024-01-16T14:20:00"
  }
]
```

---

## GET /api/users/{user_id} - Get User by ID

### Purpose
Retrieve a single user by their ID.

### Request Flow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Client    │     │   FastAPI   │     │  SQLAlchemy │     │  Database   │
│             │     │             │     │    ORM      │     │             │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                   │                   │
       │  GET /users/1     │                   │                   │
       │─────────────────►│                   │                   │
       │                   │                   │                   │
       │                   │  Query user with  │                   │
       │                   │  filter on id=1   │                   │
       │                   │──────────────────►│                   │
       │                   │                   │                   │
       │                   │                   │  SELECT * FROM    │
       │                   │                   │  users WHERE     │
       │                   │                   │  id = 1 LIMIT 1 │
       │                   │                   │──────────────────►│
       │                   │                   │                   │
       │                   │                   │  User found?      │
       │                   │                   │  [{id:1, ...}]   │
       │                   │                   │◄──────────────────│
       │                   │                   │                   │
       │   User not found: │                   │                   │
       │   404 Error      │                   │                   │
       │◄──────────────────│                   │                   │
       │                   │                   │                   │
       │                   │  User exists      │                   │
       │                   │  Return user      │                   │
       │                   │◄──────────────────│                   │
       │                   │                   │                   │
       │  200 OK          │                   │                   │
       │  Body: {...}      │                   │                   │
       │◄──────────────────│                   │                   │
```

### Code Implementation

```python
@router.get("/users/{user_id}", response_model=UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db)):
    """
    Get a single user by ID
    
    Path Parameter:
    - user_id: The ID of the user to retrieve
    """
    # Step 1: Query User with filter on id
    # Step 2: Use .first() to get first result or None
    user = db.query(User).filter(User.id == user_id).first()
    
    # Step 3: If not found, raise 404 error
    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    
    # Step 4: Return user
    return user
```

### Request Examples

```bash
# Get user with ID 1
curl "http://localhost:8000/api/users/1"

# Get user with ID 999 (doesn't exist)
curl "http://localhost:8000/api/users/999"
```

### Response Examples

```json
// Success (200 OK)
{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "age": 25,
  "is_active": true,
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:00"
}

// Not Found (404)
{
  "detail": "User not found"
}
```

---

## PUT /api/users/{user_id} - Update User (Full)

### Purpose
Completely replace a user's data (all fields required).

### Request Flow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Client    │     │   FastAPI   │     │  SQLAlchemy │     │  Database   │
│             │     │             │     │    ORM      │     │             │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                   │                   │
       │  PUT /users/1     │                   │                   │
       │  Body: {         │                   │                   │
       │    name: "New",  │                   │                   │
       │    email: "new@",│                   │                   │
       │    age: 30      │                   │                   │
       │  }               │                   │                   │
       │─────────────────►│                   │                   │
       │                   │                   │                   │
       │                   │  Find user by ID │                   │
       │                   │──────────────────►│                   │
       │                   │                   │                   │
       │                   │                   │  SELECT * FROM    │
       │                   │                   │  users WHERE id=1 │
       │                   │                   │──────────────────►│
       │                   │                   │                   │
       │                   │  User not found?  │                   │
       │                   │◄──────────────────│                   │
       │   404 Error      │                   │                   │
       │◄──────────────────│                   │                   │
       │                   │                   │                   │
       │                   │  Update all fields│                   │
       │                   │  user.name = "New"│                   │
       │                   │  user.email = "new@"│                  │
       │                   │  user.age = 30    │                   │
       │                   │──────────────────►│                   │
       │                   │                   │                   │
       │                   │                   │  db.commit()      │
       │                   │                   │──────────────────►│
       │                   │                   │   UPDATE users... │
       │                   │                   │◄──────────────────│
       │                   │                   │                   │
       │                   │                   │  db.refresh(user) │
       │                   │                   │──────────────────►│
       │                   │                   │                   │
       │                   │  Return updated   │                   │
       │                   │  user            │                   │
       │                   │◄──────────────────│                   │
       │                   │                   │                   │
       │  200 OK          │                   │                   │
       │  Body: {         │                   │                   │
       │    name: "New",  │                   │                   │
       │    ...          │                   │                   │
       │  }               │                   │                   │
       │◄──────────────────│                   │                   │
```

### Code Implementation

```python
@router.put("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    """
    Update a user completely (PUT)
    All fields must be provided!
    """
    # Step 1: Find user by ID
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Step 2: Update all fields (all required in PUT)
    user.name = user_update.name
    user.email = user_update.email
    user.age = user_update.age
    
    # Step 3: Commit changes
    db.commit()
    
    # Step 4: Refresh to get updated values
    db.refresh(user)
    
    return user
```

### Request Example

```bash
curl -X PUT "http://localhost:8000/api/users/1" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Updated",
    "email": "john.updated@example.com",
    "age": 30
  }'
```

### Response Example

```json
{
  "id": 1,
  "name": "John Updated",
  "email": "john.updated@example.com",
  "age": 30,
  "is_active": true,
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-16T15:00:00"
}
```

---

## PATCH /api/users/{user_id} - Update User (Partial)

### Purpose
Partially update a user's data (only provided fields).

### Request Flow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Client    │     │   FastAPI   │     │  SQLAlchemy │     │  Database   │
│             │     │             │     │    ORM      │     │             │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                   │                   │
       │  PATCH /users/1   │                   │                   │
       │  Body: {         │                   │                   │
       │    name: "New"   │                   │                   │
       │  }               │                   │                   │
       │─────────────────►│                   │                   │
       │                   │                   │                   │
       │                   │  Find user by ID │                   │
       │                   │──────────────────►│                   │
       │                   │                   │                   │
       │   404 Error      │                   │                   │
       │◄──────────────────│                   │                   │
       │                   │                   │                   │
       │                   │  User exists -   │                   │
       │                   │  Update only     │                   │
       │                   │  provided fields │                   │
       │                   │──────────────────►│                   │
       │                   │                   │                   │
       │                   │  .model_dump(     │                   │
       │                   │    exclude_unset=│                   │
       │                   │    True)         │                   │
       │                   │  For each field: │                   │
       │                   │    setattr(      │                   │
       │                   │      user,       │                   │
       │                   │      field,      │                   │
       │                   │      value)      │                   │
       │                   │──────────────────►│                   │
       │                   │                   │                   │
       │                   │                   │  db.commit()      │
       │                   │                   │──────────────────►│
       │                   │                   │   UPDATE users    │
       │                   │                   │   SET name=...    │
       │                   │                   │   WHERE id=1      │
       │                   │                   │◄──────────────────│
       │                   │                   │                   │
       │                   │  Return updated   │                   │
       │                   │  user            │                   │
       │                   │◄──────────────────│                   │
       │                   │                   │                   │
       │  200 OK          │                   │                   │
       │  Body: {         │                   │                   │
       │    name: "New", │                   │                   │
       │    ...          │                   │                   │
       │  }               │                   │                   │
       │◄──────────────────│                   │                   │
```

### Code Implementation

```python
@router.patch("/users/{user_id}", response_model=UserResponse)
def partial_update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    """
    Update a user partially (PATCH)
    Only provided fields are updated!
    """
    # Step 1: Find user by ID
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Step 2: Get only provided fields (exclude_unset=True)
    update_data = user_update.model_dump(exclude_unset=True)
    
    # Step 3: Update only provided fields
    for field, value in update_data.items():
        setattr(user, field, value)
    
    # Step 4: Commit changes
    db.commit()
    
    # Step 5: Refresh
    db.refresh(user)
    
    return user
```

### Request Examples

```bash
# Update only name
curl -X PATCH "http://localhost:8000/api/users/1" \
  -H "Content-Type: application/json" \
  -d '{"name": "New Name"}'

# Update only email
curl -X PATCH "http://localhost:8000/api/users/1" \
  -H "Content-Type: application/json" \
  -d '{"email": "new.email@example.com"}'

# Update age and is_active
curl -X PATCH "http://localhost:8000/api/users/1" \
  -H "Content-Type: application/json" \
  -d '{"age": 26, "is_active": false}'
```

### Response Example

```json
{
  "id": 1,
  "name": "New Name",
  "email": "john@example.com",
  "age": 25,
  "is_active": true,
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-16T15:00:00"
}
```

---

## DELETE /api/users/{user_id} - Delete User

### Purpose
Remove a user from the database.

### Request Flow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Client    │     │   FastAPI   │     │  SQLAlchemy │     │  Database   │
│             │     │             │     │    ORM      │     │             │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                   │                   │
       │  DELETE /users/1  │                   │                   │
       │─────────────────►│                   │                   │
       │                   │                   │                   │
       │                   │  Find user by ID │                   │
       │                   │──────────────────►│                   │
       │                   │                   │                   │
       │                   │                   │  SELECT * FROM    │
       │                   │                   │  users WHERE id=1 │
       │                   │                   │──────────────────►│
       │                   │                   │                   │
       │                   │  User not found?  │                   │
       │                   │◄──────────────────│                   │
       │   404 Error      │                   │                   │
       │◄──────────────────│                   │                   │
       │                   │                   │                   │
       │                   │  User exists -   │                   │
       │                   │  Delete it        │                   │
       │                   │──────────────────►│                   │
       │                   │                   │                   │
       │                   │                   │  db.delete(user)  │
       │                   │                   │──────────────────►│
       │                   │                   │                   │
       │                   │                   │  db.commit()      │
       │                   │                   │──────────────────►│
       │                   │                   │   DELETE FROM     │
       │                   │                   │   users WHERE     │
       │                   │                   │   id=1            │
       │                   │                   │◄──────────────────│
       │                   │                   │                   │
       │                   │  Deletion         │                   │
       │                   │  successful      │                   │
       │                   │◄──────────────────│                   │
       │                   │                   │                   │
       │  204 No Content   │                   │                   │
       │◄──────────────────│                   │                   │
```

### Code Implementation

```python
@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """
    Delete a user by ID
    
    Returns:
    - 204 No Content on success
    - 404 Not Found if user doesn't exist
    """
    # Step 1: Find user by ID
    user = db.query(User).filter(User.id == user_id).first()
    
    # Step 2: If not found, raise 404 error
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Step 3: Delete the user
    db.delete(user)
    
    # Step 4: Commit to save (executes DELETE SQL)
    db.commit()
    
    # Step 5: Return 204 No Content
    return None
```

### Request Examples

```bash
# Delete user with ID 1
curl -X DELETE "http://localhost:8000/api/users/1"

# Delete user with ID 999 (doesn't exist)
curl -X DELETE "http://localhost:8000/api/users/999"
```

### Response Examples

```json
// Success (204 No Content)
// No body returned

// Not Found (404)
{
  "detail": "User not found"
}
```

---

## Summary: PUT vs PATCH

| Aspect | PUT | PATCH |
|--------|-----|-------|
| **Purpose** | Full replacement | Partial update |
| **All fields required** | Yes | No |
| **Example** | `{"name": "A", "age": 25}` | `{"name": "A"}` |
| **Missing fields** | Set to default/null | Remain unchanged |
| **Use case** | Complete overwrite | Selective update |

---

## Summary: Query Methods

| Method | SQL Equivalent | Returns | Use Case |
|--------|---------------|---------|----------|
| `query(User)` | SELECT | Query object | Start all queries |
| `.filter()` | WHERE | Query object | Add conditions |
| `.all()` | No LIMIT | List[User] | Get all results |
| `.first()` | LIMIT 1 | User or None | Get one or none |
| `.get(id)` | WHERE pk=id | User or None | Get by primary key |
| `.offset(n)` | OFFSET n | Query object | Pagination |
| `.limit(n)` | LIMIT n | Query object | Pagination |

---

## Complete CRUD Workflow

```
CREATE ────► READ ────► UPDATE ────► DELETE
  │           │           │           │
  ▼           ▼           ▼           ▼
POST       GET        PUT/PATCH    DELETE
/users     /users     /users/{id}  /users/{id}
  │           │           │           │
  │           │           │           │
  ▼           ▼           ▼           ▼
db.add()  query().all()  setattr()  db.delete()
db.commit() .first()     db.commit() db.commit()
```

---

## Testing with Swagger UI

1. Start the server: `uvicorn main:app --reload`
2. Open browser: `http://localhost:8000/docs`
3. Expand the `/api/users/` endpoints
4. Click "Try it out"
5. Fill in the request body
6. Click "Execute"
7. View the response
