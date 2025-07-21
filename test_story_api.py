#!/usr/bin/env python3
"""
Test script for the new job-based story generation API
"""

import requests
import time
import json

API_BASE = "http://localhost:8013"

def test_story_generation_workflow():
    """Test the complete story generation workflow"""
    
    print("🚀 Testing Story Generation Workflow")
    print("=" * 50)
    
    # Step 1: Create a story generation job
    print("📝 Step 1: Creating story generation job...")
    
    story_request = {
        "story_type": "random",
        "language": "Hindi"
    }
    
    try:
        response = requests.post(f"{API_BASE}/generate-story", json=story_request)
        if response.status_code == 200:
            job_data = response.json()
            job_id = job_data["job_id"]
            print(f"✅ Job created successfully!")
            print(f"   Job ID: {job_id}")
            print(f"   Status: {job_data['status']}")
        else:
            print(f"❌ Failed to create job: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Error creating job: {e}")
        return
    
    # Step 2: Check job status periodically
    print(f"\n🔍 Step 2: Monitoring job status...")
    
    max_checks = 10
    check_interval = 5  # seconds
    
    for i in range(max_checks):
        try:
            response = requests.get(f"{API_BASE}/generate-story-status/{job_id}")
            if response.status_code == 200:
                status_data = response.json()
                print(f"   Check {i+1}: {status_data['status']} - {status_data.get('progress_message', '')}")
                
                if status_data["status"] == "completed":
                    print("✅ Job completed!")
                    break
                elif status_data["status"] == "failed":
                    print(f"❌ Job failed: {status_data.get('error_message', '')}")
                    return
                    
            else:
                print(f"❌ Failed to check status: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error checking status: {e}")
        
        if i < max_checks - 1:
            time.sleep(check_interval)
    
    # Step 3: Get the final result
    print(f"\n📥 Step 3: Retrieving job result...")
    
    try:
        response = requests.get(f"{API_BASE}/generate-story/{job_id}")
        if response.status_code == 200:
            result_data = response.json()
            print("✅ Job result retrieved successfully!")
            print(f"   Story Type: {result_data['story_type']}")
            print(f"   Story Length: {len(result_data['story_text'])} characters")
            print(f"   Video URL: {result_data.get('video_url', 'None')}")
            print(f"   YouTube Title: {result_data['youtube_title']}")
            print(f"   Tags: {len(result_data['youtube_tags'])} tags")
            print(f"   Story Preview: {result_data['story_text'][:100]}...")
            
        elif response.status_code == 202:
            print("⏳ Job still in progress")
        elif response.status_code == 404:
            print("❌ Job not found")
        else:
            print(f"❌ Failed to get result: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error getting result: {e}")

if __name__ == "__main__":
    test_story_generation_workflow()
