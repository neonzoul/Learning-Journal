# Debug version of the scraper with simplified approach

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import time
import os

# The directory to store the browser profile, acting like a real user's browser
USER_DATA_DIR = os.path.join(os.getcwd(), "user_data")
search_term = "iphone"

def run(playwright):
    print("Starting browser...")
    
    context = playwright.chromium.launch_persistent_context(
        USER_DATA_DIR,
        headless=False,
        args=['--disable-blink-features=AutomationControlled'],
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        viewport={'width': 1920, 'height': 1080},
    )
    
    page = context.pages[0] if context.pages else context.new_page()
    
    try:
        print("Navigating to homepage...")
        page.goto("https://www.powerbuy.co.th/th", timeout=60000)
        print("OK: Page loaded successfully")
        
        print("Waiting for page to load completely...")
        page.wait_for_load_state("networkidle", timeout=30000)
        print("OK: Network idle state reached")
        
        print("Taking homepage screenshot...")
        page.screenshot(path="debug_homepage.png")
        print("OK: Screenshot saved")
        
        try:
            print("Looking for cookie banner...")
            cookie_button = page.locator("button#btn-accept-cookie")
            if cookie_button.is_visible(timeout=5000):
                cookie_button.click()
                print("OK: Cookie banner accepted")
                time.sleep(1)
            else:
                print("INFO: No cookie banner found")
        except PlaywrightTimeoutError:
            print("INFO: No cookie banner found (timeout)")

        print("Looking for search input...")
        search_selectors = [
            "input[placeholder*='ค้นหา']",
            "input#txt-search-box",
            "input[placeholder*='search']",
            "input[placeholder*='Search']",
            ".search-input input",
            "[data-testid*='search'] input"
        ]
        
        search_element = None
        used_selector = None
        
        for selector in search_selectors:
            safe_selector_str = selector if selector.isascii() else '[non-ascii selector]'
            print(f"  Trying: {safe_selector_str}")
            
            try:
                element = page.locator(selector).first
                if element.is_visible(timeout=3000):
                    search_element = element
                    used_selector = selector
                    print(f"OK: Found search box with selector: {safe_selector_str}")
                    break
            except Exception as e:
                print(f"  ERROR: An error occurred for selector {safe_selector_str}: {e}")
                continue
        
        if not search_element:
            print("FATAL: Could not find search input")
            all_inputs = page.query_selector_all("input")
            print(f"Found {len(all_inputs)} input elements:")
            for i, inp in enumerate(all_inputs[:10]):
                try:
                    inp_id = inp.get_attribute("id") or ""
                    inp_class = inp.get_attribute("class") or ""
                    inp_placeholder = inp.get_attribute("placeholder") or ""
                    inp_type = inp.get_attribute("type") or ""
                    safe_placeholder = inp_placeholder if inp_placeholder.isascii() else '[non-ascii placeholder]'
                    print(f"  {i+1}. id='{inp_id}' class='{inp_class}' placeholder='{safe_placeholder}' type='{inp_type}'")
                except:
                    print(f"  {i+1}. Could not get attributes")
            
            context.close()
            return
        
        print(f"Typing '{search_term}' into search box...")
        search_element.fill(search_term)
        search_element.press("Enter")
        print("OK: Search submitted")
        
        print("Waiting for search results to load...")
        page.wait_for_selector(".product-card-container", timeout=30000)
        print("OK: Product container found!")

        print("Searching for product elements...")
        
        product_selectors = [
            ".product-card-container",
            ".product-card",
            ".product-item",
            "[class*='product']",
            ".search-result-item",
            ".grid-item",
            ".item"
        ]
        
        found_products = False
        product_cards = []

        for selector in product_selectors:
            try:
                elements = page.query_selector_all(selector)
                if len(elements) > 0:
                    print(f"OK: Found {len(elements)} elements with '{selector}'")
                    first_text = elements[0].inner_text()[:100] if elements[0] else ""
                    safe_text = first_text.strip().encode('utf-8', 'replace').decode('utf-8')
                    print(f"  First element text: {safe_text}")
                    
                    if len(elements) >= 2:
                        print(f"OK: Using selector: {selector}")
                        product_cards = elements
                        found_products = True
                        break
                else:
                    print(f"INFO: No elements found with '{selector}'")
            except Exception as e:
                print(f"ERROR with selector '{selector}': {e}")
        
        if found_products:
            print(f"SUCCESS! Found {len(product_cards)} products. Extracting data...")
            for i, card in enumerate(product_cards[:5]): # Limit to first 5 for debug
                try:
                    name_element = card.query_selector(".mat-line.ng-star-inserted, .product-name, .product-title, h3, h4")
                    price_element = card.query_selector(".price-value, .price, .current-price")
                    
                    name = name_element.inner_text().strip() if name_element else "Name not found"
                    price = price_element.inner_text().strip() if price_element else "Price not found"
                    
                    safe_name = name.encode('utf-8', 'replace').decode('utf-8')
                    safe_price = price.encode('utf-8', 'replace').decode('utf-8')

                    print(f"Product {i+1}:")
                    print(f"  Name: {safe_name}")
                    print(f"  Price: {safe_price}")
                    print("-" * 20)

                except Exception as e:
                    print(f"Error extracting data from product {i+1}: {e}")
                    continue
        else:
            print("ERROR: No product elements found even after direct navigation.")
            page_html = page.content()
            with open("debug_search_page.html", "w", encoding="utf-8") as f:
                f.write(page_html)
            print("INFO: Saved page HTML to debug_search_page.html for inspection.")
        
        print("Debug complete!")
        
    except Exception as e:
        safe_error = str(e).encode('utf-8', 'replace').decode('utf-8')
        print(f"FATAL ERROR: {safe_error}")
        print("Taking error screenshot...")
        try:
            page.screenshot(path="debug_error.png")
            print("OK: Error screenshot saved")
        except:
            pass
    
    finally:
        print("Press Enter to close browser...")
        context.close()

if __name__ == "__main__":
    with sync_playwright() as playwright:
        run(playwright)