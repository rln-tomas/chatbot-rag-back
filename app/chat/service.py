"""
Chat service with business logic.
"""

from typing import Optional, List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from langchain.schema import HumanMessage, AIMessage, BaseMessage
from app.chat.repository import ConversationRepository, MessageRepository
from app.chat.models import Conversation, Message
from app.chat.schemas import ChatResponse, MessageResponse


def generate_conversation_title(message: str, max_length: int = 50) -> str:
    """
    Generate a conversation title from the first user message.
    
    Args:
        message: The first user message
        max_length: Maximum length for the title
        
    Returns:
        Generated title
    """
    # Clean and truncate the message
    title = message.strip()
    
    # Remove newlines and extra spaces
    title = ' '.join(title.split())
    
    # Truncate to max_length and add ellipsis if needed
    if len(title) > max_length:
        title = title[:max_length - 3] + "..."
    
    return title or "Nueva conversación"


class ChatService:
    """Service for chat operations."""

    def __init__(self, db: Session):
        self.conversation_repo = ConversationRepository(db)
        self.message_repo = MessageRepository(db)
        self.db = db

    def get_or_create_conversation(
        self,
        user_id: int,
        conversation_id: Optional[int] = None
    ) -> Conversation:
        """
        Get existing conversation or create a new one.

        Args:
            user_id: User ID
            conversation_id: Optional conversation ID

        Returns:
            Conversation instance

        Raises:
            HTTPException: If conversation not found or doesn't belong to user
        """
        if conversation_id:
            conversation = self.conversation_repo.get_by_id(conversation_id, user_id)
            if not conversation:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Conversation not found"
                )
            return conversation
        else:
            # Create new conversation
            return self.conversation_repo.create(user_id)

    def save_message(
        self,
        conversation_id: int,
        content: str,
        is_user_message: bool
    ) -> Message:
        """
        Save a message to the database.

        Args:
            conversation_id: Conversation ID
            content: Message content
            is_user_message: Whether message is from user or bot

        Returns:
            Created message
        """
        return self.message_repo.create(
            conversation_id=conversation_id,
            content=content,
            is_user_message=is_user_message
        )

    def get_conversation_history(
        self,
        conversation_id: int,
        limit: int = 10
    ) -> List[BaseMessage]:
        """
        Get conversation history formatted for LangChain.

        Args:
            conversation_id: Conversation ID
            limit: Maximum number of messages to retrieve

        Returns:
            List of LangChain messages
        """
        messages = self.message_repo.get_conversation_history(conversation_id, limit)

        # Convert to LangChain messages (reverse to get chronological order)
        langchain_messages = []
        for msg in reversed(messages):
            if msg.is_user_message:
                langchain_messages.append(HumanMessage(content=msg.content))
            else:
                langchain_messages.append(AIMessage(content=msg.content))

        return langchain_messages

    def process_chat(
        self,
        user_id: int,
        message: str,
        chain,
        conversation_id: Optional[int] = None
    ) -> ChatResponse:
        """
        Process a chat message (non-streaming).

        Args:
            user_id: User ID
            message: User message
            chain: LangChain chain
            conversation_id: Optional conversation ID

        Returns:
            Chat response with bot reply
        """
        # Get or create conversation
        conversation = self.get_or_create_conversation(user_id, conversation_id)
        
        # Check if this is the first message in the conversation
        is_first_message = self.message_repo.count_by_conversation(conversation.id) == 0
        
        # If it's a new conversation without a title, generate one from the first message
        if is_first_message and not conversation.title:
            title = generate_conversation_title(message)
            self.conversation_repo.update_title(conversation.id, title)
            conversation.title = title  # Update local instance

        # Get conversation history for context
        history = self.get_conversation_history(conversation.id)

        # Save user message
        user_msg = self.save_message(
            conversation_id=conversation.id,
            content=message,
            is_user_message=True
        )

        # Generate bot response
        full_history = history + [HumanMessage(content=message)]

        try:
            response = chain.invoke({"messages": full_history})

            # Extract content from response
            # RAG chain with StrOutputParser returns string directly
            if isinstance(response, str):
                bot_response = response
            elif hasattr(response, 'content'):
                bot_response = response.content
            elif isinstance(response, dict) and 'content' in response:
                bot_response = response['content']
            else:
                bot_response = str(response)

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error generating response: {str(e)}"
            )

        # Save bot message
        bot_msg = self.save_message(
            conversation_id=conversation.id,
            content=bot_response,
            is_user_message=False
        )

        return ChatResponse(
            conversation_id=conversation.id,
            user_message=MessageResponse.model_validate(user_msg),
            bot_message=MessageResponse.model_validate(bot_msg),
            response=bot_response
        )

    def get_conversation_with_messages(
        self,
        conversation_id: int,
        user_id: int
    ) -> Conversation:
        """
        Get conversation with all messages.

        Args:
            conversation_id: Conversation ID
            user_id: User ID

        Returns:
            Conversation with messages

        Raises:
            HTTPException: If not found
        """
        conversation = self.conversation_repo.get_by_id(conversation_id, user_id)

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )

        return conversation

    def get_user_conversations(self, user_id: int) -> List[Conversation]:
        """
        Get all conversations for a user.

        Args:
            user_id: User ID

        Returns:
            List of conversations
        """
        return self.conversation_repo.get_all_by_user(user_id)

    def delete_all_conversations(self, user_id: int) -> int:
        """
        Delete all conversations and their messages for a user.
        Messages are deleted automatically due to cascade delete in the model.

        Args:
            user_id: User ID

        Returns:
            Number of conversations deleted
        """
        deleted_count = self.conversation_repo.delete_all_by_user(user_id)
        return deleted_count
