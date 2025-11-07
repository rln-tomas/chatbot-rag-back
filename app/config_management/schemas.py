"""
Configuration management Pydantic schemas.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, HttpUrl, Field
from app.config_management.models import ScrapingStatus


class ConfigurationBase(BaseModel):
    """Base configuration schema."""
    url: str = Field(..., max_length=2048, description="URL to scrape")


class ConfigurationCreate(ConfigurationBase):
    """Schema for creating a new configuration."""
    pass


class ConfigurationUpdate(BaseModel):
    """Schema for updating configuration status."""
    status: ScrapingStatus
    error_message: Optional[str] = None


class ConfigurationResponse(ConfigurationBase):
    """Schema for configuration response."""
    id: int
    user_id: int
    status: ScrapingStatus
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ConfigurationListResponse(BaseModel):
    """Schema for paginated configuration list."""
    total: int
    items: list[ConfigurationResponse]
    page: int
    page_size: int
