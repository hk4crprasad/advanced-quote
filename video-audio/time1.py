import base64
import os
import mimetypes
import struct
import re
import json
import time
import requests
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv
import uuid
load_dotenv()
# Global variable to track current API key index
current_api_key_index = 0
api_keys = [
    "AIzaSyDrpQAfGDiFTXEzBitBIn9gj1fEMCiHVus",
]

# Azure OpenAI configuration
AZURE_ENDPOINT = "https://hara-md2td469-westus3.cognitiveservices.azure.com/"
AZURE_DEPLOYMENT = "gpt-image-1"
AZURE_API_VERSION = "2025-04-01-preview"
AZURE_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
def set_azure_api_key(api_key):
    """Set Azure API key if not found in environment"""
    global AZURE_API_KEY
    AZURE_API_KEY = api_key
    print(f"✅ Azure API key set: ...{api_key[-4:] if api_key else 'None'}")

def test_azure_connection():
    """Test Azure OpenAI connection"""
    if not AZURE_API_KEY:
        print("❌ Azure API key not set. Use set_azure_api_key() or set AZURE_OPENAI_API_KEY environment variable")
        return False
    
    try:
        test_result = generate_image_azure_openai("test dark forest", "test_azure_image")
        if test_result:
            print("✅ Azure OpenAI connection successful")
            return True
        else:
            print("❌ Azure OpenAI test failed")
            return False
    except Exception as e:
        print(f"❌ Azure connection error: {e}")
        return False

def get_next_api_key():
    """Get the next API key in rotation"""
    global current_api_key_index
    current_api_key_index = (current_api_key_index + 1) % len(api_keys)
    return api_keys[current_api_key_index]

def get_current_api_key():
    """Get the current API key"""
    return api_keys[current_api_key_index]

def safe_api_call_delay():
    """Add a small delay between API calls to avoid rate limiting"""
    time.sleep(1)  # 1 second delay

def generate_image_azure_openai(prompt, output_filename="generated_image"):
    """Generate image using Azure OpenAI DALL-E as fallback"""
    try:
        if not AZURE_API_KEY:
            print("❌ Azure OpenAI API key not found in environment variables")
            return None
            
        base_path = f'openai/deployments/{AZURE_DEPLOYMENT}/images'
        params = f'?api-version={AZURE_API_VERSION}'
        generation_url = f"{AZURE_ENDPOINT}{base_path}/generations{params}"
        
        # Convert prompt to be suitable for DALL-E (remove Hindi context, focus on visual elements)
        visual_prompt = f"{prompt}, high quality, detailed, cinematic lighting, 9:16 aspect ratio, professional photography"
        
        generation_body = {
            "prompt": visual_prompt[:900],  # DALL-E has prompt length limits
            "n": 1,
            "size": "1024x1536",  # Closest to 9:16 ratio
            "quality": "medium",  # Use medium quality for better results
            "output_format": "png"
        }
        
        response = requests.post(
            generation_url,
            headers={
                'Api-Key': AZURE_API_KEY,
                'Content-Type': 'application/json',
            },
            json=generation_body,
            timeout=30
        )
        
        if response.status_code == 200:
            response_data = response.json()
            if 'data' in response_data and len(response_data['data']) > 0:
                b64_data = response_data['data'][0]['b64_json']
                image = Image.open(BytesIO(base64.b64decode(b64_data)))
                
                # Convert to JPG if needed
                if not output_filename.endswith('.jpg'):
                    output_filename += '.jpg'
                
                # Convert RGBA to RGB if necessary
                if image.mode == 'RGBA':
                    image = image.convert('RGB')
                    
                image.save(output_filename)
                print(f"✅ Azure OpenAI image saved to: {output_filename}")
                return output_filename
            else:
                print("❌ Azure: No image data received")
                return None
        else:
            print(f"❌ Azure API error: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Azure error: {str(e)[:50]}...")
        return None


def save_binary_file(file_name, data):
    f = open(file_name, "wb")
    f.write(data)
    f.close()
    print(f"File saved to to: {file_name}")


