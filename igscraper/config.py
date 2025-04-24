import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
ENV_PATH = Path('.') / '.env'
load_dotenv(dotenv_path=ENV_PATH)

# Constants
LOGIN_URL = 'https://www.instagram.com/accounts/login/'
INSTAGRAM_BASE_URL = 'https://www.instagram.com/'
SHORT_DELAY_MS = 2000  # Renamed for clarity
EXPLICIT_WAIT_TIMEOUT_S = 20  # Renamed for clarity (seconds)
COOKIES_FILENAME = 'instagram_cookies.json' # Renamed for clarity
RESULTS_FILENAME = 'reels_results.json'

# Environment Variables (consider adding default values or error handling)
INSTAGRAM_USERNAME = os.getenv('INSTAGRAM_USERNAME')
INSTAGRAM_PASSWORD = os.getenv('INSTAGRAM_PASSWORD')
INSTAGRAM_SESSION_COOKIES = os.getenv('INSTAGRAM_SESSION_COOKIES')

def check_credentials():
    """Checks if essential credentials are provided."""
    if not INSTAGRAM_USERNAME or not INSTAGRAM_PASSWORD:
        if not ENV_PATH.exists():
            raise ValueError('Could not find .env file. Please create one with INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD.')
        else:
            raise ValueError('Please ensure INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD are set in your .env file.')
    return True 