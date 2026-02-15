"""
Day 10: Service Layer - Business Logic
=======================================

CONCEPTUAL BREAKDOWN:
--------------------
The SERVICE LAYER acts as an intermediary between API routes and data access.
It contains all business logic, validation, and database operations.

Think of it like a RESTAURANT:
- Routes = The Waiter (takes orders, serves food)
- Service = The Kitchen (prepares the food, follows recipes)
- Models = The Pantry (raw ingredients)

WHY USE A SERVICE LAYER?
- Separation of Concerns: Routes only handle HTTP, services handle business logic
- Reusability: Services can be called from multiple routes or other services
- Testability: Easy to test business logic without HTTP overhead
- Maintainability: Changes to business logic don't affect API structure

SERVICE PATTERN:
- Each entity (Customer, Product, Order) has its own service class
- Service methods take data and db session, return processed results
- Routes call services and handle HTTP responses
"""

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional, Tuple

# Import models
from models import Customer as CustomerModel
from models import Product as ProductModel
from models import Order as OrderModel
from models import OrderItem as OrderItemModel

# Import schemas for type hints and data transfer
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
)


# ============================================================
# CUSTOMER SERVICE
# ============================================================

class CustomerService:
    """
    CustomerService handles all business logic related to customers.
    
    This service is responsible for:
    - Creating new customers
    - Retrieving customer information
    - Updating customer details
    - Soft-deleting customers (setting is_active=False)
    - Filtering and searching customers
    """
    
    @staticmethod
    def list_customers(
        db: Session,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 10
    ) -> Tuple[List[CustomerModel], int]:
        """
        List customers with optional filtering and pagination.
        
        Args:
            db: Database session
            is_active: Filter by active status
            search: Search term for name or email
            page: Page number (1-indexed)
            page_size: Number of items per page
            
        Returns:
            Tuple of (list of customers, total count)
        """
        query = db.query(CustomerModel)
        
        # Apply filters
        if is_active is not None:
            query = query.filter(CustomerModel.is_active == is_active)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (CustomerModel.name.ilike(search_term)) |
                (CustomerModel.email.ilike(search_term))
            )
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * page_size
        customers = (
            query
            .order_by(CustomerModel.created_at.desc())
            .offset(offset)
            .limit(page_size)
            .all()
        )
        
        return customers, total
    
    @staticmethod
    def get_customer(db: Session, customer_id: int) -> Optional[CustomerModel]:
        """
        Get a single customer by ID.
        
        Args:
            db: Database session
            customer_id: ID of the customer to retrieve
            
        Returns:
            Customer object if found, None otherwise
        """
        return db.query(CustomerModel).filter(
            CustomerModel.id == customer_id
        ).first()
    
    @staticmethod
    def get_customer_by_email(db: Session, email: str) -> Optional[CustomerModel]:
        """
        Get a customer by email address.
        
        Args:
            db: Database session
            email: Email address to search for
            
        Returns:
            Customer object if found, None otherwise
        """
        return db.query(CustomerModel).filter(
            CustomerModel.email == email
        ).first()
    
    @staticmethod
    def create_customer(db: Session, customer_data: CustomerCreate) -> CustomerModel:
        """
        Create a new customer.
        
        Args:
            db: Database session
            customer_data: Validated customer creation data
            
        Returns:
            Created customer object
            
        Raises:
            ValueError: If customer with email already exists
        """
        # Check if email already exists
        existing = CustomerService.get_customer_by_email(db, customer_data.email)
        if existing:
            raise ValueError(f"Customer with email '{customer_data.email}' already exists")
        
        # Create customer
        customer = CustomerModel(**customer_data.model_dump())
        db.add(customer)
        
        try:
            db.commit()
            db.refresh(customer)
        except IntegrityError:
            db.rollback()
            raise ValueError("Could not create customer")
        
        return customer
    
    @staticmethod
    def update_customer(
        db: Session,
        customer_id: int,
        update_data: CustomerUpdate
    ) -> Optional[CustomerModel]:
        """
        Update an existing customer.
        
        Args:
            db: Database session
            customer_id: ID of customer to update
            update_data: Fields to update
            
        Returns:
            Updated customer object if found, None otherwise
        """
        customer = CustomerService.get_customer(db, customer_id)
        if not customer:
            return None
        
        # Apply updates (only non-None fields)
        update_dict = update_data.model_dump(exclude_unset=True)
        
        for field, value in update_dict.items():
            setattr(customer, field, value)
        
        db.commit()
        db.refresh(customer)
        
        return customer
    
    @staticmethod
    def delete_customer(db: Session, customer_id: int) -> bool:
        """
        Soft delete a customer (set is_active=False).
        
        Args:
            db: Database session
            customer_id: ID of customer to delete
            
        Returns:
            True if customer was found and deleted, False otherwise
        """
        customer = CustomerService.get_customer(db, customer_id)
        if not customer:
            return False
        
        customer.is_active = False
        db.commit()
        
        return True


