#!/usr/bin/env python3
"""
Main entry point for the Advanced Quote Generator System
Modular architecture implementation
"""

from src.api import create_app

# Create the FastAPI application
app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8091, 
        reload=True
    )
