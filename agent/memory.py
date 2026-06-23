from langgraph.checkpoint.memory import InMemorySaver


def get_checkpointer():
    """Create and return the in-memory checkpointer for ThreadMind AI."""
    return InMemorySaver()
