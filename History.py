import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime


def load_historical_data():
    """Load data from history.csv"""
    try:
        return pd.read_csv('history.csv')
    except FileNotFoundError:
        return pd.DataFrame()


def save_year_to_history(current_data):
    """Archive current year's data to history.csv"""
    try:
        # Load existing historical data
        hist_df = load_historical_data()

        # Add year and timestamp information
        current_data['Archive_Year'] = datetime.now().year
        current_data['Archive_Date'] = datetime.now().strftime('%Y-%m-%d')

        # Combine with existing historical data
        if hist_df.empty:
            hist_df = current_data
        else:
            hist_df = pd.concat([hist_df, current_data], ignore_index=True)

        # Save to history.csv
        hist_df.to_csv('history.csv', index=False)
        return True
    except Exception as exception:
        st.error(f"Error saving to history: {str(exception)}")
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
