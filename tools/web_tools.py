import requests
import socket 
from bs4 import BeautifulSoup
from typing import Optional, List, Any, Dict 
from crewai.tools import tool
from playwright.sync_api import sync_playwright, Page, Browser, Playwright, Error as PlaywrightError, TimeoutError as PlaywrightTimeoutError

# --- WebScrapingLogic und scrape_website_content_tool (bleiben unverändert) ---
class WebScrapingLogic:
    def scrape_content(self, url: str) -> tuple[str | None, str | None]:
        print(f"--- Debug (scrape_content): Attempting to scrape URL: {url} ---")
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9,de;q=0.8',
            }
            response = requests.get(url, headers=headers, timeout=20)
            response.raise_for_status() 

            soup = BeautifulSoup(response.content, 'html.parser')

            for script_or_style in soup(["script", "style", "nav", "footer", "aside", "header"]):
                if script_or_style:
                    script_or_style.decompose()

            body = soup.find('body')
            if body:
                text = body.get_text(separator='\n', strip=True)
                text_lines = [line for line in text.splitlines() if line.strip()]
                clean_text = "\n".join(text_lines)
                
                if not clean_text.strip():
                    print(f"--- Debug (scrape_content): No text after cleaning for URL: {url} ---")
                    return None, f"TOOL_ERROR: Could not extract meaningful text content from the page (after cleaning): {url}"

                max_raw_text_chars = 15000 
                if len(clean_text) > max_raw_text_chars:
                    clean_text = clean_text[:max_raw_text_chars] + "\n... (Content truncated as it was too long)"
                print(f"--- Debug (scrape_content): Scraping successful for URL: {url}, text length (possibly truncated): {len(clean_text)} ---")
                return clean_text, None
            else:
                print(f"--- Debug (scrape_content): Could not find body tag for URL: {url} ---")
                return None, f"TOOL_ERROR: Could not find body tag in the page: {url}"

        except requests.exceptions.Timeout:
            print(f"--- Debug (scrape_content): Timeout while fetching URL: {url} ---")
            return None, f"TOOL_ERROR: Timeout while fetching URL '{url}'."
        except requests.exceptions.HTTPError as http_err:
            print(f"--- Debug (scrape_content): HTTP error for URL {url}: {http_err} ---")
            return None, f"TOOL_ERROR: HTTP error {http_err.response.status_code} while fetching URL '{url}'."
        except requests.exceptions.RequestException as e:
            print(f"--- Debug (scrape_content): General request error for URL {url}: {e} ---")
            return None, f"TOOL_ERROR: Error fetching URL '{url}': {e}"
        except Exception as e:
            print(f"--- Debug (scrape_content): Unknown error while scraping URL {url}: {e} ---")
            return None, f"TOOL_ERROR: General error while scraping '{url}': {e}"

_web_ops_logic = WebScrapingLogic()

@tool("Scrape Website Content Tool")
def scrape_website_content_tool(url: str) -> str:
    """Scrapes main text content from a URL. Args: url (str)."""
    print(f"--- Debug (Tool Call): 'Scrape Website Content Tool' called with URL: {url} ---")
    scraped_text, error = _web_ops_logic.scrape_content(url)
    if error: 
        print(f"--- Debug: Error during scraping of {url}: {error} ---")
        return error 
    if not scraped_text or not scraped_text.strip(): 
        error_msg = f"TOOL_INFO: Could not extract meaningful text content from URL or content was empty: {url}"
        print(f"--- Debug: {error_msg} ---")
        return error_msg 
    print(f"--- Debug: Scraping for {url} successful. Returning raw text (length: {len(scraped_text)}). Agent should summarize this. ---")
    return scraped_text

# --- Playwright Browser Tool (Incorporating Claude's successful fixes) ---

_playwright_instance: Optional[Playwright] = None
_browser_instance: Optional[Browser] = None
_current_page: Optional[Page] = None

def _ensure_browser_is_running(headless_mode: bool = True) -> bool: 
    """Ensures Playwright is initialized and a browser is launched."""
    global _playwright_instance, _browser_instance, _current_page
    
    if _browser_instance and _browser_instance.is_connected():
        if not _current_page or _current_page.is_closed():
            try:
                _current_page = _browser_instance.new_page()
                print("--- Debug (Playwright): New page created in existing browser. ---")
            except Exception as e:
                print(f"--- Debug (Playwright): Error creating new page: {e}. Restarting browser. ---")
                # KORRIGIERTE SYNTAX für try-except in if-Block
                if _browser_instance:
                    try: 
                        _browser_instance.close()
                    except Exception as e_close_browser:
                        print(f"--- Debug (Playwright): Minor error closing browser during restart: {e_close_browser} ---")
                if _playwright_instance:
                    try: 
                        _playwright_instance.stop()
                    except Exception as e_stop_pw:
                        print(f"--- Debug (Playwright): Minor error stopping playwright during restart: {e_stop_pw} ---")
                _browser_instance, _playwright_instance, _current_page = None, None, None
                return _ensure_browser_is_running(headless_mode) # Recursive call
        return True

    try:
        print(f"--- Debug (Playwright): Initializing Playwright and launching browser (headless={headless_mode})... ---")
        _playwright_instance = sync_playwright().start()
        _browser_instance = _playwright_instance.chromium.launch(headless=headless_mode) 
        _current_page = _browser_instance.new_page()
        print(f"--- Debug (Playwright): Browser launched (Chromium, headless={headless_mode}) and new page created. ---")
        return True
    except Exception as e:
        print(f"--- Debug (Playwright): CRITICAL - Failed to initialize Playwright or launch browser: {e} ---")
        if _browser_instance: 
            try: _browser_instance.close() 
            except: pass
        if _playwright_instance: 
            try: _playwright_instance.stop()
            except: pass
        _playwright_instance, _browser_instance, _current_page = None, None, None
        return False

