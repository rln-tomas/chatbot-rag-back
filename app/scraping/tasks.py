"""
Celery tasks for web scraping.
"""

from celery import Task
from sqlalchemy.orm import Session
from app.core.database import get_session_local
from app.config_management.repository import ConfigurationRepository
from app.config_management.models import ScrapingStatus
from app.scraping.scraper import WebScraper


class DatabaseTask(Task):
    """Base task that provides database session."""

    _db: Session = None

    @property
    def db(self):
        if self._db is None:
            SessionLocal = get_session_local()
            self._db = SessionLocal()
        return self._db

    def after_return(self, *args, **kwargs):
        if self._db is not None:
            self._db.close()
            self._db = None


def scrape_and_embed_task(config_id: int, user_id: int):
    """
    Celery task to scrape URL (and all pages in the same domain) and embed into vector store.

    This function will be decorated with @celery_app.task in worker/tasks/scraping_tasks.py

    Args:
        config_id: Configuration ID
        user_id: User ID

    Returns:
        Success message with statistics
    """
    SessionLocal = get_session_local()
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

        # Scrape URL and all pages in the same domain recursively
        scraper = WebScraper(
            chunk_size=2000,
            chunk_overlap=400,
            max_pages=50,  # Limit to 50 pages for safety
            timeout=10
        )
        
        print(f"Starting recursive scraping of {config.url}")
        chunks = scraper.scrape_website_recursive(config.url)
        
        if not chunks:
            raise ValueError("No content could be extracted from the website")

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

        print(f"Embedding {len(texts)} chunks into Pinecone...")
        
        # Add to vector store in batches to respect Google's API limits
        # Google Gemini free tier allows max 250 requests per minute
        # Using smaller batch size to stay well within limits
        batch_size = 50  # Reduced from 100 to stay safe with Google API limits
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]
            batch_metadatas = metadatas[i:i + batch_size]
            
            vectorstore.add_texts(
                texts=batch_texts,
                metadatas=batch_metadatas
            )
            batch_number = i // batch_size + 1
            total_batches = (len(texts) + batch_size - 1) // batch_size
            print(f"Embedded batch {batch_number} of {total_batches} ({len(batch_texts)} chunks)")
            
            # Add a small delay between batches to avoid rate limiting
            import time
            if i + batch_size < len(texts):  # Don't delay after the last batch
                time.sleep(1)  # 1 second delay between batches

        # Update status to completed
        config_repo.update_status(config_id, ScrapingStatus.COMPLETED)
        
        # Count unique pages scraped
        unique_sources = set(chunk["metadata"].get("source") for chunk in chunks)

        return {
            "status": "success",
            "config_id": config_id,
            "chunks_processed": len(chunks),
            "pages_scraped": len(unique_sources),
            "message": f"Successfully scraped {len(unique_sources)} pages and processed {len(chunks)} chunks"
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
