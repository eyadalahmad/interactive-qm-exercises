from uuid import uuid4

import streamlit as st

from services.attempt_service import AttemptService
from services.exercise_service import ExerciseService


class ColorMixingView:
    @staticmethod
    def hex_to_rgb(hex_color: str):
        return tuple(
            int(hex_color[i:i + 2], 16)
            for i in (1, 3, 5)
        )

    @staticmethod
    def rgb_to_hex(rgb):
        return "#{:02X}{:02X}{:02X}".format(*rgb)

    def mix_colors(self, color1: str, color2: str):
        rgb1 = self.hex_to_rgb(color1)
        rgb2 = self.hex_to_rgb(color2)

        mixed_rgb = tuple(
            round((a + b) / 2)
            for a, b in zip(rgb1, rgb2)
        )

        return self.rgb_to_hex(mixed_rgb)

    def calculate_similarity(self, target_color, mixed_color):
        target_rgb = self.hex_to_rgb(target_color)
        mixed_rgb = self.hex_to_rgb(mixed_color)

        distance = sum(
            (a - b) ** 2
            for a, b in zip(target_rgb, mixed_rgb)
        ) ** 0.5

        return max(
            0.0,
            (1 - distance / (3 * 255 ** 2) ** 0.5) * 100
        )

    def show_color_preview(self, color: str):
        safe_color = self.rgb_to_hex(self.hex_to_rgb(color))

        st.markdown(
            f"""
            <div style="
                background-color: {safe_color};
                height: 45px;
                width: 40px;
                border-radius: 6px;
                border: 1px solid #808080;
            "></div>
            """,
            unsafe_allow_html=True
        )

    def show_color_info(self, color: str):
        rgb = self.hex_to_rgb(color)

        st.code(color, language=None)

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Rot",
                f"{rgb[0] / 255 * 100:.1f}%"
            )

        with col2:
            st.metric(
                "Grün",
                f"{rgb[1] / 255 * 100:.1f}%"
            )

        with col3:
            st.metric(
                "Blau",
                f"{rgb[2] / 255 * 100:.1f}%"
            )

    def show_attempt_result(self, attempt, rgb_help=False):
        number = attempt["attempt_number"]
        parameters = attempt["parameters"]
        results = attempt["results"]

        with st.expander(f"Versuch {number}", expanded=False):

            col1, col2 = st.columns(2)

            with col1:
                st.write("**Farbe 1**")

                self.show_color_preview(results["target_color"])

            with col2:
                st.write("**Farbe 2**")

                st.color_picker(
                    "Gespeicherte Farbe 2",
                    value=parameters["color_2"],
                    disabled=True,
                    key=f"saved_color_2_{attempt['id']}"
                )

            st.write("**Mischfarbe**")

            st.color_picker(
                "Gespeicherte Mischfarbe",
                value=results["mixed_color"],
                disabled=True,
                key=f"saved_mixed_{attempt['id']}"
            )

            self.show_color_info(results["mixed_color"])

            st.divider()

            st.markdown("### Vergleich mit der Zielfarbe")

            col_target, col_mixed = st.columns(2)

            with col_target:
                st.write("**Zielfarbe**")

                st.color_picker(
                    "Gespeicherte Zielfarbe",
                    value=results["target_color"],
                    disabled=True,
                    key=f"target_{attempt['id']}"
                )

                if rgb_help:
                    self.show_color_info(results["target_color"])

            with col_mixed:
                st.write("**Mischfarbe**")

                st.color_picker(
                    "Mischfarbe im Vergleich",
                    value=results["mixed_color"],
                    disabled=True,
                    key=f"compare_{attempt['id']}"
                )

                st.code(
                    results["mixed_color"],
                    language=None
                )

            similarity = float(
                results["similarity_percent"]
            )

            st.write(
                "**Übereinstimmung mit der Zielfarbe**"
            )

            st.progress(
                min(100.0, max(0.0, similarity / 100.0)),
                text=f"{similarity:.1f}%"
            )

    def render(self, exercise):
        st.subheader("Farbmischung")

        if exercise is None:
            st.error("Übung nicht gefunden.")
            return

        if exercise["status"] == "locked":
            st.info(
                "Bitte warten Sie auf die Freigabe "
                "durch den Administrator."
            )
            return

        is_active = exercise["status"] == "active"

        if is_active:
            st.success("Die Übung ist aktiv.")

        elif exercise["status"] == "finished":
            st.warning("Die Übung ist abgeschlossen.")

        else:
            return

        group = st.session_state.get("student_group")

        if not group:
            st.error("Gruppe nicht gefunden.")
            return

        try:
            attempt_service = AttemptService()
            exercise_service = ExerciseService()
            current_round = exercise_service.get_current_round()

            attempts = attempt_service.get_attempts(
                group["id"],
                exercise["id"],
                current_round
            )

        except Exception:
            st.error(
                "Versuche konnten nicht geladen werden."
            )
            return

        used_attempts = len(attempts)

        remaining_attempts = max(
            0,
            attempt_service.MAX_ATTEMPTS - used_attempts
        )

        try:
            target_color = exercise_service.get_target_color()
            rgb_help = exercise_service.get_rgb_help()
        except Exception:
            st.error("Die Farbeinstellungen konnten nicht geladen werden.")
            return

        st.markdown(f"## Runde {current_round} / 2")
        st.markdown("### Zielfarbe")

        self.show_color_preview(target_color)

        if rgb_help:
            self.show_color_info(target_color)
        st.divider()

        st.write(
            f"**Versuche: {used_attempts} / "
            f"{attempt_service.MAX_ATTEMPTS}**"
        )

        if is_active and remaining_attempts > 0:
            session_id = attempt_service.session_service.get_current_session_id()
            attempt_scope = (group["id"], exercise["id"], session_id, current_round)
            state_key = "color_submission_state"
            state = st.session_state.get(state_key)

            if state is None or state["scope"] != attempt_scope:
                st.session_state.pop("last_color_attempt", None)
                state = {
                    "scope": attempt_scope,
                    "submission_id": str(uuid4()),
                    "awaiting_next": used_attempts > 0,
                }
                st.session_state[state_key] = state

            if state["awaiting_next"]:
                st.info(
                    "Versuch gespeichert. Starten Sie den nächsten "
                    "Versuch, um fortzufahren."
                )
                if st.button(
                    "Nächsten Versuch starten",
                    key="color_next_attempt"
                ):
                    state["submission_id"] = str(uuid4())
                    state["awaiting_next"] = False
                    st.rerun()
            else:
                st.markdown(f"### Versuch {used_attempts + 1}")

                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("### Farbe 1")
                    color1 = st.color_picker(
                        "Erste Farbe auswählen",
                        value="#FF0000",
                        key="mix_color_1"
                    )
                    self.show_color_info(color1)

                with col2:
                    st.markdown("### Farbe 2")
                    color2 = st.color_picker(
                        "Zweite Farbe auswählen",
                        value="#0000FF",
                        key="mix_color_2"
                    )
                    self.show_color_info(color2)

                st.info(
                    "Die Mischfarbe wird erst nach "
                    "Bestätigung des Versuchs angezeigt."
                )

                if st.button(
                    "Farbauswahl bestätigen",
                    key="confirm_color_attempt",
                    type="primary"
                ) and not state["awaiting_next"]:
                    mixed_color = self.mix_colors(color1, color2)
                    similarity = self.calculate_similarity(
                        target_color, mixed_color
                    )

                    parameters = {
                        "color_1": color1,
                        "color_2": color2
                    }
                    results = {
                        "target_color": target_color,
                        "mixed_color": mixed_color,
                        "similarity_percent": round(similarity, 2)
                    }

                    try:
                        attempt_number = attempt_service.save_attempt(
                            group_id=group["id"],
                            exercise_id=exercise["id"],
                            parameters=parameters,
                            results=results,
                            submission_id=state["submission_id"],
                            round_number=current_round,
                        )
                        state["awaiting_next"] = True
                        st.session_state["last_color_attempt"] = attempt_number
                        st.rerun()
                    except Exception:
                        st.error(
                            "Der Versuch konnte nicht gespeichert werden."
                        )

        elif remaining_attempts == 0:
            st.success(
                "Alle drei Versuche wurden abgeschlossen."
            )

        last_attempt = st.session_state.get(
            "last_color_attempt"
        )

        if last_attempt is not None:
            if any(
                attempt["attempt_number"] == last_attempt
                for attempt in attempts
            ):
                st.success(
                    f"Versuch {last_attempt} von 3 "
                    "wurde erfolgreich gespeichert."
                )

        if attempts:
            st.divider()

            st.markdown("## Gespeicherte Versuche")

            for attempt in attempts:
                self.show_attempt_result(attempt, rgb_help)