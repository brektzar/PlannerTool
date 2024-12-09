import streamlit as st
import pandas as pd


def adjust_tools():
    st.write("Justera listan utefter hur behoven ser ut.")
    st.divider()

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

        data_categories["Traktor"].sort()
        data_categories["Fyrhjuling"].sort()
        data_categories["Handverktyg"].sort()
        data_categories["Elverktyg"].sort()
        data_categories["Övrigt"].sort()
        dc_df = pd.DataFrame.from_dict(data_categories, orient="index")
        dc_df = dc_df.transpose()
        dc_df.to_csv("data_categories.csv", index=False)

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