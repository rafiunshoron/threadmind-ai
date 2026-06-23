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


def get_user_by_display_name(display_name: str):
    """Return a user by display name if it exists."""
    result = (
        supabase
        .table("users")
        .select("*")
        .eq("display_name", display_name)
        .execute()
    )

    if result.data:
        return result.data[0]

    return None


def get_or_create_user(display_name: str):
    """Get an existing user by name or create a new one."""
    existing_user = get_user_by_display_name(display_name)

    if existing_user:
        return existing_user

    return create_user(display_name)
