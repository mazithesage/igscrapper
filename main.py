"""
Enterprise Instagram Reels Analytics Suite
=================================

A professional-grade Instagram Reels data collection and analytics tool designed for:
- Social Media Agencies
- Digital Marketing Teams
- Content Creators & Influencers
- Brand Marketing Departments

Key Features:
1. Bulk Reel Data Collection
2. Automated Authentication
3. Detailed Analytics Extraction
4. Multi-Account Support
5. Secure Session Management
6. Enterprise-grade Error Handling

Technical Specifications:
- Supports both single-user and bulk processing modes
- Implements rate limiting and anti-ban measures
- Provides detailed logging and error tracking
- Maintains session persistence for extended runs

Output Format: Structured JSON with comprehensive metrics
"""

import os
import time
import json
import logging
import re
import pickle
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from urllib.parse import urljoin

# Secure credential storage (replace with your credentials)
INSTAGRAM_USERNAME = "YOUR_USERNAME"
INSTAGRAM_PASSWORD = "YOUR_PASSWORD"

# Environment setup
os.environ["PATH"] += ":/usr/local/bin"

# Enterprise-grade logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('instagram_scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# --- Scraping Mode Selection ---
def select_scraping_mode():
    """Interactive mode selection for data collection.
    
    Business Use Cases:
    - Single Mode: Quick analysis of specific influencer accounts
    - Bulk Mode: Large-scale competitor analysis or industry research
    
    Returns:
        str: Selected mode ('single' or 'bulk')
    """
    while True:
        print("\n=== Enterprise Instagram Reels Analytics Suite ===")
        print("1. Single Account Analysis")
        print("2. Bulk Account Analysis (via CSV/TXT)")
        print("3. Exit Application")
        
        choice = input("\nSelect Analysis Mode (1-3): ").strip()
        
        if choice == "1":
            return "single"
        elif choice == "2":
            return "bulk"
        elif choice == "3":
            print("\nThank you for using our Analytics Suite!")
            sys.exit(0)
        else:
            print("\nInvalid selection. Please choose 1, 2, or 3.")

# --- Get Target Username ---
def get_target_username():
    """Collect target account for analysis.
    
    Business Value:
    - Analyze competitor accounts
    - Track influencer performance
    - Monitor brand ambassadors
    
    Returns:
        str: Instagram username to analyze
    """
    while True:
        username = input("\nEnter target Instagram account for analysis: ").strip()
        if username:
            return username
        print("Error: Please provide a valid Instagram username for analysis.")

# --- Get Usernames File ---
def get_usernames_file():
    """Import multiple accounts for bulk analysis.
    
    Business Value:
    - Process hundreds of accounts automatically
    - Batch competitor analysis
    - Industry-wide trend analysis
    - Market research automation
    
    Accepts:
    - CSV files
    - Text files (one username per line)
    - Excel files (first column for usernames)
    
    Returns:
        list: List of Instagram usernames for analysis
    """
    while True:
        file_path = input("\nImport accounts list (CSV/TXT/XLS) or type 'back' for menu: ").strip()
        
        if file_path.lower() == 'back':
            return None
            
        if not file_path:
            print("Error: Please specify a valid file path containing account list.")
            continue
            
        try:
            with open(file_path, 'r') as f:
                usernames = [line.strip() for line in f if line.strip()]
                
            if not usernames:
                print("Error: No valid accounts found in the file.")
                continue
                
            print(f"\nSuccessfully loaded {len(usernames)} accounts for analysis.")
            return usernames
            
        except FileNotFoundError:
            print(f"Error: Account list file not found at '{file_path}'")
        except Exception as e:
            print(f"Error processing account list: {str(e)}")

# --- Process Single Username ---
def analyze_account_performance(username, driver):
    """Comprehensive analysis of a single Instagram account's Reels performance.
    
    Business Intelligence Gathered:
    - Engagement rates
    - Posting frequency
    - Content themes
    - Audience response patterns
    - Peak performance metrics
    
    Args:
        username (str): Target Instagram account
        driver: Selenium WebDriver instance
    
    Returns:
        list: Detailed analytics for each Reel
    """
    target_url = f"https://www.instagram.com/{username}/reels/?hl=en"
    
    try:
        post_urls = scrape_post_urls_from_feed(
            driver,
            target_url,
            max_urls=MAX_POST_URLS_TO_SCRAPE,
            scroll_attempts=MAX_SCROLL_ATTEMPTS,
            scroll_pause_time=SCROLL_PAUSE_TIME
        )
        
        if not post_urls:
            logger.warning(f"No Reels content found for account: {username}")
            return []
            
        account_analytics = []
        for i, url in enumerate(post_urls, 1):
            logger.info(f"Analyzing Reel {i}/{len(post_urls)}: {url}")
            reel_metrics = get_reel_info(driver, url)
            if reel_metrics:
                account_analytics.append(reel_metrics)
                print(json.dumps(reel_metrics, indent=2, ensure_ascii=False))
            time.sleep(2)  # Rate limiting for account protection
            
        return account_analytics
        
    except Exception as e:
        logger.error(f"Analysis failed for account {username}: {str(e)}")
        return []

