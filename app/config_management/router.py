"""
Configuration management routes.
Endpoints for managing URL configurations.
"""

from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from app.core.dependencies import get_db, get_current_user
from app.auth.models import User
from app.config_management.schemas import (
    ConfigurationCreate,
    ConfigurationResponse,
    ConfigurationListResponse
)
from app.config_management.service import ConfigurationService

router = APIRouter()


@router.post(
    "/",
    response_model=ConfigurationResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_configuration(
    config_data: ConfigurationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new URL configuration for scraping.

    Args:
        config_data: Configuration data with URL
        current_user: Authenticated user
        db: Database session

    Returns:
        Created configuration
    """
    service = ConfigurationService(db)
    return service.create_configuration(current_user.id, config_data)


@router.get("/", response_model=ConfigurationListResponse)
async def get_configurations(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all configurations for the authenticated user.

    Args:
        page: Page number
        page_size: Number of items per page
        current_user: Authenticated user
        db: Database session

    Returns:
        Paginated list of configurations
    """
    service = ConfigurationService(db)
    return service.get_user_configurations(current_user.id, page, page_size)


@router.get("/{config_id}", response_model=ConfigurationResponse)
async def get_configuration(
    config_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific configuration by ID.

    Args:
        config_id: Configuration ID
        current_user: Authenticated user
        db: Database session

    Returns:
        Configuration details
    """
    service = ConfigurationService(db)
    return service.get_configuration(config_id, current_user.id)


@router.delete("/{config_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_configuration(
    config_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a configuration.

    Args:
        config_id: Configuration ID
        current_user: Authenticated user
        db: Database session
    """
    service = ConfigurationService(db)
    service.delete_configuration(config_id, current_user.id)
    return None
