import streamlit as st
from Data import (load_data, save_data, get_technical_needs_list,
                  load_technical_needs, save_technical_needs, WEATHER_CONDITIONS)
from history import save_year_to_history, show_historical_analysis, load_historical_data
from Analysis import (create_cost_analysis, create_gantt_charts,
                      analyze_work_hours, create_technical_needs_analysis)
from Planning import add_goal, add_task, update_dataframe, toggle_task_completion, toggle_goal_completion
import datetime
import sys
import pandas as pd
import plotly.express as px
from risk_assessment import risk_assessment_app, display_risk_overview

# Set page config
st.set_page_config(layout="wide", page_title="Planeringsverktyg")

author = "Jimmy Nilsson"

st.sidebar.title("Välkommen till mitt Planeringsverktyg!")

st.sidebar.info("""
Detta verktyg hjälper dig att sätta upp mål och planera de uppgifter som behövs för att uppnå dem.
Följ stegen nedan för att komma igång:
""")

st.sidebar.subheader("1. Skapa Mål")
st.sidebar.info("Börja med att definiera dina mål i fliken för målbeskrivning.")

st.sidebar.subheader("2. Planera Uppgifter")
st.sidebar.info("När målen är skapade kan du planera specifika uppgifter under fliken för planering.")

st.sidebar.subheader("3. Följ Statistik och Scheman")
st.sidebar.info("Efter att du har skapat mål och uppgifter kan du visa "
                "statistik och scheman för att följa din framsteg.")

st.sidebar.subheader("4. Bocka av de färdiga målen och uppgifterna!")
st.sidebar.success("När en uppgift är klar så kan du bocka av den och när alla uppgifter för "
                   "ett mål är avklarade så kan man även bocka av målet.\n\n"
                   "Detta är en funktion under uppbyggnad!")

st.sidebar.divider()

st.sidebar.warning("""
Observera:
- Detta verktyg är ett pågående projekt för att lära mig programmering. 
- Det kan förekomma buggar och vissa funktioner kanske inte fungerar perfekt.
""")

st.sidebar.error("""
Jag uppskattar din förståelse och feedback under utvecklingsprocessen. 
Tack för att du testar verktyget!
""")

if 'df' not in st.session_state:
    st.session_state.df = load_data()
if 'edit_mode' not in st.session_state:
    st.session_state.edit_mode = False
if 'edited_data' not in st.session_state:
    st.session_state.edited_data = {}
if 'open_items' not in st.session_state:
    st.session_state.open_items = set()

# Main layout
st.title("Projektplaneringsverktyg")

# Create two columns for the layout
col1, col2 = st.columns([2, 1])

