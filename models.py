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
    "order_product",
    Base.metadata,
    Column("order_id", ForeignKey("orders.id")),
    Column("product_id", ForeignKey("products.id"))
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
    
    # status = mapped_column(String(20), default="active")
    
    # ForeignKey linking Order to User
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), onupdate='SET NULL', nullable=True) 
    # Relationship with User (Many-to-One)
    customer: Mapped["User"] = relationship(back_populates="orders")
    # Relationship with Products (Many-to-Many)
    products: Mapped[List["Product"]] = relationship(secondary="order_product", back_populates="orders")
     
# Product Model (Many-to-Many with Orders)
class Product(Base):
    __tablename__ = "products"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    product_name: Mapped[str] = mapped_column(String(500), nullable=False)
    price: Mapped[float] = mapped_column(nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(1000))
    
    # Relationship with Orders (Many-to-Many)
    orders: Mapped[List["Order"]] = relationship(secondary="order_product", back_populates="products")