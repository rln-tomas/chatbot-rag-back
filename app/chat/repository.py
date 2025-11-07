"""
Chat repository for database operations.
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.chat.models import Conversation, Message


class ConversationRepository:
    """Repository for Conversation database operations."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, user_id: int, title: Optional[str] = None) -> Conversation:
        """Create a new conversation."""
        conversation = Conversation(user_id=user_id, title=title)
        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)
        return conversation

    def get_by_id(self, conversation_id: int, user_id: int) -> Optional[Conversation]:
        """Get conversation by ID for specific user."""
        return self.db.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        ).first()

    def get_all_by_user(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 50
    ) -> List[Conversation]:
        """Get all conversations for a user."""
        return self.db.query(Conversation).filter(
            Conversation.user_id == user_id
        ).order_by(Conversation.updated_at.desc()).offset(skip).limit(limit).all()

    def delete(self, conversation_id: int, user_id: int) -> bool:
        """Delete a conversation."""
        conversation = self.get_by_id(conversation_id, user_id)
        if conversation:
            self.db.delete(conversation)
            self.db.commit()
            return True
        return False


class MessageRepository:
    """Repository for Message database operations."""

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        conversation_id: int,
        content: str,
        is_user_message: bool
    ) -> Message:
        """Create a new message."""
        message = Message(
            conversation_id=conversation_id,
            content=content,
            is_user_message=is_user_message
        )
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message

    def get_by_conversation(
        self,
        conversation_id: int,
        limit: int = 100
    ) -> List[Message]:
        """Get all messages for a conversation."""
        return self.db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at.asc()).limit(limit).all()

    def get_conversation_history(
        self,
        conversation_id: int,
        limit: int = 10
    ) -> List[Message]:
        """Get recent message history for context."""
        return self.db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at.desc()).limit(limit).all()

    def count_by_conversation(self, conversation_id: int) -> int:
        """Count messages in a conversation."""
        return self.db.query(func.count(Message.id)).filter(
            Message.conversation_id == conversation_id
        ).scalar()
