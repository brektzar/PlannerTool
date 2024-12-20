import pandas as pd
import datetime


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
        df = pd.read_csv('planner_tool.csv')
        if df.empty:
            return create_empty_dataframe()

        date_columns = ['Goal_Start_Date', 'Goal_End_Date', 'Task_Start_Date', 'Task_End_Date']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], format='mixed', errors='coerce').dt.date

        # Initialize completion columns if they don't exist
        if 'Goal_Completed' not in df.columns: df['Goal_Completed'] = False
        if 'Task_Completed' not in df.columns: df['Task_Completed'] = False
        return df
    except (FileNotFoundError, pd.errors.EmptyDataError):
        return create_empty_dataframe()


def save_data(df):
    df.to_csv('planner_tool.csv', index=False)


# Technical needs management
def load_technical_needs():
    try:
        df = pd.read_csv('technical_needs.csv')
        df['SortKey'] = df['Redskap'].apply(lambda x: x.split(" - ")[0])
        df = df.sort_values(by='SortKey').drop(columns=['SortKey'])
        return df['Redskap'].tolist()
    except FileNotFoundError:
        default_needs = [
            'Traktor - Utan Redskap',
            'Fyrhjuling - Utan Redskap',
            'Handverktyg - Övrigt',
            'Elverktyg - Övrigt',
            'Övrigt - Bil'
        ]
        pd.DataFrame({'Redskap': default_needs}).to_csv('technical_needs.csv', index=False)
        return default_needs


def save_technical_needs(needs_list):
    pd.DataFrame({'Redskap': needs_list}).to_csv('technical_needs.csv', index=False)


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
