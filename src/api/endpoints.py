#!/usr/bin/env python3
"""
FastAPI endpoints for the Advanced Quote Generator System
"""

import random
from datetime import datetime
from typing import List
from fastapi import FastAPI, HTTPException

from ..core.config import Config
from ..models.schemas import (
    QuoteRequest, ImageRequest, VideoRequest, InstagramUploadRequest,
    ViralQuote, ImageResponse, VideoResponse, InstagramResponse,
    BatchResponse, AnalyticsResponse, HealthResponse,
    RandomChoiceRequest, RandomChoiceResponse,
    YouTubeUploadRequest, YouTubeUploadResponse,
    AudienceType, ThemeType, FormatType, ImageTheme, ImageModel, YouTubePrivacy
)
from ..services.content_orchestrator import ContentOrchestrator
from ..services.youtube_service import YouTubeService
from ..generators import ImageGenerator, VideoGenerator

class QuoteAPI:
    """FastAPI application for quote generation"""
    
    def __init__(self):
        self.app = FastAPI(
            title=Config.API_TITLE,
            version=Config.API_VERSION,
            description="Advanced modular quote generation system"
        )
        
        # Initialize services
        self.orchestrator = ContentOrchestrator()
        self.image_generator = ImageGenerator()
        self.video_generator = VideoGenerator()
        self.youtube_service = YouTubeService()
        
        # Setup routes
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup all API routes"""
        
        @self.app.get("/")
        async def root():
            return {
                "message": f"{Config.API_TITLE} - Modular Architecture", 
                "version": Config.API_VERSION,
                "features": [
                    "Modular quote generation",
                    "Advanced image creation",
                    "Dynamic video production", 
                    "Instagram integration",
                    "Batch processing",
                    "Analytics and insights"
                ]
            }
        
        @self.app.post("/generate-viral-quote", response_model=ViralQuote)
        async def generate_viral_quote(request: QuoteRequest):
            """Generate a viral Instagram quote with optional image and video"""
            try:
                # Create orchestrator with specific image model for this request
                orchestrator = ContentOrchestrator(image_model=request.image_model.value)
                quote = await orchestrator.generate_complete_content(request)
                return quote
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to generate viral quote: {str(e)}")
        
        @self.app.get("/generate-trending", response_model=ViralQuote)
        async def generate_trending_quote():
            """Generate a trending viral quote optimized for maximum engagement"""
            try:
                request = self.orchestrator.generate_trending_request()
                return await self.orchestrator.generate_complete_content(request)
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to generate trending quote: {str(e)}")
        
        @self.app.post("/generate-batch-viral", response_model=BatchResponse)
        async def generate_batch_viral_quotes(requests: List[QuoteRequest]):
            """Generate multiple viral quotes in batch"""
            try:
                result = await self.orchestrator.generate_batch_content(requests)
                return BatchResponse(**result)
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Batch generation failed: {str(e)}")
        
        @self.app.post("/generate-image", response_model=ImageResponse)
        async def generate_quote_image(request: ImageRequest):
            """Generate an image for a given quote text"""
            try:
                # Create image generator with specific model for this request
                image_generator = ImageGenerator(image_model=request.image_model.value)
                filename, url, error = image_generator.generate_image_safe(
                    request.quote_text, request.image_theme.value
                )
                
                if error:
                    raise HTTPException(status_code=500, detail=f"Image generation failed: {error}")
                
                return ImageResponse(
                    quote_text=request.quote_text,
                    image_theme=request.image_theme.value,
                    image_filename=filename,
                    image_url=url
                )
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to generate image: {str(e)}")
        
        @self.app.post("/generate-video", response_model=VideoResponse)
        async def generate_quote_video(request: VideoRequest):
            """Generate a video using an existing quote image or text"""
            try:
                filename, url, error = await self.video_generator.generate_video_safe(
                    request.image_url, request.quote_title, request.quote_text, request.image_style.value
                )
                
                if error:
                    raise HTTPException(status_code=500, detail=f"Video generation failed: {error}")
                
                return VideoResponse(
                    image_url=request.image_url,
                    quote_title=request.quote_title,
                    quote_text=request.quote_text,
                    image_style=request.image_style.value,
                    video_filename=filename,
                    video_url=url
                )
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to generate video: {str(e)}")
        
        @self.app.post("/generate-complete-content", response_model=ViralQuote)
        async def generate_complete_content(
            audience: AudienceType = AudienceType.gen_z,
            theme: ThemeType = ThemeType.mixed,
            format_preference: FormatType = FormatType.mixed,
            custom_topic: str = None,
            image_model: ImageModel = ImageModel.azure,
            image_theme: ImageTheme = ImageTheme.paper,
            include_video: bool = True
        ):
            """Generate complete viral content: quote, image, and video in one request"""
            request = QuoteRequest(
                audience=audience,
                theme=theme,
                format_preference=format_preference,
                custom_topic=custom_topic,
                generate_image=True,
                image_model=image_model,
                image_theme=image_theme,
                generate_video=include_video
            )
            
            return await generate_viral_quote(request)
        
        @self.app.post("/upload-to-instagram", response_model=InstagramResponse)
        async def upload_to_instagram(request: InstagramUploadRequest):
            """Upload video to Instagram"""
            try:
                result = await self.orchestrator.upload_to_instagram(
                    request.video_url, request.caption
                )
                return InstagramResponse(**result)
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Instagram upload failed: {str(e)}")
        
        @self.app.post("/upload-to-youtube", response_model=YouTubeUploadResponse)
        async def upload_to_youtube(request: YouTubeUploadRequest):
            """Upload video as YouTube Short"""
            try:
                result = await self.youtube_service.upload_youtube_short(
                    video_url=request.video_url,
                    title=request.title,
                    description=request.description,
                    tags=request.tags,
                    privacy=request.privacy.value
                )
                return YouTubeUploadResponse(**result)
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"YouTube upload failed: {str(e)}")
        
        @self.app.post("/create-and-upload-complete")
        async def create_and_upload_complete(request: QuoteRequest):
            """Complete workflow: generate content and upload to Instagram"""
            try:
                result = await self.orchestrator.create_and_upload_complete(request)
                return result
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Complete workflow failed: {str(e)}")
        
        @self.app.get("/viral-ideas")
        async def get_viral_ideas():
            """Get ideas for creating viral content"""
            return {
                "top_viral_formats": [
                    {"format": "maturity_when", "description": "Complete 'Maturity is when...' statements", "viral_rate": "95%"},
                    {"format": "painful_truth", "description": "Harsh but accurate life realities", "viral_rate": "92%"},
                    {"format": "not_everyone_understands", "description": "Exclusive feeling quotes", "viral_rate": "88%"}
                ],
                "viral_themes": [
                    {"theme": "relationships", "why": "Universal human experience"},
                    {"theme": "mental_health", "why": "High engagement and sharing"},
                    {"theme": "life_lessons", "why": "Wisdom seekers love sharing"}
                ],
                "engagement_tips": [
                    "Keep quotes under 25 words",
                    "Use emotional trigger words",
                    "Create exclusivity feeling",
                    "Make it screenshot-worthy",
                    "End with cliffhanger feeling"
                ]
            }
        
        @self.app.get("/analytics", response_model=AnalyticsResponse)
        async def get_analytics():
            """Get analytics on what makes content go viral"""
            return AnalyticsResponse(
                optimal_word_count="10-20 words",
                best_posting_times=["6-9 AM", "6-9 PM"],
                top_hashtags=["#motivation", "#mindset", "#growth", "#success", "#life"],
                viral_triggers=["exclusivity", "painful_truth", "realization", "comparison", "wisdom"],
                engagement_boosters=["Follow for...", "Double tap if...", "Tag someone who...", "Save for later"]
            )
        
        @self.app.post("/random-choice", response_model=RandomChoiceResponse)
        async def random_choice(request: RandomChoiceRequest):
            """Select one random choice from a list of options"""
            try:
                if not request.choices:
                    raise HTTPException(status_code=400, detail="Choices list cannot be empty")
                
                # Select one random choice
                selected = random.choice(request.choices)
                
                return RandomChoiceResponse(
                    choices=request.choices,
                    selected=selected,
                    timestamp=datetime.now().isoformat()
                )
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Random choice failed: {str(e)}")
        
        @self.app.get("/health", response_model=HealthResponse)
        async def health_check():
            """System health check"""
            return HealthResponse(
                status="healthy",
                service="advanced-quote-generator",
                version=Config.API_VERSION,
                timestamp=datetime.now().isoformat(),
                ai_model=Config.MODEL_NAME
            )

def create_app() -> FastAPI:
    """Create and return the FastAPI application"""
    api = QuoteAPI()
    return api.app
