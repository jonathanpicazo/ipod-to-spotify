import os
import json
from mutagen import File

def find_ipod_path():
    # Try to find the iPod path on macOS.
    volumes_path = "/Volumes"
    if not os.path.exists(volumes_path):
        return None
    
    # List all volumes and look for iPod-like names
    for volume in os.listdir(volumes_path):
        volume_path = os.path.join(volumes_path, volume)
        ipod_control_path = os.path.join(volume_path, "iPod_Control")
        
        # Check if this volume has iPod_Control folder (typical for iPods)
        if os.path.exists(ipod_control_path):
            print(f"Found potential iPod at: {volume_path}")
            return volume_path
    
    return None

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
        
        return metadata
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return None

def scan_ipod_for_audio(ipod_path):
    """Scan iPod for audio files and extract metadata."""
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

def main():
    print("Looking for iPod...")
    ipod_path = find_ipod_path()
    
    if not ipod_path:
        ipod_path = input("Enter your iPod path (e.g., /Volumes/YOUR_IPOD_NAME): ")
    
    songs = scan_ipod_for_audio(ipod_path)
    
    if songs:
        # Save the metadata to a JSON file
        with open('ipod_songs.json', 'w') as f:
            json.dump(songs, f, indent=2)
        print(f"Saved metadata for {len(songs)} songs to 'ipod_songs.json'")
        
        # Print a few examples
        print("\nSample songs:")
        for song in songs[:5]:
            print(f"  - {song['title']} by {song['artist']} ({song['album']})")
    else:
        print("No songs found with readable metadata")

if __name__ == "__main__":
    main()