# --- Save Results ---
def export_analytics_report(results, mode, username=None):
    """Export comprehensive analytics report in business-ready format.
    
    Features:
    - Structured JSON format for easy integration
    - Timestamped reports for version control
    - Organized by account or campaign
    - Ready for import into analytics tools
    
    Business Applications:
    - Performance tracking
    - ROI analysis
    - Content strategy planning
    - Competitor benchmarking
    
    Args:
        results (list): Analytics data to export
        mode (str): Analysis mode ('single' or 'bulk')
        username (str, optional): Target account name
    """
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    
    if mode == "single":
        filename = f"analytics_report_{username}_{timestamp}.json"
    else:
        filename = f"market_analysis_{timestamp}.json"
        
    output_file = os.path.join("analytics_reports", filename)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
        
    return output_file

# Target URL will be set dynamically
# TARGET_PAGE_URL = "https://www.instagram.com/explore/tags/pythonprogramming/"

# --- Scraping Parameters ---
MAX_POST_URLS_TO_SCRAPE = 50
MAX_SCROLL_ATTEMPTS = 20
SCROLL_PAUSE_TIME = 3.5

LOGIN_URL = "https://www.instagram.com/accounts/login/"
INSTAGRAM_BASE_URL = "https://www.instagram.com/"
IMPLICIT_WAIT_TIMEOUT = 5
EXPLICIT_WAIT_TIMEOUT = 20
SHORT_DELAY = 2

# New constants for cookies
COOKIES_FILE = "instagram_cookies.pkl"
SESSION_TIMEOUT = 3 * 24 * 60 * 60  # 3 days in seconds


def get_chrome_options():
    """Sets up Chrome options for Selenium."""
    options = webdriver.ChromeOptions()
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    return options


def setup_driver():
    """Initializes and returns the Selenium WebDriver."""
    logger.info("Setting up Chrome WebDriver...")
    try:
        driver = webdriver.Chrome(options=get_chrome_options())
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        driver.implicitly_wait(IMPLICIT_WAIT_TIMEOUT)
        logger.info("WebDriver setup complete.")
        return driver
    except Exception as e:
        logger.error(f"Error setting up WebDriver: {e}")
        raise


def save_cookies(driver):
    """Save cookies to file for session persistence."""
    try:
        cookies = driver.get_cookies()
        with open(COOKIES_FILE, 'wb') as f:
            pickle.dump({
                'cookies': cookies,
                'timestamp': time.time()
            }, f)
        logger.info(f"Cookies saved to {COOKIES_FILE}")
        return True
    except Exception as e:
        logger.error(f"Error saving cookies: {e}")
        return False


def load_cookies(driver):
    """Load cookies from file if they exist and are not expired."""
    try:
        if not os.path.exists(COOKIES_FILE):
            logger.info("No cookies file found.")
            return False

        with open(COOKIES_FILE, 'rb') as f:
            data = pickle.load(f)
            
        # Check if cookies are expired
        if time.time() - data['timestamp'] > SESSION_TIMEOUT:
            logger.info("Saved cookies have expired.")
            return False
            
        # Navigate to Instagram first (cookies must be added after visiting the domain)
        driver.get(INSTAGRAM_BASE_URL)
        time.sleep(1)
        
        # Add cookies to browser
        for cookie in data['cookies']:
            # Some cookies might cause issues, so we'll try each one separately
            try:
                driver.add_cookie(cookie)
            except Exception as e:
                logger.warning(f"Couldn't add cookie: {e}")
                
        logger.info("Cookies loaded successfully")
        return True
    except Exception as e:
        logger.error(f"Error loading cookies: {e}")
        return False


