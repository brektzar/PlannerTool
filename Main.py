import streamlit as st
import task_management as tm
import goal_management as gm
import adjust_tools as at
import report as rp


st.set_page_config(
    layout="wide"
)

tab_names = ["Målbeskrivning", "Planering", "Rapport", "Tekniska Behov - lista"]
tabs = st.tabs(tab_names)

with tabs[0]:
    st.header("Målbeskrivning")
    gm.goal_management()

with tabs[1]:
    st.header("Planera uppgifter för ett givet mål")
    tm.task_management()

with tabs[2]:
    st.header("Rapport")
    inner_tabs = st.tabs(["Målrapport", "Uppgiftsrapport", "Verktygsrapport"])
    with inner_tabs[0]:
        st.header("Målschema")
        rp.goals_report()
    with inner_tabs[1]:
        st.header("Uppgiftschema")
        rp.tasks_report()
    with inner_tabs[2]:
        st.header("Verktygschema")
        rp.tools_report()
        rp.tools_categories_used_report()
        rp.tools_per_categories_report()

with (tabs[3]):
    st.header("Lista på redskap och verktyg")
    at.adjust_tools()
