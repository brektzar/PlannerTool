import plotly.express as px
import plotly.graph_objects as plotly_graph_objects
import pandas as pd
# from plotly.subplots import make_subplots
# import numpy as ny
# import streamlit as st
#

pd.options.mode.chained_assignment = None


def create_cost_analysis(dataframe):
    tasks = dataframe[dataframe["Type"] == "Task"]

    # Cost distribution by goal
    goal_costs = tasks.groupby("Goal_Name").agg({
        "Task_Estimated_Cost": "sum",
        "Task_Total_Rental_Cost": "sum"
    }).reset_index()
    goal_costs.loc[:, "Övriga Kostnader"] = goal_costs["Task_Estimated_Cost"] - goal_costs["Task_Total_Rental_Cost"]

    figure_costs = px.bar(
        goal_costs,
        x="Goal_Name",
        y=["Task_Total_Rental_Cost", "Övriga Kostnader"],
        title="Kostnadsfördelning per Mål",
        labels={"value": "Kostnad", "variable": "Typ"},
        barmode="stack"
    )

    # Add time-based cost distribution
    tasks['Month'] = pd.to_datetime(tasks['Task_Start_Date']).dt.strftime('%Y-%m')
    monthly_costs = tasks.groupby('Month').agg({
        'Task_Estimated_Cost': 'sum'
    }).reset_index()

    fig_monthly_costs = px.line(
        monthly_costs,
        x='Month',
        y='Task_Estimated_Cost',
        title='Månatlig Kostnadsfördelning',
        labels={'Task_Estimated_Cost': 'Kostnad', 'Month': 'Månad'}
    )

    # Add cost per personnel hour chart
    tasks['Cost_Per_Hour'] = tasks['Task_Estimated_Cost'] / (
                tasks['Task_Estimated_Time'] * tasks['Task_Personnel_Count'])
    tasks['Cost_Per_Hour'] = tasks['Cost_Per_Hour'].fillna(0)

    fig_cost_per_hour = px.bar(
        tasks,
        x='Task_Name',
        y='Cost_Per_Hour',
        color='Goal_Name',
        title='Kostnad per Arbetstimme',
        labels={'Cost_Per_Hour': 'Kostnad/Timme', 'Task_Name': 'Uppgift'}
    )

    # Add cumulative cost chart
    tasks = tasks.sort_values('Task_Start_Date')
    tasks['Cumulative_Cost'] = tasks['Task_Estimated_Cost'].cumsum()

    fig_cumulative = px.line(
        tasks,
        x='Task_Start_Date',
        y='Cumulative_Cost',
        title='Kumulativ Kostnadsutveckling',
        labels={'Cumulative_Cost': 'Total Kostnad', 'Task_Start_Date': 'Datum'}
    )

    # Add cost categories pie chart
    cost_categories = tasks.groupby('Goal_Name').agg({
        'Task_Estimated_Cost': 'sum'
    }).reset_index()

    fig_cost_categories = px.pie(
        cost_categories,
        values='Task_Estimated_Cost',
        names='Goal_Name',
        title='Kostnadsfördelning per Projekt'
    )

    return [figure_costs, fig_monthly_costs, fig_cost_categories, fig_cost_per_hour, fig_cumulative]


def create_gantt_charts(dataframe):
    goals = dataframe[dataframe["Type"] == "Goal"]
    tasks = dataframe[dataframe["Type"] == "Task"]
    gantt_figures = {"overview": None, "tasks": {}}

    if goals.empty:
        return {"overview": None, "tasks": {}}

    # Create goals overview Gantt chart first
    goals_data = goals[["Goal_Name", "Goal_Start_Date", "Goal_End_Date"]]
    goals_data.columns = ["Goal", "Start", "Finish"]

    overview_fig = px.timeline(
        goals_data,
        x_start="Start",
        x_end="Finish",
        y="Goal",
        title="Översikt av Projektmål"
    )

    # Store the overview chart
    gantt_figures["overview"] = overview_fig

    for _, goal in goals.iterrows():
        goal_name = goal['Goal_Name']
        goal_tasks = tasks[tasks['Goal_Name'] == goal_name]

        if goal_tasks.empty:
            continue

        # Create timeline data for this goal's tasks
        gantt_data = goal_tasks[["Task_Name", "Task_Start_Date", "Task_End_Date"]]
        gantt_data.columns = ["Task", "Start", "Finish"]

        # Create Gantt chart for this goal
        fig = px.timeline(
            gantt_data,
            x_start="Start",
            x_end="Finish",
            y="Task",
            title=f"Tidslinje för Uppgifter - {goal_name}"
        )

        gantt_figures["tasks"][goal_name] = fig

    return gantt_figures


