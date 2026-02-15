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

THE CRUD OPERATIONS:
- C reate: POST /resource (add new data)
- R ead: GET /resource (retrieve data)
- U pdate: PUT/PATCH /resource/{id} (modify data)
- D elete: DELETE /resource/{id} (remove data)

FLOW EXAMPLE - Creating a Customer:
1. POST /customers with JSON body
2. CustomerCreate schema validates the JSON
3. get_db() provides a database session
4. SQLAlchemy creates a new Customer object
5. Session.add() and Session.commit() save to DB
6. CustomerResponse schema formats the output
7. JSON response returned with 201 Created
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional

# Import our database setup
from database import get_db

# Import our models (SQLAlchemy)
from models import Customer as CustomerModel
from models import Product as ProductModel
from models import Order as OrderModel
from models import OrderItem as OrderItemModel

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
    OrderItemCreate
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
    query = db.query(CustomerModel)
    
    if is_active is not None:
        query = query.filter(CustomerModel.is_active == is_active)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (CustomerModel.name.ilike(search_term)) |
            (CustomerModel.email.ilike(search_term))
        )
    
    total = query.count()
    offset = (pagination.page - 1) * pagination.page_size
    customers = query.order_by(CustomerModel.created_at.desc())\
                     .offset(offset)\
                     .limit(pagination.page_size)\
                     .all()
    
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
    customer = db.query(CustomerModel).filter(
        CustomerModel.id == customer_id
    ).first()
    
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
    existing = db.query(CustomerModel).filter(
        CustomerModel.email == customer_data.email
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Customer with email '{customer_data.email}' already exists"
        )
    
    customer = CustomerModel(**customer_data.model_dump())
    db.add(customer)
    
    try:
        db.commit()
        db.refresh(customer)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Could not create customer")
    
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
    customer = db.query(CustomerModel).filter(
        CustomerModel.id == customer_id
    ).first()
    
    if not customer:
        raise HTTPException(
            status_code=404,
            detail=f"Customer with ID {customer_id} not found"
        )
    
    update_dict = update_data.model_dump(exclude_unset=True)
    
    for field, value in update_dict.items():
        setattr(customer, field, value)
    
    db.commit()
    db.refresh(customer)
    
    return CustomerResponse.from_orm(customer)


@router_customers.delete(
    "/{customer_id}",
    response_model=Message,
    responses={404: {"model": ErrorResponse}}
)
async def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    """DELETE CUSTOMER - Soft delete (sets is_active=False)."""
    customer = db.query(CustomerModel).filter(
        CustomerModel.id == customer_id
    ).first()
    
    if not customer:
        raise HTTPException(
            status_code=404,
            detail=f"Customer with ID {customer_id} not found"
        )
    
    customer.is_active = False
    db.commit()
    
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
    query = db.query(ProductModel)
    
    if category:
        query = query.filter(ProductModel.category == category)
    
    if min_price is not None:
        query = query.filter(ProductModel.price >= min_price)
    
    if max_price is not None:
        query = query.filter(ProductModel.price <= max_price)
    
    if not show_unavailable:
        query = query.filter(ProductModel.is_available == True)
    
    products = query.order_by(ProductModel.name).all()
    
    return [ProductResponse.from_orm(p) for p in products]


@router_products.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int, db: Session = Depends(get_db)):
    """GET PRODUCT - Read one product by ID."""
    product = db.query(ProductModel).filter(
        ProductModel.id == product_id
    ).first()
    
    if not product:
        raise HTTPException(status_code=404, detail=f"Product {product_id} not found")
    
    return ProductResponse.from_orm(product)


@router_products.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    """CREATE PRODUCT - Add a new product."""
    new_product = ProductModel(**product.model_dump())
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    
    return ProductResponse.from_orm(new_product)


@router_products.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    update: ProductUpdate,
    db: Session = Depends(get_db)
):
    """UPDATE PRODUCT - Modify product details."""
    product = db.query(ProductModel).filter(
        ProductModel.id == product_id
    ).first()
    
    if not product:
        raise HTTPException(status_code=404, detail=f"Product {product_id} not found")
    
    update_dict = update.model_dump(exclude_unset=True)
    
    for field, value in update_dict.items():
        setattr(product, field, value)
    
    db.commit()
    db.refresh(product)
    
    return ProductResponse.from_orm(product)


@router_products.delete("/{product_id}", response_model=Message)
async def delete_product(product_id: int, db: Session = Depends(get_db)):
    """DELETE PRODUCT - Soft delete."""
    product = db.query(ProductModel).filter(
        ProductModel.id == product_id
    ).first()
    
    if not product:
        raise HTTPException(status_code=404, detail=f"Product {product_id} not found")
    
    product.is_available = False
    db.commit()
    
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
    query = db.query(OrderModel)
    
    if customer_id:
        query = query.filter(OrderModel.customer_id == customer_id)
    
    if status:
        query = query.filter(OrderModel.status == status)
    
    orders = query.order_by(OrderModel.created_at.desc()).all()
    
    summaries = []
    for order in orders:
        item_count = db.query(OrderItemModel).filter(
            OrderItemModel.order_id == order.id
        ).count()
        
        summaries.append(OrderSummary(
            id=order.id,
            customer_id=order.customer_id,
            status=order.status,
            total_amount=order.total_amount,
            item_count=item_count
        ))
    
    return summaries


