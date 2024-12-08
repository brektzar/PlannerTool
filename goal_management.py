import streamlit as st
import pandas as pd
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


def goal_management():
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