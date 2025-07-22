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

def optimized_generate_image(prompt: str, filename: str, tags: List[str] = None, story_type: str = None) -> Optional[str]:
    """
    Generate image with caching optimization
    First checks vector store for similar images, only generates if not found
    """
    image_cache = get_image_cache()
    tags = tags or []
    
    # Check cache for similar images
    cached_path, is_existing = image_cache.find_or_generate_image(
        prompt=prompt,
        tags=tags,
        story_type=story_type,
        similarity_threshold=0.85
    )
    
    if is_existing:
        print(f"✅ Using cached image: {cached_path}")
        return cached_path
    
    # Generate new image with unique filename
    try:
        print(f"🔄 Generating new image: {cached_path}")
        generated_path = original_generate_image(prompt, cached_path)
        
        if generated_path:
            # Add to cache for future use
            image_cache.add_image(
                prompt=prompt,
                image_path=generated_path,
                tags=tags,
                story_type=story_type,
                additional_metadata={"original_filename": filename}
            )
            print(f"✅ Image generated and cached: {generated_path}")
            return generated_path
        else:
            print(f"❌ Image generation failed for: {prompt}")
            return None
            
    except Exception as e:
        logger.error(f"Failed to generate optimized image: {str(e)}")
        # Fallback to original function
        try:
            return original_generate_image(prompt, filename)
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

def optimized_generate_background_images(image_metadata, story_type: str = "story") -> list:
    """
    Generate background images with caching optimization
    Uses the vector store to reuse similar images
    
    Args:
        image_metadata: List of dictionaries containing image metadata
        story_type: Type of story for tagging
        
    Returns:
        List of dictionaries with image_path added to each item
    """
    if not image_metadata:
        return []
    
    print(f"🖼️ Optimizing background image generation with cache...")
    optimized_images = []
    
    # Process each image in the metadata list
    for i, img_data in enumerate(image_metadata):
        if isinstance(img_data, dict) and 'prompt' in img_data:
            prompt = img_data['prompt']
            
            # Generate tags based on prompt content
            tags = extract_tags_from_prompt(prompt)
            tags.append(story_type)
            tags.append("background")
            
            # Use optimized generation
            image_path = optimized_generate_image(
                prompt=prompt,
                filename=f"bg_image_{i:03d}",
                tags=tags,
                story_type=story_type
            )
            
            if image_path:
                # Add image_path to the original metadata
                img_data_copy = img_data.copy()
                img_data_copy['image_path'] = image_path
                optimized_images.append(img_data_copy)
                print(f"✅ Image {i+1}/{len(image_metadata)}: {image_path}")
            else:
                print(f"⚠️ Failed to generate/find image for: {prompt[:60]}...")
    
    print(f"✅ Background image optimization complete: {len(optimized_images)}/{len(image_metadata)} images")
    return optimized_images

def extract_tags_from_prompt(prompt: str) -> List[str]:
    """Extract relevant tags from image prompt for better caching"""
    prompt_lower = prompt.lower()
    
    # Common horror/story image tags
    horror_tags = []
    
    if any(word in prompt_lower for word in ['dark', 'shadow', 'night', 'black']):
        horror_tags.append('dark')
    
    if any(word in prompt_lower for word in ['forest', 'trees', 'woods']):
        horror_tags.append('forest')
    
    if any(word in prompt_lower for word in ['house', 'building', 'room', 'door']):
        horror_tags.append('building')
    
    if any(word in prompt_lower for word in ['fog', 'mist', 'smoke']):
        horror_tags.append('atmospheric')
    
    if any(word in prompt_lower for word in ['red', 'blood', 'crimson']):
        horror_tags.append('red')
    
    if any(word in prompt_lower for word in ['scary', 'horror', 'creepy', 'spooky']):
        horror_tags.append('horror')
    
    if any(word in prompt_lower for word in ['abandoned', 'empty', 'deserted']):
        horror_tags.append('abandoned')
    
    if any(word in prompt_lower for word in ['corridor', 'hallway', 'tunnel']):
        horror_tags.append('corridor')
    
    return horror_tags

def get_cache_stats() -> Dict:
    """Get image cache statistics"""
    image_cache = get_image_cache()
    return image_cache.get_cache_stats()

def cleanup_cache(min_usage: int = 1, days_old: int = 30) -> int:
    """Clean up unused images from cache"""
    image_cache = get_image_cache()
    return image_cache.cleanup_unused_images(min_usage, days_old)
