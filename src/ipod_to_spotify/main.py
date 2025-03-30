import os

def find_ipod_path():
    # Try to find the iPod path on macOS
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

def list_ipod_files(ipod_path):
    # List the media files on the iPod.
    if not ipod_path:
        print("iPod path not found")
        return
    
    music_path = os.path.join(ipod_path, "iPod_Control", "Music")
    if not os.path.exists(music_path):
        print(f"Music folder not found at {music_path}")
        return
    
    print(f"Media folder found at: {music_path}")
    
    # File counters
    total_files = 0
    audio_files = 0
    video_files = 0
    other_files = 0
    
    # Common audio and video extensions
    audio_extensions = ('.mp3', '.m4a', '.aac', '.wav', '.aiff', '.alac')
    video_extensions = ('.mp4', '.m4v', '.mov')
    
    # List all subfolders (typically F00, F01, etc.)
    for folder in os.listdir(music_path):
        folder_path = os.path.join(music_path, folder)
        if os.path.isdir(folder_path):
            print(f"Subfolder: {folder}")
            
            # Process files in this subfolder
            files = os.listdir(folder_path)
            total_files += len(files)
            
            # Count file types
            for file in files:
                file_lower = file.lower()
                if file_lower.endswith(audio_extensions):
                    audio_files += 1
                elif file_lower.endswith(video_extensions):
                    video_files += 1
                else:
                    other_files += 1
            
            # Print a few example files
            if files:
                print(f"  Sample files: {', '.join(files[:5])}")
                print(f"  Total files in {folder}: {len(files)}")
    
    print(f"\nTotal files found: {total_files}")
    print(f"Audio files found: {audio_files}")
    print(f"Video files found: {video_files}")
    print(f"Other files found: {other_files}")

def main():
    print("Looking for iPod...")
    ipod_path = find_ipod_path()
    
    if not ipod_path:
        ipod_path = input("Enter your iPod path (e.g., /Volumes/YOUR_IPOD_NAME): ")
    
    list_ipod_files(ipod_path)

if __name__ == "__main__":
    main()