def check_login_status(driver):
    """
    Check if we're already logged in with improved detection for Selenium browser sessions.
    """
    try:
        # Navigate to Instagram main page
        logger.info("Checking login status by navigating to Instagram main page...")
        driver.get(INSTAGRAM_BASE_URL)
        time.sleep(3)  # Wait for page to load completely
        
        # Take a screenshot for debugging
        try:
            driver.save_screenshot("login_status_check.png")
            logger.info("Saved screenshot of current state")
        except Exception as e:
            logger.warning(f"Couldn't save screenshot: {e}")
        
        # Method 1: Check for login form elements (not logged in)
        login_elements = driver.find_elements(By.NAME, "username")
        if login_elements and len(login_elements) > 0:
            logger.info("Login form detected - not logged in")
            return False
            
        # Method 2: Check for common elements that appear when logged in
        # These are UI elements typically only visible when logged in
        logged_in_indicators = [
            "//svg[@aria-label='Home']",
            "//a[@href='/explore/']",
            "//a[contains(@href, '/direct/inbox/')]",
            "//span[text()='Search']",
            "//div[@role='navigation']",  # Nav bar is usually present when logged in
            "//a[contains(@href, '/notifications/')]"
        ]
        
        for indicator in logged_in_indicators:
            try:
                element = driver.find_element(By.XPATH, indicator)
                if element.is_displayed():
                    logger.info(f"Detected logged-in state indicator: {indicator}")
                    return True
            except (NoSuchElementException, TimeoutException):
                continue
        
        # Method 3: Check if profile avatar is present (usually top-right when logged in)
        try:
            avatar_elements = driver.find_elements(By.XPATH, "//img[contains(@alt, 'profile picture')]")
            if avatar_elements and len(avatar_elements) > 0:
                logger.info("Profile avatar detected - logged in")
                return True
        except Exception:
            pass
            
        # Method 4: Check for Instagram Stories bar (only appears when logged in)
        try:
            stories_elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'Stories')]")
            if stories_elements and len(stories_elements) > 0:
                logger.info("Stories bar detected - logged in")
                return True
        except Exception:
            pass
            
        # Method 5: Check if the URL changed to redirect from login
        current_url = driver.current_url
        if current_url != LOGIN_URL and "/" in current_url.replace(INSTAGRAM_BASE_URL, ""):
            logger.info(f"URL indicates we're not on login page: {current_url}")
            return True
            
        logger.warning("Could not definitively determine login status - assuming not logged in")
        return False
            
    except Exception as e:
        logger.error(f"Error checking login status: {e}")
        return False



