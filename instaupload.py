from config import BASE_URL, ACCESS_TOKEN, INSTAGRAM_USER_ID
from typing import Any, Dict, Optional, Tuple
import requests
import time
class InstagramReelsAPI:
    def __init__(self, access_token: str, instagram_user_id: str):
        self.access_token = access_token
        self.instagram_user_id = instagram_user_id
        self.base_url = BASE_URL
        
    def create_reel_container(
        self, 
        video_url: str, 
        caption: str = "",
        share_to_feed: bool = True,
        thumb_offset: Optional[int] = None,
        location_id: Optional[str] = None
    ) -> Dict[str, Any]:
        endpoint = f"{self.base_url}/{self.instagram_user_id}/media"
        
        payload = {
            "media_type": "REELS",
            "video_url": video_url,
            "caption": caption,
            "share_to_feed": share_to_feed,
            "access_token": self.access_token
        }
        
        if thumb_offset is not None:
            payload["thumb_offset"] = thumb_offset
            
        if location_id:
            payload["location_id"] = location_id
        
        response = requests.post(endpoint, json=payload)
        response.raise_for_status()
        
        return response.json()
    
    def check_container_status(self, container_id: str) -> str:
        endpoint = f"{self.base_url}/{container_id}"
        
        params = {
            "fields": "status_code",
            "access_token": self.access_token
        }
        
        response = requests.get(endpoint, params=params)
        response.raise_for_status()
        
        result = response.json()
        return result.get("status_code", "UNKNOWN")
    
    def wait_for_container_ready(self, container_id: str, max_wait_minutes: int = 5) -> bool:
        max_attempts = max_wait_minutes
        
        for attempt in range(max_attempts):
            status = self.check_container_status(container_id)
            
            if status == "FINISHED":
                return True
            elif status in ["ERROR", "EXPIRED"]:
                return False
            elif status == "IN_PROGRESS":
                time.sleep(60)  # Wait 60 seconds
            else:
                time.sleep(60)
        
        return False
    
    def publish_reel(self, container_id: str) -> Dict[str, Any]:
        endpoint = f"{self.base_url}/{self.instagram_user_id}/media_publish"
        
        payload = {
            "creation_id": container_id,
            "access_token": self.access_token
        }
        
        response = requests.post(endpoint, json=payload)
        response.raise_for_status()
        
        return response.json()
    
    def upload_reel_complete(
        self, 
        video_url: str, 
        caption: str = "",
        share_to_feed: bool = True,
        thumb_offset: Optional[int] = None,
        location_id: Optional[str] = None
    ) -> Dict[str, Any]:
        # Step 1: Create container
        container_result = self.create_reel_container(
            video_url=video_url,
            caption=caption,
            share_to_feed=share_to_feed,
            thumb_offset=thumb_offset,
            location_id=location_id
        )
        
        container_id = container_result["id"]
        
        # Step 2: Wait for ready
        if not self.wait_for_container_ready(container_id):
            raise Exception("Container failed to become ready for publishing")
        
        # Step 3: Publish
        publish_result = self.publish_reel(container_id)
        
        return {
            "container_id": container_id,
            "media_id": publish_result["id"],
            "status": "published"
        }

# Initialize API client
api_client = InstagramReelsAPI(ACCESS_TOKEN, INSTAGRAM_USER_ID)