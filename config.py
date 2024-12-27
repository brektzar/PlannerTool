import streamlit as st

def get_mongodb_config():
    """Get MongoDB configuration from Streamlit secrets"""
    try:
        return {
            'uri': st.secrets.mongodb.uri,
            'db_name': st.secrets.mongodb.db_name
        }
    except Exception as e:
        st.error(f"Failed to load MongoDB configuration: {str(e)}")
        raise 