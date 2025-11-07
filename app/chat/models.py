"""
Chat models for conversations and messages.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Conversation(Base):
    """
    Conversation model to group related messages.
    Each user can have multiple conversations.
    """

    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(500), nullable=True)  # Optional conversation title
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship with messages
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Conversation {self.id} - User {self.user_id}>"


class Message(Base):
    """
    Message model to store individual chat messages.
    Messages belong to a conversation.
    """

    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    conversation_id = Column(
        Integer,
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False
    )
    content = Column(Text, nullable=False)
    is_user_message = Column(Boolean, default=True, nullable=False)  # True if from user, False if from bot
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship with conversation
    conversation = relationship("Conversation", back_populates="messages")

    def __repr__(self):
        msg_type = "User" if self.is_user_message else "Bot"
        return f"<Message {self.id} - {msg_type}>"
