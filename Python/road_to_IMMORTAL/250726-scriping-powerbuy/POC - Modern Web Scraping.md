# POC - Project BKK Gadget Hub (Thai e-commerce store)

**Date:** July 26, 2025

---

## 📋 Project Overview

### Project Purpose: Proof of Concept

This project serves as a **proof of concept** to demonstrate that we can reliably extract product data from modern, protected e-commerce websites like PowerBuy. The success of this implementation will validate our methodology for handling:

-   **Dynamic JavaScript-rendered content** (prices loaded after page load)
-   **Cloudflare anti-bot protection** (browser fingerprinting, challenge pages)
-   **Complex e-commerce architectures** (SPAs, internal APIs, session management)

### Success Validation Criteria

The proof of concept will be considered successful when we can:

1. **Consistently extract** all 4 data fields from 50 target product pages
2. **Bypass protection measures** without manual intervention
3. **Deliver clean, structured data** in CSV format ready for business use
4. **Maintain >95% success rate** across multiple test runs
5. **Complete extraction** within reasonable time limits (<5 minutes total)

### Strategic Value

Success in this project establishes our capability to handle **Tier 2 complexity websites** - those with moderate protection and dynamic content. This positions us for similar e-commerce scraping projects and validates our technical approach for future complex scraping challenges.

### Data Requirements

-   **Product Name** - Full product title
-   **Price (THB)** - Current selling price in Thai Baht
-   **Stock Status** - Availability (In Stock/Out of Stock)
-   **SKU/Product Code** - Unique product identifier

---

## 🎯 Why Traditional Scraping Fails

### Challenge 1: Dynamic Content Loading

```
❌ Problem: Price data loads via JavaScript AFTER initial page load
❌ Impact: Standard HTTP requests only get empty price containers
❌ Example: <span id="price">Loading...</span> → Later becomes actual price
```

### Challenge 2: Cloudflare Protection

```
❌ Bot Detection: Cloudflare analyzes request patterns, headers, timing
❌ Browser Fingerprinting: Checks for automation signatures
❌ Challenge Pages: CAPTCHA-like verification screens
❌ Rate Limiting: Aggressive blocking of rapid requests
```

### Challenge 3: Modern E-commerce Architecture

```
❌ Single Page Applications (SPA): Content rendered client-side
❌ API Endpoints: Data fetched from internal APIs with dynamic URLs
❌ Session Management: Requires cookies and proper session handling
❌ Action-Triggered APIs: JSON endpoints only appear after user interactions
```

### Challenge 4: Action-Dependent Data Loading

```
❌ Problem: Direct URL access doesn't trigger API calls
❌ Example: https://www.powerbuy.co.th/th/search/samsung?fill=1-0%7C2-0
   - Direct access: No samsung.json?fill=2-0&keyword=samsung in Network tab
   - Requires: User search action to trigger JSON endpoint
❌ Impact: Static URL scraping misses dynamic API data sources
```

---

## 🔧 Our Solution: Playwright-Based Dynamic Scraping

### Core Technology Stack

-   **Python** - Main programming language
-   **Playwright** - Browser automation (handles JS rendering)
-   **Persistent Browser Context** - Maintains session between runs
-   **CSV Export** - Clean, structured data output

### Method Breakdown

#### 1. Browser Automation Approach

```python
# Instead of simple HTTP requests:
requests.get(url)  # ❌ Gets static HTML only

# We use full browser rendering:
playwright.chromium.launch_persistent_context()  # ✅ Executes JavaScript
```

#### 2. Persistent User Data

```
📁 user_data/
├── cookies.db          # Session cookies
├── local_storage/      # Browser storage
├── cache/             # Cached resources
└── preferences        # Browser settings
```

**Why:** Appears as returning user, bypasses bot detection

#### 3. Anti-Detection Techniques

```python
args=['--disable-blink-features=AutomationControlled']  # Hide automation flags
user_agent='Mozilla/5.0...'  # Real browser user agent
viewport={'width': 1920, 'height': 1080}  # Standard screen size
```

#### 4. Dynamic Content Handling

```python
# Wait for JavaScript to load prices
page.wait_for_load_state("networkidle")
time.sleep(2)  # Additional buffer for async operations
```

#### 5. Action-Triggered API Discovery

```python
# Problem: Direct URL access doesn't reveal JSON endpoints
# https://www.powerbuy.co.th/th/search/samsung?fill=1-0%7C2-0
# ❌ No samsung.json?fill=2-0&keyword=samsung appears in Network tab

# Solution: Simulate user search actions to trigger API calls
page.goto("https://www.powerbuy.co.th")
page.fill('input[name="search"]', 'samsung')  # Trigger search action
page.click('button[type="submit"]')

# Now JSON endpoints become visible:
# ✅ samsung.json?fill=2-0&keyword=samsung appears in Network tab
# ✅ Can intercept and extract structured data from API responses
```

