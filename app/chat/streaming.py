"""
Streaming utilities for Server-Sent Events (SSE) chat.
"""

import json
from typing import AsyncGenerator
from langchain.schema import BaseMessage, HumanMessage


async def stream_chat_response(
    chain,
    message: str,
    conversation_history: list[BaseMessage]
) -> AsyncGenerator[str, None]:
    """
    Stream chat response using Server-Sent Events.
    Works with both RAG and simple chat chains.

    Args:
        chain: LangChain chain to use for generation
        message: User message
        conversation_history: Previous conversation messages for context

    Yields:
        SSE-formatted chunks of the response
    """
    try:
        # Add user message to history
        full_history = conversation_history + [HumanMessage(content=message)]

        # Stream the response
        full_response = ""

        async for chunk in chain.astream({"messages": full_history}):
            # Extract content from chunk
            # The RAG chain with StrOutputParser returns strings directly
            if isinstance(chunk, str):
                content = chunk
            elif hasattr(chunk, 'content'):
                content = chunk.content
            elif isinstance(chunk, dict) and 'content' in chunk:
                content = chunk['content']
            else:
                content = str(chunk)

            if content:
                full_response += content

                # Format as SSE
                data = json.dumps({
                    "type": "token",
                    "content": content
                })
                yield f"data: {data}\n\n"

        # Send completion event with full response
        completion_data = json.dumps({
            "type": "completion",
            "full_response": full_response
        })
        yield f"data: {completion_data}\n\n"

    except Exception as e:
        # Send error event
        error_data = json.dumps({
            "type": "error",
            "message": str(e)
        })
        yield f"data: {error_data}\n\n"


def format_sse_message(event_type: str, data: dict) -> str:
    """
    Format a message for Server-Sent Events.

    Args:
        event_type: Type of event (token, completion, error)
        data: Data to send

    Returns:
        SSE-formatted string
    """
    json_data = json.dumps({
        "type": event_type,
        **data
    })
    return f"data: {json_data}\n\n"
