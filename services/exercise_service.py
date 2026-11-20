
from datetime import datetime, timedelta, timezone

from database.supabase_client import SupabaseClient


class ExerciseService:
    def __init__(self):
        self.db = SupabaseClient().client

    def get_exercises(self):
        response = (
            self.db.table("exercises")
            .select(
                "id, name, status, duration_minutes, "
                "started_at, ends_at"
            )
            .order("name")
            .execute()
        )

        return response.data

    def start_exercise(self, exercise_id: str):
        exercise = (
            self.db.table("exercises")
            .select("status, duration_minutes")
            .eq("id", exercise_id)
            .single()
            .execute()
        ).data

        if exercise["status"] != "locked":
            raise ValueError(
                "Die Übung kann nicht gestartet werden."
            )

        started_at = datetime.now(timezone.utc)
        ends_at = started_at + timedelta(
            minutes=exercise["duration_minutes"]
        )

        response = (
            self.db.table("exercises")
            .update({
                "status": "active",
                "started_at": started_at.isoformat(),
                "ends_at": ends_at.isoformat()
            })
            .eq("id", exercise_id)
            .eq("status", "locked")
            .execute()
        )

        if not response.data:
            raise ValueError(
                "Die Übung wurde bereits gestartet."
            )

        return response.data[0]

    def end_exercise(self, exercise_id: str):
        response = (
            self.db.table("exercises")
            .update({"status": "finished"})
            .eq("id", exercise_id)
            .eq("status", "active")
            .execute()
        )

        if not response.data:
            raise ValueError(
                "Die Übung ist nicht aktiv."
            )

        return response.data[0]


    def finish_expired_exercises(self):
        now = datetime.now(timezone.utc).isoformat()

        response = (
            self.db.table("exercises")
            .update({"status": "finished"})
            .eq("status", "active")
            .lte("ends_at", now)
            .execute()
        )

        return response.data



    def reset_exercises(self):
        response = (
            self.db.rpc("prepare_new_session", {})
            .execute()
        )

        if not response.data:
            raise RuntimeError(
                "Die neue Sitzung konnte nicht vorbereitet werden."
            )

        return response.data


    def get_target_color(self):
        response = (
            self.db.table("settings")
            .select("value")
            .eq("key", "color_target")
            .limit(1)
            .execute()
        )

        if not response.data:
            return "#A080C0"

        return response.data[0]["value"]

    def save_target_color(self, color: str):
        import re

        if not re.fullmatch(r"#[0-9A-Fa-f]{6}", color):
            raise ValueError("Ungültiger Farbwert.")

        exercise = next(
            (
                item for item in self.get_exercises()
                if item["name"] == "Farbmischung"
            ),
            None
        )

        if exercise is None:
            raise ValueError("Übung nicht gefunden.")

        if exercise["status"] != "locked":
            raise ValueError(
                "Die Zielfarbe kann nur vor dem Start geändert werden."
            )

        self.db.table("settings").upsert(
            {
                "key": "color_target",
                "value": color.upper()
            },
            on_conflict="key"
        ).execute()
