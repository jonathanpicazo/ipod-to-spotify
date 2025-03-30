import os
import json
from typing import Dict, List, Optional
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from . import env

def debug_env_loading():
    # Debug helper to check .env loading status
    # Get the project root directory (same level as poetry.lock)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))  # just two levels up
    env_path = os.path.join(project_root, '.env')
    
    print("\nLooking for .env file:")
    print(f"Current directory: {current_dir}")
    print(f"Project root: {project_root}")
    print(f"Expected .env path: {env_path}")
    
    if not os.path.exists(env_path):
        print("\nError: Could not find .env file")
        print("Please ensure .env file exists in the project root (same level as poetry.lock)")
        return False
    
    print(f"\nFound .env file at: {env_path}")
    env.load_dotenv(env_path)
    
    # Check if variables were loaded
    required_vars = ['SPOTIFY_CLIENT_ID', 'SPOTIFY_CLIENT_SECRET', 'SPOTIFY_REDIRECT_URI']
    
    print("\nEnvironment variables status:")
    print("-" * 30)
    for var in required_vars:
        value = env.getenv(var)
        # Only show first/last few chars of secrets for security
        if value and var != 'SPOTIFY_REDIRECT_URI':
            masked_value = value[:4] + '...' + value[-4:] if len(value) > 8 else '***'
            print(f"{var}: {masked_value}")
        else:
            print(f"{var}: {value if value else 'NOT SET'}")
    print("-" * 30)
    
    missing = [var for var in required_vars if not env.getenv(var)]
    
    if missing:
        print("\nMissing environment variables:", ', '.join(missing))
        print("Please check your .env file contains all required variables")
        return False
    
    print("\nSuccessfully loaded all required environment variables")
    return True

