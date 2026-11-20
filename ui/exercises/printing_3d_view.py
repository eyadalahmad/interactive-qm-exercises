
import streamlit as st

from services.attempt_service import AttemptService
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
            attempts = self.attempt_service.get_attempts(
                group["id"], exercise["id"]
            )
        except Exception:
            st.error("Versuche konnten nicht geladen werden.")
            return

        remaining = max(
            0, self.attempt_service.MAX_ATTEMPTS - len(attempts)
        )

        st.write(
            f"Verbleibende Versuche: **{remaining}**"
        )

        if status == "active" and remaining > 0:
            self.render_inputs(group, exercise)

        if attempts:
            st.divider()
            st.subheader("Bisherige Versuche")

            for attempt in attempts:
                self.render_attempt(attempt)

    def render_inputs(self, group, exercise):
        material = st.selectbox(
            "Druckmaterial",
            options=list(MATERIALS.keys()),
            key="printing_material",
        )

        ranges = MATERIALS[material]

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

        if st.button(
            "Versuch bestätigen",
            type="primary",
            key="printing_submit",
        ):
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
                )


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
                use_container_width=True,
                key=f"printing_figure_{attempt['id']}",
            )
