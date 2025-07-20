#!/usr/bin/env python3
"""
Main application file for the Advanced Quote Generator System
"""

from fastapi import FastAPI
from .endpoints import create_app

# Create the application instance
app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
