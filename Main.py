import streamlit as st
import datetime
import sys
import pandas as pd
import plotly.express as px
from auth import init_auth, show_login_page, logout
from logging import log_action

# Importerat från andra filer
from Data import (load_data, save_data, get_technical_needs_list,
                  load_technical_needs, save_technical_needs, WEATHER_CONDITIONS)
from History import save_year_to_history, show_historical_analysis, load_historical_data
from Analysis import (create_cost_analysis, create_gantt_charts,
                      analyze_work_hours, create_technical_needs_analysis, create_completion_analysis)
from Planning import (add_goal, add_task, update_dataframe, toggle_task_completion, toggle_goal_completion,
                      bug_tracking_tab)
from Risk_Assessment import risk_assessment_app, display_risk_overview
from Admin import admin_panel

# """
# Emojis som används i programmet:
# 📋 : Uppgift
# 📅 :
# 🦺 : Riskbedömning
# 👷 : Riskanalys
# 🗂️ : Översikt
# 🛠️ : Tekniska Behov
# 🔨 : Tekniska Behov
# 🎯 : Mål
# 📆 : Planering
# 📊 : Analys
# 📈 : Kostnadsanalys
# 📉 : Historisk Data
# ✅ :
# ✔️ :
# 🔄 : Under Arbete
# ❌ : Saknar uppgifter
# �� : Alla uppgifter klara
# 💡 : Tips
# ⌚ : Arbetstid
# 🐛 : Rapportera Buggar
# 🛑 : Inget Ännu
# """


# Set page config
st.set_page_config(layout="wide", page_title="Planeringsverktyg")

