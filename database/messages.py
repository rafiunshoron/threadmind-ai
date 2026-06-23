from database.supabase_client import get_supabase_client


supabase = get_supabase_client()


def save_message(conversation_id: str, user_id: str, role: str, content: str):
    """Save a visible chat message."""
    result = (
        supabase
        .table("messages")
        .insert({
            "conversation_id": conversation_id,
            "user_id": user_id,
            "role": role,
            "content": content
        })
        .execute()
    )

    return result.data[0]


def get_messages_by_conversation(conversation_id: str):
    """Return all visible messages for a specific conversation."""
    result = (
        supabase
        .table("messages")
        .select("*")
        .eq("conversation_id", conversation_id)
        .order("created_at", desc=False)
        .execute()
    )

    return result.data


def format_messages_for_gradio(messages):
    """Convert Supabase message rows into Gradio messages format."""
    return [
        {
            "role": message["role"],
            "content": message["content"]
        }
        for message in messages
    ]
