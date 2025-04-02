# This file ensures that the routes directory is treated as a package
# Keep this file to prevent import issues
from .user_routes import user_bp
from .order_routes import order_bp
from .book_routes import book_bp
from .address_routes import address_bp