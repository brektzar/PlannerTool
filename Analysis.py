import plotly.express as px
import plotly.graph_objects as plotly_graph_objects
import pandas as pd
import plotly.graph_objects as go

# Importerade moduler som inte används för tillfället men kan behövas senare:
# - from plotly.subplots import make_subplots
# - import numpy as ny
# - import streamlit as st

"""
Emoji-förklaring för användargränssnittet:
📋 : Representerar en specifik uppgift eller task
📅 : Används för datumrelaterade element
🦺 : Indikerar riskbedömningsrelaterade element
👷 : Visar riskanalysrelaterade element
🗂️ : Används för översiktsvyer
🛠️ : Indikerar tekniska behov och verktyg
🔨 : Alternativ ikon för tekniska behov
🎯 : Representerar projektmål
📆 : Används för planeringsrelaterade element
📊 : Indikerar analysrelaterade element
📈 : Visar kostnadsanalys
📉 : Representerar historisk data
✅ : Indikerar slutförda element
✔️ : Alternativ ikon för slutförda element
🔄 : Visar pågående arbete
❌ : Indikerar saknade eller ofullständiga uppgifter
🎉 : Visar att alla uppgifter är klara
💡 : Används för tips och råd
⌚ : Indikerar arbetstidsrelaterade element
🛑 : Används för element utan innehåll
"""

# Stänger av varningar för kedjade tilldelningar i pandas
pd.options.mode.chained_assignment = None

pd.set_option('future.no_silent_downcasting', True)


def create_cost_analysis(dataframe):
    tasks = dataframe[dataframe["Type"] == "Task"]

    # Kostnadsfördelning per mål
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

    # Lägg till tidsbaserad kostnadsfördelning
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

    # Lägg till kostnad per arbetstimme-diagram
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

    # Lägg till kumulativt kostnadsdiagram
    tasks = tasks.sort_values('Task_Start_Date')
    tasks['Cumulative_Cost'] = tasks['Task_Estimated_Cost'].cumsum()

    fig_cumulative = px.line(
        tasks,
        x='Task_Start_Date',
        y='Cumulative_Cost',
        title='Kumulativ Kostnadsutveckling',
        labels={'Cumulative_Cost': 'Total Kostnad', 'Task_Start_Date': 'Datum'}
    )

    # Lägg till kostnadskategorier pajdiagram
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
    """Skapar Gantt-scheman för mål och uppgifter
    Returnerar ett dictionary med översiktsschema och individuella uppgiftsscheman per mål"""
    gantt_figures = {"overview": None, "tasks": {}}

    try:
        if dataframe.empty:
            return gantt_figures

        goals = dataframe[dataframe["Type"] == "Goal"]
        tasks = dataframe[dataframe["Type"] == "Task"]

        if goals.empty:
            return gantt_figures

        # Skapa Gantt-schema för målöversikt
        try:
            goals_data = goals[["Goal_Name", "Goal_Start_Date", "Goal_End_Date", "Goal_Completed"]]
            goals_data.columns = ["Goal", "Start", "Finish", "Completed"]
            goals_data['Completed'] = goals_data['Completed'].fillna(False).infer_objects(copy=False)

            overview_fig = px.timeline(
                goals_data,
                x_start="Start",
                x_end="Finish",
                y="Goal",
                title="Översikt av Projektmål",
                color="Completed",
                color_discrete_map={True: "#2ecc71", False: "#e74c3c"}
            )

            gantt_figures["overview"] = overview_fig
        except Exception as e:
            print(f"Fel vid skapande av översikt Gantt-schema: {str(e)}")
            return gantt_figures

        # Skapa individuella uppgiftsscheman för varje mål
        for _, goal in goals.iterrows():
            try:
                goal_name = goal['Goal_Name']
                goal_tasks = tasks[tasks['Goal_Name'] == goal_name]

                if goal_tasks.empty:
                    continue

                gantt_data = goal_tasks[["Task_Name", "Task_Start_Date", "Task_End_Date", "Task_Completed"]]
                gantt_data.columns = ["Task", "Start", "Finish", "Completed"]
                ####Confirmed working but get futurewarning!!!############################################
                gantt_data['Completed'] = gantt_data['Completed'].fillna(False)
                ##########################################################################################

                ####Hopefully fix for futurewarning!!!####################################################
                #gantt_data['Completed'] = gantt_data['Completed'].result.infer_objects(copy=False)
                ##########################################################################################

                fig = px.timeline(
                    gantt_data,
                    x_start="Start",
                    x_end="Finish",
                    y="Task",
                    title=f"Tidslinje för Uppgifter - {goal_name}",
                    color="Completed",
                    color_discrete_map={True: "#2ecc71", False: "#e74c3c"}
                )

                gantt_figures["tasks"][goal_name] = fig
            except Exception as e:
                print(f"Fel vid skapande av Gantt-schema för mål {goal_name}: {str(e)}")
                continue

        return gantt_figures

    except Exception as e:
        print(f"Fel i create_gantt_charts: {str(e)}")
        return gantt_figures


