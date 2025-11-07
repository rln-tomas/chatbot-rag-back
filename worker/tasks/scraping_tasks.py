"""
Celery tasks for web scraping.
Wraps the scraping logic from app.scraping.tasks with Celery decorators.
"""

from worker.celery_app import celery_app
from app.scraping.tasks import scrape_and_embed_task


@celery_app.task(
    bind=True,
    name="scrape_and_embed",
    max_retries=3,
    default_retry_delay=60
)
def scrape_and_embed_task_celery(self, config_id: int, user_id: int):
    """
    Celery task wrapper for scraping and embedding.

    Args:
        config_id: Configuration ID
        user_id: User ID

    Returns:
        Task result
    """
    try:
        result = scrape_and_embed_task(config_id, user_id)
        return result
    except Exception as exc:
        # Retry the task with exponential backoff
        raise self.retry(exc=exc, countdown=2 ** self.request.retries * 60)
