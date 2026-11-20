
import streamlit as st

from services.exercise_service import ExerciseService
from ui.countdown_timer import CountdownTimer
from ui.exercises.color_mixing_view import ColorMixingView
from ui.exercises.printing_3d_view import Printing3DView


class StudentDashboard:
    def render(self):
        group = st.session_state.get("student_group")

        if not group:
            st.error("Zugriff verweigert.")
            return

        st.title("Interaktive QM-Übungen")

        col1, col2 = st.columns([4, 1])

        with col1:
            st.success(f"Angemeldet als: {group['name']}")

        with col2:
            if st.button("Abmelden", key="student_logout"):
                st.session_state.pop("student_group", None)
                st.session_state.pop("group_code", None)
                st.rerun()

        st.divider()

        selected_exercise = st.segmented_control(
            "Übung auswählen",
            options=["Farbmischung", "3D-Druckoptimierung"],
            default="Farbmischung",
            key="student_exercise_selection"
        )

        st.divider()

        self.monitor_exercise_status(selected_exercise)

        self.render_selected_exercise(selected_exercise)

    
    @st.fragment(run_every="3s")
    def monitor_exercise_status(self, selected_exercise):
        try:
            exercises = ExerciseService().get_exercises()

            exercise = next(
                (
                    item for item in exercises
                    if item["name"] == selected_exercise
                ),
                None
            )

            if exercise is None:
                return

            current_state = (
                exercise["id"],
                exercise["status"],
                exercise["started_at"],
                exercise["ends_at"]
            )

            state_key = "monitored_exercise_state"

            previous_state = st.session_state.get(state_key)

            if previous_state is None:
                st.session_state[state_key] = current_state

            elif previous_state != current_state:
                st.session_state[state_key] = current_state
                st.rerun(scope="app")

        except Exception:
            st.error(
                "Übungsstatus konnte nicht aktualisiert werden."
            )

    def render_selected_exercise(self, selected_exercise):
        try:
            service = ExerciseService()
            exercises = service.get_exercises()

        except Exception:
            st.error("Übungen konnten nicht geladen werden.")
            return

        exercise_map = {
            exercise["name"]: exercise
            for exercise in exercises
        }

        exercise = exercise_map.get(selected_exercise)

        if exercise is None:
            st.error("Übung nicht gefunden.")
            return

        if exercise["status"] == "active":
            CountdownTimer().render(exercise["ends_at"])

        if selected_exercise == "Farbmischung":
            ColorMixingView().render(exercise)

        elif selected_exercise == "3D-Druckoptimierung":
            Printing3DView().render(exercise)
