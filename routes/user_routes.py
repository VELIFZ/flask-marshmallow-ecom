from schemas.user_schema import user_schema, users_schema, UserSchema
from models import db, User
from flask import request, jsonify, Blueprint, current_app
from marshmallow import ValidationError
from sqlalchemy import select, or_, and_, desc, update, delete # to query the database
from sqlalchemy.orm import selectinload
from utils.db_helpers import (
    get_table, row_to_dict, rows_to_list, paginate_results,
    handle_error, execute_query, get_by_id
)

import jwt
import datetime # to handle token expiration

# Define the Blueprint
user_bp = Blueprint('user', __name__)

# ============ MARK: Post Methods ========

@user_bp.route('/users', methods=['POST']) 
def create_user():
    try:
        # Debug message
        print("POST /users route called!")
        
        # without this error. I needed to manually pull out the password before calling the schema
        data = request.json
        existing_user = db.session.execute(select(User).where(User.email == data["email"])).scalar_one_or_none()
        if existing_user:
            return jsonify({"error": "Email is already registered", "debug": "This is the updated route"}), 400 
        
        new_user = user_schema.load(data) # Deserialize request data and reates a valid User object
        # burasi password icin 
        password = data.get('password')
        if password:  
            #! When marshmallow converst the json to a User object does ot trigger any method in the model so password will be plaintext
            new_user.set_password(password)  
        else:
            new_user.password = None  # Allow guest users

        db.session.add(new_user) # Add user to DB
        db.session.commit()
    
        return jsonify(user_schema.dump(new_user)), 201 
        
    except ValidationError as e:
        return jsonify(e.messages), 400
    except Exception as e:
        return jsonify({"error": "Something went wrong", "details": str(e)}), 500
    
# @user_bp.route('/users/login', methods=['POST'])
# def login():
#     data = request.json
#     email = data.get('email')
#     password = data.get('password')
    
#     user = db.session.query(User).filter_by(email=email).first()
    
#     if not email or not user.verify_password(password): # verify user exist and passwords is correct
#         return jsonify({'error': 'Invalid credentials'}), 401 # Unauthorized
    
#     token = jwt.encode(
#     {"user_id": user.id, "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2)},
#     current_app.config["SECRET_KEY"], 
#     algorithm="HS256"  # encryption
#     )
#     return jsonify({'token': token}), 200 # returns to jwt roken as the response
        

# ============ MARK: Get Methods ========
# get all users' basic info. Paginated & Searchable
@user_bp.route('/users', methods=['GET']) # GET /users?page=1&search=john
def get_users():
    try:
        page = request.args.get('page', 1, type=int) 
        limit = request.args.get('limit', 10, type=int)
        search = request.args.get('search', type=str)
        
        # Debug message
        print("GET /users route called!")
        
        # Get users table
        users_table = get_table('users')
        
        # ilike -> case-insensitive search & or_() to properly join conditions in sqlalchemy
        # Build query
        query = select(users_table)
        
        # Add search if provided
        if search:
            query = query.where(
                or_(
                    users_table.c.name.ilike(f'%{search}%'), 
                    users_table.c.last_name.ilike(f'%{search}%'), 
                    users_table.c.email.ilike(f'%{search}%')
                )
            )
        
        # Execute query
        users = execute_query(query)
        
        # Convert to list of dictionaries
        user_list = rows_to_list(users, users_table)
        
        if not user_list:
            return jsonify({"message": "No users found", "debug": "This is the updated route"}), 200 
        
        # Paginate results
        paginated_users = paginate_results(user_list, page, limit)
        
        return jsonify({
            "page": page,
            "total": len(user_list), 
            "users": paginated_users
        }), 200
    
    except Exception as e:
        return handle_error(e, "getting users")


# Get a Single User (With Optional Orders or/& Addresses)
@user_bp.route('/user/<int:id>', methods=['GET'])
def get_user(id):
    try:
        include = request.args.get('include', '', type=str)
        include_fields = include.split(',') if include else []

        # If no included fields are requested, use the helper function
        if not include_fields:
            return get_by_id('users', id)
            
        print("Include Fields:", include_fields)
            
        # For requests with relationship loading, we need to use the ORM
        query = select(User).where(User.id == id)
        
        # Selective loading
        if "addresses" in include_fields:
            query = query.options(selectinload(User.addresses))
        
        if "orders" in include_fields:
            query = query.options(selectinload(User.orders)) 

        user = db.session.execute(query).scalar_one_or_none()

        if not user:
            return jsonify({"error": "User not found"}), 404

        # Use dynamic schema to include relationships
        user_schema_dynamic = UserSchema(include_fields=include_fields)
        print("Schema Fields:", user_schema_dynamic.fields.keys())

        return jsonify(user_schema_dynamic.dump(user)), 200
    except Exception as e:
        return handle_error(e, "getting user")

