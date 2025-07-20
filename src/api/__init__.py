"""
API package for the Advanced Quote Generator System
Modular FastAPI application with separated concerns
"""

from .endpoints import create_app
from .main import app
from .routers import create_routers

__all__ = ['create_app', 'app', 'create_routers']