def convert_to_wav(audio_data: bytes, mime_type: str) -> bytes:
    """Generates a WAV file header for the given audio data and parameters.

    Args:
        audio_data: The raw audio data as a bytes object.
        mime_type: Mime type of the audio data.

    Returns:
        A bytes object representing the WAV file header.
    """
    parameters = parse_audio_mime_type(mime_type)
    bits_per_sample = parameters["bits_per_sample"]
    sample_rate = parameters["rate"]
    num_channels = 1
    data_size = len(audio_data)
    bytes_per_sample = bits_per_sample // 8
    block_align = num_channels * bytes_per_sample
    byte_rate = sample_rate * block_align
    chunk_size = 36 + data_size  # 36 bytes for header fields before data chunk size

    # http://soundfile.sapp.org/doc/WaveFormat/

    header = struct.pack(
        "<4sI4s4sIHHIIHH4sI",
        b"RIFF",          # ChunkID
        chunk_size,       # ChunkSize (total file size - 8 bytes)
        b"WAVE",          # Format
        b"fmt ",          # Subchunk1ID
        16,               # Subchunk1Size (16 for PCM)
        1,                # AudioFormat (1 for PCM)
        num_channels,     # NumChannels
        sample_rate,      # SampleRate
        byte_rate,        # ByteRate
        block_align,      # BlockAlign
        bits_per_sample,  # BitsPerSample
        b"data",          # Subchunk2ID
        data_size         # Subchunk2Size (size of audio data)
    )
    return header + audio_data


def parse_audio_mime_type(mime_type: str) -> dict[str, int | None]:
    """Parses bits per sample and rate from an audio MIME type string.

    Assumes bits per sample is encoded like "L16" and rate as "rate=xxxxx".

    Args:
        mime_type: The audio MIME type string (e.g., "audio/L16;rate=24000").

    Returns:
        A dictionary with "bits_per_sample" and "rate" keys. Values will be
        integers if found, otherwise None.
    """
    bits_per_sample = 16
    rate = 24000

    # Extract rate from parameters
    parts = mime_type.split(";")
    for param in parts: # Skip the main type part
        param = param.strip()
        if param.lower().startswith("rate="):
            try:
                rate_str = param.split("=", 1)[1]
                rate = int(rate_str)
            except (ValueError, IndexError):
                # Handle cases like "rate=" with no value or non-integer value
                pass # Keep rate as default
        elif param.startswith("audio/L"):
            try:
                bits_per_sample = int(param.split("L", 1)[1])
            except (ValueError, IndexError):
                pass # Keep bits_per_sample as default if conversion fails

    return {"bits_per_sample": bits_per_sample, "rate": rate}


def generate_audio_from_text(text, output_filename="ENTER_FILE_NAME"):
    """Generate audio from text using Gemini TTS with API key rotation"""
    for attempt, api_key in enumerate(api_keys):
        try:
            client = genai.Client(api_key=api_key)

            model = "gemini-2.5-pro-preview-tts"
            contents = [
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(text=text),
                    ],
                ),
            ]
            generate_content_config = types.GenerateContentConfig(
                temperature=1,
                response_modalities=[
                    "audio",
                ],
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                            voice_name="Kore"
                        )
                    )
                ),
            )

            file_index = 0
            for chunk in client.models.generate_content_stream(
                model=model,
                contents=contents,
                config=generate_content_config,
            ):
                if (
                    chunk.candidates is None
                    or chunk.candidates[0].content is None
                    or chunk.candidates[0].content.parts is None
                ):
                    continue
                if chunk.candidates[0].content.parts[0].inline_data and chunk.candidates[0].content.parts[0].inline_data.data:
                    file_name = f"{output_filename}_{file_index}"
                    file_index += 1
                    inline_data = chunk.candidates[0].content.parts[0].inline_data
                    data_buffer = inline_data.data
                    file_extension = mimetypes.guess_extension(inline_data.mime_type)
                    if file_extension is None:
                        file_extension = ".wav"
                        data_buffer = convert_to_wav(inline_data.data, inline_data.mime_type)
                    save_binary_file(f"{file_name}{file_extension}", data_buffer)
                    return f"{file_name}{file_extension}"
                else:
                    print(chunk.text)
            return None
            
        except Exception as e:
            error_str = str(e)
            
            if "RESOURCE_EXHAUSTED" in error_str or "quota" in error_str.lower():
                print(f"❌ Audio quota exceeded for ...{api_key[-4:]}")
                continue
            elif attempt == len(api_keys) - 1:  # Last attempt
                print("❌ All API keys failed for audio generation")
                return None
            else:
                print(f"❌ Audio error with ...{api_key[-4:]}")
                continue
    
    return None


