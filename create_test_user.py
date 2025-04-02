from flask import Flask
from models import db
from models.user_model import User
from app import app

def create_test_user():
    with app.app_context():
        # Check if user with ID 1 already exists
        existing_user = db.session.get(User, 1)
        if existing_user:
            print(f"Test user already exists: {existing_user.name} {existing_user.last_name}")
            return existing_user
            
        # Create a test user
        test_user = User(
            id=1,  # Force ID to be 1
            name="Test",
            last_name="User",
            phone_number="1234567890",
            email="test@example.com",
            is_seller=True
        )
        test_user.set_password("password123")
        
        # Add and commit to database
        db.session.add(test_user)
        db.session.commit()
        
        print(f"Created test user: {test_user.name} {test_user.last_name} with ID {test_user.id}")
        return test_user

if __name__ == "__main__":
    create_test_user() 