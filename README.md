# Instagram Reels Scraper

Hey there! 👋 This is a handy Python tool I built to help you gather data from Instagram reels. Whether you're interested in analyzing a single account or keeping tabs on multiple creators, this tool has got you covered.

## What Can It Do?

✨ Here's what makes this tool special:
- Grab reels data from any public Instagram account
- Work with multiple accounts at once using a simple text file
- Smart login handling that remembers your session
- Works with 2FA-enabled accounts
- Keeps detailed logs so you know exactly what's happening
- Takes screenshots when something goes wrong (super helpful for debugging!)
- Lets you tweak settings to match your needs

## Before You Start

You'll need:
- Python 3.x installed on your computer
- Chrome browser
- ChromeDriver (don't worry, the tool manages this for you!)

## Getting Started

1. First, grab the code:
```bash
git clone https://github.com/mazithesage/igscrapper.git
cd igscrapper
```

2. Install the tools we'll need:
```bash
pip install -r requirements.txt
```

## Setting Things Up

1. Open up `main.py` and add your Instagram login details:
```python
INSTAGRAM_USERNAME = "your_username"
INSTAGRAM_PASSWORD = "your_password"
```

2. Want to fine-tune things? You can adjust these settings in `main.py` (totally optional):
```python
MAX_POST_URLS_TO_SCRAPE = 50  # How many reels to grab
MAX_SCROLL_ATTEMPTS = 20       # How far to scroll
SCROLL_PAUSE_TIME = 3.5        # Time between scrolls
```

## How to Use

1. Fire it up:
```bash
python main.py
```

2. Pick how you want to use it:
   - Option 1: Look at one account's reels
   - Option 2: Check multiple accounts (from a list)
   - Option 3: Close the tool

### Looking at One Account
Just type in the Instagram username you're interested in, and the tool will do its thing! Simple as that.

### Checking Multiple Accounts
1. Create a text file with usernames (one per line)
2. When asked, tell the tool where to find your list
3. Sit back and let it work through each account

## Where to Find Your Data

- Everything gets saved in a folder called `scraped_data`
- Each file has a timestamp (like `reels_username_20250413_224556.json`)
- All the juicy details about each reel are saved in an easy-to-read format

## Keeping Track

- The tool keeps notes about what it's doing in `instagram_scraper.log`
- You'll see updates in real-time as it works
- If something goes wrong, it takes screenshots to help figure out what happened

## Playing it Safe

- Built-in safety nets to handle hiccups along the way
- Remembers your login so you don't have to keep signing in
- Takes breaks between requests to play nice with Instagram
- Smart enough to retry if something doesn't work the first time

## Quick Note

🎓 This tool is meant for learning and research. Make sure you're familiar with Instagram's rules before using it. I'm not responsible for how others might use this tool.

## License

It's under the MIT License - which means you can use it, change it, and share it freely! 🎉