def extract_timestamps(audio_path, language="English", max_duration=1.0, min_words=3, max_words=6):
    """
    Extracts timed text segments from an audio file using Gemini AI with API key rotation.
    
    Args:
        audio_path (str): Path to the audio file (e.g., 'audio.mp3').
        language (str): Language of the speech (e.g., 'English', 'Hindi').
        max_duration (float): Max duration per segment in seconds.
        min_words (int): Min words per segment.
        max_words (int): Max words per segment.
    
    Returns:
        str: JSON array of segments with timestamps and text.
    """
    # Load and encode audio
    with open(audio_path, 'rb') as audio_file:
        audio_data = audio_file.read()
    encoded_audio = base64.b64encode(audio_data).decode('utf-8')
    
    # Detect MIME type based on file extension
    mime_type, _ = mimetypes.guess_type(audio_path)
    if mime_type is None:
        if audio_path.lower().endswith('.mp3'):
            mime_type = "audio/mpeg"
        elif audio_path.lower().endswith('.wav'):
            mime_type = "audio/wav"
        elif audio_path.lower().endswith('.m4a'):
            mime_type = "audio/mp4"
        else:
            mime_type = "audio/mpeg"

    # Define prompt for general timestamp extraction
    prompt = f"""
    You are an audio timestamp extractor.
    
    Extract clear, concise subtitles from the given audio in {language}.
    
    OUTPUT FORMAT:
    Return a JSON array. Each object must include:
    - "time_start": in `mm:ss.sss` format
    - "time_end": in `mm:ss.sss` format
    - "text": Speech segment (between {min_words} to {max_words} words)
    
    CHUNK RULES:
    - Duration of each chunk must be ≤ {max_duration:.3f} seconds.
    - Break sentences naturally.
    - Avoid chunks with fewer than {min_words} words or more than {max_words}.
    
    NOTES:
    - Keep punctuation.
    - Output only the final JSON.
    
    Process this audio accurately.
    """

    # Try with API key rotation
    for attempt, api_key in enumerate(api_keys):
        try:
            # Configure Gemini client with NEW SDK
            client = genai.Client(api_key=api_key)

            # Prepare content - Use simpler string format that the SDK converts automatically
            contents = [
                prompt,
                types.Part.from_bytes(data=encoded_audio, mime_type=mime_type)
            ]

            # Generate content with thinking configuration
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=contents,
                config=types.GenerateContentConfig(
                    thinking_config=types.ThinkingConfig(
                        thinking_budget=3000,  # Set thinking budget (0 to disable, -1 for dynamic)
                        include_thoughts=False  # Set to True if you want to see the reasoning process
                    )
                )
            )
            
            return response.text
            
        except Exception as e:
            error_str = str(e)
            
            if "RESOURCE_EXHAUSTED" in error_str or "quota" in error_str.lower():
                print(f"❌ Timestamp quota exceeded for ...{api_key[-4:]}")
                continue
            elif attempt == len(api_keys) - 1:  # Last attempt
                print("❌ All API keys failed for timestamp extraction")
                return None
            else:
                print(f"❌ Timestamp error with ...{api_key[-4:]}")
                continue
    
    return None

def generate_image_from_prompt(prompt, output_filename="generated_image"):
    """Generate background image using Google Gemini Imagen with Azure OpenAI fallback"""
    
    # First try Gemini API keys rotation list
    api_keys_rotation = [
        "AIzaSyDrpQAfGDiFTXEzBitBIn9gj1fEMCiHVus"
    ]
    
    # Model options to try
    models = [
        "models/imagen-4.0-generate-preview-06-06"
    ]
    
    # Try Gemini first
    print("🔄 Trying Gemini Imagen...")
    for model in models:
        for api_key in api_keys_rotation:
            try:
                safe_api_call_delay()  # Add delay to avoid rate limiting
                client = genai.Client(api_key=api_key)

                result = client.models.generate_images(
                    model=model,
                    prompt=prompt,
                    config=dict(
                        number_of_images=1,
                        output_mime_type="image/jpeg",
                        person_generation="ALLOW_ADULT",
                        aspect_ratio="9:16",
                    ),
                )

                if not result.generated_images:
                    print(f"No images generated with {model} and API key ending in ...{api_key[-4:]}")
                    continue

                for generated_image in result.generated_images:
                    image = Image.open(BytesIO(generated_image.image.image_bytes))
                    image_path = f"{output_filename}.jpg"
                    image.save(image_path)
                    print(f"✅ Gemini image saved to: {image_path}")
                    return image_path
            
            except Exception as e:
                error_str = str(e)
                
                # Simplified error messages
                if "RESOURCE_EXHAUSTED" in error_str or "quota" in error_str.lower():
                    print(f"❌ Quota exceeded for API key ...{api_key[-4:]}")
                elif "billed users" in error_str or "INVALID_ARGUMENT" in error_str:
                    print(f"❌ Billing required for API key ...{api_key[-4:]}")
                elif "500 INTERNAL" in error_str:
                    print(f"❌ Server error with {model}")
                    break  # Try next model
                else:
                    print(f"❌ Unexpected error with ...{api_key[-4:]}")
                continue
    
    # If Gemini fails, try Azure OpenAI
    print("🔄 Switching to Azure OpenAI...")
    azure_result = generate_image_azure_openai(prompt, output_filename)
    if azure_result:
        return azure_result
    
    print("❌ All image generation services failed")
    return None

