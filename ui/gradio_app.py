import gradio as gr

from agent.agent_service import run_agent
from database.users import get_or_create_user
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


def format_conversation_choices(conversations):
    return [(conversation["title"], conversation["conversation_id"]) for conversation in conversations]


def get_status(user=None, conversation=None):
    if not user:
        return "Enter your name to start."

    if not conversation:
        return f"User: {user['display_name']} | No conversation selected."

    return (
        f"User: {user['display_name']} | "
        f"Conversation: {conversation['title']} | "
        f"conversation_id/thread_id: {conversation['conversation_id']}"
    )


def start_user_session(display_name):
    if not display_name or not display_name.strip():
        return None, gr.Dropdown(choices=[], value=None), [], "Please enter your name."

    user = get_or_create_user(display_name.strip())
    conversations = get_conversations_by_user(user["user_id"])

    if not conversations:
        return (
            user,
            gr.Dropdown(choices=[], value=None),
            [],
            get_status(user)
        )

    first_conversation = conversations[0]
    messages = get_messages_by_conversation(first_conversation["conversation_id"])

    return (
        user,
        gr.Dropdown(
            choices=format_conversation_choices(conversations),
            value=first_conversation["conversation_id"]
        ),
        format_messages_for_gradio(messages),
        get_status(user, first_conversation)
    )


def on_conversation_change(conversation_id, user):
    if not user:
        return [], "Enter your name to start."

    if not conversation_id:
        return [], get_status(user)

    conversation = get_conversation_by_id(conversation_id)
    messages = get_messages_by_conversation(conversation_id)

    return format_messages_for_gradio(messages), get_status(user, conversation)


def on_new_chat(user):
    if not user:
        return gr.Dropdown(choices=[], value=None), [], "Enter your name first."

    conversation = create_conversation(
        user_id=user["user_id"],
        title="New Chat"
    )

    conversations = get_conversations_by_user(user["user_id"])

    return (
        gr.Dropdown(
            choices=format_conversation_choices(conversations),
            value=conversation["conversation_id"]
        ),
        [],
        get_status(user, conversation)
    )


def respond(user_message, chat_history, user, conversation_id):
    if not user_message:
        return "", chat_history, gr.Dropdown(), "No message sent."

    if not user:
        return "", chat_history, gr.Dropdown(), "Enter your name first."

    if chat_history is None:
        chat_history = []

    if not conversation_id:
        conversation = create_conversation(
            user_id=user["user_id"],
            title=generate_title_from_message(user_message)
        )
        conversation_id = conversation["conversation_id"]
    else:
        conversation = get_conversation_by_id(conversation_id)

    existing_messages = get_messages_by_conversation(conversation_id)

    if conversation["title"] == "New Chat" and len(existing_messages) == 0:
        title = generate_title_from_message(user_message)
        conversation = update_conversation_title(conversation_id, title)

    save_message(
        conversation_id=conversation_id,
        user_id=user["user_id"],
        role="user",
        content=user_message
    )

    assistant_response = run_agent(
        user_message=user_message,
        conversation_id=conversation_id
    )

    save_message(
        conversation_id=conversation_id,
        user_id=user["user_id"],
        role="assistant",
        content=assistant_response
    )

    messages = get_messages_by_conversation(conversation_id)
    conversations = get_conversations_by_user(user["user_id"])

    return (
        "",
        format_messages_for_gradio(messages),
        gr.Dropdown(
            choices=format_conversation_choices(conversations),
            value=conversation_id
        ),
        get_status(user, conversation)
    )


def build_app():
    with gr.Blocks(title="ThreadMind AI") as demo:
        gr.Markdown("# ThreadMind AI")
        gr.Markdown(
            "Resume-ready AI engineering demo: multi-user, multi-conversation memory assistant. "
            "Enter your name to start. Supabase stores visible messages. "
            "LangChain uses conversation_id as thread_id."
        )

        current_user = gr.State(value=None)

        with gr.Row():
            name_input = gr.Textbox(
                label="Enter Your Name",
                placeholder="Example: Shoron"
            )
            start_button = gr.Button("Start")

        with gr.Row():
            conversation_dropdown = gr.Dropdown(
                label="Conversation",
                choices=[],
                value=None
            )
            new_chat_button = gr.Button("New Chat")

        status_box = gr.Textbox(
            label="Current Session",
            interactive=False,
            value="Enter your name to start."
        )

        chatbot = gr.Chatbot(label="ThreadMind Chat")

        user_input = gr.Textbox(
            label="Message",
            placeholder="Type your message here..."
        )

        send_button = gr.Button("Send")

        start_button.click(
            fn=start_user_session,
            inputs=[name_input],
            outputs=[current_user, conversation_dropdown, chatbot, status_box]
        )

        conversation_dropdown.change(
            fn=on_conversation_change,
            inputs=[conversation_dropdown, current_user],
            outputs=[chatbot, status_box]
        )

        new_chat_button.click(
            fn=on_new_chat,
            inputs=[current_user],
            outputs=[conversation_dropdown, chatbot, status_box]
        )

        send_button.click(
            fn=respond,
            inputs=[user_input, chatbot, current_user, conversation_dropdown],
            outputs=[user_input, chatbot, conversation_dropdown, status_box]
        )

        user_input.submit(
            fn=respond,
            inputs=[user_input, chatbot, current_user, conversation_dropdown],
            outputs=[user_input, chatbot, conversation_dropdown, status_box]
        )

    return demo
