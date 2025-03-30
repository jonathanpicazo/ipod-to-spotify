# iPod to Spotify Transfer

Transfer your iPod music library to Spotify playlists easily. This tool scans your iPod for music files, extracts their metadata, and creates a matching Spotify playlist.

## Features

- 🎵 Automatic iPod detection and music scanning
- 📝 Smart metadata extraction from audio files
- 🔍 Intelligent title/artist parsing for files with combined metadata
- 🎯 Fuzzy matching with Spotify tracks
- 📊 Detailed upload reports and statistics
- ⚡ Batch processing for faster uploads
- 🔄 Resume capability with existing scans
- 🔎 Metadata validation without uploading

## Prerequisites

- Python 3.8 or higher
- Poetry (Python package manager)
- A Spotify account
- An iPod connected in disk mode

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/jonathan/ipod-to-spotify.git
   cd ipod-to-spotify
   ```

2. Install dependencies using Poetry:

   ```bash
   poetry install
   ```

3. Set up your Spotify credentials:

   - Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
   - Create a new application
   - Get your Client ID and Client Secret
   - Add `http://127.0.0.1:8888/callback` to your app's Redirect URIs

4. Create a `.env` file in the project root with your Spotify credentials:
   ```
   SPOTIFY_CLIENT_ID=your_client_id_here
   SPOTIFY_CLIENT_SECRET=your_client_secret_here
   SPOTIFY_REDIRECT_URI=http://127.0.0.1:8888/callback
   ```

## Usage

1. Connect your iPod in disk mode

2. Run the transfer script:

   ```bash
   poetry run start
   ```

3. Choose from the available options:

   - **Use existing song data**: Upload previously scanned songs to Spotify
   - **Check metadata only**: Validate song metadata without uploading
   - **Rescan iPod**: Perform a fresh scan of your iPod
   - **Exit**: Close the application

### Metadata Checking

The tool now includes a metadata validation feature that helps identify problematic files before uploading to Spotify. When using "Check metadata only":

- Scans all songs for missing or invalid metadata
- Identifies songs with unknown titles or artists
- Shows the raw file title for comparison
- Saves detailed results to `metadata_check_results.json`
- Helps troubleshoot why certain songs might fail to upload

### Files and Reports

- `ipod_songs.json`: Cached song metadata from iPod
- `upload_results.json`: Detailed upload results and statistics
- `metadata_check_results.json`: Metadata validation results
- `playlist_cache.json`: Spotify playlist information
- `.cache`: Spotify authentication cache

Use `poetry run cleanup` to remove all cache files and start fresh.

## How It Works

1. **iPod Detection**: The tool automatically looks for an iPod mounted in disk mode
2. **Music Scanning**: Scans the iPod's music directory for audio files
3. **Metadata Extraction**: Reads metadata from each audio file
4. **Smart Parsing**: Handles various metadata formats and separators
5. **Metadata Validation**: Checks for missing or invalid metadata
6. **Spotify Matching**: Searches Spotify for matching tracks
7. **Playlist Creation**: Creates or updates a Spotify playlist with found tracks
8. **Progress Tracking**: Maintains logs of successful uploads and any issues

## Troubleshooting

### Common Issues

1. **iPod Not Detected**:

   - Ensure iPod is connected and in disk mode
   - Try manually entering the iPod path

2. **Spotify Authentication Errors**:

   - Verify your credentials in `.env` file
   - Check that redirect URI matches your Spotify app settings

3. **Missing Metadata**:
   - Use the "Check metadata only" option to identify problematic files
   - Check `metadata_check_results.json` for detailed information
   - Common issues include:
     - Missing artist information
     - Unknown or malformed titles
     - Incomplete metadata tags

## Future Updates

### Planned Features

1. **Graphical User Interface**:

   - Modern, user-friendly interface
   - Drag-and-drop functionality
   - Visual progress indicators
   - Interactive playlist management
   - Real-time upload status
   - Dark/light theme support

2. **Enhanced Matching**:

   - Improved fuzzy matching algorithm
   - Manual matching for unmatched songs
   - Batch correction tools

3. **Additional Features**:
   - Multiple playlist support
   - Playlist organization options
   - Cover art matching
   - Export/import capabilities
   - Backup functionality

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
