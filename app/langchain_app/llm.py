"""
LLM configuration supporting multiple providers (Google Gemini and Ollama).
"""

from typing import Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama
from app.core.config import settings


def get_gemini_llm(model_name: Optional[str] = None, temperature: float = 0.7):
    """
    Get configured Gemini LLM instance.

    Args:
        model_name: Name of the Gemini model to use (defaults to settings.GEMINI_MODEL)
        temperature: Temperature for response generation (0.0 to 1.0)

    Returns:
        Configured ChatGoogleGenerativeAI instance
    """
    if not settings.GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not configured")
    
    model = model_name or settings.GEMINI_MODEL
    
    llm = ChatGoogleGenerativeAI(
        model=model,
        google_api_key=settings.GEMINI_API_KEY,
        temperature=temperature,
        convert_system_message_to_human=True,  # Gemini doesn't support system messages
    )

    return llm


def get_ollama_llm(model_name: Optional[str] = None, temperature: float = 0.7):
    """
    Get configured Ollama LLM instance.

    Args:
        model_name: Name of the Ollama model to use (defaults to settings.OLLAMA_MODEL)
        temperature: Temperature for response generation (0.0 to 1.0)

    Returns:
        Configured ChatOllama instance
    """
    model = model_name or settings.OLLAMA_MODEL
    
    llm = ChatOllama(
        model=model,
        base_url=settings.OLLAMA_BASE_URL,
        temperature=temperature,
    )

    return llm


def get_llm(
    provider: Optional[str] = None,
    model_name: Optional[str] = None,
    temperature: float = 0.7
):
    """
    Get configured LLM instance based on provider.

    Args:
        provider: LLM provider ('gemini' or 'ollama'). Defaults to settings.LLM_PROVIDER
        model_name: Name of the model to use (provider-specific defaults apply)
        temperature: Temperature for response generation (0.0 to 1.0)

    Returns:
        Configured LLM instance

    Raises:
        ValueError: If provider is not supported
    """
    provider = provider or settings.LLM_PROVIDER.lower()

    if provider == "gemini":
        return get_gemini_llm(
            model_name=model_name,
            temperature=temperature
        )
    elif provider == "ollama":
        return get_ollama_llm(
            model_name=model_name,
            temperature=temperature
        )
    else:
        raise ValueError(
            f"Unsupported LLM provider: {provider}. "
            f"Supported providers: 'gemini', 'ollama'"
        )


# Create default LLM instance
default_llm = None


def get_default_llm():
    """Get or create default LLM instance based on configured provider."""
    global default_llm
    if default_llm is None:
        default_llm = get_llm()
    return default_llm