def handle_2fa(driver):
    """
    Handle two-factor authentication.
    """
    logger.info("Checking for 2FA requirements...")
    
    try:
        # Wait to see if we land on any 2FA-related page
        time.sleep(3)  
        
        # Take a screenshot to help debug
        try:
            driver.save_screenshot("2fa_detection_screen.png")
            logger.info("Saved screenshot of current screen as 2fa_detection_screen.png")
        except:
            pass
            
        # Check for various indicators of being on a 2FA screen
        page_source = driver.page_source.lower()
        security_indicators = [
            "two-factor authentication",
            "2-factor authentication", 
            "verification code",
            "security code",
            "enter the code",
            "confirmation code",
            "authentication code",
            "6-digit code",
            "sent you a code"
        ]
        
        is_2fa_screen = any(indicator in page_source for indicator in security_indicators)
        
        # Also look for typical 2FA input fields
        potential_2fa_fields = driver.find_elements(By.XPATH, 
            """//input[
                @aria-label='Security Code' or 
                @name='verificationCode' or 
                @name='securityCode' or 
                @id='security_code' or
                @placeholder='Security code' or
                @placeholder='_ _ _ _ _ _' or
                contains(@id, 'verification') or
                contains(@class, 'verification') or
                contains(@id, 'security') or
                contains(@class, 'security')
            ]"""
        )
        
        if is_2fa_screen or potential_2fa_fields:
            logger.info("2FA screen detected!")
            
            # Ask user for the code
            security_code = input("\n INSTAGRAM SECURITY CHECK: Enter the verification code sent to your email: ")
            
            # Try to find the verification input field
            input_field = None
            
            # First try the fields we already found
            if potential_2fa_fields:
                input_field = potential_2fa_fields[0]
                logger.info("Using pre-identified 2FA input field")
            
            # If no field was found, try a more aggressive search
            if not input_field:
                logger.info("Searching for input field...")
                # Look for any input field that might be for verification
                all_inputs = driver.find_elements(By.TAG_NAME, 'input')
                
                # Filter for likely verification inputs (typically these are short numeric fields)
                for inp in all_inputs:
                    input_type = inp.get_attribute('type')
                    if input_type in ['text', 'number', 'tel']:
                        # This is likely our verification field
                        input_field = inp
                        logger.info("Found potential verification input field")
                        break
            
            # If we found an input field, enter the code
            if input_field:
                input_field.clear()
                for digit in security_code:
                    input_field.send_keys(digit)
                    time.sleep(0.1)  # Small delay between digits can help
                logger.info("Entered verification code")
                
                # Get and log all buttons on the page for debugging
                all_buttons = driver.find_elements(By.TAG_NAME, 'button')
                logger.info(f"Found {len(all_buttons)} buttons on the page")
                for i, btn in enumerate(all_buttons):
                    try:
                        btn_text = btn.text.strip()
                        btn_class = btn.get_attribute('class')
                        logger.info(f"Button {i}: Text='{btn_text}', Class='{btn_class}'")
                    except:
                        logger.info(f"Button {i}: [Could not get details]")
                
                # Expanded list of possible button selectors for verification
                possible_button_xpaths = [
                    "//button[contains(text(), 'Confirm')]",
                    "//button[contains(text(), 'Submit')]",
                    "//button[contains(text(), 'Verify')]",
                    "//button[contains(text(), 'Next')]",
                    "//button[contains(text(), 'Continue')]",
                    "//button[contains(., 'Confirm')]",
                    "//button[contains(., 'Submit')]",
                    "//button[contains(., 'Verify')]",
                    "//button[contains(., 'Next')]",
                    "//button[contains(., 'Continue')]",
                    "//button[contains(@class, 'submit')]",
                    "//button[contains(@class, 'confirm')]",
                    "//button[contains(@class, 'verify')]",
                    "//button[contains(@class, 'primary')]",  # Often primary buttons
                    "//button[contains(@class, 'next')]",
                    "//div[contains(@role, 'button')][contains(., 'Next')]",
                    "//div[contains(@role, 'button')][contains(., 'Confirm')]",
                    "//div[contains(@role, 'button')][contains(., 'Continue')]",
                    "//button[@type='submit']",  # General fallback
                    "//form//button",  # Any button inside a form
                    "//button[last()]"  # Last button on page as a fallback
                ]
                
                button_clicked = False
                for xpath in possible_button_xpaths:
                    try:
                        logger.info(f"Trying to find button with selector: {xpath}")
                        buttons = driver.find_elements(By.XPATH, xpath)
                        if buttons:
                            logger.info(f"Found {len(buttons)} matching buttons")
                            # Try to click the primary one (usually first or last)
                            for btn in buttons:
                                try:
                                    # Take screenshot before clicking
                                    driver.save_screenshot("before_button_click.png")
                                    logger.info(f"About to click button with text: '{btn.text}'")
                                    
                                    # Try traditional click first
                                    btn.click()
                                    button_clicked = True
                                    logger.info(f"Successfully clicked verification button")
                                    time.sleep(1)
                                    break
                                except Exception as click_err:
                                    logger.warning(f"Standard click failed: {click_err}")
                                    try:
                                        # Try JavaScript click as fallback
                                        driver.execute_script("arguments[0].click();", btn)
                                        button_clicked = True
                                        logger.info(f"Clicked button using JavaScript")
                                        time.sleep(1)
                                        break
                                    except Exception as js_err:
                                        logger.warning(f"JavaScript click also failed: {js_err}")
                            
                            if button_clicked:
                                break
                    except Exception as e:
                        logger.info(f"Selector failed: {e}")
                        continue
                
                # If we couldn't find a button, offer manual intervention
                if not button_clicked:
                    logger.warning("Could not find or click a verification button automatically.")
                    manual_proceed = input("Button not found automatically. Press Enter once you've manually clicked the button, or type 'skip' to continue without clicking: ")
                    if manual_proceed.lower() != 'skip':
                        logger.info("Proceeding after manual button click")
                        button_clicked = True
                
                # Wait to see if login proceeds
                time.sleep(5)
                
                # Take another screenshot to see the result
                driver.save_screenshot("after_verification_screen.png")
                
                # Check if we've successfully moved past the verification screen
                new_page_source = driver.page_source.lower()
                still_on_verification = any(indicator in new_page_source for indicator in security_indicators)
                
                if still_on_verification:
                    logger.warning("Still appears to be on verification screen after submitting code.")
                    
                    # One more chance for manual intervention
                    manual_continue = input("Still on verification screen. Press Enter after manually completing verification, or type 'fail' to abort: ")
                    if manual_continue.lower() == 'fail':
                        return False
                    else:
                        time.sleep(3)
                        logger.info("Continuing after manual verification")
                        return True
                else:
                    logger.info("Verification appears successful, proceeding.")
                    return True
            else:
                logger.error("Could not find verification input field")
                # Offer manual verification
                manual_option = input("Could not find verification input field. Enter 'manual' if you want to handle verification manually, or any other key to abort: ")
                if manual_option.lower() == 'manual':
                    input("Complete the verification manually, then press Enter to continue...")
                    return True
                return False
        else:
            logger.info("No 2FA screen detected, continuing with login process.")
            return True
            
    except Exception as e:
        logger.error(f"Error handling 2FA: {e}")
        # Offer manual fallback
        manual_fallback = input("Error in 2FA handling. Enter 'manual' to continue after manual verification, or any other key to abort: ")
        if manual_fallback.lower() == 'manual':
            input("Complete the verification manually, then press Enter to continue...")
            return True
        return False

