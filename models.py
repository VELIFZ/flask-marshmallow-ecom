from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, Table, String, Column, DateTime, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from typing import List, Optional
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# Base class
class Base(DeclarativeBase):
    pass

# Initialize database
# SQLAlchemy is initialized with the app to manage database connections.
db = SQLAlchemy(model_class = Base)

# Many-to-Many Association Table
order_product = Table(
    "order_book",
    Base.metadata,
    Column("order_id", ForeignKey("orders.id")),
    Column("book_id", ForeignKey("books.id"))
)

# User Model (One-to-Many with Orders, One-to-Many with Addresses)
class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(30), nullable=False)
    last_name: Mapped[str] = mapped_column(String(30), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(15), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=True)
    # Seller related fields
    is_seller: Mapped[bool] = mapped_column(default=False)
    rating: Mapped[Optional[float]] = mapped_column(nullable=True, default=0.0)
    total_sales: Mapped[int] = mapped_column(default=0)
    
    # Relationships -> One-to-Many 
    books: Mapped[List["Book"]] = relationship(back_populates="seller", cascade="all, delete-orphan")  # Books listed by user
    reviews: Mapped[Optional[List["Review"]]] = relationship(back_populates="seller", cascade="all, delete-orphan")  # Reviews received
    # One-to-Many with Orders - no cascade delete- orders remains in db even user is deleted.
    #! bu layz load olmadan postman basic degil her seyi veriyordu
    orders: Mapped[List["Order"]] = relationship(back_populates="customer", cascade="save-update", lazy="noload" )
    # One-to-Many with Addresses - cascade delete 
    addresses: Mapped[List["Address"]] = relationship(back_populates="user", cascade="all, delete-orphan",lazy="noload" )
    
    # securely hash plaintext passwords before storing them in password fielf of User object
    def set_password(self, password):
        if password:
            self.password = generate_password_hash(password)
        else:
            self.password = None  # set to None if no password
        
    # verify the password by comparing the one hashed one stored in db
    def verify_password(self, password):
        if password is None:
            return False
        return check_password_hash(self.password, password)
    
    
# Address Model (Many-to-One with User)
class Address(Base):
    __tablename__ ='addresses'
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    street: Mapped[str] = mapped_column(String(255), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    state: Mapped[str] = mapped_column(String(100), nullable=False)
    postal_code: Mapped[str] = mapped_column(String(20), nullable=False)
    country: Mapped[str] = mapped_column(String(100), nullable=False)
    
    is_default: Mapped[bool] = mapped_column(default=False)  # Optional
    address_type: Mapped[Optional[str]] = mapped_column(String(50))  # Work, Home, Other
    
    # ForeignKey linking Address to User
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    # Relationship back to User
    user: Mapped["User"] = relationship(back_populates="addresses")


# Order Model (Many-to-One with User, Many-to-Many with Products)
class Order(Base):
    __tablename__ = "orders"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)    
    
    # Order Details
    total_amount: Mapped[float] = mapped_column(nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="Pending")  # Pending, Completed, Cancelled
    payment_status: Mapped[str] = mapped_column(String(20), default="Unpaid")  # Unpaid, Paid
    tracking_number: Mapped[Optional[str]] = mapped_column(String(100))  # Optional tracking number
    
    # ForeignKey linking Order to User
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), onupdate='SET NULL', nullable=True) 
        # Relationship with User (Many-to-One)
    customer: Mapped["User"] = relationship(back_populates="orders")
    
    # ForeignKey linking Order to Address (Shipping Destination)
    shipping_address_id: Mapped[int] = mapped_column(Integer, ForeignKey("addresses.id"), nullable=True)
    shipping_address: Mapped["Address"] = relationship()
    
    # Relationship with Products (Many-to-Many)
    products: Mapped[List["Book"]] = relationship(secondary="order_book", back_populates="orders")
     
# Product Model (Many-to-Many with Orders, One-to-Many with User)
class Book(Base):
    __tablename__ = "books"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    author: Mapped[str] = mapped_column(String(100), nullable=False)
    price: Mapped[float] = mapped_column(nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(1000))
    condition: Mapped[str] = mapped_column(String(50), nullable=False, default="Used")
    category: Mapped[Optional[str]] = mapped_column(String(100))
    # ForeignKey linking Book to User (Seller)
    seller_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationship 
    # One-to-Many with Seller
    seller: Mapped["User"] = relationship(back_populates="books")  
    # with Orders (Many-to-Many)
    orders: Mapped[List["Order"]] = relationship(secondary="order_book", back_populates="books")
    
class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    rating: Mapped[int] = mapped_column(nullable=True)  # 1-5 rating scale
    comment: Mapped[Optional[str]] = mapped_column(String(500))  # Optional review text
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Foreign Keys
    seller_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)  # User being reviewed
    buyer_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)  # User who left the review

    # Relationships
    seller: Mapped["User"] = relationship(back_populates="reviews", foreign_keys=[seller_id])
    buyer: Mapped["User"] = relationship(foreign_keys=[buyer_id])  # No back_populates because buyers don’t need stored reviews
