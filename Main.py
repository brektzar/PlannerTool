import sys

import streamlit as st
import task_management as tm
import goal_management as gm
import adjust_tools as at
import report as rp

author = "Jimmy Nilsson"



st.set_page_config(
    layout="wide"
)

st.sidebar.title("Välkommen till min Planeringsapp")

st.sidebar.info("""
Denna app hjälper dig att sätta upp mål och planera de uppgifter som behövs för att uppnå dem.
Följ stegen nedan för att komma igång:
""")

st.sidebar.subheader("1. Skapa Mål")
st.sidebar.info("Börja med att definiera dina mål i fliken för målbeskrivning.")

st.sidebar.subheader("2. Planera Uppgifter")
st.sidebar.info("När målen är skapade kan du planera specifika uppgifter under fliken för planering.")

st.sidebar.subheader("3. Följ Statistik och Scheman")
st.sidebar.info("Efter att du har skapat mål och uppgifter kan du visa "
                "statistik och scheman för att följa din framsteg.")

st.sidebar.subheader("4. Bocka av de färdiga målen och uppgifterna!")
st.sidebar.success("När en uppgift är klar så kan du bocka av den och när alla uppgifter för "
                   "ett mål är avklarade så blir målet automatiskt klart.\n\n"
                   "Detta är en funktion under uppbyggnad!")

st.sidebar.divider()

st.sidebar.warning("""
Observera:
- Denna webapp är ett pågående projekt för att lära mig programmering. 
- Det kan förekomma buggar och vissa funktioner kanske inte fungerar perfekt.
""")

st.sidebar.error("""
Jag uppskattar din förståelse och feedback under utvecklingsprocessen. 
Tack för att du testar appen!
""")

tab_names = ["Målbeskrivning", "Planering", "Rapport", "Tekniska Behov - lista"]
tabs = st.tabs(tab_names)

with tabs[0]:
    st.header("Målbeskrivning")
    gm.goal_management()

with tabs[1]:
    st.header("Planera uppgifter för ett givet mål")
    tm.task_management()

with (tabs[3]):
    st.header("Lista på redskap och verktyg")
    at.adjust_tools()

with (tabs[4]):
    st.title("Statistik och Rapporter")

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Projektöversikt",
        "Tidsstatistik",
        "Kostnadsanalys",
        "Resursanvändning",
        "Verktygsstatistik",
        "Hyreskostnader"
    ])

    with tab1:
        rp.project_overview()

    with tab2:
        rp.time_statistics()

    with tab3:
        rp.cost_analysis()

    with tab4:
        schema_inner_tabs = st.tabs(["Mål", "Uppgifter"])
        with schema_inner_tabs[0]:
            st.header("Målschema")
            rp.goals_schema()
        with schema_inner_tabs[1]:
            st.header("Uppgiftschema")
            rp.tasks_schema()
        rp.resource_utilization()

    with tab5:
        rp.tools_report()
        rp.tools_per_categories_report()
        rp.tools_categories_used_report()

    with tab6:
        rp.rental_costs()


st.divider()

col1, col2 = st.columns([2, 1])
with col2:
    st.info(f"//// By: {author}  -  Streamlit Version: {st.__version__} - "
            f"Python Version: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} ////")