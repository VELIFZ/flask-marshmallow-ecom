from sqlalchemy import String, DateTime, Boolean
from sqlalchemy.orm import relationship, Mapped, mapped_column
from werkzeug.security import generate_password_hash, check_password_hash
from typing import List, Optional
from datetime import datetime
from sqlalchemy.sql import func
from .base import Base

class User(Base):
    """
    User model representing both buyers and sellers in the system.
    
    Relationships:
        - books: Books listed by this user (as seller)
        - orders: Orders made by this user (as buyer)
        - addresses: Addresses belonging to this user (both seller, buyer)
        - reviews: Reviews received as a seller
    """
    __tablename__ = "users"
    
    # Basic user information fields
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(30), nullable=False)
    last_name: Mapped[str] = mapped_column(String(30), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(15), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=func.now())
    password: Mapped[str] = mapped_column(String(255), nullable=True)
    # Seller profile fields 
    is_seller: Mapped[bool] = mapped_column(Boolean, default=False)
    rating: Mapped[Optional[float]] = mapped_column(nullable=True)
    total_sales: Mapped[int] = mapped_column(nullable=False, default=0)

    # Relationships:
    
    # One-to-Many: One User (seller) can have Many Books
    # Books relationship: When user is deleted, all their book listings are removed
    books: Mapped[List["Book"]] = relationship("Book", back_populates="seller", cascade="all, delete-orphan")
    
    # One-to-Many: One User (seller) can receive Many Reviews
    # Reviews relationship: When user is deleted, all their received reviews are removed
    reviews: Mapped[Optional[List["Review"]]] = relationship(
        "Review",
        back_populates="seller",
        foreign_keys="Review.seller_id",
        cascade="all, delete-orphan"
    )
    
    # One-to-Many: One User (customer) can have Many Orders
    # Orders relationship: When user is deleted, orders remain in database 
    # No cascade delete - orders are preserved for record-keeping when user is deleted
    #! bu layz load olmadan postman basic degil her seyi veriyordu - prevents automatic loading of orders in API responses
    orders: Mapped[List["Order"]] = relationship("Order", back_populates="customer", cascade="save-update", lazy="noload")
    
    # One-to-Many: One User can have Many Addresses
    # Addresses relationship: When user is deleted, all their addresses are removed
    # Temporarily setting lazy="dynamic" to avoid requiring addresses at load time
    addresses: Mapped[Optional[List["Address"]]] = relationship(
        "Address", 
        back_populates="user", 
        cascade="all, delete-orphan", 
        lazy="dynamic",  # Changed from noload to dynamic
        uselist=True,
        innerjoin=False  # Explicitly make it an outer join
    )
    
    # Password management methods
    # securely hash plaintext passwords before storing them in password field of User object
    def set_password(self, password):
        """
        Securely hash and store the user's password
        If no password provided, sets it to None
        """
        if password:
            self.password = generate_password_hash(password)
        else:
            self.password = None  # set to None if no password
        
    # verify the password by comparing the one hashed one stored in db
    def verify_password(self, password):
        """
        Verify if provided password matches the stored hash
        Returns False if no password is provided
        """
        if password is None:
            return False
        return check_password_hash(self.password, password)


