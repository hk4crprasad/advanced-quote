# Image Caching Optimization System

## Overview
Successfully implemented a comprehensive vector store-based image caching system to optimize image generation costs by reusing semantically similar images.

## System Architecture

### 1. Vector Store Layer (`src/utils/image_vector_store.py`)
- **Technology**: OpenAI embeddings (text-embedding-3-large) + FAISS vector database
- **Purpose**: Semantic similarity search for image reuse
- **Features**:
  - Local FAISS storage for fast similarity queries
  - 0.85 similarity threshold for cache hits
  - Metadata storage (tags, usage count, timestamps)
  - Usage tracking and statistics
  - Cache cleanup functionality

### 2. Optimized Image Generation (`src/utils/optimized_image_gen.py`)
- **Purpose**: Wrapper around original image generation with caching
- **Features**:
  - Cache-first approach: check similarity before generating
  - Tag extraction from prompts for better matching
  - Fallback to original generation on errors
  - Support for both single images and background image batches

### 3. Enhanced Story Service (`src/services/story_service.py`)
- **Integration**: Added image cache to story generation workflow
- **Features**:
  - Optimized video workflow using cached images
  - Cache statistics monitoring
  - Cache cleanup management
  - Backward compatibility with original workflow

## Key Features

### Semantic Image Matching
- Uses OpenAI's text-embedding-3-large model via LiteLLM
- Compares prompts semantically, not just exact text matches
- 85% similarity threshold ensures good quality matches
- Tags enhance matching accuracy (horror, dark, house, etc.)

### Cost Optimization
- Reuses existing images for similar prompts
- Reduces redundant image generation calls
- Tracks cache hit rates for monitoring savings
- Maintains image quality through similarity thresholds

### Production Ready
- Error handling with fallback to original generation
- Usage statistics and monitoring
- Cache cleanup for old/unused images
- Async/await support for story generation workflow

## Configuration

### Environment Variables Required
```env
OPENAI_API_KEY=your_openai_key
LITELLM_BASE_URL=https://litellm.tecosys.ai/
```

### Dependencies Added
- `faiss-cpu`: Vector similarity search
- `langchain-community`: Document management
- `openai`: Embeddings API

## Usage Examples

### Direct Image Generation with Caching
```python
from src.utils.optimized_image_gen import optimized_generate_image

image_path = optimized_generate_image(
    prompt="A dark haunted house with eerie shadows",
    filename="haunted_house_1",
    tags=["horror", "dark", "house"],
    story_type="horror"
)
```

### Story Service with Optimized Workflow
```python
from src.services.story_service import StoryService

service = StoryService()

# Generate story with optimized image caching
result = await service._optimized_video_workflow(
    story_data={...},
    job_id="test_job"
)

# Monitor cache performance
stats = service.get_cache_statistics()
print(f"Cache hit rate: {stats['cache_stats']['cache_hit_rate']:.1%}")
```

### Cache Management
```python
# Get cache statistics
stats = service.get_cache_statistics()

# Cleanup old images
cleanup_result = service.cleanup_image_cache(min_usage=1, days_old=30)
```

## Testing

Run the test script to see the caching system in action:
```bash
python test_image_cache.py
```

This will demonstrate:
- Cache hits for similar prompts
- Statistics tracking
- Fallback behavior
- Performance monitoring

## Performance Benefits

### Before Implementation
- Every story generated unique images regardless of similarity
- High image generation costs for similar content
- No reuse of existing assets

### After Implementation
- Semantic similarity matching reuses appropriate images
- Significant cost reduction for similar story themes
- Intelligent cache management with usage tracking
- Maintains quality through similarity thresholds

## Monitoring & Maintenance

### Key Metrics to Track
- `cache_hit_rate`: Percentage of successful cache hits
- `total_images`: Number of unique images in cache
- `total_usage`: How often cached images are reused
- `vector_store_size`: Vector database size

### Recommended Maintenance
- Monitor cache hit rates (target >30% for good savings)
- Cleanup old/unused images periodically
- Adjust similarity threshold based on quality needs
- Review tag extraction logic for better matching

## Integration Notes

### Backward Compatibility
- Original image generation functions remain unchanged
- New optimized functions are drop-in replacements
- Fallback ensures system works even if cache fails

### Error Handling
- Graceful degradation to original generation
- Comprehensive logging for debugging
- Statistics tracking even during errors

## Future Enhancements

### Potential Improvements
1. **Advanced Tag Extraction**: Use NLP for better prompt analysis
2. **Image Quality Scoring**: Rate generated images for better caching decisions
3. **Distributed Caching**: Share cache across multiple instances
4. **Smart Cleanup**: ML-based decisions on which images to keep
5. **Usage Analytics**: Detailed reporting on cost savings

### Scalability Considerations
- FAISS scales well to millions of vectors
- Consider GPU version (faiss-gpu) for large datasets
- Monitor disk usage of cached images
- Implement cache size limits if needed

## Conclusion

The image caching optimization system successfully addresses the core requirement: **"optimise my image gen cost"** by implementing intelligent reuse of semantically similar images. The system maintains high quality through similarity thresholds while providing significant cost savings for story generation workflows with similar themes or content.

Key success metrics:
✅ Semantic similarity matching working
✅ Cache statistics and monitoring in place  
✅ Integration with existing story workflow
✅ Error handling and fallback mechanisms
✅ Production-ready code structure
✅ Comprehensive testing capabilities
