from sqlalchemy import Table, Column, ForeignKey
from .base import Base

# Junction table for Order-Book many-to-many relationship.

# Relationships:
    # - orders: Links to Order model
    # - books: Links to Book model

# Purpose:
    # Allows tracking which books belong to which orders,
    # enabling one order to contain multiple books and one book to appear in multiple orders.
order_book = Table(
    "order_book",
    Base.metadata,
    Column("order_id", ForeignKey("orders.id")),
    Column("book_id", ForeignKey("books.id"))
)

