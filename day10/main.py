"""
Day 10: FastAPI with SQLAlchemy - Complete CRUD Application
===========================================================

FINAL PROJECT: Coffee Shop API

This is the culmination of Days 7-10!
- Day 7: CRUD basics
- Day 8: Authentication
- Day 9: Dependency Injection
- Day 10: Putting it ALL together with real database!

CONCEPTUAL BREAKDOWN:
--------------------
This is a complete FastAPI application that:
1. Uses SQLAlchemy for database operations
2. Implements full CRUD for Customers, Products, and Orders
3. Uses dependency injection for database sessions
4. Validates all input with Pydantic schemas
5. Returns properly formatted responses

THE COFFEE SHOP DATA MODEL:
- Customers: People who order coffee
- Products: Coffee drinks and items we sell
- Orders: Records of purchases (with multiple items)
- OrderItems: Links orders to products (many-to-many)

STARTING THE APPLICATION:
-------------------------
uvicorn main:app --reload

Then visit:
- http://localhost:8000 - API welcome page
- http://localhost:8000/docs - Interactive API documentation (Swagger UI)
- http://localhost:8000/redoc - Alternative documentation (ReDoc)
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

# Add the current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import database initialization
from database import init_db

# Import routers
from api.routes import router_customers, router_products, router_orders


# ============================================================
# APP INITIALIZATION
# ============================================================

app = FastAPI(
    title="☕ Coffee Shop API - Day 10",
    description="""
    ## Welcome to the Complete Coffee Shop API!
    
    This API demonstrates a full-stack FastAPI application with:
    - **SQLAlchemy** for database operations
    - **Pydantic** for data validation
    - **Dependency Injection** for clean code
    - **Full CRUD** operations
    - **Related data** (orders with customers and products)
    
    ### Quick Start
    1. Create a customer with POST /api/v1/customers
    2. View products with GET /api/v1/products
    3. Place an order with POST /api/v1/orders
    
    ### Authentication
    This is a learning version - no authentication required!
    In production, you would add API key or JWT auth.
    """,
    version="10.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


# ============================================================
# CORS MIDDLEWARE (Allow cross-origin requests)
# ============================================================
"""
CORS (Cross-Origin Resource Sharing) allows browsers to make
requests to your API from different domains.

In production, you might restrict this to your frontend domain.
For learning, we allow everything!
"""

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)


# ============================================================
# STARTUP EVENT: Initialize Database
# ============================================================
@app.on_event("startup")
async def startup_event():
    """Run when the application starts."""
    print("🚀 Starting Coffee Shop API...")
    print("📦 Initializing database...")
    init_db()
    print("✅ Database ready!")
    print("\n📖 Documentation: http://localhost:8000/docs")
    print("🔗 API Base URL: http://localhost:8000/api/v1")


# ============================================================
# ROOT ENDPOINT
# ============================================================

@app.get("/", tags=["Root"])
async def root():
    """
    Welcome page for the API.
    
    Returns links to documentation and available endpoints.
    """
    return {
        "message": "☕ Welcome to the Coffee Shop API!",
        "version": "10.0.0",
        "documentation": {
            "swagger_ui": "/docs",
            "redoc": "/redoc"
        },
        "api_endpoints": {
            "customers": "/api/v1/customers",
            "products": "/api/v1/products",
            "orders": "/api/v1/orders"
        },
        "quick_guide": {
            "step_1": "POST /api/v1/customers - Create a customer",
            "step_2": "GET /api/v1/products - View coffee menu",
            "step_3": "POST /api/v1/orders - Place an order"
        }
    }


# ============================================================
# INCLUDE ALL ROUTERS
# ============================================================

# Include routers with prefix and tags
app.include_router(router_customers, prefix="/api/v1")
app.include_router(router_products, prefix="/api/v1")
app.include_router(router_orders, prefix="/api/v1")


# ============================================================
# EXAMPLE CURL COMMANDS (For students to try!)
# ============================================================
"""
EXAMPLE USAGE:

1. Create a customer:
   curl -X POST "http://localhost:8000/api/v1/customers" \
        -H "Content-Type: application/json" \
        -d '{"name": "Alice", "email": "alice@example.com", "phone": "555-1234"}'

2. List all customers:
   curl "http://localhost:8000/api/v1/customers"

3. Get a single customer:
   curl "http://localhost:8000/api/v1/customers/1"

4. Create a product:
   curl -X POST "http://localhost:8000/api/v1/products" \
        -H "Content-Type: application/json" \
        -d '{"name": "Espresso", "description": "Strong coffee", "price": 3.00, "category": "coffee"}'

5. List products:
   curl "http://localhost:8000/api/v1/products"

6. Place an order (after creating customer and products):
   curl -X POST "http://localhost:8000/api/v1/orders" \
        -H "Content-Type: application/json" \
        -d '{"customer_id": 1, "items": [{"product_id": 1, "quantity": 2}]}'

7. List orders:
   curl "http://localhost:8000/api/v1/orders"

8. Update order status:
   curl -X PATCH "http://localhost:8000/api/v1/orders/1" \
        -H "Content-Type: application/json" \
        -d '{"status": "preparing"}'

9. Update a customer:
   curl -X PUT "http://localhost:8000/api/v1/customers/1" \
        -H "Content-Type: application/json" \
        -d '{"name": "Alice Smith", "phone": "555-5678"}'

10. Delete a customer (soft delete):
    curl -X DELETE "http://localhost:8000/api/v1/customers/1"
"""

# ============================================================
# SUMMARY: What We Learned
# ============================================================
"""
SUMMARY OF DAYS 7-10:
---------------------

Day 7: CRUD Basics
- Learned the four operations: Create, Read, Update, Delete
- Used in-memory data (lists/dictionaries)
- Basic routing with FastAPI

Day 8: Authentication
- API Key authentication
- Password hashing (concepts)
- Protecting routes with dependencies
- Understanding auth vs authorization

Day 9: Dependency Injection
- What is DI and why it matters
- Depends() for clean code
- Database session dependencies
- Class-based dependencies
- Testing with dependency overrides

Day 10: SQLAlchemy Integration
- ORM models vs Pydantic schemas
- Database configuration with SQLAlchemy
- Complex relationships (Customer -> Order -> OrderItem -> Product)
- Full CRUD with real database
- Query parameters and pagination
- Transaction management (all-or-nothing operations)

THE COMPLETE PICTURE:
--------------------
Request → Route → Schema Validation → Dependency (DB) → Model → DB
                                                          ↓
Response ← Schema ← Model ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ←

KEY FILES:
- database.py: DB connection and session management
- models.py: SQLAlchemy ORM models (database structure)
- schemas.py: Pydantic models (API input/output validation)
- api/routes.py: All CRUD endpoints
- main.py: Application entry point

NEXT STEPS (Day 11):
-------------------
- User authentication with JWT tokens
- Password hashing with bcrypt
- Login endpoints with token generation
- Protected routes with OAuth2
- User roles and permissions
"""

# ============================================================
# A Note on Testing
# ============================================================
"""
TESTING YOUR API:
-----------------
FastAPI makes testing easy! Here's an example test:

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_create_customer():
    response = client.post(
        "/api/v1/customers",
        json={"name": "Test", "email": "test@example.com"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test"
    assert "id" in data

def test_get_nonexistent_customer():
    response = client.get("/api/v1/customers/9999")
    assert response.status_code == 404

Run tests with:
    pytest test_filename.py -v
"""