def calculate_complexity(tasks):
    # Normalisera värden till en skala mellan 0-1
    def normalize(series):
        min_val = series.min()
        max_val = series.max()
        if max_val == min_val:
            return series.map(lambda x: 1)
        return (series - min_val) / (max_val - min_val)

    # Räkna antal tekniska behov/redskap för varje uppgift
    tasks['tools_count'] = tasks['Task_Technical_Needs'].map(
        lambda x: 0 if x == 'No data' else len(str(x).split(','))
    )

    # Basera komplexitet på flera faktorer
    complexity_factors = {
        'time_factor': normalize(tasks['Task_Estimated_Time']),
        'personnel_factor': normalize(tasks['Task_Personnel_Count']),
        'cost_factor': normalize(tasks['Task_Estimated_Cost']),
        'rental_factor': normalize(tasks['Task_Total_Rental_Cost']),
        'weather_factor': tasks['Task_Weather_Conditions'].map(
            lambda x: 0.5 if x == 'No data' else len(str(x).split(',')) / 4
        ),
        'tools_factor': normalize(tasks['tools_count'])  # Ny faktor för redskap
    }
    
    # Uppdaterade vikter med tools_factor
    weights = {
        'time_factor': 0.25,        # Minskad från 0.3
        'personnel_factor': 0.20,   # Minskad från 0.25
        'cost_factor': 0.15,        # Minskad från 0.2
        'rental_factor': 0.15,      # Oförändrad
        'weather_factor': 0.1,      # Oförändrad
        'tools_factor': 0.15        # Ny vikt för redskap
    }
    
    # Beräkna viktad komplexitet
    total_complexity = sum(
        complexity_factors[factor] * weight 
        for factor, weight in weights.items()
    )
    
    # Normalisera till en 1-10 skala för enklare tolkning
    return (total_complexity * 9) + 1


