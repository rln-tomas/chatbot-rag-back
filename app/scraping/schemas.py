"""
Scraping Pydantic schemas.
"""

from pydantic import BaseModel, Field


class ScrapingTriggerRequest(BaseModel):
    """Schema for triggering scraping job."""
    config_id: int = Field(..., description="Configuration ID to scrape")


class ScrapingTriggerResponse(BaseModel):
    """Schema for scraping trigger response."""
    message: str
    task_id: str
    config_id: int
    status: str = "processing"


class ScrapingStatusResponse(BaseModel):
    """Schema for scraping status response."""
    config_id: int
    status: str
    error_message: str | None = None
