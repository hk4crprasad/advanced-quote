#!/usr/bin/env python3
"""
Image generation service using Azure OpenAI DALL-E and Google Gemini
"""

import base64
import requests
import os
import random
from io import BytesIO
from PIL import Image
from typing import Tuple, Optional

from ..core.config import Config, Templates
from ..utils.azure_utils import AzureBlobManager, FileManager

try:
    from google import genai
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False
    print("⚠️ Google Gemini not available. Install with: pip install google-genai")

class ImageGenerator:
    """Generate quote images using Azure OpenAI DALL-E or Google Gemini"""
    
    def __init__(self, image_model: str = "azure"):
        self.image_model = image_model.lower()
        
        # Azure configuration
        self.endpoint = Config.AZURE_OPENAI_ENDPOINT
        self.deployment = Config.AZURE_DEPLOYMENT_NAME
        self.api_version = Config.AZURE_API_VERSION
        self.subscription_key = Config.AZURE_SUBSCRIPTION_KEY
        
        # Google configuration
        self.gemini_api_key = os.environ.get("GEMINI_API_KEY")
        
        # Azure Blob Storage setup
        self.blob_manager = AzureBlobManager(
            Config.AZURE_STORAGE_CONNECTION_STRING,
            Config.AZURE_CONTAINER_NAME
        )
        self.blob_folder = Config.AZURE_BLOB_FOLDER
        
        # Style templates
        self.style_templates = Templates.IMAGE_STYLE_TEMPLATES
        
        # Validate model availability
        if self.image_model == "google" and not GOOGLE_AVAILABLE:
            print("⚠️ Google model requested but not available, falling back to Azure")
            self.image_model = "azure"
        
        if self.image_model == "google" and not self.gemini_api_key:
            print("⚠️ GEMINI_API_KEY not found, falling back to Azure")
            self.image_model = "azure"
    
    def _decode_image_to_bytes(self, b64_data: str) -> bytes:
        """Decode base64 image data to bytes"""
        try:
            image = Image.open(BytesIO(base64.b64decode(b64_data)))
            
            # Convert to bytes
            img_byte_arr = BytesIO()
            image.save(img_byte_arr, format='JPEG', quality=90)
            img_byte_arr.seek(0)
            
            return img_byte_arr.getvalue()
        except Exception as e:
            raise Exception(f"Failed to decode image: {str(e)}")
    
    def _build_image_prompt(self, quote_text: str, style: str = "paper") -> str:
        """Build DALL-E prompt using Config templates"""
        from ..core.config import Templates
        
        # If paper style is selected, randomly choose between paper1, paper2, paper3
        if style == "paper":
            paper_styles = ["paper", "paper1", "paper2", "paper3"]
            selected_style = random.choice(paper_styles)
            print(f"🎨 Randomly selected {selected_style} from paper styles")
        # If anime style is selected, randomly choose between anime and anime1
        elif style == "anime":
            anime_styles = ["anime", "anime1"]
            selected_style = random.choice(anime_styles)
            print(f"🎨 Randomly selected {selected_style} from anime styles")
        else:
            selected_style = style
        
        template = Templates.IMAGE_STYLE_TEMPLATES.get(selected_style, Templates.IMAGE_STYLE_TEMPLATES["paper"])
        return template.format(quote_text=quote_text).strip()
    
    def _build_google_prompt(self, quote_text: str, style: str = "paper") -> str:
        """Build Google Gemini specific prompt using Config templates"""
        from ..core.config import Templates
        
        # If paper style is selected, randomly choose between paper1, paper2, paper3
        if style == "paper":
            paper_styles = ["paper", "paper1", "paper2", "paper3"]
            selected_style = random.choice(paper_styles)
            print(f"🎨 Google Gemini randomly selected {selected_style} from paper styles")
        # If anime style is selected, randomly choose between anime and anime1
        elif style == "anime":
            anime_styles = ["anime", "anime1"]
            selected_style = random.choice(anime_styles)
            print(f"🎨 Google Gemini randomly selected {selected_style} from anime styles")
        else:
            selected_style = style
    
    def _build_google_prompt(self, quote_text: str, style: str = "paper") -> str:
        """Build Google Gemini specific prompt with quote overlay using Config templates"""
        from ..core.config import Templates
        
        # If paper style is selected, randomly choose between paper1, paper2, paper3
        if style == "paper":
            paper_styles = ["paper", "paper1", "paper2", "paper3"]
            selected_style = random.choice(paper_styles)
            print(f"🎨 Google Gemini randomly selected {selected_style} from paper styles")
        # If anime style is selected, randomly choose between anime and anime1
        elif style == "anime":
            anime_styles = ["anime", "anime1"]
            selected_style = random.choice(anime_styles)
            print(f"🎨 Google Gemini randomly selected {selected_style} from anime styles")
        else:
            selected_style = style
        
        # Get the actual template from config
        config_template = Templates.IMAGE_STYLE_TEMPLATES.get(selected_style, Templates.IMAGE_STYLE_TEMPLATES["paper"])
        
        # Use the config template directly and format it with the quote
        base_prompt = config_template.format(quote_text=quote_text)
        
        # Enhance for Google Gemini's specific requirements
        enhanced_prompt = f"""{base_prompt}

Additional requirements for Google Gemini:
- Create a square image (1:1 aspect ratio) 
- Make it Instagram-ready and professional
- Ensure text is clearly readable and well-contrasted
- Focus on the quote as the main visual element
- Use clean, modern typography
- No extra decorative elements beyond what's specified in the template"""
        
        return enhanced_prompt
    
    def _generate_with_google(self, quote_text: str, style: str = "paper") -> Tuple[str, str]:
        """Generate image using Google Gemini"""
        try:
            if not GOOGLE_AVAILABLE:
                raise Exception("Google Gemini not available")
            
            if not self.gemini_api_key:
                raise Exception("GEMINI_API_KEY not configured")
            
            # Initialize client
            client = genai.Client(api_key=self.gemini_api_key)
            
            # Build prompt
            prompt = self._build_google_prompt(quote_text, style)
            
            # Generate image
            result = client.models.generate_images(
                model="models/imagen-4.0-ultra-generate-preview-06-06",
                prompt=prompt,
                config=dict(
                    number_of_images=1,
                    output_mime_type="image/jpeg",
                    person_generation="ALLOW_ADULT",
                    aspect_ratio="1:1",
                ),
            )
            
            if not result.generated_images:
                raise Exception("No images generated by Google Gemini")
            
            if len(result.generated_images) != 1:
                raise Exception("Unexpected number of images generated")
            
            # Get image bytes
            generated_image = result.generated_images[0]
            image_bytes = generated_image.image.image_bytes
            
            # Generate unique filename
            filename = FileManager.generate_filename("quote_image_google", "jpeg")
            
            # Upload to Azure Blob Storage
            blob_url = self.blob_manager.upload_file(image_bytes, filename, self.blob_folder)
            
            return filename, blob_url
            
        except Exception as e:
            raise Exception(f"Google Gemini image generation failed: {str(e)}")
    
    def generate_image(self, quote_text: str, style: str = "paper") -> Tuple[str, str]:
        """
        Generate an image for the given quote and upload to Azure Blob Storage
        
        Args:
            quote_text: The complete quote text (content only, no title)
            style: Image style (paper, modern, minimal)
            
        Returns:
            Tuple of (image_filename, blob_url)
        """
        print(f"🎨 Generating image using {self.image_model.upper()} model with {style} style")
        
        if self.image_model == "google":
            return self._generate_with_google(quote_text, style)
        else:
            return self._generate_with_azure(quote_text, style)
    
    def _generate_with_azure(self, quote_text: str, style: str = "paper") -> Tuple[str, str]:
        """Generate image using Azure OpenAI DALL-E"""
        try:
            # Build the custom prompt
            custom_prompt = self._build_image_prompt(quote_text, style)
            
            # Build request URL
            base_path = f'openai/deployments/{self.deployment}/images'
            params = f'?api-version={self.api_version}'
            generation_url = f"{self.endpoint}{base_path}/generations{params}"
            
            # Request body
            generation_body = {
                "prompt": custom_prompt,
                "n": 1,
                "size": "1024x1024",
                "quality": "medium",
                "output_format": "jpeg",
            }
            
            # Call Azure OpenAI API
            generation_response = requests.post(
                generation_url,
                headers={
                    'Api-Key': self.subscription_key,
                    'Content-Type': 'application/json',
                },
                json=generation_body,
                timeout=60
            )
            
            # Check response
            if generation_response.status_code != 200:
                raise Exception(f"API request failed with status {generation_response.status_code}: {generation_response.text}")
            
            # Parse response
            try:
                json_response = generation_response.json()
            except Exception as e:
                raise Exception(f"Failed to parse JSON response: {str(e)}")
            
            # Extract image data
            if 'data' not in json_response or not json_response['data']:
                raise Exception("No image data in response")
            
            # Get the first image
            image_data = json_response['data'][0]
            if 'b64_json' not in image_data:
                raise Exception("No base64 image data in response")
            
            # Generate unique filename
            filename = FileManager.generate_filename("quote_image", "jpeg")
            
            # Convert image to bytes
            image_bytes = self._decode_image_to_bytes(image_data['b64_json'])
            
            # Upload to Azure Blob Storage
            blob_url = self.blob_manager.upload_file(image_bytes, filename, self.blob_folder)
            
            return filename, blob_url
            
        except Exception as e:
            raise Exception(f"Image generation failed: {str(e)}")
    
    def generate_image_safe(self, quote_text: str, style: str = "paper") -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Safe version of generate_image that returns error instead of raising
        
        Returns:
            Tuple of (filename, blob_url, error_message)
        """
        try:
            filename, blob_url = self.generate_image(quote_text, style)
            return filename, blob_url, None
        except Exception as e:
            return None, None, str(e)