# Add custom styling
st.markdown("""
<style>
    /* Modern cards for expanders */
    div.stExpander {
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        padding: 10px;
        margin: 10px 0;
        border: 1px solid rgba(255, 255, 255, 0.1);
        transition: all 0.3s ease;
    }
    div.stExpander:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }

    /* Animated progress bars */
    .stProgress > div > div > div > div {
        background: linear-gradient(45deg, #2ecc71, #27ae60);
        transition: width 1s ease-in-out;
    }

    /* Fancy metrics */
    div[data-testid="stMetricValue"] {
        font-size: 2rem;
        background: linear-gradient(45deg, #1F77B4, #2ecc71);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* Button animations */
    .stButton>button {
        border-radius: 20px;
        padding: 10px 25px;
        border: none;
        background: linear-gradient(45deg, #1F77B4, #2980b9);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }

    /* Form fields styling */
    div[data-baseweb="input"] input,
    div[data-baseweb="textarea"] textarea {
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        background-color: rgba(255, 255, 255, 0.05);
    }

    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: rgba(28, 31, 38, 0.95);
        backdrop-filter: blur(10px);
    }

    /* Headers with gradient */
    h1, h2, h3 {
        background: linear-gradient(45deg, #1F77B4, #2ecc71);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: bold;
    }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        padding: 5px;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 5px;
        padding: 10px 16px;
        background-color: transparent;
        color: #FFFFFF;
        transition: all 0.3s ease;
    }

    .stTabs [data-baseweb="tab"]:hover {
        background-color: rgba(255, 255, 255, 0.1);
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(45deg, #1F77B4, #2980b9);
        color: white !important;
        font-weight: bold;
    }

    /* Make sure tab text is always visible */
    .stTabs [role="tab"] p {
        color: inherit !important;
    }

    /* Info boxes */
    div.stAlert {
        border-radius: 10px;
        border: none;
        padding: 15px;
        backdrop-filter: blur(10px);
    }

    /* Fix for button text color */
    .stButton button:active {
        color: white !important;
    }
    .stButton button:focus {
        color: white !important;
    }
    .stButton button:hover {
        color: white !important;
    }
    .stButton button p {
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

author = "Jimmy Nilsson"

# Initialize authentication state at the very beginning
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_role' not in st.session_state:
    st.session_state.user_role = None

# Main application function
def main_app():
    """Main application logic - only shown when user is authenticated"""
    # Initialize session state variables
    if 'df' not in st.session_state:
        st.session_state.df = load_data()
    if 'edit_mode' not in st.session_state:
        st.session_state.edit_mode = False
    if 'edited_data' not in st.session_state:
        st.session_state.edited_data = {}
    if 'open_items' not in st.session_state:
        st.session_state.open_items = set()
    if 'risks' not in st.session_state:
        st.session_state.risks = []

    # Add logout button to sidebar
    st.sidebar.markdown(f"""
    ### 👤 Inloggad användare
    **Användarnamn:** {st.session_state.username}  
    **Roll:** {st.session_state.user_role}
    """)

    if st.sidebar.button("Logga ut"):
        logout()
        st.rerun()

    # Your existing main app code here
    st.title("Projektplaneringsverktyg")
    
    # Sidebar content
    st.sidebar.title("Välkommen till mitt Planeringsverktyg!")
    with st.sidebar.expander("Information om Verktyget"):

        st.info("""
        Detta verktyg hjälper dig att sätta upp mål och planera de uppgifter som behövs för att uppnå dem.
        Följ stegen nedan för att komma igång:
        """)

        st.subheader("1. Skapa Mål")
        st.info("Börja med att definiera dina mål i fliken för målbeskrivning.")

        st.subheader("2. Planera Uppgifter")
        st.info("När målen är skapade kan du planera specifika uppgifter under fliken för planering.")

        st.subheader("3. Följ Statistik och Scheman")
        st.info("Efter att du har skapat mål och uppgifter kan du visa "
                        "statistik och scheman för att följa din framsteg.")

        st.subheader("4. Bocka av de färdiga målen och uppgifterna!")
        st.success("När en uppgift är klar så kan du bocka av den och när alla uppgifter för "
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

    # Create two columns for the layout
    col1, col2 = st.columns([9, 1])

    with (col1):
        # Create tabs based on user role
        if st.session_state.user_role == 'admin':
            main_tab1, main_tab2, main_tab3, main_tab4 = st.tabs([
                "📆 **Planering**",
                "📊 **Analys**",
                "🐛 Rapportera Buggar",
                "🔐 Admin Panel"
            ])
        else:
            main_tab1, main_tab2, main_tab3 = st.tabs([
                "📆 **Planering**",
                "📊 **Analys**",
                "🐛 Rapportera Buggar"
            ])

        with main_tab1:
            planning_tab1, planning_tab2, planning_tab3, planning_tab4, planning_tab5 = st.tabs([
                "🎯 Lägg till Mål",
                "📋 Lägg till Uppgift",
                "🦺 Riskbedömning",
                "🗂️ Översikt",
                "🛠️ Hantera Tekniska Behov"
            ])

            with planning_tab1:
                with st.form("goal_form", clear_on_submit=True):
                    st.subheader("🎯 Lägg till Nytt Mål")

                    st.write(f"Här lägger man till nya mål.")
                    st.write(f"Mål är endast övergripande, exempelnamn: "
                             f"'Bygg ett nytt Hantverkshus'")
                    st.write(f"Var så beskrivande som möjligt.")
                    st.write(f"**Viktig**: Fyll i alla fält.")
                    st.divider()

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
                            st.balloons()
                            st.success("🎉 Mål tillagt!")

            with planning_tab2:
                if len(st.session_state.df[st.session_state.df['Type'] == 'Goal']) > 0:
                    with st.form("task_form", clear_on_submit=True):
                        st.subheader("📋 Lägg till Ny Uppgift")
                        st.write(f"Här lägger man till nya uppgifter.")
                        st.write(f"Uppgifterna är mer inngående än målen, exempelnamn: "
                                 f"'Gräv nya stolphål med grävmaskin'")
                        st.write(f"I uppgiften är det än viktigare att man är så beskrivande som möjligt.")
                        st.write(f"**Viktig**: Fyll i alla fält. (Hyrinformation fylls endast i om något ska hyras)")
                        st.divider()

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
                            personnel_count = st.slider("Personal som Behövs", 1, 7, 1, key="personnel")
                            tech_needs = st.multiselect("Tekniska Behov", options=get_technical_needs_list(),
                                                        key="tech_needs")
                            weather_conditions_selected = st.multiselect("Väderförhållanden",
                                                                         options=WEATHER_CONDITIONS,
                                                                         key="weather")

                        with st.expander("Hyrinformation"):
                            col5, col6 = st.columns(2)
                            with col5:
                                rental_item = st.text_input("Vad behöver hyras?", key="rental_item")
                                rental_type = st.selectbox("Hyrtyp", ["Timmar", "Dygn"], key="rental_type")

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

                st.write(f"Här får man en översikt över de mål och uppgifter man lagt till.")
                st.write(f"Man kan ändra en uppgift genom att trycka på 'Redigera Mål och Uppgifter'.")
                st.write(f"**Viktig**: Tryck på knappen innan du expanderar ett mål om du ska redigera,"
                         f" har du expanderat ett mål så förminska detta först!")
                st.write(f"Man kan även trycka i att uppgifterna och målen är färdiga på denna sidan, observera att alla "
                         f"uppgifter måste vara klara innan man kan slutföra målet.")
                st.warning("Denna biten av verktyget är lite segt och mindre buggar existerar!")
                st.write(f"✅= klar, 🔄= Under Arbete, ❌= Saknar uppgifter")
                st.divider()

                task_column, task_column2, edit_column = st.columns(3)
                with task_column:
                    st.write("Antal Mål:")
                    st.write(st.session_state.df[st.session_state.df['Type'] == 'Goal'].shape[0])
                with task_column2:
                    st.write("Antal Uppgifter:")
                    st.write(st.session_state.df[st.session_state.df['Type'] == 'Task'].shape[0])

                with edit_column:
                    st.session_state.edit_mode = st.toggle("Redigera Mål och Uppgifter")

                    if st.session_state.edited_data:  # Only show if there are changes to save
                        if st.button("Spara Ändringar"):
                            st.session_state.df = update_dataframe(st.session_state.df, st.session_state.edited_data)
                            save_data(st.session_state.df)  # Save to file
                            
                            # Clear the edited data and reset states
                            st.session_state.edited_data = {}
                            st.session_state.open_items = set()
                            st.session_state.edit_mode = False  # Turn off edit mode
                            
                            st.success("Ändringar sparade!")
                            st.rerun()

                st.divider()

                for _, goal in st.session_state.df[st.session_state.df['Type'] == 'Goal'].iterrows():
                    # Get tasks for this goal
                    tasks = st.session_state.df[
                        (st.session_state.df['Type'] == 'Task') &
                        (st.session_state.df['Goal_Name'] == goal['Goal_Name'])
                    ]
                    
                    # Determine icon based on task status
                    if tasks.empty:
                        completion_icon = "❌"  # No tasks
                    else:
                        is_completed = all(tasks['Task_Completed']) and goal['Goal_Completed']
                        completion_icon = "✅" if is_completed else "🔄"
                    
                    with st.expander(f"{completion_icon} **Mål**: {goal['Goal_Name']}"):
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
                                task_col1, task_col2 = st.columns([8, 2])
                                
                                with task_col1:
                                    if st.button(
                                        f"�� **{task['Task_Name']}**",
                                        key=f"view_task_{goal['Goal_Name']}_{task['Task_Name']}"
                                    ):
                                        # Toggle the task view state
                                        task_key = f"view_task_{goal['Goal_Name']}_{task['Task_Name']}"
                                        if task_key in st.session_state.open_items:
                                            st.session_state.open_items.remove(task_key)
                                        else:
                                            st.session_state.open_items.add(task_key)
                                        st.rerun()
                                
                                with task_col2:
                                    # Show a small indicator if task is open
                                    if f"view_task_{goal['Goal_Name']}_{task['Task_Name']}" in st.session_state.open_items:
                                        st.markdown("🔽")
                                    else:
                                        st.markdown("▶️")
                                
                                # Show task details if it's open
                                if f"view_task_{goal['Goal_Name']}_{task['Task_Name']}" in st.session_state.open_items:
                                    task_column, task_column2 = st.columns([2, 8])
                                    
                                    with task_column2:
                                        st.divider()
                                        edited_task = {}

                                        # Rest of your task detail display code remains the same
                                        if st.session_state.edit_mode:
                                            st.divider()
                                            if st.checkbox("Grundinformation", key=f"edit_basic_{task['Task_Name']}"):
                                                edited_task.update({
                                                    'name': st.text_input("**Uppgiftsnamn**", task['Task_Name']),
                                                    'description': st.text_area("**Beskrivning**", task['Task_Description']),
                                                    'dates': st.date_input("**Varaktighet**", value=(task['Task_Start_Date'],
                                                                                                     task['Task_End_Date']))
                                                })

                                            if st.checkbox("**Tid och Kostnad**", key=f"edit_cost_{task['Task_Name']}"):
                                                # column1, column2 = st.columns(2)
                                                
                                                est_time = st.number_input("**Tid (timmar)**",
                                                                               value=task['Task_Estimated_Time'],
                                                                               min_value=0)
                                                
                                                est_cost = st.number_input("**Kostnad**",
                                                                               value=task['Task_Estimated_Cost'],
                                                                               min_value=0.0, step=100.0)
                                                edited_task.update({
                                                    'est_time': est_time,
                                                    'est_cost': est_cost
                                                })

                                            if st.checkbox("**Krav**", key=f"edit_reqs_{task['Task_Name']}"):
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

                                            if st.checkbox("**Personal**", key=f"edit_personnel_{task['Task_Name']}"):
                                                personnel = st.slider(
                                                    "**Personalantal**",
                                                    min_value=1,
                                                    max_value=50,
                                                    value=task['Task_Personnel_Count']
                                                )
                                                edited_task.update({'personnel': personnel})

                                            if st.checkbox("**Hyrinformation**", key=f"edit_rental_{task['Task_Name']}"):
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

                                                edited_task.update({
                                                    'rental_item': rental_item,
                                                    'rental_type': rental_type,
                                                    'rental_duration': rental_duration,
                                                    'rental_cost_unit': rental_cost,
                                                    'total_rental_cost': total_rental_cost
                                                })

                                            if st.checkbox("**Övriga Behov**", key=f"edit_other_{task['Task_Name']}"):
                                                other_needs = st.text_area(
                                                    "**Övriga Behov**",
                                                    value=task['Task_Other_Needs'] if task['Task_Other_Needs'] != "No data" else ""
                                                )
                                                edited_task.update({'other_needs': other_needs})

                                            if edited_task:
                                                task_key = f"task_{goal['Goal_Name']}_{task['Task_Name']}"
                                                st.session_state.edited_data[task_key] = edited_task
                                        else:
                                            st.write(f"**Beskrivning:** {task['Task_Description']}")
                                            st.write(
                                                f"**Varaktighet:** {task['Task_Start_Date']} till {task['Task_End_Date']}")

                                        if not st.session_state.edit_mode:
                                            st.write(f"**Uppskattad Tid:** {task['Task_Estimated_Time']} timmar")
                                            st.write(f"**Uppskattad Kostnad:** SEK {task['Task_Estimated_Cost']:.2f}")

                                        if not st.session_state.edit_mode:
                                            st.write(f"**Tekniska Behov:** {task['Task_Technical_Needs']}")
                                            st.write(f"**Väderförhållanden:** {task['Task_Weather_Conditions']}")

                                        if not st.session_state.edit_mode:
                                            st.write(f"**Personalantal:** {task['Task_Personnel_Count']}")

                                        if not st.session_state.edit_mode and task['Task_Needs_Rental']:
                                            st.write("**Hyrinformation:**")
                                            st.write(f"**- Vad:** {task['Task_Rental_Item']}")
                                            st.write(f"**- Typ:** {task['Task_Rental_Type']}")
                                            st.write(f"**- Varaktighet:** {task['Task_Rental_Duration']} "
                                                     f"{task['Task_Rental_Type'].lower()}")
                                            st.write(
                                                f"**- Kostnad per enhet:** SEK {task['Task_Rental_Cost_Per_Unit']:.2f}")
                                            st.write(f"**- Total hyrkostnad:** SEK {task['Task_Total_Rental_Cost']:.2f}")

                                        if not st.session_state.edit_mode:
                                            st.write(f"**Övriga Behov:** {task['Task_Other_Needs']}")

                                        # Add task completion checkbox
                                        st.divider()
                                        task_completed = st.checkbox(
                                            "Uppgift slutförd",
                                            value=task['Task_Completed'],
                                            key=f"task_complete_{goal['Goal_Name']}_{task['Task_Name']}"
                                        )
                                        st.divider()
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

                        # Check if there are any tasks for this goal
                        if len(tasks) > 0:
                            # Check completion status and show appropriate message
                            all_tasks_completed = all(tasks['Task_Completed'])
                            if all_tasks_completed != goal['Goal_Completed']:
                                # Automatically update goal completion status
                                st.session_state.df, success, message = toggle_goal_completion(
                                    st.session_state.df, goal['Goal_Name'])
                                if success:
                                    save_data(st.session_state.df)
                                    if all_tasks_completed:
                                        st.success("🎉 Alla uppgifter är klara! Målet har automatiskt markerats som slutfört.")
                                    else:
                                        st.info("ℹ️ Målet har automatiskt markerats som ej slutfört då inte alla uppgifter är klara.")
                            else:
                                # Show current status
                                if all_tasks_completed:
                                    st.success("✅ Målet är slutfört!")
                                else:
                                    st.info("🔄 Målet har pågående uppgifter.")
                        else:
                            st.warning("❌ Ingen uppgift har ännu gjorts för detta målet.")

                with planning_tab5:
                    st.subheader("Hantera Tekniska Behov")

                    st.write(f"Här lägger man till redskap som sedan blir valbara när man skapar uppgifter.")
                    st.write(f"Verktygen delas upp i övergripande kategorier, välj en kategori och skriv namnet på redskapet.")

                    st.divider()

                    tech_needs = load_technical_needs()

                    categories = sorted(set(need.split(" - ")[0] for need in tech_needs))

                    with st.expander("🔨 Lägg till nytt redskap"):
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
            st.info("💡 **Tips:**\n"
                    "- Dra i diagrammen för att zooma\n"
                    "- Dubbelklicka för att återställa vyn\n"
                    "- Hovra över datapunkter för mer information")
            gantt_charts, cost_analysis, work_hours, technical_needs, completion_status, historical_data, \
                risk_matrix, risk_analysis, other = st.tabs([
                    "📊 Gantt Schema",
                    "📈 Kostnadsanalys",
                    "⌚ Arbetstid",
                    "🔨 Tekniska Behov",
                    "✔️ Slutförande Status",
                    "📉 Historisk Data",
                    "🦺 Riskbedömning",
                    "👷 Riskanalys",
                    "🛑 Inget Ännu"])

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

            with completion_status:
                completion_figures = create_completion_analysis(st.session_state.df)
                for fig in completion_figures:
                    st.plotly_chart(fig, use_container_width=True)

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
                from Risk_Assessment import create_risk_analysis

                create_risk_analysis(st.session_state.risks)

        with main_tab3:
            bug_tracking_tab()

        # Only show admin panel if user is admin
        if st.session_state.user_role == 'admin':
            with main_tab4:
                admin_panel()

    st.divider()

    col1, col2 = st.columns([2, 1])
    with col2:
        st.info(f"//// By: {author}  -  st Version: {st.__version__} - "
                f"Python Version: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} ////")
        st.write("GitHub: --->https://github.com/brektzar/PlannerTool/tree/master<---")

    with st.expander("ℹ️ Snabbguide"):
        st.markdown("""
        ### Kom igång snabbt:
        1. 🎯 **Skapa ett mål** i 'Lägg till Mål'-fliken
        2. ✅ **Lägg till uppgifter** under 'Lägg till Uppgift'
        3. 🦺 **Riskbedöm** i 'Riskbedömning'-fliken
        4. 📊 **Visa analyser** i 'Översikt'-fliken
        """)

def main():
    """Main entry point of the application"""

    # Add custom styling
    st.markdown("""
    <style>
        /* Your existing styles */
    </style>
    """, unsafe_allow_html=True)

    # Show only login page if not authenticated
    if not st.session_state.authenticated:
        show_login_page()
        return

    # Show main application if authenticated
    main_app()

if __name__ == "__main__":
    main()
