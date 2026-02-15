"""
Day 9: Dependency Injection - The Secret Sauce of Clean Code
============================================================

CONCEPTUAL BREAKDOWN:
--------------------
Dependency Injection (DI) is a design pattern where a component receives
its dependencies from external sources rather than creating them itself.

Think of it like a COFFEE SHOP:
- Without DI: You grow your own coffee beans, build your own machine, etc.
- With DI: The coffee shop provides everything; you just order and use it!

In software terms:
- Instead of your function creating its own dependencies (DB connection, etc.)
- FastAPI "injects" those dependencies for you
- Makes code: More testable, More reusable, More maintainable

WHY FASTAPI LOVES DI:
---------------------
FastAPI's dependency injection system is:
1. Simple to define
2. Automatically executed before endpoints
3. Shared across multiple endpoints
4. Easy to override (great for testing!)

REAL-WORLD ANALOGY - The Restaurant Kitchen:
--------------------------------------------
Imagine a restaurant kitchen:
- Head Chef (your endpoint) focuses on cooking
- Sous Chefs (dependencies) handle: chopping, sauces, plating
- Ingredients (parameters) are prepared beforehand
- Everything works together smoothly!

Each "dependency" is like a specialized helper:
- get_db(): Provides a clean database session
- verify_token(): Checks if user is logged in
- get_settings(): Provides configuration
"""

from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, Generator
from contextlib import contextmanager
import time

# ============================================================
# SETUP: Initialize FastAPI App
# ============================================================
app = FastAPI(
    title="Coffee Shop API - Day 9",
    description="Learning Dependency Injection with Coffee!",
    version="9.0.0"
)

# ============================================================
# PART 1: Understanding Dependencies Without DI (The Hard Way)
# ============================================================
"""
BEFORE: Without Dependency Injection
------------------------------------
This is how we'd normally write code - everything coupled together.
Hard to test, hard to maintain, hard to reuse.
"""

# A "fake" database (in real life, this would be SQLAlchemy)
coffee_menu = [
    {"id": 1, "name": "Espresso", "price": 3.00, "caffeine_mg": 63},
    {"id": 2, "name": "Latte", "price": 4.50, "caffeine_mg": 75},
    {"id": 3, "name": "Cappuccino", "price": 4.00, "caffeine_mg": 75},
    {"id": 4, "name": "Americano", "price": 3.50, "caffeine_mg": 94},
]

orders_db = []

# ============================================================
# PART 2: Defining Dependencies (The Building Blocks)
# ============================================================
"""
DEFINING DEPENDENCIES:
A dependency is just a function that returns something useful!
FastAPI will call this function and pass the result to your endpoint.

Think of dependencies as:
- Helper functions that run before your endpoint
- Providers of resources (DB, configs, services)
- Gatekeepers (authentication, validation)
"""

# ------------------------------------------
# Dependency #1: Database Session (Simulated)
# ------------------------------------------
@contextmanager
def get_db_session():
    """
    DEPENDENCY: Provides a database session.
    
    In real FastAPI apps, this would connect to PostgreSQL/MySQL.
    Here, we simulate it for learning purposes.
    
    WHY USE contextmanager?
    - Ensures resources are cleaned up properly
    - Like: "Open the database, do work, close it automatically"
    
    ANALOGY: Borrowing a book from a library
    - Get the book (begin transaction)
    - Read it (query database)
    - Return it (commit/close)
    
    Usage in endpoint:
        with get_db_session() as db:
            db.query(...)
    """
    # Simulate opening a database connection
    print("🔌 Opening database connection...")
    
    # This "try" block represents our database operations
    try:
        yield {
            "menu": coffee_menu,
            "orders": orders_db
        }
    finally:
        # This always runs - even if there's an error!
        print("🔌 Closing database connection...")

