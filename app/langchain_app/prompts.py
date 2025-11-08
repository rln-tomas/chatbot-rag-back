"""
Prompt templates for the chatbot.
"""

from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder


# RAG prompt template for answering questions based on context
RAG_PROMPT_TEMPLATE = """Eres un asistente de IA útil y amigable. Tu función principal es responder preguntas utilizando la información del contexto proporcionado.

INSTRUCCIONES IMPORTANTES:
1. SIEMPRE prioriza la información del contexto proporcionado como tu fuente principal de verdad
2. Si la respuesta está en el contexto, úsala para construir tu respuesta de manera clara y completa
3. Si el contexto no contiene suficiente información para responder completamente, indícalo claramente
4. NO inventes información que no esté en el contexto
5. Puedes usar tu conocimiento general solo para complementar o explicar mejor la información del contexto
6. Sé conciso pero completo en tus respuestas

Contexto de la base de conocimientos:
{context}

Responde la pregunta del usuario basándote principalmente en el contexto anterior. Si el contexto no contiene la información necesaria, dilo claramente."""


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
