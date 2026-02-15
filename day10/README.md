# Day 10: FastAPI with SQLAlchemy - Complete CRUD Application

## Overview

Day 10 brings together everything we've learned in Days 7-9 and adds **real database integration** using SQLAlchemy. This is where your API becomes a "real" application that persists data!

## What You'll Learn

### Core Concepts

1. **SQLAlchemy ORM** - Map Python classes to database tables
2. **Pydantic Schemas** - Validate and serialize API data
3. **Dependency Injection** - Clean database session management
4. **Full CRUD Operations** - Create, Read, Update, Delete
5. **Related Data** - Orders with Customers and Products
6. **Transactions** - All-or-nothing database operations

### Project Structure

```
day10/
├── main.py              # Application entry point
├── database.py          # Database configuration and session management
├── models.py            # SQLAlchemy ORM models (database structure)
├── schemas.py           # Pydantic models (API validation)
├── requirements.txt     # Python dependencies
├── api/
│   └── routes.py       # All API endpoints (CRUD operations)
└── README.md           # This file
```

## Getting Started

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Application

```bash
uvicorn main:app --reload
```

### 3. Access the API

- **Interactive Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **API Root**: http://localhost:8000/

## Coffee Shop Data Model

### Customer
- `id`: Unique identifier
- `name`: Customer's name
- `email`: Unique email address
- `phone`: Optional phone number
- `is_active`: Soft delete flag
- `orders`: Related orders

### Product
- `id`: Unique identifier
- `name`: Product name
- `description`: Product details
- `price`: Selling price
- `category`: coffee, tea, pastry, etc.
- `stock`: Inventory count
- `is_available`: Sales flag

### Order
- `id`: Unique identifier
- `customer_id`: Foreign key to Customer
- `status`: pending, preparing, ready, completed
- `total_amount`: Order total
- `items`: Related OrderItems

### OrderItem (Junction Table)
- `id`: Unique identifier
- `order_id`: Foreign key to Order
- `product_id`: Foreign key to Product
- `quantity`: Number of items
- `price_at_order`: Price at time of order

## API Endpoints

### Customers (`/api/v1/customers`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/customers` | List all customers (paginated) |
| GET | `/customers/{id}` | Get single customer |
| POST | `/customers` | Create new customer |
| PUT | `/customers/{id}` | Update customer |
| DELETE | `/customers/{id}` | Soft delete customer |

### Products (`/api/v1/products`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/products` | List all products |
| GET | `/products/{id}` | Get single product |
| POST | `/products` | Create new product |
| PUT | `/products/{id}` | Update product |
| DELETE | `/products/{id}` | Soft delete product |

### Orders (`/api/v1/orders`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/orders` | List all orders |
| GET | `/orders/{id}` | Get full order details |
| POST | `/orders` | Place new order |
| PATCH | `/orders/{id}` | Update order status |

## Example Usage

### Create a Customer
```bash
curl -X POST "http://localhost:8000/api/v1/customers" \
  -H "Content-Type: application/json" \
  -d '{"name": "Alice", "email": "alice@example.com", "phone": "555-1234"}'
```

### View Products
```bash
curl "http://localhost:8000/api/v1/products"
```

### Place an Order
```bash
curl -X POST "http://localhost:8000/api/v1/orders" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": 1,
    "items": [
      {"product_id": 1, "quantity": 2},
      {"product_id": 2, "quantity": 1}
    ]
  }'
```

### Update Order Status
```bash
curl -X PATCH "http://localhost:8000/api/v1/orders/1" \
  -H "Content-Type: application/json" \
  -d '{"status": "preparing"}'
```

## Query Parameters

### Customer Filtering
- `?is_active=true` - Filter by active status
- `?search=alice` - Search in name or email
- `?page=1&page_size=10` - Pagination

### Product Filtering
- `?category=coffee` - Filter by category
- `?min_price=3.00` - Minimum price
- `?max_price=10.00` - Maximum price
- `?show_unavailable=true` - Include out-of-stock

### Order Filtering
- `?customer_id=1` - Filter by customer
- `?status=pending` - Filter by status

## Key Concepts Explained

### Why SQLAlchemy?

**Without SQLAlchemy (Raw SQL):**
```python
@app.get("/customers")
def get_customers():
    cursor.execute("SELECT * FROM customers")
    results = cursor.fetchall()
    # Manual mapping to dictionary...
```

**With SQLAlchemy (ORM):**
```python
@app.get("/customers")
def get_customers(db: Session = Depends(get_db)):
    return db.query(Customer).all()
```

Benefits:
- Type safety
- Database-agnostic (SQLite, PostgreSQL, MySQL)
- Relationship handling
- SQL injection protection
- migrations support

### Why Pydantic Schemas?

Schemas separate:
- **Database structure** (models.py)
- **API contracts** (schemas.py)

This separation allows:
- Different validation rules for input vs output
- Hiding internal fields (password_hash)
- Custom formatting of responses
- Backward compatibility

### Dependency Injection Flow

```
Request
   ↓
Route receives parameters
   ↓
Depends() calls dependency function
   ↓
get_db() provides Session
   ↓
Route uses session for DB operations
   ↓
Response formatted with Schema
   ↓
Session automatically closed
```

## Common Patterns

### Pagination
```python
@router.get("")
async def list_items(
    pagination: PaginationParams = Depends(),
    db: Session = Depends(get_db)
):
    items = db.query(Model)\
              .offset((pagination.page - 1) * pagination.page_size)\
              .limit(pagination.page_size)\
              .all()
    return PaginatedResponse.create(items, total, page, page_size)
```

### Soft Delete
```python
@router.delete("/{id}")
async def delete_item(id: int, db: Session = Depends(get_db)):
    item = db.query(Model).get(id)
    item.is_active = False  # Soft delete
    db.commit()
```

### Transaction (All or Nothing)
```python
@router.post("/orders")
async def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    # All these succeed or all fail together
    new_order = Order(...)
    db.add(new_order)
    db.flush()  # Get ID before committing
    
    for item in order.items:
        order_item = OrderItem(..., order_id=new_order.id)
        db.add(order_item)
    
    db.commit()  # Everything saved at once
```

## Testing Your API

### Using the Test Client

```python
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
```

### Running Tests

```bash
pytest -v
```

## Moving to Production

### Switch to PostgreSQL

1. Install driver:
```bash
pip install psycopg2-binary
```

2. Update DATABASE_URL:
```python
DATABASE_URL = "postgresql://user:password@localhost/coffee_shop"
```

### Environment Variables

Create `.env` file:
```env
DATABASE_URL=postgresql://user:password@localhost/coffee_shop
SECRET_KEY=your-secret-key
```

Load in code:
```python
from dotenv import load_dotenv
import os
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
```

## Homework Challenges

### Easy
1. Add an `PATCH /products/{id}/stock` endpoint to update inventory
2. Add filtering by `created_at` date for orders

### Medium
3. Add an `OrderItem` delete endpoint
4. Add a `GET /products/categories` endpoint to list unique categories
5. Add validation to prevent ordering out-of-stock items

### Hard
6. Implement hard delete (permanently remove records)
7. Add order history for customers (GET /customers/{id}/orders)
8. Implement order cancellation (refunds stock)

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [SQLAlchemy Tutorial](https://docs.sqlalchemy.org/tutorial/)

---

**Remember**: "First learn the concepts, then build the code. Understanding is the key to mastery!"


## running 
cd day10
pip install -r requirements.txt
uvicorn main:app --reload