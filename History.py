import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime
from Data import current_time, year_one_month_ago
from custom_logging import log_action
import pytz
from database import get_database


def load_historical_data():
    """Load data from MongoDB history collection"""
    try:
        db = get_database()
        data = list(db.history.find({}, {'_id': 0}))
        if not data:
            return pd.DataFrame()
        return pd.DataFrame(data)
    except Exception as e:
        print(f"Error loading historical data: {e}")
        return pd.DataFrame()


def save_year_to_history(current_data):
    """Archive current year's data to MongoDB history collection"""
    try:
        db = get_database()
        
        # Create a copy of the dataframe to avoid modifying the original
        data_to_save = current_data.copy()
        
        # Add year and timestamp information
        data_to_save['Archive_Year'] = datetime.now().year
        data_to_save['Archive_Date'] = current_time()
        
        # Convert DataFrame to records
        records = data_to_save.to_dict('records')
        
        # Convert date objects to strings for MongoDB
        for record in records:
            for key, value in record.items():
                if hasattr(value, 'isoformat'):  # Check if object has isoformat method
                    record[key] = value.isoformat()
        
        # Insert new records
        if records:
            db.history.insert_many(records)
        log_action("save_history", f"Historiken för {year_one_month_ago()} sparades av {st.session_state.username}", "Analy/Historisk Data")
        return True
    except Exception as e:
        st.error(f"Error saving to history: {str(e)}")
        return False


def compare_years(years):
    """Create comparative visualizations between selected years"""
    hist_df = load_historical_data()
    if hist_df.empty:
        st.warning("No historical data available for comparison")
        return

    # Filter for selected years
    df_filtered = hist_df[hist_df['Archive_Year'].isin(years)]

    # Create comparative visualizations
    create_cost_comparison(df_filtered)
    create_resource_comparison(df_filtered)


def create_cost_comparison(dataframe):
    """Create cost comparison visualizations"""
    st.subheader("Cost Comparison Across Years")

    # Yearly total costs
    yearly_costs = dataframe.groupby('Archive_Year').agg({
        'Task_Estimated_Cost': 'sum',
        'Task_Total_Rental_Cost': 'sum'
    }).reset_index()

    figure = px.bar(yearly_costs,
                    x='Archive_Year',
                    y=['Task_Estimated_Cost', 'Task_Total_Rental_Cost'],
                    title='Cost Comparison by Year',
                    barmode='group')
    st.plotly_chart(figure)


def create_resource_comparison(dataframe):
    """Create resource usage comparison visualizations"""
    st.subheader("Resource Usage Comparison")

    # Equipment usage frequency by year
    equipment_usage = dataframe.groupby(['Archive_Year', 'Task_Technical_Needs']).size().reset_index(name='count')
    figure = px.bar(equipment_usage,
                    x='Task_Technical_Needs',
                    y='count',
                    color='Archive_Year',
                    title='Equipment Usage by Year')
    st.plotly_chart(figure)


def show_historical_analysis():
    """Main function to display historical analysis interface"""
    st.title("Historical Data Analysis")

    # Load historical data
    hist_dataframe = load_historical_data()

    if hist_dataframe.empty:
        st.warning("No historical data available. Please archive some data first.")
        return

    # Get available years
    available_years = sorted(hist_dataframe['Archive_Year'].unique())

    # Year selection
    selected_years = st.multiselect(
        "Select years to compare",
        options=available_years,
        default=available_years[-1] if available_years else None
    )

    if selected_years:
        compare_years(selected_years)
    else:
        st.info("Please select at least one year to analyze")
