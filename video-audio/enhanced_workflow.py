#!/usr/bin/env python3
"""
Enhanced Horror Story Video Generator with Background Images
Complete workflow: Story -> Audio -> Timestamps -> Background Images -> Video

Usage:
python enhanced_workflow.py

Requirements:
- pip install google-genai pillow moviepy librosa
- Set GEMINI_API_KEY environment variable
"""

import os
import sys
from story import generate_horror_story
from time1 import complete_story_to_video_workflow

def main():
    
    print("🎬 Enhanced Horror Story Video Generator")
    print("=" * 50)
    
    # Step 1: Generate horror story
    print("📝 Step 1: Generating horror story...")
    story = generate_horror_story()
    print(f"Generated story: {story[:100]}...")
    
    # Add style instructions for TTS
    styled_story = f"""
    Style: horror storytelling. Use a calm, eerie tone with subtle pauses. 
    Build quiet tension — unsettling but never loud. Let the fear creep in slowly. 
    Story should end within 1 minute.
    
    {story}
    """
    
    # Step 2: Run complete workflow with background images
    print("\n🎥 Step 2: Running complete workflow...")
    print("This will:")
    print("  - Generate audio from story")
    print("  - Extract timestamps")
    print("  - Create image metadata (5-35 images)")
    print("  - Generate horror background images")
    print("  - Create final video with smooth transitions")
    
    output_video = "enhanced_horror_story.mp4"
    result = complete_story_to_video_workflow(
        styled_story, 
        output_video=output_video, 
        language="Hindi"
    )
    
    if result:
        print(f"\n✅ SUCCESS! Video created: {result}")
        print(f"📁 Check your current directory for: {output_video}")
        print(f"🖼️  Background images saved in: bg_images/")
        print(f"🔊 Audio file also available")
    else:
        print("\n❌ FAILED: Could not create video")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())