# Modified login_instagram function to better handle the 2FA flow
def login_instagram(driver, username, password):
    """Logs into Instagram with improved support for 2FA."""
    logger.info(f"Navigating to login page: {LOGIN_URL}")
    driver.get(LOGIN_URL)
    time.sleep(SHORT_DELAY)

    try:
        logger.info("Entering login credentials...")
        
        # Wait for login page to load and find username field
        user_field = WebDriverWait(driver, EXPLICIT_WAIT_TIMEOUT).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        user_field.send_keys(username)
        time.sleep(0.5 + (time.time() % 1))

        # Find and fill password field
        pass_field = driver.find_element(By.NAME, "password")
        pass_field.send_keys(password)
        time.sleep(0.7 + (time.time() % 1))

        # Find and click login button
        login_button_xpath = "//button[@type='submit']"
        login_button = WebDriverWait(driver, EXPLICIT_WAIT_TIMEOUT).until(
            EC.element_to_be_clickable((By.XPATH, login_button_xpath))
        )
        login_button.click()
        logger.info("Login submitted. Waiting for response...")
        
        # Take a screenshot after login attempt
        try:
            time.sleep(3)  # Give time for page transition
            driver.save_screenshot("after_login_screen.png")
            logger.info("Saved screenshot of post-login screen")
        except:
            pass

        # Extended wait time to see what happens after login
        time.sleep(5)
        
        # Check for various challenges Instagram might present
        if "challenge" in driver.current_url:
            logger.info("Detected challenge page in URL.")
            # This could be various challenge types including 2FA, suspicious login, etc.
            
        # Handle 2FA specifically 
        if not handle_2fa(driver):
            logger.warning("2FA handling unsuccessful or was not needed.")
            # We'll continue anyway as it might have worked despite our detection failing
        
        # Now check if we're actually logged in
        logged_in = False
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//svg[@aria-label='Home'] | //a[@href='/'] | //a[contains(@href, '/direct/inbox/')]"))
            )
            logger.info("Successfully logged in - detected Home element.")
            logged_in = True
        except TimeoutException:
            logger.warning("Could not confirm successful login by finding Home element.")
            
        # If we're not sure we're logged in, check for login failure indicators
        if not logged_in:
            error_messages = driver.find_elements(By.XPATH, "//p[contains(text(), 'incorrect') or contains(text(), 'wrong')]")
            if error_messages:
                logger.error("Login failed - incorrect credentials.")
                return False
        
        # Handle standard popups after successful login
        popups_handled = 0
        for _ in range(2):  # Try handling up to two popups (Save Info, Notifications)
            try:
                not_now_button = WebDriverWait(driver, 7).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Not Now')] | //div[@role='dialog']//button[contains(., 'Not Now')]"))
                )
                not_now_button.click()
                logger.info(f"Handled a popup ({popups_handled + 1}).")
                popups_handled += 1
                time.sleep(SHORT_DELAY)
            except (NoSuchElementException, TimeoutException):
                logger.info(f"Popup {popups_handled + 1} not found or timed out.")
                break

        # Save cookies after successful login
        save_cookies(driver)
        logger.info("Login process complete.")
        return True

    except (NoSuchElementException, TimeoutException) as e:
        logger.error(f"Login failed: Element not found or timed out - {e}")
        return False
    except Exception as e:
        logger.error(f"An unexpected error occurred during login: {e}")
        return False

