# Powerbuy iPhone Scraper (Proof of Concept)

This project demonstrates a robust method for scraping product data from modern e-commerce websites like Powerbuy, which heavily rely on dynamic content loading and anti-bot measures (e.g., Cloudflare).

## Project Goal

### Project Purpose: Proof of Concept

This project serves as a proof of concept to demonstrate that we can reliably extract product data from modern, protected e-commerce websites like PowerBuy. The success of this implementation will validate our methodology for handling:

### Dynamic JavaScript-rendered content (prices loaded after page load)

Cloudflare anti-bot protection (browser fingerprinting, challenge pages)
Complex e-commerce architectures (SPAs, internal APIs, session management)

## Scraper Flow & How It Works

Traditional web scraping often involves parsing raw HTML. However, for sites that load data dynamically (e.g., using JavaScript to fetch data after the initial page load), this approach is unreliable. This scraper employs a more advanced and stable method:

1.  **Initial Page Load & Cookie Collection (Playwright):**

    -   The scraper uses `Playwright`, a headless browser automation library, to visit the Powerbuy homepage (`https://www.powerbuy.co.th/th`).
    -   Playwright renders the page fully, executing all JavaScript. This is crucial because it allows the browser to bypass initial anti-bot challenges (like Cloudflare) and collect necessary cookies that are set during this process.
    -   The script then extracts all cookies from the Playwright browser context.

2.  **Simulating Search & Intercepting API Call (Playwright):**

    -   Instead of directly constructing an API URL (which often contains dynamic IDs and requires specific headers/cookies), the scraper simulates a user typing "iphone" into the search bar and pressing Enter.
    -   Crucially, `Playwright` is configured to **intercept network responses**. It listens for a specific API call pattern: `_next/data/[dynamic_id]/th/search/iphone.json`.
    -   When this API call is detected, the scraper captures its full JSON response, which contains the structured product data.

3.  **Data Extraction & Storage (Python):**
    -   Once the JSON response is intercepted, the script parses it.
    -   It navigates through the JSON structure (`pageProps -> productListData -> products`) to access the list of product dictionaries.
    -   For each product, it extracts the `name`, `sku`, and `price`.
    -   Finally, the collected data is written to a CSV file named `test_collect.csv` in the project's root directory, with a header row for clarity.

## Why This Method?

This approach is chosen for its robustness and efficiency when dealing with modern, dynamic websites:

-   **Bypassing Anti-Bot Measures:** Playwright's full browser rendering capability is highly effective at navigating initial anti-bot challenges (like Cloudflare) that often block simpler `requests`-based scrapers.
-   **Reliable Data Source:** Instead of relying on potentially unstable HTML selectors (which can change frequently), this method targets the website's internal API. This API is the exact data source the website itself uses, making it a much more stable and structured way to get information.
-   **Efficiency:** Once the API endpoint is identified and successfully intercepted, subsequent data collection is fast and efficient, as it directly fetches structured JSON rather than parsing complex HTML.
-   **Dynamic Build IDs:** Modern web frameworks (like Next.js, used by Powerbuy) often generate dynamic build IDs in their API URLs. Simulating user interaction and intercepting the API call allows the scraper to automatically discover and use the correct, current build ID, making the scraper resilient to changes in these IDs.

## Usage

1.  Ensure you have Python and Playwright installed.
2.  Run `python scraper.py` from your terminal.
3.  A browser window will open, simulate the search, and then close.
4.  The collected product data will be saved in `test_collect.csv`.

**Note:** This is a proof-of-concept. Websites can change their structure or anti-bot measures, which may require updates to the scraper. Always scrape responsibly and adhere to the website's `robots.txt` and Terms of Service.

## Development Process & AI Collaboration

This project was developed with the assistance of AI tools, primarily **Gemini CLI** and **GitHub Copilot**.

The initial approach involved traditional web scraping methods. However, during the debugging process, it was discovered that the website loads product data dynamically via a JSON file after a search is performed. This insight became the core of the new strategy.

This context and the relevant files were provided to Gemini CLI, which then implemented the final, more robust scraper logic based on intercepting and parsing the JSON data.