@router_orders.get("/{order_id}", response_model=OrderResponse)
async def get_order(order_id: int, db: Session = Depends(get_db)):
    """GET ORDER - Read full order details."""
    order = db.query(OrderModel).filter(OrderModel.id == order_id).first()
    
    if not order:
        raise HTTPException(status_code=404, detail=f"Order {order_id} not found")
    
    return OrderResponse.from_orm(order)


@router_orders.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(order_data: OrderCreate, db: Session = Depends(get_db)):
    """CREATE ORDER - Place a new order with transaction."""
    # Verify customer exists
    customer = db.query(CustomerModel).filter(
        CustomerModel.id == order_data.customer_id
    ).first()
    
    if not customer:
        raise HTTPException(
            status_code=404,
            detail=f"Customer {order_data.customer_id} not found"
        )
    
    # Calculate total and create order items
    total = 0.0
    order_items = []
    
    for item in order_data.items:
        product = db.query(ProductModel).filter(
            ProductModel.id == item.product_id
        ).first()
        
        if not product:
            raise HTTPException(
                status_code=404,
                detail=f"Product {item.product_id} not found"
            )
        
        if not product.is_available or product.stock < item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Product {product.name} not available"
            )
        
        item_total = product.price * item.quantity
        total += item_total
        
        order_items.append({
            "product_id": product.id,
            "quantity": item.quantity,
            "price_at_order": product.price
        })
    
    # Create the order
    new_order = OrderModel(
        customer_id=order_data.customer_id,
        total_amount=total,
        status="pending"
    )
    
    db.add(new_order)
    db.flush()  # Get the order ID
    
    # Create order items
    for item_data in order_items:
        order_item = OrderItemModel(
            order_id=new_order.id,
            **item_data
        )
        db.add(order_item)
        
        # Update stock
        product = db.query(ProductModel).get(item_data["product_id"])
        product.stock -= item_data["quantity"]
    
    db.commit()
    db.refresh(new_order)
    
    return OrderResponse.from_orm(new_order)


@router_orders.patch("/{order_id}", response_model=OrderResponse)
async def update_order_status(
    order_id: int,
    update: OrderUpdate,
    db: Session = Depends(get_db)
):
    """UPDATE ORDER - Modify order status."""
    order = db.query(OrderModel).filter(OrderModel.id == order_id).first()
    
    if not order:
        raise HTTPException(status_code=404, detail=f"Order {order_id} not found")
    
    if update.status:
        order.status = update.status
    
    db.commit()
    db.refresh(order)
    
    return OrderResponse.from_orm(order)


# ============================================================
# Socratic Discussion Questions
# ============================================================
"""
CLASS DISCUSSION: Test Your Understanding!
-----------------------------------------

1. What does get_db() do? Why is it a dependency?
   (Hint: What happens if we don't use it?)

2. In list_customers, we use PaginationParams as a dependency.
   How does FastAPI know what values to pass?
   (Hint: Query parameters!)

3. What is the difference between PUT and PATCH?
   (Hint: PUT replaces, PATCH partially updates)

4. Why do we use db.flush() before creating order items?
   (Hint: What ID does the order need before creating items?)

5. In the order creation, what happens if one product is out of stock?
   (Hint: Look at the validation loop!)

6. What is the purpose of responses={404: {...}} in decorators?
   (Hint: Documentation!)

7. Why do we use from_orm() instead of just returning the model?
   (Hint: Pydantic needs to convert SQLAlchemy objects!)

8. What does model_dump(exclude_unset=True) do in updates?
   (Hint: What if a field is NOT in the request?)

9. Why do we check is_active in list_customers but use hard ID lookup in get_customer?
   (Hint: Performance and use cases!)

10. What is the relationship between router and APIRouter?
    (Hint: How are prefixes applied?)

11. In the order creation, we calculate total_amount.
    What if we didn't and just trusted the client's number?
    (Hint: Security concern!)

12. What is the difference between Query and Path parameters?
    (Hint: Where do they appear in the URL?)

13. Why do we return OrderSummary for list but OrderResponse for get?
    (Hint: Performance vs completeness!)

14. What is the purpose of ilike() in the search filter?
    (Hint: Case sensitivity!)

15. What error code is returned when creation fails due to duplicate email?
    (Hint: IntegrityError!)

BONUS CHALLENGE:
----------------
Add a DELETE /orders/{order_id} endpoint that cancels an order
(if status is still 'pending'). What validations would you add?
"""
