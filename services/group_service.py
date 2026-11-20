
import secrets
import string

from database.supabase_client import SupabaseClient
from services.admin_auth import AdminAuth


class GroupService:
    def __init__(self):
        self.db = SupabaseClient().client

    @staticmethod
    def require_admin():
        if not AdminAuth().is_authenticated():
            raise PermissionError("Zugriff verweigert.")

    def get_groups(self):
        self.require_admin()
        response = (
            self.db.table("groups")
            .select("id, name, access_code")
            .order("name")
            .execute()
        )
        return response.data

    def create_group(self, name: str):
        self.require_admin()
        if not name.strip():
            raise ValueError("Gruppenname darf nicht leer sein.")

        alphabet = string.ascii_uppercase + string.digits

        for _ in range(5):
            code = "".join(
                secrets.choice(alphabet) for _ in range(8)
            )

            try:
                response = (
                    self.db.table("groups")
                    .insert({
                        "name": name.strip(),
                        "access_code": code
                    })
                    .execute()
                )
                return response.data[0]

            except Exception as error:
                if getattr(error, "code", None) == "23505":
                    raise ValueError(
                        "Gruppenname oder Gruppencode bereits vorhanden."
                    ) from error
                raise

        raise RuntimeError("Gruppencode konnte nicht erstellt werden.")


    def delete_group(self, group_id: str):
        self.require_admin()
        self.db.table("groups").delete().eq(
            "id", group_id
        ).execute()



    def authenticate_group(self, access_code: str):
        code = access_code.strip().upper()

        if not code:
            return None

        response = (
            self.db.table("groups")
            .select("id, name")
            .eq("access_code", code)
            .limit(1)
            .execute()
        )

        return response.data[0] if response.data else None
