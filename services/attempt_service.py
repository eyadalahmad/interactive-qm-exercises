
from database.supabase_client import SupabaseClient
from services.session_service import SessionService


class AttemptService:
    MAX_ATTEMPTS = 3

    def __init__(self):
        self.db = SupabaseClient().client
        self.session_service = SessionService()

    def get_attempts(self, group_id: str, exercise_id: str, round_number: int = 1):
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
            .eq("round_number", round_number)
            .order("attempt_number")
            .execute()
        )

        return response.data

    def get_remaining_attempts(
        self, group_id: str, exercise_id: str, round_number: int = 1
    ):
        attempts = self.get_attempts(group_id, exercise_id, round_number)
        return max(0, self.MAX_ATTEMPTS - len(attempts))

    def save_attempt(
        self,
        group_id: str,
        exercise_id: str,
        parameters: dict,
        results: dict,
        submission_id: str | None = None,
        round_number: int = 1,
    ):
        if not isinstance(parameters, dict):
            raise ValueError("Ungültige Versuchsparameter.")

        if not isinstance(results, dict):
            raise ValueError("Ungültige Versuchsergebnisse.")

        payload = {
            "p_group_id": group_id,
            "p_exercise_id": exercise_id,
            "p_parameters": parameters,
            "p_results": results,
        }

        if submission_id is not None:
            payload["p_submission_id"] = submission_id
            payload["p_round_number"] = round_number
        elif round_number != 1:
            raise ValueError("Submission-ID fehlt.")

        response = (
            self.db.rpc("save_exercise_attempt", payload)
            .execute()
        )

        if response.data is None:
            raise RuntimeError(
                "Der Versuch konnte nicht gespeichert werden."
            )

        return int(response.data)
