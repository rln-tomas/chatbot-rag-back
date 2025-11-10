"""
Embeddings configuration supporting multiple providers (Google Gemini and Ollama).
"""

from typing import Optional
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_ollama import OllamaEmbeddings
from app.core.config import settings


def get_gemini_embeddings(model_name: Optional[str] = None):
    """
    Get configured Google embeddings instance.

    Args:
        model_name: Name of the embedding model (defaults to settings.GEMINI_EMBEDDING_MODEL)

    Returns:
        Configured GoogleGenerativeAIEmbeddings instance
    """
    if not settings.GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not configured")
    
    model = model_name or settings.GEMINI_EMBEDDING_MODEL
    
    embeddings = GoogleGenerativeAIEmbeddings(
        model=model,
        google_api_key=settings.GEMINI_API_KEY
    )

    return embeddings


def get_ollama_embeddings(model_name: Optional[str] = None):
    """
    Get configured Ollama embeddings instance.

    Args:
        model_name: Name of the Ollama embedding model (defaults to settings.OLLAMA_EMBEDDING_MODEL)

    Returns:
        Configured OllamaEmbeddings instance
    """
    model = model_name or settings.OLLAMA_EMBEDDING_MODEL
    
    # Build headers with API key if configured (for Ollama Cloud)
    headers = {}
    if settings.OLLAMA_API_KEY:
        headers["Authorization"] = f"Bearer {settings.OLLAMA_API_KEY}"
    
    embeddings = OllamaEmbeddings(
        model=model,
        base_url=settings.OLLAMA_BASE_URL,
        headers=headers if headers else None,
    )

    return embeddings


def get_embeddings(
    provider: Optional[str] = None,
    model_name: Optional[str] = None
):
    """
    Get configured embeddings instance based on provider.

    Args:
        provider: Embeddings provider ('gemini' or 'ollama'). Defaults to settings.LLM_PROVIDER
        model_name: Name of the model to use (provider-specific defaults apply)

    Returns:
        Configured embeddings instance

    Raises:
        ValueError: If provider is not supported
    """
    provider = provider or settings.LLM_PROVIDER.lower()

    if provider == "gemini":
        return get_gemini_embeddings(
            model_name=model_name
        )
    elif provider == "ollama":
        return get_ollama_embeddings(
            model_name=model_name
        )
    else:
        raise ValueError(
            f"Unsupported embeddings provider: {provider}. "
            f"Supported providers: 'gemini', 'ollama'"
        )


# Create default embeddings instance
default_embeddings = None


def get_default_embeddings():
    """Get or create default embeddings instance based on configured provider."""
    global default_embeddings
    if default_embeddings is None:
        default_embeddings = get_embeddings()
    return default_embeddings
