"""
Day 10: Pydantic Schemas (Data Validation)
===========================================

CONCEPTUAL BREAKDOWN:
--------------------
SCHEMAS define what data your API ACCEPTS and RETURNS.
They validate incoming data and format outgoing data.

Think of schemas as FORM VALIDATORS:
- Input schemas: Check if the data you send is valid
- Output schemas: Control what data is returned
- Both: Prevent bad data from entering your system

MODEL vs SCHEMA:
- Model (SQLAlchemy): Database structure (what data looks like in DB)
- Schema (Pydantic): API contract (what data looks like in API)

Why both?
- Models: Define tables, relationships, constraints
- Schemas: Validate, serialize, control visibility

THE FLOW:
1. Client sends JSON request
2. Pydantic schema validates the JSON
3. If valid, convert to Python object
4. Use SQLAlchemy model to save to database
5. Use Pydantic schema to format response
6. Return JSON to client

COFFEE SHOP SCHEMAS:
- CustomerCreate: Data needed to create a customer
- CustomerResponse: Data returned when reading a customer
- ProductCreate: Data needed to add a product
- ProductResponse: Data returned for products
- OrderCreate: Complex schema with nested items
- OrderResponse: Complete order with all details

ANALOGY - Restaurant Menu:
- Schema is like the menu description:
  - "Burger: $10, includes bun, patty, lettuce"
  - Tells the kitchen what to expect
  - Tells the customer what they'll receive
"""

from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import List, Optional

# ============================================================
# CUSTOMER SCHEMAS
# ============================================================

class CustomerBase(BaseModel):
    """Common fields for all customer schemas"""
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr  # Pydantic validates email format automatically!
    phone: Optional[str] = Field(None, max_length=20)


class CustomerCreate(CustomerBase):
    """Schema for creating a new customer"""
    # All fields from CustomerBase + nothing extra
    # phone is optional, name and email are required
    pass

class CustomerUpdate(BaseModel):
    """Schema for updating a customer (all fields optional)"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    is_active: Optional[bool] = None


class CustomerResponse(CustomerBase):
    """Schema for customer responses (what we return to client)"""
    id: int
    created_at: datetime
    is_active: bool
    
    class Config:
        # Tells Pydantic to read from ORM model attributes
        # This allows: CustomerResponse.from_orm(db_customer)
        from_attributes = True


# ============================================================
# PRODUCT SCHEMAS
# ============================================================

class ProductBase(BaseModel):
    """Common fields for all product schemas"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    price: float = Field(..., gt=0, description="Price must be greater than 0")
    category: str = Field(default="coffee", max_length=50)


class ProductCreate(ProductBase):
    """Schema for creating a product"""
    stock: int = Field(default=0, ge=0)
    is_available: bool = True


class ProductUpdate(BaseModel):
    """Schema for updating a product"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    category: Optional[str] = None
    stock: Optional[int] = Field(None, ge=0)
    is_available: Optional[bool] = None


class ProductResponse(ProductBase):
    """Schema for product responses"""
    id: int
    stock: int
    is_available: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================
# ORDER ITEM SCHEMAS
# ============================================================

class OrderItemBase(BaseModel):
    """Base schema for order items"""
    product_id: int = Field(..., gt=0)
    quantity: int = Field(default=1, ge=1, le=100)


class OrderItemCreate(OrderItemBase):
    """Schema for creating an order item"""
    pass


class OrderItemResponse(OrderItemBase):
    """Schema for order item responses"""
    id: int
    price_at_order: float
    product: ProductResponse  # Nested response!
    
    class Config:
        from_attributes = True


# ============================================================
# ORDER SCHEMAS
# ============================================================

class OrderBase(BaseModel):
    """Base schema for orders"""
    customer_id: int = Field(..., gt=0)


class OrderCreate(BaseModel):
    """Schema for creating an order"""
    customer_id: int = Field(..., gt=0)
    items: List[OrderItemCreate] = Field(..., min_length=1, description="At least one item required")
    
    def calculate_total(self, db) -> float:
        """Calculate total price based on current product prices"""
        total = 0.0
        for item in self.items:
            # In real app, query product price from DB
            total += item.quantity * 10.0  # Placeholder!
        return total


class OrderUpdate(BaseModel):
    """Schema for updating an order status"""
    status: Optional[str] = Field(
        None, 
        pattern="^(pending|preparing|ready|completed|cancelled)$"
    )


class OrderResponse(OrderBase):
    """Schema for order responses (full details)"""
    id: int
    status: str
    total_amount: float
    created_at: datetime
    updated_at: datetime
    customer: CustomerResponse  # Nested customer!
    items: List[OrderItemResponse]  # Nested items!
    
    class Config:
        from_attributes = True


class OrderSummary(BaseModel):
    """Lightweight order response (no nested details)"""
    id: int
    customer_id: int
    status: str
    total_amount: float
    item_count: int  # Derived field!
    
    class Config:
        from_attributes = True


# ============================================================
# PAGINATION SCHEMAS
# ============================================================

class PaginationParams(BaseModel):
    """Query parameters for pagination"""
    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=10, ge=1, le=100, description="Items per page")


class PaginatedResponse(BaseModel):
    """Generic paginated response wrapper"""
    items: List
    total: int
    page: int
    page_size: int
    total_pages: int
    
    @classmethod
    def create(cls, items: List, total: int, page: int, page_size: int):
        """Helper to create paginated response"""
        total_pages = (total + page_size - 1) // page_size  # Ceiling division
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )


# ============================================================
# MESSAGE SCHEMA (Generic responses)
# ============================================================

class Message(BaseModel):
    """Generic message response"""
    message: str


class ErrorResponse(BaseModel):
    """Error response schema"""
    detail: str


# ============================================================
# THE 'AHA!' MOMENT: Common Schema Mistakes
# ============================================================
"""
⚠️  COMMON MISTAKES WITH SCHEMAS! ⚠️

