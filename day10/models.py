"""
Day 10: SQLAlchemy ORM Models
=============================

CONCEPTUAL BREAKDOWN:
--------------------
MODELS define the STRUCTURE of your database tables.
Each model class = One database table.
Each model attribute = One column in that table.

Think of models as BLUEPRANS for your data:
- Class name = Table name
- Class attributes = Column names
- Attribute types = Column types (String, Integer, etc.)
- Instances = Rows in the table

KEY COMPONENTS:
- __tablename__: The actual name of the table in the database
- Column: Defines a column with its type and constraints
- relationship: Links related tables (foreign keys)
- ForeignKey: Points to a related table's primary key

COFFEE SHOP DATA MODEL:
- Customer: People who buy coffee
- Product: Coffee drinks and items we sell
- Order: Records of purchases

RELATIONSHIPS:
- One Customer can have Many Orders (1:N)
- One Order can have Many Products (M:N, via OrderItem)

ANALOGY - Restaurant:
- Customer = Diner
- Product = Menu Item
- Order = The receipt/dishes ordered
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


# ============================================================
# MODEL 1: Customer (The people buying coffee)
# ============================================================
class Customer(Base):
    """
    CUSTOMER MODEL: Represents a coffee shop customer.
    
    Table name: customers (SQLAlchemy adds 's' by convention)
    
    Relationships:
    - orders: All orders placed by this customer (1:N)
    """
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)  # Can't be empty
    email = Column(String(100), unique=True, nullable=False, index=True)
    phone = Column(String(20), nullable=True)  # Optional
    created_at = Column(DateTime, default=datetime.utcnow)  # Auto-set on creation
    is_active = Column(Boolean, default=True)  # For soft deletes
    
    # RELATIONSHIP: Link to orders
    # "back_populates" creates a two-way link
    orders = relationship("Order", back_populates="customer")
    
    def __repr__(self):
        return f"<Customer(name='{self.name}', email='{self.email}')>"


# ============================================================
# MODEL 2: Product (Coffee drinks and items)
# ============================================================
class Product(Base):
    """
    PRODUCT MODEL: Represents items we sell.
    
    Table name: products
    
    Categories: coffee, tea, pastry, merchandise
    """
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    price = Column(Float, nullable=False)
    category = Column(String(50), default="coffee")  # coffee, tea, pastry
    stock = Column(Integer, default=0)  # 0 = out of stock
    is_available = Column(Boolean, default=True)  # Can be ordered?
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # RELATIONSHIP: Products in orders (defined in OrderItem)
    order_items = relationship("OrderItem", back_populates="product")
    
    def __repr__(self):
        return f"<Product(name='{self.name}', price={self.price})>"


# ============================================================
# MODEL 3: Order (Customer purchases)
# ============================================================
class Order(Base):
    """
    ORDER MODEL: Represents a customer order.
    
    Table name: orders
    
    Status values: pending, preparing, ready, completed, cancelled
    
    Relationship to Customer: Foreign Key
    - customer_id points to customers.id
    """
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    status = Column(String(50), default="pending")  # pending, preparing, ready, completed
    total_amount = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # RELATIONSHIP: Link back to customer
    customer = relationship("Customer", back_populates="orders")
    
    # RELATIONSHIP: Items in this order
    items = relationship("OrderItem", back_populates="order")
    
    def __repr__(self):
        return f"<Order(id={self.id}, customer_id={self.customer_id}, status='{self.status}')>"


# ============================================================
# MODEL 4: OrderItem (Junction table for Order-Product M:N)
# ============================================================
class OrderItem(Base):
    """
    ORDERITEM MODEL: Links Orders to Products.
    
    Table name: order_items
    
    This is a JUNCTION TABLE for a Many-to-Many relationship:
    - One Order has many OrderItems
    - One Product has many OrderItems
    
    Stores: quantity and price at time of order
    
    Why a separate table?
    - Orders have a status (pending, ready, etc.)
    - Products have stock levels
    - OrderItem tracks what was ordered, at what price
    """
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, default=1)
    price_at_order = Column(Float, nullable=False)  # Snapshot of price!
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # RELATIONSHIPS
    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")
    
    def __repr__(self):
        return f"<OrderItem(order_id={self.order_id}, product_id={self.product_id}, qty={self.quantity})>"

# ============================================================
# THE 'AHA!' MOMENT: Common Model Mistakes
# ============================================================
"""
⚠️  COMMON MISTAKES WITH MODELS! ⚠️

❌ MISTAKE 1: Forgetting to define __tablename__

    # WRONG - Will SQLAlchemy know the table name?
    class Customer(Base):
        id = Column(Integer, primary_key=True)
        name = Column(String(100))
    
    # CORRECT - Explicit table name
    class Customer(Base):
        __tablename__ = "customers"
        id = Column(Integer, primary_key=True)
        name = Column(String(100))

❌ MISTAKE 2: Wrong data types

    # WRONG - Don't use Python types directly!
    class Product(Base):
        price = float  # ❌ Python type, not SQLAlchemy!
        in_stock = bool  # ❌ Wrong!
    
    # CORRECT - Use SQLAlchemy column types
    class Product(Base):
        price = Column(Float)  # ✅ Correct!
        in_stock = Column(Boolean)  # ✅ Correct!

❌ MISTAKE 3: Forgetting ForeignKey relationships

    # WRONG - No connection between tables!
    class Order(Base):
        customer_id = Column(Integer)  # ❌ Just an integer!
        # How do we know this refers to customers.id?
    
    # CORRECT - ForeignKey points to another table
    class Order(Base):
        customer_id = Column(Integer, ForeignKey("customers.id"))  # ✅

❌ MISTAKE 4: Circular imports

    # models.py imports from database.py
    # database.py imports from models.py
    # → CIRCULAR IMPORT ERROR!
    
    # SOLUTION:
    # 1. Database.py defines Base only
    # 2. Models.py imports Base from database
    # 3. Routes import models and schemas

❌ MISTAKE 5: Using Model instances directly in API responses

    # WRONG - Returns SQLAlchemy objects with internal state!
    @app.get("/products")
    def get_products():
        return db.query(Product).all()  # Returns model instances!
    
    # CORRECT - Use Pydantic schemas to filter/validate output
    @app.get("/products")
    def get_products(db: Session = Depends(get_db)):
        products = db.query(Product).all()
        return [ProductSchema.from_orm(p) for p in products]
    # Or better: return ProductSchema.from_ormlist(products)

✅ BEST PRACTICES:
1. Keep models focused on database structure only
2. Use separate Pydantic schemas for API input/output
3. Use relationships for related data, not raw IDs
4. Index columns you'll search frequently (email, id)
5. Use constraints (nullable, unique) appropriately
6. Soft deletes (is_active) instead of actual deletion
"""
