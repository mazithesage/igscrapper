# igscraper/scraper.py
# Contains the core logic for scraping Instagram Reels.

import asyncio
import json
import random
import time # Import time for timestamp
from pathlib import Path # Import Path
from pyppeteer.page import Page
from typing import List, Dict, Optional

from igscraper.logger import Logger
from igscraper.config import (
    EXPLICIT_WAIT_TIMEOUT_S,
    SHORT_DELAY_MS,
    SCREENSHOTS_DIR # Import screenshot dir
)

async def scrape_reel_details(page: Page, reel_url: str) -> Optional[Dict]:
    """Navigates to a single reel URL and extracts detailed metadata.
    
    Prioritizes extracting data from embedded JSON-LD script tags.
    Falls back to scraping specific HTML elements if JSON-LD fails or lacks data.
    Returns a dictionary with details or None if essential data is missing.
    """
    # Extract shortcode for logging and as part of the data
    shortcode = reel_url.split("/reel/")[-1].split("/")[0]
    Logger.info(f"  Scraping details for reel: {shortcode} ({reel_url})")
    details = {
        "shortcode": shortcode,
        "url": reel_url,
        "is_video": True, # By definition, Reels are videos
        "type": "Reel",
        "date": None,
        "caption": None
    }
    
    try:
        # Navigate to the individual reel page
        timeout_ms = EXPLICIT_WAIT_TIMEOUT_S * 1000 # Convert s to ms
        # Use a slightly longer timeout for individual reel pages as they can be heavy
        await page.goto(reel_url, {'waitUntil': 'networkidle0', 'timeout': timeout_ms * 1.5}) 
        # Wait after load for potentially dynamic content rendering (caption/date)
        await asyncio.sleep(random.uniform(2.0, 4.0))

        # --- Method 1: Attempt to extract from embedded JSON-LD --- 
        # This is generally more reliable than HTML selectors if available.
        extracted_from_json = False
        try:
            # Find the script tag containing JSON-LD data.
            json_ld_selector = 'script[type="application/ld+json"]'
            json_ld_element = await page.querySelector(json_ld_selector)
            
            if json_ld_element:
                Logger.info(f"    Found JSON-LD script tag for {shortcode}.")
                # Extract the text content of the script tag.
                json_ld_content = await page.evaluate('(element) => element.textContent', json_ld_element)
                # Parse the text content as JSON.
                data = json.loads(json_ld_content)
                
                # JSON-LD data might be wrapped in a list.
                if isinstance(data, list): data = data[0]

                # Check if it's a dictionary and has the expected type.
                if isinstance(data, dict) and ("VideoObject" in data.get("@type", "") or "Clip" in data.get("@type", "")):
                    # Extract fields using .get() for safety in case keys are missing.
                    # Prioritize standard keys, fallback to alternatives.
                    details["caption"] = data.get("caption") or data.get("description") or data.get("name")
                    details["date"] = data.get("uploadDate") or data.get("datePublished")
                    
                    # Log success/failure for individual fields
                    if details["caption"]: Logger.info(f"      Extracted caption via JSON-LD.")
                    else: Logger.warning(f"      Caption not found in JSON-LD.")
                    if details["date"]: Logger.info(f"      Extracted date via JSON-LD: {details['date']}")
                    else: Logger.warning(f"      Date not found in JSON-LD.")
                        
                    # Mark as successful if we got at least caption or date
                    extracted_from_json = bool(details["caption"] or details["date"])
                else:
                    Logger.warning(f"    JSON-LD found but type mismatch or not a dictionary: {data.get('@type', 'N/A')}")
            else:
                Logger.info(f"    JSON-LD script tag not found using selector: {json_ld_selector}")
            
            # Placeholder: Could add attempts here to find other JSON blobs 
            # (e.g., in window.__sharedData or similar patterns if JSON-LD fails)

        except Exception as json_err:
            # Catch errors during JSON parsing or processing.
            Logger.warning(f"    Error processing JSON-LD for {shortcode}: {json_err}")
            extracted_from_json = False

        # --- Method 2: Fallback to HTML scraping if JSON failed or missed data --- 
        if not details["caption"] or not details["date"]:
            Logger.info(f"    Attempting HTML scraping for missing details ({shortcode}).")
            try:
                # Scrape Caption via HTML (if not found in JSON)
                if not details["caption"]:
                    # Strategy: Try H1 first, then fallback to more specific (brittle) selectors.
                    # Selectors MUST be updated based on current Instagram structure.
                    h1_selector = 'h1' # Often contains title/caption
                    span_selector = 'div._a9zs > span[dir="auto"]' # Example specific selector
                    
                    caption_el = await page.querySelector(h1_selector)
                    if caption_el:
                        details["caption"] = await page.evaluate('(el) => el.textContent', caption_el)
                        Logger.info(f"      Extracted caption via HTML ({h1_selector}).")
                    else:
                        # Try the more specific selector if H1 fails
                        caption_el = await page.querySelector(span_selector)
                        if caption_el:
                             details["caption"] = await page.evaluate('(el) => el.textContent', caption_el)
                             Logger.info(f"      Extracted caption via HTML ({span_selector}).")
                
                    # Log if caption still not found after HTML attempts
                    if not details["caption"]:
                         Logger.warning(f"    Could not find caption via HTML scraping for {shortcode}.")

                # Scrape Date via HTML (if not found in JSON)
                if not details["date"]:
                    # The <time> tag with a datetime attribute is usually the most reliable.
                    time_selector = 'time[datetime]'
                    time_el = await page.querySelector(time_selector)
                    if time_el:
                        details["date"] = await page.evaluate('(el) => el.getAttribute("datetime")', time_el)
                        Logger.info(f"      Extracted date via HTML ({time_selector}): {details['date']}")
                    else:
                        Logger.warning(f"    Could not find time element via HTML ({time_selector}) for {shortcode}.")
                         
            except Exception as html_err:
                # Catch errors during the HTML scraping attempt.
                Logger.error(f"    Error during HTML scraping for {shortcode}: {html_err}")
        
        # --- Final Validation & Return --- 
        # Check if we have the essential shortcode and at least one piece of metadata.
        if details["shortcode"] and (details["caption"] or details["date"]):
             Logger.info(f"    Successfully gathered details for {details['shortcode']}")
             return details
        else:
             # If even after fallbacks, key data is missing, skip this reel.
             Logger.warning(f"    Failed to scrape sufficient details (caption/date) for {reel_url}. Skipping.")
             return None
             
    except Exception as e:
        # Catch major errors during navigation or overall processing for this reel.
        Logger.error(f"  Major error scraping details page for {reel_url}: {str(e)}")
        # Add screenshotting here for debugging difficult errors.
        try: 
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            # Sanitize shortcode just in case it contains invalid characters for filename
            safe_shortcode = "".join(c for c in shortcode if c.isalnum() or c in ('_', '-')).rstrip()
            ss_path = Path(SCREENSHOTS_DIR) / f'error_reel_{safe_shortcode}_{timestamp}.png'
            await page.screenshot({'path': str(ss_path)}) 
            Logger.info(f"Saved reel detail error screenshot to: {ss_path}")
        except Exception as ss_err:
            Logger.error(f"Failed to save reel detail error screenshot: {ss_err}")
        return None # Return None on major failure

