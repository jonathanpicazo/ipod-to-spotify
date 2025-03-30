import os
import sys

def cleanup():
    # Files to clean up
    files_to_remove = [
        'metadata_check_results.json', # Metadata check results
        'ipod_songs.json',        # Scanned songs metadata
        'upload_results.json',    # Upload results and statistics
        'playlist_cache.json',    # Spotify playlist cache
        '.cache'                  # Spotify authentication cache
    ]
    
    print("\nCleaning up cache and data files...")
    
    found = False
    for file in files_to_remove:
        if os.path.exists(file):
            try:
                os.remove(file)
                print(f"Removed: {file}")
                found = True
            except Exception as e:
                print(f"Error removing {file}: {e}")
    
    if not found:
        print("No cache or data files found to clean up.")
    else:
        print("\nCleanup complete!")

if __name__ == "__main__":
    cleanup() 