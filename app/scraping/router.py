"""
Scraping routes.
Endpoints to trigger scraping jobs.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.dependencies import get_db, get_current_user
from app.auth.models import User
from app.scraping.schemas import ScrapingTriggerRequest, ScrapingTriggerResponse
from app.config_management.service import ConfigurationService
from app.config_management.repository import ConfigurationRepository
from app.config_management.models import ScrapingStatus

router = APIRouter()


@router.post("/start", response_model=ScrapingTriggerResponse)
async def trigger_scraping(
    request: ScrapingTriggerRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Trigger scraping job for a configuration.

    Args:
        request: Scraping trigger request with config_id
        current_user: Authenticated user
        db: Database session

    Returns:
        Scraping trigger response with task ID

    Raises:
        HTTPException: If user has active job or config not found
    """
    config_service = ConfigurationService(db)
    config_repo = ConfigurationRepository(db)

    # Check if user can start scraping (no active jobs)
    if not config_service.check_can_start_scraping(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already have an active scraping job. Please wait for it to complete."
        )

    # Get configuration and verify it belongs to user
    config = config_repo.get_by_id(request.config_id, current_user.id)

    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Configuration not found"
        )

    # Check if configuration is already processing or completed
    if config.status == ScrapingStatus.PROCESSING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This configuration is already being processed"
        )

    # Import Celery task here to avoid issues if Celery is not running
    try:
        from worker.tasks.scraping_tasks import scrape_and_embed_task_celery

        # Trigger Celery task
        task = scrape_and_embed_task_celery.delay(request.config_id, current_user.id)

        # Update status to processing
        config_repo.update_status(request.config_id, ScrapingStatus.PROCESSING)

        return ScrapingTriggerResponse(
            message="Scraping job started successfully",
            task_id=task.id,
            config_id=request.config_id,
            status="processing"
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start scraping job: {str(e)}"
        )
