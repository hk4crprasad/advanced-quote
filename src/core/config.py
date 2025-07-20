#!/usr/bin/env python3
"""
Core configu    # Video Generation Configuration
    AUDIO_FILES = [
        {"file": "new.mp3", "fade_in_delay": 9},
        {"file": "newsong.mp3", "fade_in_delay": 11}
    ]
    DEFAULT_AUDIO_FILE = os.getenv("DEFAULT_AUDIO_FILE", "new.mp3")
    IMAGE_MODEL = os.getenv("IMAGE_MODEL", "azure")  # azure or google
    VIDEO_SIZE = (1080, 1920)  # Portrait mode for social media
    VIDEO_TITLE = "Daily Vibe"
    FADE_IN_DELAY = 9  # seconds (default)
    FADE_IN_DURATION = 4  # seconds
    VIDEO_FPS = 24le for the Advanced Quote Generator System
"""

import os
from dotenv import load_dotenv
from typing import Dict, List

# Load environment variables
load_dotenv()

class Config:
    """Central configuration class"""
    
    # LLM Configuration
    OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "https://litellm.tecosys.ai/")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    MODEL_NAME = "cost-cut"
    TEMPERATURE = 0.8
    MAX_TOKENS = 400
    
    # Instagram API Configuration
    ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
    INSTAGRAM_USER_ID = os.getenv("INSTAGRAM_USER_ID", "17841475846754872")
    BASE_URL = "https://graph.instagram.com/v23.0"
    
    # Azure OpenAI Configuration
    AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
    AZURE_DEPLOYMENT_NAME = os.getenv("DEPLOYMENT_NAME", "gpt-image-1")
    AZURE_API_VERSION = os.getenv("OPENAI_API_VERSION", "2025-04-01-preview")
    AZURE_SUBSCRIPTION_KEY = os.getenv("AZURE_OPENAI_API_KEY")
    
    # Azure Blob Storage Configuration
    AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    AZURE_CONTAINER_NAME = os.getenv("AZURE_CONTAINER_NAME")
    AZURE_BLOB_FOLDER = os.getenv("AZURE_BLOB_FOLDER", "image-gen")
    AZURE_VIDEO_FOLDER = os.getenv("AZURE_VIDEO_FOLDER", "video-gen")
    
    # Google Gemini Configuration
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    
    # Image Generation Configuration
    IMAGE_MODEL = os.getenv("IMAGE_MODEL", "azure")  # azure or google
    
    # Video Generation Configuration
    AUDIO_FILES = [
        {"file": "song.mp3", "fade_in_delay": 11},
        {"file": "new.mp3", "fade_in_delay": 9}
    ]
    DEFAULT_AUDIO_FILE = os.getenv("DEFAULT_AUDIO_FILE", "new.mp3")
    VIDEO_SIZE = (1080, 1920)  # Portrait mode for social media
    VIDEO_TITLE = "Daily Vibe"
    FADE_IN_DELAY = 9  # seconds (default)
    FADE_IN_DURATION = 4  # seconds
    VIDEO_FPS = 24
    BACKGROUND_COLOR = (20, 20, 20)  # Dark background
    BANNER_COLOR = (255, 255, 255)  # White banner
    BANNER_HEIGHT = 160
    BANNER_Y_POSITION = 300
    TITLE_FONT_SIZE = 45
    TITLE_COLOR = 'black'
    MARGIN = 40
    LINE_SPACING = 10
    
    # API Configuration
    API_HOST = "0.0.0.0"
    API_PORT = 8013
    API_TITLE = "Viral Instagram Quote Generator"
    API_VERSION = "2.0.0"
    
    # YouTube API Configuration
    YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

