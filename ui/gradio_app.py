import gradio as gr

from agent.agent_service import run_agent


DEFAULT_CONVERSATION_ID = "default_conversation"


def respond(user_message, chat_history, conversation_id):
    """
    Handle one user message from the Gradio UI.
    """

    if not user_message:
        return "", chat_history

    if chat_history is None:
        chat_history = []

    if not conversation_id:
        conversation_id = DEFAULT_CONVERSATION_ID

    assistant_response = run_agent(
        user_message=user_message,
        conversation_id=conversation_id
    )

    chat_history.append({"role": "user", "content": user_message})
    chat_history.append({"role": "assistant", "content": assistant_response})

    return "", chat_history


def build_app():
    """
    Build and return the Gradio UI for ThreadMind AI.
    """

    with gr.Blocks(title="ThreadMind AI") as demo:
        gr.Markdown("# ThreadMind AI")
        gr.Markdown(
            "A memory-based multi-conversation AI assistant. "
            "For now, this version uses LangChain InMemorySaver only."
        )

        conversation_id = gr.Textbox(
            label="Conversation ID",
            value=DEFAULT_CONVERSATION_ID,
            placeholder="Example: conversation_a",
            interactive=True
        )

        chatbot = gr.Chatbot(
            label="ThreadMind Chat"
        )

        user_input = gr.Textbox(
            label="Message",
            placeholder="Type your message here..."
        )

        send_button = gr.Button("Send")

        send_button.click(
            fn=respond,
            inputs=[user_input, chatbot, conversation_id],
            outputs=[user_input, chatbot]
        )

        user_input.submit(
            fn=respond,
            inputs=[user_input, chatbot, conversation_id],
            outputs=[user_input, chatbot]
        )

    return demo
