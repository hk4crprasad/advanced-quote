import json
import re
import os
# Updated imports for MoviePy v2.0+
from moviepy import VideoFileClip, TextClip, ColorClip, CompositeVideoClip, concatenate_videoclips, AudioFileClip, ImageClip
from moviepy import vfx

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
    ).with_duration(total_duration)
    
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

def create_video_with_background_images(json_data, image_metadata, output_path="enhanced_video.mp4",
                                      video_width=720, video_height=1280, font_size=60, 
                                      auto_download_hindi_font=True, audio_path=None, transition_duration=0.5):
    """
    Create video with background images and smooth transitions
    """
    print("Creating enhanced video with background images...")
    
    # Font setup (reuse from create_simple_text_video)
    hindi_font = None
    if auto_download_hindi_font:
        hindi_font = download_hindi_font()
    
    system_font = find_system_font()
    chosen_font = hindi_font if hindi_font else system_font
    print(f"Using font: {chosen_font}")
    
    # Parse JSON data
    if isinstance(json_data, str):
        cleaned_json = clean_json_string(json_data)
        try:
            data = json.loads(cleaned_json)
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            return None
    else:
        data = json_data
    
    # Find total duration
    last_segment = max(data, key=lambda x: timestamp_to_seconds(x['time_end']))
    total_duration = timestamp_to_seconds(last_segment['time_end'])
    print(f"Total video duration: {total_duration:.2f} seconds")
    
    # Create background image clips with smooth transitions
    background_clips = []
    
    if image_metadata and len(image_metadata) > 0:
        print(f"Processing {len(image_metadata)} background images...")
        
        for i, img_data in enumerate(image_metadata):
            if 'image_path' not in img_data or not os.path.exists(img_data['image_path']):
                print(f"Skipping missing image {i}")
                continue
                
            # Calculate timing
            start_time = timestamp_to_seconds(img_data['time_start']) if ':' in str(img_data['time_start']) else float(img_data.get('time_start', 0))
            duration = float(img_data.get('duration', 4.0))
            
            # Create image clip
            try:
                img_clip = (ImageClip(img_data['image_path'])
                           .with_duration(duration + transition_duration)
                           .with_start(start_time))
                
                # Add fade transitions for smooth effect
                if i > 0:  # Add fade in for all except first image
                    img_clip = img_clip.with_effects([vfx.FadeIn(transition_duration)])
                if i < len(image_metadata) - 1:  # Add fade out for all except last image
                    img_clip = img_clip.with_effects([vfx.FadeOut(transition_duration)])
                
                background_clips.append(img_clip)
                print(f"✅ Added background image {i+1}: {start_time:.1f}s - {start_time+duration:.1f}s")
                
            except Exception as e:
                print(f"❌ Error processing image {i}: {e}")
    
    # Create fallback black background for any gaps
    background_base = ColorClip(
        size=(video_width, video_height), 
        color=(0, 0, 0),
    ).with_duration(total_duration + 2)
    
    # Create text clips (reuse logic from create_simple_text_video)
    text_clips = []
    successful_clips = 0
    
    for i, segment in enumerate(data):
        start_time = timestamp_to_seconds(segment['time_start'])
        end_time = timestamp_to_seconds(segment['time_end'])
        text = segment['text']
        
        # Create text clip with multiple fallback methods
        text_clip = None
        
        # Try with chosen font first
        if chosen_font:
            try:
                text_clip = TextClip(
                    text=text,
                    font_size=font_size,
                    color=(255, 255, 255),
                    font=chosen_font,
                    stroke_color=(0, 0, 0),
                    stroke_width=2
                )
            except Exception as e:
                print(f"Font failed: {e}")
        
        # Fallback methods
        if not text_clip:
            try:
                text_clip = TextClip(
                    text=text,
                    font_size=font_size,
                    color=(255, 255, 255),
                    stroke_color=(0, 0, 0),
                    stroke_width=2
                )
            except Exception as e:
                print(f"Text clip creation failed for segment {i+1}: {e}")
                continue
        
        # Set timing and position
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
            except Exception as e:
                print(f"Error setting timing for segment {i+1}: {e}")
    
    print(f"Successfully created {successful_clips}/{len(data)} text clips")
    
    if successful_clips == 0:
        print("ERROR: No text clips were created!")
        return None
    
    # Composite all clips: base background + image backgrounds + text
    all_clips = [background_base] + background_clips + text_clips
    final_video = CompositeVideoClip(all_clips)
    
    # Add audio if provided
    if audio_path and os.path.exists(audio_path):
        try:
            print(f"Adding audio from: {audio_path}")
            audio_clip = AudioFileClip(audio_path)
            
            if audio_clip.duration > total_duration:
                print(f"Trimming audio to match video duration ({total_duration:.2f}s)")
                audio_clip = audio_clip.subclipped(0, total_duration)
            
            final_video = final_video.with_audio(audio_clip)
            print("✅ Audio added successfully")
        except Exception as e:
            print(f"⚠️ Warning: Could not add audio - {e}")
    
    # Write video file
    print(f"Writing enhanced video to {output_path}...")
    print("This may take several minutes due to image processing...")
    
    final_video.write_videofile(
        output_path, 
        fps=24,
        codec='libx264',
        preset='medium',  # Better quality for images
        logger='bar'
    )
    
    # Cleanup image clips
    for clip in background_clips:
        clip.close()
    
    print(f"✅ Enhanced video saved successfully to: {output_path}")
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

