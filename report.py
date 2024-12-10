import streamlit as st
import pandas as pd
import plotly.express as px


def error_handling_csv():
    try:
        # Läs in CSV-filerna
        df_categories = pd.read_csv("data_categories.csv")
        df_planering = pd.read_csv("Planering.csv")
        return df_categories, df_planering

    except FileNotFoundError:
        st.info("Filen 'Planering.csv' hittades inte. Skapa ett nytt mål.")

    except pd.errors.EmptyDataError:
        st.info("Filen 'Planering.csv' är tom. Lägg till ett nytt mål.")

    except Exception as re:
        st.error(f"Ett oväntat fel uppstod: {re}")


def goals_schema():
    goals = []

    # Läs in CSV-filen (byt ut filvägen till din fil)
    # Läs in data från CSV-filen och visa den i en tabell
    unused, data = error_handling_csv()

    if data.empty:
        st.info("Ingen data finns ännu. Lägg till ett nytt mål.")
    else:
        for index, row in data.iterrows():
            if pd.notna(row['Övergripande Mål']) and pd.notna(row['Startdatum']) and pd.notna(row['Slutdatum']):
                goals.append({
                    'Goal': row['Övergripande Mål'],
                    'Start': row['Startdatum'],
                    'Finish': row['Slutdatum']
                })

        # Skapa DataFrame för Mål
        goals_df = pd.DataFrame(goals)

        # Konvertera Startdatum och Slutdatum till datetime-format
        goals_df['Start'] = pd.to_datetime(goals_df['Start'])
        goals_df['Finish'] = pd.to_datetime(goals_df['Finish'])

        # Skapa Gantt-diagrammet med Plotly Express
        fig = px.timeline(goals_df,
                          x_start="Start",
                          x_end="Finish",
                          y="Goal",
                          title="Gantt Schema för Övergripande Mål",
                          labels={"Goal": "Mål"})
        fig.update_layout(showlegend=True)

        # Visa diagrammet i Streamlit
        st.plotly_chart(fig, key='goals_report1')


def tasks_schema():
    # Filtrera ut data för uppgifter, mål, startdatum och slutdatum
    tasks = []

    unused, data = error_handling_csv()
    if data.empty:
        st.info("Ingen data finns ännu. Lägg till ett nytt mål.")
    else:
        for index, row in data.iterrows():
            if pd.notna(row['Mål']) and pd.notna(row['Uppgift']) and pd.notna(row['Uppgiftsstart']) and pd.notna(
                    row['Uppgiftsslut']):
                tasks.append({
                    'Goal': row['Mål'],
                    'Task': row['Uppgift'],
                    'Start': row['Uppgiftsstart'],
                    'Finish': row['Uppgiftsslut']
                })

        # Skapa DataFrame för uppgifter
        tasks_df = pd.DataFrame(tasks)

        # Konvertera Startdatum och Slutdatum till datetime-format
        tasks_df['Start'] = pd.to_datetime(tasks_df['Start'])
        tasks_df['Finish'] = pd.to_datetime(tasks_df['Finish'])

        # Skapa en Streamlit layout för varje mål
        goals = tasks_df['Goal'].unique()

        # Skapa ett Gantt-diagram per mål
        for goal in goals:
            st.subheader(f'Schema för {goal}')  # Skapar en rubrik för varje mål
            goal_tasks = tasks_df[tasks_df['Goal'] == goal]

            # Skapa Gantt-diagrammet för uppgifterna inom målet
            fig = px.timeline(goal_tasks,
                              x_start="Start",
                              x_end="Finish",
                              y="Task",
                              title=f"Gantt Schema för {goal}",
                              labels={"Task": "Uppgift"})
            fig.update_layout(showlegend=True)

            # Visa diagrammet i Streamlit
            st.plotly_chart(fig, key= f'tasks_report{goal}')


