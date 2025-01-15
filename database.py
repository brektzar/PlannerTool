from pymongo import MongoClient
import streamlit as st
import sys
import dns.resolver
from config import get_mongodb_config
from custom_logging import log_action

@st.cache_resource(ttl=3600)  # Cache for 1 hour
def get_database():
    """Get MongoDB database connection with caching"""
    try:
        print("\n=== Starting MongoDB Connection Process ===")
        print(f"Python version: {sys.version}")
        
        # Get MongoDB configuration
        mongodb_config = get_mongodb_config()
        MONGODB_URI = mongodb_config['uri']
        DB_NAME = mongodb_config['db_name']
        
        # Mask URI for logging
        masked_uri = MONGODB_URI.replace(MONGODB_URI.split('@')[0], '***')
        print(f"MongoDB URI (masked): {masked_uri}")
        print(f"Target database: {DB_NAME}")
        
        # Configure DNS resolver
        print("\nConfiguring DNS resolver...")
        dns.resolver.default_resolver = dns.resolver.Resolver(configure=False)
        dns.resolver.default_resolver.nameservers = ['8.8.8.8', '8.8.4.4']  # Google DNS
        print("✓ DNS resolver configured")
        
        print("\nStep 1: Creating MongoDB client...")
        client = MongoClient(
            MONGODB_URI,
            directConnection=False,
            connect=True,
            serverSelectionTimeoutMS=30000,
            connectTimeoutMS=30000,
            socketTimeoutMS=30000
        )
        print("✓ Client created successfully")
        
        print("\nStep 2: Testing connection...")
        client.server_info()
        print("✓ Connection test successful")
        
        print("\nStep 3: Accessing database...")
        db = client[DB_NAME]
        print(f"✓ Database '{DB_NAME}' accessed")
        
        print("\n=== MongoDB Connection Successful ===\n")
        
        return db
        
    except Exception as e:
        print("\n!!! MongoDB Connection Error !!!")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        print(f"Error details: {repr(e)}")
        
        # Try different DNS resolution methods
        try:
            print("\nTrying alternative DNS resolution methods:")
            hostname = MONGODB_URI.split('@')[1].split('/')[0]
            
            print("\n1. Using dns.resolver:")
            resolver = dns.resolver.Resolver()
            resolver.nameservers = ['8.8.8.8', '8.8.4.4']
            answers = resolver.resolve(hostname, 'A')
            print(f"DNS Resolution successful: {[rdata.address for rdata in answers]}")
            
            print("\n2. Using socket.getaddrinfo:")
            import socket
            addrinfo = socket.getaddrinfo(hostname, 27017)
            print(f"Address info: {addrinfo}")
            
        except Exception as dns_error:
            print(f"Alternative DNS resolution failed: {str(dns_error)}")
        
        st.error(f"Failed to connect to MongoDB: {str(e)}")
        raise

def dataframe_to_dict(df):
    """Convert DataFrame to list of dictionaries with proper date handling"""
    print("\n=== Converting DataFrame to Dict ===")
    if df is None or df.empty:
        print("Empty or None DataFrame received")
        return []
    
    # Create a copy to avoid modifying the original DataFrame
    df_copy = df.copy()
    
    # Convert date columns to datetime if they exist
    date_columns = [
        'Goal_Start_Date', 'Goal_End_Date',
        'Task_Start_Date', 'Task_End_Date'
    ]
    
    for col in date_columns:
        if col in df_copy.columns:
            # Convert date to datetime, handling None/NaT values
            df_copy[col] = pd.to_datetime(df_copy[col], errors='coerce').apply(
                lambda x: x.replace(tzinfo=None).to_pydatetime() if pd.notnull(x) else None
            )
    
    # Handle NaN values before converting to dict
    result = df_copy.replace({pd.NaT: None, pd.NA: None, float('nan'): None}).to_dict('records')
    print(f"Converted {len(result)} records")
    return result

def dict_to_dataframe(data, date_columns=None):
    """Convert list of dictionaries to DataFrame with proper date handling"""
    print("\n=== Converting Dict to DataFrame ===")
    print(f"Received {len(data) if data else 0} records")
    print(f"Date columns to process: {date_columns}")
    
    if not data:
        print("No data received, creating empty DataFrame")
        from Data import create_empty_dataframe
        return create_empty_dataframe()
    
    df = pd.DataFrame(data)
    print(f"Created DataFrame with shape: {df.shape}")
    
    if date_columns:
        for col in date_columns:
            if col in df.columns:
                print(f"Processing date column: {col}")
                df[col] = pd.to_datetime(df[col]).dt.date
    
    return df

def clear_all_collections():
    """Clear all collections in the database"""
    try:
        db = get_database()
        collections = ["goals", 'tasks', "technical_needs", "bugs", "history", "risks"]  # Add risks
        for collection in collections:
            db[collection].delete_many({})
            log_action("clear_all_data", f"{st.session_state.username} Rensade all samlad data!", "Admin Panel")
        return True
    except Exception as e:
        print(f"Error clearing collections: {str(e)}")
        return False

def clear_specific_collection(collection_name):
    """Clear a specific collection in the database"""
    db = get_database()
    result = db[collection_name].delete_many({})
    log_action("clear_specific_data", f"{st.session_state.username} Rensade all data relaterat till{collection_name}!", "Admin Panel")
    return result.deleted_count