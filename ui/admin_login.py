
import streamlit as st

from services.admin_auth import AdminAuth


class AdminLogin:
    def __init__(self):
        self.auth = AdminAuth()

    def render(self):
        st.subheader("Admin-Anmeldung")

        if self.auth.is_authenticated():
            st.success("Als Administrator angemeldet.")

            if st.button("Abmelden"):
                self.auth.logout()
                st.rerun()

            return

        with st.form("admin_login_form"):
            password = st.text_input(
                "Admin-Passwort",
                type="password"
            )

            submitted = st.form_submit_button("Anmelden")

        if submitted:
            if self.auth.login(password):
                st.rerun()
            else:
                st.error("Ungültiges Passwort.")
