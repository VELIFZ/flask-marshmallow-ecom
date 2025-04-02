from sqlalchemy import Integer, String, ForeignKey, DateTime, Enum, CheckConstraint
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import List, Optional
from datetime import datetime
from sqlalchemy.sql import func
from .base import Base
from .user_model import User
from .address_model import Address
from decimal import Decimal

# Order Model (Many-to-One with User, Many-to-Many with Books)
class Order(Base):
    """
    Order model representing book purchases.
    
    Relationships:
        - customer: User who placed the order
        - books: Books included in this order
        - shipping_address: Delivery address for the order
    
    Key Fields:
        - total_amount: Total cost of the order
        - status: Order status (Pending/Processing/Shipped/Delivered/Cancelled)
        - payment_status: Payment status (Unpaid/Processing/Paid/Refunded)
        - tracking_number: Shipping tracking number (optional)
        - order_date: When order was placed
    """
    
    __tablename__ = "orders"
    
    # Basic order information fields
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_date: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())    
    
    # Order Details and Status
    #! total_amount is required and must be calculated before saving order
    total_amount: Mapped[Decimal] = mapped_column(nullable=False, default=0)
    status: Mapped[str] = mapped_column(
        Enum("Pending", "Processing", "Shipped", "Delivered", "Cancelled", name="order_status"),
        default="Pending"
    )
    payment_status: Mapped[str] = mapped_column(
        Enum("Unpaid", "Processing", "Paid", "Refunded", name="payment_status"),
        default="Unpaid"
    )
    tracking_number: Mapped[Optional[str]] = mapped_column(String(100), unique=True)
    
    # Relationships -> Many-to-One with User
    # onupdate='SET NULL' keeps order record even if user is deleted
    # nullable=True allows keeping order history even without user
    user_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("users.id"), 
        onupdate='SET NULL', 
        nullable=True
    ) 
    # Bidirectional relationship with User model's orders field
    customer: Mapped["User"] = relationship(back_populates="orders")
    
    # Relationships -> Many-to-One with Address
    # Each order can have one shipping address
    # nullable=True allows creating order before adding shipping address
    shipping_address_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("addresses.id"), 
        nullable=True
    )
    # Unidirectional relationship - we don't need to access orders from address
    shipping_address: Mapped["Address"] = relationship()
    
    # Relationships -> Many-to-Many with Books
    # One order can have many books, and one book can be in many orders
    # Uses order_book as junction table defined elsewhere
    # Use string reference to avoid circular import
    books: Mapped[List["Book"]] = relationship(secondary="order_book", back_populates="orders", lazy="noload")

    __table_args__ = (
        # Ensure total_amount is not negative
        CheckConstraint('total_amount >= 0', name='check_positive_amount'),
    )

    # Method to update order status
    def update_status(self, new_status: str):
        """
        Update order status and handle related changes
        Valid statuses: Pending, Processing, Shipped, Delivered, Cancelled
        """
        if new_status in ["Pending", "Processing", "Shipped", "Delivered", "Cancelled"]:
            self.status = new_status
            if new_status == "Shipped" and not self.tracking_number:
                raise ValueError("Tracking number required for shipped status")
        else:
            raise ValueError("Invalid status")

    # Method to update payment status
    def update_payment_status(self, new_status: str):
        """
        Update payment status
        Valid statuses: Unpaid, Processing, Paid, Refunded
        """
        if new_status in ["Unpaid", "Processing", "Paid", "Refunded"]:
            self.payment_status = new_status
        else:
            raise ValueError("Invalid payment status")

    """
    Order model representing book purchases.
    
    Relationships:
        - customer: User who placed the order
        - books: Books included in this order
        - shipping_address: Delivery address for the order
    
    Key Fields:
        - total_amount: Total cost of the order
        - status: Order status (Pending/Processing/Shipped/Delivered/Cancelled)
        - payment_status: Payment status (Unpaid/Processing/Paid/Refunded)
        - tracking_number: Shipping tracking number (optional)
        - order_date: When order was placed
    """
