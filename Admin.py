import streamlit as st
from database import get_database, clear_all_collections, clear_specific_collection
import pandas as pd
from Data import save_data
from auth import require_auth, create_user, init_auth
from custom_logging import log_action, get_logs_by_action

def validate_csv_data(df, collection_type):
    """Validate uploaded CSV data based on collection type"""
    required_columns = {
        'goals': ['Type', 'Goal_Name', 'Goal_Description'],
        'technical_needs': ['Redskap'],
        'bugs': ['description', 'location', 'date_reported', 'status'],
        'history': ['Archive_Year', 'Archive_Date'],
        'risks': ['Risk_Name', 'Risk_Description', 'Risk_Level', 'Status']
    }
    
    if collection_type not in required_columns:
        return False, f"Unknown collection type: {collection_type}"
    
    missing_columns = [col for col in required_columns[collection_type] if col not in df.columns]
    if missing_columns:
        return False, f"Missing required columns: {', '.join(missing_columns)}"
    
    return True, "Valid"

def import_csv_to_mongodb(df, collection_name):
    """Import CSV data to MongoDB collection"""
    try:
        db = get_database()
        
        # Convert DataFrame to records
        records = df.to_dict('records')
        
        # Handle date columns if present
        for record in records:
            for key, value in record.items():
                if 'Date' in key and pd.notnull(value):
                    try:
                        # Convert to datetime then to ISO format string
                        record[key] = pd.to_datetime(value).isoformat()
                    except:
                        pass
        
        # Get existing data
        existing_data = list(db[collection_name].find({}, {'_id': 0}))
        existing_df = pd.DataFrame(existing_data) if existing_data else pd.DataFrame()
        
        # Initialize counters
        added_count = 0
        skipped_count = 0
        
        # Process each record
        for record in records:
            if collection_name == 'goals':
                # Check if goal exists
                if existing_df.empty or not any((existing_df['Type'] == 'Goal') & 
                                              (existing_df['Goal_Name'] == record['Goal_Name'])):
                    db[collection_name].insert_one(record)
                    added_count += 1
                else:
                    skipped_count += 1
            
            elif collection_name == 'technical_needs':
                # Check if technical need exists
                if existing_df.empty or not any(existing_df['Redskap'] == record['Redskap']):
                    db[collection_name].insert_one(record)
                    added_count += 1
                else:
                    skipped_count += 1
            
            else:
                # For other collections, just insert (you can add specific logic for other collections)
                db[collection_name].insert_one(record)
                added_count += 1
        log_action("import_data", (f"{st.session_state.username} Importerade data," 
                                    f"{added_count} poster lades till men hoppade över {skipped_count} poster som var dubbletter"), 
                                    "Admin Panel/Import/Export")
        return True, f"Import complete: Added {added_count} records, Skipped {skipped_count} duplicates"
    except Exception as e:
        return False, f"Error importing data: {str(e)}"

@require_auth(role='admin')
def admin_panel():
    """Admin panel function - only accessible to authenticated admin users"""
    # Authentication check is handled by the decorator
    st.title("Admin Panel")
    
    # Create tabs for different admin functions
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Clear Data", "Import/Export", "Database Stats", "User Management", "Loggar",])
    
    with tab1:
        st.header("Clear Data")
        st.warning("⚠️ Warning: These actions cannot be undone!")
        
        # Clear specific collection
        col1, col2 = st.columns([2, 3])
        with col1:
            collection_to_clear = st.selectbox(
                "Select Collection to Clear",
                ["goals", "technical_needs", "bugs", "history", "risks"]
            )

            if st.button("Clear Collection", key="clear_collection"):
                if st.session_state.get('confirm_clear_collection', False):
                    success = clear_specific_collection(collection_to_clear)
                    if success:
                        st.success(f"Collection {collection_to_clear} cleared successfully!")
                        st.session_state.confirm_clear_collection = False
                        st.rerun()
                    else:
                        st.error("Error clearing collection")
                else:
                    st.session_state.confirm_clear_collection = True
                    st.warning("Are you sure? Click again to confirm.")
        
        # Clear all collections
        if st.button("Clear All Collections", key="clear_all"):
            if st.session_state.get('confirm_clear_all', False):
                success = clear_all_collections()
                if success:
                    st.success("All collections cleared successfully!")
                    st.session_state.confirm_clear_all = False
                    st.rerun()
                else:
                    st.error("Error clearing collections")
            else:
                st.session_state.confirm_clear_all = True
                st.warning("⚠️ Are you sure? This will delete ALL data! Click again to confirm.")
    
    with tab2:
        st.header("Import/Export Data")
        
        # Import section
        st.subheader("Import Data")
        import_collection = st.selectbox(
            "Select Collection to Import",
            ["goals", "technical_needs", "bugs", "history", "risks"],
            key="import_select"
        )
        
        uploaded_file = st.file_uploader(
            "Choose a CSV file",
            type="csv",
            help="Upload a CSV file with the required columns for the selected collection",
            key="file_uploader"
        )
        
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                
                st.write("Preview of uploaded data:")
                st.dataframe(df.head())
                
                is_valid, message = validate_csv_data(df, import_collection)
                
                if not is_valid:
                    st.error(message)
                else:
                    if st.button("Import Data", key="import_button"):
                        success, message = import_csv_to_mongodb(df, import_collection)
                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)
            
            except Exception as e:
                st.error(f"Error processing uploaded file: {str(e)}")
        
        # Export section
        st.subheader("Export Data")
        if st.button("Download Current Data"):
            try:
                csv = st.session_state.df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name="planner_tool_data.csv",
                    mime="text/csv"
                )
            except Exception as e:
                st.error(f"Error during download: {str(e)}")
    
    with tab3:
        st.header("Database Statistics")
        try:
            db = get_database()
            
            # Get collection stats
            collections = ["goals", "technical_needs", "bugs", "history", "risks"]
            for collection in collections:
                count = db[collection].count_documents({})
                st.metric(f"{collection.capitalize()} Count", count)
            
        except Exception as e:
            st.error(f"Error getting database statistics: {str(e)}")
    
    with tab4:
        st.header("User Management")
        
        # Create new user section
        st.subheader("Create New User")
        with st.form("create_user_form"):
            new_username = st.text_input("Username")
            new_password = st.text_input("Password", type="password")
            role = st.selectbox("Role", ["user", "admin"])
            
            if st.form_submit_button("Create User"):
                if new_username and new_password:
                    success, message = create_user(new_username, new_password, role)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
                else:
                    st.error("Please fill in all fields")
        
        # Display users
        st.subheader("Existing Users")
        db = get_database()
        users = list(db.users.find({}, {'password': 0}))  # Exclude password from display
        if users:
            user_df = pd.DataFrame(users)
            user_df = user_df.drop('_id', axis=1)
            st.dataframe(user_df)
        else:
            st.info("No users found") 

    with tab5:
        st.header("Loggar")
        st.write("tillfälligt text")

        # Hämta loggar
        logs_by_action = get_logs_by_action()

        # Skapa flikar för varje action
        if logs_by_action:
            tab_labels = list(logs_by_action.keys())
            tabs = st.tabs(tab_labels)

            for tab, action in zip(tabs, tab_labels):
                with tab:
                    st.header(f"Loggar för {action}")
                    logs = logs_by_action[action]

                    if logs:
                        # Visa loggarna som en tabell
                        st.dataframe(logs)
                    else:
                        st.write("Inga loggar hittades för denna action.")
