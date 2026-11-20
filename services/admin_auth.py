
import hmac

import streamlit as st


class AdminAuth:
    def __init__(self):
        self.password = st.secrets["ADMIN_PASSWORD"]

    def login(self, entered_password: str) -> bool:
        if hmac.compare_digest(entered_password, self.password):
            st.session_state["admin_authenticated"] = True
            return True

        return False

    def logout(self):
        st.session_state["admin_authenticated"] = False

    def is_authenticated(self) -> bool:
        return st.session_state.get(
            "admin_authenticated", False
        )
