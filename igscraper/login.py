# igscraper/login.py
# Handles Instagram login, 2FA, and session status checks.

import asyncio
import random
import time # Import time for timestamp
from pathlib import Path # Import Path
from pyppeteer.page import Page

from igscraper.logger import Logger
from igscraper.config import (
    LOGIN_URL,
    INSTAGRAM_BASE_URL,
    SHORT_DELAY_MS,
    EXPLICIT_WAIT_TIMEOUT_S,
    SCREENSHOTS_DIR # Import screenshot dir
)
# Import save_cookies specifically needed for successful login
from igscraper.browser import save_cookies 

async def check_login_status(page: Page) -> bool:
    """Checks if a login session is active by navigating to the base URL
    and looking for indicators of the login page.
    """
    try:
        Logger.info('Checking login status by navigating to Instagram base URL...')
        # Navigate to the main page, wait for network activity to settle.
        await page.goto(INSTAGRAM_BASE_URL, {'waitUntil': 'networkidle0'})
        # Add a small explicit delay just in case networkidle0 fires too early.
        await asyncio.sleep(SHORT_DELAY_MS / 1000)

        # Simple heuristic: If the username input field (characteristic of login page) exists,
        # assume we are NOT logged in.
        login_form_username = await page.querySelector('input[name="username"]')
        if login_form_username:
            Logger.info('Login page username field found. Assuming NOT logged in.')
            return False
        else:
            # If the username field is not found, assume we are logged in.
            # This is a basic check; more robust checks could look for profile icons, feed elements, etc.
            Logger.info('Login page username field NOT found. Assuming logged in.')
            return True
    except Exception as e:
        # If any error occurs during navigation or check (e.g., network error, page crash), 
        # conservatively assume not logged in.
        Logger.error(f'Error during login status check: {str(e)}')
        return False

async def handle_2fa(page: Page) -> bool:
    """Detects and handles the 2-Factor Authentication input prompt."""
    try:
        Logger.info('Checking for 2FA prompt...')
        # Wait briefly to allow the 2FA screen to potentially load after login attempt.
        await asyncio.sleep(SHORT_DELAY_MS / 1000)

        is_2fa_screen = False
        # First, try to quickly find the specific input field for the code.
        # Use a short timeout because if it's there, it should appear relatively fast.
        try:
            await page.waitForSelector('input[name="verificationCode"]', { 'timeout': 3000 })
            Logger.info('Detected 2FA screen via input field [name="verificationCode"].')
            is_2fa_screen = True
        except Exception:
            # If specific input field not found quickly, check page content for 2FA-related text.
            # This is a fallback in case the input field selector changes.
            Logger.info('2FA input field not immediately found, checking page content for keywords...')
            page_content = await page.content()
            security_indicators = [
                'two-factor authentication', '2-factor authentication',
                'verification code', 'security code', 'enter the code'
            ]
            if any(indicator.lower() in page_content.lower() for indicator in security_indicators):
                 Logger.info('Detected 2FA screen via text content.')
                 is_2fa_screen = True

        # If 2FA screen is detected (by either method):
        if is_2fa_screen:
            Logger.info('Requesting 2FA code from user input...')
            try:
                # Prompt the user running the script to enter the code.
                security_code = input('\n>>> INSTAGRAM SECURITY CHECK: Enter the verification code: ')
            except EOFError:
                # Handle cases where script runs non-interactively (e.g., in Docker without tty).
                Logger.error("Cannot get 2FA code from input (EOFError). Login cannot proceed.")
                return False

            # Find the input field again (might use a broader selector)
            input_selector = 'input[name="verificationCode"], input[aria-label*="Security Code" i]'
            input_field = await page.querySelector(input_selector)
            if not input_field:
                 Logger.error(f'Could not find the 2FA input field using selector: {input_selector}')
                 return False
            
            await input_field.type(security_code, { 'delay': random.randint(80, 180) })
            Logger.info('Entered verification code.')

            # Find and click the confirmation button.
            confirm_selector = 'button:has-text("Confirm"), button:has-text("Submit"), button:has-text("Next")'
            confirm_button = await page.querySelector(confirm_selector)
            if not confirm_button:
                 Logger.error(f'Could not find the 2FA confirmation button using selector: {confirm_selector}')
                 return False
                 
            await confirm_button.click()
            Logger.info('Clicked 2FA confirmation button. Waiting for verification...')
            # Wait longer after submitting 2FA code.
            await asyncio.sleep(SHORT_DELAY_MS / 1000 * 2.5)
            # Assume success if code submission didn't immediately error out.
            # Further verification happens in the main login function after navigation.
            return True
        else:
            # If no 2FA indicators were found.
            Logger.info('No 2FA prompt detected.')
            return True # It's not an error if 2FA wasn't required.

    except Exception as e:
        Logger.error(f'Error during 2FA handling: {str(e)}')
        return False

