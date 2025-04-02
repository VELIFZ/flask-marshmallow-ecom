from flask import Flask, jsonify, url_for
from dotenv import load_dotenv
import os
from models import db
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate

# Load environment variables (the .env file)
load_dotenv()

# Initialize Flask
app = Flask(__name__) # location

# Database configuration
#! Using SQLite for development
# app gonna serve the database connection - flask config
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("SQLALCHEMY_DATABASE_URI")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS')

# Set up JWT secret key
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')

# Add a test route
@app.route('/test', methods=['GET'])
def test_route():
    return jsonify({"message": "Test route is working!"}), 200

# Initialize database and extensions
db.init_app(app)
from schemas import ma
ma.init_app(app)
migrate = Migrate(app, db)

# Import and register blueprints
from routes.user_routes import user_bp
from routes.order_routes import order_bp
from routes.book_routes import book_bp
from routes.address_routes import address_bp
from routes.auth_routes import auth_bp
from routes.review_routes import review_bp

# Register each blueprint separately
app.register_blueprint(user_bp)
app.register_blueprint(order_bp)
app.register_blueprint(book_bp)
app.register_blueprint(address_bp)
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(review_bp)

# Debug route to list all registered routes
@app.route('/debug/routes')
def list_routes():
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append({
            "endpoint": rule.endpoint,
            "methods": list(rule.methods),
            "path": str(rule)
        })
    return jsonify(routes)

# Run the app
if __name__ == "__main__":
    with app.app_context():
        #db.drop_all()
        db.create_all()
    
    # Print routes for debugging
    print("Registered routes:")
    for rule in app.url_map.iter_rules():
        print(f"{rule} - {rule.endpoint} - {rule.methods}")
    
    # run the app
    app.run(debug=True)