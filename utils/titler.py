def generate_title_from_message(message: str) -> str:
    """Generate a simple conversation title from the first user message."""
    if not message:
        return "New Chat"

    title = message.strip()

    if len(title) > 40:
        title = title[:40].rstrip() + "..."

    return title