class SpotifyUploader:
    def __init__(self):
        # Initialize Spotify client with necessary scopes
        scopes = [
            'playlist-modify-public',
            'playlist-modify-private',
            'playlist-read-private'
        ]
        
        # Check environment configuration
        error = env.load_spotify_env()
        if error:
            raise ValueError(error)
        
        try:
            creds = env.get_spotify_creds()
            self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
                scope=' '.join(scopes),
                **creds
            ))
            self.user_id = self.sp.current_user()['id']
            self._load_playlist_cache()
        except Exception as e:
            if "invalid_client" in str(e).lower():
                print("\nError: Invalid Spotify client credentials")
                print("Please make sure your client ID and secret in .env are correct")
                print("You can find these at https://developer.spotify.com/dashboard")
                raise
            raise

    def _load_playlist_cache(self):
        # Load or create playlist cache file
        self.cache_file = 'playlist_cache.json'
        if os.path.exists(self.cache_file):
            with open(self.cache_file, 'r') as f:
                self.playlist_cache = json.load(f)
        else:
            self.playlist_cache = {}

    def _save_playlist_cache(self):
        # Save playlist cache to file
        with open(self.cache_file, 'w') as f:
            json.dump(self.playlist_cache, f)

    def get_or_create_playlist(self, name: str) -> str:
        # Get existing playlist ID or create new one
        # Check cache first
        if name in self.playlist_cache:
            # Verify playlist still exists
            try:
                self.sp.playlist(self.playlist_cache[name])
                return self.playlist_cache[name]
            except:
                pass

        # Search for existing playlist
        playlists = self.sp.user_playlists(self.user_id)
        for playlist in playlists['items']:
            if playlist['name'] == name:
                self.playlist_cache[name] = playlist['id']
                self._save_playlist_cache()
                return playlist['id']

        # Create new playlist
        playlist = self.sp.user_playlist_create(self.user_id, name)
        self.playlist_cache[name] = playlist['id']
        self._save_playlist_cache()
        return playlist['id']

    def search_track(self, title: str, artist: str) -> Optional[str]:
        # Search for track with fuzzy matching
        # Try exact match first
        query = f"track:{title} artist:{artist}"
        results = self.sp.search(q=query, type='track', limit=1)
        
        if results['tracks']['items']:
            return results['tracks']['items'][0]['id']
        
        # Try more lenient search
        query = f"{title} {artist}"
        results = self.sp.search(q=query, type='track', limit=5)
        
        if results['tracks']['items']:
            # You could implement more sophisticated matching here
            return results['tracks']['items'][0]['id']
        
        return None

    def get_existing_tracks(self, playlist_id: str) -> set:
        # Get all tracks currently in the playlist
        existing_tracks = set()
        results = self.sp.playlist_tracks(playlist_id)
        
        while results:
            for item in results['items']:
                if item['track']:
                    existing_tracks.add(item['track']['id'])
            
            if results['next']:
                results = self.sp.next(results)
            else:
                break
        
        return existing_tracks

    def upload_songs(self, songs: List[Dict], playlist_name: Optional[str] = None) -> Dict:
        # Upload songs to Spotify playlist and return results
        playlist_name = playlist_name or env.get_default_playlist_name()
        playlist_id = self.get_or_create_playlist(playlist_name)
        
        # Get existing tracks to avoid duplicates
        print("\nChecking existing playlist tracks...")
        existing_tracks = self.get_existing_tracks(playlist_id)
        if existing_tracks:
            print(f"Found {len(existing_tracks)} existing tracks in playlist")
        
        results = {
            'success': [],
            'failed': [],
            'skipped': [],  # Track songs already in playlist
            'invalid_metadata': []  # Track songs with missing/unknown metadata
        }
        
        # Process songs in batches
        track_ids = []
        total_songs = len(songs)
        
        print(f"\nSearching and uploading {total_songs} songs to Spotify...")
        print("Progress: [", end="", flush=True)
        
        for idx, song in enumerate(songs, 1):
            # Print progress bar
            if idx % (total_songs // 50 + 1) == 0:  # Update roughly 50 times
                print("=", end="", flush=True)
            
            # Skip songs with Unknown metadata
            if song['title'] == 'Unknown Title' or song['artist'] == 'Unknown Artist':
                results['invalid_metadata'].append({
                    'original_song': song,
                    'reason': f"Invalid metadata: {'Unknown Title' if song['title'] == 'Unknown Title' else ''}"
                             f"{'Unknown Artist' if song['artist'] == 'Unknown Artist' else ''}"
                })
                continue
            
            track_id = self.search_track(song['title'], song['artist'])
            
            if track_id:
                if track_id in existing_tracks:
                    results['skipped'].append({
                        'original_song': song,
                        'reason': 'Already in playlist'
                    })
                else:
                    track_ids.append(track_id)
                    results['success'].append({
                        'original_song': song,
                        'spotify_track_id': track_id
                    })
            else:
                results['failed'].append({
                    'original_song': song,
                    'reason': 'No matching song found on Spotify'
                })
            
            # Add tracks in batches of 100 (Spotify API limit)
            if len(track_ids) >= 100:
                try:
                    self.sp.playlist_add_items(playlist_id, track_ids)
                    print(f"\nUploaded batch of {len(track_ids)} songs...")
                    track_ids = []
                except Exception as e:
                    print(f"\nError uploading batch: {str(e)}")
                    # Move failed batch to failed results
                    last_batch = results['success'][-len(track_ids):]
                    results['success'] = results['success'][:-len(track_ids)]
                    results['failed'].extend([{
                        'original_song': item['original_song'],
                        'reason': f'Batch upload failed: {str(e)}'
                    } for item in last_batch])
                    track_ids = []
        
        # Add remaining tracks
        if track_ids:
            try:
                self.sp.playlist_add_items(playlist_id, track_ids)
                print(f"\nUploaded final batch of {len(track_ids)} songs...")
            except Exception as e:
                print(f"\nError uploading final batch: {str(e)}")
                # Move failed batch to failed results
                last_batch = results['success'][-len(track_ids):]
                results['success'] = results['success'][:-len(track_ids)]
                results['failed'].extend([{
                    'original_song': item['original_song'],
                    'reason': f'Batch upload failed: {str(e)}'
                } for item in last_batch])
        
        print("]\n")  # Close progress bar
        
        # Save results to file with more details
        output_data = {
            'total_songs': total_songs,
            'success_count': len(results['success']),
            'failed_count': len(results['failed']),
            'skipped_count': len(results['skipped']),
            'invalid_metadata_count': len(results['invalid_metadata']),
            'success_songs': results['success'],
            'failed_songs': results['failed'],
            'skipped_songs': results['skipped'],
            'invalid_metadata_songs': results['invalid_metadata']
        }
        
        with open('upload_results.json', 'w') as f:
            json.dump(output_data, f, indent=2)
        
        # Print summary
        print("\nUpload Summary:")
        print(f"Total songs processed: {total_songs}")
        print(f"Successfully uploaded: {len(results['success'])} songs")
        print(f"Already in playlist: {len(results['skipped'])} songs")
        print(f"Invalid metadata: {len(results['invalid_metadata'])} songs")
        print(f"Failed to upload: {len(results['failed'])} songs")
        
        if results['success']:
            success_rate = (len(results['success'])/total_songs)*100
            print(f"Success rate: {success_rate:.1f}%")
        
        if results['failed'] or results['skipped'] or results['invalid_metadata']:
            print(f"\nDetailed results saved to 'upload_results.json'")
        
        return results

def process_songs(songs_data: List[Dict] = None, json_path: str = None, playlist_name: Optional[str] = None):
    # Process songs either from direct data or JSON file
    songs = songs_data
    
    # If no direct data provided, try loading from JSON
    if songs is None:
        if not json_path:
            raise ValueError("Either songs_data or json_path must be provided")
            
        try:
            with open(json_path, 'r') as f:
                songs = json.load(f)
        except Exception as e:
            raise ValueError(f"Failed to load songs from {json_path}: {str(e)}")
    
    # Validate we have data after all attempts
    if not songs:
        raise ValueError("No songs provided (empty data)")
    
    # Process the songs
    uploader = SpotifyUploader()
    return uploader.upload_songs(songs, playlist_name) 