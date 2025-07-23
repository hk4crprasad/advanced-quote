#!/usr/bin/env python3
"""
Optimized image generation wrapper that uses vector store caching
"""

import os
import sys
import logging
from pathlib import Path
from typing import List, Dict, Optional, Any

# Add video-audio directory to path
video_audio_path = Path(__file__).parent.parent.parent / "video-audio"
sys.path.insert(0, str(video_audio_path))

try:
    from time1 import generate_image_from_prompt as original_generate_image
    from time1 import generate_background_images as original_generate_background_images
except ImportError:
    print("Warning: Could not import image generation functions")
    def original_generate_image(prompt, filename):
        return None
    def original_generate_background_images(metadata):
        return {}

from .image_vector_store import get_image_cache, ImageVectorStore

# Set up logging
logger = logging.getLogger(__name__)

def optimized_generate_image(prompt: str, filename: str, tags: List[str] = None, story_type: str = None, output_dir: str = "bg_images") -> Optional[str]:
    """
    Generate image with minimal caching optimization for more variety
    Uses lower similarity threshold and minimal tags to avoid repetitive images
    
    Args:
        prompt: Image generation prompt
        filename: Base filename for the image
        tags: Minimal tags for categorization (kept small for variety)
        story_type: Type of story for organization
        output_dir: Directory to store the image (default: bg_images)
    """
    import os
    import random
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    image_cache = get_image_cache()
    tags = tags or []
    
    # Add randomness to reduce cache hits and increase variety
    # 30% chance to skip cache entirely for fresh images
    skip_cache = random.random() < 0.3
    
    if not skip_cache:
        # Check cache for similar images with LOWER threshold for more variety
        cached_path, is_existing = image_cache.find_or_generate_image(
            prompt=prompt,
            tags=tags,
            story_type=story_type,
            similarity_threshold=0.65  # Lowered from 0.85 to 0.65 for more variety
        )
        
        if is_existing:
            print(f"✅ Using cached image: {cached_path}")
            return cached_path
    else:
        print(f"🎲 Skipping cache for variety: generating fresh image")
        # Generate unique filename for fresh image using existing method
        image_id = image_cache._generate_image_id(prompt, tags)
        cached_path = f"{story_type}_{prompt[:30].replace(' ', '_')}_{image_id[:8]}.jpg"
    
    # Generate new image with unique filename in the specified directory
    try:
        # Create full path with directory
        output_path = os.path.join(output_dir, cached_path)
        print(f"🔄 Generating new image: {output_path}")
        
        generated_path = original_generate_image(prompt, output_path)
        
        if generated_path:
            # Add to cache for future use (but with lower threshold, less likely to reuse)
            image_cache.add_image(
                prompt=prompt,
                image_path=generated_path,
                tags=tags,
                story_type=story_type,
                additional_metadata={"original_filename": filename, "output_dir": output_dir}
            )
            print(f"✅ Image generated and cached: {generated_path}")
            return generated_path
        else:
            print(f"❌ Image generation failed for: {prompt}")
            return None
            
    except Exception as e:
        logger.error(f"Failed to generate optimized image: {str(e)}")
        # Fallback to original function with proper directory
        try:
            fallback_path = os.path.join(output_dir, filename)
            return original_generate_image(prompt, fallback_path)
        except Exception as fallback_error:
            logger.error(f"Fallback image generation also failed: {str(fallback_error)}")
            return None
    
    # Generate new image with unique filename in the specified directory
    try:
        # Create full path with directory
        output_path = os.path.join(output_dir, cached_path)
        print(f"🔄 Generating new image: {output_path}")
        
        generated_path = original_generate_image(prompt, output_path)
        
        if generated_path:
            # Add to cache for future use
            image_cache.add_image(
                prompt=prompt,
                image_path=generated_path,
                tags=tags,
                story_type=story_type,
                additional_metadata={"original_filename": filename, "output_dir": output_dir}
            )
            print(f"✅ Image generated and cached: {generated_path}")
            return generated_path
        else:
            print(f"❌ Image generation failed for: {prompt}")
            return None
            
    except Exception as e:
        logger.error(f"Failed to generate optimized image: {str(e)}")
        # Fallback to original function with proper directory
        try:
            fallback_path = os.path.join(output_dir, filename)
            return original_generate_image(prompt, fallback_path)
        except Exception as fallback_error:
            logger.error(f"Fallback image generation also failed: {str(fallback_error)}")
            return None

