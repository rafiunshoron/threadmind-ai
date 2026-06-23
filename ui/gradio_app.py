import gradio as gr

from agent.agent_service import run_agent
from database.users import get_all_users, create_user
from database.conversations import (
    create_conversation,
    get_conversations_by_user,
    get_conversation_by_id,
    update_conversation_title,
)
from database.messages import (
    save_message,
    get_messages_by_conversation,
    format_messages_for_gradio,
)
from utils.titler import generate_title_from_message


def format_user_choices(users):
    """Convert user rows into Gradio dropdown choices."""
    return [(user["display_name"], user["user_id"]) for user in users]


def format_conversation_choices(conversations):
    """Convert conversation rows into Gradio dropdown choices."""
    return [(conversation["title"], conversation["conversation_id"]) for conversation in conversations]


def get_status(user_id=None, conversation=None):
    """Create a readable status message for the UI."""
    if not user_id:
        return "No user selected."

    if not conversation:
        return f"User ID: {user_id} | No conversation selected."

    return (
        f"Conversation: {conversation['title']} | "
        f"conversation_id/thread_id: {conversation['conversation_id']}"
    )


def load_users():
    """Load users for the user dropdown."""
    users = get_all_users()

    if not users:
        return gr.Dropdown(choices=[], value=None)

    return gr.Dropdown(choices=format_user_choices(users), value=users[0]["user_id"])


def on_create_user(display_name):
    """Create a new user from the UI and refresh the user dropdown."""
    if not display_name or not display_name.strip():
        return gr.Dropdown(), "Please enter a user name."

    user = create_user(display_name.strip())
    users = get_all_users()

    return (
        gr.Dropdown(
            choices=format_user_choices(users),
            value=user["user_id"]
        ),
        f"Created user: {user['display_name']}"
    )


def on_user_change(user_id):
    """When user changes, load that user's conversations."""
    if not user_id:
        return gr.Dropdown(choices=[], value=None), [], "No user selected."

    conversations = get_conversations_by_user(user_id)

    if not conversations:
        return gr.Dropdown(choices=[], value=None), [], get_status(user_id)

    first_conversation = conversations[0]
    messages = get_messages_by_conversation(first_conversation["conversation_id"])

    return (
        gr.Dropdown(
            choices=format_conversation_choices(conversations),
            value=first_conversation["conversation_id"]
        ),
        format_messages_for_gradio(messages),
        get_status(user_id, first_conversation)
    )


def on_conversation_change(conversation_id):
    """When conversation changes, load its visible messages."""
    if not conversation_id:
        return [], "No conversation selected."

    conversation = get_conversation_by_id(conversation_id)
    messages = get_messages_by_conversation(conversation_id)

    return format_messages_for_gradio(messages), get_status(
        conversation["user_id"],
        conversation
    )


def on_new_chat(user_id):
    """Create a new conversation for the selected user."""
    if not user_id:
        return gr.Dropdown(choices=[], value=None), [], "Please select a user first."

    conversation = create_conversation(
        user_id=user_id,
        title="New Chat"
    )

    conversations = get_conversations_by_user(user_id)

    return (
        gr.Dropdown(
            choices=format_conversation_choices(conversations),
            value=conversation["conversation_id"]
        ),
        [],
        get_status(user_id, conversation)
    )


def respond(user_message, chat_history, user_id, conversation_id):
    """
    Save visible messages in Supabase and run LangChain agent with conversation_id as thread_id.
    """

    if not user_message:
        return "", chat_history, gr.Dropdown(), "No message sent."

    if chat_history is None:
        chat_history = []

    if not user_id:
        return (
            "",
            chat_history + [{"role": "assistant", "content": "Please select a user first."}],
            gr.Dropdown(),
            "No user selected."
        )

    if not conversation_id:
        conversation = create_conversation(
            user_id=user_id,
            title=generate_title_from_message(user_message)
        )
        conversation_id = conversation["conversation_id"]
    else:
        conversation = get_conversation_by_id(conversation_id)

    existing_messages = get_messages_by_conversation(conversation_id)

    if conversation["title"] == "New Chat" and len(existing_messages) == 0:
        new_title = generate_title_from_message(user_message)
        conversation = update_conversation_title(conversation_id, new_title)

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
    conversations = get_conversations_by_user(user_id)

    return (
        "",
        format_messages_for_gradio(messages),
        gr.Dropdown(
            choices=format_conversation_choices(conversations),
            value=conversation_id
        ),
        get_status(user_id, conversation)
    )


def build_app():
    """Build and return the Gradio UI for ThreadMind AI."""

    with gr.Blocks(title="ThreadMind AI") as demo:
        gr.Markdown("# ThreadMind AI")
        gr.Markdown(
            "A multi-user, multi-conversation AI assistant. "
            "Supabase stores visible messages. "
            "LangChain uses conversation_id as thread_id for memory."
        )

        with gr.Row():
            user_name_input = gr.Textbox(
                label="Enter New User Name",
                placeholder="Example: Shoron"
            )

            create_user_button = gr.Button("Create User")

        with gr.Row():
            user_dropdown = gr.Dropdown(
                label="User",
                choices=[],
                value=None
            )

            conversation_dropdown = gr.Dropdown(
                label="Conversation",
                choices=[],
                value=None
            )

            new_chat_button = gr.Button("New Chat")

        status_box = gr.Textbox(
            label="Current Conversation",
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
            fn=load_users,
            inputs=[],
            outputs=[user_dropdown]
        )

        create_user_button.click(
            fn=on_create_user,
            inputs=[user_name_input],
            outputs=[user_dropdown, status_box]
        )

        user_dropdown.change(
            fn=on_user_change,
            inputs=[user_dropdown],
            outputs=[conversation_dropdown, chatbot, status_box]
        )

        conversation_dropdown.change(
            fn=on_conversation_change,
            inputs=[conversation_dropdown],
            outputs=[chatbot, status_box]
        )

        new_chat_button.click(
            fn=on_new_chat,
            inputs=[user_dropdown],
            outputs=[conversation_dropdown, chatbot, status_box]
        )

        send_button.click(
            fn=respond,
            inputs=[user_input, chatbot, user_dropdown, conversation_dropdown],
            outputs=[user_input, chatbot, conversation_dropdown, status_box]
        )

        user_input.submit(
            fn=respond,
            inputs=[user_input, chatbot, user_dropdown, conversation_dropdown],
            outputs=[user_input, chatbot, conversation_dropdown, status_box]
        )

    return demo
