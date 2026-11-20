import streamlit as st
import pandas as pd

from services.exercise_service import ExerciseService
from services.results_service import ResultsService
import altair as alt

class ResultsComparison:
    SCORE_KEYS = {
        "Farbmischung": "similarity_percent",
        "3D-Druckoptimierung": "quality_score",
    }

    def __init__(self):
        self.exercise_service = ExerciseService()
        self.results_service = ResultsService()

    @st.fragment
    def render(self):
        st.subheader("Ergebnisse der Gruppen")

        selected = st.segmented_control(
            "Übung auswählen",
            options=list(self.SCORE_KEYS.keys()),
            default="Farbmischung",
            key="admin_results_exercise",
        )

        if not selected:
            return

        try:
            exercises = self.exercise_service.get_exercises()
            exercise = next(
                (item for item in exercises if item["name"] == selected),
                None,
            )
            if exercise is None:
                st.error("Übung nicht gefunden.")
                return

            groups = self.results_service.get_results(exercise["id"])
        except Exception:
            st.error("Ergebnisse konnten nicht geladen werden.")
            return

        score_key = self.SCORE_KEYS[selected]
        ranking = []

        for group in groups:
            attempts = group["attempts"]
            valid_attempts = [
                attempt for attempt in attempts
                if score_key in attempt["results"]
            ]
            best = (
                max(
                    valid_attempts,
                    key=lambda attempt: float(attempt["results"][score_key]),
                )
                if valid_attempts else None
            )
            ranking.append({
                "group": group,
                "best": best,
                "score": (
                    float(best["results"][score_key]) if best else None
                ),
            })

        ranking.sort(
            key=lambda item: (
                item["score"] is None,
                -item["score"] if item["score"] is not None else 0,
            )
        )

        if not ranking:
            st.info("Keine Gruppen vorhanden.")
            return

        st.markdown("### Gruppenvergleich")
        chart_rows = [
            {
                "Gruppe": item["group"]["group_name"],
                "Bestes Ergebnis (%)": item["score"],
            }
            for item in ranking if item["score"] is not None
        ]
        if chart_rows:
            chart = (
                alt.Chart(alt.Data(values=chart_rows))
                .mark_bar(color="#7DBEF0")
                .encode(
                    x=alt.X(
                        "Gruppe:N",
                        sort=None,
                        title="Gruppe",
                    ),
                    y=alt.Y(
                        "Bestes Ergebnis (%):Q",
                        scale=alt.Scale(domain=[0, 100]),
                        title="Ergebnis (%)",
                    ),
                    tooltip=[
                        alt.Tooltip("Gruppe:N"),
                        alt.Tooltip(
                            "Bestes Ergebnis (%):Q",
                            format=".2f",
                        ),
                    ],
                )
                .properties(height=350, width="container")
            )

            st.altair_chart(
                chart,
                use_container_width=True,
            )
        else:
            st.info("Noch keine Ergebnisse für diese Übung vorhanden.")

        st.markdown("### Rangliste")
        rows = [
            {
                "Rang": str(position) if item["best"] else "–",
                "Gruppe": item["group"]["group_name"],
                "Versuche": len(item["group"]["attempts"]),
                "Bester Versuch": (
                    int(item["best"]["attempt_number"])
                    if item["best"] else None
                ),
                "Bestes Ergebnis": (
                    f"{item['score']:.2f} %"
                    if item["score"] is not None else "–"
                ),
            }
            for position, item in enumerate(ranking, start=1)
        ]
        df = pd.DataFrame(rows)

        df["Bester Versuch"] = pd.to_numeric(
            df["Bester Versuch"], errors="coerce"
        )

        styled_df = df.style.format(
            {
                "Bester Versuch": "{:.0f}",
            },
            na_rep="–",
        )

        st.dataframe(
            styled_df,
            hide_index=True,
            width="stretch",
        )

        st.markdown("### Details der Versuche")
        group_names = [item["group"]["group_name"] for item in ranking]
        chosen_group = st.selectbox(
            "Gruppe auswählen",
            options=group_names,
            key="admin_results_group",
        )
        chosen = next(
            item for item in ranking
            if item["group"]["group_name"] == chosen_group
        )
        attempts = chosen["group"]["attempts"]
        if not attempts:
            st.info("Noch keine Versuche vorhanden.")
            return

        detail_rows = []
        for attempt in attempts:
            parameters = attempt["parameters"]
            results = attempt["results"]
            if selected == "Farbmischung":
                detail_rows.append({
                    "Versuch": attempt["attempt_number"],
                    "Farbe 1": parameters["color_1"],
                    "Farbe 2": parameters["color_2"],
                    "Mischfarbe": results["mixed_color"],
                    "Zielfarbe": results["target_color"],
                    "Ähnlichkeit (%)": results["similarity_percent"],
                })
            else:
                detail_rows.append({
                    "Versuch": attempt["attempt_number"],
                    "Material": parameters["material"],
                    "Temperatur (°C)": parameters["temperature"],
                    "Geschwindigkeit (mm/s)": parameters["print_speed"],
                    "Schichthöhe (mm)": parameters["layer_height"],
                    "Qualität (%)": results["quality_score"],
                    "Schichten": results["layer_count"],
                    "Warping (mm)": results["warping_mm"],
                    "Layer Shifting (mm)": results["layer_shifting_mm"],
                })

        st.dataframe(detail_rows, hide_index=True, use_container_width=True)