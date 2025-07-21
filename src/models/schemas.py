#!/usr/bin/env python3
"""
Data models and schemas for the Advanced Quote Generator System
"""

from pydantic import BaseModel
from typing import Optional, List
from enum import Enum

# Enums for better API structure
class AudienceType(str, Enum):
    gen_z = "gen-z"
    millennial = "millennial"
    mixed = "mixed"

class ThemeType(str, Enum):
    motivation = "motivation"
    relationships = "relationships"
    success = "success"
    life_lessons = "life_lessons"
    self_improvement = "self_improvement"
    money_mindset = "money_mindset"
    mental_health = "mental_health"
    business = "business"
    mixed = "mixed"

class FormatType(str, Enum):
    maturity_when = "maturity_when"
    painful_truth = "painful_truth"
    not_everyone_understands = "not_everyone_understands"
    realization = "realization"
    comparison = "comparison"
    rules_for_year = "rules_for_year"
    deep_quote = "deep_quote"
    mixed = "mixed"

class ImageTheme(str, Enum):
    paper = "paper"
    modern = "modern"
    minimal = "minimal"
    anime = "anime"

class ImageModel(str, Enum):
    azure = "azure"
    google = "google"

class YouTubePrivacy(str, Enum):
    private = "private"
    public = "public"
    unlisted = "unlisted"

# Request Models
class QuoteRequest(BaseModel):
    """Request model for quote generation"""
    audience: AudienceType = AudienceType.gen_z
    theme: ThemeType = ThemeType.mixed
    format_preference: FormatType = FormatType.mixed
    custom_topic: Optional[str] = None
    generate_image: bool = False
    image_model: ImageModel = ImageModel.azure
    image_theme: ImageTheme = ImageTheme.paper
    generate_video: bool = False

class ImageRequest(BaseModel):
    """Request model for image generation"""
    quote_text: str
    image_model: ImageModel = ImageModel.azure
    image_theme: ImageTheme = ImageTheme.paper

class VideoRequest(BaseModel):
    """Request model for video generation"""
    image_url: Optional[str] = None
    quote_title: str = "Daily Vibe"
    quote_text: Optional[str] = None
    image_style: ImageTheme = ImageTheme.minimal

class InstagramUploadRequest(BaseModel):
    """Request model for Instagram upload"""
    video_url: str
    caption: str = ""
    share_to_feed: bool = True
    thumb_offset: Optional[int] = None
    location_id: Optional[str] = None

# Response Models
class ViralQuote(BaseModel):
    """Response model for generated viral quotes"""
    title: str
    quote: str
    full_caption: str
    theme: str
    format_type: str
    virality_score: int
    image_filename: Optional[str] = None
    image_url: Optional[str] = None
    video_filename: Optional[str] = None
    video_url: Optional[str] = None
    # YouTube metadata
    youtube_title: Optional[str] = None
    youtube_description: Optional[str] = None
    youtube_tags: Optional[List[str]] = None

class ImageResponse(BaseModel):
    """Response model for image generation"""
    quote_text: str
    image_theme: str
    image_filename: Optional[str] = None
    image_url: Optional[str] = None
    error: Optional[str] = None

class VideoResponse(BaseModel):
    """Response model for video generation"""
    image_url: Optional[str] = None
    quote_title: str
    quote_text: Optional[str] = None
    image_style: str
    video_filename: Optional[str] = None
    video_url: Optional[str] = None
    error: Optional[str] = None

class InstagramResponse(BaseModel):
    """Response model for Instagram upload"""
    container_id: str
    media_id: str
    status: str

class BatchResponse(BaseModel):
    """Response model for batch operations"""
    viral_quotes: List[ViralQuote]
    total_generated: int
    total_requested: int
    success_rate: float

class AnalyticsResponse(BaseModel):
    """Response model for analytics"""
    optimal_word_count: str
    best_posting_times: List[str]
    top_hashtags: List[str]
    viral_triggers: List[str]
    engagement_boosters: List[str]

class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str
    service: str
    version: str
    timestamp: str
    ai_model: str

class RandomChoiceRequest(BaseModel):
    """Request model for random choice selection"""
    choices: List[str]

class RandomChoiceResponse(BaseModel):
    """Response model for random choice selection"""
    choices: List[str]
    selected: str
    timestamp: str

class YouTubeUploadRequest(BaseModel):
    """Request model for YouTube Short upload"""
    video_url: str
    title: str
    description: str
    tags: Optional[List[str]] = []
    privacy: YouTubePrivacy = YouTubePrivacy.private

class YouTubeUploadResponse(BaseModel):
    """Response model for YouTube upload"""
    success: bool
    video_id: Optional[str] = None
    video_url: Optional[str] = None
    shorts_url: Optional[str] = None
    title: str
    privacy: str
    message: str
    error: Optional[str] = None

# Story Generation Enums
class StoryType(str, Enum):
    random = "random"
    job = "job"
    horror = "horror"

class JobStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    failed = "failed"

# Story Generation Models
class StoryRequest(BaseModel):
    """Request model for story generation"""
    story_type: StoryType = StoryType.random
    custom_job: Optional[str] = None
    custom_location: Optional[str] = None
    custom_theme: Optional[str] = None
    language: str = "Hindi"

class StoryJobResponse(BaseModel):
    """Response model for story job creation"""
    job_id: str
    status: JobStatus
    message: str
    created_at: str

class StoryStatusResponse(BaseModel):
    """Response model for story job status"""
    job_id: str
    status: JobStatus
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    progress_message: Optional[str] = None
    error_message: Optional[str] = None

class StoryResponse(BaseModel):
    """Response model for generated story content"""
    story_text: str
    story_type: str
    video_url: Optional[str] = None
    audio_filename: Optional[str] = None
    instagram_caption: str
    youtube_title: str
    youtube_description: str
    youtube_tags: List[str]
    hashtags: List[str]
    success: bool
    message: str
    error: Optional[str] = None
