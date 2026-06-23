import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq


load_dotenv()


def get_model():
    """Create and return the ChatGroq model used by ThreadMind AI."""
    groq_api_key = os.getenv("GROQ_API_KEY")

    if not groq_api_key:
        raise ValueError("GROQ_API_KEY is missing. Please add it to your .env file.")

    model = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0
    )

    return model