❌ MISTAKE 1: Exposing internal fields in responses

    # WRONG - User sees internal fields like password_hash!
    class UserResponse(BaseModel):
        username: str
        password_hash: str  # ❌ SECURITY RISK!
    
    # CORRECT - Only expose necessary fields
    class UserResponse(BaseModel):
        id: int
        username: str
        email: str  # But NOT password!
        # password_hash is NOT included!

❌ MISTAKE 2: Using Input schemas for Output

    # WRONG - Input schema has required fields that aren't in DB
    class ProductInput(BaseModel):
        name: str
        description: str
        price: float
        import_id: int  # Internal tracking ID!
    
    # Output includes tracking ID - CONFUSING for API consumers!
    
    # CORRECT - Separate Input and Output schemas
    class ProductInput(BaseModel):
        name: str
        description: str
        price: float
    
    class ProductOutput(BaseModel):
        id: int
        name: str
        description: str
        price: float
        created_at: datetime

❌ MISTAKE 3: Forgetting validation

    # WRONG - No constraints on data!
    class UserCreate(BaseModel):
        name: str  # Can be empty string!
        email: str  # Can be invalid format!
        age: int  # Can be negative!
    
    # CORRECT - Add meaningful constraints
    class UserCreate(BaseModel):
        name: str = Field(..., min_length=1)
        email: EmailStr  # Built-in email validation!
        age: int = Field(..., ge=0)

❌ MISTAKE 4: Not handling optional fields properly

    # WRONG - Can't update just one field!
    class UserUpdate(BaseModel):
        name: str
        email: str
        phone: str
        # If I only want to update phone, I must provide ALL fields!
    
    # CORRECT - Make fields Optional
    class UserUpdate(BaseModel):
        name: Optional[str] = None
        email: Optional[str] = None
        phone: Optional[str] = None

❌ MISTAKE 5: Not using from_orm for ORM objects

    # WRONG - Manual conversion!
    @app.get("/products")
    def get_products(db: Session):
        products = db.query(Product).all()
        return [{"id": p.id, "name": p.name} for p in products]
    
    # CORRECT - Use from_orm!
    @app.get("/products")
    def get_products(db: Session):
        products = db.query(Product).all()
        return [ProductResponse.from_orm(p) for p in products]

✅ BEST PRACTICES:
1. Separate schemas for input (Create) and output (Response)
2. Use Field() for meaningful constraints and descriptions
3. Use EmailStr for email validation
4. Never expose sensitive data (passwords, hashes, internal IDs)
5. Use Optional[] for fields that can be updated
6. Use from_orm() or Config.from_attributes = True for ORM objects
7. Add helpful descriptions for API documentation
"""

# ============================================================
# Socratic Discussion Questions
# ============================================================
"""
CLASS DISCUSSION: Test Your Understanding!
-----------------------------------------

1. What's the difference between a Model and a Schema?
   (Hint: Where does each one live? What purpose does each serve?)

2. In CustomerCreate, we use EmailStr for the email field.
   What happens if someone sends: "not-an-email"?
   (Hint: Does the request succeed or fail?)

3. Why do we have both CustomerCreate and CustomerResponse?
   Why not one schema for both?
   (Hint: What fields are in the database but NOT in the create request?)

4. In OrderItemResponse, we have a nested ProductResponse.
   What happens if the product is deleted from the database?
   (Hint: Can we still return the order?)

5. The ProductCreate schema has stock: int = Field(default=0, ge=0).
   What do default and ge mean?
   (Hint: What if someone sends stock: -5?)

6. Why is CustomerUpdate different from CustomerCreate?
   Why are fields Optional in update but not in create?
   (Hint: When creating, what must we have? When updating, what must we provide?)

7. Look at OrderCreate.calculate_total().
   Why would we want to calculate total at the schema level?
   (Hint: What if product prices change after order is placed?)

8. What's the purpose of PaginatedResponse?
   Why not just return a list of items?
   (Hint: What if you have 10,000 products?)

9. In the schema examples, we use Field(..., description="...").
   Where would this description appear?
   (Hint: Check the automatic API documentation at /docs!)

10. Why is password_hash NOT included in any response schema?
    (Hint: What's the security implication of exposing hash?)

11. We have OrderResponse with nested items and nested customer.
    What's the trade-off of this approach?
    (Hint: One request vs multiple requests for related data)

12. In the PaginatedResponse.create() method, how is total_pages calculated?
    (Hint: What if total=25 and page_size=10? How many pages?)

13. What is from_attributes = True doing in the Config class?
    Why do we need it for ORM objects?
    (Hint: Does Pydantic know about SQLAlchemy by default?)

14. Look at OrderItemCreate.product_id.
    What happens if someone sends product_id: 9999?
    Does the schema validate this?
    (Hint: Schema checks TYPE, not EXISTENCE in DB!)

15. We use List[OrderItemCreate] for order items.
    What if someone sends an empty list: items: []?
    (Hint: min_length=1 - what does this prevent?)

BONUS CHALLENGE:
----------------
Add a "Search" query parameter to the products endpoint.
Create a ProductSearch schema that:
1. Accepts a search query string
2. Has optional filters (min_price, max_price, category)
3. Returns products matching the criteria
"""
