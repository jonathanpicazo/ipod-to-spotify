import os
from typing import Optional, Dict
from dotenv import load_dotenv

def _find_env_file() -> str:
    # Get the project root directory (same level as poetry.lock)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    return os.path.join(project_root, '.env')

def _print_env_status(env_path: str, required_vars: list) -> None:
    # Print environment loading status
    print("\nLooking for .env file:")
    print(f"Current directory: {os.path.dirname(os.path.abspath(__file__))}")
    print(f"Project root: {os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))}")
    print(f"Expected .env path: {env_path}")
    
    if os.path.exists(env_path):
        print(f"\nFound .env file at: {env_path}")
        # Load the environment variables before checking them
        load_dotenv(env_path, override=True)
        
        print("\nEnvironment variables status:")
        print("-" * 30)
        for var in required_vars:
            value = os.getenv(var)
            # Only show first/last few chars of secrets for security
            if value and var != 'SPOTIFY_REDIRECT_URI':
                masked_value = value[:4] + '...' + value[-4:] if len(value) > 8 else '***'
                print(f"{var}: {masked_value}")
            else:
                print(f"{var}: {value if value else 'NOT SET'}")
        print("-" * 30)
    else:
        print("\nError: Could not find .env file")
        print("Please ensure .env file exists in the project root (same level as poetry.lock)")

def _verify_env_file(env_path: str) -> Optional[str]:
    # Verify that the .env file exists and has content
    if not os.path.exists(env_path):
        return "Environment file not found"
    
    try:
        with open(env_path, 'r') as f:
            content = f.read().strip()
            if not content:
                return "Environment file is empty"
            
            # Check if it contains placeholder values
            if 'your_client_id_here' in content or 'your_client_secret_here' in content:
                return "Environment file contains placeholder values. Please replace them with your actual Spotify credentials."
            
            # Basic format check
            lines = content.split('\n')
            for line in lines:
                if line.strip() and '=' not in line:
                    return f"Invalid line format in .env file: {line}"
    except Exception as e:
        return f"Error reading environment file: {str(e)}"
    
    return None

def load_spotify_env() -> Optional[str]:
    # Load and validate Spotify environment variables
    env_path = _find_env_file()
    required_vars = [
        'SPOTIFY_CLIENT_ID',
        'SPOTIFY_CLIENT_SECRET',
        'SPOTIFY_REDIRECT_URI'
    ]
    
    # Verify the .env file first
    error = _verify_env_file(env_path)
    if error:
        return error
    
    # Load environment variables with override to ensure fresh values
    load_dotenv(env_path, override=True)
    
    # Print status after loading
    _print_env_status(env_path, required_vars)
    
    missing = [var for var in required_vars if not os.getenv(var)]
    
    if missing:
        return f"""
Missing required Spotify credentials in .env file:
{', '.join(missing)}

Please create a .env file in the project root with the following:
SPOTIFY_CLIENT_ID=your_client_id_here
SPOTIFY_CLIENT_SECRET=your_client_secret_here
SPOTIFY_REDIRECT_URI=http://127.0.0.1:8888/callback

You can get these credentials by:
1. Going to https://developer.spotify.com/dashboard
2. Creating a new application
3. Getting the client ID and secret
4. Adding http://127.0.0.1:8888/callback to the Redirect URIs in your Spotify app settings
"""
    
    print("\nSuccessfully loaded all required environment variables")
    return None

def get_spotify_creds() -> Dict[str, str]:
    # Return Spotify credentials as a dictionary
    return {
        'client_id': os.getenv('SPOTIFY_CLIENT_ID'),
        'client_secret': os.getenv('SPOTIFY_CLIENT_SECRET'),
        'redirect_uri': os.getenv('SPOTIFY_REDIRECT_URI')
    }

def get_default_playlist_name() -> str:
    # Get default playlist name from env or return fallback
    return os.getenv('DEFAULT_PLAYLIST_NAME', 'iPod Library') 