"""
LangChain chains for RAG and chat.
"""

from langchain.schema.runnable import RunnablePassthrough, RunnableParallel
from langchain.schema.output_parser import StrOutputParser
from app.langchain_app.llm import get_default_llm
from app.langchain_app.prompts import get_rag_prompt, get_chat_prompt
from app.langchain_app.vectorstore import get_retriever


def get_rag_chain(k: int = 4):
    """
    Create RAG chain with vector store retrieval.

    Args:
        k: Number of documents to retrieve

    Returns:
        Configured RAG chain
    """
    llm = get_default_llm()
    prompt = get_rag_prompt()
    retriever = get_retriever(k=k)

    # Create RAG chain
    # The chain retrieves context and generates response
    chain = (
        RunnableParallel({
            "context": retriever,
            "messages": RunnablePassthrough()
        })
        | prompt
        | llm
        | StrOutputParser()
    )

    return chain


def get_chat_chain():
    """
    Create simple chat chain without RAG.

    Returns:
        Configured chat chain
    """
    llm = get_default_llm()
    prompt = get_chat_prompt()

    # Create simple chat chain
    chain = (
        prompt
        | llm
    )

    return chain


# Global chain instances
_rag_chain = None
_chat_chain = None


def get_default_rag_chain():
    """Get or create default RAG chain instance."""
    global _rag_chain
    if _rag_chain is None:
        _rag_chain = get_rag_chain()
    return _rag_chain


def get_default_chat_chain():
    """Get or create default chat chain instance."""
    global _chat_chain
    if _chat_chain is None:
        _chat_chain = get_chat_chain()
    return _chat_chain