def tools_report():
    st.title("Verktyg")
    # Läs in data från CSV

    unused, data = error_handling_csv()
    if data.empty:
        st.info("Ingen data finns ännu. Lägg till ett nytt mål.")
    else:
        # Filtrera och extrahera verktygen från kolumnen "Tekniska behov"
        tools = data['Tekniska behov'].dropna().str.split(',', expand=True).stack()

        # Skapa en frekvenstabell för verktygen
        tools_freq = tools.value_counts().reset_index()
        tools_freq.columns = ['Tool', 'Frequency']

        # Skapa en graf för att visa de vanligaste verktygen
        fig = px.bar(tools_freq, x='Tool', y='Frequency', title='Vanligaste Verktygen',
                     labels={'Tool': 'Verktyg', 'Frequency': 'Antal Användningar'})
        fig.update_layout(showlegend=False)

        # Visa grafen i Streamlit
        st.plotly_chart(fig, key='tools_report1')


def tools_per_categories_report():
    # Läs in CSV-filen
    df, unused = error_handling_csv()

    # Smält data och ta bort dubletter
    df = df.melt(var_name='Kategori', value_name='Verktyg')
    df = df.dropna(subset=['Verktyg'])  # Ta bort rader där "Verktyg" är NaN
    df = df.drop_duplicates()

    # Räkna antal verktyg per kategori
    verktyg_per_kategori = df.groupby('Kategori')['Verktyg'].count().reset_index()

    # Skapa stapeldiagram
    fig = px.bar(verktyg_per_kategori, x='Kategori', y='Verktyg',
                 labels={'Kategori': 'Kategori', 'Verktyg': 'Antal verktyg'},
                 title='Antal unika verktyg per kategori')

    # Visa grafen i Streamlit
    st.plotly_chart(fig, key='tools_per_categories_report1')


def tools_categories_used_report():
    item_list = []
    # Läs in data från Planering.csv och data_categories.csv
    df_categories, df_planering = error_handling_csv()

    # Dela upp värdena i "Tekniska behov" baserat på kommatecken och skapa en ny DataFrame
    df_tekniska_behov = df_planering['Tekniska behov'].str.split(', ', expand=True).stack().reset_index(level=1,
                                                                                                        drop=True).to_frame()
    df_tekniska_behov.columns = ['Tekniskt behov']

    # Skapa en dictionary för att mappa tekniska behov till deras kategorier
    category_mapping = {}
    for col in df_categories.columns:
        for value in df_categories[col].dropna():
            category_mapping[value] = col

    # Mappa varje tekniskt behov till en kategori
    df_tekniska_behov['Kategori'] = df_tekniska_behov['Tekniskt behov'].map(category_mapping)

    # Räkna antalet förekomster för varje kategori
    category_counts = df_tekniska_behov['Kategori'].value_counts().reset_index()
    category_counts.columns = ['Kategori', 'Antal användningar']

    # Skapa grafen med plotly
    fig = px.bar(category_counts, x='Kategori', y='Antal användningar',
                 title="Antal användningar per kategori",
                 labels={'Kategori': 'Kategori', 'Antal användningar': 'Antal användningar'},
                 color='Kategori', color_discrete_sequence=px.colors.qualitative.Set2)

    # Visa grafen i Streamlit
    st.plotly_chart(fig, key= 'tools_categories_used_report1')


def rental_costs():
    # Läs in CSV-filen
    df_categories, df_planering = error_handling_csv()

    # Räkna ut hyreskostnader
    total_cost = 0
    for index, row in df_planering.iterrows():
        if pd.notna(row['Total hyreskostnad']):
            total_cost += row['Total hyreskostnad']
    # Skriv ut totala hyreskostnader
    st.write(f"Totala hyreskostnader: {total_cost} kr")

    total_rental_days = 0
    for index, row in df_planering.iterrows():
        if (row['Hyrestyp']) == "Dygn":
            total_rental_days += row['Antal Dygn/Timmar']
    st.write(f"Antal Hyresdygn: {total_rental_days}")

    total_rental_hours = 0
    for index, row in df_planering.iterrows():
        if (row['Hyrestyp']) == "Timmar":
            total_rental_hours += row['Antal Dygn/Timmar']
    st.write(f"Antal Hyrestimmar: {total_rental_hours}")

    for index, row in df_planering.iterrows():
        if pd.notna(row['Hyra']):
            total_rental_hours += row['Antal Dygn/Timmar']