@tool("Navigate Browser Tool")
def navigate_browser_tool(url: str) -> str:
    """
    Navigates the browser to the specified URL.
    Launches a browser and creates a page if one isn't already active.
    Args:
        url (str): The URL to navigate to.
    """
    global _current_page
    print(f"--- Debug (Tool Call): 'Navigate Browser Tool' called with URL: {url} ---")
    if not _ensure_browser_is_running(headless_mode=True) or not _current_page:
        return "TOOL_ERROR (Playwright): Browser or page could not be initialized."
    try:
        print(f"--- Debug (Playwright): Navigating to {url}...")
        response = _current_page.goto(url, timeout=30000, wait_until="load") 
        if response and response.ok:
            title = _current_page.title()
            print(f"--- Debug (Playwright): Navigation to {url} successful. Page title: '{title}'. Current URL: {_current_page.url} ---")
            return f"Successfully navigated to {url}. Page title: '{title}'"
        else:
            status = response.status if response else "Unknown"
            print(f"--- Debug (Playwright): Navigation to {url} failed. Status: {status} ---")
            return f"TOOL_ERROR (Playwright): Failed to navigate to {url}. Status: {status}"
    except PlaywrightTimeoutError as te:
        return f"TOOL_ERROR (Playwright): Timeout error during navigation to {url}: {str(te)}"
    except PlaywrightError as e:
        return f"TOOL_ERROR (Playwright): Navigation error for {url}: {e.message if hasattr(e, 'message') else str(e)}"
    except Exception as e:
        return f"TOOL_ERROR (Playwright): Unexpected error during navigation to {url}: {e}"

@tool("Click Element Tool")
def click_element_tool(selector: str, expected_navigation_url_pattern: Optional[str] = None) -> str:
    """
    Clicks on an element specified by a CSS selector or text content.
    If navigation is expected, waits for the URL to match a pattern or for page load.
    Args:
        selector (str): CSS selector (e.g., 'a.my-link') or text selector (e.g., 'text=More information...', 'role=link,name=More information...').
        expected_navigation_url_pattern (Optional[str]): Glob pattern for the expected URL after click (e.g., "**/iana.org/**").
    """
    global _current_page
    print(f"--- Debug (Tool Call): 'Click Element Tool' called with selector: '{selector}', expected URL pattern: '{expected_navigation_url_pattern}' ---")
    if not _current_page or _current_page.is_closed():
        return "TOOL_ERROR (Playwright): No active page to click on. Please navigate first."
    try:
        element_to_click = None
        if selector.startswith("text="):
            text_content = selector.split("=", 1)[1]
            print(f"--- Debug (Playwright): Attempting to click by text: '{text_content}' ---")
            element_to_click = _current_page.get_by_text(text_content, exact=True).first
        elif selector.startswith("role=link,name="):
            name_content = selector.split("name=", 1)[1]
            print(f"--- Debug (Playwright): Attempting to click by role=link, name: '{name_content}' ---")
            element_to_click = _current_page.get_by_role("link", name=name_content).first
        else:
            print(f"--- Debug (Playwright): Attempting to click by CSS selector: '{selector}' ---")
            element_to_click = _current_page.locator(selector).first
        
        if not element_to_click or not element_to_click.is_visible(timeout=5000):
             return f"TOOL_ERROR (Playwright): Element with selector '{selector}' not found or not visible."

        print(f"--- Debug (Playwright): Element found. Clicking on '{selector}'... ---")
        
        element_to_click.click(timeout=10000) 
        
        if expected_navigation_url_pattern:
            print(f"--- Debug (Playwright): Waiting for URL pattern: '{expected_navigation_url_pattern}' ---")
            _current_page.wait_for_url(f"**{expected_navigation_url_pattern}**", timeout=15000)
        else:
            print(f"--- Debug (Playwright): Waiting for load state 'domcontentloaded'... ---")
            _current_page.wait_for_load_state("domcontentloaded", timeout=15000) 
            
        current_url_prop = _current_page.url 
        print(f"--- Debug (Playwright): Click successful. Current page URL: {current_url_prop} ---")
        return f"Successfully clicked on element matching selector '{selector}'. Current page URL: {current_url_prop}"
    except PlaywrightTimeoutError as te:
        return f"TOOL_ERROR (Playwright): Timeout error clicking or waiting after click on '{selector}': {str(te)}"
    except PlaywrightError as e:
        return f"TOOL_ERROR (Playwright): Error clicking element '{selector}': {e.message if hasattr(e, 'message') else str(e)}"
    except Exception as e:
        return f"TOOL_ERROR (Playwright): Unexpected error clicking element '{selector}': {e}"