#?GET /users/me to return the logged-in user's info?

# ============ MARK: Put Methods ========

@user_bp.route('/user/<int:id>', methods=["PUT"])
def update_user(id):
    try:
        # Get the user data from the request
        data = request.json
        
        # Validate using schema (partial update)
        try:
            # Validate data with marshmallow schema
            user_schema.load(data, partial=True)
        except ValidationError as e:
            return jsonify(e.messages), 400
        
        # Get users table
        users_table = get_table('users')
        
        # Check if user exists
        result, _ = get_by_id('users', id, response=False)
        
        if not result:
            return jsonify({"error": "User not found"}), 404
        
        # Handle password separately if provided
        if 'password' in data:
            # We need to hash the password before updating
            user = db.session.get(User, id)
            user.set_password(data['password'])
            # Remove from data to avoid double update
            data.pop('password')
            
        # Update user fields using SQLAlchemy Core update
        if data:  # Only proceed if there are fields to update
            stmt = update(users_table).where(users_table.c.id == id).values(**data)
            db.session.execute(stmt)
            
        db.session.commit()
        
        # Get updated user
        return get_by_id('users', id)
        
    except Exception as e:
        db.session.rollback()
        return handle_error(e, "updating user")

# ============ MARK: Delete Methods ========

@user_bp.route('/user/<int:id>', methods=['DELETE'])
def delete_user(id):
    try:
        # Check if user exists
        result, _ = get_by_id('users', id, response=False)
        
        if not result:
            return jsonify({"error": "User not found"}), 404
            
        # Delete user
        users_table = get_table('users')
        stmt = delete(users_table).where(users_table.c.id == id)
        db.session.execute(stmt)
        db.session.commit()
        
        return jsonify({"message": "User deleted successfully"}), 200
        
    except Exception as e:
        db.session.rollback()
        return handle_error(e, "deleting user")

# Get orders for a specific user
@user_bp.route('/user/<int:user_id>/orders', methods=['GET'])
def get_user_orders(user_id):
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 10, type=int)
        status = request.args.get('status', type=str)
        sort = request.args.get('sort', 'order_date', type=str)
        order = request.args.get('order', 'desc', type=str)
        
        # Check if user exists
        users_table = get_table('users')
        user_query = select(users_table).where(users_table.c.id == user_id)
        user = execute_query(user_query, single_result=True)
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Get orders table
        orders_table = get_table('orders')
        
        # Build query to get orders for the user
        query = select(orders_table).where(orders_table.c.user_id == user_id)
        
        # Apply status filter if provided
        if status:
            query = query.where(orders_table.c.status == status)
        
        # Apply sorting
        if hasattr(orders_table.c, sort):
            sort_column = getattr(orders_table.c, sort)
            if order.lower() == 'desc':
                query = query.order_by(desc(sort_column))
            else:
                query = query.order_by(sort_column)
        else:
            # Default sort by order_date descending
            query = query.order_by(desc(orders_table.c.order_date))
        
        # Execute query
        orders = execute_query(query)
        
        # Convert to list of dictionaries
        order_list = rows_to_list(orders, orders_table)
        
        # Paginate results
        paginated_orders = paginate_results(order_list, page, limit)
        
        # For each order, get its books
        for order_dict in paginated_orders:
            # Get order_book junction table
            order_book_table = get_table('order_book')
            books_table = get_table('books')
            
            # Get books for this order
            book_query = select(books_table).where(
                books_table.c.id.in_(
                    select(order_book_table.c.book_id).where(
                        order_book_table.c.order_id == order_dict['id']
                    )
                )
            )
            books = execute_query(book_query)
            order_dict['books'] = rows_to_list(books, books_table)
        
        return jsonify({
            "page": page,
            "limit": limit,
            "total": len(order_list),
            "orders": paginated_orders
        }), 200
        
    except Exception as e:
        return handle_error(e, f"getting orders for user {user_id}")