def analyze_work_hours(dataframe):
    tasks = dataframe[dataframe["Type"] == "Task"]

    # Tidsfördelning för uppgifter
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
    # Sätter minimi höjd i pixlar
    fig_duration.update_layout(height=600)
    fig_duration.update_layout(
        height=600,
        xaxis=dict(
            rangeslider=dict(visible=True),  # Aktiverar områdeslider
        ),
        yaxis=dict(title='Uppskattad Tid (timmar)')
    )

    # Resursallokering per mål
    goal_resources = tasks.groupby('Goal_Name').agg({
        'Task_Personnel_Count': 'max',
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

    # Analys av uppgiftskomplexitet
    tasks['Complexity_Score'] = calculate_complexity(tasks)
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

    # Frekvens av verktygsanvändning
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

    # Korrelation med väder
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
        height=500,
        width=350,
    )

    return figure_risk


def create_completion_analysis(dataframe):
    """Skapar visualiseringar för mål- och uppgiftsstatus
    Returnerar en lista med diagram för mål- och uppgiftsstatus"""
    completion_figures = []

    try:
        # Statistisk över målstatus
        goals = dataframe[dataframe['Type'] == 'Goal']
        if goals.empty:
            return [go.Figure().update_layout(
                title="Inga Mål Tillgängliga",
                annotations=[{"text": "Lägg till några mål för att se slutförandestatistik",
                              "x": 0.5, "y": 0.5, "showarrow": False}]
            )]

        goal_completion = goals['Goal_Completed'].fillna(False).infer_objects(copy=False).value_counts()

        fig_goals = go.Figure(data=[
            go.Pie(
                labels=['Slutförda', 'Pågående'],
                values=[
                    goal_completion.get(True, 0),
                    goal_completion.get(False, 0)
                ],
                hole=.3,
                marker_colors=['#2ecc71', '#e74c3c']
            )
        ])
        fig_goals.update_layout(
            title="Målstatus",
            annotations=[{
                'text': f"{(goal_completion.get(True, 0) / len(goals) * 100):.1f}%<br>Slutförda",
                'x': 0.5, 'y': 0.5,
                'font_size': 20,
                'showarrow': False
            }]
        )
        completion_figures.append(fig_goals)

        # Statistisk över uppgiftsstatus
        tasks = dataframe[dataframe['Type'] == 'Task']
        if not tasks.empty:
            task_completion = tasks['Task_Completed'].fillna(False).infer_objects(copy=False).value_counts()

            fig_tasks = go.Figure(data=[
                go.Pie(
                    labels=['Slutförda', 'Pågående'],
                    values=[
                        task_completion.get(True, 0),
                        task_completion.get(False, 0)
                    ],
                    hole=.3,
                    marker_colors=['#2ecc71', '#e74c3c']
                )
            ])
            fig_tasks.update_layout(
                title="Uppgiftsstatus",
                annotations=[{
                    'text': f"{(task_completion.get(True, 0) / len(tasks) * 100):.1f}%<br>Slutförda",
                    'x': 0.5, 'y': 0.5,
                    'font_size': 20,
                    'showarrow': False
                }]
            )
            completion_figures.append(fig_tasks)

            # Uppgiftsstatus per mål
            try:
                # Säkerställ att Task_Completed är korrekt mappat
                tasks['Status'] = tasks['Task_Completed'].fillna(False).infer_objects(copy=False).map({
                    True: 'Slutförda', 
                    False: 'Pågående'
                })
                
                task_by_goal = tasks.groupby(['Goal_Name', 'Status']).size().unstack(fill_value=0)
                
                if 'Slutförda' not in task_by_goal.columns:
                    task_by_goal['Slutförda'] = 0
                if 'Pågående' not in task_by_goal.columns:
                    task_by_goal['Pågående'] = 0

                fig_by_goal = go.Figure(data=[
                    go.Bar(name='Slutförda', y=task_by_goal.index, x=task_by_goal['Slutförda'],
                           orientation='h', marker_color='#2ecc71'),
                    go.Bar(name='Pågående', y=task_by_goal.index, x=task_by_goal['Pågående'],
                           orientation='h', marker_color='#e74c3c')
                ])
                fig_by_goal.update_layout(
                    title="Uppgiftsstatus per Mål",
                    barmode='stack',
                    yaxis_title="Mål",
                    xaxis_title="Antal Uppgifter"
                )
                completion_figures.append(fig_by_goal)
            except Exception as e:
                print(f"Fel vid skapande av uppgiftsstatus per mål-diagram: {str(e)}")

        return completion_figures

    except Exception as e:
        print(f"Fel i create_completion_analysis: {str(e)}")
        return [go.Figure().update_layout(
            title="Fel vid skapande av slutförandeanalys",
            annotations=[{"text": f"Ett fel inträffade: {str(e)}",
                          "x": 0.5, "y": 0.5, "showarrow": False}]
        )]
