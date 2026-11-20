
import streamlit as st

from services.admin_auth import AdminAuth
from services.group_service import GroupService


class GroupManagement:
    def __init__(self):
        self.auth = AdminAuth()

    def render(self):
        if not self.auth.is_authenticated():
            st.error("Zugriff verweigert.")
            return

        st.subheader("Gruppenverwaltung")

        with st.form("create_group_form", clear_on_submit=True):
            name = st.text_input("Gruppenname")
            submitted = st.form_submit_button("Gruppe erstellen")

        if submitted:
            try:
                service = GroupService()
                service.create_group(name)
                st.success("Gruppe erfolgreich erstellt.")
            except ValueError as error:
                st.warning(str(error))
            except Exception:
                st.error("Gruppe konnte nicht erstellt werden.")

        st.divider()
        st.write("**Vorhandene Gruppen**")

        try:
            groups = GroupService().get_groups()

        except Exception:
            st.error("Gruppen konnten nicht geladen werden.")
            return

        if not groups:
            st.info("Noch keine Gruppen vorhanden.")
            return

        st.dataframe(
            [
                {
                    "Gruppe": group["name"],
                    "Gruppencode": group["access_code"]
                }
                for group in groups
            ],
            use_container_width=True,
            hide_index=True
        )

        st.divider()
        st.write("**Gruppe löschen**")

        group_options = {
            group["name"]: group["id"]
            for group in groups
        }

        selected_group = st.selectbox(
            "Gruppe auswählen",
            options=list(group_options.keys())
        )

        confirm_delete = st.checkbox(
            "Ich bestätige, dass die Gruppe und "
            "alle zugehörigen Ergebnisse gelöscht werden."
        )

        if st.button(
            "Gruppe löschen",
            disabled=not confirm_delete
        ):
            if not self.auth.is_authenticated():
                st.error("Zugriff verweigert.")
                return

            try:
                GroupService().delete_group(
                    group_options[selected_group]
                )
                st.success("Gruppe erfolgreich gelöscht.")
                st.rerun()

            except Exception:
                st.error("Gruppe konnte nicht gelöscht werden.")
