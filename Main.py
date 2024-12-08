import streamlit as st
import pandas as pd
import numpy as np
import os


def save_to_csv(datainput, name):
    datainput.to_csv(name, mode='a', header=not os.path.exists(name), index=False)


def clear_csv():
    try:
        os.remove("Planering.csv")
        st.success("Filen har rensats.")
    except FileNotFoundError:
        st.info("Filen fanns inte från början.")
    except Exception as ce:
        st.error(f"Ett fel uppstod vid rensning: {ce}")


def update_data(df_input, index_input, column_input, new_value):
    # Hämta den ursprungliga datatypen för kolumnen
    original_dtype = df_input[column_input].dtype

    # Försök konvertera det nya värdet till rätt datatyp
    try:
        if column == "Tekniska behov":
            if not new_value:
                new_value = ["Inget Verktyg Valt"]
            else:
                if not isinstance(new_value, list):
                    new_value = [new_value]
            df.loc[index, column] = ", ".join(new_value)

        if original_dtype == 'datetime64[ns]':
            new_value = pd.to_datetime(new_value)
        elif original_dtype == 'float64':
            new_value = float(new_value)
        elif original_dtype == 'int64':
            new_value = int(new_value)
        else:
            new_value = str(new_value)  # Konvertera till sträng som standard

        df.loc[index_input, column_input] = new_value
        df.to_csv("Planering.csv", index=False)
        st.success("Data uppdaterad!")
    except ValueError:
        st.error("Ogiltigt värde. Vänligen ange ett värde av rätt typ.")


tab_names = ["Målbeskrivning", "Planering", "Rapport", "Tekniska Behov - lista"]
tabs = st.tabs(tab_names)

with tabs[0]:
    with st.form(key="Målbeskrivning"):
        goal = st.text_input("Övergripande Mål")
        task_desc = st.text_input("Beskrivning")
        start_date = st.date_input("Startdatum")
        end_date = st.date_input("Slutdatum")
        submitted = st.form_submit_button("Submit")

    if submitted:
        if not goal or not task_desc or not start_date or not end_date:
            st.error("Alla fält måste fyllas i.")
        else:
            try:
                goal_data = pd.DataFrame(
                    {
                        "Övergripande Mål": [goal],
                        "Beskrivning": [task_desc],
                        "Startdatum": [start_date],
                        "Slutdatum": [end_date],
                    }
                )
                save_to_csv(goal_data, "Planering.csv")
                st.success("Målet har lagts till!")
                st.rerun()
            except Exception as ge:
                st.error(f"Ett fel uppstod: {ge}")

    # Läs in data från CSV-filen och visa den i en tabell
    try:
        df = pd.read_csv("Planering.csv")
        if df.empty:
            st.info("Ingen data finns ännu. Lägg till ett nytt mål.")
        else:
            st.dataframe(df)
    except FileNotFoundError:
        st.info("Filen 'Planering.csv' hittades inte. Skapa ett nytt mål.")

    except pd.errors.EmptyDataError:
        st.info("Filen 'Planering.csv' är tom. Lägg till ett nytt mål.")

    except Exception as re:
        st.error(f"Ett oväntat fel uppstod: {re}")

    # Knapp för att rensa filen
    if st.button("Rensa fil"):
        clear_csv()
        st.rerun()

