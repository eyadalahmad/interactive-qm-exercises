import streamlit as st
import pandas as pd
import plotly.express as px

from services.exercise_service import ExerciseService
from services.results_service import ResultsService


class ResultsComparison:
    SCORE_KEYS = {
        "Farbmischung": "similarity_percent",
        "3D-Druckoptimierung": "quality_score",
    }

    def __init__(self):
        self.exercise_service = ExerciseService()
        self.results_service = ResultsService()

    def calculate_round_comparison(self, groups, score_key):
        comparison = []

        for group in groups:
            round_1 = [
                float(attempt["results"][score_key])
                for attempt in group["attempts"]
                if attempt["round_number"] == 1
                and score_key in attempt["results"]
            ]

            round_2 = [
                float(attempt["results"][score_key])
                for attempt in group["attempts"]
                if attempt["round_number"] == 2
                and score_key in attempt["results"]
            ]

            best_1 = max(round_1) if round_1 else None
            best_2 = max(round_2) if round_2 else None

            improvement = (
                round(best_2 - best_1, 2)
                if best_1 is not None and best_2 is not None
                else None
            )

            comparison.append({
                "Gruppe": group["group_name"],
                "Runde 1": best_1,
                "Runde 2": best_2,
                "Verbesserung (PP)": improvement,
            })

        df = pd.DataFrame(comparison)

        if not df.empty:
            for column in [
                "Runde 1",
                "Runde 2",
                "Verbesserung (PP)"
            ]:
                df[column] = pd.to_numeric(
                    df[column],
                    errors="coerce"
                )

        return df

    def render_round_comparison(self, groups, selected):
        st.markdown("### Vorher-Nachher-Vergleich")

        score_key = self.SCORE_KEYS[selected]

        axis_title = (
            "Ähnlichkeit (%)"
            if selected == "Farbmischung"
            else "Qualität (%)"
        )

        df = self.calculate_round_comparison(
            groups,
            score_key
        )

        if df.empty:
            st.info("Keine Gruppen vorhanden.")
            return

        paired = df.dropna(subset=["Runde 1", "Runde 2"])

        if paired.empty:
            st.info(
                "Für den Vorher-Nachher-Vergleich werden "
                "Ergebnisse aus beiden Runden benötigt."
            )
        else:
            mean_1 = paired["Runde 1"].mean()
            mean_2 = paired["Runde 2"].mean()
            improvement = mean_2 - mean_1

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "Ø Runde 1",
                    f"{mean_1:.2f} %"
                )

            with col2:
                st.metric(
                    "Ø Runde 2",
                    f"{mean_2:.2f} %"
                )

            with col3:
                st.metric(
                    "Durchschnittliche Verbesserung",
                    f"{improvement:+.2f} PP"
                )

            st.caption(
                f"Vergleichbare Gruppen: {len(paired)} / {len(df)}"
            )

        chart_col1, chart_col2 = st.columns(2, gap="medium")

        with chart_col1:
            st.markdown("### Gruppenvergleich nach Runden")

            chart_df = df.melt(
                id_vars=["Gruppe"],
                value_vars=["Runde 1", "Runde 2"],
                var_name="Runde",
                value_name="Bestes Ergebnis (%)"
            ).dropna(subset=["Bestes Ergebnis (%)"])

            if not chart_df.empty:
                fig = px.bar(
                    chart_df,
                    x="Gruppe",
                    y="Bestes Ergebnis (%)",
                    color="Runde",
                    barmode="group",
                    text_auto=".1f",
                    color_discrete_map={
                        "Runde 1": "#7DBEF0",
                        "Runde 2": "#2ECC71"
                    }
                )

                fig.update_layout(
                    height=300,
                    yaxis_range=[0, 110],
                    yaxis_title=axis_title,
                    xaxis_title="Gruppe",
                    bargap=0.45,
                    bargroupgap=0.1,
                    margin=dict(l=10, r=10, t=35, b=10),
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="center",
                        x=0.5,
                        title_text=""
                    )
                )

                fig.update_traces(textposition="outside")

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

            else:
                st.info("Noch keine Ergebnisse vorhanden.")

        with chart_col2:
            st.markdown("### Verbesserung pro Gruppe")

            improvement_df = df.dropna(
                subset=["Verbesserung (PP)"]
            ).sort_values("Verbesserung (PP)")

            if not improvement_df.empty:
                fig = px.bar(
                    improvement_df,
                    x="Verbesserung (PP)",
                    y="Gruppe",
                    orientation="h",
                    text_auto="+.2f"
                )

                fig.update_traces(
                    marker_color="#E74C3C",
                    textposition="outside",
                    cliponaxis=False
                )

                fig.add_vline(
                    x=0,
                    line_color="gray",
                    line_width=1
                )

                fig.update_layout(
                    height=300,
                    xaxis_title="Veränderung (Prozentpunkte)",
                    yaxis_title="Gruppe",
                    showlegend=False,
                    bargap=0.65,
                    margin=dict(l=10, r=45, t=35, b=10)
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

            else:
                st.info(
                    "Noch keine vergleichbaren Ergebnisse "
                    "aus beiden Runden vorhanden."
                )
        st.markdown("### Ergebnisvergleich")

        display_df = df.copy()

        for column in ["Runde 1", "Runde 2"]:
            display_df[column] = display_df[column].apply(
                lambda value: f"{value:.2f} %"
                if pd.notna(value) else "–"
            )

        display_df["Verbesserung (PP)"] = (
            display_df["Verbesserung (PP)"].apply(
                lambda value: f"{value:+.2f} PP"
                if pd.notna(value) else "–"
            )
        )

        st.dataframe(
            display_df,
            hide_index=True,
            width="stretch"
        )

        st.markdown("### Details der Versuche")

        group_names = [
            group["group_name"]
            for group in groups
        ]

        chosen_group = st.selectbox(
            "Gruppe auswählen",
            options=group_names,
            key=f"admin_round_results_group_{selected}"
        )

        chosen = next(
            group for group in groups
            if group["group_name"] == chosen_group
        )

        if not chosen["attempts"]:
            st.info("Noch keine Versuche vorhanden.")
            return

        detail_rows = []

        for attempt in chosen["attempts"]:
            parameters = attempt["parameters"]
            results = attempt["results"]

            if selected == "Farbmischung":
                detail_rows.append({
                    "Runde": attempt["round_number"],
                    "Versuch": attempt["attempt_number"],
                    "Farbe 1": parameters["color_1"],
                    "Farbe 2": parameters["color_2"],
                    "Mischfarbe": results["mixed_color"],
                    "Zielfarbe": results["target_color"],
                    "Ähnlichkeit (%)": results["similarity_percent"],
                })

            else:
                detail_rows.append({
                    "Runde": attempt["round_number"],
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
        st.dataframe(
            detail_rows,
            hide_index=True,
            width="stretch"
        )
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

        self.render_round_comparison(groups, selected)