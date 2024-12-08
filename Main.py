import streamlit as st
import pandas as pd
import numpy as np
import os


def save_to_csv(datainput):
    datainput.to_csv("Planering.csv", mode='a', header=not os.path.exists("Planering.csv"), index=False)


def clear_csv():
    try:
        os.remove("Planering.csv")
        st.success("Filen har rensats.")
    except FileNotFoundError:
        st.info("Filen fanns inte från början.")
    except Exception as e:
        st.error(f"Ett fel uppstod vid rensning: {e}")


tab_names = ["Målbeskrivning", "Planering", "Rapport"]
tabs = st.tabs(tab_names)

with tabs[0]:
    with st.form(key="Målbeskrivning"):
        goal = st.text_input("Övergripande Mål")
        taskDesc = st.text_input("Beskrivning")
        startDate = st.date_input("Startdatum")
        endDate = st.date_input("Slutdatum")
        submitted = st.form_submit_button("Submit")

    if submitted:
        if not goal or not taskDesc or not startDate or not endDate:
            st.error("Alla fält måste fyllas i.")
        else:
            try:
                data = pd.DataFrame(
                    {
                        "Övergripande Mål": [goal],
                        "Beskrivning": [taskDesc],
                        "Startdatum": [startDate],
                        "Slutdatum": [endDate],
                    }
                )
                save_to_csv(data)
                st.success("Målet har lagts till!")
                st.rerun()
            except Exception as e:
                st.error(f"Ett fel uppstod: {e}")

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

    except Exception as e:
        st.error(f"Ett oväntat fel uppstod: {e}")

    # Knapp för att rensa filen
    if st.button("Rensa fil"):
        clear_csv()
        st.rerun()

with tabs[1]:

    st.write("Planering")
    col1, col2 = st.columns([2, 1])

    with col1:
        st.write("Planering")
    # Läs in data från CSV-filen och visa den i en tabell
        try:
            df = pd.read_csv("Planering.csv")
            if df.empty:
                st.info("Ingen data finns ännu. Lägg till ett nytt mål.")
            else:
                goals = df['Övergripande Mål'].dropna().unique()
                selected_goal = st.selectbox("Välj mål", goals)

                # Visa uppgifter för det valda målet (implementera senare)

                with st.form("Lägg till uppgift"):
                    task = st.text_input("Uppgift")
                    task_desc = st.text_area("Beskrivning")
                    estimated_time = st.number_input("Uppskattad tidsåtgång (timmar)", min_value=0.0)
                    estimated_cost = st.number_input("Uppskattad kostnad", min_value=0.0)

                    technical_needs = st.multiselect(
                        "Tekniska behov",
                        ["Traktor", "Fyrhjuling", "Traktor - Griplastarvagn", "Elverktyg", ...]
                    )

                    with st.expander("Hyra?"):
                        rental = st.write("Vad ska hyras?")
                        rental_type = st.selectbox("Hyrestyp", ["Dygn", "Timme"])
                        rental_amount = st.number_input("Antal dygn/timmar", min_value=0.0)
                        rental_cost = st.number_input("Hyrkostnad per timme/dygn", min_value=0.0)
                        total_rental_cost = rental_amount * rental_cost

                    personnel = st.slider("Personalantal", 1, 10, 1)
                    other_needs = st.text_area("Andra behov")

                    submit_task = st.form_submit_button("Lägg till")

                    if submit_task:
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
                            "Hyreskostnad": rental_cost if rental == "Ja" else 0,
                            "Total hyreskostnad": total_rental_cost if rental == "Ja" else 0,
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

        except Exception as e:
            st.error(f"Ett oväntat fel uppstod: {e}")

    with col2:
        st.write("Mål och Uppgifter")

        # Läs in data från uppgiftsfilen (justera filnamnet och kolumnerna efter behov)
        try:
            df_tasks = pd.read_csv("Planering.csv")

            # Gruppera uppgifter efter mål
            for goal, tasks_df in df_tasks.groupby('Mål'):
                with st.expander(goal):
                    for index, row in tasks_df.iterrows():
                        task_checked = st.checkbox(f"Uppgift {index + 1}: {row['Uppgift']}")
                        if task_checked:
                            for column, value in row.items():
                                # Exkludera dessa kolumner
                                if column not in ['Mål', 'Uppgift', 'Övergripande Mål', 'Startdatum', 'Slutdatum']:
                                    st.write(f"{column}: {value}")

        except FileNotFoundError:
            st.info("Fil med uppgifter hittades inte.")
        except Exception as e:
            st.error(f"Ett fel uppstod: {e}")


with tabs[2]:
    st.write("Rapport")