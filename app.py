# bd in models
from models import db

from flask import Flask
from dotenv import load_dotenv
import os

# Load environment variables (the .env file)
load_dotenv()

# Initialize Flask
app = Flask(__name__) # location

# Database configuration
# app gonna serve the database connection - flask config
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("SQLALCHEMY_DATABASE_URI")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS')

db.init_app(app)

# Run the app
if __name__ == "__main__":
    with app.app_context():
        # db.drop_all()
        db.create_all()
        
    app.run(debug=True)