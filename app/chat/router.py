"""
Chat routes.
Endpoints for normal and streaming chat.
"""

from fastapi import APIRouter, Depends, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from langchain.schema import HumanMessage
from app.core.dependencies import get_db, get_current_user
from app.auth.models import User
from app.chat.schemas import (
    ChatRequest,
    ChatResponse,
    StreamChatRequest,
    ConversationResponse,
    ConversationListResponse
)
from app.chat.service import ChatService
from app.chat.streaming import stream_chat_response
from app.chat.repository import MessageRepository

router = APIRouter()


# Note: Chain will be initialized from langchain_app module
# This is a placeholder that will be replaced in main.py
_chat_chain = None


def set_chat_chain(chain):
    """Set the chat chain to be used by routes."""
    global _chat_chain
    _chat_chain = chain


@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Normal chat endpoint (non-streaming).

    Args:
        request: Chat request with message and optional conversation_id
        current_user: Authenticated user
        db: Database session

    Returns:
        Chat response with bot reply
    """
    if _chat_chain is None:
        from app.langchain_app.chains import get_rag_chain
        chain = get_rag_chain()
    else:
        chain = _chat_chain

    service = ChatService(db)

    return service.process_chat(
        user_id=current_user.id,
        message=request.message,
        chain=chain,
        conversation_id=request.conversation_id
    )


@router.post("/stream")
async def chat_stream(
    request: StreamChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Streaming chat endpoint using Server-Sent Events.

    Args:
        request: Chat request with message and optional conversation_id
        current_user: Authenticated user
        db: Database session

    Returns:
        StreamingResponse with SSE events
    """
    if _chat_chain is None:
        from app.langchain_app.chains import get_rag_chain
        chain = get_rag_chain()
    else:
        chain = _chat_chain

    service = ChatService(db)

    # Get or create conversation
    conversation = service.get_or_create_conversation(
        user_id=current_user.id,
        conversation_id=request.conversation_id
    )
    
    # Check if this is the first message in the conversation
    message_repo = MessageRepository(db)
    is_first_message = message_repo.count_by_conversation(conversation.id) == 0
    
    # If it's a new conversation without a title, generate one from the first message
    if is_first_message and not conversation.title:
        from app.chat.service import generate_conversation_title
        title = generate_conversation_title(request.message)
        service.conversation_repo.update_title(conversation.id, title)
        conversation.title = title  # Update local instance

    # Save user message
    user_msg = service.save_message(
        conversation_id=conversation.id,
        content=request.message,
        is_user_message=True
    )

    # Get conversation history
    history = service.get_conversation_history(conversation.id)

    # Create async generator for streaming
    async def generate():
        full_response = ""

        async for sse_message in stream_chat_response(chain, request.message, history):
            yield sse_message

            # Extract full_response if it's a completion event
            if '"type": "completion"' in sse_message:
                import json
                try:
                    data = json.loads(sse_message.replace("data: ", "").strip())
                    full_response = data.get("full_response", "")
                except:
                    pass

        # Save bot message after streaming completes
        if full_response:
            service.save_message(
                conversation_id=conversation.id,
                content=full_response,
                is_user_message=False
            )

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.get("/conversations", response_model=list[ConversationListResponse])
async def get_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all conversations for the authenticated user.

    Args:
        current_user: Authenticated user
        db: Database session

    Returns:
        List of conversations
    """
    service = ChatService(db)
    message_repo = MessageRepository(db)

    conversations = service.get_user_conversations(current_user.id)

    # Format response with message counts
    response = []
    for conv in conversations:
        count = message_repo.count_by_conversation(conv.id)
        response.append(
            ConversationListResponse(
                id=conv.id,
                user_id=conv.user_id,
                title=conv.title,
                created_at=conv.created_at,
                updated_at=conv.updated_at,
                message_count=count
            )
        )

    return response


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific conversation with all messages.

    Args:
        conversation_id: Conversation ID
        current_user: Authenticated user
        db: Database session

    Returns:
        Conversation with messages
    """
    service = ChatService(db)
    conversation = service.get_conversation_with_messages(conversation_id, current_user.id)

    return ConversationResponse.model_validate(conversation)


@router.delete("/conversations", status_code=status.HTTP_200_OK)
async def delete_all_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete all conversations and their associated messages for the authenticated user.
    
    This endpoint will:
    - Delete all conversations belonging to the user
    - Automatically delete all messages in those conversations (cascade delete)
    
    Args:
        current_user: Authenticated user
        db: Database session
        
    Returns:
        Success message with count of deleted conversations
    """
    service = ChatService(db)
    deleted_count = service.delete_all_conversations(current_user.id)
    
    return {
        "message": "All conversations deleted successfully",
        "conversations_deleted": deleted_count
    }
