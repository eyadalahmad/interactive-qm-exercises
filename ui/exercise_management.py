
import streamlit as st

from services.admin_auth import AdminAuth
from services.exercise_service import ExerciseService
from ui.countdown_timer import CountdownTimer


class ExerciseManagement:
    def __init__(self):
        self.auth = AdminAuth()
        self.service = ExerciseService()

    def render(self):
        if not self.auth.is_authenticated():
            st.error("Zugriff verweigert.")
            return

        st.subheader("Übungssteuerung")

        try:
            self.service.finish_expired_exercises()
        except Exception:
            st.error("Übungsstatus konnte nicht aktualisiert werden.")
            return

        try:
            exercises = self.service.get_exercises()
        except Exception:
            st.error("Übungen konnten nicht geladen werden.")
            return

        if not exercises:
            st.info("Keine Übungen vorhanden.")
            return

        st.divider()
        st.subheader("Sitzungsverwaltung")

        confirm_reset = st.checkbox(
            "Ich bestätige, dass die Übungen für eine neue Sitzung "
            "zurückgesetzt werden.",
            key="confirm_session_reset"
        )

        if st.button(
            "Neue Sitzung vorbereiten",
            disabled=not confirm_reset,
            key="reset_exercises"
        ):
            if not self.auth.is_authenticated():
                st.error("Zugriff verweigert.")
                return

            try:
                self.service.reset_exercises()
                st.rerun()

            except Exception as error:
                st.error(
                    "Die Übungen konnten nicht zurückgesetzt werden."
                )
                st.exception(error)

        st.divider()

        for exercise in exercises:
            with st.container(border=True):
                st.write(f"**{exercise['name']}**")
                st.write(f"Status: {exercise['status']}")
                st.write(
                    f"Dauer: {exercise['duration_minutes']} Minuten"
                )
                if exercise["status"] == "active":
                    CountdownTimer().render(exercise["ends_at"])

                if exercise["status"] == "locked":
                    if st.button(
                        "Starten",
                        key=f"start_{exercise['id']}"
                    ):
                        if not self.auth.is_authenticated():
                            st.error("Zugriff verweigert.")
                            return

                        try:
                            self.service.start_exercise(
                                exercise["id"]
                            )
                            st.rerun()

                        except ValueError as error:
                            st.warning(str(error))

                        except Exception:
                            st.error(
                                "Die Übung konnte nicht gestartet werden."
                            )

                elif exercise["status"] == "active":
                    if st.button(
                        "Beenden",
                        key=f"end_{exercise['id']}"
                    ):
                        if not self.auth.is_authenticated():
                            st.error("Zugriff verweigert.")
                            return

                        try:
                            self.service.end_exercise(
                                exercise["id"]
                            )
                            st.rerun()

                        except ValueError as error:
                            st.warning(str(error))

                        except Exception:
                            st.error(
                                "Die Übung konnte nicht beendet werden."
                            )

                elif exercise["status"] == "finished":
                    st.success("Übung abgeschlossen.")

                if exercise["name"] == "Farbmischung":
                    st.divider()
                    st.write("**Zielfarbe einstellen**")

                    try:
                        target_color = self.service.get_target_color()
                    except Exception:
                        st.error(
                            "Die Zielfarbe konnte nicht geladen werden."
                        )
                        return

                    selected_color = st.color_picker(
                        "Zielfarbe auswählen",
                        value=target_color,
                        key="admin_target_color",
                        disabled=exercise["status"] != "locked"
                    )

                    st.code(selected_color, language=None)

                    if exercise["status"] == "locked":
                        if st.button(
                            "Zielfarbe speichern",
                            key="save_target_color"
                        ):
                            if not self.auth.is_authenticated():
                                st.error("Zugriff verweigert.")
                                return

                            try:
                                self.service.save_target_color(
                                    selected_color
                                )
                                st.success(
                                    "Die Zielfarbe wurde erfolgreich gespeichert."
                                )
                            except ValueError as error:
                                st.warning(str(error))
                            except Exception:
                                st.error(
                                    "Die Zielfarbe konnte nicht gespeichert werden."
                                )
                    else:
                        st.info(
                            "Die Zielfarbe kann während oder nach "
                            "der Übung nicht geändert werden."
                        )
