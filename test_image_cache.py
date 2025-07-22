#!/usr/bin/env python3
"""
Test script to demonstrate the image caching system
"""

import asyncio
from src.services.story_service import StoryService
from src.utils.optimized_image_gen import optimized_generate_image, get_cache_stats

async def test_image_caching():
    """Test the image caching optimization system"""
    print("🧪 Testing Image Caching System")
    print("=" * 50)
    
    # Initialize story service
    story_service = StoryService()
    
    # Get initial cache stats
    initial_stats = story_service.get_cache_statistics()
    print(f"📊 Initial cache stats: {initial_stats['cache_stats']}")
    
    print("\n🔍 Testing image generation with caching...")
    
    # Test prompts - these should demonstrate caching behavior
    test_prompts = [
        ("A dark haunted house with eerie shadows", ["horror", "dark", "house"]),
        ("Spooky haunted mansion at night", ["horror", "dark", "house"]),  # Similar to first
        ("Bright sunny meadow with flowers", ["nature", "bright", "outdoor"]),
        ("Dark forest with mysterious fog", ["horror", "dark", "forest"])
    ]
    
    generated_images = []
    
    for i, (prompt, tags) in enumerate(test_prompts, 1):
        print(f"\n{i}. Testing prompt: '{prompt}'")
        print(f"   Tags: {tags}")
        
        # Generate image with caching
        image_path = optimized_generate_image(
            prompt=prompt,
            filename=f"test_image_{i}",
            tags=tags,
            story_type="test"
        )
        
        if image_path:
            generated_images.append(image_path)
            print(f"   ✅ Result: {image_path}")
        else:
            print(f"   ❌ Generation failed")
        
        # Show cache stats after each generation
        current_stats = get_cache_stats()
        print(f"   📊 Cache: {current_stats['total_images']} images, "
              f"{current_stats['cache_hits']} hits, "
              f"{current_stats['cache_hit_rate']:.1%} hit rate")
    
    # Final statistics
    print("\n" + "=" * 50)
    print("🏁 Final Results:")
    
    final_stats = story_service.get_cache_statistics()
    cache_data = final_stats['cache_stats']
    
    print(f"📊 Cache Statistics:")
    print(f"   • Total images in cache: {cache_data['total_images']}")
    print(f"   • Total usage count: {cache_data['total_usage']}")
    print(f"   • Cache hits: {cache_data['cache_hits']}")
    print(f"   • Cache hit rate: {cache_data['cache_hit_rate']:.1%}")
    print(f"   • Vector store size: {cache_data['vector_store_size']}")
    
    print(f"\n💾 Generated images: {len(generated_images)}")
    for img in generated_images:
        print(f"   • {img}")
    
    # Test cache cleanup (dry run)
    print(f"\n🧹 Testing cache cleanup...")
    cleanup_result = story_service.cleanup_image_cache(min_usage=0, days_old=0)
    print(f"   Cleanup result: {cleanup_result['message']}")
    
    print("\n✅ Image caching system test completed!")

if __name__ == "__main__":
    asyncio.run(test_image_caching())
