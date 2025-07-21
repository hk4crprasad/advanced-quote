import json
import re
import os
# Updated imports for MoviePy v2.0+
from moviepy import VideoFileClip, TextClip, ColorClip, CompositeVideoClip, concatenate_videoclips, AudioFileClip

def timestamp_to_seconds(timestamp):
    """Convert mm:ss.sss format to seconds"""
    match = re.match(r'(\d+):(\d+)\.(\d+)', timestamp)
    if match:
        minutes, seconds, milliseconds = match.groups()
        total_seconds = int(minutes) * 60 + int(seconds) + int(milliseconds) / 1000
        return total_seconds
    return 0

def find_system_font():
    """Find a working font on the system, prioritizing Hindi/Devanagari fonts"""
    import os
    
    # Hindi/Devanagari fonts (priority)
    hindi_fonts = [
        # Downloaded Hindi fonts (common locations)
        'NotoSansDevanagari-Regular.ttf',
        './NotoSansDevanagari-Regular.ttf',
        '/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf',
        '/usr/share/fonts/TTF/NotoSansDevanagari-Regular.ttf',
        
        # System Hindi fonts
        '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',  # Supports some Hindi
        '/usr/share/fonts/truetype/lohit-devanagari/Lohit-Devanagari.ttf',
        '/usr/share/fonts/truetype/gargi/gargi.ttf',
        '/usr/share/fonts/truetype/nakula/nakula.ttf',
        
        # Windows Hindi fonts
        'C:/Windows/Fonts/mangal.ttf',
        'C:/Windows/Fonts/Nirmala.ttf',
        
        # macOS fonts (some support Hindi)
        '/System/Library/Fonts/Apple Symbols.ttf',
        '/System/Library/Fonts/Arial Unicode MS.ttf',
    ]
    
    # Fallback fonts (basic support)
    fallback_fonts = [
        'Arial',
        'arial.ttf',
        'Arial.ttf',
        '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
        '/usr/share/fonts/TTF/DejaVuSans.ttf', 
        '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
        '/System/Library/Fonts/Arial.ttf',
        'C:/Windows/Fonts/arial.ttf',
    ]
    
    # Check Hindi fonts first
    for font_path in hindi_fonts:
        if os.path.exists(font_path):
            print(f"Found Hindi font: {font_path}")
            return font_path
    
    print("No Hindi-specific fonts found, checking fallback fonts...")
    
    # Check fallback fonts
    for font_path in fallback_fonts:
        if os.path.exists(font_path):
            print(f"Found fallback font: {font_path}")
            return font_path
    
    print("No specific font found, will try default")
    return None

def download_hindi_font():
    """Download Noto Sans Devanagari font for Hindi text"""
    import urllib.request
    import os
    
    font_url = "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansDevanagari/NotoSansDevanagari-Regular.ttf"
    font_filename = "Hind-Medium.ttf"
    
    if not os.path.exists(font_filename):
        try:
            print("Downloading Hindi font...")
            urllib.request.urlretrieve(font_url, font_filename)
            print(f"✓ Downloaded Hindi font: {font_filename}")
            return font_filename
        except Exception as e:
            print(f"✗ Failed to download Hindi font: {e}")
            return None
    else:
        print(f"✓ Hindi font already exists: {font_filename}")
        return font_filename

def clean_json_string(json_string):
    """Clean JSON string by removing markdown code blocks and extra formatting"""
    if not isinstance(json_string, str):
        return json_string
    
    json_string = json_string.strip()
    
    # Remove ```json at the beginning
    if json_string.startswith('```json'):
        json_string = json_string[7:]
    elif json_string.startswith('```'):
        json_string = json_string[3:]
    
    # Remove ``` at the end
    if json_string.endswith('```'):
        json_string = json_string[:-3]
    
    json_string = json_string.strip()
    return json_string