def time_statistics():
    """Analyze time-related statistics for tasks and goals"""
    st.subheader("Tidsstatistik")
    
    unused, df = error_handling_csv()
    if df.empty:
        st.info("Ingen data finns ännu. Lägg till ett nytt mål.")
        return
        
    # Convert dates to datetime
    df['Uppgiftsstart'] = pd.to_datetime(df['Uppgiftsstart'])
    df['Uppgiftsslut'] = pd.to_datetime(df['Uppgiftsslut'])
    
    # Calculate duration for each task
    df['Duration'] = (df['Uppgiftsslut'] - df['Uppgiftsstart']).dt.days
    
    # Time statistics
    total_days = df['Duration'].sum()
    avg_task_duration = df['Duration'].mean()
    total_work_hours = df['Tidsåtgång'].sum()
    avg_work_hours = df['Tidsåtgång'].mean()
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Totalt antal projektdagar", f"{total_days:.0f}")
        st.metric("Genomsnittlig uppgiftslängd (dagar)", f"{avg_task_duration:.1f}")
    with col2:
        st.metric("Totalt antal arbetstimmar", f"{total_work_hours:.1f}")
        st.metric("Genomsnittliga arbetstimmar per uppgift", f"{avg_work_hours:.1f}")


def cost_analysis():
    """Analyze cost-related statistics"""
    st.subheader("Kostnadsanalys")
    
    unused, df = error_handling_csv()
    if df.empty:
        st.info("Ingen data finns ännu. Lägg till ett nytt mål.")
        return
        
    # Calculate costs
    total_cost = df['Kostnad'].sum()
    total_rental = df['Total hyreskostnad'].sum()
    total_project_cost = total_cost + total_rental
    
    # Cost per goal - including both direct costs and rental costs
    cost_per_goal = df.groupby('Mål').agg({
        'Kostnad': 'sum',
        'Total hyreskostnad': 'sum'
    }).fillna(0)
    
    # Calculate total cost per goal
    cost_per_goal['Total kostnad'] = cost_per_goal['Kostnad'] + cost_per_goal['Total hyreskostnad']
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total projektkostnad", f"{total_project_cost:,.0f} kr")
        st.metric("Material/Arbetskostnad", f"{total_cost:,.0f} kr")
        st.metric("Total hyreskostnad", f"{total_rental:,.0f} kr")
    
    with col2:
        # Create pie chart for cost distribution
        fig = px.pie(
            values=[total_cost, total_rental],
            names=['Material/Arbete', 'Hyrkostnad'],
            title='Kostnadsfördelning'
        )
        st.plotly_chart(fig, key='cost_analysis1')
    
    # Bar chart for cost per goal with stacked costs
    fig = px.bar(
        cost_per_goal,
        x=cost_per_goal.index,
        y=['Kostnad', 'Total hyreskostnad'],
        title='Kostnad per mål',
        labels={
            'value': 'Kostnad (kr)',
            'variable': 'Kostnadstyp',
            'index': 'Mål'
        },
        barmode='stack'
    )
    
    # Update the legend labels
    fig.update_layout(
        legend_title_text='Kostnadstyp',
        showlegend=True
    )
    
    # Rename the legend items
    newnames = {'Kostnad': 'Material/Arbete', 'Total hyreskostnad': 'Hyrkostnad'}
    fig.for_each_trace(lambda t: t.update(name = newnames[t.name]))
    
    # Add value labels on the bars
    fig.update_traces(texttemplate='%{y:,.0f} kr', textposition='inside')
    
    st.plotly_chart(fig, key='cost_analysis2')
    
    # Display detailed cost breakdown table
    st.subheader("Detaljerad kostnadsfördelning per mål")
    formatted_costs = cost_per_goal.copy()
    for col in formatted_costs.columns:
        formatted_costs[col] = formatted_costs[col].apply(lambda x: f"{x:,.0f} kr")
    st.dataframe(formatted_costs)