def create_image_metadata_json(timestamp_data, total_duration):
    """Create metadata for background images based on timestamps"""
    try:
        if isinstance(timestamp_data, str):
            data = json.loads(timestamp_data.strip().replace('```json', '').replace('```', ''))
        else:
            data = timestamp_data
        
        # Calculate optimal number of images (one every 3-4 seconds)
        target_interval = 4.0  # 4 seconds per image
        estimated_images = max(5, min(35, int(total_duration / target_interval)))
        
        print(f"Creating {estimated_images} background images for {total_duration:.1f}s video")
        
        image_metadata = []
        interval = total_duration / estimated_images
        
        # Group text segments by time intervals
        for i in range(estimated_images):
            start_time = i * interval
            end_time = min((i + 1) * interval, total_duration)
            
            # Find text segments in this time range
            relevant_texts = []
            for segment in data:
                seg_start = timestamp_to_seconds_simple(segment['time_start'])
                seg_end = timestamp_to_seconds_simple(segment['time_end'])
                
                if (seg_start >= start_time and seg_start <= end_time) or \
                   (seg_end >= start_time and seg_end <= end_time):
                    relevant_texts.append(segment['text'])
            
            # Create contextual prompt based on story content
            context_text = " ".join(relevant_texts[:3])  # Use first few relevant texts
            
            image_metadata.append({
                "image_index": i,
                "time_start": f"{int(start_time//60):02d}:{start_time%60:06.3f}",
                "time_end": f"{int(end_time//60):02d}:{end_time%60:06.3f}",
                "duration": end_time - start_time,
                "context_text": context_text,
                "prompt": create_image_prompt_from_context(context_text, i)
            })
        
        return image_metadata
    
    except Exception as e:
        print(f"Error creating image metadata: {e}")
        return None

def timestamp_to_seconds_simple(timestamp):
    """Convert mm:ss.sss format to seconds"""
    try:
        if ':' in timestamp:
            parts = timestamp.split(':')
            minutes = int(parts[0])
            seconds = float(parts[1])
            return minutes * 60 + seconds
        else:
            return float(timestamp)
    except:
        return 0

def create_image_prompt_from_context(context_text, image_index):
    """Create horror-themed image prompts based on story context"""
    
    # Base horror atmosphere prompts
    base_atmospheres = [
        "Dark, eerie forest at night with twisted trees and fog",
        "Abandoned hospital corridor with flickering lights", 
        "Old cemetery with weathered tombstones in moonlight",
        "Dimly lit office building with empty cubicles at night",
        "Desolate factory floor with machinery shadows",
        "Empty school hallway with lockers, dark and unsettling",
        "Foggy graveyard with ancient stone monuments",
        "Mysterious radio station booth in darkness"
    ]
    
    # Select base atmosphere cycling through options
    base_prompt = base_atmospheres[image_index % len(base_atmospheres)]
    
    # Enhance with context if available
    if context_text and len(context_text.strip()) > 0:
        # Extract key mood words from Hindi text (basic approach)
        mood_keywords = {
            "रात": "nighttime atmosphere",
            "अंधेरा": "deep darkness", 
            "डर": "fearful mood",
            "चेतावनी": "warning signs",
            "आवाज": "mysterious sounds",
            "छाया": "creepy shadows",
            "खामोशी": "eerie silence"
        }
        
        context_mood = ""
        for hindi_word, english_mood in mood_keywords.items():
            if hindi_word in context_text:
                context_mood += f", {english_mood}"
        
        enhanced_prompt = f"{base_prompt}{context_mood}, cinematic horror atmosphere, 9:16 aspect ratio, dark tones, professional photography"
    else:
        enhanced_prompt = f"{base_prompt}, horror atmosphere, cinematic lighting, 9:16 vertical format, dark and moody"
    
    return enhanced_prompt