---

## 🚀 What We CAN Do

### ✅ Capabilities

1. **Handle Dynamic Content**

    - Extract prices loaded via JavaScript
    - Wait for AJAX calls to complete
    - Process single-page applications
    - Trigger action-dependent API endpoints

2. **API Endpoint Discovery**

    - Simulate user interactions to reveal hidden JSON APIs
    - Intercept network requests for structured data
    - Handle action-triggered data loading patterns
    - Extract data from dynamic API responses

3. **Bypass Basic Protection**

    - Navigate Cloudflare challenges
    - Maintain session cookies
    - Simulate human browsing patterns

4. **Reliable Data Extraction**

    - Multiple selector fallbacks
    - Error handling and recovery
    - Data validation and cleaning

5. **Production-Ready Features**
    - Comprehensive logging
    - Screenshot capture for debugging
    - Structured CSV output
    - Progress tracking

### 📊 Data Quality Assurance

```python
# Data validation example
product_data = {
    'name': validate_text(extracted_name),
    'price': validate_currency(extracted_price),
    'stock': validate_stock_status(extracted_stock),
    'sku': validate_sku(extracted_sku)
}
```

---

## ⚠️ What We CAN'T Do (Limitations)

### ❌ Technical Limitations

1. **Advanced Bot Detection**

    - Machine learning-based detection systems
    - Behavioral analysis over time
    - Device fingerprinting beyond basic masking

2. **Complex Authentication**

    - Two-factor authentication (2FA)
    - Dynamic login systems
    - Member-only content requiring human verification

3. **Real-time Requirements**

    - Sub-second response times
    - Continuous monitoring (minutes apart)
    - Live price streaming

4. **Scale Limitations**
    - 1000+ products per run (browser memory limits)
    - Multiple concurrent browser instances
    - Very high-frequency requests (>1 per second)

### 🔒 Ethical & Legal Boundaries

```
❌ Cannot scrape if:
   - robots.txt explicitly forbids
   - Terms of Service prohibit data extraction
   - Personal/private data is involved
   - Scraping causes server overload
```

---

## 🛠️ Implementation Strategy Idea

### Phase 1: Development Setup

1. **Environment Preparation**

    ```bash
    pip install playwright beautifulsoup4 pandas pydantic
    playwright install chromium
    ```

2. **Initial Testing**
    - Test single product page
    - Verify data extraction accuracy
    - Validate anti-detection measures
    - Map action-triggered API endpoints
    - Test JSON data interception methods

### Phase 2: Production Implementation

1. **Robust Error Handling**

    ```python
    try:
        data = extract_product_data(page)
    except TimeoutError:
        log_error("Page load timeout")
        take_screenshot_for_debug()
    except ElementNotFound:
        try_alternative_selectors()
    ```

2. **Data Validation**
    ```python
    class ProductData(BaseModel):
        name: str
        price: float
        stock_status: str
        sku: str
    ```

### Phase 3: Monitoring & Maintenance

1. **Success Metrics**

    - Data extraction success rate (>95%)
    - Average execution time (<2 minutes per product)
    - Error recovery rate

2. **Maintenance Schedule**
    - Weekly selector validation
    - Monthly anti-detection review
    - Quarterly full system audit

---

## 📈 Expected Outcomes

### Immediate Benefits

-   **Time Savings:** 2-3 hours daily → 5 minutes automated
-   **Data Accuracy:** 100% consistent formatting
-   **Competitive Advantage:** Real-time pricing intelligence

### Success Criteria

```
✅ 50 products scraped successfully
✅ All 4 data fields extracted accurately
✅ <5% error rate across runs
✅ CSV format ready for business use
✅ Runs reliably without manual intervention
```

---

## 🔍 Risk Assessment & Mitigation

### High Risk

-   **Website Structure Changes:** Monthly monitoring required
-   **Anti-bot Upgrades:** Continuous adaptation needed

### Medium Risk

-   **IP Blocking:** Use residential proxies if needed
-   **Rate Limiting:** Implement smart delays

### Low Risk

-   **Server Downtime:** Retry mechanisms in place
-   **Data Format Changes:** Flexible parsing logic

---

## 🎯 Team Guidelines

### Development Best Practices

1. **Always test on sample data first**
2. **Implement comprehensive logging**
3. **Use version control for scraper iterations**
4. **Document all selector changes**
5. **Maintain ethical scraping standards**

### Deployment Checklist

```
□ Test on all 20 target URLs
□ Verify data quality and completeness
□ Check execution time performance
□ Validate CSV output format
□ Test error recovery scenarios
□ Document any site-specific quirks
```

---

_This methodology ensures reliable, ethical, and maintainable web scraping for competitive intelligence while respecting target website resources and terms of service._
