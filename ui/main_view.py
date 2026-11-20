
import streamlit as st

from services.admin_auth import AdminAuth
from ui.admin_login import AdminLogin
from ui.group_management import GroupManagement
from services.group_service import GroupService
from ui.exercise_management import ExerciseManagement
from ui.admin_dashboard import AdminDashboard
from ui.student_dashboard import StudentDashboard


class MainView:
    def __init__(self):
        self.auth = AdminAuth()

    def render(self):
        st.set_page_config(
            page_title="Interactive QM Exercises",
            page_icon="🎓",
            layout="wide"
        )

        if self.auth.is_authenticated():
            AdminDashboard().render()
        elif st.session_state.get("student_group"):
            StudentDashboard().render()
        else:
            self.render_home()

    def render_home(self):
        st.title("Interaktive QM-Übungen")
        st.write(
            "Willkommen zu den interaktiven Übungen "
            "im Qualitätsmanagement."
        )

        st.divider()

        if st.session_state.get("show_admin_login", False):
            if st.button("← Zurück"):
                st.session_state["show_admin_login"] = False
                st.rerun()

            AdminLogin().render()
            return

        st.subheader("Gruppenanmeldung")
        st.text_input("Gruppencode", key="group_code")

        
        if st.button("Anmelden", key="student_login"):
            try:
                group = GroupService().authenticate_group(
                    st.session_state.get("group_code", "")
            )

                if group:
                    st.session_state["student_group"] = group
                    st.rerun()
                else:
                    st.error("Ungültiger Gruppencode.")

            except Exception:
                st.error("Anmeldung fehlgeschlagen.")


        st.divider()

        if st.button("Administration"):
            st.session_state["show_admin_login"] = True
            st.rerun()