def get_cache_stats() -> Dict[str, Any]:
    """Get cache usage statistics"""
    cache = ImageVectorStore()
    return cache.get_cache_stats()

def cleanup_cache(min_usage: int = 1, days_old: int = 30) -> int:
    """Clean up unused images from cache"""
    cache = ImageVectorStore()
    return cache.cleanup_old_images(min_usage, days_old)

def optimized_generate_background_images(image_metadata, story_type: str = "story", output_dir: str = "bg_images") -> list:
    """
    Generate background images with caching optimization
    Uses the vector store to reuse similar images
    
    Args:
        image_metadata: List of dictionaries containing image metadata
        story_type: Type of story for tagging
        output_dir: Directory to store background images (default: bg_images)
        
    Returns:
        List of dictionaries with image_path added to each item
    """
    import os
    
    if not image_metadata:
        return []
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"🖼️ Optimizing background image generation with cache...")
    print(f"📁 Storing images in: {output_dir}")
    optimized_images = []
    
    # Process each image in the metadata list
    for i, img_data in enumerate(image_metadata):
        if isinstance(img_data, dict) and 'prompt' in img_data:
            prompt = img_data['prompt']
            
            # Generate MINIMAL tags based on prompt content for more variety
            tags = extract_tags_from_prompt(prompt)
            # Only add story_type, remove "background" to reduce over-tagging
            tags.append(story_type)
            
            print(f"🏷️ Using minimal tags for variety: {tags}")
            
            # Use optimized generation with specified output directory
            image_path = optimized_generate_image(
                prompt=prompt,
                filename=f"bg_image_{i:03d}",
                tags=tags,
                story_type=story_type,
                output_dir=output_dir
            )
            
            if image_path:
                # Add image_path to the original metadata
                img_data_copy = img_data.copy()
                img_data_copy['image_path'] = image_path
                optimized_images.append(img_data_copy)
                print(f"✅ Image {i+1}/{len(image_metadata)}: {image_path}")
            else:
                print(f"⚠️ Failed to generate/find image for: {prompt[:60]}...")
    
    print(f"✅ Background image optimization complete: {len(optimized_images)}/{len(image_metadata)} images stored in {output_dir}")
    return optimized_images

def extract_tags_from_prompt(prompt: str) -> List[str]:
    """Extract minimal relevant tags from image prompt for diverse caching"""
    prompt_lower = prompt.lower()
    
    # Use MINIMAL tags - only 1-2 main categories to allow more variety
    minimal_tags = []
    
    # Primary setting/location (only pick ONE)
    if any(word in prompt_lower for word in ['forest', 'trees', 'woods']):
        minimal_tags.append('forest')
    elif any(word in prompt_lower for word in ['house', 'building', 'room']):
        minimal_tags.append('building')
    elif any(word in prompt_lower for word in ['hospital', 'medical']):
        minimal_tags.append('hospital')
    elif any(word in prompt_lower for word in ['cemetery', 'graveyard', 'grave']):
        minimal_tags.append('cemetery')
    elif any(word in prompt_lower for word in ['corridor', 'hallway']):
        minimal_tags.append('corridor')
    # If none of the above, don't add a location tag for maximum variety
    
    # Time of day (only if explicitly mentioned)
    if any(word in prompt_lower for word in ['night', 'midnight', 'evening']):
        minimal_tags.append('night')
    
    # Only return 1-2 minimal tags maximum to increase image variety
    return minimal_tags[:2]

def get_cache_stats() -> Dict:
    """Get image cache statistics"""
    image_cache = get_image_cache()
    return image_cache.get_cache_stats()

def cleanup_cache(min_usage: int = 1, days_old: int = 30) -> int:
    """Clean up unused images from cache"""
    image_cache = get_image_cache()
    return image_cache.cleanup_unused_images(min_usage, days_old)
