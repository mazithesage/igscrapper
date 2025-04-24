import asyncio
import random
from pyppeteer.page import Page

from igscraper.logger import Logger
from igscraper.config import (
    LOGIN_URL,
    INSTAGRAM_BASE_URL,
    SHORT_DELAY_MS,
    EXPLICIT_WAIT_TIMEOUT_S
)
from igscraper.browser import save_cookies # Import save_cookies

async def check_login_status(page: Page) -> bool:
    """Check if the user is currently logged in by navigating to base URL."""
    try:
        Logger.info('Checking login status...')
        await page.goto(INSTAGRAM_BASE_URL, {'waitUntil': 'networkidle0'})
        await asyncio.sleep(SHORT_DELAY_MS / 1000)

        # Simple check: Look for username input field of the login page
        login_form_username = await page.querySelector('input[name="username"]')
        if login_form_username:
            Logger.info('Login form detected - assuming not logged in.')
            return False
        else:
            Logger.info('Login form not detected - assuming logged in.')
            return True
    except Exception as e:
        Logger.error(f'Error checking login status: {str(e)}')
        return False

async def handle_2fa(page: Page) -> bool:
    """Handle two-factor authentication if required."""
    try:
        Logger.info('Checking for 2FA requirements...')
        await asyncio.sleep(SHORT_DELAY_MS / 1000)

        is_2fa_screen = False
        try:
            # Prioritize checking for the input field
            await page.waitForSelector('input[name="verificationCode"]', timeout=3000)
            Logger.info('Detected 2FA input field [name="verificationCode"]')
            is_2fa_screen = True
        except Exception:
            page_content = await page.content()
            security_indicators = [
                'two-factor authentication', '2-factor authentication',
                'verification code', 'security code', 'enter the code'
            ]
            if any(indicator.lower() in page_content.lower() for indicator in security_indicators):
                 Logger.info('Detected 2FA text indicator on page.')
                 is_2fa_screen = True

        if is_2fa_screen:
            Logger.info('2FA screen detected!')
            try:
                security_code = input('\nINSTAGRAM SECURITY CHECK: Enter the verification code: ')
            except EOFError: # Handle case where input is not available (e.g., non-interactive env)
                Logger.error("Could not get 2FA code from input. Login cannot proceed.")
                return False

            input_field = await page.querySelector('input[name="verificationCode"], input[aria-label*="Security Code" i]')
            if not input_field:
                 Logger.error('Could not find the 2FA input field.')
                 return False
            
            await input_field.type(security_code)
            Logger.info('Entered verification code')

            confirm_button = await page.querySelector('button:has-text("Confirm"), button:has-text("Submit"), button:has-text("Next")')
            if not confirm_button:
                 Logger.error('Could not find the 2FA confirmation button.')
                 return False
                 
            await confirm_button.click()
            Logger.info('Clicked 2FA confirmation button')
            await asyncio.sleep(SHORT_DELAY_MS / 1000 * 2) 
            return True
        else:
            Logger.info('No 2FA screen detected.')
            return True

    except Exception as e:
        Logger.error(f'Error handling 2FA: {str(e)}')
        return False

async def login_instagram(page: Page, username: str, password: str) -> bool:
    """Log in to Instagram with the provided credentials."""
    try:
        Logger.info(f'Navigating to login page: {LOGIN_URL}')
        await page.goto(LOGIN_URL, {'waitUntil': 'networkidle0'})
        await asyncio.sleep(SHORT_DELAY_MS / 1000)

        Logger.info('Entering login credentials...')
        timeout_ms = EXPLICIT_WAIT_TIMEOUT_S * 1000
        
        await page.waitForSelector('input[name="username"]', { 'timeout': timeout_ms })
        await page.type('input[name="username"]', username, { 'delay': random.randint(50, 150) })
        await asyncio.sleep(0.5 + random.random())

        await page.type('input[name="password"]', password, { 'delay': random.randint(50, 150) })
        await asyncio.sleep(0.7 + random.random())

        login_button = await page.waitForSelector('button[type="submit"]', { 'timeout': timeout_ms })
        await login_button.click()
        Logger.info('Login button clicked. Waiting for navigation or 2FA...')
        await asyncio.sleep(SHORT_DELAY_MS / 1000 * 2)

        error_message = await page.querySelector('#slfErrorAlert')
        if error_message:
             err_text = await page.evaluate('(element) => element.textContent', error_message)
             Logger.error(f'Login failed immediately: {err_text}')
             return False

        if not await handle_2fa(page):
            Logger.error('2FA handling failed.')
            return False 

        # Slightly longer wait for navigation/redirect after potential 2FA
        await page.waitForNavigation({'waitUntil': 'networkidle0', 'timeout': timeout_ms * 2})
        current_url = page.url
        
        if 'instagram.com' in current_url and 'login' not in current_url and 'challenge' not in current_url:
            Logger.info('Login appears successful based on URL.')
            try:
                 # Check for a common logged-in element
                 await page.waitForSelector('svg[aria-label="Home"], a[href*="/direct/inbox/"]', timeout=5000)
                 Logger.info('Verified login via Home/Inbox icon.')
                 await save_cookies(page)
                 return True
            except Exception:
                 Logger.warning('Login URL seems okay, but Home/Inbox icon not found quickly. Assuming success.')
                 await save_cookies(page)
                 return True
        else:
             Logger.error(f'Login failed. Current URL after attempts: {current_url}')
             return False

    except Exception as e:
        Logger.error(f'Error during login process: {str(e)}')
        # Maybe take screenshot on login failure?
        # try: await page.screenshot({'path': 'login_error.png'})
        # except: pass
        return False 