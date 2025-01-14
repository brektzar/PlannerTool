import streamlit as st
import pandas as pd
from Data import validate_dates, convert_rental_info, WEATHER_CONDITIONS
from datetime import datetime
from database import get_database
from custom_logging import log_action

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
# 🎉 : Alla uppgifter klara
# 💡 : Tips
# ⌚ : Arbetstid
# 🐛 : Rapportera Buggar
# 🛑 : Inget Ännu


def add_goal(dataframe, goal_name, goal_description, goal_dates):
    """
    Lägger till ett nytt mål i databasen.
    Kontrollerar att målnamnet är unikt och att alla nödvändiga fält är ifyllda.
    """
    if not goal_name:
        st.error("Målnamn krävs!")
        return dataframe, False

    if goal_name in dataframe[dataframe['Type'] == 'Goal']['Goal_Name'].values:
        st.error("Ett mål med detta namn finns redan!")
        return dataframe, False

    new_goal = pd.DataFrame({
        'Type': ['Goal'],
        'Goal_Name': [goal_name],
        'Goal_Description': [goal_description if goal_description else "No data"],
        'Goal_Start_Date': [goal_dates[0]],
        'Goal_End_Date': [goal_dates[1]],
        'Goal_Completed': [False],
        'Task_Name': [""],
        'Task_Description': [""],
        'Task_Start_Date': [None],
        'Task_End_Date': [None],
        'Task_Estimated_Time': [0],
        'Task_Estimated_Cost': [0],
        'Task_Technical_Needs': ["No data"],
        'Task_Weather_Conditions': ["No data"],
        'Task_Needs_Rental': [False],
        'Task_Rental_Item': ["No data"],
        'Task_Rental_Type': ["No data"],
        'Task_Rental_Duration': [0],
        'Task_Rental_Cost_Per_Unit': [0],
        'Task_Total_Rental_Cost': [0],
        'Task_Personnel_Count': [0],
        'Task_Other_Needs': ["No data"]
    })

    return pd.concat([dataframe, new_goal], ignore_index=True), True


def add_task(dataframe, goal_name, task_data):
    """
    Lägger till en ny uppgift kopplad till ett specifikt mål.
    Kontrollerar att uppgiftsnamnet är unikt inom målet och att alla nödvändiga fält är ifyllda.
    Hanterar även automatisk uppdatering av målstatus om målet tidigare var markerat som klart.
    """
    if not task_data['name']:
        st.error("Uppgiftsnamn krävs!")
        return dataframe, False

    # Check if goal exists and is completed
    goal_mask = (dataframe['Type'] == 'Goal') & (dataframe['Goal_Name'] == goal_name)
    if goal_mask.any() and dataframe.loc[goal_mask, 'Goal_Completed'].iloc[0]:
        # Uncomplete the goal when adding new task
        dataframe.loc[goal_mask, 'Goal_Completed'] = False

    goal_row = dataframe[
        (dataframe['Type'] == 'Goal') &
        (dataframe['Goal_Name'] == goal_name)
        ].iloc[0]

    existing_tasks = dataframe[
        (dataframe['Type'] == 'Task') &
        (dataframe['Goal_Name'] == goal_name)
        ]

    if task_data['name'] in existing_tasks['Task_Name'].values:
        st.error("En uppgift med detta namn finns redan för detta mål!")
        return dataframe, False

    rental_info = convert_rental_info(
        task_data['rental_item'],
        task_data['rental_duration'],
        task_data['rental_cost_unit']
    )

    # Modify the tech_needs handling
    if not task_data['tech_needs']:  # If tech_needs is empty
        tech_needs_str = "Inget - Inga Redskap Behövs"
    else:
        # Filter out "Inget - Inga Redskap Behövs" if it exists when other tools are selected
        tech_needs = [need for need in task_data['tech_needs'] if need != "Inget - Inga Redskap Behövs"]
        tech_needs_str = ','.join(tech_needs)

    new_task = pd.DataFrame({
        'Type': ['Task'],
        'Goal_Name': [goal_name],
        'Goal_Description': [goal_row['Goal_Description']],
        'Goal_Start_Date': [goal_row['Goal_Start_Date']],
        'Goal_End_Date': [goal_row['Goal_End_Date']],
        'Task_Name': [task_data['name']],
        'Task_Description': [task_data['description'] if task_data['description'] else "No data"],
        'Task_Start_Date': [task_data['dates'][0]],
        'Task_End_Date': [task_data['dates'][1]],
        'Task_Estimated_Time': [task_data['est_time']],
        'Task_Estimated_Cost': [task_data['est_cost']],
        'Task_Technical_Needs': [tech_needs_str],
        'Task_Weather_Conditions': [','.join(task_data['weather']) if task_data['weather'] else "No data"],
        'Task_Needs_Rental': [rental_info['needs_rental']],
        'Task_Rental_Item': [rental_info['rental_item']],
        'Task_Rental_Type': [task_data['rental_type']],
        'Task_Rental_Duration': [rental_info['rental_duration']],
        'Task_Rental_Cost_Per_Unit': [rental_info['rental_cost_unit']],
        'Task_Total_Rental_Cost': [rental_info['total_rental_cost']],
        'Task_Personnel_Count': [task_data['personnel']],
        'Task_Other_Needs': [task_data['other_needs'] if task_data['other_needs'] else "No data"],
        'Task_Completed': [False],
    })

    return pd.concat([dataframe, new_task], ignore_index=True), True


