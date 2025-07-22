#!/usr/bin/env python3
"""
Test script to verify background images are stored in bg_images directory
"""

import os
from pathlib import Path
from src.utils.optimized_image_gen import optimized_generate_background_images

def test_background_image_directory():
    """Test that background images are stored in bg_images directory"""
    print("🧪 Testing Background Image Directory Storage")
    print("=" * 50)
    
    # Test metadata - similar to what would be generated
    test_metadata = [
        {
            'prompt': 'A dark haunted house with eerie shadows at midnight',
            'start_time': 0,
            'end_time': 5
        },
        {
            'prompt': 'Spooky graveyard with ancient tombstones and fog',
            'start_time': 5,
            'end_time': 10
        }
    ]
    
    print(f"📋 Test metadata: {len(test_metadata)} images")
    
    # Check initial state of bg_images directory
    bg_dir = Path("bg_images")
    print(f"📁 bg_images directory exists: {bg_dir.exists()}")
    
    if bg_dir.exists():
        initial_files = list(bg_dir.glob("*"))
        print(f"📁 Initial files in bg_images: {len(initial_files)}")
    
    # Test the optimized function
    print("\n🖼️ Testing optimized background image generation...")
    try:
        result = optimized_generate_background_images(
            image_metadata=test_metadata,
            story_type="horror",
            output_dir="bg_images"
        )
        
        print(f"\n📊 Results:")
        print(f"   • Images processed: {len(result)}")
        
        # Check what files were created/referenced
        if bg_dir.exists():
            final_files = list(bg_dir.glob("*"))
            print(f"   • Files in bg_images after: {len(final_files)}")
            
            for file in final_files[:5]:  # Show first 5 files
                print(f"     - {file.name}")
        
        # Check the image paths in the result
        print(f"\n📄 Image paths in result:")
        for i, img in enumerate(result):
            if 'image_path' in img:
                path = img['image_path']
                print(f"   {i+1}. {path}")
                
                # Check if path includes bg_images directory
                if 'bg_images' in path:
                    print(f"      ✅ Correctly using bg_images directory")
                else:
                    print(f"      ⚠️ Not using bg_images directory")
                    
                # Check if file exists
                if os.path.exists(path):
                    print(f"      ✅ File exists")
                else:
                    print(f"      ❌ File does not exist")
        
        print(f"\n✅ Test completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_background_image_directory()
