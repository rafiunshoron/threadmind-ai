from database.supabase_client import get_supabase_client


supabase = get_supabase_client()


def create_user(display_name: str):
    """Create a new simulated user."""
    result = (
        supabase
        .table("users")
        .insert({"display_name": display_name})
        .execute()
    )

    return result.data[0]


def get_all_users():
    """Return all users."""
    result = (
        supabase
        .table("users")
        .select("*")
        .order("created_at", desc=False)
        .execute()
    )

    return result.data
