# main.py
# Main entry point for the Instagram Reels Scraper application.

import asyncio
import json
import os
import time
import random
from typing import List, Dict
from pathlib import Path
from pyppeteer.network_manager import Request # Import Request type

# Import necessary components from the igscraper package
from igscraper.logger import Logger
from igscraper.config import (
    INSTAGRAM_USERNAME, # Loaded from .env via config
    INSTAGRAM_PASSWORD, # Loaded from .env via config
    RESULTS_FILENAME,   # Filename for saving results
    SCREENSHOTS_DIR,    # Directory for screenshots
    PROXY_LIST_FILE, # Import proxy file path
    check_credentials   # Utility to validate credentials early
)
from igscraper.browser import (
    setup_browser,      # Function to launch the browser
    load_cookies,       # Function to load session cookies
    try_click_not_now   # Function to handle post-login popups
)
from igscraper.login import (
    check_login_status, # Function to verify if session is active
    login_instagram     # Function to perform the login process
)
from igscraper.scraper import (
    scrape_reels        # Function to scrape reels for a single user
)
from igscraper.proxy_rotator import ProxyRotator # Import the rotator

async def handle_request_interception(request: Request, rotator: ProxyRotator):
    """Intercepts requests and routes them through the next available proxy."""
    # Optimization: Optionally ignore interception for non-essential resources
    # resource_types_to_proxy = {'document', 'script', 'xhr', 'fetch'}
    # if request.resourceType not in resource_types_to_proxy:
    #     await request.continue_()
    #     return

    proxy = rotator.get_next_proxy()
    if proxy:
        try:
            # Logger.debug(f"Routing {request.method} {request.url[:80]}... via {proxy}")
            await request.continue_(proxy={'server': proxy})
        except Exception as e:
            # Log if continuing the request with the proxy fails
            Logger.error(f"Error continuing request for {request.url[:80]} with proxy {proxy}: {e}")
            # Abort the request if the proxy fails catastrophically?
            # Or try without proxy?
            try: 
                await request.abort() # Abort if proxy fails badly
            except Exception:
                 pass # Ignore if abort also fails
    else:
        # If rotation is disabled or no proxies are available, continue normally
        try:
            await request.continue_()
        except Exception as e:
             Logger.error(f"Error continuing request {request.url[:80]} (no proxy): {e}")
             try: 
                await request.abort()
             except Exception:
                 pass # Ignore if abort also fails

