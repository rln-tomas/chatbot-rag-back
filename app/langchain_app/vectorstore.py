"""
Pinecone vector store configuration.
"""

from pinecone import Pinecone, ServerlessSpec
from langchain_pinecone import PineconeVectorStore
from app.core.config import settings
from app.langchain_app.embeddings import get_default_embeddings


def init_pinecone():
    """
    Initialize Pinecone client and ensure index exists.

    Returns:
        Pinecone client instance
    """
    pc = Pinecone(api_key=settings.PINECONE_API_KEY)

    # Check if index exists, create if not
    index_name = settings.PINECONE_INDEX_NAME

    if index_name not in pc.list_indexes().names():
        # Create index with appropriate dimensions for the embedding model
        # Dimensions depend on your EMBEDDING_PROVIDER:
        # - Gemini (models/embedding-001): 768 dimensions
        # - Jina (jina-embeddings-v3): 1024 dimensions (default)
        # - Ollama (nomic-embed-text): 768 dimensions
        # Make sure this matches your embedding model!
        pc.create_index(
            name=index_name,
            dimension=1024,  # Updated to 1024 for Jina embeddings
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1"
            )
        )

    return pc


def get_vectorstore(namespace: str = "default"):
    """
    Get Pinecone vector store instance.

    Args:
        namespace: Namespace for the vector store (optional)

    Returns:
        PineconeVectorStore instance
    """
    # Initialize Pinecone
    pc = init_pinecone()

    # Get embeddings
    embeddings = get_default_embeddings()

    # Create vector store
    vectorstore = PineconeVectorStore(
        index_name=settings.PINECONE_INDEX_NAME,
        embedding=embeddings,
        namespace=namespace
    )

    return vectorstore


def get_retriever(namespace: str = "default", k: int = 4):
    """
    Get retriever from vector store.

    Args:
        namespace: Namespace for the vector store
        k: Number of documents to retrieve

    Returns:
        Retriever instance
    """
    vectorstore = get_vectorstore(namespace)

    retriever = vectorstore.as_retriever(
        search_kwargs={"k": k}
    )

    return retriever


# Global vector store instance
_vectorstore = None


def get_default_vectorstore():
    """Get or create default vector store instance."""
    global _vectorstore
    if _vectorstore is None:
        _vectorstore = get_vectorstore()
    return _vectorstore
