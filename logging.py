import datetime
import streamlit as st
from database import get_database
import pandas as pd

def log_action(action, description, location):
    """
    Loggar en användarhandling och sparar den i databasen.

    :param action: Typ av handling (t.ex. "Bug Rapporterad", "Status Uppdaterad").
    :param description: Detaljerad beskrivning av handlingen.
    :param location: Var handlingen inträffade (kan vara en modul eller funktion).
    """
    try:
        db = get_database()
        log_entry = {
            'action': action,
            'description': description,
            'location': location,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        db.logs.insert_one(log_entry)
    except Exception as e:
        print(f"Error logging action: {e}")

def load_logs():
    """
    Laddar loggar från databasen.

    :return: DataFrame med loggar.
    """
    try:
        db = get_database()
        logs = list(db.logs.find({}, {'_id': 0}))
        if not logs:
            return pd.DataFrame(columns=['action', 'description', 'location', 'timestamp'])
        return pd.DataFrame(logs)
    except Exception as e:
        print(f"Error loading logs from MongoDB: {e}")
        return pd.DataFrame(columns=['action', 'description', 'location', 'timestamp'])

