import os
from mutagen import File
from typing import Optional

def parse_title_metadata(title: str) -> tuple[Optional[str], str]:
    # Parse a title into artist and song components
    # Returns (artist, title) tuple. Artist may be None if parsing fails
    if not title or title == 'Unknown Title':
        return None, title
        
    title = title.strip()
    
    # Common separators in titles
    separators = [
        ' - ',   # Standard hyphen
        ' – ',   # En dash
        ' — ',   # Em dash
        ' -- ',  # Double hyphen
    ]
    
    for separator in separators:
        if separator in title:
            parts = title.split(separator, 1)  # Split on first occurrence only
            if len(parts) == 2:
                artist, song = parts
                artist = artist.strip()
                song = song.strip()
                
                # Only use the parsed result if both parts are meaningful
                if artist and song and artist != 'Unknown Artist':
                    # Handle features in parentheses
                    if '(' in song:
                        song = song.split('(', 1)[0].strip()
                    
                    return artist, song
    
    return None, title

def extract_metadata(file_path):
    # Extract metadata from an audio file.
    try:
        audio = File(file_path)
        if audio is None:
            return None
        
        # Initialize with default values
        metadata = {
            'file_path': file_path,
            'title': 'Unknown Title',
            'artist': 'Unknown Artist',
            'album': 'Unknown Album'
        }
        
        # Different file types store metadata differently
        if hasattr(audio, 'tags') and audio.tags:
            # MP3 files with ID3 tags
            if audio.tags and hasattr(audio.tags, 'getall'):
                # Extract common ID3 tags
                for tag, field in [('TIT2', 'title'), ('TPE1', 'artist'), ('TALB', 'album')]:
                    try:
                        frames = audio.tags.getall(tag)
                        if frames:
                            metadata[field] = str(frames[0])
                    except:
                        pass
            # MP4/AAC files
            elif hasattr(audio, 'get'):
                # Map of common MP4 tags to our fields
                mp4_map = {
                    '©nam': 'title',
                    '©ART': 'artist',
                    '©alb': 'album'
                }
                for mp4_tag, field in mp4_map.items():
                    if mp4_tag in audio:
                        metadata[field] = str(audio[mp4_tag][0])
        
        # Store raw title before any parsing
        metadata['raw_title'] = metadata['title']
        
        # If artist is unknown but we have a title, try to parse title
        if metadata['artist'] == 'Unknown Artist' and metadata['title'] != 'Unknown Title':
            parsed_artist, parsed_title = parse_title_metadata(metadata['title'])
            if parsed_artist:
                metadata['artist'] = parsed_artist
                metadata['title'] = parsed_title
        
        return metadata
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return None

def scan_ipod_for_audio(ipod_path):
    # Scan iPod for audio files and extract metadata.
    if not ipod_path:
        print("iPod path not found")
        return []
    
    music_path = os.path.join(ipod_path, "iPod_Control", "Music")
    if not os.path.exists(music_path):
        print(f"Music folder not found at {music_path}")
        return []
    
    print(f"Scanning for audio files in: {music_path}")
    
    # Audio file extensions
    audio_extensions = ('.mp3', '.m4a', '.aac', '.wav', '.aiff', '.alac', '.m4p')
    
    songs = []
    processed = 0
    
    # Walk through all subfolders
    for root, dirs, files in os.walk(music_path):
        for file in files:
            if file.lower().endswith(audio_extensions):
                file_path = os.path.join(root, file)
                
                processed += 1
                if processed % 100 == 0:
                    print(f"Processed {processed} files...")
                
                metadata = extract_metadata(file_path)
                if metadata:
                    songs.append(metadata)
    
    print(f"Found {len(songs)} songs with metadata out of {processed} audio files")
    return songs 