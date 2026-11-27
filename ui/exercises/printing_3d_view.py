
from uuid import uuid4

import streamlit as st

from services.attempt_service import AttemptService
from services.exercise_service import ExerciseService
from services.printing_simulation_service import (
    MATERIALS,
    PrintingSettings,
    PrintingSimulationService,
)
from ui.exercises.printing_3d_visualizer import Printing3DVisualizer


class Printing3DView:
    def __init__(self):
        self.attempt_service = AttemptService()
        self.visualizer = Printing3DVisualizer()
        self.exercise_service = ExerciseService()

    def render(self, exercise):
        st.subheader("3D-Druckoptimierung")

        if exercise is None:
            st.error("Übung nicht gefunden.")
            return

        status = exercise["status"]

        if status == "locked":
            st.info(
                "Bitte warten Sie auf die Freigabe "
                "durch den Administrator."
            )
            return

        if status == "active":
            st.success("Die Übung ist aktiv.")

        elif status == "finished":
            st.warning("Die Übung ist abgeschlossen.")

        else:
            st.error("Unbekannter Übungsstatus.")
            return

        group = st.session_state.get("student_group")

        if not group:
            st.error("Gruppe nicht gefunden.")
            return

        try:
            current_round = (
                self.exercise_service.get_printing_current_round()
            )

            attempts = self.attempt_service.get_attempts(
                group["id"],
                exercise["id"],
                current_round
            )

        except Exception:
            st.error("Versuche konnten nicht geladen werden.")
            return

        st.markdown(f"## Runde {current_round} / 2")

        remaining = max(
            0, self.attempt_service.MAX_ATTEMPTS - len(attempts)
        )

        st.write(
            f"Verbleibende Versuche: **{remaining}**"
        )

        if status == "active" and remaining > 0:
            self.render_inputs(group, exercise, current_round)

        if attempts:
            st.divider()
            st.subheader("Bisherige Versuche")

            for attempt in attempts:
                self.render_attempt(attempt)

    def render_inputs(self, group, exercise, current_round):
        session_id = self.attempt_service.session_service.get_current_session_id()
        attempt_scope = (group["id"], exercise["id"], session_id, current_round)
        state_key = "printing_submission_state"
        state = st.session_state.get(state_key)

        if state is None or state["scope"] != attempt_scope:
            state = {
                "scope": attempt_scope,
                "submission_id": str(uuid4()),
                "awaiting_next": False,
            }
            st.session_state[state_key] = state

        if state["awaiting_next"]:
            st.info("Versuch gespeichert. Starten Sie den nächsten Versuch, um fortzufahren.")
            if st.button("Nächsten Versuch starten", key="printing_next_attempt"):
                state["submission_id"] = str(uuid4())
                state["awaiting_next"] = False
                st.rerun()
            return

        material = st.selectbox(
            "Druckmaterial",
            options=list(MATERIALS.keys()),
            key="printing_material",
        )

        ranges = MATERIALS[material]

        with st.form(key="printing_attempt_form"):
            temperature = st.slider(
                "Düsentemperatur (°C)",
                min_value=ranges["temperature"][0],
                max_value=ranges["temperature"][1],
                value=ranges["temperature"][2],
                step=ranges["temperature"][3],
                key=f"printing_temperature_{material}",
            )

            speed = st.slider(
                "Druckgeschwindigkeit (mm/s)",
                min_value=ranges["speed"][0],
                max_value=ranges["speed"][1],
                value=ranges["speed"][2],
                step=ranges["speed"][3],
                key=f"printing_speed_{material}",
            )

            layer_height = st.slider(
                "Schichthöhe (mm)",
                min_value=ranges["layer"][0],
                max_value=ranges["layer"][1],
                value=ranges["layer"][2],
                step=ranges["layer"][3],
                key=f"printing_layer_{material}",
            )

            submitted = st.form_submit_button(
                "Versuch bestätigen",
                type="primary",
            )

        if submitted and not state["awaiting_next"]:
            try:
                settings = PrintingSettings(
                    material=material,
                    temperature=temperature,
                    print_speed=speed,
                    layer_height=layer_height,
                )

                result = PrintingSimulationService(
                    settings
                ).run()

                parameters = {
                    "material": material,
                    "temperature": temperature,
                    "print_speed": speed,
                    "layer_height": layer_height,
                }

                self.attempt_service.save_attempt(
                    group_id=group["id"],
                    exercise_id=exercise["id"],
                    parameters=parameters,
                    results=result,
                    submission_id=state["submission_id"],
                    round_number=current_round,
                )
                state["awaiting_next"] = True
                st.rerun()

            except Exception as error:
                st.error(
                    f"Versuch konnte nicht gespeichert werden: {error}"
                )

    def render_attempt(self, attempt):
        result = attempt["results"]

        with st.expander(
            f"Versuch {attempt['attempt_number']}",
            expanded=True,
        ):
            col1, col2 = st.columns(2)

            with col1:
                st.metric(
                    "Qualität",
                    f"{result['quality_score']:.2f} %",
                )
                st.metric(
                    "Anzahl der Schichten",
                    result["layer_count"],
                )

            with col2:
                st.metric(
                    "Warping",
                    f"{result['warping_mm']:.4f} mm",
                )
                st.metric(
                    "Layer Shifting",
                    f"{result['layer_shifting_mm']:.4f} mm",
                )

            figure = self.visualizer.create_figure(result)

            st.plotly_chart(
                figure,
                width="stretch",
                key=f"printing_figure_{attempt['id']}",
            )