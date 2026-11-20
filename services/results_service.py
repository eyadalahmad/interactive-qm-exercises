
from database.supabase_client import SupabaseClient
from services.group_service import GroupService
from services.session_service import SessionService


class ResultsService:
    def __init__(self):
        self.db = SupabaseClient().client
        self.group_service = GroupService()
        self.session_service = SessionService()

    def get_results(self, exercise_id: str):
        session_id = self.session_service.get_current_session_id()

        if not session_id:
            return []

        groups = self.group_service.get_groups()

        response = (
            self.db.table("attempts")
            .select(
                "id, group_id, attempt_number, "
                "parameters, results, created_at"
            )
            .eq("exercise_id", exercise_id)
            .eq("session_id", session_id)
            .order("attempt_number")
            .execute()
        )

        attempts = response.data or []

        results_by_group = []

        for group in groups:
            group_attempts = [
                attempt
                for attempt in attempts
                if attempt["group_id"] == group["id"]
            ]

            results_by_group.append({
                "group_id": group["id"],
                "group_name": group["name"],
                "attempts": group_attempts,
            })

        return results_by_group
