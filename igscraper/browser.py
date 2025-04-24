import asyncio
import json
import random
from pathlib import Path
from pyppeteer import launch
from pyppeteer.page import Page # Specific import for type hinting
from typing import Optional

from igscraper.logger import Logger
from igscraper.config import (
    COOKIES_FILENAME,
    INSTAGRAM_SESSION_COOKIES
)

async def setup_browser() -> 'Browser':
    """Launch and configure the browser."""
    try:
        Logger.info('Launching browser...')
        # Consider making headless configurable via config.py or args
        browser = await launch({
            'headless': False, 
            'args': [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--disable-gpu',
                '--window-size=1920x1080',
            ],
            'defaultViewport': None
        })
        return browser
    except Exception as e:
        Logger.error(f'Error setting up browser: {str(e)}')
        raise

async def save_cookies(page: Page) -> bool:
    """Save cookies to file for session persistence."""
    try:
        cookies = await page.cookies()
        with open(COOKIES_FILENAME, 'w') as f:
            json.dump(cookies, f, indent=2)
        Logger.info(f'Cookies saved to {COOKIES_FILENAME}')
        return True
    except Exception as e:
        Logger.error(f'Error saving cookies: {str(e)}')
        return False

async def load_cookies(page: Page) -> bool:
    """Load cookies from environment variable or file."""
    cookies_loaded = False
    
    # 1. Try loading from environment variable
    if INSTAGRAM_SESSION_COOKIES:
        Logger.info('Found INSTAGRAM_SESSION_COOKIES environment variable.')
        try:
            cookies = json.loads(INSTAGRAM_SESSION_COOKIES)
            if isinstance(cookies, list):
                await page.setCookie(*cookies)
                Logger.info('Cookies loaded successfully from environment variable.')
                cookies_loaded = True
            else:
                Logger.warning('INSTAGRAM_SESSION_COOKIES does not contain a valid JSON list.')
        except json.JSONDecodeError:
            Logger.error('Failed to parse JSON from INSTAGRAM_SESSION_COOKIES.')
        except Exception as e:
            Logger.error(f'Error setting cookies from environment variable: {str(e)}')

    # 2. If not loaded from env var, try loading from file
    if not cookies_loaded:
        Logger.info(f'Attempting to load cookies from file: {COOKIES_FILENAME}')
        try:
            cookies_path = Path(COOKIES_FILENAME)
            if not cookies_path.exists():
                Logger.info(f'Cookies file not found: {COOKIES_FILENAME}')
                return False

            with open(cookies_path, 'r') as f:
                cookies = json.load(f)
            await page.setCookie(*cookies)
            Logger.info(f'Cookies loaded successfully from {COOKIES_FILENAME}.')
            cookies_loaded = True
        except json.JSONDecodeError:
            Logger.error(f'Failed to parse JSON from cookies file: {COOKIES_FILENAME}')
        except Exception as e:
            Logger.error(f'Error loading cookies from file: {str(e)}')

    return cookies_loaded

async def try_click_not_now(page: Page) -> bool:
    """Attempts to find and click common 'Not Now' buttons."""
    not_now_selectors = [
        "//button[contains(text(), 'Not Now')]",
        "//div[@role='dialog']//button[contains(., 'Not Now')]", 
        "button._a9--._a9_1" # Example class-based selector (may change)
    ]
    clicked = False
    for selector in not_now_selectors:
        try:
            if selector.startswith("//"):
                 button = await page.waitForXPath(selector, timeout=2000) 
            else:
                 button = await page.waitForSelector(selector, timeout=2000)
            
            if button:
                await button.click()
                Logger.info(f"Clicked 'Not Now' button using selector: {selector}")
                await asyncio.sleep(1.0)
                clicked = True
                # Optionally break if we assume one click is enough, 
                # or continue to catch multiple popups
                # break 
        except Exception:
            pass # Ignore if not found, try next selector
    if not clicked:
        Logger.info("No 'Not Now' popups found or clicked.")
    return clicked 