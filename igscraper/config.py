# igscraper/config.py
# Handles configuration loading, constants, and credential management.

import os
from pathlib import Path
from dotenv import load_dotenv

# Determine the project root based on this file's location
# This makes it more robust if the script is run from a different directory.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = PROJECT_ROOT / '.env'

# Load environment variables from .env file found in the project root
# If the file doesn't exist, load_dotenv() will silently fail, 
# which is handled later by check_credentials.
load_dotenv(dotenv_path=ENV_PATH)

# --- Core Constants ---
LOGIN_URL = 'https://www.instagram.com/accounts/login/'
INSTAGRAM_BASE_URL = 'https://www.instagram.com/'

# Delays & Timeouts
SHORT_DELAY_MS = 2000  # General purpose short delay in milliseconds
EXPLICIT_WAIT_TIMEOUT_S = 20  # Max time in seconds for pyppeteer waits (e.g., waitForSelector)

# Filenames
COOKIES_FILENAME = 'instagram_cookies.json' # File to store session cookies
RESULTS_FILENAME = 'reels_results.json' # File to store final scraped data
SCREENSHOTS_DIR = 'screenshots' # Directory to store error screenshots

# --- Environment Variables --- 
# Fetched from the environment (or .env file) when the module is loaded.
INSTAGRAM_USERNAME = os.getenv('INSTAGRAM_USERNAME')
INSTAGRAM_PASSWORD = os.getenv('INSTAGRAM_PASSWORD')
# Optional session cookies can be provided via env var as a JSON string
INSTAGRAM_SESSION_COOKIES = os.getenv('INSTAGRAM_SESSION_COOKIES')
# Optional: Path to a file containing proxy servers (one per line, e.g., http://host:port)
PROXY_LIST_FILE = os.getenv('PROXY_LIST_FILE')

# --- Utility Functions ---
def check_credentials() -> bool:
    """Checks if essential INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD are provided either via env vars or .env file."""
    if not INSTAGRAM_USERNAME or not INSTAGRAM_PASSWORD:
        # Provide more specific error messages based on .env file presence
        if not ENV_PATH.exists():
            raise ValueError(
                f'Could not find .env file at {ENV_PATH}. ' 
                'Please create one with INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD.'
            )
        else:
            raise ValueError('Please ensure INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD are set in your .env file.')
    return True 