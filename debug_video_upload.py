#!/usr/bin/env python3
"""
Debug script to test Azure blob upload and database storage
"""

import asyncio
import os
from pathlib import Path
from src.services.story_service import StoryService
from src.utils.job_database import JobDatabase, JobStatus

async def test_video_upload_and_db_storage():
    """Test video upload to Azure and database storage"""
    print("🧪 Testing Video Upload and Database Storage")
    print("=" * 60)
    
    # Initialize services
    story_service = StoryService()
    job_db = JobDatabase()
    
    # Create a test job
    print("1. Creating test job...")
    job_id = job_db.create_job("random", language="Hindi")
    print(f"   Job ID: {job_id}")
    
    # Check if there are any existing video files to test with
    video_dir = Path("story_videos")
    if video_dir.exists():
        video_files = list(video_dir.glob("*.mp4"))
        if video_files:
            test_video = video_files[0]
            print(f"2. Found test video: {test_video}")
            print(f"   File exists: {test_video.exists()}")
            if test_video.exists():
                file_size = test_video.stat().st_size
                print(f"   File size: {file_size} bytes ({file_size / (1024*1024):.2f} MB)")
            
            # Test Azure upload directly
            print("3. Testing Azure blob upload...")
            try:
                from src.utils.azure_utils import FileManager
                blob_filename = FileManager.generate_filename("test_video", "mp4")
                
                video_url = await story_service.blob_manager.upload_file_async(
                    str(test_video), 
                    blob_filename, 
                    folder="video-gen"
                )
                print(f"   ✅ Upload successful: {video_url}")
                
                # Test database update
                print("4. Testing database update...")
                test_result = {
                    "story_text": "Test story content",
                    "video_url": video_url,
                    "audio_filename": "test_audio.wav",
                    "instagram_caption": "Test caption",
                    "youtube_title": "Test title",
                    "youtube_description": "Test description",
                    "youtube_tags": ["test", "video"],
                    "hashtags": ["#test", "#video"],
                    "success": True,
                    "message": "Test successful"
                }
                
                job_db.update_job_result(job_id, test_result)
                
                # Verify database update
                print("5. Verifying database update...")
                updated_job = job_db.get_job(job_id)
                if updated_job:
                    print(f"   ✅ Job status: {updated_job['status']}")
                    print(f"   ✅ Video URL stored: {updated_job['video_url']}")
                    print(f"   ✅ Story text: {updated_job['story_text'][:50]}...")
                else:
                    print("   ❌ Failed to retrieve updated job")
                    
            except Exception as e:
                print(f"   ❌ Upload failed: {e}")
                import traceback
                traceback.print_exc()
        else:
            print("2. No existing video files found to test with")
    else:
        print("2. No video directory found")
    
    print("\n" + "=" * 60)
    print("🏁 Test completed!")

if __name__ == "__main__":
    asyncio.run(test_video_upload_and_db_storage())
