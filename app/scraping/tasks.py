"""
Celery tasks for web scraping.
"""

from celery import Task
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.config_management.repository import ConfigurationRepository
from app.config_management.models import ScrapingStatus
from app.scraping.scraper import WebScraper


class DatabaseTask(Task):
    """Base task that provides database session."""

    _db: Session = None

    @property
    def db(self):
        if self._db is None:
            self._db = SessionLocal()
        return self._db

    def after_return(self, *args, **kwargs):
        if self._db is not None:
            self._db.close()
            self._db = None


def scrape_and_embed_task(config_id: int, user_id: int):
    """
    Celery task to scrape URL and embed into vector store.

    This function will be decorated with @celery_app.task in worker/tasks/scraping_tasks.py

    Args:
        config_id: Configuration ID
        user_id: User ID

    Returns:
        Success message
    """
    db = SessionLocal()

    try:
        # Get configuration
        config_repo = ConfigurationRepository(db)
        config = config_repo.get_by_id(config_id, user_id)

        if not config:
            db.close()
            raise ValueError(f"Configuration {config_id} not found")

        # Update status to processing
        config_repo.update_status(config_id, ScrapingStatus.PROCESSING)

        # Scrape URL
        scraper = WebScraper()
        chunks = scraper.scrape_url(config.url)

        # Import here to avoid circular imports
        from app.langchain_app.vectorstore import get_vectorstore
        from app.langchain_app.embeddings import get_embeddings

        # Get vector store and embeddings
        vectorstore = get_vectorstore()
        embeddings = get_embeddings()

        # Embed chunks into Pinecone
        texts = [chunk["content"] for chunk in chunks]
        metadatas = [
            {
                **chunk["metadata"],
                "user_id": user_id,
                "config_id": config_id
            }
            for chunk in chunks
        ]

        # Add to vector store
        vectorstore.add_texts(
            texts=texts,
            metadatas=metadatas
        )

        # Update status to completed
        config_repo.update_status(config_id, ScrapingStatus.COMPLETED)

        return {
            "status": "success",
            "config_id": config_id,
            "chunks_processed": len(chunks)
        }

    except Exception as e:
        # Rollback any pending transactions
        try:
            db.rollback()
        except:
            pass
            
        # Update status to failed with error message
        try:
            config_repo.update_status(
                config_id,
                ScrapingStatus.FAILED,
                error_message=str(e)
            )
        except:
            pass
        raise

    finally:
        db.close()
