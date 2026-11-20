
from database.supabase_client import SupabaseClient
from services.session_service import SessionService


class AttemptService:
    MAX_ATTEMPTS = 3

    def __init__(self):
        self.db = SupabaseClient().client
        self.session_service = SessionService()

    def get_attempts(self, group_id: str, exercise_id: str):
        session_id = self.session_service.get_current_session_id()

        if not session_id:
            return []

        response = (
            self.db.table("attempts")
            .select(
                "id, attempt_number, parameters, "
                "results, created_at"
            )
            .eq("group_id", group_id)
            .eq("exercise_id", exercise_id)
            .eq("session_id", session_id)
            .order("attempt_number")
            .execute()
        )

        return response.data

    def get_remaining_attempts(
        self, group_id: str, exercise_id: str
    ):
        attempts = self.get_attempts(group_id, exercise_id)
        return max(0, self.MAX_ATTEMPTS - len(attempts))

    def save_attempt(
        self,
        group_id: str,
        exercise_id: str,
        parameters: dict,
        results: dict
    ):
        if not isinstance(parameters, dict):
            raise ValueError("Ungültige Versuchsparameter.")

        if not isinstance(results, dict):
            raise ValueError("Ungültige Versuchsergebnisse.")

        response = (
            self.db.rpc(
                "save_exercise_attempt",
                {
                    "p_group_id": group_id,
                    "p_exercise_id": exercise_id,
                    "p_parameters": parameters,
                    "p_results": results
                }
            )
            .execute()
        )

        if response.data is None:
            raise RuntimeError(
                "Der Versuch konnte nicht gespeichert werden."
            )

        return int(response.data)
