"""
Prompt templates for the chatbot.
"""

from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder


# RAG prompt template for answering questions based on context
RAG_PROMPT_TEMPLATE = """You are a helpful AI assistant. Use the following pieces of context to answer the user's question.
If you don't know the answer based on the context, just say that you don't know, don't try to make up an answer.

Context:
{context}

Answer the question based on the context above. Be concise and helpful."""


def get_rag_prompt():
    """
    Get RAG prompt template with conversation history.

    Returns:
        ChatPromptTemplate with context, history, and question placeholders
    """
    prompt = ChatPromptTemplate.from_messages([
        ("system", RAG_PROMPT_TEMPLATE),
        MessagesPlaceholder(variable_name="messages"),
    ])

    return prompt


# Simple chat prompt without RAG
CHAT_PROMPT_TEMPLATE = """You are a helpful AI assistant. Answer the user's questions in a friendly and informative way."""


def get_chat_prompt():
    """
    Get simple chat prompt template with conversation history.

    Returns:
        ChatPromptTemplate with history and question placeholders
    """
    prompt = ChatPromptTemplate.from_messages([
        ("system", CHAT_PROMPT_TEMPLATE),
        MessagesPlaceholder(variable_name="messages"),
    ])

    return prompt
