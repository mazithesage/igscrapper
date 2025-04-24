# Instagram Reels Scraper (Pyppeteer Version)

This Python project scrapes metadata (caption, date, URL, shortcode) for Instagram Reels from specified public accounts using Pyppeteer (a Python port of Puppeteer). It supports multi-account scraping, session persistence via cookies, and loading credentials from a `.env` file.

## Features

*   **Detailed Reel Data:** Extracts shortcode, URL, caption, and publication date for each reel.
*   **Multi-Account Scraping:** Can scrape reels from a list of target usernames in a single run.
*   **Pyppeteer Backend:** Utilizes `pyppeteer` for browser automation, controlling a headless or non-headless Chromium instance.
*   **Session Persistence:** Saves and loads login cookies (`instagram_cookies.json`) to minimize manual logins. Can also load cookies from an environment variable (`INSTAGRAM_SESSION_COOKIES`).
*   **Credential Management:** Securely loads Instagram username and password from a `.env` file.
*   **Modular Structure:** Codebase is organized into logical modules (`config`, `browser`, `login`, `scraper`) within the `igscraper` package for better maintainability.
*   **Basic Popup Handling:** Attempts to dismiss common post-login popups ("Save Info?", "Turn on Notifications?").
*   **Structured Output:** Saves scraped data in a well-formatted JSON file (`reels_results.json`).

## Project Structure

```
igscrapper/
├── igscraper/
│   ├── __init__.py       # Makes 'igscraper' a Python package
│   ├── logger.py         # Simple console logger
│   ├── config.py         # Constants, .env loading, credentials
│   ├── browser.py        # Browser setup, cookie handling, popups
│   ├── login.py          # Login, 2FA, session status logic
│   └── scraper.py        # Reel scraping logic (list & details)
├── main.py             # Main script entry point
├── .env.example        # Example environment file (!!! DO NOT COMMIT ACTUAL .env FILE !!!)
├── requirements.txt    # Project dependencies
├── .gitignore          # Git ignore rules
├── README.md           # This file
└── reels_results.json  # Output file (created after successful run)
└── instagram_cookies.json # Saved cookies (created after successful login)
```

## Setup Instructions

**1. Prerequisites:**
    *   Python 3.8+
    *   pip (Python package installer)

**2. Clone the Repository:**
    ```bash
    git clone https://github.com/mazithesage/igscrapper.git
    cd igscrapper
    ```

**3. Install Dependencies:**
    This will install `pyppeteer`, `python-dotenv`, and other required packages. It will also download a compatible Chromium browser the first time `pyppeteer` is used.
    ```bash
    pip install -r requirements.txt
    ```

**4. Create `.env` File:**
    Create a file named `.env` in the project root directory. **Do not commit this file to Git.** Add your Instagram credentials:
    ```dotenv
    # .env
    INSTAGRAM_USERNAME="your_instagram_username"
    INSTAGRAM_PASSWORD="your_instagram_password"

    # Optional: Proxy server configuration
    # Uncomment and set if you want to route traffic through a proxy.
    # Use the format scheme://host:port (e.g., http://127.0.0.1:8080 or socks5://proxy.example.com:1080)
    # PROXY_STRING="http://your_proxy_host:your_proxy_port"

    # Optional: Add session cookies as a JSON string if you have them
    # INSTAGRAM_SESSION_COOKIES='[{"name": "sessionid", "value": "...", ...}]'
    ```
    *(See `.env.example` for a template)*

## Usage

**1. Configure Target Accounts:**
    *   Open the `main.py` file.
    *   Locate the `target_usernames` list within the `main()` function.
    *   Modify this list to include the Instagram usernames you want to scrape.
    ```python
    # main.py
    async def main():
        # ...
        # --- Define Target Usernames ---
        target_usernames = ['nasa', 'natgeo', 'another_user'] # <-- EDIT THIS LIST
        Logger.info(f'Target accounts: {target_usernames}')
        # ...
    ```
    *(Alternatively, you could modify the script to read usernames from a file like `target_accounts.txt`)*

