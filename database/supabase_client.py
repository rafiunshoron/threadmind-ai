import os
from dotenv import load_dotenv
from supabase import create_client, Client


load_dotenv()


def get_supabase_client() -> Client:
    """Create and return the Supabase client."""
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")

    if not supabase_url:
        raise ValueError("SUPABASE_URL is missing. Please add it to your .env file.")

    if not supabase_key:
        raise ValueError("SUPABASE_KEY is missing. Please add it to your .env file.")

    return create_client(supabase_url, supabase_key)
