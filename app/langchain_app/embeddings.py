"""
Embeddings configuration for Google Generative AI.
"""

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from app.core.config import settings


def get_embeddings(model_name: str = "models/embedding-001"):
    """
    Get configured Google embeddings instance.

    Args:
        model_name: Name of the embedding model

    Returns:
        Configured GoogleGenerativeAIEmbeddings instance
    """
    embeddings = GoogleGenerativeAIEmbeddings(
        model=model_name,
        google_api_key=settings.GEMINI_API_KEY
    )

    return embeddings


# Create default embeddings instance
default_embeddings = None


def get_default_embeddings():
    """Get or create default embeddings instance."""
    global default_embeddings
    if default_embeddings is None:
        default_embeddings = get_embeddings()
    return default_embeddings