async def scrape_reels(page: Page, username: str) -> List[Dict]:
    """Scrapes all reel URLs from a user's profile page by scrolling,
    then iterates through the URLs to scrape detailed metadata for each.
    """
    reels_data: List[Dict] = [] # Stores the final list of dictionaries
    try:
        # Navigate to the target user's reels tab.
        target_url = f'https://www.instagram.com/{username}/reels/'
        Logger.info(f'Navigating to user reels page: {target_url}')
        await page.goto(target_url, {'waitUntil': 'networkidle0'})
        await asyncio.sleep(SHORT_DELAY_MS / 1000) # Short pause after initial load

        # --- Scroll to Collect All Reel URLs --- 
        reel_urls: set[str] = set() # Use a set to automatically handle duplicates
        last_height = await page.evaluate('document.body.scrollHeight')
        attempts = 0 # Track consecutive scrolls that yield no height change
        max_scroll_attempts = 25 # Increased max scrolls slightly
        scroll_count = 0

        Logger.info(f'Starting scroll loop to find all reel URLs for {username}...')
        while attempts < 3 and scroll_count < max_scroll_attempts:
            # Execute JavaScript in the page context to find all reel links.
            # Looks for <a> tags whose href contains "/reel/"
            new_urls_on_page = await page.evaluate('''() => {
                const links = Array.from(document.querySelectorAll('a[href*="/reel/"]'));
                return links.map(link => link.href);
            }''')
            
            # Add newly found URLs to the set.
            original_count = len(reel_urls)
            reel_urls.update(new_urls_on_page)
            newly_added_count = len(reel_urls) - original_count
            
            Logger.info(f'Scroll {scroll_count+1}/{max_scroll_attempts}: Found {len(new_urls_on_page)} links on screen, added {newly_added_count} new. Total unique URLs: {len(reel_urls)}')

            # Scroll down the page.
            await page.evaluate('window.scrollTo(0, document.body.scrollHeight);')
            # Wait for new content to potentially load after scroll.
            await asyncio.sleep(SHORT_DELAY_MS / 1000 + random.random() * 1.5) # Slightly longer random wait
            scroll_count += 1
            
            # Check if the page height has changed.
            new_height = await page.evaluate('document.body.scrollHeight')
            if new_height == last_height:
                # If height hasn't changed for 3 consecutive scrolls, assume end of content.
                attempts += 1
                Logger.info(f'Scroll height ({new_height}) did not change. Attempt {attempts}/3.')
            else:
                attempts = 0 # Reset counter if height changed
            last_height = new_height
            
        if scroll_count >= max_scroll_attempts:
             Logger.warning(f'Reached max scroll attempts ({max_scroll_attempts}) for {username}. May not have found all reels.')
        
        unique_reel_urls = list(reel_urls)
        Logger.info(f'Finished scrolling phase. Found {len(unique_reel_urls)} unique reel URLs for {username}. Now scraping details...')

        # --- Scrape Details for Each Found URL --- 
        total_urls = len(unique_reel_urls)
        for i, reel_url in enumerate(unique_reel_urls):
            Logger.info(f"---> Processing reel {i+1}/{total_urls} for {username}...")
            # Call the detail scraping function for the current URL.
            details = await scrape_reel_details(page, reel_url)
            if details:
                reels_data.append(details)
            # Crucial delay between visiting individual reel pages to avoid rate limiting.
            await asyncio.sleep(random.uniform(4, 8)) # Increased delay range

        Logger.info(f'Finished scraping details for {username}. Successfully extracted data for {len(reels_data)} out of {total_urls} found reels.')
        return reels_data # Return the list of successfully scraped reel dictionaries
        
    except Exception as e:
        # Catch errors occurring during the process for this specific user.
        Logger.error(f'Error occurred while scraping reels for {username}: {str(e)}')
        try:
            # Try to get page source for context on error (e.g., private account page)
            page_content = await page.content()
            if "This Account is Private" in page_content:
                Logger.warning(f'Account {username} appears to be private.')
            elif "Sorry, this page isn\'t available." in page_content:
                Logger.warning(f'Account {username} page seems unavailable or does not exist.')
            else:
                # Log snippet if unknown error
                Logger.warning(f"Page content snippet on error for {username}: {page_content[:500]}...")
        except Exception as page_err:
             Logger.error(f'Could not get page content for {username} after error: {page_err}')
             
        return [] # Return an empty list if scraping failed for this user 