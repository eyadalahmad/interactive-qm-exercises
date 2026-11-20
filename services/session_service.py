
from database.supabase_client import SupabaseClient


class SessionService:
    def __init__(self):
        self.db = SupabaseClient().client

    def get_current_session_id(self):
        response = (
            self.db.table("settings")
            .select("value")
            .eq("key", "current_session_id")
            .limit(1)
            .execute()
        )

        if not response.data:
            return None

        return response.data[0]["value"]
