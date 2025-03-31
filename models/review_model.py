from sqlalchemy import Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column
from werkzeug.security import generate_password_hash, check_password_hash
from typing import Optional
from datetime import datetime
from sqlalchemy.sql import func
from .base import Base


class Review(Base):
    """
    Review model for seller ratings and comments.
    
    Relationships:
        - seller: User who received the review
        - buyer: User who wrote the review
        - book: Book that was purchased (optional)
        - order: Order associated with this review (optional)
    
    Key Fields:
        - rating: Numeric rating (1-5)
        - comment: Optional text review
        - created_at: When review was submitted
    """
    __tablename__ = "reviews"
    # Basic review information
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    rating: Mapped[int] = mapped_column(nullable=False)
    comment: Mapped[Optional[str]] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    
    # Foreign Keys
    
    # Many-to-One: Many reviews can belong to One seller
    # User that being reviewed
    seller_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    ) 
    # Many-to-One: Many reviews can be written by One buyer
    # User who left the review
    buyer_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    ) 
    # Many-to-One: Many reviews can be about One book 
    book_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("books.id"),
        nullable=True
    )
    # Many-to-One: Many reviews can be associated with One order
    order_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("orders.id"),
        nullable=True
    )
    
    # Relationships: 
    
    # Many-to-One: Links each review to the seller
    # Bidirectional relationship - seller can access their reviews
    seller: Mapped["User"] = relationship(
        back_populates="reviews",
        foreign_keys=[seller_id],
        cascade="all, delete-orphan"
    )
    # Many-to-One: Reviews to Buyer
    # Unidirectional relationship - No back_populates because buyers don't need stored reviews
    buyer: Mapped["User"] = relationship(
        foreign_keys=[buyer_id],
        lazy="noload"  # Prevent unnecessary loading
    ) 
    # Many-to-One: Reviews to Book
    # Unidirectional relationship - optional connection to specific book
    book: Mapped["Book"] = relationship(
        foreign_keys=[book_id],
        lazy="noload"
    )
    # Many-to-One: Reviews to Order
    # Unidirectional relationship - optional connection to specific order
    order: Mapped["Order"] = relationship(
        foreign_keys=[order_id],
        lazy="noload"
    )