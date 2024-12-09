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
        st.plotly_chart(fig)


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
            st.plotly_chart(fig)


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
        st.plotly_chart(fig)


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
    st.plotly_chart(fig)


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
    st.plotly_chart(fig)

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