# ============================================================
# PRODUCT SERVICE
# ============================================================

class ProductService:
    """
    ProductService handles all business logic related to products.
    
    This service is responsible for:
    - Creating new products
    - Retrieving product information
    - Updating product details
    - Soft-deleting products (setting is_available=False)
    - Filtering products by category, price, availability
    """
    
    @staticmethod
    def list_products(
        db: Session,
        category: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        show_unavailable: bool = False
    ) -> List[ProductModel]:
        """
        List products with optional filtering.
        
        Args:
            db: Database session
            category: Filter by category
            min_price: Minimum price filter
            max_price: Maximum price filter
            show_unavailable: Whether to include out-of-stock items
            
        Returns:
            List of products matching the filters
        """
        query = db.query(ProductModel)
        
        # Apply filters
        if category:
            query = query.filter(ProductModel.category == category)
        
        if min_price is not None:
            query = query.filter(ProductModel.price >= min_price)
        
        if max_price is not None:
            query = query.filter(ProductModel.price <= max_price)
        
        if not show_unavailable:
            query = query.filter(ProductModel.is_available == True)
        
        products = query.order_by(ProductModel.name).all()
        
        return products
    
    @staticmethod
    def get_product(db: Session, product_id: int) -> Optional[ProductModel]:
        """
        Get a single product by ID.
        
        Args:
            db: Database session
            product_id: ID of the product to retrieve
            
        Returns:
            Product object if found, None otherwise
        """
        return db.query(ProductModel).filter(
            ProductModel.id == product_id
        ).first()
    
    @staticmethod
    def create_product(db: Session, product_data: ProductCreate) -> ProductModel:
        """
        Create a new product.
        
        Args:
            db: Database session
            product_data: Validated product creation data
            
        Returns:
            Created product object
        """
        new_product = ProductModel(**product_data.model_dump())
        db.add(new_product)
        db.commit()
        db.refresh(new_product)
        
        return new_product
    
    @staticmethod
    def update_product(
        db: Session,
        product_id: int,
        update_data: ProductUpdate
    ) -> Optional[ProductModel]:
        """
        Update an existing product.
        
        Args:
            db: Database session
            product_id: ID of product to update
            update_data: Fields to update
            
        Returns:
            Updated product object if found, None otherwise
        """
        product = ProductService.get_product(db, product_id)
        if not product:
            return None
        
        # Apply updates (only non-None fields)
        update_dict = update_data.model_dump(exclude_unset=True)
        
        for field, value in update_dict.items():
            setattr(product, field, value)
        
        db.commit()
        db.refresh(product)
        
        return product
    
    @staticmethod
    def delete_product(db: Session, product_id: int) -> bool:
        """
        Soft delete a product (set is_available=False).
        
        Args:
            db: Database session
            product_id: ID of product to delete
            
        Returns:
            True if product was found and deleted, False otherwise
        """
        product = ProductService.get_product(db, product_id)
        if not product:
            return False
        
        product.is_available = False
        db.commit()
        
        return True
    
    @staticmethod
    def check_product_availability(
        db: Session,
        product_id: int,
        quantity: int
    ) -> Tuple[bool, str, Optional[ProductModel]]:
        """
        Check if a product is available in sufficient quantity.
        
        Args:
            db: Database session
            product_id: ID of the product
            quantity: Required quantity
            
        Returns:
            Tuple of (is_available, message, product)
        """
        product = ProductService.get_product(db, product_id)
        
        if not product:
            return False, f"Product {product_id} not found", None
        
        if not product.is_available:
            return False, f"Product {product.name} is not available", product
        
        if product.stock < quantity:
            return False, f"Product {product.name} has insufficient stock", product
        
        return True, "Product available", product


# ============================================================
# ORDER SERVICE
# ============================================================

