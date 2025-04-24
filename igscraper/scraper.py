import asyncio
import json
import random
from pyppeteer.page import Page
from typing import List, Dict, Optional

from igscraper.logger import Logger
from igscraper.config import (
    EXPLICIT_WAIT_TIMEOUT_S,
    SHORT_DELAY_MS
)

async def scrape_reel_details(page: Page, reel_url: str) -> Optional[Dict]:
    """Navigates to a single reel URL and extracts detailed information."""
    shortcode = reel_url.split("/reel/")[-1].split("/")[0] 
    Logger.info(f"  Scraping details for reel: {shortcode} ({reel_url})")
    details = {
        "shortcode": shortcode,
        "url": reel_url,
        "is_video": True,
        "type": "Reel",
        "date": None,
        "caption": None
    }
    
    try:
        timeout_ms = EXPLICIT_WAIT_TIMEOUT_S * 1500 # Convert seconds to ms for timeout
        await page.goto(reel_url, {'waitUntil': 'networkidle0', 'timeout': timeout_ms * 1.5}) 
        await asyncio.sleep(random.uniform(2.0, 4.0))

        # --- Method 1: Look for embedded JSON (preferred) --- 
        extracted_from_json = False
        try:
            json_ld_element = await page.querySelector('script[type="application/ld+json"]')
            if json_ld_element:
                Logger.info(f"    Found JSON-LD script tag for {shortcode}.")
                json_ld_content = await page.evaluate('(element) => element.textContent', json_ld_element)
                data = json.loads(json_ld_content)
                
                if isinstance(data, list): data = data[0]

                if isinstance(data, dict) and ("VideoObject" in data.get("@type", "") or "Clip" in data.get("@type", "")):
                    details["caption"] = data.get("caption") or data.get("description") or data.get("name")
                    details["date"] = data.get("uploadDate") or data.get("datePublished")
                    
                    if details["caption"]:
                        Logger.info(f"      Extracted caption via JSON-LD.")
                    else:
                         Logger.warning(f"      Caption not found in JSON-LD.")
                         
                    if details["date"]:
                        Logger.info(f"      Extracted date via JSON-LD: {details['date']}")
                    else:
                        Logger.warning(f"      Date not found in JSON-LD.")
                        
                    extracted_from_json = bool(details["caption"] or details["date"])
                else:
                     Logger.warning(f"    JSON-LD found but type mismatch or not a dictionary: {data.get('@type', 'N/A')}")
            else:
                Logger.info(f"    JSON-LD script tag not found for {shortcode}.")
            
        except Exception as json_err:
            Logger.warning(f"    Error processing JSON-LD for {shortcode}: {json_err}")
            extracted_from_json = False

        # --- Method 2: Fallback to HTML scraping --- 
        if not details["caption"] or not details["date"]:
            Logger.info(f"    Attempting HTML scraping for missing details ({shortcode}).")
            try:
                if not details["caption"]:
                    caption_el = await page.querySelector('h1')
                    if caption_el:
                        details["caption"] = await page.evaluate('(el) => el.textContent', caption_el)
                        Logger.info(f"      Extracted caption via HTML (H1 tag).")
                    
                    if not details["caption"]:
                        caption_el = await page.querySelector('div._a9zs > span[dir="auto"]') # Example selector
                        if caption_el:
                             details["caption"] = await page.evaluate('(el) => el.textContent', caption_el)
                             Logger.info(f"      Extracted caption via HTML (div._a9zs > span).")
                
                    if not details["caption"]:
                         Logger.warning(f"    Could not find caption via HTML scraping for {shortcode}.")

                if not details["date"]:
                    time_el = await page.querySelector('time[datetime]')
                    if time_el:
                        details["date"] = await page.evaluate('(el) => el.getAttribute("datetime")', time_el)
                        Logger.info(f"      Extracted date via HTML (time tag): {details['date']}")
                    else:
                        Logger.warning(f"    Could not find time element via HTML scraping for {shortcode}.")
                         
            except Exception as html_err:
                Logger.error(f"    Error during HTML scraping for {shortcode}: {html_err}")
        
        if details["shortcode"] and (details["caption"] or details["date"]):
             Logger.info(f"    Successfully scraped some details for {details['shortcode']}")
             return details
        else:
             Logger.warning(f"    Failed to scrape sufficient details for {reel_url}. Skipping.")
             return None
             
    except Exception as e:
        Logger.error(f"  Major error scraping details for {reel_url}: {str(e)}")
        return None

async def scrape_reels(page: Page, username: str) -> List[Dict]:
    """Scrape reel URLs from profile and then scrape details for each reel."""
    reels_data: List[Dict] = []
    try:
        target_url = f'https://www.instagram.com/{username}/reels/'
        Logger.info(f'Navigating to reels page: {target_url}')
        await page.goto(target_url, {'waitUntil': 'networkidle0'})
        await asyncio.sleep(SHORT_DELAY_MS / 1000)

        reel_urls: set[str] = set()
        last_height = await page.evaluate('document.body.scrollHeight')
        attempts = 0
        max_scroll_attempts = 10
        scroll_count = 0

        Logger.info(f'Starting scroll loop to find reel URLs for {username}...')
        while attempts < 3 and scroll_count < max_scroll_attempts:
            new_urls_on_page = await page.evaluate('''() => {
                const links = Array.from(document.querySelectorAll('a[href*="/reel/"]'));
                return links.map(link => link.href);
            }''')
            
            newly_added_count = 0
            for url in new_urls_on_page:
                if url not in reel_urls:
                    reel_urls.add(url)
                    newly_added_count += 1
            
            Logger.info(f'Scroll {scroll_count+1}: Found {len(new_urls_on_page)} links, added {newly_added_count} new URLs. Total unique URLs: {len(reel_urls)}')

            await page.evaluate('window.scrollTo(0, document.body.scrollHeight);')
            await asyncio.sleep(SHORT_DELAY_MS / 1000 + random.random())
            scroll_count += 1
            
            new_height = await page.evaluate('document.body.scrollHeight')
            if new_height == last_height:
                attempts += 1
                Logger.info(f'Scroll height did not change. Attempt {attempts}/3.')
            else:
                attempts = 0
            last_height = new_height
            
        if scroll_count >= max_scroll_attempts:
             Logger.warning(f'Reached max scroll attempts ({max_scroll_attempts}) for {username}.')
        
        unique_reel_urls = list(reel_urls)
        Logger.info(f'Finished scrolling. Found {len(unique_reel_urls)} unique reel URLs for {username}. Now scraping details...')

        total_urls = len(unique_reel_urls)
        for i, reel_url in enumerate(unique_reel_urls):
            Logger.info(f"  Processing reel {i+1}/{total_urls}...")
            details = await scrape_reel_details(page, reel_url)
            if details:
                reels_data.append(details)
            await asyncio.sleep(random.uniform(3, 7))

        Logger.info(f'Finished scraping details for {username}. Successfully extracted data for {len(reels_data)} reels.')
        return reels_data
        
    except Exception as e:
        Logger.error(f'Error scraping reels list for {username}: {str(e)}')
        try: # Try to get page content for context, but don't fail if page is gone
            page_content = await page.content()
            if "This Account is Private" in page_content:
                Logger.warning(f'Account {username} is private.')
            elif "Sorry, this page isn\'t available." in page_content:
                Logger.warning(f'Account {username} page not available or does not exist.')
        except Exception as page_err:
             Logger.error(f'Could not get page content for {username} after error: {page_err}')
        return [] 