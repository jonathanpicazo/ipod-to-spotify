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
                
                # Display upload results summary
                print("\nUpload Results Summary:")
                print(f"Total songs processed: {results['total_songs']}")
                print(f"Successfully uploaded: {results['success_count']} songs")
                print(f"Already in playlist: {results['skipped_count']} songs")
                print(f"Failed to upload: {results['failed_count']} songs")
                print(f"Invalid metadata: {results['invalid_metadata_count']} songs")
                
                if results['success_count']:
                    success_rate = (results['success_count']/results['total_songs'])*100
                    print(f"Success rate: {success_rate:.1f}%")
                
                # Show sample of failed songs if any
                if results['failed_songs']:
                    print("\nSample of failed uploads:")
                    for song in results['failed_songs'][:3]:
                        print(f"\nTitle: {song['title']}")
                        print(f"Artist: {song['artist']}")
                        print(f"Album: {song['album']}")
                        print(f"Reason: {song.get('reason', 'Unknown error')}")
                    
                    if len(results['failed_songs']) > 3:
                        print(f"\n... and {len(results['failed_songs']) - 3} more failed songs")
                
                print("\nDetailed results saved to 'upload_results.json'")
                
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
            
            # Create detailed metadata report
            song_report = {
                'file_path': song['file_path'],
                'title': song['title'],
                'artist': song['artist'],
                'album': song['album'],
                'raw_title': song.get('raw_title', 'Unknown Title'),
                'format': song.get('format', 'unknown'),
                'reason': f"Invalid metadata: {' '.join(invalid_reason)}",
                'raw_metadata': song.get('raw_metadata', {})
            }

            # Add technical details if available
            tech_info = {}
            raw_meta = song.get('raw_metadata', {})
            if raw_meta:
                if 'bitrate' in raw_meta:
                    tech_info['bitrate'] = f"{raw_meta['bitrate'] // 1000}kbps"
                if 'sample_rate' in raw_meta:
                    tech_info['sample_rate'] = f"{raw_meta['sample_rate'] // 1000}kHz"
                if 'length_seconds' in raw_meta:
                    minutes = raw_meta['length_seconds'] // 60
                    seconds = raw_meta['length_seconds'] % 60
                    tech_info['duration'] = f"{minutes}:{seconds:02d}"
                if 'mode' in raw_meta:
                    tech_info['mode'] = raw_meta['mode']
            
            if tech_info:
                song_report['technical_info'] = tech_info

            # Add additional metadata if available
            additional_meta = {}
            if raw_meta:
                # Map common ID3 tags to readable names
                tag_mapping = {
                    'TCON': 'genre',
                    'TDRC': 'year',
                    'TRCK': 'track_number',
                    'TPOS': 'disc_number',
                    'TPE2': 'album_artist',
                    'TCOM': 'composer'
                }
                
                for tag, readable_name in tag_mapping.items():
                    if tag in raw_meta and raw_meta[tag]:
                        additional_meta[readable_name] = raw_meta[tag][0]
                
                # Add any user-defined text frames
                if 'TXXX' in raw_meta:
                    additional_meta['user_defined'] = raw_meta['TXXX']
                
                # Add any comments
                if 'COMM' in raw_meta:
                    additional_meta['comments'] = raw_meta['COMM']

            if additional_meta:
                song_report['additional_metadata'] = additional_meta
            
            invalid_songs.append(song_report)
    
    # Save results to file with more organized structure
    output_data = {
        'total_songs': len(songs),
        'invalid_metadata_count': len(invalid_songs),
        'summary': {
            'mp3_count': sum(1 for s in songs if s.get('format') == 'mp3'),
            'mp4_count': sum(1 for s in songs if s.get('format') == 'mp4'),
            'other_format_count': sum(1 for s in songs if s.get('format') not in ['mp3', 'mp4'])
        },
        'invalid_metadata_songs': invalid_songs
    }
    
    with open('metadata_check_results.json', 'w') as f:
        json.dump(output_data, f, indent=2)
    
    # Print summary
    print("\nMetadata Check Summary:")
    print(f"Total songs checked: {len(songs)}")
    print(f"Songs with invalid metadata: {len(invalid_songs)}")
    print("\nFormat breakdown:")
    for format_type, count in output_data['summary'].items():
        print(f"  {format_type.replace('_', ' ').title()}: {count}")
    
    if invalid_songs:
        print("\nSample of invalid songs:")
        for song in invalid_songs[:5]:
            print(f"\nFile: {song['file_path']}")
            print(f"Format: {song['format']}")
            print(f"Raw Title: {song['raw_title']}")
            print(f"Parsed Title: {song['title']}")
            print(f"Artist: {song['artist']}")
            
            if 'technical_info' in song:
                print("Technical Info:")
                for key, value in song['technical_info'].items():
                    print(f"  {key}: {value}")
            
            if 'additional_metadata' in song:
                print("Additional Metadata:")
                for key, value in song['additional_metadata'].items():
                    if key not in ['user_defined', 'comments']:
                        print(f"  {key}: {value}")
            
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