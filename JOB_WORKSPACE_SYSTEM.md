# Job Workspace System

## Overview
Implemented a job-specific workspace system that organizes temporary files during story generation while keeping background images in a global directory.

## Directory Structure

### Job-Specific Workspaces
```
job_workspaces/
├── {job_id_1}/
│   ├── audio/          # TTS-generated audio files
│   ├── video/          # Video processing and output
│   └── temp/           # Temporary processing files
├── {job_id_2}/
│   ├── audio/
│   ├── video/
│   └── temp/
└── ...
```

### Global Image Storage
```
bg_images/              # All background images (shared across jobs)
├── job_random_bg_image_000.jpg
├── job_horror_bg_image_001.jpg
├── cached_image_xyz.jpg
└── ...
```

## Key Features

### 1. Isolated Job Processing
- Each job gets its own workspace directory
- Prevents file conflicts between concurrent jobs
- Organized temporary file management
- Easy debugging with preserved failed job workspaces

### 2. Global Image Sharing
- Background images stored in shared `bg_images` directory
- Enables image caching and reuse across different jobs
- Optimizes storage by avoiding duplicate images
- Vector store can reference images across all jobs

### 3. Automatic Cleanup
- **Success**: Workspace deleted after successful database update
- **Failure**: Workspace preserved for debugging
- Only temporary processing files are cleaned up
- Background images persist for reuse

## Workflow

### Job Processing Steps
1. **Create Workspace**: `job_workspaces/{job_id}/`
2. **Generate Audio**: Save in `{job_id}/audio/`
3. **Process Video**: Work in `{job_id}/video/`
4. **Generate Images**: Save in global `bg_images/`
5. **Upload to Azure**: Video uploaded to cloud storage
6. **Update Database**: Store results in SQLite
7. **Cleanup**: Remove job workspace (success) or preserve (failure)

### File Lifecycle
```
Job Start → Workspace Created → Audio Generated → Images Generated → Video Created
    ↓                            ↓                 ↓                  ↓
Job Temp Files              Job Temp Files    Global bg_images   Job Temp Files
    ↓                            ↓                 ↓                  ↓
Upload Success → Database Updated → Workspace Deleted → Images Remain
```

## Benefits

### 1. Organization
- Clear separation of temporary vs permanent files
- Job-specific isolation prevents conflicts
- Global image sharing enables optimization

### 2. Performance
- Background images cached and reused
- Parallel job processing without interference
- Efficient storage management

### 3. Debugging
- Failed jobs preserve workspace for investigation
- Clear file organization for troubleshooting
- Logs indicate workspace locations

### 4. Storage Optimization
- Shared background images reduce duplication
- Automatic cleanup of temporary files
- Vector store enables intelligent image reuse

## Configuration

### Directory Paths
- **Job Workspaces**: `job_workspaces/{job_id}/`
- **Background Images**: `bg_images/`
- **Vector Store**: `image_cache/vector_store/`
- **Final Videos**: Uploaded to Azure (local copies removed)

### Cleanup Policy
- **Success**: Immediate workspace cleanup after database update
- **Failure**: Workspace preserved indefinitely for debugging
- **Manual Cleanup**: Can be triggered via admin interface

## Usage Examples

### Story Service Integration
```python
# Workspace is automatically created and managed
async def process_job(self, job_id: str):
    workspace = self._create_job_workspace(job_id)
    
    # Generate content using workspace
    result = await self.generate_story_content_with_workspace(
        job_id, workspace, story_type, ...
    )
    
    # Automatic cleanup based on success/failure
    if result.get('success'):
        self._cleanup_job_workspace(job_id)
```

### File Organization
```python
# Audio files in job workspace
audio_path = workspace["audio"] / "story_audio.wav"

# Video processing in job workspace  
video_path = workspace["video"] / "story_video.mp4"

# Images in global directory
image_path = workspace["bg_images"] / "bg_image_001.jpg"
```

## Monitoring

### Workspace Status
- Active workspaces indicate ongoing jobs
- Preserved workspaces indicate failed jobs needing attention
- Empty `job_workspaces/` directory indicates all jobs completed successfully

### Storage Usage
- Monitor `bg_images/` directory size for image cache growth
- Track `job_workspaces/` for any stuck or failed jobs
- Vector store size indicates caching effectiveness

## Maintenance

### Regular Cleanup
```bash
# Clean up old failed job workspaces (optional)
find job_workspaces/ -type d -mtime +7 -exec rm -rf {} \;

# Monitor bg_images directory size
du -sh bg_images/

# Check vector store statistics
python -c "from src.utils.optimized_image_gen import get_cache_stats; print(get_cache_stats())"
```

### Troubleshooting
1. **Failed Jobs**: Check preserved workspace in `job_workspaces/{job_id}/`
2. **Missing Images**: Verify `bg_images/` directory permissions
3. **Storage Issues**: Monitor disk usage of workspace directories
4. **Concurrency**: Each job has isolated workspace preventing conflicts

## Integration Notes

### Backward Compatibility
- Original story generation still works
- New workspace system is opt-in for async job processing
- Existing image generation falls back gracefully

### Scalability
- Supports unlimited concurrent jobs
- Global image cache improves efficiency
- Automatic cleanup prevents storage bloat

This system provides excellent organization, debugging capabilities, and storage optimization while maintaining clear separation between temporary processing files and reusable assets.
