#!/usr/bin/env python3
"""
Video generation service using MoviePy
"""

import os
import asyncio
import tempfile
import random
from typing import Optional, Tuple
from moviepy import AudioFileClip, ImageClip, CompositeVideoClip, ColorClip
from moviepy.video.fx.FadeIn import FadeIn
from PIL import Image, ImageDraw, ImageFont

from ..core.config import Config
from ..utils.azure_utils import AzureBlobManager, FileManager
from .image_generator import ImageGenerator

class VideoGenerator:
    """Generate quote videos with MoviePy"""
    
    def __init__(self, image_model: str = "azure"):
        # Azure Blob Storage setup
        self.blob_manager = AzureBlobManager(
            Config.AZURE_STORAGE_CONNECTION_STRING,
            Config.AZURE_CONTAINER_NAME
        )
        self.video_folder = Config.AZURE_VIDEO_FOLDER
        
        # Video settings
        self.video_size = Config.VIDEO_SIZE
        self.title_text = Config.VIDEO_TITLE
        self.fade_in_duration = Config.FADE_IN_DURATION
        
        # Initialize image generator for creating quote images when needed
        self.image_generator = ImageGenerator(image_model=image_model)
    
    def _select_audio_file(self):
        """Randomly select an audio file and return file path and fade-in delay"""
        audio_config = random.choice(Config.AUDIO_FILES)
        audio_file = audio_config["file"]
        fade_in_delay = audio_config["fade_in_delay"]
        
        print(f"🎵 Selected audio: {audio_file} with fade-in at {fade_in_delay}s")
        return audio_file, fade_in_delay
    
    def _load_font(self, size: int):
        """Load font with fallback to default"""
        font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVu-Sans-Bold.ttf"
        ]
        
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    return ImageFont.truetype(font_path, size)
                except:
                    continue
        
        return ImageFont.load_default()
    
    def _wrap_text(self, text: str, font, draw, max_width: int, margin: int = 40):
        """Wrap text to fit within max_width"""
        words = text.split()
        lines = []
        line = ""
        
        for word in words:
            test_line = f"{line} {word}".strip()
            bbox = draw.textbbox((0, 0), test_line, font=font)
            text_width = bbox[2] - bbox[0]
            
            if text_width <= max_width - 2 * margin:
                line = test_line
            else:
                if line:
                    lines.append(line)
                    line = word
                else:
                    lines.append(word)
                    line = ""
        
        if line:
            lines.append(line)
        
        return lines
    
    def _get_best_font(self, text: str, draw, max_width: int, max_height: int, margin: int = 40, line_spacing: int = 10):
        """Find the best font size that fits the text within dimensions"""
        for size in range(100, 8, -2):
            font = self._load_font(size)
            lines = self._wrap_text(text, font, draw, max_width, margin)
            
            line_heights = []
            for line in lines:
                bbox = draw.textbbox((0, 0), line, font=font)
                line_height = bbox[3] - bbox[1]
                line_heights.append(line_height)
            
            total_height = sum(line_heights) + (len(lines) - 1) * line_spacing
            
            if total_height <= max_height - 2 * margin:
                return font, lines
        
        return self._load_font(8), self._wrap_text(text, self._load_font(8), draw, max_width, margin)
    
    async def _create_title_banner(self, text: str, width: int = None, height: int = None) -> str:
        """Create a title banner image using PIL"""
        loop = asyncio.get_event_loop()
        
        def create_banner():
            banner_width = width or self.video_size[0]
            
            # Settings
            bg_color = Config.BANNER_COLOR
            text_color = Config.TITLE_COLOR
            margin = Config.MARGIN
            line_spacing = Config.LINE_SPACING
            min_banner_height = 100
            max_banner_height = 400
            
            # Create a temporary image for text measurement
            temp_image = Image.new("RGB", (banner_width, 100), bg_color)
            draw = ImageDraw.Draw(temp_image)
            
            # Find optimal font size
            optimal_font_size = 40
            for size in range(60, 20, -2):
                font = self._load_font(size)
                lines = self._wrap_text(text, font, draw, banner_width, margin)
                
                line_heights = []
                for line in lines:
                    bbox = draw.textbbox((0, 0), line, font=font)
                    line_height = bbox[3] - bbox[1]
                    line_heights.append(line_height)
                
                total_text_height = sum(line_heights) + (len(lines) - 1) * line_spacing
                needed_height = total_text_height + 2 * margin
                
                if needed_height <= max_banner_height:
                    optimal_font_size = size
                    break
            
            # Create the banner with optimal font size
            font = self._load_font(optimal_font_size)
            lines = self._wrap_text(text, font, draw, banner_width, margin)
            
            line_heights = []
            for line in lines:
                bbox = draw.textbbox((0, 0), line, font=font)
                line_height = bbox[3] - bbox[1]
                line_heights.append(line_height)
            
            total_text_height = sum(line_heights) + (len(lines) - 1) * line_spacing
            
            if height:
                banner_height = height
            else:
                banner_height = max(min_banner_height, min(max_banner_height, total_text_height + 2 * margin))
            
            # Create the actual banner image
            image = Image.new("RGB", (banner_width, banner_height), bg_color)
            draw = ImageDraw.Draw(image)
            
            # Adjust font size if needed
            while total_text_height > banner_height - 2 * margin and optimal_font_size > 12:
                optimal_font_size -= 2
                font = self._load_font(optimal_font_size)
                lines = self._wrap_text(text, font, draw, banner_width, margin)
                line_heights = []
                for line in lines:
                    bbox = draw.textbbox((0, 0), line, font=font)
                    line_height = bbox[3] - bbox[1]
                    line_heights.append(line_height)
                total_text_height = sum(line_heights) + (len(lines) - 1) * line_spacing
            
            # Center text vertically
            y = (banner_height - total_text_height) // 2
            
            # Draw each line centered
            for i, line in enumerate(lines):
                bbox = draw.textbbox((0, 0), line, font=font)
                line_width = bbox[2] - bbox[0]
                x = (banner_width - line_width) // 2
                draw.text((x, y), line, fill=text_color, font=font)
                y += line_heights[i] + line_spacing
            
            # Save image
            temp_banner_path = tempfile.NamedTemporaryFile(delete=False, suffix='.png').name
            image.save(temp_banner_path)
            return temp_banner_path
        
        return await loop.run_in_executor(None, create_banner)
    
    async def _create_quote_image_from_text(self, quote_text: str, style: str = "minimal") -> str:
        """Create a quote image using the image_generator when no external image is available"""
        try:
            filename, blob_url, error = self.image_generator.generate_image_safe(quote_text, style)
            
            if error:
                raise Exception(f"Image generation failed: {error}")
            
            if not blob_url:
                raise Exception("No image URL returned from image generator")
            
            # Download the generated image to a temporary file for video use
            temp_image_path = await FileManager.download_from_url(blob_url, '.jpeg')
            return temp_image_path
            
        except Exception as e:
            raise Exception(f"Failed to create quote image from text: {str(e)}")
    
    async def generate_video(self, image_url: str = None, quote_title: str = None, quote_text: str = None, image_style: str = "minimal") -> Tuple[str, str]:
        """
        Generate a quote video with optional image and upload to Azure Blob Storage
        
        Args:
            image_url: URL of the quote image (from blob storage) - optional
            quote_title: The AI-generated quote title to use in the video
            quote_text: The quote text to display if no image is provided
            image_style: Style for generated images when no image_url provided
            
        Returns:
            Tuple of (video_filename, video_blob_url)
        """
        temp_image_path = None
        temp_video_path = None
        temp_banner_path = None
        audio_clip = None
        final_video = None
        
        try:
            # Select audio file and fade-in delay
            audio_file, fade_in_delay = self._select_audio_file()
            
            # Check if audio file exists
            if not os.path.exists(audio_file):
                raise Exception(f"Audio file not found: {audio_file}")
            
            print(f"🎵 Audio file found: {audio_file}")
            
            # Setup
            title_text = quote_title if quote_title else self.title_text
            
            # Create banner first (always needed)
            temp_banner_path = await self._create_title_banner(title_text)
            print(f"📝 Title banner created: {temp_banner_path}")
            
            # Handle image
            if image_url:
                temp_image_path = await FileManager.download_from_url(image_url, '.jpeg')
                print(f"🖼️ Image downloaded to: {temp_image_path}")
            else:
                temp_image_path = await self._create_quote_image_from_text(quote_text or title_text, image_style)
                print(f"📝 Quote image created via image generator ({image_style} style): {temp_image_path}")
            
            print("🔊 Loading audio and setting up video...")
            audio_clip = AudioFileClip(audio_file)
            video_duration = audio_clip.duration
            print(f"⏱️ Video duration: {video_duration} seconds")
            print(f"🎬 Using fade-in delay: {fade_in_delay} seconds")
            
            # Create video components with proper positioning
            background_clip = ColorClip(
                size=self.video_size, 
                color=Config.BACKGROUND_COLOR
            ).with_duration(video_duration)
            
            # Get banner dimensions for proper positioning
            banner_img = Image.open(temp_banner_path)
            banner_height = banner_img.height
            banner_img.close()
            
            # Calculate optimal quote image size (fill most of the screen)
            video_height = self.video_size[1]
            available_height = video_height - banner_height - 80  # 80px total margin (40 top + 40 gap)
            
            # Make quote image fill available space optimally
            quote_image_size = min(self.video_size[0] - 40, available_height)  # 40px margin from sides
            
            # Center everything vertically in the video frame
            total_content_height = banner_height + 20 + quote_image_size  # 20px gap between banner and quote
            start_y = (video_height - total_content_height) // 2
            
            banner_y_pos = start_y
            quote_y_pos = start_y + banner_height + 20
            
            banner_clip = (
                ImageClip(temp_banner_path)
                .with_duration(video_duration)
                .with_position(("center", banner_y_pos))
            )
            
            quote_clip = (
                ImageClip(temp_image_path)
                .with_duration(video_duration - fade_in_delay)
                .with_start(fade_in_delay)
                .resized(width=self.video_size[0])  # Fill full window width
                .with_position(("center", quote_y_pos))
                .with_effects([FadeIn(self.fade_in_duration)])
            )
            
            # Final composition
            print("🎬 Compositing video...")
            layers = [background_clip, banner_clip, quote_clip]
            final_video = CompositeVideoClip(layers).with_audio(audio_clip)
            
            # Generate filename and export
            video_filename = FileManager.generate_filename("quote_video", "mp4")
            temp_video_path = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4').name
            
            print(f"💾 Writing video to temporary file...")
            loop = asyncio.get_event_loop()
            
            def export_video():
                final_video.write_videofile(
                    temp_video_path, 
                    codec="libx264", 
                    audio_codec="aac", 
                    fps=Config.VIDEO_FPS
                )
            
            await loop.run_in_executor(None, export_video)
            
            # Upload to Azure Blob Storage
            print("☁️ Uploading video to Azure Blob Storage...")
            video_blob_url = await self.blob_manager.upload_file_async(temp_video_path, video_filename, self.video_folder)
            
            print("✅ Video created and uploaded successfully!")
            return video_filename, video_blob_url
            
        except Exception as e:
            raise Exception(f"Video generation failed: {str(e)}")
        
        finally:
            # Clean up temporary files and resources
            FileManager.cleanup_temp_files(temp_image_path, temp_banner_path, temp_video_path)
            if audio_clip:
                audio_clip.close()
            if final_video:
                final_video.close()
    
    async def generate_video_safe(self, image_url: str = None, quote_title: str = None, quote_text: str = None, image_style: str = "minimal") -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """Safe version of generate_video that returns error instead of raising"""
        try:
            print(f"🎬 Starting video generation with image URL: {image_url}")
            print(f"📝 Using title: {quote_title}")
            print(f"📄 Using quote text: {quote_text}")
            print(f"🎨 Using image style: {image_style}")
            filename, blob_url = await self.generate_video(image_url, quote_title, quote_text, image_style)
            print(f"✅ Video generation completed: {filename}")
            return filename, blob_url, None
        except Exception as e:
            error_msg = f"Video generation failed: {str(e)}"
            print(f"❌ {error_msg}")
            return None, None, error_msg
