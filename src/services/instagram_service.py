#!/usr/bin/env python3
"""
Instagram upload service
"""

import time
import requests
from typing import Dict, Any, Optional

from ..core.config import Config

class InstagramService:
    """Instagram Reels API service"""
    
    def __init__(self):
        self.base_url = Config.BASE_URL
    
    def create_reel_container(
        self, 
        video_url: str,
        access_token: str,
        instagram_user_id: str,
        caption: str = "",
        share_to_feed: bool = True,
        thumb_offset: Optional[int] = None,
        location_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a reel container"""
        endpoint = f"{self.base_url}/{instagram_user_id}/media"
        
        payload = {
            "media_type": "REELS",
            "video_url": video_url,
            "caption": caption,
            "share_to_feed": share_to_feed,
            "access_token": access_token
        }
        
        if thumb_offset is not None:
            payload["thumb_offset"] = thumb_offset
            
        if location_id:
            payload["location_id"] = location_id
        
        response = requests.post(endpoint, json=payload)
        response.raise_for_status()
        
        return response.json()
    
    def check_container_status(self, container_id: str, access_token: str) -> str:
        """Check the status of a container"""
        endpoint = f"{self.base_url}/{container_id}"
        
        params = {
            "fields": "status_code",
            "access_token": access_token
        }
        
        response = requests.get(endpoint, params=params)
        response.raise_for_status()
        
        result = response.json()
        return result.get("status_code", "UNKNOWN")
    
    def wait_for_container_ready(self, container_id: str, access_token: str, max_wait_minutes: int = 5) -> bool:
        """Wait for container to be ready for publishing"""
        max_attempts = max_wait_minutes
        
        for attempt in range(max_attempts):
            status = self.check_container_status(container_id, access_token)
            
            if status == "FINISHED":
                return True
            elif status in ["ERROR", "EXPIRED"]:
                return False
            elif status == "IN_PROGRESS":
                time.sleep(60)  # Wait 60 seconds
            else:
                time.sleep(60)
        
        return False
    
    def publish_reel(self, container_id: str, access_token: str, instagram_user_id: str) -> Dict[str, Any]:
        """Publish a reel from container"""
        endpoint = f"{self.base_url}/{instagram_user_id}/media_publish"
        
        payload = {
            "creation_id": container_id,
            "access_token": access_token
        }
        
        response = requests.post(endpoint, json=payload)
        response.raise_for_status()
        
        return response.json()
    
    def upload_reel_complete(
        self, 
        video_url: str,
        access_token: str,
        instagram_user_id: str,
        caption: str = "",
        share_to_feed: bool = True,
        thumb_offset: Optional[int] = None,
        location_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Complete reel upload process"""
        # Step 1: Create container
        container_result = self.create_reel_container(
            video_url=video_url,
            access_token=access_token,
            instagram_user_id=instagram_user_id,
            caption=caption,
            share_to_feed=share_to_feed,
            thumb_offset=thumb_offset,
            location_id=location_id
        )
        
        container_id = container_result["id"]
        
        # Step 2: Wait for ready
        if not self.wait_for_container_ready(container_id, access_token):
            raise Exception("Container failed to become ready for publishing")
        
        # Step 3: Publish
        publish_result = self.publish_reel(container_id, access_token, instagram_user_id)
        
        return {
            "container_id": container_id,
            "media_id": publish_result["id"],
            "status": "published"
        }
