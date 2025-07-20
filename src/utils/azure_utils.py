#!/usr/bin/env python3
"""
Azure utility functions for blob storage and services
"""

import uuid
import tempfile
import asyncio
from datetime import datetime
from typing import Tuple, Optional
from azure.storage.blob import BlobServiceClient
import requests

class AzureBlobManager:
    """Manage Azure Blob Storage operations"""
    
    def __init__(self, connection_string: str, container_name: str):
        self.connection_string = connection_string
        self.container_name = container_name
        self.blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        self.container_client = self.blob_service_client.get_container_client(container_name)
    
    def upload_file(self, file_data: bytes, filename: str, folder: str = "") -> str:
        """Upload file data to Azure Blob Storage"""
        try:
            # Create blob path with folder
            blob_path = f"{folder}/{filename}" if folder else filename
            
            # Upload the file
            blob_client = self.container_client.get_blob_client(blob_path)
            blob_client.upload_blob(file_data, overwrite=True)
            
            # Return the blob URL
            blob_url = f"https://{self.blob_service_client.account_name}.blob.core.windows.net/{self.container_name}/{blob_path}"
            return blob_url
            
        except Exception as e:
            raise Exception(f"Failed to upload file to blob storage: {str(e)}")
    
    async def upload_file_async(self, file_path: str, filename: str, folder: str = "") -> str:
        """Upload file asynchronously to Azure Blob Storage"""
        try:
            loop = asyncio.get_event_loop()
            
            # Create blob path with folder
            blob_path = f"{folder}/{filename}" if folder else filename
            
            # Upload the file
            blob_client = self.container_client.get_blob_client(blob_path)
            
            # Run the blocking upload operation in a thread pool
            def upload_blob():
                with open(file_path, 'rb') as file:
                    blob_client.upload_blob(file, overwrite=True)
            
            await loop.run_in_executor(None, upload_blob)
            
            # Return the blob URL
            blob_url = f"https://{self.blob_service_client.account_name}.blob.core.windows.net/{self.container_name}/{blob_path}"
            return blob_url
            
        except Exception as e:
            raise Exception(f"Failed to upload file to blob storage: {str(e)}")
    
    def delete_file(self, filename: str, folder: str = "") -> bool:
        """Delete file from Azure Blob Storage"""
        try:
            blob_path = f"{folder}/{filename}" if folder else filename
            blob_client = self.container_client.get_blob_client(blob_path)
            blob_client.delete_blob()
            return True
        except Exception:
            return False

class FileManager:
    """Manage temporary files and downloads"""
    
    @staticmethod
    async def download_from_url(url: str, suffix: str = '.tmp') -> str:
        """Download file from URL to temporary file asynchronously"""
        try:
            loop = asyncio.get_event_loop()
            
            # Run the blocking requests call in a thread pool
            response = await loop.run_in_executor(
                None, lambda: requests.get(url, timeout=30)
            )
            response.raise_for_status()
            
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
            temp_file.write(response.content)
            temp_file.close()
            
            return temp_file.name
        except Exception as e:
            raise Exception(f"Failed to download file from URL: {str(e)}")
    
    @staticmethod
    def generate_filename(prefix: str, extension: str) -> str:
        """Generate unique filename with timestamp"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        return f"{prefix}_{timestamp}_{unique_id}.{extension}"
    
    @staticmethod
    def cleanup_temp_files(*file_paths: str) -> None:
        """Clean up temporary files"""
        import os
        for file_path in file_paths:
            if file_path and os.path.exists(file_path):
                try:
                    os.unlink(file_path)
                except Exception:
                    pass  # Ignore cleanup errors
