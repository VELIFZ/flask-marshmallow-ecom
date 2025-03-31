from flask_sqlalchemy import SQLAlchemy
from .base import Base

# Initialize database
# SQLAlchemy is initialized with the app to manage database connections.
db = SQLAlchemy(model_class = Base)

# Import all models AFTER db initialization
from .user_model import User
from .review_model import Review
from .book_model import Book
from .order_model import Order
from .address_model import Address
from .associations import order_book