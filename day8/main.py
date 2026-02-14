"""
Day 8: API Authentication - Protecting Your FastAPI Routes
============================================================

CONCEPTUAL BREAKDOWN:
---------------------
Authentication is the process of verifying WHO a user is.
Authorization is determining WHAT a user is allowed to do.

Think of it like a hotel:
- Authentication: The front desk checking your ID to confirm you're a guest
- Authorization: Your room key card that only opens YOUR specific room

In this lesson, we'll learn:
1. What is API Key authentication?
2. How to create secure password hashing
3. How to protect routes using dependencies
4. How to handle login/verification

REAL-WORLD ANALOGY:
-------------------
Imagine a library system where:
- Users need a library card (API Key) to borrow books
- Staff need a special key (Admin Key) to add new books
- Each card has different permissions

This is exactly how API authentication works!
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import APIKeyHeader, OAuth2PasswordBearer
from pydantic import BaseModel, Field
from typing import Optional
import hashlib
import secrets

# ============================================================
# SETUP: Initialize our FastAPI app
# ============================================================
app = FastAPI(
    title="Library API - Day 8",
    description="Learning API Authentication the Fun Way!",
    version="8.0.0"
)

# ============================================================
# PART 1: Security Schemes
# ============================================================
"""
SECURITY SCHEMES EXPLAINED:
- APIKeyHeader: Looks for a key in the header (like X-API-Key)
- OAuth2PasswordBearer: More complex scheme for login flows
"""

# This header will look for: "X-API-Key: some_key_here"
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

# For login flow (username/password)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# ============================================================
# PART 2: Database (Simulated with Python dictionaries)
# ============================================================
"""
DATABASE EXPLANATION:
In real apps, you'd use PostgreSQL or MongoDB.
For learning, we're using Python dictionaries (in-memory storage).
"""

# Simulated user database
# format: {username: {"password_hash": "...", "api_key": "...", "role": "..."}}
users_db = {
    "student1": {
        "password_hash": "",  # Will be set when we create users
        "api_key": "",
        "role": "student"
    },
    "admin": {
        "password_hash": "",
        "api_key": "",
        "role": "admin"
    }
}

# Simulated book database
books_db = [
    {"id": 1, "title": "Python Basics", "author": "John Doe", "available": True},
    {"id": 2, "title": "FastAPI Mastery", "author": "Jane Smith", "available": True},
    {"id": 3, "title": "Learn APIs", "author": "Bob Wilson", "available": False},
]


# ============================================================
# PART 3: Helper Functions (Password Security)
# ============================================================
def hash_password(password: str) -> str:
    """
    Converts password to a secure hash.
    
    ANALOGY: Turning a plain text letter into encrypted code
    that only the system can decode.
    
    Args:
        password: The plain text password
    
    Returns:
        Hashed password string
    """
    # Add a "salt" - random data added to make hash unique
    salt = "Day8_Learning"  # In real apps, use random salts!
    
    # Combine password + salt, then hash
    combined = password + salt
    hashed = hashlib.sha256(combined.encode()).hexdigest()
    
    return hashed


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Checks if a password matches its hash.
    
    ANALOGY: Checking if a key fits a lock by comparing patterns.
    """
    return hash_password(plain_password) == hashed_password


def generate_api_key() -> str:
    """
    Creates a unique, secure random key for API access.
    
    ANALOGY: Printing a unique library card number.
    """
    return "key_" + secrets.token_hex(16)


# ============================================================
# PART 4: Initialize Our Database with Secure Passwords
# ============================================================
"""
INITIALIZATION:
We're setting up our demo users with secure hashed passwords.
"""

# Set up initial users with hashed passwords
users_db["student1"]["password_hash"] = hash_password("student123")
users_db["student1"]["api_key"] = generate_api_key()

users_db["admin"]["password_hash"] = hash_password("adminpass")
users_db["admin"]["api_key"] = generate_api_key()


# ============================================================
# PART 5: Dependency Functions (The Gatekeepers)
# ============================================================
"""
DEPENDENCIES EXPLAINED:
Dependencies are functions that "inject" functionality.
They're like bouncers at a club - they check if you're allowed in!

Think of it as: "Before running this function, FIRST run this check"
"""

async def verify_api_key(api_key: str = Depends(api_key_header)):
    """
    DEPENDENCY: Checks if API key is valid.
    
    This function runs BEFORE any endpoint that uses it.
    It's like a security checkpoint.
    
    Args:
        api_key: The API key from the header (injected by FastAPI)
    
    Returns:
        The username if key is valid
    
    Raises:
        HTTPException: If key is invalid or missing
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API Key - You need a key to enter!"
        )
    
    # Search for this key in our database
    for username, user_data in users_db.items():
        if user_data["api_key"] == api_key:
            return username  # Key is valid!
    
    # If we get here, key wasn't found
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid API Key - Access Denied!"
    )


async def verify_admin(user: str = Depends(verify_api_key)) -> str:
    """
    DEPENDENCY: Checks if user is an admin.
    
    This is a LAYERED dependency - it runs verify_api_key FIRST,
    THEN checks if the user is an admin.
    
    Args:
        user: Username from the first dependency check
    
    Returns:
        Username if they're an admin
    
    Raises:
        HTTPException: If user is not an admin
    """
    if users_db[user]["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admins Only - You don't have permission!"
        )
    return user


# ============================================================
# PART 6: Pydantic Models (Data Validation)
# ============================================================
"""
PYDANTIC MODELS:
These define what data our API accepts and returns.
They automatically validate incoming data!