with tabs[1]:
    st.header("Planera uppgifter för ett givet mål")
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Planering")
        # Läs in data från CSV-filen och visa den i en tabell
        try:
            df = pd.read_csv("Planering.csv")
            if df.empty:
                st.info("Ingen data finns ännu. Lägg till ett nytt mål.")
            else:
                goals = df['Övergripande Mål'].dropna().unique()
                selected_goal = st.selectbox("Välj mål", goals)

                with st.form("Lägg till uppgift"):

                    technical_needs_data = pd.read_csv("technical_needs.csv")

                    task = st.text_input("Uppgift")
                    task_desc = st.text_area("Beskrivning")
                    start_date = st.date_input("Startdatum")
                    end_date = st.date_input("Slutdatum")
                    estimated_time = st.number_input("Uppskattad tidsåtgång (timmar)", min_value=0.0)
                    estimated_cost = st.number_input("Uppskattad kostnad", min_value=0.0)

                    technical_needs = st.multiselect("Välj Verktyg/Redskap", technical_needs_data['Redskap'].tolist(),
                                                     default="Inget Verktyg Valt")
                    if not technical_needs:
                        technical_needs = ["Inget Verktyg Valt"]

                    with st.expander("Hyra?"):
                        rental = st.text_input("Vad ska hyras?")
                        rental_type = st.selectbox("Hyrestyp", ["Dygn", "Timme"])
                        rental_amount = st.number_input("Antal dygn/timmar", min_value=0.0)
                        rental_cost = st.number_input("Hyrkostnad per timme/dygn", min_value=0.0)
                        total_rental_cost = rental_amount * rental_cost

                    personnel = st.slider("Personalantal", 1, 10, 1)
                    other_needs = st.text_area("Andra behov")

                    submit_task = st.form_submit_button("Lägg till")

                    if submit_task:
                        if not technical_needs:
                            technical_needs = ["Inget Verktyg Valt"]
                            st.rerun()
                        # Spara uppgiften till CSV-filen
                        new_data = {
                            "Mål": selected_goal,
                            "Uppgift": task,
                            "Beskrivning": task_desc,
                            "Tidsåtgång": estimated_time,
                            "Kostnad": estimated_cost,
                            "Tekniska behov": ", ".join(technical_needs),
                            "Hyra": rental,
                            "Hyrestyp": rental_type,
                            "Antal Dygn/Timmar": rental_amount,
                            "Hyreskostnad": rental_cost,
                            "Total hyreskostnad": total_rental_cost,
                            "Personalantal": personnel,
                            "Andra behov": other_needs
                        }
                        df_new = pd.DataFrame(new_data, index=[0])
                        df = pd.read_csv("Planering.csv")
                        df = pd.concat([df, df_new], ignore_index=True)
                        df.to_csv("Planering.csv", index=False)
                        st.success("Uppgift tillagd!")
                        st.rerun()

        except FileNotFoundError:
            st.info("Filen 'Planering.csv' hittades inte. Skapa ett nytt mål.")

        except pd.errors.EmptyDataError:
            st.info("Filen 'Planering.csv' är tom. Lägg till ett nytt mål.")

        except Exception as re:
            st.error(f"Ett oväntat fel uppstod: {re}")

    with col2:
        st.write("Mål och Uppgifter")

        # Läs in data från uppgiftsfilen (justera filnamnet och kolumnerna efter behov)
        try:
            df_tasks = pd.read_csv("Planering.csv")

            # Gruppera uppgifter efter mål
            for goal, tasks_df in df_tasks.groupby('Mål'):
                with st.expander(goal):
                    for index, row in tasks_df.iterrows():
                        task_checked = st.checkbox(f"Uppgift: {row['Uppgift']}", key=f"task_{index}")
                        if task_checked:
                            for column, value in row.items():
                                # Exkludera dessa kolumner
                                if column not in ['Mål', 'Uppgift', 'Övergripande Mål', 'Startdatum', 'Slutdatum']:
                                    data_checked = st.checkbox(f"{column}: {value}", key=f"data_{index}_{column}")
                                    if data_checked:
                                        if column == "Tekniska behov":
                                            # Hämta nuvarande tekniska behov som en lista
                                            current_needs = df.loc[index, column].split(", ")
                                            new_value = st.multiselect("Välj Verktyg/Redskap",
                                                                       technical_needs_data['Redskap'].tolist(),
                                                                       default=current_needs)
                                        else:
                                            # För andra kolumner, använd samma logik som tidigare
                                            new_value = st.text_input(f"Nytt värde för {column}:", value=value)

                                        if st.button("Uppdatera"):
                                            if not technical_needs:
                                                technical_needs = ["Inget Verktyg Valt"]
                                                st.rerun()
                                            update_data(df_tasks, index, column, new_value)

        except FileNotFoundError:
            st.info("Fil med uppgifter hittades inte.")
        except Exception as we:
            st.error(f"Ett fel uppstod: {we} (Detta beror förmodligen på att målet saknar uppgifter.)")
        except pd.errors.EmptyDataError:
            st.info("Filen 'Planering.csv' är tom. Lägg till ett nytt mål.")

