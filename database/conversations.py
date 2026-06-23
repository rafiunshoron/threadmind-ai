from database.supabase_client import get_supabase_client


supabase = get_supabase_client()


def create_conversation(user_id: str, title: str = "New Chat"):
    """Create a new conversation for a user."""
    result = (
        supabase
        .table("conversations")
        .insert({
            "user_id": user_id,
            "title": title
        })
        .execute()
    )

    return result.data[0]


def get_conversations_by_user(user_id: str):
    """Return all conversations for a specific user."""
    result = (
        supabase
        .table("conversations")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=False)
        .execute()
    )

    return result.data


def get_conversation_by_id(conversation_id: str):
    """Return one conversation by conversation_id."""
    result = (
        supabase
        .table("conversations")
        .select("*")
        .eq("conversation_id", conversation_id)
        .single()
        .execute()
    )

    return result.data


def get_conversation_by_id(conversation_id: str):
    """Return one conversation by conversation_id."""
    result = (
        supabase
        .table("conversations")
        .select("*")
        .eq("conversation_id", conversation_id)
        .single()
        .execute()
    )

    return result.data
