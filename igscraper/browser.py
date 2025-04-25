# igscraper/browser.py
# Contains functions related to browser setup, interaction, and cookie management.

import asyncio
import json
import random
from pathlib import Path
from pyppeteer import launch
from pyppeteer.page import Page # Specific import for type hinting
from pyppeteer.browser import Browser # Specific import for type hinting
from typing import Optional

from igscraper.logger import Logger
from igscraper.config import (
    COOKIES_FILENAME,
    INSTAGRAM_SESSION_COOKIES
)

async def setup_browser() -> Browser:
    """Launches and configures a Pyppeteer browser instance."""
    try:
        Logger.info('Launching browser...')
        
        launch_args = [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-accelerated-2d-canvas',
            '--disable-gpu',
            '--window-size=1920x1080',
        ]

        browser = await launch({
            'headless': True, 
            'args': launch_args,
            'defaultViewport': None 
        })
        return browser
    except Exception as e:
        Logger.error(f'Error setting up browser: {str(e)}')
        raise

async def save_cookies(page: Page) -> bool:
    """Saves the current page's cookies to a JSON file."""
    try:
        cookies = await page.cookies()
        # Use project root from config? For now, assume current dir.
        cookies_path = Path(COOKIES_FILENAME) 
        with open(cookies_path, 'w') as f:
            json.dump(cookies, f, indent=2) # indent=2 for readability
        Logger.info(f'Cookies saved to {cookies_path}')
        return True
    except Exception as e:
        Logger.error(f'Error saving cookies: {str(e)}')
        return False

async def load_cookies(page: Page) -> bool:
    """Loads cookies into the page, prioritizing environment variable then file."""
    cookies_loaded = False
    
    # Priority 1: Environment Variable (INSTAGRAM_SESSION_COOKIES)
    if INSTAGRAM_SESSION_COOKIES:
        Logger.info('Attempting to load cookies from INSTAGRAM_SESSION_COOKIES env var.')
        try:
            # The env var must contain a valid JSON string representing a list of cookies.
            cookies = json.loads(INSTAGRAM_SESSION_COOKIES)
            if isinstance(cookies, list):
                # setCookie takes positional arguments, hence the splat (*)
                await page.setCookie(*cookies)
                Logger.info('Cookies loaded successfully from environment variable.')
                cookies_loaded = True
            else:
                Logger.warning('INSTAGRAM_SESSION_COOKIES does not contain a valid JSON list.')
        except json.JSONDecodeError:
            Logger.error('Failed to parse JSON from INSTAGRAM_SESSION_COOKIES.')
        except Exception as e:
            # Catch other potential errors during setCookie
            Logger.error(f'Error setting cookies from environment variable: {str(e)}')

    # Priority 2: File (if not loaded from env var)
    if not cookies_loaded:
        cookies_path = Path(COOKIES_FILENAME)
        Logger.info(f'Attempting to load cookies from file: {cookies_path}')
        try:
            if not cookies_path.exists():
                Logger.info(f'Cookies file not found: {cookies_path}')
                return False # Return False explicitly if file doesn't exist

            with open(cookies_path, 'r') as f:
                cookies = json.load(f)
            # Ensure cookies from file are also a list before setting
            if isinstance(cookies, list):
                await page.setCookie(*cookies)
                Logger.info(f'Cookies loaded successfully from {cookies_path}.')
                cookies_loaded = True
            else:
                Logger.warning(f'Cookies file {cookies_path} does not contain a valid JSON list.')
        except json.JSONDecodeError:
            Logger.error(f'Failed to parse JSON from cookies file: {cookies_path}')
        except Exception as e:
            Logger.error(f'Error loading/setting cookies from file: {str(e)}')

    return cookies_loaded

async def try_click_not_now(page: Page) -> bool:
    """Attempts to find and click common 'Not Now' buttons after login.
    
    Handles potential popups like "Save Login Info?" or "Turn on Notifications?".
    Iterates through known selectors (XPath and CSS) as these popups change.
    """
    # Selectors are brittle and may need frequent updates.
    # Combine text-based XPath and potential CSS selectors.
    not_now_selectors = [
        "//button[contains(text(), 'Not Now')]", # Common text
        "//div[@role='dialog']//button[contains(., 'Not Now')]", # More specific within a dialog
        "button._a9--._a9_1" # Example CSS class selector observed previously (HIGHLY LIKELY TO CHANGE)
    ]
    clicked_any = False
    for selector in not_now_selectors:
        try:
            # Use appropriate waitFor function based on selector type
            if selector.startswith("//"):
                 # Use a short timeout as these popups appear quickly if they do
                 button = await page.waitForXPath(selector, { 'timeout': 2500 }) 
            else:
                 button = await page.waitForSelector(selector, { 'timeout': 2500 })
            
            if button:
                await asyncio.sleep(random.uniform(0.3, 0.8)) # Small delay before click
                await button.click()
                Logger.info(f"Clicked 'Not Now' button using selector: {selector}")
                await asyncio.sleep(random.uniform(1.0, 1.5)) # Wait for action to complete
                clicked_any = True
                # Depending on UI, multiple popups might appear.
                # Option 1: return True immediately after first click
                # Option 2: continue loop to potentially catch a second popup
                # Current implementation continues the loop.
        except Exception:
            # It's normal for selectors not to be found if the popup didn't appear.
            # Silently ignore TimeoutError or other exceptions here.
            pass 
            
    if not clicked_any:
        Logger.info("No common 'Not Now' popups found or clicked.")
        
    return clicked_any # Return True if any button was clicked 