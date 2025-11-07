"""
Configuration management models.
Defines the Configuration model for URL scraping management.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class ScrapingStatus(str, enum.Enum):
    """Enum for scraping status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Configuration(Base):
    """
    Configuration model for managing URLs to scrape.
    Each user can have multiple configurations, but only one can be processing at a time.
    """

    __tablename__ = "configurations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    url = Column(String(2048), nullable=False)
    status = Column(
        SQLEnum(ScrapingStatus),
        default=ScrapingStatus.PENDING,
        nullable=False
    )
    error_message = Column(String(1000), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship with User (if needed for eager loading)
    # user = relationship("User", back_populates="configurations")

    def __repr__(self):
        return f"<Configuration {self.url} - {self.status}>"