Think of them as: "Forms that check their own answers"
"""

class UserLogin(BaseModel):
    """Schema for user login requests"""
    username: str = Field(..., description="Your username")
    password: str = Field(..., description="Your password")


class UserResponse(BaseModel):
    """Schema for user info responses"""
    username: str
    api_key: str
    role: str


class Book(BaseModel):
    """Schema for book data"""
    title: str
    author: str
    available: bool = True


# ============================================================
# PART 7: Public Endpoints (No Authentication Required)
# ============================================================

@app.get("/")
async def root():
    """Welcome message - open to everyone!"""
    return {
        "message": "Welcome to the Library API!",
        "hint": "Use /register to get an API key, or /login to authenticate",
        "available_routes": [
            "GET / - This page",
            "POST /register - Get a new API key",
            "POST /login - Login with username/password"
        ]
    }


@app.post("/register")
async def register(user: UserLogin):
    """
    REGISTER ENDPOINT: Get a new API key.
    
    This simulates registering for the first time.
    In a real app, you'd save this to a database!
    
    SAMPLE CURL:
    curl -X POST "http://localhost:8000/register" \
         -H "Content-Type: application/json" \
         -d '{"username":"newuser", "password":"mypass123"}'
    """
    # Check if username already exists
    if user.username in users_db:
        raise HTTPException(
            status_code=400,
            detail="Username already taken! Choose another."
        )
    
    # Create new user with hashed password
    users_db[user.username] = {
        "password_hash": hash_password(user.password),
        "api_key": generate_api_key(),
        "role": "student"
    }
    
    return {
        "message": "User registered successfully!",
        "username": user.username,
        "api_key": users_db[user.username]["api_key"],
        "warning": "SAVE THIS API KEY! You won't see it again!"
    }


@app.post("/login")
async def login(user: UserLogin) -> dict:
    """
    LOGIN ENDPOINT: Verify credentials and return info.
    
    This is like signing into a website.
    
    SAMPLE CURL:
    curl -X POST "http://localhost:8000/login" \
         -H "Content-Type: application/json" \
         -d '{"username":"student1", "password":"student123"}'
    """
    # Check if user exists
    if user.username not in users_db:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )
    
    # Get stored user data
    stored_data = users_db[user.username]
    
    # Verify password
    if not verify_password(user.password, stored_data["password_hash"]):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )
    
    return {
        "message": "Login successful!",
        "username": user.username,
        "api_key": stored_data["api_key"],
        "role": stored_data["role"]
    }


# ============================================================
# PART 8: Protected Endpoints (Authentication Required)
# ============================================================

@app.get("/books")
async def get_books(user: str = Depends(verify_api_key)):
    """
    LIST ALL BOOKS - Requires valid API key.
    
    This endpoint is protected by the verify_api_key dependency.
    Without a valid X-API-Key header, this will return 401!
    
    SAMPLE CURL:
    curl -X GET "http://localhost:8000/books" \
         -H "X-API-Key: key_abc123..."
    
    DEPENDENCY CHAIN:
    1. FastAPI extracts X-API-Key from header
    2. Calls verify_api_key() function
    3. If valid, returns username to use in endpoint
    """
    return {
        "user": user,
        "books": books_db
    }


@app.get("/books/{book_id}")
async def get_book(book_id: int, user: str = Depends(verify_api_key)):
    """
    GET SINGLE BOOK - Requires valid API key.
    
    Path parameter: book_id (integer)
    Dependency: verify_api_key (from header)
    """
    for book in books_db:
        if book["id"] == book_id:
            return {"user": user, "book": book}
    
    raise HTTPException(
        status_code=404,
        detail=f"Book with ID {book_id} not found"
    )


# ============================================================
# PART 9: Admin-Only Endpoints
# ============================================================

@app.post("/books", response_model=dict)
async def add_book(
    book: Book,
    admin: str = Depends(verify_admin)
):
    """
    ADD NEW BOOK - Admin only!
    
    This endpoint has TWO layers of protection:
    1. verify_api_key - Must be logged in
    2. verify_admin - Must be an admin
    
    Only users with role="admin" can access this!
    
    SAMPLE CURL:
    curl -X POST "http://localhost:8000/books" \
         -H "X-API-Key: admin_key_here" \
         -H "Content-Type: application/json" \
         -d '{"title":"New Book", "author":"Author Name", "available":true}'
    """
    new_book = {
        "id": len(books_db) + 1,
        "title": book.title,
        "author": book.author,
        "available": book.available
    }
    books_db.append(new_book)
    
    return {
        "message": "Book added successfully!",
        "added_by": admin,
        "book": new_book
    }


@app.delete("/books/{book_id}")
async def delete_book(
    book_id: int,
    admin: str = Depends(verify_admin)
):
    """
    DELETE BOOK - Admin only!
    
    ADMIN SAMPLE CURL:
    curl -X DELETE "http://localhost:8000/books/1" \
         -H "X-API-Key: admin_key_here"
    """
    for i, book in enumerate(books_db):
        if book["id"] == book_id:
            deleted_book = books_db.pop(i)
            return {
                "message": f"Book '{deleted_book['title']}' deleted",
                "deleted_by": admin
            }
    
    raise HTTPException(
        status_code=404,
        detail=f"Book with ID {book_id} not found"
    )


# ============================================================
# THE 'AHA!' MOMENT: Common Logical Error
# ============================================================
"""
⚠️  COMMON MISTAKE TO AVOID! ⚠️

