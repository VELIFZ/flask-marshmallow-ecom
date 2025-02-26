from flask import Flask
from dotenv import load_dotenv
import os
from models import db
from flask_migrate import Migrate

# Load environment variables (the .env file)
load_dotenv()

# Initialize Flask
app = Flask(__name__) # location

# Database configuration
# app gonna serve the database connection - flask config
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("SQLALCHEMY_DATABASE_URI")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS')

# link the app to the db - Initialize database with Flask app
db.init_app(app)

# Initialize Flask-Migrate
migrate = Migrate(app, db)

# Run the app
if __name__ == "__main__":
    with app.app_context():
        #db.drop_all()
        db.create_all()
    
   # Import and register blueprints from the routes folder
    from routes.user_routes import user_bp
    from routes.order_routes import order_bp
    from routes.product_routes import product_bp
    from routes.address_routes import address_bp

    # Register each blueprint separately
    app.register_blueprint(user_bp) # app.register_blueprint(user_bp, url_prefix='/users') - if this routes -> @user_bp.route('', methods=['POST'])
    app.register_blueprint(order_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(address_bp)
    
    # run the app
    app.run(debug=True)