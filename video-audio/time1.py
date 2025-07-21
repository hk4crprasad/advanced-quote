import base64
import os
import mimetypes
import struct
import re
from google import genai
from google.genai import types


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
    """Generate audio from text using Gemini TTS"""
    client = genai.Client(
        api_key=os.environ.get("GEMINI_API_KEY"),
    )

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


def extract_timestamps(audio_path, language="English", max_duration=1.0, min_words=3, max_words=6):
    """
    Extracts timed text segments from an audio file using Gemini AI.
    
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

    # Configure Gemini client with NEW SDK
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

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

    # Prepare content - Use simpler string format that the SDK converts automatically
    contents = [
        prompt,
        types.Part.from_bytes(data=encoded_audio, mime_type=mime_type)
    ]

    # Alternative approach: Use explicit Content structure
    # contents = types.Content(
    #     role='user',
    #     parts=[
    #         types.Part.from_text(text=prompt),  # Use keyword argument
    #         types.Part.from_bytes(data=encoded_audio, mime_type=mime_type)
    #     ]
    # )

    # Generate content with thinking configuration
    try:
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
        print(f"Error: {e}")
        return None

def complete_story_to_video_workflow(story_text, output_video="story_video.mp4", language="Hindi"):
    """Complete workflow: Text -> Audio -> Timestamps -> Video"""
    print("Starting complete story to video workflow...")
    
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
    
    # Step 3: Create video using timestamps and audio
    print("Step 3: Creating video from timestamps with audio...")
    try:
        from video import create_simple_text_video
        video_path = create_simple_text_video(json_result, output_video, audio_path=audio_file)
        print(f"✅ Complete workflow finished! Video saved to: {video_path}")
        return video_path
    except ImportError:
        print("Error: Could not import create_simple_text_video from video.py")
        print("Please make sure video.py is in the same directory")
        return None


# Example usage
if __name__ == "__main__":
    try:
        # Test with the original story
        from story import generate_horror_story
        story = f"""
        Style: horror storytelling. Use a calm, eerie tone with subtle pauses. Build quiet tension — unsettling but never loud. Let the fear creep in slowly. but story should end within 1 min
        {generate_horror_story()}
"""
        print("Generated Story:", story)
        
        # Run complete workflow
        result = complete_story_to_video_workflow(story, "horror_story_video.mp4", language="Hindi")
        
        # Alternative: Just test timestamp extraction
        # result = extract_timestamps("/home/cp/advanced-quote/WhatsApp Video 2025-07-20 at 20.23.16_c77606b7.mp3", language="Hindi")
        # print(result)
    except Exception as e:
        print(f"Error: {e}")