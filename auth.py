import streamlit as st
from database import get_database
import bcrypt
from datetime import datetime, timedelta
from custom_logging import log_action


def init_auth():
    """Initialize authentication state"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_role' not in st.session_state:
        st.session_state.user_role = None


def hash_password(password):
    """Hash a password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())


def verify_password(password, hashed_password):
    """Verify a password against its hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password)


def create_user(username, password, role='user'):
    """Create a new user in the database"""
    db = get_database()

    # Check if username already exists
    if db.users.find_one({'username': username}):
        return False, "Username already exists"

    # Create new user
    user = {
        'username': username,
        'password': hash_password(password),
        'role': role,
        'created_at': datetime.utcnow(),
        'last_login': None
    }

    try:
        db.users.insert_one(user)
        return True, "User created successfully"
    except Exception as e:
        return False, f"Error creating user: {str(e)}"


def login(username, password):
    """Authenticate a user"""
    db = get_database()
    user = db.users.find_one({'username': username})

    if user and verify_password(password, user['password']):
        # Update last login
        db.users.update_one(
            {'username': username},
            {'$set': {'last_login': datetime.utcnow()}}
        )

        st.session_state.authenticated = True
        st.session_state.user_role = user['role']
        st.session_state.username = username
        return True
    return False


def logout():
    """Log out the current user"""
    st.session_state.authenticated = False
    st.session_state.user_role = None
    if 'username' in st.session_state:
        del st.session_state.username


def show_login_page():
    """Display the login page"""
    # Center the login form
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.title("🔐 Login")
        st.markdown("---")

        # Add some information about the app
        st.markdown("""
        ### Välkommen till Projektplaneringsverktyg
        Logga in för att:
        - Skapa och hantera projekt
        - Spåra uppgifter och mål
        - Analysera projektdata
        - Hantera risker
        """)

        st.markdown("---")

        # Create login form
        with st.form("login_form"):
            username = st.text_input("Användarnamn")
            password = st.text_input("Lösenord", type="password")
            submitted = st.form_submit_button("Logga in")

            if submitted:
                if login(username, password):
                    st.success("Inloggning lyckades!")
                    st.rerun()
                else:
                    st.error("Felaktigt användarnamn eller lösenord")

        # Add version info at the bottom
        st.markdown("---")
        st.caption("Version 1.0")


def require_auth(role=None):
    """Decorator to require authentication and optional role"""

    def decorator(func):
        def wrapper(*args, **kwargs):
            # Ensure authentication state is initialized
            init_auth()

            if not st.session_state.authenticated:
                show_login_page()
                return

            if role and st.session_state.user_role != role:
                st.error("You don't have permission to access this page")
                return

            return func(*args, **kwargs)

        return wrapper

    return decorator
