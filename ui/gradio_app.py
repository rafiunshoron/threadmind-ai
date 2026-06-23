import gradio as gr

from agent.agent_service import run_agent
from database.users import get_all_users
from database.conversations import get_conversations_by_user
from database.messages import (
    save_message,
    get_messages_by_conversation,
    format_messages_for_gradio,
)


def get_demo_user_and_conversation():
    """
    Get the first user and the first conversation from Supabase.

    This is temporary for Stage 10.
    Later, the UI will support user selection and conversation switching.
    """
    users = get_all_users()

    if not users:
        raise ValueError("No users found in Supabase. Please create a user first.")

    user = users[0]
    conversations = get_conversations_by_user(user["user_id"])

    if not conversations:
        raise ValueError("No conversations found for this user. Please create a conversation first.")

    conversation = conversations[0]

    return user, conversation


def load_initial_chat():
    """
    Load existing visible messages from Supabase for the demo conversation.
    """
    user, conversation = get_demo_user_and_conversation()

    messages = get_messages_by_conversation(conversation["conversation_id"])
    chat_history = format_messages_for_gradio(messages)

    status = (
        f"User: {user['display_name']} | "
        f"Conversation: {conversation['title']} | "
        f"conversation_id/thread_id: {conversation['conversation_id']}"
    )

    return chat_history, status


def respond(user_message, chat_history):
    """
    Handle one user message.

    Flow:
    1. Get demo user and conversation from Supabase.
    2. Save user message in Supabase.
    3. Run LangChain agent using conversation_id as thread_id.
    4. Save assistant response in Supabase.
    5. Reload visible messages from Supabase.
    6. Return updated chat history to Gradio.
    """

    if not user_message:
        return "", chat_history

    user, conversation = get_demo_user_and_conversation()

    user_id = user["user_id"]
    conversation_id = conversation["conversation_id"]

    save_message(
        conversation_id=conversation_id,
        user_id=user_id,
        role="user",
        content=user_message
    )

    assistant_response = run_agent(
        user_message=user_message,
        conversation_id=conversation_id
    )

    save_message(
        conversation_id=conversation_id,
        user_id=user_id,
        role="assistant",
        content=assistant_response
    )

    messages = get_messages_by_conversation(conversation_id)
    updated_chat_history = format_messages_for_gradio(messages)

    return "", updated_chat_history


def build_app():
    """
    Build and return the Gradio UI for ThreadMind AI.
    """

    with gr.Blocks(title="ThreadMind AI") as demo:
        gr.Markdown("# ThreadMind AI")
        gr.Markdown(
            "A memory-based multi-conversation AI assistant. "
            "This version saves visible chat messages in Supabase "
            "and uses LangChain InMemorySaver for agent memory."
        )

        status_box = gr.Textbox(
            label="Current Supabase Conversation",
            interactive=False
        )

        chatbot = gr.Chatbot(
            label="ThreadMind Chat"
        )

        user_input = gr.Textbox(
            label="Message",
            placeholder="Type your message here..."
        )

        send_button = gr.Button("Send")

        demo.load(
            fn=load_initial_chat,
            inputs=[],
            outputs=[chatbot, status_box]
        )

        send_button.click(
            fn=respond,
            inputs=[user_input, chatbot],
            outputs=[user_input, chatbot]
        )

        user_input.submit(
            fn=respond,
            inputs=[user_input, chatbot],
            outputs=[user_input, chatbot]
        )

    return demo
