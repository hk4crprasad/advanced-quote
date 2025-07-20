#!/usr/bin/env python3
"""
Test configuration for the modular Advanced Quote Generator System
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient

from src.api import create_app
from src.core.config import Config
from src.models.schemas import QuoteRequest, AudienceType, ThemeType, FormatType, ImageTheme

@pytest.fixture
def app():
    """Create test FastAPI application"""
    return create_app()

@pytest.fixture
def client(app):
    """Create test client"""
    return TestClient(app)

@pytest.fixture
def sample_quote_request():
    """Sample quote request for testing"""
    return QuoteRequest(
        audience=AudienceType.gen_z,
        theme=ThemeType.motivation,
        format_preference=FormatType.question,
        custom_topic="success mindset",
        generate_image=True,
        image_theme=ImageTheme.paper,
        generate_video=True
    )

@pytest.fixture
def mock_image_generator():
    """Mock image generator for testing"""
    mock = MagicMock()
    mock.generate_image_safe.return_value = (
        "test_image.jpg",
        "https://example.com/test_image.jpg",
        None
    )
    return mock

@pytest.fixture
def mock_video_generator():
    """Mock video generator for testing"""
    mock = AsyncMock()
    mock.generate_video_safe.return_value = (
        "test_video.mp4",
        "https://example.com/test_video.mp4", 
        None
    )
    return mock

@pytest.fixture
def mock_orchestrator():
    """Mock content orchestrator for testing"""
    mock = AsyncMock()
    mock.generate_complete_content.return_value = {
        "quote_text": "Test quote about success",
        "audience": "gen_z",
        "theme": "motivation",
        "hashtags": ["#motivation", "#success"],
        "image_url": "https://example.com/test_image.jpg",
        "video_url": "https://example.com/test_video.mp4"
    }
    return mock

# Test configuration
Config.TEST_MODE = True
