"""
LLM configuration for Google Gemini.
"""

from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.config import settings


def get_llm(model_name: str = "gemini-1.5-pro", temperature: float = 0.7):
    """
    Get configured Gemini LLM instance.

    Args:
        model_name: Name of the Gemini model to use
        temperature: Temperature for response generation (0.0 to 1.0)

    Returns:
        Configured ChatGoogleGenerativeAI instance
    """
    llm = ChatGoogleGenerativeAI(
        model=model_name,
        google_api_key=settings.GEMINI_API_KEY,
        temperature=temperature,
        convert_system_message_to_human=True,  # Gemini doesn't support system messages
    )

    return llm


# Create default LLM instance
default_llm = None


def get_default_llm():
    """Get or create default LLM instance."""
    global default_llm
    if default_llm is None:
        default_llm = get_llm()
    return default_llm
