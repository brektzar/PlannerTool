import pandas as pd
from datetime import datetime
import pytz



def current_time():
    # Hämta den aktuella tiden för Stockholm (som beaktar sommartid)
    timezone = pytz.timezone('Europe/Stockholm')
    
    # Hämta aktuell tid med rätt tidszon
    stockholm_time = datetime.now(timezone)
    stockholm_time_iso = stockholm_time.isoformat()
    # Konvertera till ISO 8601-format som MongoDB kan hantera
    
    return stockholm_time_iso

# DataFrame structure
def create_empty_dataframe():
    return pd.DataFrame(columns=[
        'Type', 'Goal_Name', 'Goal_Description', 'Goal_Start_Date', 'Goal_End_Date',
        'Goal_Completed', 'Task_Completed',
        'Task_Name', 'Task_Description', 'Task_Start_Date', 'Task_End_Date',
        'Task_Estimated_Time', 'Task_Estimated_Cost', 'Task_Technical_Needs',
        'Task_Weather_Conditions', 'Task_Needs_Rental', 'Task_Rental_Item',
        'Task_Rental_Type', 'Task_Rental_Duration', 'Task_Rental_Cost_Per_Unit',
        'Task_Total_Rental_Cost', 'Task_Personnel_Count', 'Task_Other_Needs'
    ])


# Data loading and saving functions
def load_data():
    try:
        from database import get_database
        db = get_database()
        data = list(db.goals.find({}, {'_id': 0}))  # Exclude MongoDB _id field
        
        if not data:
            return create_empty_dataframe()
            
        df = pd.DataFrame(data)
        
        # Convert date strings to datetime.date objects
        date_columns = ['Goal_Start_Date', 'Goal_End_Date', 'Task_Start_Date', 'Task_End_Date']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], format='mixed', errors='coerce').dt.date
        
        # Initialize completion columns if they don't exist
        if 'Goal_Completed' not in df.columns: df['Goal_Completed'] = False
        if 'Task_Completed' not in df.columns: df['Task_Completed'] = False
        
        return df
    except Exception as e:
        print(f"Error loading data from MongoDB: {e}")
        return create_empty_dataframe()


def save_data(df):
    try:
        from database import get_database
        db = get_database()
        # Convert DataFrame to dict records
        records = df.to_dict('records')
        
        # Convert date objects to strings for MongoDB
        for record in records:
            for key, value in record.items():
                if isinstance(value, datetime.date):
                    record[key] = value.isoformat()
        
        # Clear existing data and insert new
        db.goals.delete_many({})
        if records:
            db.goals.insert_many(records)
    except Exception as e:
        print(f"Error saving data to MongoDB: {e}")


# Technical needs management
def load_technical_needs():
    try:
        from database import get_database
        db = get_database()
        needs = list(db.technical_needs.find({}, {'_id': 0}))
        if not needs:
            default_needs = [
                'Traktor - Utan Redskap',
                'Fyrhjuling - Utan Redskap',
                'Handverktyg - Övrigt',
                'Elverktyg - Övrigt',
                'Övrigt - Bil'
            ]
            db.technical_needs.insert_many([{'Redskap': need} for need in default_needs])
            return default_needs
        return [need['Redskap'] for need in needs]
    except Exception as e:
        print(f"Error loading technical needs from MongoDB: {e}")
        return []


def save_technical_needs(needs_list):
    try:
        db = get_database()
        db.technical_needs.delete_many({})
        if needs_list:
            db.technical_needs.insert_many([{'Redskap': need} for need in needs_list])
    except Exception as e:
        print(f"Error saving technical needs to MongoDB: {e}")


def get_technical_needs_list():
    try:
        needs = load_technical_needs()
        return sorted([n for n in needs if n.strip()])
    except Exception as e:
        print(f"Error loading technical needs: {e}")
        return []


# Constants and hardcoded data
WEATHER_CONDITIONS = [
    'Soligt',
    'Molnigt',
    'Regnigt',
    'Snöigt',
    'Blåsigt',
    'Torr Mark',
    'Våt Mark',
    'Frusen Mark'
]


# Data validation and conversion functions
def validate_dates(start_date, end_date):
    if not start_date or not end_date:
        raise ValueError("Start- och slutdatum krävs")
    if isinstance(start_date, str):
        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
    if isinstance(end_date, str):
        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
    return start_date, end_date


def convert_rental_info(rental_item, rental_duration, rental_cost_unit):
    needs_rental = bool(rental_item and rental_duration > 0 and rental_cost_unit > 0)
    if not needs_rental:
        return {
            'needs_rental': False,
            'rental_item': "No data",
            'rental_type': "No data",
            'rental_duration': 0,
            'rental_cost_unit': 0,
            'total_rental_cost': 0
        }
    return {
        'needs_rental': True,
        'rental_item': rental_item,
        'rental_duration': rental_duration,
        'rental_cost_unit': rental_cost_unit,
        'total_rental_cost': rental_duration * rental_cost_unit
    }


def save_risk_data(risks):
    """Save risks to MongoDB"""
    try:
        from database import get_database
        db = get_database()
        # Clear existing risks
        db.risks.delete_many({})
        # Insert new risks if any exist
        if risks:
            # Convert any date objects to strings
            formatted_risks = []
            for risk in risks:
                risk_copy = risk.copy()
                for key, value in risk_copy.items():
                    if isinstance(value, (datetime.date, datetime.datetime)):
                        risk_copy[key] = value.isoformat()
                formatted_risks.append(risk_copy)
            
            db.risks.insert_many(formatted_risks)
            print(f"Saved {len(risks)} risks to database")  # Debug print
        return True
    except Exception as e:
        print(f"Error saving risks: {str(e)}")
        return False


def load_risk_data():
    """Load risks from MongoDB"""
    try:
        from database import get_database
        db = get_database()
        risks = list(db.risks.find({}, {'_id': 0}))
        print(f"Loaded {len(risks)} risks from database")  # Debug print
        
        # Convert date strings back to date objects
        for risk in risks:
            if 'action_date' in risk:
                risk['action_date'] = datetime.datetime.strptime(
                    risk['action_date'], '%Y-%m-%d').date()
            if 'follow_up_date' in risk:
                risk['follow_up_date'] = datetime.datetime.strptime(
                    risk['follow_up_date'], '%Y-%m-%d').date()
        
        return risks
    except Exception as e:
        print(f"Error loading risks: {str(e)}")
        return []
