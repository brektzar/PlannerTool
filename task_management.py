import streamlit as st
import pandas as pd



def update_data(df, index, column, new_value):
    # Hämta den ursprungliga datatypen
    original_dtype = df[column].dtype

    # Försök konvertera det nya värdet till rätt datatyp
    try:
        if column == "Tekniska behov":
            if not new_value:
                new_value = ["Inget Verktyg Valt"]
            else:
                if not isinstance(new_value, list):
                    new_value = [new_value]
            df.loc[index, column] = ", ".join(new_value)

        else:
            if pd.api.types.is_numeric_dtype(original_dtype):
                try:
                    new_value = pd.to_numeric(new_value)
                except ValueError:
                    st.error(f"Ogiltigt värde för {column}. Vänligen ange ett nummer.")
                    return
            elif original_dtype == 'datetime64[ns]':
                try:
                    new_value = pd.to_datetime(new_value)
                except ValueError:
                    st.error(f"Ogiltigt datum för {column}. Använd formatet ÅÅÅÅ-MM-DD.")
                    return
            else:
                new_value = str(new_value)  # Konvertera till sträng som standard

        df.loc[index, column] = new_value
        df.to_csv("Planering.csv", index=False)
        st.success("Data uppdaterad!")
    except Exception as e:
        st.error(f"Ett fel uppstod: {e}")


def task_management():

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
                    task_start_date = st.date_input("Uppgiftsstart")
                    task_end_date = st.date_input("Uppgiftsslut")
                    estimated_time = st.number_input("Uppskattad tidsåtgång (timmar)", min_value=0.0)
                    estimated_cost = st.number_input("Uppskattad kostnad", min_value=0.0)

                    technical_needs = st.multiselect("Välj Verktyg/Redskap", technical_needs_data['Redskap'].tolist(),
                                                     default="Inget Verktyg Valt")
                    if not technical_needs:
                        technical_needs = ["Inget Verktyg Valt"]

                    with st.expander("Hyra?"):
                        rental = st.text_input("Vad ska hyras?")
                        rental_type = st.selectbox("Hyrestyp", ["Dygn", "Timmar"])
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
                            "Uppgiftsstart": task_start_date,
                            "Uppgiftsslut": task_end_date,
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
            task_updated = False

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
                                        elif column == "Uppgiftsstart" or column == "Uppgiftsslut":
                                            # Datum hanteras som datum
                                            value = pd.to_datetime(value)
                                            new_value = st.date_input(f"Nytt datum för {column}:", value=value)
                                        else:
                                            # För andra kolumner, använd samma logik som tidigare
                                            new_value = st.text_input(f"Nytt värde för {column}:", value=value)

                                        if st.button("Uppdatera", key=f"update_{index}_{column}"):
                                            update_data(df_tasks, index, column, new_value)
                                            task_updated = True

            if task_updated:
                st.rerun()

        except FileNotFoundError:
            st.info("Fil med uppgifter hittades inte.")
        except Exception as we:
            st.error(f"Ett fel uppstod: {we} (Detta beror förmodligen på att målet saknar uppgifter.)")
        except pd.errors.EmptyDataError:
            st.info("Filen 'Planering.csv' är tom. Lägg till ett nytt mål.")