class Templates:
    """Template configurations"""
    
    HOOK_OPTIONS = [
        "Let this sink in",
        "Save this for later",
        "Tag someone who needs this",
        "Double tap if you felt this",
        "Share if you agree",
        "Comment if you relate",
        "This hit different",
        "Read that again",
        "Screenshot this",
        "Bookmark this wisdom"
    ]
    
    CAPTION_TEMPLATES = [
        "Follow for powerful daily reminders 💯",
        "Follow for daily motivation 🔥", 
        "Follow for life-changing quotes ✨",
        "Follow for daily wisdom drops 💎",
        "Follow for mindset shifts 🧠",
        "Follow for growth mindset content 🚀",
        "Follow for daily inspiration ⚡",
        "Follow for success mindset 💪"
    ]
    
    IMAGE_STYLE_TEMPLATES = {
        "paper1": """
Design a square motivational quote image with an authentic, tactile paper texture background. The paper should have:
- Realistic cream/off-white aged paper texture with visible paper fibers and subtle grain
- Natural paper imperfections like slight wrinkles, subtle stains, or worn edges
- Warm, soft lighting that creates gentle shadows and highlights on the paper surface
- A vintage, handwritten journal or notebook aesthetic

Typography:
- Use large, bold serif font (like Times or Garamond) in deep black/charcoal for the main quote
- Make the quote text prominently sized - it should be the dominant visual element and easily readable
- Font size should be generous and impactful, filling most of the available space while maintaining readability
- Highlight key impactful words or phrases with realistic yellow highlighter strokes that look hand-drawn with slight transparency and irregular edges
- The highlighter should appear slightly faded and authentic, not perfect digital highlighting

Layout:
- Center the quote with natural, readable spacing that feels handwritten or carefully typed
- Ensure the main quote text is large enough to be easily read on mobile devices
- Place "—hara point" in the bottom-right corner using a smaller, elegant script or serif font
- Add "Share this if you agree." at the bottom center in clean, smaller text
- Ensure the text appears naturally embedded on the paper surface with subtle shadows
- Leave appropriate margins but prioritize making the quote text as large and readable as possible

The overall aesthetic should feel like a meaningful quote carefully written or typed on quality paper, photographed with natural lighting. Make it warm, authentic, and tactile - as if you could reach out and touch the actual paper. The quote should be the star of the image with bold, large, easily readable text.

Quote: {quote_text}
""",
        "paper2": """
Create a square motivational quote image with an antique parchment background. The aesthetic should include:
- Rich, weathered parchment texture with coffee-stained or tea-stained appearance
- Vintage burn marks or aged spots around the edges
- Deep cream to light brown gradient coloring
- Authentic old manuscript or ancient scroll feel

Typography:
- Use large, ornate serif font (like Trajan or Old English) in dark brown or sepia ink
- Make the text appear hand-lettered with slight imperfections and character variations
- Font should be bold and prominently sized for maximum readability and impact
- Highlight important phrases with gold or amber colored accents that look like illuminated manuscript details
- Add subtle ink bleed effects around letters for authenticity

Layout:
- Center the quote with generous spacing, as if carefully inscribed by a calligrapher
- Large, commanding text that dominates the parchment surface
- Place "—hara point" in elegant calligraphy style in the bottom-right corner
- Add "Share this if you agree." in smaller, refined lettering at the bottom center
- Include subtle decorative flourishes or borders around the text area
- Ensure readability on mobile while maintaining the antique manuscript aesthetic

The image should evoke the feeling of discovering an ancient piece of wisdom written on precious parchment, with bold, large text that commands attention.

Quote: {quote_text}
""",
        "paper3": """
Design a square motivational quote image with a modern rustic paper aesthetic. Features should include:
- Handmade artisan paper texture with visible fiber strands and natural edges
- Soft white to warm beige coloring with organic, uneven surface
- Natural lighting with soft shadows that emphasize the paper's texture
- Contemporary craft paper or watercolor paper appearance

Typography:
- Use large, clean serif font (like Minion or Crimson) in deep charcoal black
- Text should be bold, modern, and highly readable while maintaining elegance
- Font size should be generous and impactful, filling the space prominently
- Highlight key words with hand-drawn style yellow or orange marker strokes
- The highlighting should look fresh and vibrant, like modern brush lettering

Layout:
- Center the quote with modern, clean spacing that feels intentional and designed
- Ensure large, prominent text that's easily readable on all devices
- Place "—hara point" in a contemporary script font in the bottom-right
- Add "Share this if you agree." in clean, modern typography at the bottom center
- Use minimalist design principles with focus on typography and texture balance
- Leave clean margins while maximizing text size and impact

The overall feel should be modern artisan craftsmanship - handmade paper meets contemporary design, with bold, large text that stands out beautifully.

Quote: {quote_text}
""",
        "paper": """
Design a square motivational quote image with an authentic, tactile paper texture background. The paper should have:
- Realistic cream/off-white aged paper texture with visible paper fibers and subtle grain
- Natural paper imperfections like slight wrinkles, subtle stains, or worn edges
- Warm, soft lighting that creates gentle shadows and highlights on the paper surface
- A vintage, handwritten journal or notebook aesthetic

Typography:
- Use large, bold serif font (like Times or Garamond) in deep black/charcoal for the main quote
- Make the quote text prominently sized - it should be the dominant visual element and easily readable
- Font size should be generous and impactful, filling most of the available space while maintaining readability
- Highlight key impactful words or phrases with realistic yellow highlighter strokes that look hand-drawn with slight transparency and irregular edges
- The highlighter should appear slightly faded and authentic, not perfect digital highlighting

Layout:
- Center the quote with natural, readable spacing that feels handwritten or carefully typed
- Ensure the main quote text is large enough to be easily read on mobile devices
- Place "—hara point" in the bottom-right corner using a smaller, elegant script or serif font
- Add "Share this if you agree." at the bottom center in clean, smaller text
- Ensure the text appears naturally embedded on the paper surface with subtle shadows
- Leave appropriate margins but prioritize making the quote text as large and readable as possible

The overall aesthetic should feel like a meaningful quote carefully written or typed on quality paper, photographed with natural lighting. Make it warm, authentic, and tactile - as if you could reach out and touch the actual paper. The quote should be the star of the image with bold, large, easily readable text.

Quote: {quote_text}
""",
        "modern": """
Create a modern, minimalist square quote image with a clean gradient background. 
Use a contemporary sans-serif font in dark text for the quote. 
Center the quote with proper spacing and add "—hara point" in the bottom-right corner in a subtle font. 
Include "Share this if you agree" at the bottom center. 
Style should be clean, professional, and Instagram-ready.
Quote: {quote_text}
""",
        "minimal": """
Design a simple, elegant square quote image with a solid color or subtle texture background. 
Use clean typography with the quote prominently centered. 
Add "—hara point" attribution in the bottom-right and "Share this if you agree" at the bottom center. 
Keep the design minimalist and focused on the text.
Quote: {quote_text}
""",
        "anime1": """
A cinematic anime-style illustration of a young male character with glowing red eyes, white and black dual-tone hair, and a scar on his face. He's wearing a black cloak, standing in a dark, mysterious cyberpunk environment with purple and blue lighting and organic tentacle-like shadows. The atmosphere is intense, emotional, and symbolic of strength and solitude.

Overlay this quote at the center of the image in clean serif font with yellow highlight for key words:

"{quote_text}"
—harapoint

The quote should be centered and integrated visually, without covering the character's face. No extra icons, logos, or titles.
""",
        "anime": """
A highly detailed anime-style digital artwork of a male character inspired by Goku in his Mastered Ultra Instinct (MUI) form. He has glowing silver eyes, spiky silver hair, and a calm, intensely focused expression. His tattered orange and blue martial arts outfit flutters dramatically in the wind. A radiant, bluish-white aura surrounds him, with swirling divine energy. The background is epic — a shattered battlefield, cosmic space, or storm-lit sky. The mood represents inner peace, strength, and transcendence.

In the center of the image, overlay this motivational quote in bold serif font (Playfair Display or Georgia). Add soft yellow highlight behind important lines:

"{quote_text}"
—harapoint

Ensure the quote is clearly readable, centered, and doesn't cover the character's face. Use soft shadow or blur behind the text to enhance contrast. No watermarks, logos, or unnecessary design elements. Keep the artwork emotionally intense and heroic in anime style.
"""
    }
    
    VIRAL_TEMPLATES = {
        "maturity_when": """
Create a viral Instagram quote starting with "Maturity is when" for {audience} about {theme}.

Rules for viral content:
- Title: "Maturity is when"
- Quote: Complete the sentence with something deeply relatable and profound
- Keep quote under 25 words
- Make it hit emotional triggers
- Use simple but powerful language
- Focus on personal growth and wisdom
- Make it shareable and quotable

Topic context: {custom_topic}

Format your response as:
TITLE: Maturity is when
QUOTE: [complete the maturity statement in under 25 words]
""",
        
        "painful_truth": """
Create a viral "Painful But True" Instagram quote for {audience} about {theme}.

Rules for viral content:
- Title: "Painful But True"
- Quote: A harsh but accurate life reality that hits deep
- Maximum 20 words
- Make people think "damn, that's so true"
- Touch on universal human experiences
- Create that "uncomfortable but accurate" feeling

Topic context: {custom_topic}

Format your response as:
TITLE: Painful But True
QUOTE: [harsh but accurate truth in under 20 words]
""",
        
        "not_everyone_understands": """
Create a viral "Not everyone can understand" Instagram quote for {audience} about {theme}.

Rules for viral content:
- Title: "Not everyone can understand this quote"
- Quote: Something profound that makes people feel special for understanding it
- Maximum 15 words
- Create exclusivity feeling
- Make it mysterious but relatable
- Use metaphors or deeper meaning

Topic context: {custom_topic}

Format your response as:
TITLE: Not everyone can understand this quote
QUOTE: [profound quote in under 15 words]
""",
        
        "realization": """
Create a viral realization Instagram quote for {audience} about {theme}.

Rules for viral content:
- Title: "I realized it late, but it was worth it" or similar realization phrase
- Quote: A life-changing epiphany moment
- Maximum 25 words
- Make it inspiring and relatable
- Focus on personal growth
- Create that "aha moment" feeling

Topic context: {custom_topic}

Format your response as:
TITLE: [realization title]
QUOTE: [life-changing realization in under 25 words]
""",
        
        "comparison": """
Create a viral comparison Instagram quote for {audience} about {theme}.

Rules for viral content:
- Title: Format like "MAN VS WOMAN" or "THEN VS NOW" or similar comparison
- Quote: Contrasting statements that are relatable
- Each part maximum 15 words
- Make it thought-provoking
- Create debate and discussion
- Use universal experiences

Topic context: {custom_topic}

Format your response as:
TITLE: [comparison title]
QUOTE: [comparison statements]
""",
        
        "rules_for_year": """
Create viral "Rules for 2025" Instagram content for {audience} about {theme}.

Rules for viral content:
- Title: "Rules for 2025:" or "How to get respect:"
- Quote: 3-4 short, powerful rules
- Each rule maximum 8 words
- Make them actionable and memorable
- Create authority and wisdom feeling
- Focus on self-improvement

Topic context: {custom_topic}

Format your response as:
TITLE: [rules title]
QUOTE: [3-4 short rules, each on new line]
""",
        
        "deep_quote": """
Create a deep, viral Instagram quote for {audience} about {theme}.

Rules for viral content:
- Title: Something mysterious and engaging
- Quote: Philosophical and profound
- Maximum 20 words
- Make people screenshot and save
- Create deep thinking
- Use metaphors or life analogies

Topic context: {custom_topic}

Format your response as:
TITLE: [engaging title]
QUOTE: [deep philosophical quote in under 20 words]
"""
    }

