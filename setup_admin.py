from auth import create_user
from database import get_database

def setup_initial_admin():
    db = get_database()
    
    # Check if any admin user exists
    if db.users.find_one({'role': 'admin'}):
        print("An admin user already exists.")
        return
    
    # Create initial admin user
    success, message = create_user(
        username="admin",
        password="admin123",  # Change this to a secure password
        role="admin"
    )
    
    if success:
        print("Initial admin user created successfully!")
        print("Username: admin")
        print("Password: admin123")  # Remember to change this
    else:
        print(f"Failed to create admin user: {message}")

if __name__ == "__main__":
    setup_initial_admin() 