def resource_utilization():
    # Analysera resursanvändning
    st.subheader("Resursanvändning")
    
    unused, df = error_handling_csv()
    if df.empty:
        st.info("Ingen data finns ännu. Lägg till ett nytt mål.")
        return
    
    # Personalstatistik
    total_personnel_hours = (df['Personalantal'] * df['Tidsåtgång']).sum()
    avg_personnel_per_task = df['Personalantal'].mean()
    
    # Verktygsanvändning över tid
    tools_df = df['Tekniska behov'].str.split(',', expand=True).stack()
    tools_df = tools_df.str.strip()
    tool_usage = tools_df.value_counts()
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Totalt antal personaltimmar", f"{total_personnel_hours:,.0f}")
        st.metric("Genomsnittlig personal per uppgift", f"{avg_personnel_per_task:.1f}")

    # Filtrera bort rader utan uppgifter och datum
    df_tasks = df[df['Uppgift'].notna()].copy()
    df_tasks = df_tasks.dropna(subset=['Uppgiftsstart', 'Uppgiftsslut', 'Personalantal'])

    if not df_tasks.empty:
        # Konvertera datum till datetime-format
        df_tasks['Uppgiftsstart'] = pd.to_datetime(df_tasks['Uppgiftsstart'])
        df_tasks['Uppgiftsslut'] = pd.to_datetime(df_tasks['Uppgiftsslut'])
        
        start_date = df_tasks['Uppgiftsstart'].min()
        end_date = df_tasks['Uppgiftsslut'].max()
        
        if pd.notna(start_date) and pd.notna(end_date):
            date_range = pd.date_range(start_date, end_date)
            
            # Beräkna personal per dag
            daily_personnel = pd.DataFrame(index=date_range, columns=['Personal'])
            daily_personnel['Personal'] = 0
            
            # För varje uppgift, lägg till personal för alla dagar mellan start och slut
            for _, task in df_tasks.iterrows():
                if pd.notna(task['Uppgiftsstart']) and pd.notna(task['Uppgiftsslut']):
                    task_dates = pd.date_range(task['Uppgiftsstart'], task['Uppgiftsslut'])
                    daily_personnel.loc[task_dates, 'Personal'] += task['Personalantal']
            
            # Skapa tidslinjediagram
            fig = px.line(
                daily_personnel,
                x=daily_personnel.index,
                y='Personal',
                title='Personalbehov över tid',
                labels={
                    'Personal': 'Antal personal',
                    'index': 'Datum'
                }
            )
            
            # Lägg till markörer på linjen
            fig.update_traces(mode='lines+markers')
            
            # Uppdatera layout för bättre läsbarhet
            fig.update_layout(
                xaxis_title="Datum",
                yaxis_title="Antal personal",
                hovermode='x'
            )
            
            # Lägg till rangeslider
            fig.update_xaxes(rangeslider_visible=True)
            
            # Visa maximalt personalbehov
            max_personnel = daily_personnel['Personal'].max()
            st.metric("Maximalt personalbehov per dag", f"{max_personnel:.0f} personer")
            
            # Visa tidslinjen
            st.plotly_chart(fig, key='resource_utilization2')

            # Alternativ för att visa detaljerad daglig data
            if st.checkbox("Visa detaljerad personaldata per dag", key="details"):
                daily_personnel['Personal'] = daily_personnel['Personal'].astype(int)
                daily_personnel.index = daily_personnel.index.strftime('%Y-%m-%d')

                # Beräkna hur många rader som ska vara i varje kolumn
                total_rows = len(daily_personnel)
                rows_per_column = total_rows // 3 + (1 if total_rows % 3 else 0)

                # Skapa tre kolumner
                col1, col2, col3, col4, col5, col6, col7, col8 = st.columns([1, 1, 1, 1, 1, 1, 1, 1])

                with col1:
                    st.dataframe(daily_personnel.iloc[:rows_per_column])
                with col2:
                    st.dataframe(daily_personnel.iloc[rows_per_column:2 * rows_per_column])
                with col3:
                    st.dataframe(daily_personnel.iloc[2 * rows_per_column:])
        else:
            st.warning("Kunde inte skapa tidslinje: Ogiltiga datum hittades i data.")
    else:
        st.warning("Kunde inte skapa tidslinje: Inga uppgifter med kompletta datum hittades.")


