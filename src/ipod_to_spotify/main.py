import json
from .metadata import scan_ipod_for_audio
from .device import find_ipod_path

def main():
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