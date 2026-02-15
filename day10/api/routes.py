"""
Day 10: API Routes - The Complete CRUD Application
===================================================

CONCEPTUAL BREAKDOWN:
--------------------
ROUTES define the ENDPOINTS of your API.
They connect HTTP methods (GET, POST, etc.) to database operations.

Think of routes as the MENU of a restaurant:
- /customers = Customer section
- /products = Product section  
- /orders = Order section

THE SERVICE LAYER:
-----------------
In professional backend development, we separate concerns:
- ROUTES: Handle HTTP requests/responses, validation
- SERVICE: Contains all business logic
- MODELS: Define database structure

This makes code:
- Easier to test
- Easier to maintain
- Reusable across different interfaces

FLOW EXAMPLE - Creating a Customer:
1. POST /customers with JSON body
2. CustomerCreate schema validates the JSON
3. Route calls CustomerService.create_customer()
4. Service handles business logic (checks email exists, creates record)
5. Service returns the created customer
6. CustomerResponse schema formats the output
7. JSON response returned with 201 Created
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional

# Import our database setup
from database import get_db

# Import our schemas (Pydantic)
from schemas import (
    CustomerCreate,
    CustomerUpdate,
    CustomerResponse,
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    OrderCreate,
    OrderUpdate,
    OrderResponse,
    OrderSummary,
    Message,
    ErrorResponse,
    PaginatedResponse,
    PaginationParams,
)

# Import our service layer
from api.service import (
    CustomerService,
    ProductService,
    OrderService,
)


# ============================================================
# ROUTERS SETUP
# ============================================================

router_customers = APIRouter(prefix="/customers", tags=["Customers"])
router_products = APIRouter(prefix="/products", tags=["Products"])
router_orders = APIRouter(prefix="/orders", tags=["Orders"])


# ============================================================
# CUSTOMER ROUTES
# ============================================================

@router_customers.get(
    "",
    response_model=PaginatedResponse,
    summary="List all customers",
    description="Get a paginated list of all customers"
)
async def list_customers(
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    search: Optional[str] = Query(None, description="Search in name or email"),
    pagination: PaginationParams = Depends(),
    db: Session = Depends(get_db)
):
    """LIST CUSTOMERS - READ with filtering and pagination."""
    # Delegate to service layer
    customers, total = CustomerService.list_customers(
        db=db,
        is_active=is_active,
        search=search,
        page=pagination.page,
        page_size=pagination.page_size
    )
    
    return PaginatedResponse.create(
        items=[CustomerResponse.from_orm(c) for c in customers],
        total=total,
        page=pagination.page,
        page_size=pagination.page_size
    )


@router_customers.get(
    "/{customer_id}",
    response_model=CustomerResponse,
    responses={404: {"model": ErrorResponse}}
)
async def get_customer(customer_id: int, db: Session = Depends(get_db)):
    """GET CUSTOMER - READ one customer by ID."""
    # Delegate to service layer
    customer = CustomerService.get_customer(db, customer_id)
    
    if not customer:
        raise HTTPException(
            status_code=404,
            detail=f"Customer with ID {customer_id} not found"
        )
    
    return CustomerResponse.from_orm(customer)


@router_customers.post(
    "",
    response_model=CustomerResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new customer",
    responses={400: {"model": ErrorResponse}}
)
async def create_customer(customer_data: CustomerCreate, db: Session = Depends(get_db)):
    """CREATE CUSTOMER - Add a new customer."""
    # Delegate to service layer
    try:
        customer = CustomerService.create_customer(db, customer_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return CustomerResponse.from_orm(customer)


@router_customers.put(
    "/{customer_id}",
    response_model=CustomerResponse,
    responses={404: {"model": ErrorResponse}}
)
async def update_customer(
    customer_id: int,
    update_data: CustomerUpdate,
    db: Session = Depends(get_db)
):
    """UPDATE CUSTOMER - Modify customer information."""
    # Delegate to service layer
    customer = CustomerService.update_customer(db, customer_id, update_data)
    
    if not customer:
        raise HTTPException(
            status_code=404,
            detail=f"Customer with ID {customer_id} not found"
        )
    
    return CustomerResponse.from_orm(customer)


@router_customers.delete(
    "/{customer_id}",
    response_model=Message,
    responses={404: {"model": ErrorResponse}}
)
async def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    """DELETE CUSTOMER - Soft delete (sets is_active=False)."""
    # Delegate to service layer
    success = CustomerService.delete_customer(db, customer_id)
    
    if not success:
        raise HTTPException(
            status_code=404,
            detail=f"Customer with ID {customer_id} not found"
        )
    
    return {"message": f"Customer {customer_id} deleted successfully"}


# ============================================================
# PRODUCT ROUTES
# ============================================================

@router_products.get("", response_model=List[ProductResponse])
async def list_products(
    category: Optional[str] = Query(None, description="Filter by category"),
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    show_unavailable: bool = Query(False, description="Include out-of-stock items"),
    db: Session = Depends(get_db)
):
    """LIST PRODUCTS - Read all products with optional filters."""
    # Delegate to service layer
    products = ProductService.list_products(
        db=db,
        category=category,
        min_price=min_price,
        max_price=max_price,
        show_unavailable=show_unavailable
    )
    
    return [ProductResponse.from_orm(p) for p in products]


@router_products.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int, db: Session = Depends(get_db)):
    """GET PRODUCT - Read one product by ID."""
    # Delegate to service layer
    product = ProductService.get_product(db, product_id)
    
    if not product:
        raise HTTPException(status_code=404, detail=f"Product {product_id} not found")
    
    return ProductResponse.from_orm(product)


@router_products.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    """CREATE PRODUCT - Add a new product."""
    # Delegate to service layer
    new_product = ProductService.create_product(db, product)
    
    return ProductResponse.from_orm(new_product)


@router_products.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    update: ProductUpdate,
    db: Session = Depends(get_db)
):
    """UPDATE PRODUCT - Modify product details."""
    # Delegate to service layer
    product = ProductService.update_product(db, product_id, update)
    
    if not product:
        raise HTTPException(status_code=404, detail=f"Product {product_id} not found")
    
    return ProductResponse.from_orm(product)


@router_products.delete("/{product_id}", response_model=Message)
async def delete_product(product_id: int, db: Session = Depends(get_db)):
    """DELETE PRODUCT - Soft delete."""
    # Delegate to service layer
    success = ProductService.delete_product(db, product_id)
    
    if not success:
        raise HTTPException(status_code=404, detail=f"Product {product_id} not found")
    
    return {"message": f"Product {product_id} deleted"}


# ============================================================
# ORDER ROUTES
# ============================================================

@router_orders.get("", response_model=List[OrderSummary])
async def list_orders(
    customer_id: Optional[int] = Query(None, description="Filter by customer"),
    status: Optional[str] = Query(None, description="Filter by status"),
    db: Session = Depends(get_db)
):
    """LIST ORDERS - Read all orders with optional filters."""
    # Delegate to service layer
    orders = OrderService.list_orders(
        db=db,
        customer_id=customer_id,
        status=status
    )
    
    return orders


@router_orders.get("/{order_id}", response_model=OrderResponse)
async def get_order(order_id: int, db: Session = Depends(get_db)):
    """GET ORDER - Read full order details."""
    # Delegate to service layer
    order = OrderService.get_order(db, order_id)
    
    if not order:
        raise HTTPException(status_code=404, detail=f"Order {order_id} not found")
    
    return OrderResponse.from_orm(order)


@router_orders.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(order_data: OrderCreate, db: Session = Depends(get_db)):
    """CREATE ORDER - Place a new order with transaction."""
    # Delegate to service layer
    try:
        new_order = OrderService.create_order(db, order_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return OrderResponse.from_orm(new_order)


@router_orders.patch("/{order_id}", response_model=OrderResponse)
async def update_order_status(
    order_id: int,
    update: OrderUpdate,
    db: Session = Depends(get_db)
):
    """UPDATE ORDER - Modify order status."""
    # Delegate to service layer
    if not update.status:
        raise HTTPException(status_code=400, detail="Status is required")
    
    order = OrderService.update_order_status(db, order_id, update.status)
    
    if not order:
        raise HTTPException(status_code=404, detail=f"Order {order_id} not found")
    
    return OrderResponse.from_orm(order)


# ============================================================
# Socratic Discussion Questions
# ============================================================

"""
CLASS DISCUSSION: Test Your Understanding!
-----------------------------------------

1. What does the service layer do? Why is it separate from routes?
   (Hint: Separation of concerns!)

2. In list_customers, we now call CustomerService.list_customers().
   What benefit does this provide over having the query in the route?
   (Hint: Reusability and testability!)

3. What is the difference between ValueError raised in service vs HTTPException in route?
   (Hint: Where should each type of error be handled?)

4. Why do we still use schemas like CustomerResponse in routes?
   (Hint: What does from_orm() do?)

5. In create_order, we catch ValueError and convert to HTTPException.
   Why not just raise HTTPException in the service?
   (Hint: What if the service is called from a non-HTTP context?)

6. What would happen if we didn't use the service layer and had all logic in routes?
   (Hint: Consider adding a GraphQL API or background job!)

7. The service methods return Model objects, not Response schemas.
   Where does the conversion happen?
   (Hint: Look at the route handlers!)

8. Why is CustomerService methods @staticmethod?
   (Hint: Do we need to maintain state between requests?)

9. In the service layer, we check for existing customers/products.
   Could this cause race conditions?
   (Hint: What if two requests come in at the exact same time?)

10. What's the benefit of having separate services for Customer, Product, and Order?
    (Hint: What if you need to add a new endpoint that uses multiple services?)
"""
