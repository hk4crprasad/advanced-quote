#!/usr/bin/env python3
"""
Story Generation Service
Integrates the video-audio story generation functionality
"""

import os
import sys
import random
from typing import Optional, Dict, List, Tuple
from pathlib import Path

# Add video-audio directory to path
video_audio_path = Path(__file__).parent.parent.parent / "video-audio"
sys.path.insert(0, str(video_audio_path))

# Import story generation functions
try:
    from story import (
        generate_job_horror_story,
        generate_general_horror_story, 
        generate_random_horror_story,
        generate_specific_type_story
    )
    from time1 import complete_story_to_video_workflow
except ImportError as e:
    print(f"Warning: Could not import story functions: {e}")
    # Fallback functions
    def generate_job_horror_story():
        return "Job horror story generation not available"
    def generate_general_horror_story():
        return "General horror story generation not available"
    def generate_random_horror_story():
        return "Random horror story generation not available"
    def generate_specific_type_story(story_type):
        return f"{story_type} story generation not available"
    def complete_story_to_video_workflow(story, output_video, language):
        return None

from ..core.config import Config

class StoryService:
    """Service for generating story content with video and metadata"""
    
    def __init__(self):
        self.video_output_dir = Path(__file__).parent.parent.parent / "story_videos"
        self.video_output_dir.mkdir(exist_ok=True)
        
    def generate_story_content(self, story_type: str = "random", custom_job: Optional[str] = None, 
                             custom_location: Optional[str] = None, custom_theme: Optional[str] = None,
                             language: str = "Hindi") -> Dict:
        """
        Generate complete story content including video, metadata, and social media content
        """
        try:
            # Step 1: Generate story based on type
            story_text = self._generate_story_by_type(story_type, custom_job, custom_location, custom_theme)
            
            # Step 2: Generate video
            video_filename = f"story_{story_type}_{random.randint(1000, 9999)}.mp4"
            video_path = self.video_output_dir / video_filename
            
            # Create styled story for TTS
            styled_story = f"""
            Style: horror storytelling. Use a calm, eerie tone with subtle pauses. 
            Build quiet tension — unsettling but never loud. Let the fear creep in slowly. 
            Story should end within 1 minute.
            
            {story_text}
            """
            
            # Generate video
            video_result = complete_story_to_video_workflow(
                styled_story, 
                output_video=str(video_path),
                language=language
            )
            
            # Step 3: Generate social media metadata
            instagram_caption = self._generate_instagram_caption(story_text, story_type)
            youtube_title, youtube_description, youtube_tags = self._generate_youtube_metadata(story_text, story_type)
            hashtags = self._generate_hashtags(story_type)
            
            return {
                "story_text": story_text,
                "story_type": story_type,
                "video_url": str(video_path) if video_result else None,
                "audio_filename": None,  # Could be extracted from workflow if needed
                "instagram_caption": instagram_caption,
                "youtube_title": youtube_title,
                "youtube_description": youtube_description,
                "youtube_tags": youtube_tags,
                "hashtags": hashtags,
                "success": True,
                "message": "Story content generated successfully",
                "error": None
            }
            
        except Exception as e:
            return {
                "story_text": "",
                "story_type": story_type,
                "video_url": None,
                "audio_filename": None,
                "instagram_caption": "",
                "youtube_title": "",
                "youtube_description": "",
                "youtube_tags": [],
                "hashtags": [],
                "success": False,
                "message": "Failed to generate story content",
                "error": str(e)
            }
    
    def _generate_story_by_type(self, story_type: str, custom_job: Optional[str] = None,
                               custom_location: Optional[str] = None, custom_theme: Optional[str] = None) -> str:
        """Generate story based on specified type"""
        if story_type == "job":
            return generate_job_horror_story(custom_job, custom_location)
        elif story_type == "horror":
            return generate_general_horror_story(custom_theme, custom_location)
        elif story_type == "random":
            return generate_random_horror_story()
        else:
            # Default to random if unknown type
            return generate_random_horror_story()
    
    def _generate_instagram_caption(self, story_text: str, story_type: str) -> str:
        """Generate Instagram caption with hashtags"""
        story_preview = story_text[:100] + "..." if len(story_text) > 100 else story_text
        
        caption = f"""🎬 डरावनी कहानी | Horror Story 🎬

{story_preview}

पूरी कहानी सुनने के लिए वीडियो देखें! 👆

क्या आपको यह कहानी डरावनी लगी? कमेंट में बताएं! 💀

Follow करें और डेली नई डरावनी कहानी सुनें! 

#HorrorStory #ScaryStory #HindiHorror #DarawaniKahani #HorrorShorts #CreepyTales #Horror #Suspense #Thriller #HorrorReels #ScaryReels #HorrorVideo #DarkStories #HorrorLovers #HorrorFan #HorrorContent #HorrorCommunity #HorrorFacts #ScaryFacts #HorrorTelling #StoryTime #HorrorNight #BhootKiKahani #HorrorAddict #HorrorVibes #CreepyStories #HorrorShort #viralreels #trendingreels #explorepage"""
        
        return caption
    
    def _generate_youtube_metadata(self, story_text: str, story_type: str) -> Tuple[str, str, List[str]]:
        """Generate YouTube title, description, and tags"""
        
        # Generate title
        title_templates = [
            "🎬 डरावनी कहानी जो आपको सोने नहीं देगी | Horror Story in Hindi",
            "😱 सबसे डरावनी कहानी | Scary Story That Will Give You Chills",
            "🌙 रात में मत सुनना यह कहानी | Midnight Horror Story Hindi",
            "👻 भूतिया कहानी | Real Ghost Story in Hindi",
            "💀 डरावनी सच्ची कहानी | True Horror Story Hindi"
        ]
        
        youtube_title = random.choice(title_templates)
        
        # Generate description
        story_preview = story_text[:200] + "..." if len(story_text) > 200 else story_text
        
        youtube_description = f"""🎬 डरावनी कहानी | Horror Story in Hindi

{story_preview}

यह कहानी पूरी तरह से काल्पनिक है और केवल मनोरंजन के लिए बनाई गई है।

🔔 Subscribe करें डेली नई डरावनी कहानी के लिए!
👍 Like करें अगर आपको कहानी पसंद आई!
💬 Comment में बताएं कि आपको कैसी लगी यह कहानी!
📤 Share करें अपने दोस्तों के साथ!

🎯 More Horror Content:
• डरावनी कहानियां
• भूतिया कहानियां  
• सच्ची हॉरर स्टोरी
• रहस्यमय कहानियां

⚠️ Warning: यह कहानी 18+ दर्शकों के लिए है।

#HorrorStory #HindiHorror #ScaryStory #DarawaniKahani #HorrorShorts #BhootKiKahani #HorrorVideo #ScaryVideo #HorrorReels #CreepyStory #Suspense #Thriller #HorrorContent #HorrorLovers #ScaryTales #HorrorNight #DarkStories #HorrorFacts #StoryTelling #HorrorTime

📱 Connect with us:
Instagram: @horror_stories_hindi
Facebook: Horror Stories Hindi

© All content is original and created for entertainment purposes."""
        
        # Generate tags
        youtube_tags = [
            "horror story", "hindi horror", "scary story", "darawani kahani",
            "horror shorts", "bhoot ki kahani", "horror video", "scary video",
            "horror reels", "creepy story", "suspense", "thriller", "hindi stories",
            "horror content", "horror lovers", "scary tales", "horror night",
            "dark stories", "horror facts", "story telling", "horror time",
            "viral horror", "trending horror", "best horror", "real horror",
            "ghost story", "paranormal", "supernatural", "mystery story",
            "horror channel", "hindi content"
        ]
        
        return youtube_title, youtube_description, youtube_tags
    
    def _generate_hashtags(self, story_type: str) -> List[str]:
        """Generate relevant hashtags for the story type"""
        base_hashtags = [
            "#HorrorStory", "#HindiHorror", "#ScaryStory", "#DarawaniKahani",
            "#HorrorShorts", "#CreepyTales", "#Horror", "#Suspense", "#Thriller"
        ]
        
        type_specific_hashtags = {
            "job": ["#JobHorror", "#WorkplaceHorror", "#OfficeHorror", "#CareerScary"],
            "horror": ["#BhootKiKahani", "#GhostStory", "#Paranormal", "#Supernatural"],
            "random": ["#RandomHorror", "#MixedHorror", "#VarietyHorror", "#AllHorror"]
        }
        
        hashtags = base_hashtags + type_specific_hashtags.get(story_type, [])
        
        # Add general engagement hashtags
        hashtags.extend([
            "#HorrorReels", "#ScaryReels", "#HorrorVideo", "#DarkStories",
            "#HorrorLovers", "#HorrorFan", "#HorrorContent", "#StoryTime",
            "#viralreels", "#trendingreels", "#explorepage", "#reels",
            "#shorts", "#viral", "#trending"
        ])
        
        return hashtags
