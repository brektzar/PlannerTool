import streamlit as st
import pandas as pd
import numpy as np
from st_aggrid import AgGrid, GridOptionsBuilder




# Functionality: Risk Severity
def get_severity_info(severity):
    if 1 <= severity <= 3:
        return "Låg", "green"
    elif 4 <= severity <= 6:
        return "Medellåg", "yellow"
    elif 7 <= severity <= 9:
        return "Medelhög", "orange"
    else:
        return "Hög", "red"


# Function to render the Risk Assessment form and logic
def risk_assessment_page():

    # Streamlit-app
    st.title("Riskmatris")

    st.image("Riskmatris.png")
    st.text("Grön = Låg, Gul = Medellåg, Orange = Medelhög, Röd = Hög")

    st.subheader("Riskbedömning för arbete")

    # Form to input risk details
    with st.form("risk_form"):
        risk_name = st.text_input("Riskkälla:", placeholder="Skriv in vart risken har uppstått")
        risk_description = st.text_area("Riskbeskrivning:", placeholder="Beskriv risken tydligt")
        likelihood = st.selectbox("Sannolikhet:", [1, 2, 3, 4])
        impact = st.selectbox("Konsekvens:", [1, 2, 3, 4])
        action = st.text_input("Åtgärd:", placeholder="Skriv ner åtgärd för att hantera risken")
        responsible = st.text_input("Ansvarig:", placeholder="Välj den person som ansvarar")
        action_date = st.date_input("Datum för åtgärd:")
        follow_up_date = st.date_input("Datum för Uppföljning:")

        # Calculate severity
        severity = likelihood * impact
        severity_level, severity_color = get_severity_info(severity)

        # Submit button
        submitted = st.form_submit_button("Spara")
        if submitted:
            st.success(f"Risk: {risk_name} har sparats med allvarlighetsgraden {severity_level}.")
            st.write("Detaljer:")
            st.json(
                {
                    "Riskkälla": risk_name,
                    "Riskbeskrivning": risk_description,
                    "Sannolikhet": likelihood,
                    "Konsekvens": impact,
                    "Allvarlighet": severity,
                    "Åtgärd": action,
                    "Ansvarig": responsible,
                    "Datum för åtgärd": str(action_date),
                    "Datum för uppföljning": str(follow_up_date),
                }
            )

    # Risk severity matrix visualization
    # Definiera sannolikhets- och konsekvensnivåer
    sannolikhet = ['Osannolik', 'Möjlig', 'Trolig', 'Mycket trolig']
    konsekvens = ['Ringa', 'Medel', 'Stor', 'Mycket stor']

    # Skapa en tom DataFrame
    df = pd.DataFrame(
        data=[[0] * len(konsekvens) for _ in sannolikhet],
        index=sannolikhet,
        columns=konsekvens
    )

    # Fyll DataFrame med värden enligt din önskade struktur
    for i, s in enumerate(sannolikhet):
        for j, k in enumerate(konsekvens):
            df.loc[s, k] = (i + 1) * (j + 1)

    # Fyll DataFrame med värden enligt din önskade struktur
    for i, s in enumerate(sannolikhet):
        for j, k in enumerate(konsekvens):
            df.loc[s, k] = (i + 1) * (j + 1)


# Configure the page
st.set_page_config(
    page_title="Arbetsmiljö - Hjälpmedel",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Choose a page", ["Risk och Konsekvensanalys", "Åtgärdsplanering"])

# Theme switcher (Light/Dark mode toggle)
theme_toggle = st.sidebar.checkbox("Dark Mode", value=True)  # Start with dark mode by default
if theme_toggle:
    st.markdown(
        """
        <style>
        body {
            background-color: #1c1f26;
            color: #FAFAFA;
        }
        .stSelectbox, .stTextInput, .stTextArea, .stDateInput, .stButton {
            background-color: #2a2e38;
            color: #FAFAFA;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        """
        <style>
        body {
            background-color: #FFFFFF;
            color: #333333;
        }
        .stSelectbox, .stTextInput, .stTextArea, .stDateInput, .stButton {
            background-color: #f2f2f2;
            color: #333333;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

# Header
st.title("Arbetsmiljö - Hjälpmedel")

# Page content
if page == "Risk och Konsekvensanalys":
    risk_assessment_page()
elif page == "Åtgärdsplanering":
    st.subheader("Funktion under uppbyggnad")