def create_simple_text_video(json_data, output_path="simple_text_video.mp4", 
                            video_width=720, video_height=1280,  # Reel format 9:16
                            font_size=60, auto_download_hindi_font=True, audio_path=None):
    """
    Create a simple video with white text on black background - guaranteed to work
    """
    
    # Try to download Hindi font if needed
    hindi_font = None
    if auto_download_hindi_font:
        hindi_font = download_hindi_font()
    
    # Find a working font
    system_font = find_system_font()
    
    # Prefer Hindi font if available
    chosen_font = hindi_font if hindi_font else system_font
    print(f"Using font: {chosen_font}")
    
    # Parse JSON if it's a string
    if isinstance(json_data, str):
        cleaned_json = clean_json_string(json_data)
        print(f"Parsing JSON data...")
        try:
            data = json.loads(cleaned_json)
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            raise
    else:
        data = json_data
    
    print(f"Found {len(data)} text segments to process")
    
    # Find total video duration
    last_segment = max(data, key=lambda x: timestamp_to_seconds(x['time_end']))
    total_duration = timestamp_to_seconds(last_segment['time_end']) + 2  # Add buffer
    
    print(f"Total video duration: {total_duration:.2f} seconds")
    
    # Create BLACK background clip
    background = ColorClip(
        size=(video_width, video_height), 
        color=(0, 0, 0),  # Pure black
        duration=total_duration
    )
    
    print("Created background clip")
    
    # Create text clips for each segment
    text_clips = []
    successful_clips = 0
    
    for i, segment in enumerate(data):
        start_time = timestamp_to_seconds(segment['time_start'])
        end_time = timestamp_to_seconds(segment['time_end'])
        text = segment['text']
        
        #print(f"Processing segment {i+1}/{len(data)}: '{text}' at {start_time:.1f}s-{end_time:.1f}s")
        
        # Try multiple approaches to create text clip
        text_clip = None
        
        # Method 1: Use chosen font (Hindi font preferred)
        if chosen_font:
            try:
                text_clip = TextClip(
                    text=text,
                    font_size=font_size,
                    color=(255, 255, 255),
                    font=chosen_font
                )
                #print(f"✓ Created with chosen font: {chosen_font}")
            except Exception as e:
                print(f"✗ Chosen font failed: {e}")
        
        # Method 2: Try Hindi font names
        if not text_clip:
            hindi_font_names = [
                'NotoSansDevanagari-Regular',
                'Noto Sans Devanagari',
                'Mangal',
                'Nirmala UI',
                'Lohit Devanagari'
            ]
            
            for font_name in hindi_font_names:
                try:
                    text_clip = TextClip(
                        text=text,
                        font_size=font_size,
                        color=(255, 255, 255),
                        font=font_name
                    )
                    #print(f"✓ Created with Hindi font: {font_name}")
                    break
                except:
                    continue
        
        # Method 3: Try common font names
        if not text_clip:
            for font_name in ['Arial', 'DejaVu Sans', 'Liberation Sans']:
                try:
                    text_clip = TextClip(
                        text=text,
                        font_size=font_size,
                        color=(255, 255, 255),
                        font=font_name
                    )
                    #print(f"✓ Created with font: {font_name}")
                    break
                except:
                    continue
        
        # Method 4: Try without specifying font (let MoviePy use default)
        if not text_clip:
            try:
                text_clip = TextClip(
                    text=text,
                    font_size=font_size,
                    color=(255, 255, 255)
                )
                print(f"✓ Created with default font")
            except Exception as e:
                print(f"✗ All methods failed for segment {i+1}: {e}")
                continue
        
        # If we successfully created a text clip, add timing and position
        if text_clip:
            try:
                clip_duration = end_time - start_time
                if clip_duration > 0:
                    text_clip = (text_clip
                               .with_duration(clip_duration)
                               .with_start(start_time)
                               .with_position('center'))
                    
                    text_clips.append(text_clip)
                    successful_clips += 1
                    #   print(f"✓ Successfully added text clip {i+1}")
                else:
                    print(f"✗ Skipped segment {i+1} - invalid duration")
            except Exception as e:
                print(f"✗ Error setting timing for segment {i+1}: {e}")
    
    print(f"Successfully created {successful_clips}/{len(data)} text clips")
    
    if successful_clips == 0:
        print("ERROR: No text clips were created successfully!")
        print("💡 Try installing Hindi fonts manually:")
        print("   sudo apt install fonts-noto-devanagari fonts-lohit-devanagari")
        return None
    
    # Composite all clips
    print("Compositing video...")
    final_video = CompositeVideoClip([background] + text_clips)
    
    # Add audio if provided
    if audio_path and os.path.exists(audio_path):
        try:
            print(f"Adding audio from: {audio_path}")
            audio_clip = AudioFileClip(audio_path)
            
            # Match audio duration to video duration if needed
            if audio_clip.duration < total_duration:
                print(f"Audio duration ({audio_clip.duration:.2f}s) is shorter than video ({total_duration:.2f}s)")
            elif audio_clip.duration > total_duration:
                print(f"Trimming audio to match video duration ({total_duration:.2f}s)")
                audio_clip = audio_clip.subclipped(0, total_duration)
            
            final_video = final_video.with_audio(audio_clip)
            print("✓ Audio added successfully")
        except Exception as e:
            print(f"⚠️ Warning: Could not add audio - {e}")
            print("Video will be created without audio")
    elif audio_path:
        print(f"⚠️ Warning: Audio file not found at {audio_path}")
        print("Video will be created without audio")
    
    # Write video file with simple settings
    print(f"Writing video to {output_path}...")
    print("This may take a few minutes...")
    
    final_video.write_videofile(
        output_path, 
        fps=24,
        codec='libx264',
        preset='fast',
        logger='bar'
    )
    
    print(f"✅ Video saved successfully to: {output_path}")
    return output_path

