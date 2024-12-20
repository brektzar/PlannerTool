import streamlit as streamlit
import pandas as pd
from Data import validate_dates, convert_rental_info, WEATHER_CONDITIONS


def add_goal(dataframe, goal_name, goal_description, goal_dates):
    if not goal_name:
        streamlit.error("Målnamn krävs!")
        return dataframe, False

    if goal_name in dataframe[dataframe['Type'] == 'Goal']['Goal_Name'].values:
        streamlit.error("Ett mål med detta namn finns redan!")
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
    if not task_data['name']:
        streamlit.error("Uppgiftsnamn krävs!")
        return dataframe, False

    goal_row = dataframe[
        (dataframe['Type'] == 'Goal') &
        (dataframe['Goal_Name'] == goal_name)
        ].iloc[0]

    existing_tasks = dataframe[
        (dataframe['Type'] == 'Task') &
        (dataframe['Goal_Name'] == goal_name)
        ]

    if task_data['name'] in existing_tasks['Task_Name'].values:
        streamlit.error("En uppgift med detta namn finns redan för detta mål!")
        return dataframe, False

    rental_info = convert_rental_info(
        task_data['rental_item'],
        task_data['rental_duration'],
        task_data['rental_cost_unit']
    )

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
        'Task_Technical_Needs': [','.join(task_data['tech_needs']) if task_data['tech_needs'] else "No data"],
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


def update_dataframe(dataframe, edited_data):
    dataframe_copy = dataframe.copy()

    for key, value in edited_data.items():
        if key.startswith('goal_'):
            goal_name = key.replace('goal_', '')
            mask = (dataframe_copy['Type'] == 'Goal') & (dataframe_copy['Goal_Name'] == goal_name)
            if mask.any():
                dataframe_copy.loc[mask, 'Goal_Name'] = value['name']
                dataframe_copy.loc[mask, 'Goal_Description'] = value['description']
                dataframe_copy.loc[mask, 'Goal_Start_Date'] = value['dates'][0]
                dataframe_copy.loc[mask, 'Goal_End_Date'] = value['dates'][1]

                if value['name'] != goal_name:
                    task_mask = (dataframe_copy['Type'] == 'Task') & (dataframe_copy['Goal_Name'] == goal_name)
                    dataframe_copy.loc[task_mask, 'Goal_Name'] = value['name']

        elif key.startswith('task_'):
            _, goal_name, task_name = key.split('_', 2)
            mask = (dataframe_copy['Type'] == 'Task') & (dataframe_copy['Goal_Name'] == goal_name) & (
                        dataframe_copy['Task_Name'] == task_name)
            if mask.any():
                for field, new_value in value.items():
                    if field in dataframe_copy.columns:
                        dataframe_copy.loc[mask, field] = new_value

    return dataframe_copy


def toggle_task_completion(dataframe, goal_name, task_name):
    mask = (dataframe['Type'] == 'Task') & (dataframe['Goal_Name'] == goal_name) & (dataframe['Task_Name'] == task_name)
    if mask.any():
        dataframe.loc[mask, 'Task_Completed'] = ~dataframe.loc[mask, 'Task_Completed'].iloc[0]
    return dataframe


def toggle_goal_completion(dataframe, goal_name):
    # Check if all tasks are completed
    tasks = dataframe[(dataframe['Type'] == 'Task') & (dataframe['Goal_Name'] == goal_name)]
    if not tasks.empty and not all(tasks['Task_Completed']):
        return dataframe, False, "All tasks must be completed before completing the goal"

    # Toggle goal completion
    mask = (dataframe['Type'] == 'Goal') & (dataframe['Goal_Name'] == goal_name)
    if mask.any():
        dataframe.loc[mask, 'Goal_Completed'] = ~dataframe.loc[mask, 'Goal_Completed'].iloc[0]
        return dataframe, True, "Goal completion status updated"

    return dataframe, False, "Goal not found"
