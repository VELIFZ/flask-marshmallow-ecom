from schemas import user_schema, users_schema, UserSchema
from models import db, User
from flask import request, jsonify, Blueprint, current_app
from marshmallow import ValidationError
from sqlalchemy import select, or_ # to query the database
from sqlalchemy.orm import selectinload

import jwt
import datetime # to handle token expiration

# Define the Blueprint
user_bp = Blueprint('user', __name__)

# ============ MARK: Post Methods ========

@user_bp.route('/users', methods=['POST']) 
def create_user():
    try:
        # without this error. I needed to manually pull out the password before calling the schema
        data = request.json
        existing_user = db.session.execute(select(User).where(User.email == data["email"])).scalar_one_or_none()
        if existing_user:
            return jsonify({"error": "Email is already registered"}), 400 
        
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
        
        query = select(User)
        
        # ilike -> case-insensitive search & or_() to properly join conditions in sqlalchemy
        if search:
            query = query.where(or_(User.name.ilike(f'%{search}%'), User.last_name.ilike(f'%{search}%'), User.email.ilike(f'%{search}%')))
        
        users = db.session.execute(query).scalars().all()
        
        if not users:
            return jsonify({"message": "No users found"}), 200 
        
        # total_users = len(users) # for fronted 
        # total_pages = (total_users + limit - 1) // limit # frontend
        start = (page-1) * limit # calculate the start index
        end = start + limit 
        paginated_users = users[start:end]

        return jsonify({"page": page, "users": users_schema.dump(paginated_users)}), 200
    
    except Exception as e:
        return jsonify({"error": "Something went wrong", "details": str(e)}), 500


# Get a Single User (With Optional Orders or/& Addresses)
# Get a Single User (With Optional Orders or/& Addresses)
@user_bp.route('/user/<int:id>', methods=['GET'])
def get_user(id):
    try:
        include = request.args.get('include', '', type=str)
        include_fields = include.split(',') if include else []

        print("Include Fields:", include_fields)

        query = select(User).where(User.id == id)
        
        #select IN loading - available via lazy='selectin' or the selectinload() option
        if "addresses" in include_fields:
            query = query.options(selectinload(User.addresses))  # Load addresses only if in included= addresses
        
        if "orders" in include_fields:
            query = query.options(selectinload(User.orders)) 

        user = db.session.execute(query).scalar_one_or_none()

        if not user:
            return jsonify({"error": "User not found"}), 404

        user_schema_dynamic = UserSchema(include_fields=include_fields)

        print("Schema Fields:", user_schema_dynamic.fields.keys())

        return jsonify(user_schema_dynamic.dump(user)), 200
    except Exception as e:
        return jsonify({"error": "Something went wrong", "details": str(e)}), 500



#?GET /users/me to return the logged-in user's info?

# ============ MARK: Put Methods ========

@user_bp.route('/user/<int:id>', methods=["PUT"])
def update_user(id):
    try:
        # partial updates (Only update fields that exist in request)
        new_user = user_schema.load(request.json, partial=True)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    # Query to get the existing user (make sure the person is exist)
    query = select(User).where(User.id == id)
    update_user = db.session.execute(query).scalar_one_or_none()
    
    if not update_user:
        return jsonify({"error": "Your id is not valid"}), 404
    # Update fields 
    for field, attribute in request.json.items():
        setattr(update_user, field, attribute)
    db.session.commit()
    
    return jsonify(user_schema.dump(update_user)), 200

# ============ MARK: Delete Methods ========

@user_bp.route('/user/<int:id>', methods=['DELETE'])
def delete_user(id):
    user = db.session.get(User, id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted"}), 200