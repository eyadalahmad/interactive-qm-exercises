
import streamlit as st

from services.admin_auth import AdminAuth
from ui.group_management import GroupManagement
from ui.exercise_management import ExerciseManagement
from ui.results_comparison import ResultsComparison


class AdminDashboard:
    def __init__(self):
        self.auth = AdminAuth()

    def render(self):
        if not self.auth.is_authenticated():
            st.error("Zugriff verweigert.")
            return

        st.title("Admin Dashboard")
        st.write("Willkommen im Administrationsbereich.")

        if st.button("Abmelden"):
            self.auth.logout()
            st.session_state["show_admin_login"] = False
            st.rerun()

        st.divider()

        GroupManagement().render()

        st.divider()

        ExerciseManagement().render()

        st.divider()

        ResultsComparison().render()