with tabs[2]:
    st.header("Rapport")

with (tabs[3]):
    st.header("Lista på redskap och verktyg")
    st.subheader("Justera listan utefter hur behoven ser ut.")

    base_data = ["Traktor", "Fyrhjuling", "Bil"]
    col1, col2 = st.columns([2, 1])

    data_categories = {
        "Traktor": [],
        "Fyrhjuling": [],
        "Handverktyg": [],
        "Elverktyg": [],
        "Övrigt": []
    }

    # Läs in data från CSV-filen
    try:
        df_technical_needs = pd.read_csv("technical_needs.csv")

    except FileNotFoundError:
        st.info("Filen 'technical_needs.csv' hittades inte. En ny med basdata skapas.")
        df_technical_needs = pd.DataFrame(base_data, columns=["Redskap"])

    with col1:
        st.subheader("Lägg till redskap och verktyg")
        with st.form("redskap_form"):
            category = st.selectbox("Kategori", list(data_categories.keys()))
            redskap = st.text_input("Redskap eller verktyg:")
            submit_redskap = st.form_submit_button("Lägg till")

            if submit_redskap:
                new_tool = f"{category} - {redskap}"  # Skapa en sträng direkt
                # Skapa en ny rad som en DataFrame
                new_row = pd.DataFrame({'Redskap': new_tool}, index=[0])

                # Sätt ihop de två DataFrames
                df_technical_needs = pd.concat([df_technical_needs, new_row], ignore_index=True)
                # Ta bort duplikater (om det behövs)
                df_technical_needs = df_technical_needs.drop_duplicates()
                # Spara till CSV
                df_technical_needs.to_csv("technical_needs.csv", index=False)
                st.success("Redskap eller verktyg tillagd!")
                st.rerun()

    with col2:
        st.subheader("Redskap och verktyg")
        st.write("Markera rutan för att ta radera")

        for row in df_technical_needs.iterrows():
            redskap = row[1]["Redskap"]

            if "Traktor" in redskap:
                data_categories["Traktor"].append(redskap)
            elif "Fyrhjuling" in redskap:
                data_categories["Fyrhjuling"].append(redskap)
            elif "Handverktyg" in redskap:
                data_categories["Handverktyg"].append(redskap)
            elif "Elverktyg" in redskap:
                data_categories["Elverktyg"].append(redskap)
            else:
                data_categories["Övrigt"].append(redskap)

        tractor_data_length = len(data_categories["Traktor"])
        atv_data_length = len(data_categories["Fyrhjuling"])
        handtool_data_length = len(data_categories["Handverktyg"])
        powertool_data_length = len(data_categories["Elverktyg"])
        other_data_length = len(data_categories["Övrigt"])

        selected_tools = set()
        for category, data in data_categories.items():
            with st.expander(f"{category} - Antal redskap: {len(data)}"):
                for item in data:
                    if st.checkbox(item):
                        selected_tools.add(item)
                    else:
                        selected_tools.discard(item)

        if st.button("Ta Bort Redskap"):
            if selected_tools:
                df_technical_needs = df_technical_needs[~df_technical_needs["Redskap"].isin(selected_tools)]
                df_technical_needs.to_csv("technical_needs.csv", index=False)
                st.session_state.success_message = (f"{len(selected_tools)} valda redskap borttagna! Dessa togs bort: "
                                                    f"{', '.join(selected_tools)}")
                st.rerun()
            else:
                st.warning("Inga redskap valda.")
        if "success_message" in st.session_state:
            st.success(st.session_state.success_message)
            del st.session_state.success_message