with (col1):
    main_tab1, main_tab2 = st.tabs(["Planering", "Analys"])

    with main_tab1:
        planning_tab1, planning_tab2, planning_tab3, planning_tab4, planning_tab5 = st.tabs([
            "Lägg till Mål",
            "Lägg till Uppgift",
            "Riskbedömning",
            "Översikt",
            "Hantera Tekniska Behov"
        ])

        with planning_tab1:
            with st.form("goal_form", clear_on_submit=True):
                st.subheader("Lägg till Nytt Mål")
                goal_name = st.text_input("Målnamn", key="goal_name")
                goal_description = st.text_area("Målbeskrivning", key="goal_desc")
                goal_dates = st.date_input(
                    "Målets Varaktighet",
                    value=(datetime.datetime.now(), datetime.datetime.now() + datetime.timedelta(days=30)),
                    min_value=datetime.datetime.now()
                )

                submit_goal = st.form_submit_button("Lägg till Mål")
                if submit_goal:
                    st.session_state.df, success = add_goal(st.session_state.df, goal_name,
                                                            goal_description, goal_dates)
                    if success:
                        save_data(st.session_state.df)
                        st.success("Mål tillagt!")

        with planning_tab2:
            if len(st.session_state.df[st.session_state.df['Type'] == 'Goal']) > 0:
                with st.form("task_form", clear_on_submit=True):
                    st.subheader("Lägg till Ny Uppgift")

                    selected_goal = st.selectbox(
                        "Välj Mål",
                        options=st.session_state.df[st.session_state.df['Type'] == 'Goal'][
                            'Goal_Name'].tolist(),
                        key="goal_select"
                    )

                    task_name = st.text_input("Uppgiftsnamn", key="task_name")
                    task_description = st.text_area("Uppgiftsbeskrivning", key="task_desc")
                    task_dates = st.date_input(
                        "Uppgiftens Varaktighet",
                        value=(datetime.datetime.now(), datetime.datetime.now() + datetime.timedelta(days=7)),
                        min_value=datetime.datetime.now(),
                        key="task_dates"
                    )

                    col3, col4 = st.columns(2)
                    with col3:
                        est_time = st.number_input("Uppskattad Tid (timmar)", min_value=0, key="est_time")
                        est_cost = st.number_input("Uppskattad Kostnad", min_value=0.0, step=100.0,
                                                   key="est_cost")

                    with col4:
                        personnel_count = st.slider("Personal som Behövs", 1, 50, 1, key="personnel")
                        tech_needs = st.multiselect("Tekniska Behov", options=get_technical_needs_list(),
                                                    key="tech_needs")
                        weather_conditions_selected = st.multiselect("Väderförhållanden",
                                                                     options=WEATHER_CONDITIONS,
                                                                     key="weather")

                    with st.expander("Hyrinformation"):
                        col5, col6 = st.columns(2)
                        with col5:
                            rental_item = st.text_input("Vad behöver hyras?", key="rental_item")
                            rental_type = st.selectbox("Hyrtyp", ["Per timme", "Per dag"], key="rental_type")

                        with col6:
                            rental_duration = st.number_input("Varaktighet", min_value=0, key="rental_duration")
                            rental_cost_unit = st.number_input("Kostnad per enhet", min_value=0.0, step=100.0,
                                                               key="rental_cost")
                            if rental_duration > 0 and rental_cost_unit > 0:
                                total_rental_cost = rental_duration * rental_cost_unit
                                st.write(f"Total Hyrkostnad: ${total_rental_cost:.2f}")
                            else:
                                total_rental_cost = 0

                        needs_rental_bool = bool(rental_item and rental_duration > 0 and rental_cost_unit > 0)

                        if not needs_rental_bool:
                            rental_item = "No data"
                            rental_type = "No data"
                            rental_duration = 0
                            rental_cost_unit = 0
                            total_rental_cost = 0

                    other_needs = st.text_area("Övriga Behov", key="other_needs")

                    submit_task = st.form_submit_button("Lägg till Uppgift")
                    if submit_task:
                        task_data = {
                            'name': task_name,
                            'description': task_description,
                            'dates': task_dates,
                            'est_time': est_time,
                            'est_cost': est_cost,
                            'tech_needs': tech_needs,
                            'weather': weather_conditions_selected,
                            'rental_item': rental_item,
                            'rental_type': rental_type,
                            'rental_duration': rental_duration,
                            'rental_cost_unit': rental_cost_unit,
                            'personnel': personnel_count,
                            'other_needs': other_needs
                        }
                        st.session_state.df, success = add_task(st.session_state.df, selected_goal,
                                                                task_data)
                        if success:
                            save_data(st.session_state.df)  # Save after adding task
                            st.success("Uppgift tillagd!")
            else:
                st.warning("Lägg till ett mål först innan du skapar uppgifter.")

        with planning_tab3:
            risk_assessment_app(st.session_state.df)

        with planning_tab4:
            st.subheader("Mål- och Uppgiftsöversikt")
            task_column, edit_column = st.columns(2)
            for _, goal in st.session_state.df[st.session_state.df['Type'] == 'Goal'].iterrows():
                with st.expander(f"**Mål**: {goal['Goal_Name']}"):
                    if st.session_state.edit_mode and st.checkbox(f"Redigera {goal['Goal_Name']}",
                                                                  key=f"edit_goal_{goal['Goal_Name']}"):
                        edited_goal = {
                            'name': st.text_input("Målnamn", goal['Goal_Name']),
                            'description': st.text_area("Målbeskrivning", goal['Goal_Description']),
                            'dates': st.date_input(
                                "Målets Varaktighet",
                                value=(goal['Goal_Start_Date'], goal['Goal_End_Date'])
                            )
                        }
                        st.session_state.edited_data[f"goal_{goal['Goal_Name']}"] = edited_goal
                    else:
                        st.write(f"**Beskrivning:** {goal['Goal_Description']}")
                        st.write(f"**Varaktighet:** {goal['Goal_Start_Date']} till {goal['Goal_End_Date']}")

                    tasks = st.session_state.df[
                        (st.session_state.df['Type'] == 'Task') &
                        (st.session_state.df['Goal_Name'] == goal['Goal_Name'])
                        ]

                    if len(tasks) > 0:
                        st.markdown("---")
                        for _, task in tasks.iterrows():
                            if st.checkbox(
                                    f"**{task['Task_Name']}**",
                                    key=f"view_task_{goal['Goal_Name']}_{task['Task_Name']}",
                                    value=f"view_task_{goal['Goal_Name']}_{task['Task_Name']}"
                                          in st.session_state.open_items
                            ):
                                st.session_state.open_items.add(
                                    f"view_task_{goal['Goal_Name']}_{task['Task_Name']}")
                                edited_task = {}

                                if st.session_state.edit_mode and st.checkbox(
                                        "Grundinformation",
                                        key=f"edit_basic_{task['Task_Name']}",
                                        value=f"edit_basic_{task['Task_Name']}" in st.session_state.open_items
                                ):
                                    st.session_state.open_items.add(f"edit_basic_{task['Task_Name']}")
                                    edited_task.update({
                                        'name': st.text_input("**Uppgiftsnamn**", task['Task_Name']),
                                        'description': st.text_area("**Beskrivning**", task['Task_Description']),
                                        'dates': st.date_input("**Varaktighet**", value=(task['Task_Start_Date'],
                                                                                         task['Task_End_Date']))
                                    })
                                else:
                                    st.session_state.open_items.discard(f"edit_basic_{task['Task_Name']}")
                                    st.write(f"**Beskrivning:** {task['Task_Description']}")
                                    st.write(
                                        f"**Varaktighet:** {task['Task_Start_Date']} till {task['Task_End_Date']}")

                                if st.session_state.edit_mode and st.checkbox("**Tid och Kostnad**",
                                                                              key=f"edit_cost_"
                                                                                  f"{task['Task_Name']}"):
                                    column1, column2 = st.columns(2)
                                    with column1:
                                        est_time = st.number_input("**Tid (timmar)**",
                                                                   value=task['Task_Estimated_Time'],
                                                                   min_value=0)
                                    with column2:
                                        est_cost = st.number_input("**Kostnad**",
                                                                   value=task['Task_Estimated_Cost'],
                                                                   min_value=0.0, step=100.0)
                                    edited_task.update({
                                        'est_time': est_time,
                                        'est_cost': est_cost
                                    })
                                else:
                                    st.write(f"**Uppskattad Tid:** {task['Task_Estimated_Time']} timmar")
                                    st.write(f"**Uppskattad Kostnad:** ${task['Task_Estimated_Cost']:.2f}")

                                if st.session_state.edit_mode and st.checkbox("**Krav**",
                                                                              key=f"edit_reqs_"
                                                                                  f"{task['Task_Name']}"):
                                    tech_needs = st.multiselect(
                                        "**Tekniska Behov**",
                                        options=load_technical_needs(),
                                        default=task['Task_Technical_Needs'].split(',') if
                                        task['Task_Technical_Needs'] != "No data" else []
                                    )
                                    weather_conds = st.multiselect(
                                        "**Väderförhållanden**",
                                        options=WEATHER_CONDITIONS,
                                        default=task['Task_Weather_Conditions'].split(',') if
                                        task['Task_Weather_Conditions'] != "No data" else []
                                    )
                                    edited_task.update({
                                        'tech_needs': tech_needs,
                                        'weather': weather_conds
                                    })
                                else:
                                    st.write(f"**Tekniska Behov:** {task['Task_Technical_Needs']}")
                                    st.write(f"**Väderförhållanden:** {task['Task_Weather_Conditions']}")

                                if st.session_state.edit_mode and st.checkbox("**Personal**",
                                                                              key=f"edit_personnel_"
                                                                                  f"{task['Task_Name']}"):
                                    personnel = st.slider(
                                        "**Personalantal**",
                                        min_value=1,
                                        max_value=50,
                                        value=task['Task_Personnel_Count']
                                    )
                                    edited_task.update({'personnel': personnel})
                                else:
                                    st.write(f"**Personalantal:** {task['Task_Personnel_Count']}")

                                if st.session_state.edit_mode and st.checkbox("**Hyrinformation**",
                                                                              key=f"edit_rental_"
                                                                                  f"{task['Task_Name']}"):
                                    column1, column2 = st.columns(2)
                                    with column1:
                                        rental_item = st.text_input("**Vad behöver hyras?**",
                                                                    value=task['Task_Rental_Item'] if
                                                                    task[
                                                                        'Task_Rental_Item'] != "No data" else "")
                                        rental_type = st.selectbox("**Hyrtyp**",
                                                                   ["Timmar", "Dygn"],
                                                                   index=0 if
                                                                   task[
                                                                       'Task_Rental_Type'] == "Per timme" else 1)
                                    with column2:
                                        rental_duration = st.number_input("**Varaktighet**",
                                                                          value=task['Task_Rental_Duration'],
                                                                          min_value=0)
                                        rental_cost = st.number_input("**Kostnad per enhet**",
                                                                      value=task['Task_Rental_Cost_Per_Unit'],
                                                                      min_value=0.0,
                                                                      step=100.0)

                                    total_rental_cost = (
                                        rental_duration * rental_cost if rental_duration > 0 and rental_cost > 0
                                        else 0
                                    )

                                    if total_rental_cost > 0:
                                        st.write(f"**Total Hyrkostnad:** ${total_rental_cost:.2f}")

                                    edited_task.update({
                                        'rental_item': rental_item,
                                        'rental_type': rental_type,
                                        'rental_duration': rental_duration,
                                        'rental_cost_unit': rental_cost,
                                        'total_rental_cost': total_rental_cost
                                    })
                                elif task['Task_Needs_Rental']:
                                    st.write("**Hyrinformation:**")
                                    st.write(f"**- Vad:** {task['Task_Rental_Item']}")
                                    st.write(f"**- Typ:** {task['Task_Rental_Type']}")
                                    st.write(f"**- Varaktighet:** {task['Task_Rental_Duration']} "
                                             f"{task['Task_Rental_Type'].lower()}")
                                    st.write(
                                        f"**- Kostnad per enhet:** ${task['Task_Rental_Cost_Per_Unit']:.2f}")
                                    st.write(f"**- Total hyrkostnad:** ${task['Task_Total_Rental_Cost']:.2f}")

                                if st.session_state.edit_mode and st.checkbox("**Övriga Behov**",
                                                                              key=f"edit_other_"
                                                                                  f"{task['Task_Name']}"):
                                    other_needs = st.text_area(
                                        "**Övriga Behov**",
                                        value=task['Task_Other_Needs'] if task['Task_Other_Needs'] != "No data" else ""
                                    )
                                    edited_task.update({'other_needs': other_needs})
                                else:
                                    st.write(f"**Övriga Behov:** {task['Task_Other_Needs']}")

                                # Add task completion checkbox
                                task_completed = st.checkbox(
                                    "Uppgift slutförd",
                                    value=task['Task_Completed'],
                                    key=f"task_complete_{goal['Goal_Name']}_{task['Task_Name']}"
                                )
                                if task_completed != task['Task_Completed']:
                                    st.session_state.df = toggle_task_completion(
                                        st.session_state.df,
                                        goal['Goal_Name'],
                                        task['Task_Name']
                                    )
                                    save_data(st.session_state.df)

                            else:
                                st.session_state.open_items.discard(
                                    f"view_task_{goal['Goal_Name']}_{task['Task_Name']}")
                    else:
                        st.write("**Inga uppgifter tillagda ännu för detta mål.**")

                    # Add goal completion checkbox
                    tasks = st.session_state.df[
                        (st.session_state.df['Type'] == 'Task') &
                        (st.session_state.df['Goal_Name'] == goal['Goal_Name'])
                        ]

                    goal_completed = st.checkbox(
                        "Mål slutfört",
                        value=goal['Goal_Completed'],
                        disabled=not all(tasks['Task_Completed']),
                        key=f"goal_complete_{goal['Goal_Name']}"
                    )

                    if goal_completed != goal['Goal_Completed']:
                        st.session_state.df, success, message = toggle_goal_completion(
                            st.session_state.df, goal['Goal_Name'])
                        if success:
                            save_data(st.session_state.df)

            with edit_column:
                st.session_state.edit_mode = st.toggle("Redigera Mål och Uppgifter")

                if st.session_state.edit_mode and st.session_state.edited_data:
                    if st.button("Spara Ändringar"):
                        st.session_state.df = update_dataframe(st.session_state.df,
                                                               st.session_state.edited_data)
                        save_data(st.session_state.df)

                        st.session_state.edited_data = {}
                        st.session_state.open_items = set()
                        st.session_state.edit_mode = False

                        st.success("Ändringar sparade!")

        with planning_tab5:
            st.subheader("Hantera Tekniska Behov")

            tech_needs = load_technical_needs()

            categories = sorted(set(need.split(" - ")[0] for need in tech_needs))

            with st.expander("Lägg till nytt redskap"):
                with st.form("add_need"):
                    category = st.selectbox(
                        "Välj Kategori",
                        options=categories
                    )
                    need = st.text_input("Nytt redskap")
                    submit_need = st.form_submit_button("Lägg till redskap")
                    if submit_need and need:
                        full_need = f"{category} - {need}"
                        if full_need not in tech_needs:
                            tech_needs.append(full_need)
                            tech_needs.sort(key=lambda x: x.split(" - ")[0])
                            save_technical_needs(tech_needs)
                            st.success(f"Redskap '{full_need}' tillagt!")
                            st.rerun()
                        else:
                            st.error("Detta redskap finns redan!")

            st.subheader("Befintliga Redskap")
            for category in categories:
                with st.expander(category):
                    category_needs = [need for need in tech_needs if need.startswith(category)]
                    for need in category_needs:
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.write(need)
                        with col2:
                            if st.button("Ta Bort", key=f"del_{need}"):
                                tech_needs.remove(need)
                                save_technical_needs(tech_needs)
                                st.success(f"Behov '{need}' borttaget!")
                                st.rerun()

    with main_tab2:  # Analys Tab

        st.subheader("Analys")

        gantt_charts, cost_analysis, work_hours, technical_needs, historical_data, \
            risk_matrix, risk_analysis, other = st.tabs([
                "Gantt Schema",
                "Kostnadsanalys",
                "Arbetstid",
                "Tekniska Behov",
                "Historisk Data",
                "Riskbedömning",
                "Riskanalys",
                "Annat"])

        with cost_analysis:
            # Get all cost analysis figures at once
            cost_figures = create_cost_analysis(st.session_state.df)
            for fig in cost_figures:
                st.plotly_chart(fig, use_container_width=True)

        with gantt_charts:
            gantt_figs = create_gantt_charts(st.session_state.df)
            if gantt_figs:
                # Display overview chart first (outside of expanders)
                if gantt_figs["overview"] is not None:
                    st.plotly_chart(gantt_figs["overview"], use_container_width=True)

                # Display task timelines in expanders
                for goal_name, fig in gantt_figs["tasks"].items():
                    with st.expander(f"Tidslinje för {goal_name}"):
                        st.plotly_chart(fig, use_container_width=True)

                if not gantt_figs["tasks"]:
                    st.info("Inga uppgifter att visa i tidslinjer")

            else:
                st.warning("Inga uppgifter att visa i Gantt-schema")

        with work_hours:
            work_figures = analyze_work_hours(st.session_state.df)
            for fig in work_figures:
                st.plotly_chart(fig, use_container_width=True)

        with technical_needs:
            tech_figures = create_technical_needs_analysis(st.session_state.df)
            for fig in tech_figures:
                if fig is not None:
                    st.plotly_chart(fig, use_container_width=True)

            # Add weather conditions summary
            tasks = st.session_state.df[st.session_state.df['Type'] == 'Task']
            weather_counts = []
            for weather in tasks['Task_Weather_Conditions'].str.split(','):
                if isinstance(weather, list):
                    weather_counts.extend([w.strip() for w in weather if w != 'No data'])

            if weather_counts:
                weather_df = pd.DataFrame({
                    'Weather': weather_counts
                }).value_counts().reset_index()
                weather_df.columns = ['Weather', 'Count']
                st.plotly_chart(px.pie(weather_df, values='Count', names='Weather',
                                       title='Väderbehov'), use_container_width=True)

        with historical_data:
            # Add Archive Data button at the top of historical data tab
            if st.button("Arkivera Årets Data"):
                if save_year_to_history(st.session_state.df):
                    st.success("Data arkiverad!")
                else:
                    st.error("Fel vid arkivering av data")

            # Always try to show historical analysis
            hist_df = load_historical_data()
            if not hist_df.empty:
                show_historical_analysis()
            else:
                st.warning("Ingen historisk data tillgänglig. "
                           "Använd 'Arkivera Årets Data' för att spara nuvarande data.")

        with risk_matrix:
            display_risk_overview(st.session_state.df, st.session_state.risks, context="analysis")

        with risk_analysis:
            from risk_assessment import create_risk_analysis

            create_risk_analysis(st.session_state.risks)

st.divider()

col1, col2 = st.columns([2, 1])
with col2:
    st.info(f"//// By: {author}  -  st Version: {st.__version__} - "
            f"Python Version: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} ////")
    st.write("GitHub: --->https://github.com/brektzar/PlannerTool/tree/master<---")
