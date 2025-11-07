"""
Configuration management service with business logic.
"""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.config_management.repository import ConfigurationRepository
from app.config_management.schemas import (
    ConfigurationCreate,
    ConfigurationResponse,
    ConfigurationListResponse
)
from app.config_management.models import Configuration


class ConfigurationService:
    """Service for configuration management operations."""

    def __init__(self, db: Session):
        self.repository = ConfigurationRepository(db)
        self.db = db

    def create_configuration(
        self,
        user_id: int,
        config_data: ConfigurationCreate
    ) -> ConfigurationResponse:
        """
        Create a new configuration.

        Args:
            user_id: User ID
            config_data: Configuration data

        Returns:
            Created configuration

        Raises:
            HTTPException: If validation fails
        """
        # Validate URL format (basic validation, can be enhanced)
        url = config_data.url.strip()

        if not url.startswith(('http://', 'https://')):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="URL must start with http:// or https://"
            )

        # Create configuration
        config = self.repository.create(user_id=user_id, url=url)

        return ConfigurationResponse.model_validate(config)

    def get_configuration(self, config_id: int, user_id: int) -> ConfigurationResponse:
        """
        Get configuration by ID.

        Args:
            config_id: Configuration ID
            user_id: User ID

        Returns:
            Configuration

        Raises:
            HTTPException: If not found
        """
        config = self.repository.get_by_id(config_id, user_id)

        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Configuration not found"
            )

        return ConfigurationResponse.model_validate(config)

    def get_user_configurations(
        self,
        user_id: int,
        page: int = 1,
        page_size: int = 20
    ) -> ConfigurationListResponse:
        """
        Get all configurations for a user with pagination.

        Args:
            user_id: User ID
            page: Page number (starts at 1)
            page_size: Number of items per page

        Returns:
            Paginated configuration list
        """
        skip = (page - 1) * page_size
        configs = self.repository.get_all_by_user(user_id, skip=skip, limit=page_size)
        total = self.repository.count_by_user(user_id)

        return ConfigurationListResponse(
            total=total,
            items=[ConfigurationResponse.model_validate(c) for c in configs],
            page=page,
            page_size=page_size
        )

    def delete_configuration(self, config_id: int, user_id: int) -> None:
        """
        Delete a configuration.

        Args:
            config_id: Configuration ID
            user_id: User ID

        Raises:
            HTTPException: If not found or cannot be deleted
        """
        # Check if configuration exists and belongs to user
        config = self.repository.get_by_id(config_id, user_id)

        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Configuration not found"
            )

        # Don't allow deletion of processing configurations
        if config.status.value == "processing":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete configuration while processing"
            )

        # Delete configuration
        self.repository.delete(config_id, user_id)

    def check_can_start_scraping(self, user_id: int) -> bool:
        """
        Check if user can start a new scraping job.

        Args:
            user_id: User ID

        Returns:
            True if can start, False otherwise
        """
        return not self.repository.has_active_job(user_id)