**2. Run the Scraper:**
    Execute the `main.py` script from your terminal:
    ```bash
    python3 main.py
    ```

**3. Monitor Output:**
    *   The script will log its progress to the console, including browser launch, login attempts, 2FA prompts (if any), and scraping progress for each account and reel.
    *   If 2FA is required, you will be prompted to enter the code directly in the terminal.
    *   A non-headless browser window will open, allowing you to observe the automation (useful for debugging).

**4. Get Results:**
    *   Upon successful completion, the scraped data will be saved in the `reels_results.json` file in the project root.
    *   The file structure will be a JSON object where keys are the target usernames and values are lists of dictionaries, each dictionary containing the details for one scraped reel.
    ```json
    // Example reels_results.json
    {
      "nasa": [
        {
          "shortcode": "C8...",
          "url": "https://www.instagram.com/nasa/reel/C8.../",
          "is_video": true,
          "type": "Reel",
          "date": "2024-06-12T...",
          "caption": "Caption text here..."
        },
        // ... more reels from nasa
      ],
      "natgeo": [
        {
          "shortcode": "C7...",
          "url": "https://www.instagram.com/natgeo/reel/C7.../",
          // ... details ...
        },
        // ... more reels from natgeo
      ]
    }
    ```

## Important Considerations

*   **Proxy Usage:** You can configure a proxy via the `PROXY_STRING` environment variable in your `.env` file. Note that this implementation does **not** handle proxy authentication (username/password). Use proxies that authenticate via IP whitelisting or use a middleware proxy solution if authentication is required.
*   **Instagram Updates:** Instagram frequently changes its website structure (HTML elements, CSS classes, internal APIs, JSON data formats). This **will inevitably break the scraper's selectors** and data extraction logic over time. You will likely need to manually inspect the Instagram website using browser developer tools and update the selectors in `igscraper/scraper.py` (primarily `scrape_reel_details`) periodically.
*   **Rate Limiting & Blocks:** Scraping too aggressively (visiting many pages quickly) can lead to temporary or permanent blocks from Instagram. This script includes delays, but use it responsibly. Scraping large numbers of reels or accounts increases the risk. Consider adding longer delays or scraping fewer accounts per run if you encounter issues.
*   **Ethical Use & Terms of Service:** This tool is intended for educational and personal analysis purposes. Automated access may violate Instagram's Terms of Service. Use this tool ethically and at your own risk. The developers are not responsible for misuse or any consequences thereof.
*   **Login Stability:** Instagram's login process can be complex and change often. While this script handles basic login and 2FA, it may fail if Instagram introduces new challenges or modifies the flow. Session cookies help but can expire.
*   **Data Accuracy:** The accuracy of scraped data (especially caption and date) depends on the stability of the selectors and the availability of data in embedded JSON. Fallback HTML scraping is less reliable.

## Troubleshooting

*   **Login Failed:**
    *   Double-check credentials in `.env`.
    *   Check console logs for specific error messages.
    *   Watch the browser window for unexpected pages or prompts.
    *   Delete `instagram_cookies.json` to force a fresh login attempt.
    *   Instagram may have implemented a new login challenge.
*   **No Data in `reels_results.json` (Empty Lists):**
    *   Check console logs for errors during the "Scraping details for reel..." phase. This usually indicates outdated selectors in `scrape_reel_details`.
    *   The target accounts might be private or have no reels.
    *   Instagram might be blocking content loading when visiting individual reel pages.
*   **Script Crashes / Errors:**
    *   Note the full error message and traceback from the console.
    *   Ensure all dependencies are installed (`pip install -r requirements.txt`).
    *   Check for `pyppeteer` or `asyncio` related errors.

## Potential Future Enhancements

*   Implement Python's `logging` module for more robust logging (levels, file output).
*   Add more sophisticated error handling and retry mechanisms.
*   Develop more resilient selector strategies (if possible).
*   Add command-line arguments for configuration (target users, headless mode).
*   Implement unit/integration tests.
*   Explore options for managing target accounts via a file instead of editing `main.py`.