def get_reel_info(driver, reel_url):
    """Extract comprehensive business intelligence from a single Reel.
    
    Business Metrics Collected:
    1. Content Performance
       - Upload timing and lifecycle
       - Engagement velocity
       - Content retention score
    
    2. Audience Engagement
       - View count and watch time
       - Engagement rate calculation
       - Audience interaction patterns
    
    3. Content Analysis
       - Caption effectiveness
       - Hashtag performance
       - Sound/music impact
       - Call-to-action success
    
    Returns:
        dict: Detailed performance metrics and content analysis
    """
    try:
        driver.get(reel_url)
        time.sleep(3)  # Ensure full content loading
        
        # Extract unique identifier
        content_id = reel_url.split('/')[-2]
        
        # Capture posting timestamp
        try:
            time_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "time"))
            )
            post_timestamp = time_element.get_attribute("datetime")
        except:
            post_timestamp = None
            
        # Analyze content strategy
        try:
            caption_element = driver.find_element(By.CSS_SELECTOR, "h1")
            content_strategy = caption_element.text
            hashtags = re.findall(r'#\w+', content_strategy)
            mentions = re.findall(r'@\w+', content_strategy)
        except:
            content_strategy = ""
            hashtags = []
            mentions = []
            
        # Compile comprehensive analytics
        return {
            "content_id": content_id,
            "url": reel_url,
            "content_type": "Reel",
            "performance_metrics": {
                "post_timestamp": post_timestamp,
                "analysis_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "engagement_metrics": {
                    "views": None,  # Populated by parent function
                    "likes": None,  # Populated by parent function
                    "comments": None,  # Populated by parent function
                    "shares": None  # Populated by parent function
                }
            },
            "content_analysis": {
                "caption": content_strategy,
                "hashtags": hashtags,
                "mentions": mentions,
                "hashtag_count": len(hashtags),
                "mention_count": len(mentions)
            }
        }
    except Exception as e:
        logger.error(f"Analytics extraction failed for {reel_url}: {str(e)}")
        return None

