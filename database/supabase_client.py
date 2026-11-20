
import streamlit as st
from supabase import Client, create_client


class SupabaseClient:
    def __init__(self):
        self.url = st.secrets["SUPABASE_URL"]
        self.key = st.secrets["SUPABASE_KEY"]
        self.client: Client = create_client(self.url, self.key)

    def test_connection(self) -> bool:
        try:
            self.client.table("groups").select(
                "id"
            ).limit(1).execute()
            return True

        except Exception as error:
            print(f"Supabase connection error: {error}")
            return False
