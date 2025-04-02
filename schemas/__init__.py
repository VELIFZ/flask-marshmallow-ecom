from flask_marshmallow import Marshmallow

# Initialize without app
ma = Marshmallow()

# Import schemas after ma initialization (when needed)

from .user_schema import user_schema, users_schema
from .order_schema import order_schema, orders_schema
from .book_schema import book_schema, books_schema
from .review_schema import review_schema, reviews_schema
from .address_schema import address_schema, addresses_schema
