import os
import json
from typing import Optional, List, Dict
from .metadata import scan_ipod_for_audio
from .device import find_ipod_path
from .spotify import process_songs
from . import env

def load_existing_songs() -> Optional[List[Dict]]:
    """Load songs from existing JSON file if it exists."""
    if os.path.exists('ipod_songs.json'):
        try:
            with open('ipod_songs.json', 'r') as f:
                songs = json.load(f)
            return songs
        except json.JSONDecodeError:
            print("Error reading existing songs file. Will need to rescan.")
    return None

def scan_new_songs(ipod_path: str) -> Optional[List[Dict]]:
    """Scan iPod for songs and save to JSON."""
    songs = scan_ipod_for_audio(ipod_path)
    if songs:
        with open('ipod_songs.json', 'w') as f:
            json.dump(songs, f, indent=2)
        print(f"Saved metadata for {len(songs)} songs to 'ipod_songs.json'")
    return songs

def print_song_samples(songs: List[Dict]):
    """Print sample of songs found."""
    print("\nSample songs:")
    for song in songs[:5]:
        print(f"  - {song['title']} by {song['artist']} ({song['album']})")

def handle_spotify_upload(songs: List[Dict]):
    """Handle Spotify upload process."""
    error = env.load_spotify_env()
    if error:
        print("\nCannot upload to Spotify:")
        print(error)
        return
    
    print("\nWould you like to upload these songs to Spotify?")
    print("1. Yes")
    print("2. No")
    
    while True:
        choice = input("\nEnter your choice (1 or 2): ").strip()
        if choice == "1":
            playlist_name = input("\nEnter playlist name (press Enter for default 'iPod Library'): ").strip()
            if not playlist_name:
                playlist_name = None
            try:
                results = process_songs(songs_data=songs, playlist_name=playlist_name)
            except Exception as e:
                print(f"\nError during Spotify upload: {str(e)}")
                print("Please check your Spotify credentials and try again.")
            break
        elif choice == "2":
            print("Skipping Spotify upload.")
            break
        else:
            print("Invalid choice. Please enter 1 or 2.")

def check_metadata(songs: List[Dict]):
    """Check for invalid metadata without uploading to Spotify."""
    invalid_songs = []
    for song in songs:
        if song['title'] == 'Unknown Title' or song['artist'] == 'Unknown Artist':
            invalid_reason = []
            if song['title'] == 'Unknown Title':
                invalid_reason.append('Unknown Title')
            if song['artist'] == 'Unknown Artist':
                invalid_reason.append('Unknown Artist')
            
            invalid_songs.append({
                'file_path': song['file_path'],
                'title': song['title'],
                'artist': song['artist'],
                'album': song['album'],
                'raw_title': song.get('raw_title', 'Unknown Title'),
                'reason': f"Invalid metadata: {' '.join(invalid_reason)}"
            })
    
    # Save results to file
    output_data = {
        'total_songs': len(songs),
        'invalid_metadata_count': len(invalid_songs),
        'invalid_metadata_songs': invalid_songs
    }
    
    with open('metadata_check_results.json', 'w') as f:
        json.dump(output_data, f, indent=2)
    
    # Print summary
    print("\nMetadata Check Summary:")
    print(f"Total songs checked: {len(songs)}")
    print(f"Songs with invalid metadata: {len(invalid_songs)}")
    
    if invalid_songs:
        print("\nSample of invalid songs:")
        for song in invalid_songs[:5]:
            print(f"\nFile: {song['file_path']}")
            print(f"Raw Title: {song['raw_title']}")
            print(f"Parsed Title: {song['title']}")
            print(f"Artist: {song['artist']}")
            print(f"Reason: {song['reason']}")
        
        if len(invalid_songs) > 5:
            print(f"\n... and {len(invalid_songs) - 5} more")
        
        print("\nFull results saved to 'metadata_check_results.json'")

def handle_ipod_scan() -> Optional[List[Dict]]:
    """Handle iPod scanning process."""
    print("Looking for iPod...")
    ipod_path = find_ipod_path()
    
    if not ipod_path:
        print("\nNo iPod detected automatically. Please make sure:")
        print("1. Your iPod is connected to your computer")
        print("2. Your iPod is in disk/sync mode")
        print("\nWould you like to:")
        print("1. Enter the iPod path manually")
        print("2. Exit the script")
        
        while True:
            choice = input("\nEnter your choice (1 or 2): ").strip()
            if choice == "1":
                ipod_path = input("Enter your iPod path (e.g., /Volumes/YOUR_IPOD_NAME): ")
                break
            elif choice == "2":
                return None
            else:
                print("Invalid choice. Please enter 1 or 2.")
    
    return scan_new_songs(ipod_path) 