❌ WRONG WAY (INSECURE - DO NOT USE IN PRODUCTION!):
    
    async def verify_password_unsafe(plain: str, stored: str) -> bool:
        return plain == stored  # NEVER compare plain text passwords!
    
    # This is like leaving your house keys under the doormat!
    # Anyone who sees this can read the actual passwords!

✅ CORRECT WAY (What we do in this lesson):

    def verify_password(plain_password: str, hashed_password: str) -> bool:
        # Hash the plain password, then compare hashes
        return hash_password(plain_password) == hashed_password

❌ ANOTHER COMMON ERROR - Forgetting to hash during registration:

    # WRONG:
    users_db[username] = {
        "password": password,  # ❌ Plain text password saved!
        ...
    }
    
    # CORRECT:
    users_db[username] = {
        "password_hash": hash_password(password),  # ✅ Secure hash!
        ...
    }

WHY DOES THIS MATTER?
If a hacker gets access to your database:
- Plain text passwords → They can try these passwords on OTHER sites
- Hashed passwords → Much harder to reverse engineer

This is why you should NEVER store passwords in plain text!
"""


# ============================================================
# Socratic Discussion Questions
# ============================================================
"""
CLASS DISCUSSION: Test Your Understanding!
-----------------------------------------

1. What is the difference between authentication and authorization?
   (Hint: Think about hotel check-in vs. room key card)

2. In our code, what happens if someone sends a request without an
   X-API-Key header to the /books endpoint?
   (Hint: Look at the verify_api_key dependency)

3. Why do we use hashlib.sha256() instead of storing passwords directly?
   (Hint: What would happen if someone stole our database?)

4. What is the purpose of the "salt" in password hashing?
   (Hint: Does adding salt make two identical passwords have different hashes?)

5. In the dependency function verify_admin, we call verify_api_key FIRST.
   Why is this order important?
   (Hint: Can you be an admin if you don't have a valid API key?)

6. What would happen if we removed Depends(verify_api_key) from the
   /books endpoint? Would it still work?
   (Hint: Try to visualize what the function receives as 'user')

7. In our UserLogin schema, why do we use Field(..., description="...")?
   What does the "..." accomplish?
   (Hint: Try removing it and see what error you get!)

8. The generate_api_key() function uses secrets.token_hex(16).
   Why is this better than just using the username as a key?
   (Hint: Can users guess or predict a good API key?)

9. What HTTP status code is returned when authentication fails?
   What about when authorization fails?
   (Hint: 401 vs 403 - what's the difference?)

10. In the /register endpoint, we check if username already exists.
    What would happen if we removed this check?
    (Hint: What if two users have the same username?)

11. Why do we return the API key only ONCE during registration?
    Why don't we return it every time someone logs in?
    (Hint: Think about security - where might the key be stored?)

12. What is the difference between POST /register and POST /login?
    Why do we need both?
    (Hint: When would you use each one?)

13. If a student's API key is stolen, what should they do?
    How would they get a new one?
    (Hint: Look at the /register endpoint - can they re-register?)

14. In the add_book endpoint, we verify the admin TWICE (once as a
    user, once as admin). Is this redundant?
    (Hint: What if someone with a student key tried to access this?)

15. The api_key_header has auto_error=False. What does this mean?
    What would happen if we set it to True?
    (Hint: Try changing it and see what error message you get!)

BONUS CHALLENGE:
----------------
Try adding a new endpoint that allows users to change their password.
What security considerations would you need to remember?
"""

# ============================================================
# End of Day 8!
# ============================================================
"""
SUMMARY:
- Day 7: CRUD operations (Create, Read, Update, Delete)
- Day 8: Adding authentication to protect our routes

NEXT DAY (Day 9): We'll learn about environment variables and
how to keep our secrets (API keys, database URLs) safe!

HOMEWORK:
1. Try calling all endpoints using curl or Postman
2. Add a new endpoint to list only available books
3. Add a "borrow book" feature that changes availability

Remember: "With great power comes great responsibility!"
Use your authentication knowledge to build SECURE apps! 🔐
"""
