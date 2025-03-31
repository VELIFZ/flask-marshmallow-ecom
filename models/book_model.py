from sqlalchemy import Integer, String, ForeignKey, Enum, CheckConstraint
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import List, Optional
from datetime import datetime
from .base import Base 

# (Many-to-Many with Orders, One-to-Many with User)
class Book(Base):
    """
    Book model representing books listed for sale.
    
    Relationships:
        - seller: User who is selling the book
        - orders: Orders containing this book
        - reviews: Reviews about this book
    """
    __tablename__ = "books"
    
    # Basic book information fields
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    author: Mapped[str] = mapped_column(String(255), nullable=False)
    price: Mapped[float] = mapped_column(nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(1000))
    
    # Additional book details
    condition: Mapped[str] = mapped_column(
        Enum("New", "Like New", "Very Good", "Good", "Fair", name="book_condition"),
        nullable=False,
        default="Good"
    )
    genre: Mapped[Optional[str]] = mapped_column(String(100))
    publication_year: Mapped[Optional[int]] = mapped_column()
    isbn: Mapped[Optional[str]] = mapped_column(String(13))
    
    status: Mapped[str] = mapped_column(Enum("Available", "Reserved", "Sold", name="book_status"), nullable=False, default="Available") 
    
    # Image handling
    # Stores URL or path to book cover image
    image_url: Mapped[Optional[str]] = mapped_column(String(255))
    
    # Relationships -> Many-to-One with Seller
    # Each book must have One seller
    seller_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    seller: Mapped["User"] = relationship("User", back_populates="books")

    # Relationships -> Many-to-Many with Orders
    # One book can be in many orders (if seller has multiple copies)
    # Uses order_book as junction table
    orders: Mapped[List["Order"]] = relationship("Order", secondary="order_book", back_populates="books", lazy="noload")
    
    # Relationships -> One-to-Many with Reviews
    # One book can have many reviews
    # When book is deleted, all its reviews are removed
    reviews: Mapped[List["Review"]] = relationship(back_populates="book", cascade="all, delete-orphan", lazy="noload")

    __table_args__ = (
        CheckConstraint('price >= 0 AND price <= 10000', name='check_price_range'),
        CheckConstraint('LENGTH(isbn) = 13 OR isbn IS NULL', name='check_isbn_length'),
        CheckConstraint(
            'publication_year >= 1800 AND publication_year <= 2100',
            name='check_publication_year'
        ),
    )

    # Methods
    def update_status(self, new_status: str):
        """
        Update book status with validation.
        Valid statuses: Available, Reserved, Sold
        """
        valid_statuses = {"Available", "Reserved", "Sold"}
        if new_status not in valid_statuses:
            raise ValueError(f"Invalid status: {new_status}")

        self.status = new_status

    def is_available(self) -> bool:
        """
        Check if book is available for purchase
        Returns True if status is 'Available'
        """
        return self.status == "Available"
