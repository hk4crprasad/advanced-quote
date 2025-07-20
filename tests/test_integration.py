#!/usr/bin/env python3
"""
Integration tests for the modular Advanced Quote Generator System
"""

import pytest
from fastapi.testclient import TestClient

class TestModularIntegration:
    """Test the modular architecture integration"""
    
    def test_app_creation(self, app):
        """Test that the app creates successfully"""
        assert app is not None
        assert app.title == "Advanced Quote Generator API"
    
    def test_root_endpoint(self, client):
        """Test the root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "features" in data
    
    def test_health_endpoint(self, client):
        """Test the health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "service" in data
        assert "version" in data
    
    def test_viral_ideas_endpoint(self, client):
        """Test the viral ideas endpoint"""
        response = client.get("/viral-ideas")
        assert response.status_code == 200
        data = response.json()
        assert "top_viral_formats" in data
        assert "viral_themes" in data
        assert "engagement_tips" in data
    
    def test_analytics_endpoint(self, client):
        """Test the analytics endpoint"""
        response = client.get("/analytics")
        assert response.status_code == 200
        data = response.json()
        assert "optimal_word_count" in data
        assert "best_posting_times" in data
        assert "top_hashtags" in data

class TestAPIEndpoints:
    """Test API endpoint functionality"""
    
    def test_quote_generation_request_validation(self, client):
        """Test quote generation request validation"""
        # Test valid request
        valid_request = {
            "audience": "gen_z",
            "theme": "motivation", 
            "format_preference": "question",
            "generate_image": True,
            "image_theme": "paper",
            "generate_video": True
        }
        
        # Should not crash on valid request (may fail on actual generation due to mocks)
        response = client.post("/generate-viral-quote", json=valid_request)
        # We expect either success or controlled failure, not validation error
        assert response.status_code != 422
    
    def test_image_generation_request_validation(self, client):
        """Test image generation request validation"""
        valid_request = {
            "quote_text": "Test quote for image",
            "image_theme": "paper"
        }
        
        response = client.post("/generate-image", json=valid_request)
        # Should not be a validation error
        assert response.status_code != 422
    
    def test_video_generation_request_validation(self, client):
        """Test video generation request validation"""
        valid_request = {
            "image_url": "https://example.com/image.jpg",
            "quote_title": "Test Title",
            "quote_text": "Test quote for video",
            "image_style": "paper"
        }
        
        response = client.post("/generate-video", json=valid_request)
        # Should not be a validation error
        assert response.status_code != 422

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
