from langchain.agents import create_agent

from agent.model import get_model
from agent.tools import get_tools
from agent.memory import get_checkpointer


SYSTEM_PROMPT = """
You are ThreadMind AI, a memory-aware AI assistant.

Your main job is to help users with project planning, progress tracking,
budget calculations, and simple financial reports.

Important memory rules:
- Use only the current conversation memory.
- Do not claim to remember information from other conversations.
- If information is missing in the current conversation, say that you do not know.
- When calculation is needed, use the available tools.
- When a user asks to recalculate and some information was given earlier in the same conversation,
  use the current conversation memory to infer the missing values.
"""


model = get_model()
tools = get_tools()
checkpointer = get_checkpointer()

agent = create_agent(
    model=model,
    tools=tools,
    system_prompt=SYSTEM_PROMPT,
    checkpointer=checkpointer
)


def run_agent(user_message: str, conversation_id: str) -> str:
    """
    Run the ThreadMind AI agent for a user message inside one conversation.

    conversation_id is used as LangChain thread_id.
    Same conversation_id means same memory.
    Different conversation_id means isolated memory.
    """

    config = {
        "configurable": {
            "thread_id": conversation_id
        }
    }

    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": user_message
                }
            ]
        },
        config=config
    )

    final_message = result["messages"][-1]
    return final_message.content