def create_video_from_audio_timestamps(audio_path, language="Hindi", output_video="text_video.mp4"):
    """Complete pipeline: Extract timestamps from audio and create simple text video with audio"""
    try:
        from time1 import extract_timestamps
    except ImportError:
        print("Error: Could not import extract_timestamps from time1.py")
        return None
    
    print("Extracting timestamps from audio...")
    json_result = extract_timestamps(audio_path, language=language)
    
    if json_result:
        print("Creating video from timestamps with audio...")
        return create_simple_text_video(json_result, output_video, audio_path=audio_path)
    else:
        print("Failed to extract timestamps")
        return None

# Test function to verify everything works
def test_simple_video():
    """Test with minimal data to verify the system works"""
    test_data = [
        {
            "time_start": "00:00.000",
            "time_end": "00:02.000", 
            "text": "Hello World"
        },
        {
            "time_start": "00:02.000",
            "time_end": "00:04.000",
            "text": "नमस्ते दुनिया"  # Hindi text
        },
        {
            "time_start": "00:04.000",
            "time_end": "00:06.000",
            "text": "बधाई हो।"  # More Hindi text
        }
    ]
    
    print("Creating test video with Hindi text...")
    result = create_simple_text_video(test_data, "test_hindi.mp4", font_size=80)
    if result:
        print("✅ Test successful! Check test_hindi.mp4")
    else:
        print("❌ Test failed!")

def install_hindi_fonts_instructions():
    """Print instructions for installing Hindi fonts"""
    print("\n🔤 HINDI FONT INSTALLATION INSTRUCTIONS:")
    print("\n📦 Option 1 - Install via package manager:")
    print("   Ubuntu/Debian:")
    print("   sudo apt update")
    print("   sudo apt install fonts-noto-devanagari fonts-lohit-devanagari")
    print("\n   CentOS/RHEL/Fedora:")
    print("   sudo dnf install google-noto-sans-devanagari-fonts")
    
    print("\n💾 Option 2 - Download manually:")
    print("   The script will auto-download NotoSansDevanagari-Regular.ttf")
    
    print("\n🎯 Option 3 - Use custom font:")
    print("   Download any Hindi font (.ttf file) and place it in the script directory")
    
    print("\n✅ The script tries all these methods automatically!")
    print("=" * 60)

# FOR YOUR USE CASE WITH HINDI FONTS:
# create_video_from_audio_timestamps("/home/cp/advanced-quote/WhatsApp Video 2025-07-20 at 20.23.16_c77606b7.mp3", 
#                                    language="Hindi", 
#                                    output_video="hindi_video.mp4")