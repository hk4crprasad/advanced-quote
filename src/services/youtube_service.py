#!/usr/bin/env python3
"""
YouTube API service for uploading shorts and videos
"""

import os
import pickle
import json
from typing import Optional, Dict, Any
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

from ..core.config import Config

class YouTubeService:
    """YouTube API service for uploading shorts and managing videos"""
    
    def __init__(self):
        # YouTube API credentials from config
        self.api_key = getattr(Config, 'YOUTUBE_API_KEY', None)
        
        # OAuth credentials for personal channel access
        self.oauth_credentials = None
        self.youtube = None
        
        # Scopes for OAuth (personal YouTube access)
        self.OAUTH_SCOPES = [
            'https://www.googleapis.com/auth/youtube.upload',
            'https://www.googleapis.com/auth/youtube',
            'https://www.googleapis.com/auth/youtube.readonly'
        ]
    
    def authenticate_oauth_for_upload(self, client_secrets_file='client_secrets.json', token_file='youtube_token.pickle'):
        """
        Authenticate using OAuth 2.0 for personal YouTube channel uploads
        This is required for uploading videos to your channel
        """
        credentials = None
        
        # Check if we have a saved token
        if os.path.exists(token_file):
            with open(token_file, 'rb') as token:
                credentials = pickle.load(token)
        
        # If no valid credentials, get new ones
        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                print("🔄 Refreshing expired YouTube token...")
                credentials.refresh(Request())
            else:
                if not os.path.exists(client_secrets_file):
                    raise FileNotFoundError(f"""
❌ {client_secrets_file} not found!

📋 To upload to YOUR YouTube channel, you need OAuth 2.0:
1. Go to https://console.cloud.google.com/
2. Navigate to 'APIs & Services' > 'Credentials'
3. Click 'Create Credentials' > 'OAuth 2.0 Client ID'
4. Choose 'Desktop Application'
5. Download and save as '{client_secrets_file}'
""")
                
                print("🌐 Opening browser for Google YouTube login...")
                flow = InstalledAppFlow.from_client_secrets_file(
                    client_secrets_file, self.OAUTH_SCOPES)
                credentials = flow.run_local_server(port=0)
            
            # Save credentials for next run
            with open(token_file, 'wb') as token:
                pickle.dump(credentials, token)
        
        self.oauth_credentials = credentials
        self.youtube = build('youtube', 'v3', credentials=credentials)
        print("✅ YouTube OAuth authentication successful!")
        return self.youtube
    
    async def upload_youtube_short(self, 
                                 video_url: str,
                                 title: str, 
                                 description: str, 
                                 tags: Optional[list] = None, 
                                 privacy: str = 'private') -> Dict[str, Any]:
        """
        Upload a YouTube Short from video URL
        
        Args:
            video_url: URL of the video file (from Azure blob storage)
            title: Video title
            description: Video description
            tags: List of tags
            privacy: 'private', 'public', or 'unlisted'
        
        Returns:
            Dict with upload result
        """
        try:
            if not self.oauth_credentials:
                self.authenticate_oauth_for_upload()
            
            # Download video from URL to temporary file
            from ..utils.azure_utils import FileManager
            temp_video_path = await FileManager.download_from_url(video_url, '.mp4')
            
            # Upload the short
            result = await self._upload_short_to_youtube(
                temp_video_path, title, description, tags, privacy
            )
            
            # Clean up temporary file
            if os.path.exists(temp_video_path):
                os.remove(temp_video_path)
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "video_id": None,
                "video_url": None
            }
    
    async def _upload_short_to_youtube(self, 
                                     video_file: str,
                                     title: str, 
                                     description: str, 
                                     tags: Optional[list] = None, 
                                     privacy: str = 'private') -> Dict[str, Any]:
        """
        Internal method to upload YouTube Short
        """
        if not self.oauth_credentials:
            raise ValueError("❌ OAuth authentication required to upload YouTube Shorts!")
        
        if not os.path.exists(video_file):
            raise FileNotFoundError(f"Video file not found: {video_file}")
        
        # Prepare tags and description for Shorts
        tags = tags or []
        if 'Shorts' not in tags:
            tags.append('Shorts')
        
        # Ensure #Shorts is in description
        if '#Shorts' not in description:
            description = f"{description}\n\n#Shorts"
        
        body = {
            'snippet': {
                'title': title,
                'description': description,
                'tags': tags,
                'categoryId': '24'  # Entertainment category
            },
            'status': {
                'privacyStatus': privacy
            }
        }
        
        # Create media upload object
        media = MediaFileUpload(video_file, resumable=True)
        
        print(f"📱 Starting YouTube Short upload: '{title}'")
        
        try:
            # Execute upload
            request = self.youtube.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=media
            )
            
            response = await self._resumable_upload(request, is_short=True)
            
            if response and 'id' in response:
                video_id = response['id']
                return {
                    "success": True,
                    "video_id": video_id,
                    "video_url": f"https://www.youtube.com/watch?v={video_id}",
                    "shorts_url": f"https://www.youtube.com/shorts/{video_id}",
                    "title": title,
                    "privacy": privacy,
                    "message": "YouTube Short uploaded successfully!"
                }
            else:
                return {
                    "success": False,
                    "error": "Upload failed - no video ID returned",
                    "response": response
                }
                
        except HttpError as e:
            return {
                "success": False,
                "error": f"YouTube API error: {str(e)}",
                "video_id": None
            }
    
    async def _resumable_upload(self, request, is_short=False):
        """
        Handle resumable upload with progress
        """
        response = None
        error = None
        retry = 0
        
        video_type = "Short 📱" if is_short else "Video 🎬"
        
        while response is None:
            try:
                status, response = request.next_chunk()
                if status:
                    print(f"📤 {video_type} upload {int(status.progress() * 100)}% complete...")
            except HttpError as e:
                if e.resp.status in [500, 502, 503, 504]:
                    error = e
                    if retry < 3:
                        retry += 1
                        print(f"🔄 Upload failed, retrying ({retry}/3)...")
                    else:
                        raise e
                else:
                    raise e
        
        if 'id' in response:
            print(f"✅ {video_type} upload successful!")
            print(f"📺 Video ID: {response['id']}")
            print(f"🔗 Watch at: https://www.youtube.com/watch?v={response['id']}")
            if is_short:
                print(f"📱 Shorts URL: https://www.youtube.com/shorts/{response['id']}")
        else:
            print(f"❌ {video_type} upload failed: {response}")
        
        return response
    
    def get_channel_info(self):
        """
        Get YOUR channel information (requires OAuth)
        """
        if not self.oauth_credentials:
            raise ValueError("OAuth authentication required for personal channel access")
        
        request = self.youtube.channels().list(
            part="snippet,contentDetails,statistics",
            mine=True
        )
        
        response = request.execute()
        return response