def analyze_work_hours(dataframe):
    tasks = dataframe[dataframe["Type"] == "Task"]

    # Task duration distribution
    fig_duration = px.bar(
        tasks,
        x='Task_Name',
        y='Task_Estimated_Time',
        color='Goal_Name',
        title='Uppgifternas Tidsfördelning',
        labels={'Task_Estimated_Time': 'Uppskattad Tid (timmar)',
                'Task_Name': 'Uppgift',
                'Goal_Name': 'Mål'},
    )
    # Set minimum height in pixels
    fig_duration.update_layout(height=600)
    fig_duration.update_layout(
        height=600,
        xaxis=dict(
            rangeslider=dict(visible=True),  # Enable range slider
        ),
        yaxis=dict(title='Uppskattad Tid (timmar)')
    )

    # Resource allocation by goal
    goal_resources = tasks.groupby('Goal_Name').agg({
        'Task_Personnel_Count': 'sum',
        'Task_Estimated_Time': 'sum'
    }).reset_index()

    fig_resources = px.scatter(
        goal_resources,
        x='Task_Personnel_Count',
        y='Task_Estimated_Time',
        # text='Goal_Name',
        title='Resursallokering per Mål',
        color='Goal_Name',
        labels={
            'Task_Personnel_Count': 'Total Personal',
            'Task_Estimated_Time': 'Total Tid (timmar)',
            'Goal_Name': 'Mål'
        }
    )

    # Task complexity analysis
    tasks['Complexity_Score'] = tasks['Task_Estimated_Time'] * tasks['Task_Personnel_Count']
    fig_complexity = px.bar(
        tasks.sort_values('Complexity_Score', ascending=False),
        x='Task_Name',
        y='Complexity_Score',
        color='Goal_Name',
        title='Uppgiftskomplexitet',
        labels={'Complexity_Score': 'Komplexitetspoäng',
                'Task_Name': 'Uppgift',
                'Goal_Name': 'Mål'}
    )

    return [fig_duration, fig_resources, fig_complexity]


def create_technical_needs_analysis(dataframe):
    tasks = dataframe[dataframe["Type"] == "Task"]

    # Tool usage frequency
    tool_counts = []
    for tools in tasks['Task_Technical_Needs'].str.split(','):
        if isinstance(tools, list):
            tool_counts.extend(tools)

    tool_freq = pd.DataFrame({
        'Tool': tool_counts
    }).value_counts().reset_index()
    tool_freq.columns = ['Tool', 'Count']

    fig_tool_usage = px.bar(
        tool_freq,
        x='Tool',
        y='Count',
        title='Verktygsanvändning',
        labels={'Count': 'Antal Användningar'}
    )

    # Weather correlation
    weather_tools = []
    for idx, row in tasks.iterrows():
        if row['Task_Weather_Conditions'] != 'No data' and row['Task_Technical_Needs'] != 'No data':
            weathers = str(row['Task_Weather_Conditions']).split(',')
            tools = str(row['Task_Technical_Needs']).split(',')
            for weather in weathers:
                for tool in tools:
                    weather_tools.append({
                        'Weather': weather.strip(),
                        'Tool': tool.strip()
                    })

    weather_tool_df = pd.DataFrame(weather_tools)
    if not weather_tool_df.empty:
        fig_weather_correlation = px.density_heatmap(
            weather_tool_df,
            x='Weather',
            y='Tool',
            title='Väder och Verktygskorrelation'
        )
    else:
        fig_weather_correlation = None

    return [fig_tool_usage, fig_weather_correlation]


def create_risk_matrix():
    data = [[1, 2, 3, 4],
            [2, 4, 6, 8],
            [3, 6, 9, 12],
            [4, 8, 12, 16]]

    dataframe = pd.DataFrame(data)

    figure_risk = plotly_graph_objects.Figure(data=plotly_graph_objects.Heatmap(
        z=dataframe,
        showscale=False,
        colorscale=[
            [0, "green"], [0.16, "green"],
            [0.16, "yellow"], [0.40, "yellow"],
            [0.40, "rgb(255,165,0)"], [0.60, "rgb(255,165,0)"],
            [0.60, "red"], [1.0, "red"]
        ],
        x=["1", "2", "3", "4"],
        y=["1", "2", "3", "4"],
        text=dataframe,
        texttemplate="%{text}",
        textfont={"size": 20},
        xgap=2,
        ygap=2,
    ))

    figure_risk.update_layout(
        title="Riskbedömningsmatris",
        xaxis_title="Sannolikhet",
        yaxis_title="Konsekvens",
    )

    return figure_risk
