"""
FastAPI router configurations for the Advanced Quote Generator System
"""

from fastapi import APIRouter
from .endpoints import QuoteAPI

def create_routers():
    """Create API routers for different functionality"""
    
    # Main API router
    api_router = APIRouter(prefix="/api/v1", tags=["api"])
    
    # Quote generation router
    quote_router = APIRouter(prefix="/quotes", tags=["quotes"])
    
    # Media generation router  
    media_router = APIRouter(prefix="/media", tags=["media"])
    
    # Instagram router
    instagram_router = APIRouter(prefix="/instagram", tags=["instagram"])
    
    # Analytics router
    analytics_router = APIRouter(prefix="/analytics", tags=["analytics"])
    
    return {
        "api": api_router,
        "quotes": quote_router,
        "media": media_router,
        "instagram": instagram_router,
        "analytics": analytics_router
    }
