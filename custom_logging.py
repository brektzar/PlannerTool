import datetime
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
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        # Lägg till loggen i databasen
        db.logs.insert_one(log_entry)
        print(f"Log saved successfully: {log_entry}")
        os.write(f'Log saved successfully: {log_entry}\n')
    except Exception as e:
        print(f"Error saving data to MongoDB: {e}")
        os.write(f'Error saving data to MongoDB: {e}\n')

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

