from schemas import user_schema, users_schema
from models import db, User
from flask import request, jsonify, Blueprint, current_app
from marshmallow import ValidationError
from sqlalchemy import select
import jwt
import datetime # to handle token expiration

# Define the Blueprint
user_bp = Blueprint('main', __name__)

# ============ MARK: Post Methods ========

@user_bp.route('/users', methods=['POST']) 
def create_user():
    try:
        new_user = user_schema.load(request.json) # Deserialize request data and reates a valid User object
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    #! When marshmallow converst the json to a User object does ot trigger any method in the model so password will be plaintext
    new_user.set_password(request.json['password'])

    db.session.add(new_user) # Add user to DB
    db.session.commit()
    
    return jsonify(user_schema.dumps(new_user)), 201 # Return JSON response

@user_bp.route('/users/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    user = db.session.query(User).filter_by(email=email).first()
    
    if not email or not user.verify_password(password): # verify user exist and passwords is correct
        return jsonify({'error': 'Invalid credentials'}), 401 # Unauthorized
    
    token = jwt.encode(
    {"user_id": user.id, "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2)},
    current_app.config["SECRET_KEY"], 
    algorithm="HS256"  # encryption
    )
    return jsonify({'token': token}), 200 # returns to jwt roken as the response
        

# ============ MARK: Get Methods ========

@user_bp.route('/users', methods=['GET'])
def get_users():
    query = select(User)
    users = db.session.execute(query).scalars().all()

    return users_schema.dump(users), 200

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
    
    return user_schema.dumps(update_user), 200

# ============ MARK: Delete Methods ========

@user_bp.route('/user/<int:id>', methods=['DELETE'])
def delete_user(id):
    delete_user = db.session.get(User, id)
    
    if delete_user == None:
        return jsonify