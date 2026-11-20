
from datetime import datetime, timezone

import streamlit as st



class CountdownTimer:
    def render(self, ends_at: str):
        if not ends_at:
            return

        end_time = datetime.fromisoformat(
            ends_at.replace("Z", "+00:00")
        )

        @st.fragment(run_every="1s")
        def countdown():
            remaining = max(
                0,
                int(
                    (end_time - datetime.now(timezone.utc))
                    .total_seconds()
                )
            )

            minutes, seconds = divmod(remaining, 60)

            st.metric(
                "Verbleibende Zeit",
                f"{minutes:02d}:{seconds:02d}"
            )

            if remaining == 0:
                st.info("Die Übungszeit ist abgelaufen.")

        countdown()
