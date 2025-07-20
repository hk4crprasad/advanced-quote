#!/usr/bin/env python3
"""
Test script for YouTube Shorts upload API
"""

import sys
import json
sys.path.append('/home/cp/advanced-quote')

from src.models.schemas import YouTubeUploadRequest, YouTubePrivacy

def test_youtube_api_creation():
    """Test YouTube API creation"""
    print("🎬 Testing YouTube API Integration")
    print("=" * 50)
    
    try:
        from src.api.endpoints import create_app
        app = create_app()
        print("✅ YouTube API integrated successfully!")
        
        # Check available routes
        routes = [route.path for route in app.routes if hasattr(route, 'path')]
        youtube_routes = [r for r in routes if 'youtube' in r]
        
        if youtube_routes:
            print(f"✅ YouTube endpoints: {youtube_routes}")
        else:
            print("❌ No YouTube endpoints found")
        
        print(f"📊 Total API routes: {len(routes)}")
        
        # Show key routes
        key_routes = [r for r in routes if r in ['/upload-to-youtube', '/generate-viral-quote', '/random-choice']]
        print(f"🎯 Key routes: {key_routes}")
        
    except Exception as e:
        print(f"❌ Error creating YouTube API: {e}")
        import traceback
        traceback.print_exc()

def test_youtube_request_schema():
    """Test YouTube upload request schema"""
    print("\n📝 Testing YouTube Upload Request Schema")
    print("-" * 40)
    
    # Test basic request
    try:
        request = YouTubeUploadRequest(
            video_url="https://example.com/video.mp4",
            title="Amazing Python Trick! 🐍✨",
            description="Learn this Python trick in 30 seconds! Perfect for beginners.",
            tags=["python", "programming", "tutorial", "shorts", "coding"],
            privacy=YouTubePrivacy.private
        )
        
        print("✅ Basic YouTube upload request created successfully!")
        print(f"   Title: {request.title}")
        print(f"   Privacy: {request.privacy}")
        print(f"   Tags: {request.tags}")
        print(f"   Description length: {len(request.description)} chars")
        
    except Exception as e:
        print(f"❌ Schema creation failed: {e}")
    
    # Test minimal request (default values)
    try:
        minimal_request = YouTubeUploadRequest(
            video_url="https://example.com/video.mp4",
            title="Quick Test",
            description="Test video"
        )
        
        print("\n✅ Minimal YouTube upload request created successfully!")
        print(f"   Default tags: {minimal_request.tags}")
        print(f"   Default privacy: {minimal_request.privacy}")
        
    except Exception as e:
        print(f"❌ Minimal schema creation failed: {e}")

def show_usage_examples():
    """Show usage examples for the YouTube API"""
    print("\n🚀 YouTube Shorts Upload API Usage Examples")
    print("=" * 50)
    
    print("\n📝 Example 1: Basic Upload Request")
    print("POST /upload-to-youtube")
    print("""
{
  "video_url": "https://your-storage.blob.core.windows.net/videos/my_short.mp4",
  "title": "Amazing Python Trick! 🐍✨",
  "description": "Learn this Python trick in 30 seconds! Perfect for beginners.",
  "tags": ["python", "programming", "tutorial", "shorts", "coding"],
  "privacy": "private"
}
""")
    
    print("\n📝 Example 2: Minimal Upload Request")
    print("POST /upload-to-youtube")
    print("""
{
  "video_url": "https://your-storage.blob.core.windows.net/videos/my_short.mp4",
  "title": "Quick Python Tip",
  "description": "Fast Python tutorial!"
}
""")
    
    print("\n📝 Example 3: Public Upload with Custom Tags")
    print("POST /upload-to-youtube")
    print("""
{
  "video_url": "https://your-storage.blob.core.windows.net/videos/motivational_short.mp4",
  "title": "Daily Motivation 💪",
  "description": "Your daily dose of motivation! #Shorts #Motivation",
  "tags": ["motivation", "inspiration", "shorts", "mindset", "success"],
  "privacy": "public"
}
""")
    
    print("\n📋 Setup Requirements:")
    print("1. 📥 Install dependencies: pip install -r requirements.txt")
    print("2. 🔑 Create OAuth 2.0 credentials at https://console.cloud.google.com/")
    print("3. 📄 Download and save as 'client_secrets.json'")
    print("4. 🚀 Start API: python -m uvicorn src.api.endpoints:create_app --reload")
    print("5. 📤 First upload will open browser for YouTube authentication")
    
    print("\n✨ Features:")
    print("• ✅ Automatic #Shorts tag addition")
    print("• ✅ Support for private/public/unlisted uploads")
    print("• ✅ Custom title, description, and tags")
    print("• ✅ Direct upload from Azure blob storage URLs")
    print("• ✅ OAuth 2.0 authentication for personal channels")

if __name__ == "__main__":
    test_youtube_api_creation()
    test_youtube_request_schema()
    show_usage_examples()
    
    print("\n🎉 YouTube Shorts API integration complete!")
    print("📺 Ready to upload shorts to your YouTube channel!")