# ------------------------------------------
# Dependency #2: Current Time (Simple Utility)
# ------------------------------------------
def get_current_time() -> dict:
    """
    DEPENDENCY: Returns current timestamp.
    
    Simple example of a dependency that provides data.
    
    Usage: Depends(get_current_time)
    """
    return {
        "timestamp": time.time(),
        "formatted": time.strftime("%Y-%m-%d %H:%M:%S")
    }

# ------------------------------------------
# Dependency #3: Service Health Check
# ------------------------------------------
def check_service_health() -> dict:
    """
    DEPENDENCY: Checks if external services are available.
    
    In real apps, this might check:
    - Database connectivity
    - External API availability
    - Cache server status
    
    ANALOGY: A mechanic checking a car before a road trip!
    """
    # Simulate health check
    return {
        "database": "healthy",
        "cache": "healthy",
        "external_api": "healthy",
        "checked_at": time.strftime("%H:%M:%S")
    }

# ------------------------------------------
# Dependency #4: Rate Limiter (Security)
# ------------------------------------------
class RateLimiter:
    """
    DEPENDENCY: Limits how many requests a user can make.
    
    This is a CLASS-based dependency!
    FastAPI can instantiate and use classes as dependencies.
    
    ANALOGY: A bouncer at a club counting how many people enter.
    """
    
    def __init__(self, max_requests: int = 5, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}  # Track request counts
    
    def check_rate_limit(self, client_id: str) -> bool:
        """
        Returns True if request is allowed, False if rate limited.
        """
        current_time = time.time()
        
        if client_id not in self.requests:
            self.requests[client_id] = []
        
        # Remove old requests outside the window
        self.requests[client_id] = [
            t for t in self.requests[client_id]
            if current_time - t < self.window_seconds
        ]
        
        # Check if under limit
        if len(self.requests[client_id]) >= self.max_requests:
            return False
        
        # Record this request
        self.requests[client_id].append(current_time)
        return True


# Create a rate limiter instance (shared across requests)
rate_limiter = RateLimiter(max_requests=3, window_seconds=60)

# ============================================================
# PART 3: Pydantic Models (Data Validation)
# ============================================================

class OrderCreate(BaseModel):
    """Schema for creating a new order"""
    coffee_id: int = Field(..., gt=0, description="ID of the coffee to order")
    quantity: int = Field(default=1, ge=1, le=10, description="How many cups")
    customer_name: str = Field(..., min_length=2, description="Your name")


class OrderResponse(BaseModel):
    """Schema for order responses"""
    order_id: int
    coffee_name: str
    quantity: int
    total_price: float
    status: str
    created_at: str

# ============================================================
# PART 4: Endpoints - First, Without Dependencies (Hard Way)
# ============================================================

@app.get("/menu-legacy")
async def get_menu_legacy():
    """
    ❌ LEGACY WAY: No dependencies used directly.
    
    Problem: If we need the DB session elsewhere, we'd duplicate code.
    Problem: Hard to test because everything is coupled.
    Problem: What if DB connection logic changes? We update everywhere!
    """
    # Manually doing what a dependency would do
    return {"menu": coffee_menu}

# ============================================================
# PART 5: Endpoints - Using Dependencies (The Right Way!)
# ============================================================

# ------------------------------------------
# Example 1: Simple Dependency Injection
# ------------------------------------------
@app.get("/menu")
async def get_menu(
    # FastAPI will call get_db_session() and pass the result here!
    # The "db" parameter receives what the dependency "yields"
    db: dict = Depends(get_db_session)
):
    """
    ✅ DEPENDENCY INJECTION: Clean and simple!
    
    How it works:
    1. FastAPI sees db = Depends(get_db_session)
    2. Calls get_db_session() → gets the yielded dictionary
    3. Passes that dictionary as the `db` parameter
    4. Our endpoint uses it!
    
    SAMPLE CURL:
        curl "http://localhost:8000/menu"
    """
    return {
        "menu": db["menu"],
        "source": "This data came from our get_db_session dependency!"
    }