class HashtagPools:
    """Hashtag configurations"""
    
    POOLS = {
        "motivation": [
            "motivation", "mindset", "success", "goals", "growth", "inspiration",
            "hustle", "grind", "mindfulness", "selfimprovement", "winning",
            "focus", "determination", "achievement", "believe", "strength"
        ],
        "relationships": [
            "relationships", "love", "loyalty", "trust", "respect", "boundaries",
            "healing", "selflove", "toxic", "growth", "communication",
            "friendship", "family", "dating", "marriage", "connection"
        ],
        "success": [
            "success", "wealth", "money", "business", "entrepreneur", "mindset",
            "goals", "achievement", "winning", "leadership", "growth",
            "hustle", "focus", "determination", "vision", "empire"
        ],
        "life_lessons": [
            "wisdom", "life", "lessons", "growth", "mindfulness", "reality",
            "truth", "experience", "knowledge", "understanding", "awareness",
            "consciousness", "enlightenment", "perspective", "insight", "deep"
        ],
        "self_improvement": [
            "selfimprovement", "growth", "mindset", "habits", "discipline",
            "focus", "productivity", "goals", "success", "transformation",
            "change", "better", "upgrade", "evolution", "development", "progress"
        ],
        "money_mindset": [
            "money", "wealth", "financial", "rich", "abundance", "prosperity",
            "invest", "business", "entrepreneur", "freedom", "mindset",
            "success", "goals", "hustle", "empire", "luxury"
        ],
        "mental_health": [
            "mentalhealth", "healing", "selfcare", "mindfulness", "peace",
            "therapy", "growth", "wellness", "recovery", "strength",
            "resilience", "balance", "calm", "meditation", "positivity", "joy"
        ],
        "business": [
            "business", "entrepreneur", "startup", "success", "leadership",
            "strategy", "growth", "innovation", "hustle", "empire",
            "wealth", "money", "goals", "vision", "achievement", "winning"
        ]
    }
    
    GENERAL_HASHTAGS = [
        "trending", "viral", "explore", "fyp", "content", "quotes",
        "thoughts", "lifestyle", "freedom", "power", "energy", "vibe"
    ]