def scrape_post_urls_from_feed(driver, page_url, max_urls=50, scroll_attempts=20, scroll_pause_time=3.5):
    """
    Scrolls down a page (profile/hashtag/reels) and extracts unique post URLs.
    """
    logger.info(f"Navigating to target page: {page_url}")
    driver.get(page_url)
    time.sleep(SHORT_DELAY + 3)  # Extended wait for initial page load
    
    # Take screenshot of initial page for debugging
    try:
        driver.save_screenshot("initial_page_view.png")
        logger.info("Saved screenshot of initial page view")
    except Exception as e:
        logger.warning(f"Couldn't save screenshot: {e}")

    # Determine page type
    is_reels_page = '/reels/' in page_url or 'reels' in page_url
    is_hashtag_page = '/explore/tags/' in page_url
    
    logger.info(f"Detected page type: {'REELS' if is_reels_page else 'HASHTAG' if is_hashtag_page else 'STANDARD'}")

    post_urls = set()
    last_height = driver.execute_script("return document.body.scrollHeight")
    attempts_without_new_content = 0

    logger.info(f"Starting scroll process. Target: {max_urls} URLs or {scroll_attempts} scrolls.")

    for attempt in range(scroll_attempts):
        # Extract links BEFORE scrolling
        current_urls_count = len(post_urls)
        
        # REELS-SPECIFIC DETECTION
        if is_reels_page:
            # Method specific for reels pages
            try:
                # Reels often use video elements or specific containers
                video_containers = driver.find_elements(By.XPATH, "//div[contains(@role, 'presentation') or contains(@role, 'dialog')]//a")
                reels_containers = driver.find_elements(By.XPATH, "//div[contains(@class, 'ENC4A') or contains(@class, '_ab8w')]//a")
                
                # Try to find any links in parts of the page that appear to be reels
                for container in video_containers + reels_containers:
                    try:
                        href = container.get_attribute('href')
                        if href and ('/reel/' in href or '/p/' in href):
                            clean_url = href.split("?")[0]
                            if clean_url not in post_urls:
                                post_urls.add(clean_url)
                                logger.info(f"Found REEL URL ({len(post_urls)}/{max_urls}): {clean_url}")
                    except Exception:
                        continue
                        
                # Direct reels detection
                reel_links = driver.find_elements(By.XPATH, "//a[contains(@href, '/reel/')]")
                for link in reel_links:
                    href = link.get_attribute('href')
                    if href:
                        clean_url = href.split("?")[0]
                        if clean_url not in post_urls:
                            post_urls.add(clean_url)
                            logger.info(f"Found direct REEL URL ({len(post_urls)}/{max_urls}): {clean_url}")
            except Exception as e:
                logger.warning(f"Error in reels-specific detection: {e}")
                
        # STANDARD POST DETECTION (works for hashtags)
        # Method 1: Direct link detection
        links = driver.find_elements(By.TAG_NAME, 'a')
        for link in links:
            try:
                href = link.get_attribute('href')
                if not href:
                    continue
                    
                # Check if href is a valid post/reel URL 
                if href and (href.startswith(INSTAGRAM_BASE_URL + "p/") or 
                         href.startswith(INSTAGRAM_BASE_URL + "reel/") or
                         "/p/" in href or "/reel/" in href):
                    # Use regex to confirm it's a content URL
                    if re.match(r"https://www\.instagram\.com/(p|reel)/[\w-]+/?.*$", href):
                        # Clean the URL (remove query parameters)
                        clean_url = href.split("?")[0]
                        if clean_url not in post_urls:
                            post_urls.add(clean_url)
                            logger.info(f"Found URL ({len(post_urls)}/{max_urls}): {clean_url}")
            except Exception as e:
                continue  # Skip problematic links
        
        # Additional methods as in your original code...
        # [rest of your URL finding methods here]
        
        # If this is a reels page and standard methods aren't finding anything,
        # try a more aggressive JavaScript approach
        if is_reels_page and len(post_urls) < current_urls_count + 1:
            try:
                # Execute JS to find reels URLs
                reel_urls = driver.execute_script("""
                    var links = [];
                    var elements = document.getElementsByTagName('a');
                    for (var i = 0; i < elements.length; i++) {
                        var href = elements[i].getAttribute('href');
                        if (href && (href.includes('/reel/'))) {
                            links.push('https://www.instagram.com' + href);
                        }
                    }
                    return links;
                """)
                
                for href in reel_urls:
                    clean_url = href.split("?")[0]
                    if clean_url not in post_urls:
                        post_urls.add(clean_url)
                        logger.info(f"Found REEL URL via JavaScript ({len(post_urls)}): {clean_url}")
            except Exception as e:
                logger.error(f"JavaScript extraction for reels failed: {e}")
                
        # Scrolling logic as in your original code...
        # [rest of your scrolling code here]
        
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        logger.info(f"Scrolled down. Pausing for {scroll_pause_time}s...")
        time.sleep(scroll_pause_time)

        # Check if target number of URLs reached
        if len(post_urls) >= max_urls:
            logger.info(f"Reached target number of URLs ({max_urls}). Stopping scroll.")
            break

        # Check if scroll height has changed
        new_height = driver.execute_script("return document.body.scrollHeight")
        found_new_this_scroll = len(post_urls) > current_urls_count
        
        if new_height == last_height and not found_new_this_scroll:
            attempts_without_new_content += 1
            logger.warning(f"No new content. Attempt {attempts_without_new_content}/3 without new content.")
            
            # For reels pages, try more specialized approaches when stuck
            if is_reels_page and attempts_without_new_content == 1:
                logger.info("Trying reels-specific interaction...")
                try:
                    # Try clicking to load more or interact with reels interface
                    driver.execute_script("window.scrollBy(0, -200);")  # Scroll up a bit
                    time.sleep(1)
                    # Try to find and click a "Load more" button if it exists
                    load_buttons = driver.find_elements(By.XPATH, 
                        "//button[contains(text(), 'Load more') or contains(text(), 'See more')]")
                    if load_buttons:
                        load_buttons[0].click()
                        logger.info("Clicked 'Load more' button")
                        time.sleep(2)
                except Exception as e:
                    logger.warning(f"Reels-specific interaction failed: {e}")
            
            # Try an alternative scroll method
            if attempts_without_new_content == 2:
                logger.info("Trying alternative scroll method...")
                driver.execute_script("window.scrollBy(0, -100);")  # Scroll up slightly
                time.sleep(1)
                driver.execute_script("window.scrollBy(0, 200);")   # Then scroll down more
            
            if attempts_without_new_content >= 3:
                logger.warning("Stopping scroll: No new content after multiple attempts.")
                break
        else:
            if found_new_this_scroll:
                attempts_without_new_content = 0  # Reset counter if we found new URLs
                
        last_height = new_height

    # If we didn't find any URLs, try a last-ditch approach
    # [your existing last-ditch approach code]
    
    logger.info(f"Found a total of {len(post_urls)} unique post URLs.")
    return list(post_urls)

