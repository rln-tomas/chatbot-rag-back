"""
Embeddings configuration supporting multiple providers (Google Gemini, Ollama, and Jina AI).
"""

from typing import Optional
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_ollama import OllamaEmbeddings
from langchain_community.embeddings import JinaEmbeddings
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

    # Build client_kwargs with API key if configured (for Ollama Cloud)
    client_kwargs = {}
    if settings.OLLAMA_API_KEY:
        client_kwargs["headers"] = {
            "Authorization": f"Bearer {settings.OLLAMA_API_KEY}"
        }

    embeddings = OllamaEmbeddings(
        model=model,
        base_url=settings.OLLAMA_BASE_URL,
        client_kwargs=client_kwargs if client_kwargs else None,
    )

    return embeddings


def get_jina_embeddings(
    model_name: Optional[str] = None,
    dimensions: Optional[int] = None,
    task: Optional[str] = None
):
    """
    Get configured Jina AI embeddings instance.

    Args:
        model_name: Name of the Jina model (defaults to settings.JINA_EMBEDDING_MODEL)
        dimensions: Embedding dimensions (defaults to settings.JINA_EMBEDDING_DIMENSIONS)
        task: Task type for embeddings (defaults to settings.JINA_TASK)

    Returns:
        Configured JinaEmbeddings instance
    """
    if not settings.JINA_API_KEY:
        raise ValueError("JINA_API_KEY is not configured")

    model = model_name or settings.JINA_EMBEDDING_MODEL
    dims = dimensions or settings.JINA_EMBEDDING_DIMENSIONS
    task_type = task or settings.JINA_TASK

    embeddings = JinaEmbeddings(
        jina_api_key=settings.JINA_API_KEY,
        model_name=model,
        dimensions=dims,
        task=task_type,
    )

    return embeddings


def get_embeddings(
    provider: Optional[str] = None,
    model_name: Optional[str] = None
):
    """
    Get configured embeddings instance based on provider.

    Args:
        provider: Embeddings provider ('gemini', 'ollama', or 'jina').
                 Defaults to settings.EMBEDDING_PROVIDER, or settings.LLM_PROVIDER if not set
        model_name: Name of the model to use (provider-specific defaults apply)

    Returns:
        Configured embeddings instance

    Raises:
        ValueError: If provider is not supported
    """
    # Use EMBEDDING_PROVIDER if set, otherwise fall back to LLM_PROVIDER
    provider = provider or settings.EMBEDDING_PROVIDER or settings.LLM_PROVIDER
    provider = provider.lower()

    if provider == "gemini":
        return get_gemini_embeddings(
            model_name=model_name
        )
    elif provider == "ollama":
        return get_ollama_embeddings(
            model_name=model_name
        )
    elif provider == "jina":
        return get_jina_embeddings(
            model_name=model_name
        )
    else:
        raise ValueError(
            f"Unsupported embeddings provider: {provider}. "
            f"Supported providers: 'gemini', 'ollama', 'jina'"
        )


# Create default embeddings instance
default_embeddings = None


def get_default_embeddings():
    """Get or create default embeddings instance based on configured provider."""
    global default_embeddings
    if default_embeddings is None:
        default_embeddings = get_embeddings()
    return default_embeddings
