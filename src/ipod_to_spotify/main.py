from .commands import (
    load_existing_songs,
    print_song_samples,
    handle_spotify_upload,
    check_metadata,
    handle_ipod_scan
)

def main():
    # Check for existing songs data
    existing_songs = load_existing_songs()
    
    if existing_songs:
        print(f"Found existing song data ({len(existing_songs)} songs)")
        print("\nWhat would you like to do?")
        print("1. Use existing song data")
        print("2. Check metadata only")
        print("3. Rescan iPod")
        print("4. Exit")
        
        while True:
            choice = input("\nEnter your choice (1-4): ").strip()
            if choice == "1":
                print_song_samples(existing_songs)
                handle_spotify_upload(existing_songs)
                break
            elif choice == "2":
                check_metadata(existing_songs)
                break
            elif choice == "3":
                # Fall through to iPod scanning
                break
            elif choice == "4":
                print("Exiting script...")
                return
            else:
                print("Invalid choice. Please enter 1-4.")
        
        if choice in ["1", "2"]:  # If user chose to use existing data or check metadata, we're done
            return
    
    # If we get here, we need to scan the iPod
    songs = handle_ipod_scan()
    
    if songs:
        print_song_samples(songs)
        print("\nWhat would you like to do?")
        print("1. Upload to Spotify")
        print("2. Check metadata only")
        print("3. Exit")
        
        while True:
            choice = input("\nEnter your choice (1-3): ").strip()
            if choice == "1":
                handle_spotify_upload(songs)
                break
            elif choice == "2":
                check_metadata(songs)
                break
            elif choice == "3":
                print("Exiting script...")
                break
            else:
                print("Invalid choice. Please enter 1-3.")
    else:
        print("No songs found with readable metadata")

if __name__ == "__main__":
    main()