def update_dataframe(df, edited_data):
    """
    Uppdaterar befintliga mål och uppgifter i databasen baserat på användarens ändringar.
    Hanterar olika datatyper och säkerställer att data sparas i rätt format.
    """
    for key, data in edited_data.items():
        if key.startswith('goal_'):
            goal_name = key.replace('goal_', '')
            mask = (df['Type'] == 'Goal') & (df['Goal_Name'] == goal_name)

            if 'name' in data:
                df.loc[mask, 'Goal_Name'] = data['name']
            if 'description' in data:
                df.loc[mask, 'Goal_Description'] = data['description']
            if 'dates' in data:
                # Handle both tuple and list date formats
                dates = data['dates']
                if isinstance(dates, (tuple, list)) and len(dates) >= 2:
                    df.loc[mask, 'Goal_Start_Date'] = dates[0]
                    df.loc[mask, 'Goal_End_Date'] = dates[1]
                else:
                    # Handle single date or invalid date format
                    df.loc[mask, 'Goal_Start_Date'] = dates
                    df.loc[mask, 'Goal_End_Date'] = dates

        elif key.startswith('task_'):
            # Extract goal name and task name from the key
            _, goal_name, task_name = key.split('_', 2)
            mask = (df['Type'] == 'Task') & (df['Goal_Name'] == goal_name) & (df['Task_Name'] == task_name)

            # Update task fields
            for field, value in data.items():
                if field == 'name':
                    df.loc[mask, 'Task_Name'] = value
                elif field == 'description':
                    df.loc[mask, 'Task_Description'] = value
                elif field == 'dates':
                    if isinstance(value, (tuple, list)) and len(value) >= 2:
                        df.loc[mask, 'Task_Start_Date'] = value[0]
                        df.loc[mask, 'Task_End_Date'] = value[1]
                elif field == 'est_time':
                    df.loc[mask, 'Task_Estimated_Time'] = value
                elif field == 'est_cost':
                    df.loc[mask, 'Task_Estimated_Cost'] = value
                elif field == 'tech_needs':
                    if not value:  # If tech_needs is empty
                        df.loc[mask, 'Task_Technical_Needs'] = "Inget - Inga Redskap Behövs"
                    else:
                        # Filter out "Inget - Inga Redskap Behövs" if it exists when other tools are selected
                        tech_needs = [need for need in value if need != "Inget - Inga Redskap Behövs"]
                        df.loc[mask, 'Task_Technical_Needs'] = ','.join(tech_needs)
                elif field == 'weather':
                    df.loc[mask, 'Task_Weather_Conditions'] = ','.join(value) if value else "No data"
                elif field == 'personnel':
                    df.loc[mask, 'Task_Personnel_Count'] = value
                elif field == 'rental_item':
                    df.loc[mask, 'Task_Rental_Item'] = value if value else "No data"
                    df.loc[mask, 'Task_Needs_Rental'] = bool(value and value != "No data")
                elif field == 'rental_type':
                    df.loc[mask, 'Task_Rental_Type'] = value
                elif field == 'rental_duration':
                    df.loc[mask, 'Task_Rental_Duration'] = value
                elif field == 'rental_cost_unit':
                    df.loc[mask, 'Task_Rental_Cost_Per_Unit'] = value
                elif field == 'total_rental_cost':
                    df.loc[mask, 'Task_Total_Rental_Cost'] = value
                elif field == 'other_needs':
                    df.loc[mask, 'Task_Other_Needs'] = value if value else "No data"

    return df


def toggle_task_completion(dataframe, goal_name, task_name):
    """
    Växlar en uppgifts slutförandestatus mellan klar och ej klar.
    Används när användaren markerar eller avmarkerar en uppgift som slutförd.
    """
    mask = (dataframe['Type'] == 'Task') & (dataframe['Goal_Name'] == goal_name) & (dataframe['Task_Name'] == task_name)
    if mask.any():
        dataframe.loc[mask, 'Task_Completed'] = ~dataframe.loc[mask, 'Task_Completed'].iloc[0]
    return dataframe


