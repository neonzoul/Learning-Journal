#  gemini2.5pro

# ````
# to scraping modern e-commerce site like Powerbuy which loads product data dynamically. 
# the easiest and most reliable mothod is to fine the internal API is uses rather than parsing the raw HTML.
# This appoach gives a clean, structured JSON data directly, which is much simpler to work with.
# ````

# !! Ethical Scraping Cisclaimer
# first, for Scrape responsibly by sending requests at a reasonable rate to avoid overloading their servers. 
# | always check the website's robits.txt file e.g. https://www.powerbuy.co.th/robots.txt |

# How It Works
"""
Instead of rendering the whole page, we'll use Python's 'requests' library to call the same API endpoint
the website's frontend uses to fetch product listings. We can find this endpoint using your browser's
Developer Tools.
"""

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import time
import os
import json
import re
import csv

# The directory to store the browser profile, acting like a real user's browser
USER_DATA_DIR = os.path.join(os.getcwd(), "user_data")
search_term = "iphone"

def safe_print(text):
    with open("scraper_debug.log", "a", encoding="utf-8") as f:
        f.write(text + "\n")

def run(playwright):
    safe_print("Starting browser...")
    
    # Option 1: Persistent context (current - keeps user_data)
    context = playwright.chromium.launch_persistent_context(
        USER_DATA_DIR,
        headless=False,
        args=['--disable-blink-features=AutomationControlled'],
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        viewport={'width': 1920, 'height': 1080},
    )
    
    # Option 2: Temporary context (uncomment to use - no user_data folder)
    # browser = playwright.chromium.launch(
    #     headless=False,
    #     args=['--disable-blink-features=AutomationControlled']
    # )
    # context = browser.new_context(
    #     user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    #     viewport={'width': 1920, 'height': 1080}
    # )
    
    page = context.pages[0] if context.pages else context.new_page()
    
    product_data_found = []

    def handle_response(response):
        if re.search(r'/_next/data/[a-zA-Z0-9_-]+/th/search/iphone.json', response.url):
            try:
                data = response.json()
                products = data.get('pageProps', {}).get('productListData', {}).get('products', [])
                if products:
                    product_data_found.extend(products)
                    safe_print(f"Intercepted product data from: {response.url}")
            except json.JSONDecodeError:
                safe_print(f"Could not decode JSON from: {response.url}")
            except Exception as e:
                safe_print(f"Error processing intercepted response from {response.url}: {e}")

    page.on("response", handle_response)

    try:
        safe_print("Navigating to homepage...")
        page.goto("https://www.powerbuy.co.th/th", timeout=60000)
        
        safe_print("Waiting for page to load completely...")
        page.wait_for_load_state("networkidle", timeout=30000)
        time.sleep(2)
        
        try:
            safe_print("Looking for cookie banner on homepage...")
            page.locator("button#btn-accept-cookie").click(timeout=10000)
            safe_print("Cookie banner accepted.")
            time.sleep(1)
        except PlaywrightTimeoutError:
            safe_print("Cookie banner not found or already accepted.")

        safe_print(f"Searching for search input element...")
        
        search_selectors = [
            "input[placeholder*='ค้นหา']", 
            "input#txt-search-box",
            "input[placeholder*='search']",
            "input[placeholder*='Search']",
            "[data-testid*='search']",
            ".search-input",
            "input[type='search']",
            "input[name*='search']",
            "input.search-box"
        ]
        
        search_element = None
        used_selector = None
        
        for selector in search_selectors:
            try:
                safe_print(f"Trying selector: {selector}")
                search_element = page.locator(selector).first
                if search_element.is_visible(timeout=5000):
                    used_selector = selector
                    safe_print(f"Found search element with selector: {selector}")
                    break
            except:
                continue
        
        if not search_element or not used_selector:
            raise Exception("Search input element not found with any known selector")

        safe_print(f"Typing '{search_term}' into the search bar using selector: {used_selector}")
        search_element.fill(search_term)
        search_element.press("Enter")
        
        safe_print("Waiting for URL to change to search results page...")
        page.wait_for_url(f"https://www.powerbuy.co.th/search/{search_term}", timeout=60000)
        safe_print(f"Navigated to: {page.url}")

        safe_print("Waiting for network to be idle after search...")
        page.wait_for_load_state("networkidle", timeout=30000)
        time.sleep(5) 

        if product_data_found:
            safe_print(f"\nSUCCESS! Found {len(product_data_found)} products via API interception. Saving to CSV...\n")
            
            output_file_path = os.path.join(os.getcwd(), "test_collect.csv")
            with open(output_file_path, "w", encoding="utf-8", newline='') as csvfile:
                fieldnames = ['Name', 'SKU', 'Price']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                writer.writeheader()
                for product in product_data_found:
                    name = product.get('name', 'N/A')
                    sku = product.get('sku', 'N/A')
                    price = product.get('price', 'N/A')
                    writer.writerow({'Name': name, 'SKU': sku, 'Price': price})
            safe_print(f"Successfully collected {len(product_data_found)} product details to {output_file_path}")

        else:
            safe_print("No product data intercepted. The search might not have returned results or the API endpoint changed.")
            safe_print(f"Final URL: {page.url}")
            safe_print(f"Page title: {page.title()}")
            page.screenshot(path="debug_no_api_data.png")
            safe_print("Screenshot saved as debug_no_api_data.png")

    except PlaywrightTimeoutError as e:
        safe_print(f"\n--- TIMEOUT ERROR --- Details: {e}")

    except Exception as e:
        safe_print(f"\nAn unexpected error occurred: {e}")

    finally:
        safe_print("\nScript finished. Press Enter in this terminal to close the browser.")
        context.close()

with sync_playwright() as playwright:
    run(playwright)