# ------------------------------------------
# Example 2: Multiple Dependencies
# ------------------------------------------
@app.get("/health")
async def health_check(
    # Can use multiple dependencies!
    time_info: dict = Depends(get_current_time),
    service_status: dict = Depends(check_service_health)
):
    """
    ✅ MULTIPLE DEPENDENCIES: Combining helpers.
    
    FastAPI will call BOTH dependencies and pass both results!
    
    Order matters for parameters, but FastAPI matches by name.
    
    SAMPLE CURL:
        curl "http://localhost:8000/health"
    """
    return {
        "server_time": time_info,
        "services": service_status,
        "status": "All systems operational!"
    }

# ------------------------------------------
# Example 3: Dependency with Rate Limiting
# ------------------------------------------
@app.post("/orders")
async def create_order(
    order: OrderCreate,
    db: dict = Depends(get_db_session),
    rate_ok: bool = Depends(lambda: rate_limiter.check_rate_limit("web_client"))
):
    """
    ✅ DEPENDENCY WITH RATE LIMITING: Protecting our API!
    
    Dependencies used:
    1. get_db_session: For database operations
    2. Inline lambda: For rate limiting check
    
    SAMPLE CURL:
        curl -X POST "http://localhost:8000/orders" \
             -H "Content-Type: application/json" \
             -d '{"coffee_id": 2, "quantity": 2, "customer_name": "Alice"}'
    
    If you call this 4 times in 60 seconds, you'll get a 429 error!
    """
    if not rate_ok:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Slow down! Maximum 3 orders per minute."
        )
    
    # Find the coffee in our menu
    coffee = None
    for item in db["menu"]:
        if item["id"] == order.coffee_id:
            coffee = item
            break
    
    if not coffee:
        raise HTTPException(
            status_code=404,
            detail=f"Coffee with ID {order.coffee_id} not found"
        )
    
    # Calculate total
    total_price = coffee["price"] * order.quantity
    
    # Create order
    new_order = {
        "order_id": len(db["orders"]) + 1,
        "coffee_name": coffee["name"],
        "coffee_id": order.coffee_id,
        "quantity": order.quantity,
        "total_price": total_price,
        "customer_name": order.customer_name,
        "status": "preparing",
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    db["orders"].append(new_order)
    
    return {
        "message": "Order placed successfully!",
        "order": new_order,
        "rate_limit_remaining": 2  # Shows rate limiter working!
    }


@app.get("/orders")
async def get_orders(
    db: dict = Depends(get_db_session)
):
    """
    ✅ DEPENDENCY: Get all orders.
    
    Reusing the same database dependency!
    
    SAMPLE CURL:
        curl "http://localhost:8000/orders"
    """
    return {"orders": db["orders"]}

# ===========================================================
# PART 6: Advanced - Class-Based Dependencies
# ============================================================

class Settings:
    """
    CLASS-BASED DEPENDENCY: Configuration holder.
    
    Classes can be dependencies too!
    FastAPI will instantiate them automatically.
    
    ANALOGY: A configuration file that different parts of the app read from.
    """
    
    def __init__(self, tax_rate: float = 0.08, currency: str = "USD"):
        self.tax_rate = tax_rate
        self.currency = currency
        self.shop_name = "☕ FastAPI Coffee House"
        self.version = "9.0.0"


# Create settings instance
app_settings = Settings(tax_rate=0.10, currency="$")


@app.get("/settings")
async def get_settings(
    settings: Settings = Depends(lambda: app_settings)
):
    """
    ✅ CLASS DEPENDENCY: Using a settings object.
    
    Note: We use a lambda to return our pre-created instance.
    
    SAMPLE CURL:
        curl "http://localhost:8000/settings"
    """
    return {
        "shop_name": settings.shop_name,
        "currency": settings.currency,
        "tax_rate": settings.tax_rate,
        "version": settings.version
    }

# ============================================================
# PART 7: Sub-Dependencies (Dependencies that Depend!)
# ============================================================
"""
SUB-DEPENDENCIES:
A dependency can itself depend on other dependencies!

CHAIN EXAMPLE:
    Endpoint → get_order_details → validate_order_id → get_db_session

This creates a chain of dependencies!
"""

def validate_order_id(order_id: int) -> int:
    """
    SUB-DEPENDENCY: Validates order ID format.
    
    Could itself depend on: get_db_session to check if order exists!
    """
    if order_id < 1:
        raise HTTPException(
            status_code=400,
            detail="Order ID must be positive"
        )
    return order_id


@app.get("/orders/{order_id}")
async def get_order(
    order_id: int = Depends(validate_order_id),
    db: dict = Depends(get_db_session)
):
    """
    ✅ SUB-DEPENDENCY: Order ID validated BEFORE using in endpoint!
    
    Chain: get_order → validate_order_id → get_db_session
    
    SAMPLE CURL:
        curl "http://localhost:8000/orders/1"
    """
    for order in db["orders"]:
        if order["order_id"] == order_id:
            return {"order": order}
    
    raise HTTPException(
        status_code=404,
        detail=f"Order #{order_id} not found"
    )

# ============================================================
# PART 8: Dependency Override (Testing Magic!)
# ============================================================
"""
THE MAGIC OF OVERRIDING:
In testing, you can REPLACE real dependencies with fake ones!
This makes testing EASY and FAST!

Example in tests:
    app.dependency_overrides[get_db_session] = fake_db_session
    
Now all endpoints use fake_db_session instead of real one!
No real database needed for tests!
"""

# ============================================================
# THE 'AHA!' MOMENT: Common Dependency Injection Mistakes
# ============================================================
"""
⚠️  COMMON MISTAKES TO AVOID! ⚠️

❌ MISTAKE 1: Forgetting to yield in contextmanager

    # WRONG - This will hang!
    def get_db():
        db = connect()  # Opens connection
        yield db
        # Forgot to close! Connection stays open!
    
    # CORRECT - Always clean up!
    def get_db():
        db = connect()
        try:
            yield db
        finally:
            db.close()  # ✅ Always closes

❌ MISTAKE 2: Modifying dependency parameters

    # WRONG - Don't change the dependency object!
    @app.get("/")
    async def endpoint(db: Session = Depends(get_session)):
        db.some_internal_value = "hacked"  # ❌ Modifying shared state!
    
    # CORRECT - Treat dependencies as read-only
    async def endpoint(db: Session = Depends(get_session)):
        result = db.query(User).all()  # ✅ Just use it

❌ MISTAKE 3: Dependencies with side effects in production

    # WRONG - Don't log in production dependencies
    def get_config():
        log_user_access()  # Side effect!
        return config
    
    # CORRECT - Separate concerns
    def get_config():
        return config
    
    def audit_access():
        log_user_access()

❌ MISTAKE 4: Circular dependencies

    # WRONG - A depends on B, B depends on A!
    def get_a(b: str = Depends(get_b)):
        return {"a": b}
    
    def get_b(a: str = Depends(get_a)):  # ❌ Circular!
        return {"b": a}
    
    # CORRECT - Restructure to avoid cycles

✅ BEST PRACTICES:
1. Keep dependencies simple and focused
2. Always clean up resources (context managers)
3. Don't share state between requests
4. Use classes for complex configurations
5. Override dependencies for testing
"""

# ============================================================
# Socratic Discussion Questions
# ============================================================
"""
CLASS DISCUSSION: Test Your Understanding!
-----------------------------------------

1. What is a dependency in FastAPI terms?
   (Hint: Is it a class, function, or something else?)

2. When you write `db: Session = Depends(get_db)`:
   - What does Depends() do?
   - When is get_db() called?
   - What does it return to the endpoint?
   
3. Compare the legacy endpoint (/menu-legacy) with the DI endpoint (/menu).
   - What's the difference in code structure?
   - Which is easier to maintain?

4. Why do we use @contextmanager for get_db_session?
   What problem does it solve?
   (Hint: Think about what happens if an error occurs mid-request)

5. In the health check endpoint, we used TWO dependencies.
   What if we added a third? What would the endpoint signature look like?
   (Hint: Think about parameter order and names)

6. The RateLimiter is a CLASS-based dependency.
   What advantage does this have over a function?
   (Hint: What can a class store that a function can't?)

7. When you call /orders multiple times quickly, what happens?
   Which dependency prevents abuse?
   (Hint: Look at the check_rate_limit call)

8. What's the difference between Depends(get_db_session) and
   Depends(lambda: get_db_session)?
   (Hint: One calls a function, one passes a reference)

9. In the settings example, we used a lambda: Depends(lambda: app_settings)
   Why couldn't we just use: Depends(app_settings)?
   (Hint: FastAPI needs to CALL the dependency)

10. What is a "sub-dependency"? Can you identify one in this code?
    (Hint: Look for dependencies that validate before using)

11. Why is dependency injection good for TESTING?
    (Hint: What does "dependency override" allow us to do?)

12. If we wanted to add caching to our API, would this be a dependency?
    How would you implement it?
    (Hint: A caching dependency could store results and return them on repeat requests)

13. What happens if a dependency raises an HTTPException?
    Does the endpoint still run?
    (Hint: Try it! Add a dependency that always raises an error)

14. In a real app, get_db_session might connect to PostgreSQL.
    Why would we want to create a NEW dependency override for tests?
    (Hint: Tests should NOT touch the real database)

15. The RateLimiter class stores requests in self.requests = {}.
    This is shared across all requests!
    Is this a problem? What would be a better approach for production?
    (Hint: Think about multiple workers, memory limits, security)

BONUS CHALLENGE:
----------------
Add a new dependency called get_current_user() that:
1. Checks for an "Authorization" header
2. Returns the user if valid, or raises 401 if missing
3. Add this dependency to the /orders POST endpoint

What changes do you need to make?
"""
# ============================================================
# SUMMARY & NEXT STEPS
# ============================================================
"""
SUMMARY OF DAY 9:
-----------------
✅ Day 8: Authentication (protecting who can access)
✅ Day 9: Dependency Injection (clean, reusable, testable code)

KEY TAKEAWAYS:
1. Dependencies are functions/classes that provide resources
2. Use Depends() to inject them into endpoints
3. Context managers ensure cleanup (database connections!)
4. Multiple dependencies can be used in one endpoint
5. Class-based dependencies are great for settings/state
6. Override dependencies for easy testing!

NEXT DAY (Day 10):
------------------
We'll combine everything we've learned:
- Full CRUD with authentication
- Dependency injection for clean architecture
- Real database integration with SQLAlchemy
- Deployment considerations

REMEMBER:
"Dependencies aren't just imports - they're the glue that holds
your application together in a clean, maintainable way!"
"""

# ============================================================
# QUICK REFERENCE: Dependency Patterns
# ============================================================
"""
PATTERN 1: Simple Function Dependency
-------------------------------------
def get_config():
    return {"setting": "value"}

@app.get("/")
async def endpoint(config: dict = Depends(get_config)):
    return config


PATTERN 2: Context Manager (Database)
-------------------------------------
@contextmanager
def get_db():
    db = connect()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
async def endpoint(db = Depends(get_db)):
    return db.query.all()


PATTERN 3: Class Dependency
--------------------------
class Settings:
    def __init__(self, api_key: str):
        self.api_key = api_key

settings = Settings(api_key="secret")

@app.get("/")
async def endpoint(settings: Settings = Depends(lambda: settings)):
    return {"key": settings.api_key}


PATTERN 4: Multiple Dependencies
--------------------------------
@app.get("/")
async def endpoint(
    db = Depends(get_db),
    config = Depends(get_config),
    time = Depends(get_time)
):
    return {"db": db, "config": config, "time": time}


PATTERN 5: Override for Testing
--------------------------------
# In your test file:
app.dependency_overrides[get_db] = fake_get_db

# Now all endpoints use fake_get_db instead!
"""