async def login_instagram(page: Page, username: str, password: str) -> bool:
    """Performs the login process on Instagram, including handling 2FA."""
    try:
        Logger.info(f'Navigating to login page: {LOGIN_URL}')
        await page.goto(LOGIN_URL, {'waitUntil': 'networkidle0'})
        # Short delay after page load
        await asyncio.sleep(SHORT_DELAY_MS / 1000)

        Logger.info('Entering login credentials...')
        # Convert timeout from seconds (config) to milliseconds (pyppeteer)
        timeout_ms = EXPLICIT_WAIT_TIMEOUT_S * 1000
        
        # Wait for username field and type username
        await page.waitForSelector('input[name="username"]', { 'timeout': timeout_ms })
        # Add random delay to typing to mimic human behavior
        await page.type('input[name="username"]', username, { 'delay': random.randint(50, 150) })
        await asyncio.sleep(random.uniform(0.5, 1.0))

        # Type password
        await page.type('input[name="password"]', password, { 'delay': random.randint(50, 150) })
        await asyncio.sleep(random.uniform(0.7, 1.2))

        # Find and click login button
        login_button = await page.waitForSelector('button[type="submit"]', { 'timeout': timeout_ms })
        await login_button.click()
        Logger.info('Login button clicked. Waiting...')
        # Wait after click for page to potentially react (redirect, show error, show 2FA)
        await asyncio.sleep(SHORT_DELAY_MS / 1000 * 2)

        # Check for immediate login failure message (before potential 2FA screen)
        error_selector = '#slfErrorAlert, p[data-testid="login-error-message"]' # Combine known error selectors
        error_message = await page.querySelector(error_selector)
        if error_message:
             # Try to get the error text content
             err_text = await page.evaluate('(element) => element.textContent', error_message)
             Logger.error(f'Login failed with immediate error message: {err_text.strip()}')
             return False

        # Proceed to handle 2FA if required
        if not await handle_2fa(page):
            Logger.error('Login failed due to 2FA handling error.')
            return False 

        # --- Verify Login Success --- 
        Logger.info('Checking login status after submission/2FA...')
        try:
            # Wait for navigation to complete after login/2FA actions.
            # Use a longer timeout here as redirects can take time.
            await page.waitForNavigation({'waitUntil': 'networkidle0', 'timeout': timeout_ms * 2})
        except Exception as nav_err:
            # Sometimes navigation doesn't register correctly, or page hangs.
            # Don't fail immediately, check URL and key elements anyway.
             Logger.warning(f'waitForNavigation timed out or failed after login attempt: {nav_err}. Checking URL/elements...')
             await asyncio.sleep(SHORT_DELAY_MS / 1000) # Wait a bit more

        current_url = page.url
        # Check if URL indicates successful login (on main domain, not login/challenge page)
        is_url_ok = 'instagram.com' in current_url and 'login' not in current_url and 'challenge' not in current_url
        
        if is_url_ok:
            Logger.info(f'Login successful based on URL: {current_url}')
            try:
                 # As a final check, look for a common element present only when logged in.
                 # Use a short timeout for this verification step.
                 await page.waitForSelector('svg[aria-label="Home"], a[href*="/direct/inbox/"]', { 'timeout': 5000 })
                 Logger.info('Verified login via presence of Home/Inbox icon.')
                 await save_cookies(page) # Save cookies on successful login
                 return True
            except Exception:
                 # If the element isn't found quickly, but URL looks good, 
                 # warn but assume success (could be a new UI element).
                 Logger.warning('Login URL okay, but key logged-in element not found quickly. Assuming success.')
                 await save_cookies(page)
                 return True
        else:
             # If URL still looks like login/challenge page.
             Logger.error(f'Login failed. Final URL indicates failure: {current_url}')
             # Capture final state for debugging
             try: 
                 timestamp = time.strftime("%Y%m%d_%H%M%S")
                 ss_path = Path(SCREENSHOTS_DIR) / f'login_final_url_fail_{timestamp}.png'
                 await page.screenshot({'path': str(ss_path)}) 
                 Logger.info(f"Saved login failure screenshot to: {ss_path}")
             except Exception as ss_err:
                  Logger.error(f"Failed to save login failure screenshot: {ss_err}")
             return False

    except Exception as e:
        Logger.error(f'Unexpected error during login process: {str(e)}')
        # Capture state on unexpected error
        try: 
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            ss_path = Path(SCREENSHOTS_DIR) / f'login_unexpected_error_{timestamp}.png'
            await page.screenshot({'path': str(ss_path)}) 
            Logger.info(f"Saved login error screenshot to: {ss_path}")
        except Exception as ss_err:
             Logger.error(f"Failed to save login error screenshot: {ss_err}")
        return False 