def project_overview():
    """Display overall project statistics and interactive goal/task details"""
    st.title("Projektöversikt")
    
    unused, df = error_handling_csv()
    if df.empty:
        st.info("Ingen data finns ännu. Lägg till ett nytt mål.")
        return
    
    # Basic project metrics
    total_goals = df['Övergripande Mål'].nunique()
    total_tasks = df['Uppgift'].count()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Antal mål", total_goals)
    with col2:
        st.metric("Antal uppgifter", total_tasks)
    with col3:
        st.metric("Uppgifter per mål", f"{total_tasks/total_goals:.1f}")

    st.divider()
    
    # Interactive goal and task view
    st.subheader("Mål och Uppgifter")
    
    # Group data by goals
    goals = df['Övergripande Mål'].dropna().unique()
    
    for goal in goals:
        goal_data = df[df['Övergripande Mål'] == goal]
        goal_desc = goal_data['Beskrivning'].iloc[0]
        
        with st.expander(f"🎯 {goal}"):
            # Goal details
            st.write(f"**Beskrivning:** {goal_desc}")
            st.write(f"**Period:** {goal_data['Startdatum'].iloc[0]} till {goal_data['Slutdatum'].iloc[0]}")
            
            # Tasks for this goal
            tasks = df[df['Mål'] == goal]
            if not tasks.empty:
                st.write("**Uppgifter:**")
                for _, task in tasks.iterrows():
                    if st.checkbox(f"📋 {task['Uppgift']}", key=f"task_{goal}_{task['Uppgift']}"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Beskrivning:** {task['Beskrivning']}")
                            st.write(f"**Period:** {task['Uppgiftsstart']} till {task['Uppgiftsslut']}")
                            st.write(f"**Tidsåtgång:** {task['Tidsåtgång']} timmar")
                            st.write(f"**Personal:** {task['Personalantal']} personer")
                        with col2:
                            st.write(f"**Kostnad:** {task['Kostnad']:,.0f} kr")
                            st.write(f"**Tekniska behov:** {task['Tekniska behov']}")
                            if pd.notna(task['Hyra']):
                                st.write(f"**Hyra:** {task['Hyra']}")
                                st.write(f"**Hyreskostnad:** {task['Total hyreskostnad']:,.0f} kr")
                            if pd.notna(task['Andra behov']):
                                st.write(f"**Andra behov:** {task['Andra behov']}")
                
                # Task statistics for this goal
                st.divider()
                task_stats_col1, task_stats_col2 = st.columns(2)
                with task_stats_col1:
                    total_task_hours = tasks['Tidsåtgång'].sum()
                    total_task_cost = tasks['Kostnad'].sum()
                    total_task_rental = tasks['Total hyreskostnad'].sum()
                    total_goal_cost = total_task_cost + total_task_rental
                    st.metric("Total tidsåtgång", f"{total_task_hours:.1f} timmar")
                    st.metric("Total kostnad", f"{total_goal_cost:,.0f} kr")
                with task_stats_col2:
                    total_personnel = tasks['Personalantal'].sum()
                    avg_duration = (pd.to_datetime(tasks['Uppgiftsslut']) -
                                    pd.to_datetime(tasks['Uppgiftsstart'])).mean().days
                    st.metric("Total personal", total_personnel)
                    st.metric("Genomsnittlig uppgiftslängd", f"{avg_duration:.1f} dagar")
            else:
                st.info("Inga uppgifter har lagts till för detta mål ännu.")
