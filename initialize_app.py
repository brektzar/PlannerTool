from auth import create_user
from database import get_database
import streamlit as st

def initialize_app():
    """Initialize the application with required setup"""
    db = get_database()
    
    # Create admin collection if it doesn't exist
    if 'users' not in db.list_collection_names():
        db.create_collection('users')
    
    # Check if admin user exists
    admin_exists = db.users.find_one({'role': 'admin'})
    
    if not admin_exists:
        # Create default admin user
        success, message = create_user(
            username="admin",
            password="admin123",  # Change this in production
            role="admin"
        )
        if success:
            print("Default admin user created successfully")
            print("Username: admin")
            print("Password: admin123")
        else:
            print(f"Failed to create admin user: {message}")

if __name__ == "__main__":
    initialize_app() 