async def run_scraper_for_accounts(target_usernames: List[str]) -> Dict[str, List[Dict]]:
    """Initializes the browser, handles login/session, iterates through target
    usernames, orchestrates scraping for each, and handles browser cleanup.
    
    Args:
        target_usernames: A list of Instagram usernames to scrape.
        
    Returns:
        A dictionary where keys are usernames and values are lists of 
        scraped reel data dictionaries.
    """
    browser = None # Initialize browser variable to ensure it's available in finally block
    page = None    # Initialize page variable
    # Use type hint for the results dictionary
    results: Dict[str, List[Dict]] = {}
    rotator = None # Initialize rotator

    try:
        # --- Initialization --- 
        # Create screenshots directory if it doesn't exist
        try:
            screenshots_path = Path(SCREENSHOTS_DIR)
            screenshots_path.mkdir(parents=True, exist_ok=True)
            Logger.info(f"Ensured screenshots directory exists: {screenshots_path.resolve()}")
        except OSError as dir_err:
            Logger.error(f"Could not create screenshots directory '{SCREENSHOTS_DIR}': {dir_err}")
            # Decide if this is fatal? For now, continue but log error.
            
        check_credentials()
        
        # Initialize the proxy rotator
        rotator = ProxyRotator(PROXY_LIST_FILE)
        
        # Launch the Pyppeteer browser instance
        browser = await setup_browser()
        # Open a new page (tab) in the browser
        page = await browser.newPage()
        
        # --- Set up Proxy Rotation via Request Interception --- 
        if rotator and rotator.enabled:
            Logger.info("Enabling request interception for proxy rotation.")
            await page.setRequestInterception(True)
            # Attach the handler using a lambda to pass the rotator instance
            # Use asyncio.ensure_future to handle the async handler correctly
            page.on('request', lambda req: asyncio.ensure_future(handle_request_interception(req, rotator)))
        else:
             Logger.info("Proxy rotation not enabled. Proceeding without request interception.")
             # Ensure interception is off if not using proxies
             await page.setRequestInterception(False)

        # --- Login/Session Handling --- 
        Logger.info('Initiating login/session check...')
        # Attempt to load cookies first (from env var or file)
        session_loaded = await load_cookies(page)
        is_logged_in = False # Flag to track login status
        
        if session_loaded:
            Logger.info('Session cookies were loaded. Verifying if session is active...')
            # If cookies were loaded, check if they represent an active session
            is_logged_in = await check_login_status(page)
            if is_logged_in:
                 Logger.info('✓ Session is active.')
            else:
                 # Cookies might be expired or invalid
                 Logger.info('Loaded session cookies are invalid or expired.')
        else:
            Logger.info('No session cookies found or loaded.')

        # If not logged in (either no cookies or cookies invalid), perform login
        if not is_logged_in:
            Logger.info('Login required. Attempting login...')
            login_successful = await login_instagram(page, INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
            if not login_successful:
                # If login fails, raise a specific error to stop the process.
                # This prevents attempting to scrape without being logged in.
                raise ConnectionError('Login failed. Cannot proceed with scraping.') 
            Logger.info('✓ Login successful.')
            is_logged_in = True # Update flag after successful login
        
        # --- Post-Login Popup Handling --- 
        if is_logged_in:
             Logger.info("Checking for post-login popups (e.g., 'Save Info', 'Notifications')...")
             # Attempt to click "Not Now" for potential popups. 
             # It's safe if they don't appear; the function handles that.
             await try_click_not_now(page)
             await asyncio.sleep(0.5) # Brief pause between checks
             await try_click_not_now(page) # Check again for potential second popup
        else:
             # Safety check: If somehow not logged in after all attempts, abort.
             Logger.error("Critical error: Not logged in after checks/attempts. Aborting scraping.")
             # Return empty results dictionary
             return results 

        # --- Account Iteration & Scraping --- 
        Logger.info("Starting scraping process for target accounts...")
        for target_username in target_usernames:
            Logger.info(f'---> Processing account: {target_username}')
            # Call the main scraping function for the current user
            # Pass the existing, logged-in page object
            reels_list = await scrape_reels(page, target_username) 
            # Store the results (list of reel dicts) in the main results dict
            results[target_username] = reels_list
            Logger.info(f'---> Finished processing for {target_username}. Found {len(reels_list)} reels with details.')
            # Add a polite delay between scraping different accounts
            await asyncio.sleep(random.uniform(2.5, 5.5))

    except Exception as e:
        Logger.error(f'An error occurred during the main scraping process: {str(e)}')
        # Save screenshot on major error
        if page:
            try: 
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                ss_path = Path(SCREENSHOTS_DIR) / f'run_scraper_error_{timestamp}.png'
                await page.screenshot({'path': str(ss_path)}) 
                Logger.info(f"Saved error screenshot to: {ss_path}")
            except Exception as ss_err: 
                Logger.error(f"Failed to save error screenshot: {ss_err}")
    finally:
        # --- Cleanup --- 
        # Ensure the browser is closed regardless of success or failure.
        if browser:
            try:
                Logger.info('Closing browser...')
                await browser.close()
                Logger.info('Browser closed successfully.')
            except Exception as close_err:
                 # Log error if browser closing fails, but don't crash.
                 Logger.error(f'Error closing browser: {close_err}')

    # Return the dictionary containing results for all processed accounts.
    return results

async def main():
    """Main asynchronous function to set up and run the scraper."""
    
    # --- Define Target Usernames --- 
    # TODO: Consider reading target usernames from a file (e.g., target_accounts.txt) 
    # or command-line arguments for more flexibility.
    target_usernames = ['nasa', 'natgeo'] # Example list - EDIT THIS!
    Logger.info(f'Target accounts configured: {target_usernames}')

    # --- Execute Scraping --- 
    start_time = time.time()
    scraped_data = {}
    try:
        # Call the main orchestration function.
        # This handles browser setup, login, iteration, and cleanup.
        scraped_data = await run_scraper_for_accounts(target_usernames)
    except ValueError as cred_err:
        # Catch credential validation errors from check_credentials()
        Logger.error(f"Configuration Error: {cred_err}")
        return # Exit gracefully
    except ConnectionError as login_err:
        # Catch login failures raised from run_scraper_for_accounts
         Logger.error(f"Login Process Error: {login_err}")
         return # Exit gracefully
    except Exception as run_err:
        # Catch any other unexpected errors during the run
        Logger.error(f"An unexpected error occurred during the scraping run: {run_err}")
        # Ensure scraped_data is an empty dict so saving logic doesn't fail
        scraped_data = {} 
        
    end_time = time.time()
    
    # --- Save Results --- 
    # Only attempt to save if scraped_data is not empty (i.e., scraping started)
    if scraped_data:
        Logger.info("Attempting to save scraped data...")
        try:
            # Write the results dictionary to a JSON file.
            # indent=2 makes the output file human-readable.
            with open(RESULTS_FILENAME, 'w') as f:
                json.dump(scraped_data, f, indent=2)
            Logger.info(f'✓ Results successfully saved to {RESULTS_FILENAME}')
        except Exception as e:
             Logger.error(f'Failed to save results to {RESULTS_FILENAME}: {str(e)}')
    else:
         Logger.warning("No data was successfully scraped or an early error occurred. Results file not written.")

    Logger.info(f'Total execution time: {end_time - start_time:.2f} seconds')
    Logger.info("Script finished.")

# --- Script Entry Point --- 
if __name__ == '__main__':
    # This block executes when the script is run directly (python3 main.py).
    
    # Workaround for potential asyncio issues on Windows.
    if os.name == 'nt': # Check if the OS is Windows
        try:
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        except Exception as policy_err:
             # This is not critical, just log a warning if it fails.
             print(f"[WARNING] Could not set Windows event loop policy: {policy_err}")
    
    try:
        # Start the asyncio event loop and run the main asynchronous function.
        # asyncio.run() is the preferred way to run the top-level async function.
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        # Handle graceful shutdown if the user interrupts (Ctrl+C).
        print("\n[INFO] Script interrupted by user. Exiting.")
    except Exception as e:
         # Catch any unexpected errors that weren't handled deeper in the call stack.
         print(f"\n[FATAL ERROR] An unhandled exception occurred in main execution: {str(e)}")
         # For debugging, consider uncommenting the traceback print:
         # import traceback
         # print(traceback.format_exc()) 