class OrderService:
    """
    OrderService handles all business logic related to orders.
    
    This service is responsible for:
    - Creating new orders with transaction support
    - Retrieving order information
    - Updating order status
    - Calculating order totals
    - Managing inventory (deducting stock on order)
    """
    
    @staticmethod
    def list_orders(
        db: Session,
        customer_id: Optional[int] = None,
        status: Optional[str] = None
    ) -> List[OrderSummary]:
        """
        List orders with optional filtering.
        
        Args:
            db: Database session
            customer_id: Filter by customer ID
            status: Filter by order status
            
        Returns:
            List of order summaries
        """
        query = db.query(OrderModel)
        
        # Apply filters
        if customer_id:
            query = query.filter(OrderModel.customer_id == customer_id)
        
        if status:
            query = query.filter(OrderModel.status == status)
        
        orders = query.order_by(OrderModel.created_at.desc()).all()
        
        # Build order summaries with item counts
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
    
    @staticmethod
    def get_order(db: Session, order_id: int) -> Optional[OrderModel]:
        """
        Get a single order by ID.
        
        Args:
            db: Database session
            order_id: ID of the order to retrieve
            
        Returns:
            Order object if found, None otherwise
        """
        return db.query(OrderModel).filter(OrderModel.id == order_id).first()
    
    @staticmethod
    def create_order(db: Session, order_data: OrderCreate) -> OrderModel:
        """
        Create a new order with transaction support.
        
        This method:
        1. Validates customer exists
        2. Validates all products are available
        3. Calculates total amount
        4. Creates order with items
        5. Deducts stock from inventory
        
        Args:
            db: Database session
            order_data: Validated order creation data
            
        Returns:
            Created order object
            
        Raises:
            ValueError: If customer not found or products unavailable
        """
        # Step 1: Verify customer exists
        customer = CustomerService.get_customer(db, order_data.customer_id)
        if not customer:
            raise ValueError(f"Customer {order_data.customer_id} not found")
        
        # Step 2: Validate all products and calculate total
        total = 0.0
        order_items = []
        
        for item in order_data.items:
            # Check product availability
            is_available, message, product = ProductService.check_product_availability(
                db, item.product_id, item.quantity
            )
            
            if not is_available:
                raise ValueError(message)
            
            # Calculate item total
            item_total = product.price * item.quantity
            total += item_total
            
            # Store item data for later creation
            order_items.append({
                "product_id": product.id,
                "quantity": item.quantity,
                "price_at_order": product.price
            })
        
        # Step 3: Create the order
        new_order = OrderModel(
            customer_id=order_data.customer_id,
            total_amount=total,
            status="pending"
        )
        
        db.add(new_order)
        db.flush()  # Get the order ID
        
        # Step 4: Create order items and update inventory
        for item_data in order_items:
            order_item = OrderItemModel(
                order_id=new_order.id,
                **item_data
            )
            db.add(order_item)
            
            # Deduct stock from inventory
            product = db.query(ProductModel).get(item_data["product_id"])
            product.stock -= item_data["quantity"]
        
        # Step 5: Commit the transaction
        db.commit()
        db.refresh(new_order)
        
        return new_order
    
    @staticmethod
    def update_order_status(
        db: Session,
        order_id: int,
        new_status: str
    ) -> Optional[OrderModel]:
        """
        Update an order's status.
        
        Args:
            db: Database session
            order_id: ID of order to update
            new_status: New status value
            
        Returns:
            Updated order object if found, None otherwise
        """
        order = OrderService.get_order(db, order_id)
        if not order:
            return None
        
        order.status = new_status
        db.commit()
        db.refresh(order)
        
        return order
    
    @staticmethod
    def validate_order_status(status: str) -> bool:
        """
        Validate if a status string is valid.
        
        Args:
            status: Status string to validate
            
        Returns:
            True if valid, False otherwise
        """
        valid_statuses = {"pending", "preparing", "ready", "completed", "cancelled"}
        return status in valid_statuses


# ============================================================
# FACTORY FUNCTIONS (For convenience)
# ============================================================

def get_customer_service() -> CustomerService:
    """Get an instance of CustomerService."""
    return CustomerService()


def get_product_service() -> ProductService:
    """Get an instance of ProductService."""
    return ProductService()


def get_order_service() -> OrderService:
    """Get an instance of OrderService."""
    return OrderService()


# ============================================================
# THE 'AHA!' MOMENT: When to Use Services
# ============================================================

"""
WHY USE THE SERVICE LAYER PATTERN?

✅ BENEFITS:
1. Separation of Concerns
   - Routes handle HTTP (requests/responses)
   - Services handle business logic (validation, calculations)
   - Models handle data (database)

2. Reusability
   - Same service can be used by:
     * REST API routes
     * GraphQL resolvers
     * Background jobs
     * Admin panels
     * Other microservices

3. Testability
   - Services can be unit tested without:
     * HTTP requests
     * Database connections
     * FastAPI app setup

4. Maintainability
   - Business logic changes don't affect API structure
   - Easy to add new features without breaking existing code

❌ WHEN NOT TO USE:
- Simple CRUD apps with no business logic
- Small prototypes
- Very simple microservices

EXAMPLE: Without vs With Service Layer

WITHOUT SERVICE (Monolithic routes):
```python
@app.post("/orders")
def create_order(order_data: OrderCreate, db: Session = Depends(get_db)):
    # Business logic mixed with HTTP handling
    customer = db.query(Customer).filter(...).first()
    if not customer:
        raise HTTPException(404)
    # ... 50 more lines of business logic
    return order
```

WITH SERVICE (Separated concerns):
```python
@app.post("/orders")
def create_order(order_data: OrderCreate, db: Session = Depends(get_db)):
    # Just call the service
    order = OrderService.create_order(db, order_data)
    return order
```

The service handles all the business logic internally.
"""
