#!/usr/bin/env python3
"""
Story Generation Service
Integrates the video-audio story generation functionality
"""

import os
import sys
import random
import asyncio
from typing import Optional, Dict, List, Tuple
from pathlib import Path
import concurrent.futures
from datetime import datetime

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
from ..utils.azure_utils import AzureBlobManager, FileManager
from ..utils.job_database import JobDatabase, JobStatus
from ..utils.image_vector_store import get_image_cache
from ..utils.optimized_image_gen import optimized_generate_background_images, get_cache_stats

class StoryService:
    """Service for generating story content with video and metadata"""
    
    def __init__(self):
        self.video_output_dir = Path(__file__).parent.parent.parent / "story_videos"
        self.video_output_dir.mkdir(exist_ok=True)
        
        # Initialize Azure Blob Manager for video uploads
        self.blob_manager = AzureBlobManager(
            connection_string=Config.AZURE_STORAGE_CONNECTION_STRING,
            container_name=Config.AZURE_CONTAINER_NAME
        )
        
        # Initialize image cache for optimization
        self.image_cache = get_image_cache()
        
        # Initialize job database
        self.job_db = JobDatabase()
        
    def create_story_job(self, story_type: str = "random", custom_job: Optional[str] = None, 
                        custom_location: Optional[str] = None, custom_theme: Optional[str] = None,
                        language: str = "Hindi") -> Dict:
        """Create a new story generation job"""
        try:
            job_id = self.job_db.create_job(
                story_type=story_type,
                custom_job=custom_job,
                custom_location=custom_location,
                custom_theme=custom_theme,
                language=language
            )
            
            return {
                "job_id": job_id,
                "status": JobStatus.pending,
                "message": "Story generation job created successfully",
                "created_at": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "job_id": "",
                "status": JobStatus.failed,
                "message": "Failed to create story generation job",
                "error": str(e),
                "created_at": datetime.now().isoformat()
            }
    
    def get_job_status(self, job_id: str) -> Dict:
        """Get the status of a story generation job"""
        try:
            job_data = self.job_db.get_job(job_id)
            if not job_data:
                return {
                    "job_id": job_id,
                    "status": JobStatus.failed,
                    "error_message": "Job not found"
                }
            
            return {
                "job_id": job_id,
                "status": job_data["status"],
                "created_at": job_data["created_at"],
                "started_at": job_data.get("started_at"),
                "completed_at": job_data.get("completed_at"),
                "progress_message": self._get_progress_message(job_data["status"]),
                "error_message": job_data.get("error_message")
            }
        except Exception as e:
            return {
                "job_id": job_id,
                "status": JobStatus.failed,
                "error_message": str(e)
            }
    
    def get_job_result(self, job_id: str) -> Dict:
        """Get the result of a completed story generation job"""
        try:
            job_data = self.job_db.get_job(job_id)
            if not job_data:
                return {
                    "success": False,
                    "message": "Job not found",
                    "error": "Job not found"
                }
            
            if job_data["status"] != JobStatus.completed:
                return {
                    "success": False,
                    "message": f"Job is {job_data['status']}, not completed",
                    "status": job_data["status"]
                }
            
            return {
                "story_text": job_data["story_text"] or "",
                "story_type": job_data["story_type"],
                "video_url": job_data["video_url"],
                "audio_filename": job_data["audio_filename"],
                "instagram_caption": job_data["instagram_caption"] or "",
                "youtube_title": job_data["youtube_title"] or "",
                "youtube_description": job_data["youtube_description"] or "",
                "youtube_tags": job_data["youtube_tags"] or [],
                "hashtags": job_data["hashtags"] or [],
                "success": True,
                "message": "Story generation completed successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "message": "Failed to retrieve job result",
                "error": str(e)
            }
    
    async def process_job(self, job_id: str):
        """Process a story generation job asynchronously"""
        try:
            # Get job details
            job_data = self.job_db.get_job(job_id)
            if not job_data:
                return
            
            # Update status to in_progress
            self.job_db.update_job_status(job_id, JobStatus.in_progress, started_at=datetime.now())
            
            # Generate story content
            result = await self.generate_story_content(
                story_type=job_data["story_type"],
                custom_job=job_data["custom_job"],
                custom_location=job_data["custom_location"],
                custom_theme=job_data["custom_theme"],
                language=job_data["language"]
            )
            
            # Update job with results
            self.job_db.update_job_result(job_id, result)
            
        except Exception as e:
            # Update job as failed
            self.job_db.update_job_status(job_id, JobStatus.failed, error_message=str(e))
    
    def _get_progress_message(self, status: str) -> Optional[str]:
        """Get user-friendly progress message"""
        messages = {
            JobStatus.pending: "Job is waiting to be processed",
            JobStatus.in_progress: "Generating story content and video...",
            JobStatus.completed: "Story generation completed successfully",
            JobStatus.failed: "Story generation failed"
        }
        return messages.get(status)
        
    async def generate_story_content(self, story_type: str = "random", custom_job: Optional[str] = None, 
                             custom_location: Optional[str] = None, custom_theme: Optional[str] = None,
                             language: str = "Hindi") -> Dict:
        """
        Generate complete story content including video, metadata, and social media content
        This runs asynchronously to avoid blocking other API requests
        """
        try:
            # Step 1: Generate story based on type (run in thread pool for CPU-bound operations)
            story_text = await self._generate_story_by_type_async(story_type, custom_job, custom_location, custom_theme)
            
            # Step 2: Generate video (run in background thread)
            video_filename = f"story_{story_type}_{random.randint(1000, 9999)}.mp4"
            video_path = self.video_output_dir / video_filename
            
            # Create styled story for TTS
            styled_story = f"""
            Style: horror storytelling. Use a calm, eerie tone with subtle pauses. 
            Build quiet tension — unsettling but never loud. Let the fear creep in slowly. 
            Story should end within 1 minute.
            
            {story_text}
            """
            
            # Generate video asynchronously with optimized image caching
            video_result = await self._generate_video_with_optimized_images_async(styled_story, str(video_path), language, story_type)
            
            # Upload video to Azure Blob if generation was successful
            video_url = None
            if video_result and video_path.exists():
                try:
                    # Upload to Azure Blob Storage
                    blob_name = f"{Config.AZURE_VIDEO_FOLDER}/{video_filename}"
                    video_url = await self._upload_video_to_blob_async(str(video_path), blob_name)
                    
                    # Clean up local file after successful upload
                    video_path.unlink()
                    print(f"✅ Video uploaded to Azure: {video_url}")
                except Exception as e:
                    print(f"⚠️ Failed to upload video to Azure: {e}")
                    # Keep local path as fallback
                    video_url = str(video_path)
            
            # Step 3: Upload video to Azure Blob Storage if video was generated
            video_url = None
            if video_result and video_path.exists():
                try:
                    # Generate unique filename for Azure
                    blob_filename = FileManager.generate_filename("story_video", "mp4")
                    
                    # Upload to Azure Blob Storage in the video folder
                    video_url = await self.blob_manager.upload_file_async(
                        str(video_path), 
                        blob_filename, 
                        folder=Config.AZURE_VIDEO_FOLDER
                    )
                    
                    # Clean up local file after successful upload
                    FileManager.cleanup_temp_files(str(video_path))
                    print(f"✅ Video uploaded to Azure: {video_url}")
                    
                except Exception as e:
                    print(f"⚠️ Failed to upload video to Azure: {e}")
                    # Fallback to local path if Azure upload fails
                    video_url = str(video_path)
            
            # Step 4: Generate social media metadata (run in parallel)
            instagram_caption_task = asyncio.create_task(self._generate_instagram_caption_async(story_text, story_type))
            youtube_metadata_task = asyncio.create_task(self._generate_youtube_metadata_async(story_text, story_type))
            hashtags_task = asyncio.create_task(self._generate_hashtags_async(story_type))
            
            # Wait for all metadata generation tasks to complete
            instagram_caption = await instagram_caption_task
            youtube_title, youtube_description, youtube_tags = await youtube_metadata_task
            hashtags = await hashtags_task
            
            return {
                "story_text": story_text,
                "story_type": story_type,
                "video_url": video_url,  # Now returns Azure blob URL
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
    
    async def _generate_story_by_type_async(self, story_type: str, custom_job: Optional[str] = None,
                               custom_location: Optional[str] = None, custom_theme: Optional[str] = None) -> str:
        """Generate story based on specified type asynchronously"""
        loop = asyncio.get_event_loop()
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            if story_type == "job":
                return await loop.run_in_executor(
                    executor, generate_job_horror_story, custom_job, custom_location
                )
            elif story_type == "horror":
                return await loop.run_in_executor(
                    executor, generate_general_horror_story, custom_theme, custom_location
                )
            elif story_type == "random":
                return await loop.run_in_executor(
                    executor, generate_random_horror_story
                )
            else:
                # Default to random if unknown type
                return await loop.run_in_executor(
                    executor, generate_random_horror_story
                )
    
    async def _generate_video_async(self, styled_story: str, video_path: str, language: str) -> str:
        """Generate video asynchronously in background thread"""
        loop = asyncio.get_event_loop()
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            try:
                result = await loop.run_in_executor(
                    executor, complete_story_to_video_workflow, styled_story, video_path, language
                )
                # Check if the video file was actually created
                if result and Path(video_path).exists():
                    return result
                else:
                    print(f"⚠️ Video generation completed but file not found: {video_path}")
                    return None
            except Exception as e:
                print(f"❌ Video generation failed: {e}")
                return None
    
    async def _generate_video_with_optimized_images_async(self, styled_story: str, video_path: str, language: str, story_type: str) -> str:
        """Generate video with optimized image caching"""
        loop = asyncio.get_event_loop()
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            return await loop.run_in_executor(
                executor, self._optimized_video_workflow, styled_story, video_path, language, story_type
            )
    
    def _optimized_video_workflow(self, styled_story: str, video_path: str, language: str, story_type: str) -> str:
        """Custom video workflow that uses image caching"""
        try:
            # Import video-audio functions dynamically
            import sys
            from pathlib import Path
            
            video_audio_path = Path(__file__).parent.parent.parent / "video-audio"
            sys.path.insert(0, str(video_audio_path))
            
            from time1 import (
                generate_audio_from_text, extract_timestamps, 
                create_image_metadata_json, timestamp_to_seconds_simple
            )
            from video import create_video_with_background_images
            
            print("🎬 Starting optimized video workflow...")
            
            # Step 1: Generate audio
            print("🎵 Generating audio...")
            audio_file = generate_audio_from_text(styled_story, f"story_audio_{story_type}")
            if not audio_file:
                print("❌ Audio generation failed")
                return None
            
            # Step 2: Extract timestamps
            print("⏰ Extracting timestamps...")
            json_result = extract_timestamps(audio_file, language=language)
            if not json_result:
                print("❌ Timestamp extraction failed")
                return None
            
            # Step 3: Calculate audio duration
            try:
                import librosa
                audio_data, sr = librosa.load(audio_file, sr=None)
                total_duration = len(audio_data) / sr
                print(f"📊 Audio duration: {total_duration:.2f} seconds")
            except Exception as e:
                print(f"⚠️ Duration calculation failed: {e}")
                # Fallback: estimate from timestamps
                try:
                    import json as json_lib
                    timestamp_data = json_lib.loads(json_result.strip().replace('```json', '').replace('```', ''))
                    last_segment = max(timestamp_data, key=lambda x: timestamp_to_seconds_simple(x['time_end']))
                    total_duration = timestamp_to_seconds_simple(last_segment['time_end'])
                except:
                    total_duration = 60  # Default 1 minute
            
            if total_duration <= 0:
                print("❌ Invalid audio duration detected")
                return None
            
            # Step 4: Create image metadata
            print("📋 Creating image metadata...")
            image_metadata = create_image_metadata_json(json_result, total_duration)
            if not image_metadata:
                print("❌ Image metadata creation failed")
                return None
            
            # Step 5: Generate optimized background images
            print("🖼️ Generating optimized background images...")
            generated_images = optimized_generate_background_images(image_metadata, story_type)
            if not generated_images:
                print("⚠️ No background images generated, proceeding with basic video")
            
            # Step 6: Create video
            print("🎬 Creating final video...")
            video_result = create_video_with_background_images(
                json_result, 
                generated_images, 
                video_path, 
                audio_path=audio_file
            )
            
            if video_result:
                print(f"✅ Optimized video workflow completed: {video_result}")
                return video_result
            else:
                print("❌ Video creation failed")
                return None
                
        except Exception as e:
            print(f"❌ Optimized video workflow error: {e}")
            # Fallback to original workflow
            try:
                return complete_story_to_video_workflow(styled_story, video_path, language)
            except Exception as fallback_error:
                print(f"❌ Fallback workflow also failed: {fallback_error}")
                return None
    
    async def _upload_video_to_blob_async(self, video_path: str, blob_name: str) -> str:
        """Upload video to Azure Blob Storage asynchronously"""
        loop = asyncio.get_event_loop()
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            return await loop.run_in_executor(
                executor, self.blob_manager.upload_file, video_path, blob_name
            )
    
    def _generate_story_by_type(self, story_type: str, custom_job: Optional[str] = None,
                               custom_location: Optional[str] = None, custom_theme: Optional[str] = None) -> str:
        """Generate story based on specified type (sync version for backward compatibility)"""
        if story_type == "job":
            return generate_job_horror_story(custom_job, custom_location)
        elif story_type == "horror":
            return generate_general_horror_story(custom_theme, custom_location)
        elif story_type == "random":
            return generate_random_horror_story()
        else:
            # Default to random if unknown type
            return generate_random_horror_story()
    
    async def _generate_instagram_caption_async(self, story_text: str, story_type: str) -> str:
        """Generate Instagram caption with hashtags asynchronously"""
        loop = asyncio.get_event_loop()
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            return await loop.run_in_executor(
                executor, self._generate_instagram_caption, story_text, story_type
            )
    
    async def _generate_youtube_metadata_async(self, story_text: str, story_type: str) -> Tuple[str, str, List[str]]:
        """Generate YouTube title, description, and tags asynchronously"""
        loop = asyncio.get_event_loop()
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            return await loop.run_in_executor(
                executor, self._generate_youtube_metadata, story_text, story_type
            )
    
    async def _generate_hashtags_async(self, story_type: str) -> List[str]:
        """Generate relevant hashtags for the story type asynchronously"""
        loop = asyncio.get_event_loop()
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            return await loop.run_in_executor(
                executor, self._generate_hashtags, story_type
            )
    
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
    
    def get_cache_statistics(self) -> Dict:
        """Get image cache statistics for monitoring"""
        try:
            stats = get_cache_stats()
            return {
                "success": True,
                "cache_stats": stats,
                "message": "Cache statistics retrieved successfully"
            }
        except Exception as e:
            return {
                "success": False,
                "cache_stats": {},
                "message": f"Failed to get cache statistics: {str(e)}"
            }
    
    def cleanup_image_cache(self, min_usage: int = 1, days_old: int = 30) -> Dict:
        """Clean up unused images from cache"""
        try:
            from ..utils.optimized_image_gen import cleanup_cache
            cleaned_count = cleanup_cache(min_usage, days_old)
            return {
                "success": True,
                "cleaned_images": cleaned_count,
                "message": f"Successfully cleaned {cleaned_count} unused images"
            }
        except Exception as e:
            return {
                "success": False,
                "cleaned_images": 0,
                "message": f"Cache cleanup failed: {str(e)}"
            }
