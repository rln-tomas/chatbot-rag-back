"""
API v1 router aggregator.
Combines all module routers into a single v1 API router.
"""

from fastapi import APIRouter
from app.auth.router import router as auth_router
from app.chat.router import router as chat_router
from app.config_management.router import router as config_router
from app.scraping.router import router as scraping_router

# Create v1 API router
api_router = APIRouter()

# Include all module routers with appropriate prefixes and tags
api_router.include_router(
    auth_router,
    prefix="/auth",
    tags=["Authentication"]
)

api_router.include_router(
    chat_router,
    prefix="/chat",
    tags=["Chat"]
)

api_router.include_router(
    config_router,
    prefix="/configs",
    tags=["Configuration Management"]
)

api_router.include_router(
    scraping_router,
    prefix="/scraping",
    tags=["Web Scraping"]
)
