from datetime import datetime
from Data import current_time
import pytz
import streamlit as st
import pandas as pd
import os


def initialize_logs_collection():
    """
    Kontrollerar om samlingen 'logs' existerar och skapar den om den saknas.
    """
    try:
        from database import get_database
        db = get_database()

        # Kontrollera om samlingen existerar
        if "logs" not in db.list_collection_names():
            print("Logs collection does not exist. Creating it now.")
            db.create_collection("logs")
            # Eventuellt kan du sätta en indexering här för bättre prestanda.
            db.logs.create_index([("timestamp", pymongo.ASCENDING)])
            print("Logs collection created successfully.")
    except Exception as e:
        print(f"Error initializing logs collection: {e}")


def log_action(action, description, location):
    """
    Loggar en användarhandling och sparar den i databasen.

    :param action: Typ av handling (t.ex. "Bug Rapporterad", "Status Uppdaterad").
    :param description: Detaljerad beskrivning av handlingen.
    :param location: Var handlingen inträffade (kan vara en modul eller funktion).
    """
   
    
    try:
        print("Trying to save logs")
        logs_df = load_logs()  # Ladda befintliga loggar
        from database import get_database  # Import inuti funktionen för att undvika cirkulära importer
        db = get_database()

        # Kontrollera och initiera samlingen 'logs' om den saknas
        initialize_logs_collection()

        # Kontrollera att databasen och loggen är korrekt konfigurerade
        if not hasattr(db, "logs"):
            raise AttributeError("Database object does not have a 'logs' attribute")

        log_entry = {
            'action': action,
            'description': description,
            'location': location,
            'timestamp': current_time()
        }

        # Lägg till loggen i databasen

        log_print_success = (f"Log saved successfully: {log_entry}")
        lps = str.encode(log_print_success)

        db.logs.insert_one(log_entry)
        print(f"Log saved successfully: {log_entry}")
        os.write(1, lps)
    except Exception as e:

        log_print_fail = (f"Error saving data to MongoDB: {e}")
        lpf = str.encode(log_print_fail)

        print(f"Error saving data to MongoDB: {e}")
        os.write(1,lpf)

def load_logs():
    """
    Laddar loggar från databasen.

    :return: DataFrame med loggar.
    """
    try:
        from database import get_database  # Import inuti funktionen för att undvika cirkulära importer
        db = get_database()

        # Hämta loggar från databasen
        logs = list(db.logs.find({}, {'_id': 0}))
        
        # Om det inte finns några loggar, returnera en tom DataFrame med rätt kolumner
        if not logs:
            return pd.DataFrame(columns=['action', 'description', 'location', 'timestamp'])
        
        # Skapa en DataFrame från loggarna
        return pd.DataFrame(logs)
    except Exception as e:
        print(f"Error loading logs from MongoDB: {e}")
        return pd.DataFrame(columns=['action', 'description', 'location', 'timestamp'])

def get_logs_by_action():
    """
    Använder aggregation pipeline för att gruppera loggar efter action.
    Returnerar en ordbok där nycklarna är actions och värdena är listor av loggar.
    """
    actions = [
        "add_goal", "add_task", "add_risk", "add_tool",
        "remove_tool", "complete_task", "complete_goal",
        "bug_report", "bug_fixed", "bug_unfixed", "save_history"
    ]

    try:
        from database import get_database
        db = get_database()
        logs_collection = db.logs

        # Aggregation pipeline för att gruppera loggar
        pipeline = [
            {"$match": {"action": {"$in": actions}}},
            {"$group": {"_id": "$action", "logs": {"$push": "$$ROOT"}}}
        ]
        
        # Kör aggregation och skapa en ordbok
        logs_by_action = {}
        for group in logs_collection.aggregate(pipeline):
            logs_by_action[group["_id"]] = group["logs"]
        
        success = f"Hämtar loggar!"
        os.write(1, success.encode())

        return logs_by_action

    except Exception as e:
        error_h = f"Error fetching logs by action with aggregation: {e}"
        os.write(1, error_h.encode())
        print(f"Error fetching logs by action with aggregation: {e}")
        return {}


    """ 
    def get_logs_by_action(): """
    """
    Skapar separata listor för varje unik action i loggsamlingen.
    Returnerar en ordbok där nycklarna är actions och värdena är listor av loggar.
    """
    """     
        actions = [
        "add_goal", "add_task", "add_risk", "add_tool",
        "remove_tool", "complete_task", "complete_goal",
        "bug_report", "bug_fixed", "bug_unfixed", "save_history"
    ] """

    try:
        from database import get_database
        db = get_database()
        logs_collection = db.logs

        # Ordbok för att lagra loggar per action
        logs_by_action = {action: [] for action in actions}

        # Hämta loggar för varje action
        for action in actions:
            logs_by_action[action] = list(logs_collection.find({"action": action}))

        return logs_by_action

    except Exception as e:
        print(f"Error fetching logs by action: {e}")
        return {}

def compare_and_log_changes(df, edited_data):
    changes_made = []

    # Iterera över alla redigerade data
    for index, new_data in edited_data.items():
        # Hämta det gamla värdet från df (du kan använda indexet för att hitta motsvarande rad)
        old_data = df.loc[index] if index in df.index else None

        # Jämför varje kolumn (värde) för att se om något ändrats
        for column in new_data:
            old_value = old_data[column] if old_data is not None else None
            new_value = new_data[column]

            if old_value != new_value:
                changes_made.append({
                    "index": index,
                    "column": column,
                    "old_value": old_value,
                    "new_value": new_value
                })
    
    # Logga ändringarna om några finns
    if changes_made:
        for change in changes_made:
            log_action("update", 
                       (f"{st.session_state.username} ändrade uppgiften {change['column']} \n"
                       f"för rad {change['index']} \n"
                       f"från {change['old_value']} \n"
                       f"till {change['new_value']}\n"), 
                       "Planering/Redigera Mål och Uppgifter")
    return changes_made