#!/usr/bin/env python3
"""
Main content orchestration service
"""

import random
from typing import Dict, List, Tuple
from langchain_openai import OpenAI
from langchain.prompts import PromptTemplate
from ..core.config import Config
from ..models.schemas import QuoteRequest, ViralQuote, AudienceType, ThemeType, FormatType
from ..generators import QuoteGenerator, ImageGenerator, VideoGenerator
from ..services.instagram_service import InstagramService

class ContentOrchestrator:
    """Orchestrate the complete content generation pipeline"""
    
    def __init__(self, image_model: str = None):
        # Use config default if not specified
        image_model = image_model or Config.IMAGE_MODEL
        
        self.quote_generator = QuoteGenerator()
        self.image_generator = ImageGenerator(image_model=image_model)
        self.video_generator = VideoGenerator(image_model=image_model)
        self.instagram_service = InstagramService()
        
        # Initialize AI LLM for YouTube metadata generation
        self.ai_llm = OpenAI(
            openai_api_base=Config.OPENAI_API_BASE,
            openai_api_key=Config.OPENAI_API_KEY,
            model_name=Config.MODEL_NAME,
            temperature=Config.TEMPERATURE,
            max_tokens=Config.MAX_TOKENS
        )
    
    async def generate_complete_content(self, request: QuoteRequest) -> ViralQuote:
        """Generate complete viral content package"""
        
        # Step 1: Generate the quote
        quote_data = self.quote_generator.generate_quote(request)
        
        # Initialize response data
        title = quote_data['title']
        quote = quote_data['quote']
        full_caption = quote_data['full_caption']
        theme = quote_data['theme']
        format_type = quote_data['format_type']
        virality_score = quote_data['virality_score']
        
        image_filename = None
        image_url = None
        video_filename = None
        video_url = None
        
        # Step 2: Generate image if requested
        if request.generate_image:
            try:
                image_filename, image_url, error = self.image_generator.generate_image_safe(
                    quote, request.image_theme.value
                )
                if error:
                    print(f"Image generation failed: {error}")
            except Exception as e:
                print(f"Image generation error: {str(e)}")
        
        # Step 3: Generate video if requested
        if request.generate_video:
            try:
                # Pass the image URL if available, otherwise generate text-based video
                video_filename, video_url, error = await self.video_generator.generate_video_safe(
                    image_url, title, quote, request.image_theme.value
                )
                if error:
                    print(f"Video generation failed: {error}")
            except Exception as e:
                print(f"Video generation error: {str(e)}")
        
        # Step 4: Generate YouTube metadata
        youtube_title, youtube_description, youtube_tags = self._generate_youtube_metadata(
            quote, title, theme, format_type
        )
        
        return ViralQuote(
            title=title,
            quote=quote,
            full_caption=full_caption,
            theme=theme,
            format_type=format_type,
            virality_score=virality_score,
            image_filename=image_filename,
            image_url=image_url,
            video_filename=video_filename,
            video_url=video_url,
            youtube_title=youtube_title,
            youtube_description=youtube_description,
            youtube_tags=youtube_tags
        )
    
    def generate_trending_request(self) -> QuoteRequest:
        """Generate a trending viral quote request"""
        viral_combinations = self.quote_generator.get_trending_combinations()
        combo = random.choice(viral_combinations)
        
        return QuoteRequest(
            audience=combo["audience"],
            theme=combo["theme"],
            format_preference=combo["format"]
        )
    
    async def generate_batch_content(self, requests: List[QuoteRequest], max_batch_size: int = 5) -> Dict[str, any]:
        """Generate multiple viral quotes in batch"""
        if len(requests) > max_batch_size:
            raise Exception(f"Maximum {max_batch_size} quotes per batch to ensure quality")
        
        quotes = []
        successful = 0
        
        for request in requests:
            try:
                quote = await self.generate_complete_content(request)
                quotes.append(quote)
                successful += 1
            except Exception as e:
                print(f"Batch item failed: {str(e)}")
                continue
        
        return {
            "viral_quotes": quotes, 
            "total_generated": successful,
            "total_requested": len(requests),
            "success_rate": successful / len(requests) if requests else 0.0
        }
    
    async def upload_to_instagram(self, video_url: str, caption: str) -> Dict[str, any]:
        """Upload video to Instagram"""
        try:
            result = self.instagram_service.upload_reel_complete(video_url, caption)
            return result
        except Exception as e:
            raise Exception(f"Instagram upload failed: {str(e)}")
    
    async def create_and_upload_complete(self, request: QuoteRequest) -> Dict[str, any]:
        """Complete workflow: generate content and upload to Instagram"""
        # Generate content
        content = await self.generate_complete_content(request)
        
        if not content.video_url:
            raise Exception("Video generation required for Instagram upload")
        
        # Upload to Instagram
        upload_result = await self.upload_to_instagram(content.video_url, content.full_caption)
        
        return {
            "content": content,
            "instagram_upload": upload_result
        }
    
    def _generate_youtube_metadata(self, quote: str, title: str, theme: str, format_type: str) -> Tuple[str, str, List[str]]:
        """Generate YouTube title, description, and tags using AI"""
        
        # AI-powered YouTube Title Generation
        try:
            title_prompt = f"""Create a viral YouTube Shorts title for this motivational quote. Make it engaging, under 100 characters, and include emojis:

Quote: "{quote[:50]}"
Theme: {theme.replace('_', ' ')}
Format: {format_type.replace('_', ' ')}

Examples of good titles:
- "Life Lesson: Success is not final... 💯"
- "Truth Bomb: Failure is not fatal... �" 
- "Mindset Shift: Courage to continue... 💪"
- "Daily Motivation: Change your life... ✨"

Generate 1 catchy title (max 100 chars):"""
            
            ai_title = self.ai_llm.invoke(title_prompt).strip()
            ai_title = ai_title.replace('"', '').replace('\n', ' ').strip()
            if len(ai_title) > 100:
                ai_title = ai_title[:97] + "..."
            youtube_title = ai_title
        except Exception as e:
            print(f"AI title generation failed, using fallback: {e}")
            youtube_title = f"Daily Motivation: {quote[:40]}... 💯"
        
        # Use the format you requested
        youtube_description = f'''💯 "{quote}" 💯

Do you agree with this? Drop a 🔥 in comments!

Life changing quotes that hit different 💪

Thanks for watching 🙏
Keep supporting.. @Motivational_Ai

#shortsviral
#motivation 
#inspirationalquotes
#lifequotes
#motivationalquotes 
#viral 
#ytshorts 
#motivationalvideo 
#shortvideo
#inspiringquotes 
#inspirational 
#quote 
#quotesoftheday 
#quotesaboutlife 
#thoughtoftheday
#richmindset
#billionaire 
#sigmarule 
#sigma 
#attitude
#status
#trendingshorts 
#youtubeshort 
#trending 
#billionairethoughts 
#billionairequotes 
#richmindsetmotivation
#success
#wealth
#money
#entrepreneur
#business
#goals
#dreams
#hustle
#grind
#focus
#discipline
#mindset
#positivity
#selfimprovement
#personalgrowth
#achievement
#excellence
#leadership
#confidence
#determination
#persistence
#resilience
#wisdom
#philosophy
#psychology
#spiritual
#consciousness
#transformation
#change
#growth
#development
#improvement
#mastery
#expertise
#knowledge
#learning
#education
#teaching
#coaching
#mentoring
#guidance

Search Terms:

{theme.replace('_', ' ')} motivational quotes
{format_type.replace('_', ' ')} inspirational lines
life lessons motivational status
success mindset quotes
billionaire mindset motivation
motivational whatsapp status
inspirational video shorts
attitude motivational quotes
sigma male quotes
life changing quotes
powerful motivational lines
deep life quotes
wisdom quotes for life
success inspiration shorts
millionaire mindset quotes
entrepreneur motivation
business success quotes
money mindset quotes
wealth creation mindset
rich mindset motivation
luxury lifestyle quotes
achievement motivation
goal setting quotes
dream chasing quotes
hustle motivation quotes
grind mindset quotes
focus and discipline quotes
habit formation quotes
lifestyle design quotes
personal branding quotes
self development quotes
growth mindset quotes
transformation quotes
change your life quotes
improve yourself quotes
be better quotes
level up quotes
upgrade your mindset
evolve and grow quotes
progress motivation
advancement quotes'''
        
        # AI-powered YouTube Tags Generation
        try:
            tags_prompt = f"""Generate 30 highly effective YouTube tags for this motivational quote. Focus on viral, trending, and SEO-optimized keywords:

Quote: "{quote[:100]}"
Theme: {theme.replace('_', ' ')}
Format: {format_type.replace('_', ' ')}

Include these types of tags:
- Base viral tags: shorts, motivation, quotes, viral, trending
- Theme-specific tags related to {theme.replace('_', ' ')}
- Format-specific tags related to {format_type.replace('_', ' ')}
- Popular SEO tags: fyp, explore, motivationalquotes, dailymotivation
- Trending lifestyle tags: mindset, success, entrepreneur, billionaire
- Engagement tags: inspirational, wisdom, lifelessons, selfimprovement

Generate exactly 30 tags as a comma-separated list (no hashtags, just words):"""
            
            ai_tags_response = self.ai_llm.invoke(tags_prompt).strip()
            ai_tags = [tag.strip().lower().replace('#', '') for tag in ai_tags_response.split(',')]
            youtube_tags = [tag for tag in ai_tags if tag and len(tag) > 2][:30]
            
            # Ensure essential tags are included
            essential_tags = ["shorts", "motivation", "quotes", "viral", "motivational_ai"]
            for tag in essential_tags:
                if tag not in youtube_tags:
                    youtube_tags.insert(0, tag)
            
            youtube_tags = youtube_tags[:30]
            
        except Exception as e:
            print(f"AI tags generation failed, using fallback: {e}")
            youtube_tags = [
                "shorts", "motivation", "quotes", "viral", "trending", "motivational_ai",
                "inspirational", "lifequotes", "motivationalquotes", "dailymotivation",
                "mindset", "success", "entrepreneur", "billionaire", "sigma", "attitude",
                "selfimprovement", "personalgrowth", "wisdom", "philosophy", "psychology",
                "spiritual", "consciousness", "transformation", "achievement", "excellence",
                "leadership", "confidence", "determination", "resilience", "goals"
            ]
        
        return youtube_title, youtube_description, youtube_tags
