import os
import json
from typing import Optional
from .metadata import scan_ipod_for_audio
from .device import find_ipod_path
from .spotify import process_songs
from . import env

def load_existing_songs():
    """Load songs from existing JSON file if it exists."""
    if os.path.exists('ipod_songs.json'):
        try:
            with open('ipod_songs.json', 'r') as f:
                songs = json.load(f)
            return songs
        except json.JSONDecodeError:
            print("Error reading existing songs file. Will need to rescan.")
    return None

def scan_new_songs(ipod_path):
    """Scan iPod for songs and save to JSON."""
    songs = scan_ipod_for_audio(ipod_path)
    if songs:
        with open('ipod_songs.json', 'w') as f:
            json.dump(songs, f, indent=2)
        print(f"Saved metadata for {len(songs)} songs to 'ipod_songs.json'")
    return songs

def print_song_samples(songs):
    """Print sample of songs found."""
    print("\nSample songs:")
    for song in songs[:5]:
        print(f"  - {song['title']} by {song['artist']} ({song['album']})")

def handle_spotify_upload(songs):
    """Handle Spotify upload process."""
    # Validate Spotify environment before attempting upload
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

def main():
    # Check for existing songs data
    existing_songs = load_existing_songs()
    
    if existing_songs:
        print(f"Found existing song data ({len(existing_songs)} songs)")
        print("\nWhat would you like to do?")
        print("1. Use existing song data")
        print("2. Rescan iPod")
        print("3. Exit")
        
        while True:
            choice = input("\nEnter your choice (1-3): ").strip()
            if choice == "1":
                print_song_samples(existing_songs)
                handle_spotify_upload(existing_songs)
                break
            elif choice == "2":
                # Fall through to iPod scanning
                break
            elif choice == "3":
                print("Exiting script...")
                return
            else:
                print("Invalid choice. Please enter 1-3.")
        
        if choice == "1":  # If user chose to use existing data, we're done
            return
    
    # If we get here, we need to scan the iPod
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
                print("Exiting script...")
                return
            else:
                print("Invalid choice. Please enter 1 or 2.")
    
    songs = scan_new_songs(ipod_path)
    
    if songs:
        print_song_samples(songs)
        handle_spotify_upload(songs)
    else:
        print("No songs found with readable metadata")

if __name__ == "__main__":
    main()