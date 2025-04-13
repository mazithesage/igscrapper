# Instagram Reels Scraper

A powerful Python-based tool for scraping Instagram reels data using Selenium WebDriver. This tool allows you to collect detailed information about reels from either single or multiple Instagram accounts.

## Features

- Scrape reels from a single Instagram user
- Bulk scraping from multiple users using a text file
- Automatic session handling with cookie persistence
- Two-factor authentication (2FA) support
- Detailed logging system
- Screenshot capture for debugging
- Customizable scraping parameters

## Requirements

- Python 3.x
- Chrome browser
- ChromeDriver (automatically managed)

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/igscrapper.git
cd igscrapper
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

## Configuration

1. Open `main.py` and update your Instagram credentials:
```python
INSTAGRAM_USERNAME = "your_username"
INSTAGRAM_PASSWORD = "your_password"
```

2. (Optional) Adjust scraping parameters in `main.py`:
```python
MAX_POST_URLS_TO_SCRAPE = 50
MAX_SCROLL_ATTEMPTS = 20
SCROLL_PAUSE_TIME = 3.5
```

## Usage

1. Run the script:
```bash
python main.py
```

2. Choose your scraping mode:
   - Option 1: Scrape reels from a single user
   - Option 2: Scrape reels from multiple users (via text file)
   - Option 3: Exit

### Single User Mode
- Enter the target Instagram username when prompted
- The script will automatically scrape their reels

### Bulk Mode
- Prepare a text file with one Instagram username per line
- Enter the path to your usernames file when prompted
- The script will process each username sequentially

## Output

- Scraped data is saved in the `scraped_data` directory
- Files are named with timestamps (e.g., `reels_username_20250413_224556.json`)
- Each reel's data is stored in JSON format with detailed information

## Logging

- All activities are logged to `instagram_scraper.log`
- Console output provides real-time progress updates
- Screenshots are saved for debugging purposes

## Error Handling

- Automatic retry mechanism for failed requests
- Session persistence to minimize login requirements
- Detailed error logging with screenshots for debugging

## Safety Features

- Rate limiting to prevent Instagram blocks
- Cookie-based session management
- Configurable delays between requests

## Disclaimer

This tool is for educational purposes only. Please review Instagram's terms of service and use responsibly. The developers are not responsible for any misuse of this tool.

## License

MIT License - feel free to use and modify as needed.