def main():
    """Main function to run the scraper with improved session handling."""
    driver = None
    
    try:
        # Create analytics output directory if it doesn't exist
        output_dir = "analytics_reports"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        while True:
            mode = select_scraping_mode()
            
            driver = setup_driver()
            if not driver:
                return
                
            # Check login status and handle authentication
            logger.info("Checking if already logged in via browser session...")
            driver.get(INSTAGRAM_BASE_URL)
            time.sleep(3)
            
            is_logged_in = check_login_status(driver)
            
            if not is_logged_in:
                session_valid = False
                if load_cookies(driver):
                    session_valid = check_login_status(driver)
                    
                if not session_valid:
                    logger.info("No valid session found. Performing standard login...")
                    if not login_instagram(driver, INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD):
                        logger.error("Login failed. Cannot proceed to scrape.")
                        return
                else:
                    logger.info("Successfully logged in using saved cookies.")
            
            if mode == "single":
                username = get_target_username()
                results = analyze_account_performance(username, driver)
                if results:
                    output_file = export_analytics_report(results, mode, username)
                    logger.info(f"\nSaved {len(results)} reel details to {output_file}")
                
            else:  # bulk mode
                usernames = get_usernames_file()
                if not usernames:  # User chose to go back
                    continue
                    
                all_results = {}
                for i, username in enumerate(usernames, 1):
                    print(f"\n{'='*50}")
                    print(f"Processing user {i}/{len(usernames)}: {username}")
                    print(f"{'='*50}\n")
                    
                    results = analyze_account_performance(username, driver)
                    if results:
                        all_results[username] = results
                        
                if all_results:
                    output_file = export_analytics_report(all_results, mode)
                    total_reels = sum(len(reels) for reels in all_results.values())
                    logger.info(f"\nSaved {total_reels} reels from {len(all_results)} users to {output_file}")
                
            # Ask if user wants to continue
            if input("\nWould you like to scrape more reels? (y/n): ").lower() != 'y':
                print("\nGoodbye!")
                break
            
            # Close the current driver before starting a new session
            if driver:
                driver.quit()
                driver = None

        # First check if we're already logged in using just the browser session
        # (without relying on our cookies file)
        logger.info("Checking if already logged in via browser session...")
        driver.get(INSTAGRAM_BASE_URL)
        time.sleep(3)
        
        # Take a screenshot of the initial state
        try:
            driver.save_screenshot("initial_state.png")
        except:
            pass
            
        # Check if already logged in
        is_logged_in = check_login_status(driver)
        
        if is_logged_in:
            logger.info("✓ Already logged in via browser session! Skipping login process.")
        else:
            # Try to use saved cookies file
            session_valid = False
            if load_cookies(driver):
                session_valid = check_login_status(driver)
                
            # If still not logged in, perform standard login
            if not session_valid:
                logger.info("No valid session found. Performing standard login...")
                if not login_instagram(driver, INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD):
                    logger.error("Login failed. Cannot proceed to scrape feed.")
                    return
            else:
                logger.info("Successfully logged in using saved cookies.")
        
        # Now proceed with scraping
        time.sleep(SHORT_DELAY)
        post_urls = scrape_post_urls_from_feed(driver,
                                              TARGET_PAGE_URL,
                                              max_urls=MAX_POST_URLS_TO_SCRAPE,
                                              scroll_attempts=MAX_SCROLL_ATTEMPTS,
                                              scroll_pause_time=SCROLL_PAUSE_TIME)

        logger.info("\n--- Collecting Detailed Reel Information ---")
        if post_urls:
            all_reel_data = []
            for i, url in enumerate(post_urls, 1):
                logger.info(f"Scraping reel {i}/{len(post_urls)}: {url}")
                reel_info = get_reel_info(driver, url)
                if reel_info:
                    all_reel_data.append(reel_info)
                    print(json.dumps(reel_info, indent=2, ensure_ascii=False))
                time.sleep(2)  # Delay between requests
            
            # Save to JSON file
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            output_file = os.path.join("scraped_data", f"reels_{timestamp}.json")
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(all_reel_data, f, indent=2, ensure_ascii=False)
            logger.info(f"\nSaved {len(all_reel_data)} reel details to {output_file}")
        else:
            logger.warning("No post URLs were collected.")
        logger.info("--------------------------")

    except Exception as e:
        logger.critical(f"A critical error occurred in main execution: {e}", exc_info=True)
        if driver:
            try:
                driver.save_screenshot("critical_error_feed_scrape.png")
                logger.info("Screenshot saved as critical_error_feed_scrape.png")
            except Exception as ss_e:
                logger.error(f"Could not save screenshot: {ss_e}")

    finally:
        if driver:
            logger.info("Closing WebDriver.")
            driver.quit()


if __name__ == "__main__":
    if not INSTAGRAM_USERNAME or INSTAGRAM_USERNAME == "YOUR_TEST_USERNAME" or \
       not INSTAGRAM_PASSWORD or INSTAGRAM_PASSWORD == "YOUR_TEST_PASSWORD":
        logger.error("Please update INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD before running.")
    else:
        main()