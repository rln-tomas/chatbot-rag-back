"""
Configuration repository for database operations.
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from app.config_management.models import Configuration, ScrapingStatus


class ConfigurationRepository:
    """Repository for Configuration database operations."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, user_id: int, url: str) -> Configuration:
        """
        Create a new configuration.

        Args:
            user_id: User ID
            url: URL to scrape

        Returns:
            Created Configuration instance
        """
        config = Configuration(
            user_id=user_id,
            url=url,
            status=ScrapingStatus.PENDING
        )
        self.db.add(config)
        self.db.commit()
        self.db.refresh(config)
        return config

    def get_by_id(self, config_id: int, user_id: int) -> Optional[Configuration]:
        """
        Get configuration by ID for specific user.

        Args:
            config_id: Configuration ID
            user_id: User ID

        Returns:
            Configuration instance or None
        """
        return self.db.query(Configuration).filter(
            Configuration.id == config_id,
            Configuration.user_id == user_id
        ).first()

    def get_all_by_user(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Configuration]:
        """
        Get all configurations for a user with pagination.

        Args:
            user_id: User ID
            skip: Number of records to skip
            limit: Maximum number of records

        Returns:
            List of Configuration instances
        """
        return self.db.query(Configuration).filter(
            Configuration.user_id == user_id
        ).offset(skip).limit(limit).all()

    def count_by_user(self, user_id: int) -> int:
        """
        Count total configurations for a user.

        Args:
            user_id: User ID

        Returns:
            Total count
        """
        return self.db.query(Configuration).filter(
            Configuration.user_id == user_id
        ).count()

    def has_active_job(self, user_id: int) -> bool:
        """
        Check if user has an active (processing) scraping job.

        Args:
            user_id: User ID

        Returns:
            True if user has active job, False otherwise
        """
        return self.db.query(Configuration).filter(
            Configuration.user_id == user_id,
            Configuration.status == ScrapingStatus.PROCESSING
        ).first() is not None

    def update_status(
        self,
        config_id: int,
        status: ScrapingStatus,
        error_message: Optional[str] = None
    ) -> Optional[Configuration]:
        """
        Update configuration status.

        Args:
            config_id: Configuration ID
            status: New status
            error_message: Optional error message

        Returns:
            Updated Configuration instance or None
        """
        config = self.db.query(Configuration).filter(
            Configuration.id == config_id
        ).first()

        if config:
            config.status = status
            if error_message:
                config.error_message = error_message
            self.db.commit()
            self.db.refresh(config)

        return config

    def delete(self, config_id: int, user_id: int) -> bool:
        """
        Delete a configuration.

        Args:
            config_id: Configuration ID
            user_id: User ID

        Returns:
            True if deleted, False if not found
        """
        config = self.get_by_id(config_id, user_id)

        if config:
            self.db.delete(config)
            self.db.commit()
            return True

        return False