def toggle_goal_completion(dataframe, goal_name):
    """
    Uppdaterar ett måls slutförandestatus baserat på dess uppgifter.
    Ett mål markeras automatiskt som klart när alla dess uppgifter är slutförda,
    och som ej klart när någon uppgift är oavslutad.
    """
    # Get all tasks for this goal
    tasks = dataframe[(dataframe['Type'] == 'Task') & (dataframe['Goal_Name'] == goal_name)]

    # Calculate if all tasks are completed
    all_tasks_completed = all(tasks['Task_Completed']) if not tasks.empty else False

    # Find the goal
    mask = (dataframe['Type'] == 'Goal') & (dataframe['Goal_Name'] == goal_name)
    if mask.any():
        # Set goal completion status based on tasks
        dataframe.loc[mask, 'Goal_Completed'] = all_tasks_completed
        return dataframe, True, "Goal completion status updated"

    return dataframe, False, "Goal not found"

def load_bugs():
    try:
        db = get_database()
        bugs = list(db.bugs.find({}, {'_id': 0}))
        if not bugs:
            return pd.DataFrame(columns=['bug_title','description', 'location', 'date_reported', 'status'])
        return pd.DataFrame(bugs)
    except Exception as e:
        print(f"Error loading bugs from MongoDB: {e}")
        return pd.DataFrame(columns=['bug_title','description', 'location', 'date_reported', 'status'])

def save_bugs(bugs_df):
    try:
        db = get_database()
        # Convert DataFrame to records
        records = bugs_df.to_dict('records')
        
        # Clear existing bugs and insert new ones
        db.bugs.delete_many({})
        if records:
            db.bugs.insert_many(records)
    except Exception as e:
        print(f"Error saving bugs to MongoDB: {e}")

def get_all_locations():
    return [
        "Lägg till Mål",
        "Lägg till Uppgift",
        "Riskbedömning",
        "Översikt",
        "Hantera Tekniska Behov",
        " Buggar",
        "Gantt Schema",
        "Kostnadsanalys",
        "Arbetstid",
        "Tekniska Behov",
        "Slutförande Status",
        "Historisk Data",
        "Riskbedömning",
        "Riskanalys"
    ]


def bug_tracking_tab():
    st.subheader("🐛 Rapportera Buggar")

    st.warning("Var tydlig med hur felet artar sig, går det att reproducera? \n\n "
               "Om du får ett felmeddelande, skriv in hela meddelandet i fältet med din beskrivning.")

    # Load existing bugs
    bugs_df = load_bugs()
    for idx, bug in bugs_df.iterrows():
        if bug['bug_title'] == "":
            bug['bug_title'] = "No Title"
        else:
            pass

    # Create two columns for the layout
    col1, col2 = st.columns([2, 1])

    with col1:
        # Bug reporting form
        with st.form("bug_report_form"):
            bug_title = st.text_input("Titel", max_chars=50)
            description = st.text_area("Beskrivning av buggen", height=100)
            location = st.selectbox("Var finns buggen?", options=get_all_locations())
            submit_bug = st.form_submit_button("Rapportera Bug")

            if submit_bug and description:
                new_bug = pd.DataFrame({
                    'bug_title': [bug_title],
                    'description': [description],
                    'location': [location],
                    'date_reported': [datetime.now().strftime("%Y-%m-%d")],
                    'status': ['Ej Fixad']
                })

                bugs_df = pd.concat([bugs_df, new_bug], ignore_index=True)
                log_action("Bug Rapporterad", f"Buggen '{bug_title}' rapporterades av {st.session_state.username}", location)
                save_bugs(bugs_df)
                
                st.success("Bug rapporterad!")
                st.rerun()
    
    with col2:
        st.write("### Statistik")
        if not bugs_df.empty:
            total_bugs = len(bugs_df)
            fixed_bugs = len(bugs_df[bugs_df['status'] == 'Fixad'])
            st.metric("Totalt antal buggar", total_bugs)
            st.metric("Fixade buggar", fixed_bugs)
            st.metric("Aktiva buggar", total_bugs - fixed_bugs)
    
    # Display existing bugs
    st.subheader("Rapporterade Buggar")
    if not bugs_df.empty:
        for idx, bug in bugs_df.iterrows():
            
            # Select the icon based on the bug status
            icon = "✔️" if bug['status'] == 'Fixad' else "❌"
            
            with st.expander(f"{icon} {bug['bug_title']} - rapporterad i {bug['location']} - {bug['date_reported']}"):
                st.write(f"**Beskrivning:** {bug['description']}")
                st.write(f"**Status:** {bug['status']}")
                
                # Toggle bug status
                current_status = bug['status']
                new_status = st.toggle(
                    "Markera som fixad",
                    value=current_status == 'Fixad',
                    key=f"bug_{idx}"
                )
                
                if new_status != (current_status == 'Fixad'):
                    bugs_df.at[idx, 'status'] = 'Fixad' if new_status else 'Ej Fixad'
                    if bug['status'] == 'Fixad':
                        log_action("Bug åter ej fixad!", f"Buggen '{bug['bug_title']}' ändrades av {st.session_state.username}", location)
                    else:
                        log_action("Bug Fixad", f"Buggen '{bug['bug_title']}' fixades av {st.session_state.username}", location)
                    save_bugs(bugs_df)
                    st.rerun()
    else:
        st.info("Inga buggar rapporterade ännu.")
