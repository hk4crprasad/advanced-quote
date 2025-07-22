#!/usr/bin/env python3
"""
Test script for job workspace functionality
"""

import asyncio
from pathlib import Path
from src.services.story_service import StoryService
from src.utils.job_database import JobDatabase

async def test_job_workspace():
    """Test the job workspace creation and management"""
    print("🧪 Testing Job Workspace System")
    print("=" * 50)
    
    # Initialize services
    story_service = StoryService()
    job_db = JobDatabase()
    
    # Create a test job
    print("1. Creating test job...")
    job_id = job_db.create_job("random", language="Hindi")
    print(f"   Job ID: {job_id}")
    
    # Test workspace creation
    print("2. Creating job workspace...")
    workspace = story_service._create_job_workspace(job_id)
    
    print(f"   Base directory: {workspace['base']}")
    print(f"   Audio directory: {workspace['audio']}")
    print(f"   Video directory: {workspace['video']}")
    print(f"   Temp directory: {workspace['temp']}")
    print(f"   BG Images directory: {workspace['bg_images']}")
    
    # Verify directories exist
    for name, path in workspace.items():
        if path.exists():
            print(f"   ✅ {name} directory exists: {path}")
        else:
            print(f"   ❌ {name} directory missing: {path}")
    
    # Check bg_images is global
    bg_images = Path("bg_images")
    if bg_images.exists():
        print(f"   ✅ Global bg_images directory: {bg_images}")
        # List any existing images
        images = list(bg_images.glob("*.jpg")) + list(bg_images.glob("*.png"))
        print(f"   📊 Existing images in bg_images: {len(images)}")
    else:
        print(f"   ⚠️ Global bg_images directory not found")
    
    # Check if job_workspaces directory structure looks correct
    print("\n3. Checking workspace structure...")
    job_workspaces = Path("job_workspaces")
    if job_workspaces.exists():
        print(f"   📁 Main workspace directory: {job_workspaces}")
        
        # List all job directories
        job_dirs = list(job_workspaces.iterdir())
        print(f"   📊 Total job workspaces: {len(job_dirs)}")
        
        if job_dirs:
            latest_job = job_dirs[-1]
            print(f"   📂 Latest job workspace: {latest_job.name}")
            
            # List subdirectories
            subdirs = list(latest_job.iterdir())
            print(f"   📁 Subdirectories: {[d.name for d in subdirs if d.is_dir()]}")
    
    # Test cleanup
    print("\n4. Testing workspace cleanup...")
    story_service._cleanup_job_workspace(job_id)
    
    # Verify cleanup
    job_dir = Path("job_workspaces") / job_id
    if not job_dir.exists():
        print(f"   ✅ Job workspace cleaned up successfully")
    else:
        print(f"   ⚠️ Job workspace still exists: {job_dir}")
    
    print("\n" + "=" * 50)
    print("🏁 Job workspace test completed!")

if __name__ == "__main__":
    asyncio.run(test_job_workspace())