def generate_background_images(image_metadata, output_dir="bg_images"):
    """Generate all background images based on metadata with improved error handling and Azure fallback"""
    os.makedirs(output_dir, exist_ok=True)
    generated_images = []
    failed_count = 0
    
    # Check if Azure is available as fallback
    azure_available = AZURE_API_KEY is not None
    if azure_available:
        print("✅ Azure OpenAI available as fallback for image generation")
    else:
        print("⚠️ Azure OpenAI not configured - only Gemini will be used")
    
    for i, img_data in enumerate(image_metadata):
        print(f"Generating image {i+1}/{len(image_metadata)}: {img_data['prompt'][:60]}...")
        
        output_path = os.path.join(output_dir, f"bg_image_{i:03d}")
        image_path = generate_image_from_prompt(img_data['prompt'], output_path)
        
        if image_path:
            img_data['image_path'] = image_path
            generated_images.append(img_data)
            print(f"✅ Generated: {image_path}")
            failed_count = 0  # Reset failed count on success
        else:
            failed_count += 1
            print(f"❌ Failed to generate image {i+1}")
            
            # If too many consecutive failures and no Azure fallback, stop trying
            if failed_count >= 5 and len(generated_images) == 0 and not azure_available:
                print("❌ Too many consecutive failures without fallback, stopping image generation")
                break
            elif failed_count >= 10:  # Even with Azure, stop after 10 consecutive failures
                print("❌ Too many consecutive failures even with fallback, stopping image generation")
                break
    
    success_rate = len(generated_images) / len(image_metadata) * 100
    print(f"Successfully generated {len(generated_images)}/{len(image_metadata)} images ({success_rate:.1f}% success rate)")
    
    # If we have at least some images, continue
    if len(generated_images) > 0:
        return generated_images
    else:
        print("⚠️ No images generated, video will be created without background images")
        return []

def complete_story_to_video_workflow(story_text, output_video="story_video.mp4", language="Hindi"):
    """Enhanced workflow: Text -> Audio -> Timestamps -> Background Images -> Video"""
    print("Starting complete story to video workflow with background images...")
    
    # Step 1: Generate audio from story text
    print("Step 1: Generating audio from story text...")
    audio_file = generate_audio_from_text(story_text, "story_audio")
    if not audio_file:
        print("Failed to generate audio")
        return None
    
    # Step 2: Extract timestamps from generated audio
    print("Step 2: Extracting timestamps from audio...")
    json_result = extract_timestamps(audio_file, language=language)
    if not json_result:
        print("Failed to extract timestamps")
        return None
    
    # Step 3: Calculate total duration
    try:
        import librosa
        audio_duration, _ = librosa.load(audio_file, sr=None)
        total_duration = len(audio_duration) / _
    except:
        # Fallback: estimate from timestamps
        timestamp_data = json.loads(json_result.strip().replace('```json', '').replace('```', ''))
        last_segment = max(timestamp_data, key=lambda x: timestamp_to_seconds_simple(x['time_end']))
        total_duration = timestamp_to_seconds_simple(last_segment['time_end'])
    
    print(f"Audio duration: {total_duration:.2f} seconds")
    
    # Step 4: Create image metadata
    print("Step 3: Creating background image plan...")
    image_metadata = create_image_metadata_json(json_result, total_duration)
    if not image_metadata:
        print("Failed to create image metadata")
        return None
    
    # Step 5: Generate background images
    print("Step 4: Generating background images...")
    generated_images = generate_background_images(image_metadata)
    if not generated_images:
        print("No background images generated, proceeding without images")
    
    # Step 6: Create video using enhanced video creation
    print("Step 5: Creating video with background images and audio...")
    try:
        import video
        video_path = video.create_video_with_background_images(
            json_result, 
            generated_images, 
            output_video, 
            audio_path=audio_file
        )
        print(f"✅ Complete workflow finished! Video saved to: {video_path}")
        return video_path
    except (ImportError, AttributeError) as e:
        print(f"Enhanced video function not found: {e}, using simple version...")
        try:
            import video
            video_path = video.create_simple_text_video(json_result, output_video, audio_path=audio_file)
            print(f"✅ Basic workflow finished! Video saved to: {video_path}")
            return video_path
        except (ImportError, AttributeError) as e:
            print(f"Error: Could not import video functions from video.py: {e}")
            return None