@tool("Get Page Content Tool")
def get_page_content_tool(selector: Optional[str] = "h1") -> str:
    """
    Retrieves text content of the first element matching the CSS selector.
    Waits for the element to be visible.
    Args:
        selector (Optional[str]): CSS selector (e.g., 'h1'). Defaults to 'h1'.
    """
    global _current_page
    print(f"--- Debug (Tool Call): 'Get Page Content Tool' called with selector: {selector} ---")
    if not _current_page or _current_page.is_closed():
        return "TOOL_ERROR (Playwright): No active page. Navigate first."
    
    actual_selector = selector if selector else "h1"
    try:
        print(f"--- Debug (Playwright): Waiting for selector '{actual_selector}' to be visible... ---")
        _current_page.wait_for_selector(actual_selector, state="visible", timeout=10000)
        
        js_script = f"""() => {{
            const el = document.querySelector('{actual_selector.replace("'", "\\'")}');
            return el ? el.textContent : null;
        }}"""
        print(f"--- Debug (Playwright): Evaluating JS for selector '{actual_selector}' ---")
        content = _current_page.evaluate(js_script)

        if content is not None:
            print(f"--- Debug (Playwright): Content for '{actual_selector}' (via JS): '{str(content).strip()}' ---")
            return str(content).strip()
        else:
            print(f"--- Debug (Playwright): JS evaluation returned null for '{actual_selector}', trying locator... ---")
            element = _current_page.locator(actual_selector).first
            if element.count() > 0: 
                content = element.text_content(timeout=5000)
                if content is not None:
                    print(f"--- Debug (Playwright): Content for '{actual_selector}' (via locator): '{str(content).strip()}' ---")
                    return str(content).strip()
        
        print(f"--- Debug (Playwright): No text content found for selector '{actual_selector}'. ---")
        return f"TOOL_INFO (Playwright): No text content found for selector '{actual_selector}'."

    except PlaywrightTimeoutError as te:
        return f"TOOL_ERROR (Playwright): Timeout waiting for element with selector '{actual_selector}': {str(te)}"
    except PlaywrightError as e:
        return f"TOOL_ERROR (Playwright): Error getting content for selector '{actual_selector}': {e.message if hasattr(e, 'message') else str(e)}"
    except Exception as e:
        return f"TOOL_ERROR (Playwright): Unexpected error getting content for selector '{actual_selector}': {e}"

@tool("Type Text Tool")
def type_text_tool(selector: str, text_to_type: str, press_enter: bool = False) -> str:
    """
    Types the given text into an element specified by a CSS selector.
    Optionally presses Enter after typing.
    Args:
        selector (str): The CSS selector of the input element.
        text_to_type (str): The text to type into the element.
        press_enter (bool): Whether to press Enter after typing. Defaults to False.
    """
    global _current_page
    print(f"--- Debug (Tool Call): 'Type Text Tool' called for selector: {selector}, text: '{text_to_type}' ---")
    if not _current_page or _current_page.is_closed():
        return "TOOL_ERROR (Playwright): No active page to type on. Please navigate first."
    try:
        element = _current_page.locator(selector)
        element.fill(text_to_type, timeout=10000) 
        if press_enter:
            element.press("Enter")
        return f"Successfully typed text into element with selector '{selector}'."
    except PlaywrightError as e:
        return f"TOOL_ERROR (Playwright): Error typing into element '{selector}': {e.message if hasattr(e, 'message') else str(e)}"
    except Exception as e:
        return f"TOOL_ERROR (Playwright): Unexpected error typing into element '{selector}': {e}"

@tool("Close Browser Tool")
def close_browser_tool() -> str:
    """
    Closes the Playwright browser instance if it is running.
    This should be called at the end of all browser interactions to free up resources.
    """
    global _playwright_instance, _browser_instance, _current_page
    print("--- Debug (Tool Call): 'Close Browser Tool' called. ---")
    closed_something = False
    if _browser_instance:
        try:
            _browser_instance.close()
            print("--- Debug (Playwright): Browser instance closed. ---")
            closed_something = True
        except Exception as e:
            print(f"--- Debug (Playwright): Error closing browser instance: {e} ---")
        _browser_instance = None
        _current_page = None 

    if _playwright_instance:
        try:
            _playwright_instance.stop()
            print("--- Debug (Playwright): Playwright instance stopped. ---")
            closed_something = True
        except Exception as e:
            print(f"--- Debug (Playwright): Error stopping Playwright instance: {e} ---")
        _playwright_instance = None
        
    return "Playwright browser session closed successfully." if closed_something else "Playwright browser was not running or already closed."

