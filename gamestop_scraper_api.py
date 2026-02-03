"""
GameStop Digital Products Scraper API
Backend service using Constructor.io API with STRICT Digital condition filter
NOTE: GameStop does NOT sell PlayStation digital products - only Xbox, Nintendo, and PC
"""

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import requests
import time
import re
from typing import Optional, List, Dict, Any
from datetime import datetime
import os

app = FastAPI(title="GameStop Scraper API", version="4.0.1")

# Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Constructor.io API (GameStop's search provider)
CONSTRUCTOR_API_KEY = "key_FIW9YAimY77z5QEf"
CONSTRUCTOR_BASE = "https://ac.cnstrc.com"
PRODUCTS_PER_PAGE = 60

# Platform detection from product name
# NOTE: PlayStation excluded - GameStop doesn't sell PS digital products
PLATFORM_PATTERNS = {
    "Xbox": [r"xbox\s*(one|series|360)?", r"xbox\s*series\s*[xs]"],
    "Nintendo": [r"nintendo\s*(switch|wii|3ds)?", r"\bswitch\s*2?\b"],
    "PC": [r"\bpc\b", r"steam", r"ea\s*app", r"origin", r"epic", r"windows", r"gog", r"battle\.net", r"battlenet"],
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Origin": "https://www.gamestop.com",
    "Referer": "https://www.gamestop.com/",



def detect_platform(product_name: str, product_id: str = "") -> str:
    """Detect platform from product name using regex patterns"""
    text = f"{product_name} {product_id}".lower()

    for platform, patterns in PLATFORM_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return platform

    # Check for Meta Quest
    if "meta quest" in text or "oculus" in text:
        return "Meta Quest"

    return "Other"


def parse_price(price_value) -> Optional[float]:
    """Parse price value to float"""
    if price_value is None:
        return None
    try:
        return float(price_value)
    except (ValueError, TypeError):
        return None


def is_valid_digital_product(name: str) -> bool:
    """Check if product is actually a digital game code (not hardware or gift cards)
    Also excludes PlayStation products as GameStop doesn't sell PS digital codes"""
    name_lower = name.lower()

    # Exclude PlayStation products - GameStop does NOT sell PlayStation digital codes
    # These show up in digital-store but are actually physical disc products
    playstation_patterns = [
        r"playstation\s*[45]?",
        r"\bps[45]\b",
        r"\bps\s*[45]\b",
        r"-\s*playstation",
        r"playstation\s*vr",
        r"\bpsvr\b",
    ]

    for pattern in playstation_patterns:
        if re.search(pattern, name_lower):
            return False

    # Exclude hardware/physical products, gift cards, AND subscriptions
    exclude_patterns = [
        # Hardware & Accessories
        r"\bconsole\b",
        r"\bcontroller\b",
        r"\bjoy-?con\b",  # Nintendo controllers
        r"\bheadset\b",
        r"\bheadphones\b",
        r"\bcable\b",
        r"\bcharger\b",
        r"\badapter\b",
        r"\bstand\b",
        r"\bcase\b(?!.*pass)",
        r"\bcover\b",
        r"screen\s*protector",
        r"\bdock\b",
        r"\bstorage\b",
        r"hard\s*drive",
        r"\bssd\b",
        r"memory\s*card",
        r"\bsd\s*card\b",
        r"micro\s*sd",
        r"\bamiibo\b",
        r"\bfigure\b",
        r"\bcollectible\b",
        r"\bposter\b",
        r"\bt-?shirt\b",
        r"\bhoodie\b",
        r"\bplush\b",
        r"\btoy\b",
        r"\bhardware\b",
        r"\baccessor",
        r"\bkeyboard\b",
        r"\bmouse\b",
        r"\bmonitor\b",
        r"\bchair\b",
        r"\bdesk\b",
        # Gift cards & Currency - can't purchase with GameStop cards
        r"\bgift\s*card\b",
        r"\bpsn\s*card\b",
        r"\bxbox\s*gift\b",
        r"\bnintendo\s*eshop\s*card\b",
        r"\bsteam\s*wallet\b",
        r"\bv-?bucks\s*card\b",
        r"\brobux\s*card\b",
        r"\bprepaid\b",
        r"\bwallet\s*card\b",
        r"\bdigital\s*card\b",
        r"\bcurrency\s*card\b",
        # Subscriptions & Memberships - can't purchase with gift cards
        r"game\s*pass",
        r"xbox\s*live",
        r"ps\s*plus",
        r"playstation\s*plus",
        r"nintendo\s*online",
        r"membership",
        r"subscription",
        r"\bea\s*play\b",
    ]

    for pattern in exclude_patterns:
        if re.search(pattern, name_lower):
            return False

    return True


def fetch_digital_products(page: int, sort_by: str = "popularity") -> dict:
    """Fetch digital products from digital-store group with strict filtering"""
    # Using digital-store group but with STRICT filtering to exclude pre-owned
    url = f"{CONSTRUCTOR_BASE}/browse/group_id/digital-store"

    params = {
        "key": CONSTRUCTOR_API_KEY,
        "page": page,
        "num_results_per_page": PRODUCTS_PER_PAGE,
        "sort_by": sort_by,
        "sort_order": "descending",
    }

    try:
        response = requests.get(url, params=params, headers=HEADERS, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"API request failed: {e}")
        return {}


def parse_constructor_product(item: dict) -> Dict[str, Any]:
    """Parse a product from Constructor.io browse response"""
    data = item.get('data', {})
    name = item.get('value', '') or data.get('product_name', '')

    # CRITICAL: Check condition field to exclude pre-owned products
    condition = str(data.get('condition', '')).lower()
    if 'pre' in condition or 'owned' in condition or 'used' in condition or 'refurb' in condition:
        return None  # Skip pre-owned products

    # Also check name for pre-owned indicators
    name_lower = name.lower()
    if 'pre-owned' in name_lower or 'preowned' in name_lower or 'pre owned' in name_lower:
        return None  # Skip pre-owned products

    # Get prices
    regular_price = parse_price(data.get('price'))

    # Calculate Pro price (5% off)
    pro_price = round(regular_price * 0.95, 2) if regular_price else None

    # Get URL
    url = data.get('url', '')
    if url and not url.startswith('http'):
        url = f"https://www.gamestop.com{url}"
    # Fix staging URL
    url = url.replace('sfcc-stg.gamestop.com', 'www.gamestop.com')

    # Detect platform from name and ID
    product_id = data.get('id', '')
    platform = detect_platform(name, product_id)

    # Get SKU from ID or productId
    sku = str(data.get('productId', '')) or product_id.split('++')[0] if '++' in product_id else product_id

    return {
        'sku': sku,
        'name': name,
        'platform': platform,
        'category': 'Digital',
        'regularPrice': regular_price,
        'proPrice': pro_price,
        'availability': 'Available',
        'url': url,
        'imageUrl': data.get('image_url', ''),
        'edition': data.get('edition', ''),
        'condition': data.get('condition', 'Digital'),  # Add condition field
    }


def get_usd_eur_rate() -> float:
    """Get current USD to EUR exchange rate from Google Finance"""
    # Try Google Finance first
    try:
        response = requests.get(
            "https://www.google.com/finance/quote/USD-EUR",
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            },
            timeout=10
        )
        if response.ok:
            # Extract rate from Google Finance page
            # Look for the data-last-price attribute or the rate in the page
            import re
            # Pattern to find the exchange rate (e.g., 0.8552)
            patterns = [
                r'data-last-price="([0-9.]+)"',
                r'"USD / EUR","([0-9.]+)"',
                r'>([0-9]\.[0-9]{4})<',
            ]
            for pattern in patterns:
                match = re.search(pattern, response.text)
                if match:
                    rate = float(match.group(1))
                    if 0.5 < rate < 1.5:  # Sanity check for USD/EUR range
                        return rate
    except Exception as e:
        print(f"Google Finance failed: {e}")

    # Fallback to exchangerate-api.com
    try:
        response = requests.get(
            "https://api.exchangerate-api.com/v4/latest/USD",
            timeout=10
        )
        if response.ok:
            data = response.json()
            return data['rates'].get('EUR', 0.85)
    except Exception:
        pass
    return 0.85


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.get("/rate")
async def get_exchange_rate():
    """Get current USD to EUR exchange rate"""
    rate = get_usd_eur_rate()
    return {
        "rate": rate,
        "pair": "USD/EUR",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/scrape")
async def scrape_products(
    category: str = Query("all", description="Filter by category: all, xbox, nintendo, pc"),
    max_pages: int = Query(0, description="Maximum pages to scrape (0 = all)"),
    discount_rate: float = Query(0.88, description="Your discount rate for GameStop cards")
):
    """Scrape GameStop digital products - ONLY actual digital downloads/codes"""
    all_products = []

    page = 1
    max_page = max_pages if max_pages > 0 else 100  # Safety limit
    total_available = 0

    print(f"\n=== Scraping Digital Products (Condition=Digital filter - excludes pre-owned) ===")

    while page <= max_page:
        data = fetch_digital_products(page, sort_by="popularity")

        if not data:
            break

        response = data.get('response', {})
        results = response.get('results', [])

        if not results:
            break

        # Get total for first page
        if page == 1:
            total_available = response.get('total_num_results', 0)
            total_pages_available = (total_available + PRODUCTS_PER_PAGE - 1) // PRODUCTS_PER_PAGE

            if max_pages == 0:
                max_page = min(total_pages_available, 100)

            print(f"Total digital products available: {total_available} ({total_pages_available} pages)")

        print(f"Page {page}/{max_page}: {len(results)} products")

        for item in results:
            product = parse_constructor_product(item)

            # Skip if product is None (pre-owned/used product)
            if product is None:
                continue

            # Validate it's a real digital product (not hardware or gift cards)
            if product.get('name') and is_valid_digital_product(product['name']):
                all_products.append(product)

        page += 1
        time.sleep(0.15)  # Rate limiting

    print(f"\nTotal scraped: {len(all_products)} products")

    # Remove duplicates by SKU
    seen_skus = set()
    unique_products = []
    for p in all_products:
        sku = p.get('sku', '')
        if sku and sku not in seen_skus:
            seen_skus.add(sku)
            unique_products.append(p)
        elif not sku:
            name = p.get('name', '')
            if name not in seen_skus:
                seen_skus.add(name)
                unique_products.append(p)

    print(f"After deduplication: {len(unique_products)} unique products")

    # Filter by category/platform if specified
    if category.lower() != "all":
        category_map = {
            "xbox": "Xbox",
            "nintendo": "Nintendo",
            "pc": "PC"
        }
        target_platform = category_map.get(category.lower())
        if target_platform:
            unique_products = [p for p in unique_products if p.get('platform') == target_platform]
            print(f"After platform filter ({target_platform}): {len(unique_products)} products")

    # Get exchange rate
    usd_eur_rate = get_usd_eur_rate()

    # Calculate costs
    for product in unique_products:
        pro_price = product.get('proPrice') or product.get('regularPrice')
        if pro_price:
            product['yourCostUSD'] = round(pro_price * discount_rate, 2)
            product['yourCostEUR'] = round(product['yourCostUSD'] * usd_eur_rate, 2)
        else:
            product['yourCostUSD'] = None
            product['yourCostEUR'] = None

    return {
        "products": unique_products,
        "metadata": {
            "scrapedAt": datetime.now().isoformat(),
            "totalProducts": len(unique_products),
            "totalAvailable": total_available,
            "usdEurRate": usd_eur_rate,
            "discountRate": discount_rate,
            "source": "Constructor.io API (Video Games with Condition=Digital filter)",
            "note": "PlayStation digital products not available on GameStop",
            "priceWarning": "IMPORTANT: Prices from Constructor API may be outdated. Always verify prices on GameStop.com before purchasing. Some prices may differ by $5-10 from current GameStop prices.",
            "recommendation": "Click product URLs to verify current prices on GameStop before making purchase decisions"
        }
    }


@app.get("/scrape/quick")
async def scrape_quick(
    pages: int = Query(3, description="Number of pages to scrape"),
    discount_rate: float = Query(0.88, description="Your discount rate")
):
    """Quick scrape - first few pages for testing"""
    return await scrape_products(category="all", max_pages=pages, discount_rate=discount_rate)


@app.get("/scrape/category/{platform}")
async def scrape_by_platform(
    platform: str,
    max_pages: int = Query(0, description="Maximum pages"),
    discount_rate: float = Query(0.88, description="Discount rate")
):
    """Scrape products for a specific platform"""
    return await scrape_products(category=platform, max_pages=max_pages, discount_rate=discount_rate)


@app.get("/allkeyshop/price")
async def get_allkeyshop_price(
    url: str = Query(..., description="AllKeyShop product URL"),
    edition: str = Query("", description="Edition filter (e.g., Ultimate, Standard)"),
    region: str = Query("", description="Region filter (e.g., Global, Europe)"),
    keys_only: bool = Query(True, description="Only show CD Keys (exclude accounts)")
):
    """Scrape lowest price from AllKeyShop for a product using embedded JSON data"""
    import json

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": "https://www.google.com/",
        }

        response = requests.get(url, headers=headers, timeout=15)

        if not response.ok:
            return {"error": "Failed to fetch AllKeyShop page", "status": response.status_code}

        html = response.text

        # Extract gamePageTrans JSON data from the page
        json_pattern = r'var\s+gamePageTrans\s*=\s*(\{.*?\});'
        json_match = re.search(json_pattern, html, re.DOTALL)

        if not json_match:
            json_pattern2 = r'gamePageTrans\s*=\s*(\{[^;]+\})'
            json_match = re.search(json_pattern2, html, re.DOTALL)

        if not json_match:
            return {
                "error": "Could not find price data in page",
                "url": url,
                "hint": "Page structure may have changed"
            }

        try:
            data = json.loads(json_match.group(1))
        except json.JSONDecodeError as e:
            return {"error": f"Failed to parse price data: {str(e)}", "url": url}

        prices_data = data.get('prices', [])
        regions_data = data.get('regions', {})
        merchants_data = data.get('merchants', {})
        editions_data = data.get('editions', {})

        if not prices_data:
            return {"error": "No prices found in data", "url": url}

        # Filter and process prices
        filtered_prices = []
        edition_lower = edition.lower() if edition else ""
        region_lower = region.lower() if region else ""

        for price_item in prices_data:
            # Check if it's an account (skip if keys_only=True)
            is_account = price_item.get('account', False)
            if keys_only and is_account:
                continue

            # Get edition info
            edition_id = str(price_item.get('edition', ''))
            edition_info = editions_data.get(edition_id, {})
            edition_name = edition_info.get('name', 'Standard') if isinstance(edition_info, dict) else str(edition_info)

            # Apply edition filter
            if edition_lower:
                if edition_lower not in edition_name.lower():
                    continue

            # Get region info
            region_id = str(price_item.get('region', ''))
            region_info = regions_data.get(region_id, {})
            region_name = region_info.get('filter_name', region_info.get('filterName', '')) if isinstance(region_info, dict) else str(region_info)

            # Apply region filter
            if region_lower:
                if region_lower == "global" and "global" not in region_name.lower():
                    continue
                elif region_lower == "europe" and "europe" not in region_name.lower() and "eu" not in region_name.lower():
                    continue
                elif region_lower not in ["global", "europe"] and region_lower not in region_name.lower():
                    continue

            # Get merchant info
            merchant_id = str(price_item.get('merchant', ''))
            merchant_info = merchants_data.get(merchant_id, {})
            merchant_name = price_item.get('merchantName', '')
            if not merchant_name:
                merchant_name = merchant_info.get('name', 'Unknown') if isinstance(merchant_info, dict) else str(merchant_info)

            # Get price - use priceCard which includes fees (matches displayed price on AllKeyShop)
            # priceCard = price after coupon + payment fees (what you actually pay)
            final_price = price_item.get('priceCard', price_item.get('price', price_item.get('originalPrice', 0)))
            original_price = price_item.get('originalPrice', final_price)
            fees = price_item.get('feesCard', 0)

            # Get coupon info
            coupon_code = price_item.get('voucher_code', '')
            coupon_discount = price_item.get('voucher_discount_value', 0)

            # Get activation platform
            activation = price_item.get('activationPlatform', '')

            filtered_prices.append({
                'price': round(final_price, 2),
                'originalPrice': round(original_price, 2),
                'fees': round(fees, 2),
                'merchant': merchant_name,
                'region': region_name,
                'edition': edition_name,
                'activation': activation,
                'couponCode': coupon_code,
                'couponDiscount': coupon_discount,
                'isAccount': is_account
            })

        if not filtered_prices:
            return {
                "error": "No prices match your filters",
                "url": url,
                "totalOffers": len(prices_data),
                "filters": {"edition": edition, "region": region, "keys_only": keys_only}
            }

        # Sort by price
        filtered_prices.sort(key=lambda x: x['price'])

        lowest = filtered_prices[0]

        return {
            "lowestPrice": lowest['price'],
            "originalPrice": lowest['originalPrice'],
            "currency": "EUR",
            "store": lowest['merchant'],
            "region": lowest['region'],
            "edition": lowest['edition'],
            "activation": lowest['activation'],
            "couponCode": lowest['couponCode'],
            "couponDiscount": lowest['couponDiscount'],
            "totalOffers": len(filtered_prices),
            "allPrices": filtered_prices[:10],
            "url": url,
            "scrapedAt": datetime.now().isoformat()
        }

    except requests.RequestException as e:
        return {"error": f"Request failed: {str(e)}", "url": url}
    except Exception as e:
        return {"error": f"Scraping failed: {str(e)}", "url": url}


@app.get("/verify-price")
async def verify_price(
    url: str = Query(..., description="GameStop product URL to verify"),
):
    """
    Verify/Fetch LIVE price from GameStop product page using CloudScraper.
    Bypasses cache and fetches what you actually see on the page.
    """
    global driver
    if not url:
        return {"error": "URL required"}

    print(f"Verifying live price for: {url}")
    
    # Ensure we use production URL
    if 'sfcc-stg.gamestop.com' in url:
        url = url.replace('sfcc-stg.gamestop.com', 'www.gamestop.com')
        print(f"Corrected URL to: {url}")
    
    async with browser_lock:
        # Retry loop for driver stability
        for attempt in range(3):
            try:
                # Use undetected_chromedriver
                driver = get_driver()
                
                # Check if driver is actually alive
                try:
                    # Simple check to see if we can communicate
                    if not driver.service.process.poll() is None:
                        raise Exception("Driver process terminated")
                    _ = driver.current_url 
                except Exception:
                   print("Driver dead or unresponsive, restarting...")
                   if driver:
                       try: driver.quit()
                       except: pass
                   driver = None
                   time.sleep(1) # Wait before retry
                   driver = get_driver()

                # Navigate to page
                print(f"Navigating to {url}...")
                driver.get(url)
                # Removed break - proceed to scraping logic
            except Exception as e:
                print(f"Attempt {attempt+1} failed: {e}")
                # Reset driver
                if driver:
                    try: driver.quit()
                    except: pass
                driver = None
                time.sleep(2) # Backoff
                
                if attempt == 2: # Last attempt
                    return {"status": "error", "message": f"Browser Error: {str(e)}"}
                continue # Try next attempt
            
            # Wait for some content to load (price)
            # We can wait for a generic element or just sleep briefly
            time.sleep(3) # Wait for JS to render
            
            # --- DIGITAL SELECTION LOGIC ---
            # Try to find and click "Digital" format
            is_digital_confirmed = False
            try:
                print("Checking for Digital format...")
                
                # Check 1: Is it already digital? (URL often contains 'digital' or 'standard-edition' but not 'physical')
                # But better to check UI elements.
                
                # Look for buttons/labels with "Digital" text
                # XPath to find elements with text 'Digital' that are likely buttons or selectors
                digital_elems = driver.find_elements(By.XPATH, "//*[contains(text(), 'Digital')]")
                
                clicked_digital = False
                for elem in digital_elems:
                    try:
                        # Check if it's a clickable option (e.g., inside a button, label, or div with class attributes)
                        tag = elem.tag_name.lower()
                        parent = elem.find_element(By.XPATH, "..")
                        
                        # Heuristic: verify it's part of a selection group
                        if tag in ['button', 'label', 'span', 'div'] and elem.is_displayed():
                            # Check if already selected
                            # GameStop often uses 'selected' class on the container or element
                            classes = elem.get_attribute('class') or ''
                            parent_classes = parent.get_attribute('class') or ''
                            
                            is_selected = 'selected' in classes.lower() or 'selected' in parent_classes.lower()
                            
                            if is_selected:
                                print("Digital format already selected.")
                                is_digital_confirmed = True
                                break
                            
                            # If not selected, try to click
                            # Prefer elements that look like buttons
                            if not clicked_digital:
                                print(f"Clicking Digital option ({tag})...")
                                driver.execute_script("arguments[0].click();", elem) # Force click
                                time.sleep(2) # Wait for update
                                clicked_digital = True
                                is_digital_confirmed = True
                                break
                    except:
                        continue
                        
                if not is_digital_confirmed:
                    # Maybe it's a "Digital Only" page? 
                    # If there are no Physical options, assume it's digital if the title/breadcrumbs say so
                    page_text = driver.find_element(By.TAG_NAME, "body").text
                    if "Format: Digital" in page_text or "Platform: Digital" in page_text:
                        is_digital_confirmed = True
                        print("Confirmed Digital by page text.")
            
            except Exception as e:
                print(f"Digital check warning: {e}")

            if not is_digital_confirmed:
                print("Could not confirm Digital format. Skipping.")
                return {
                    "status": "error", 
                    "message": "Skipped: format is not Digital",
                    "code": "NOT_DIGITAL"
                }

            html = driver.page_source
            
            # --- PRICE EXTRACTION LOGIC ---
            regular_price = None
            pro_price = None
            
            # Strategy 1: "Digital" Condition Tile Price (High Accuracy for Digital Items)
            # The user text shows "Condition Digital $16.62".
            try:
                # Look for the container that represents the Digital option
                # It usually contains the text "Digital" and a price
                digital_labels = driver.find_elements(By.XPATH, "//*[contains(text(), 'Digital')]")
                
                for label in digital_labels:
                    try:
                        # Check parent/ancestor for the tile container
                        # usually a label, button, or div with class 'attribute' or 'value'
                        parent = label.find_element(By.XPATH, "./..")
                        grandparent = parent.find_element(By.XPATH, "./..")
                        
                        # Get text of the block
                        block_text = grandparent.text.replace("\n", " ").strip()
                        
                        # Look for price in this block
                        # Pattern: "Digital $16.62" or "Digital ... $16.62"
                        if "Digital" in block_text:
                            match = re.search(r'\$?([0-9]+\.[0-9]{2})', block_text)
                            if match:
                                val = float(match.group(1))
                                # Sanity check: is it in a realistic range?
                                if 0 < val < 200:
                                    print(f"Found Price in Digital Tile: {val}")
                                    # This is likely the 'effective' price (Pro price if logged in/visible, or just sale)
                                    # We treat this as a strong candidate for Pro Price if it matches 'for Pros' context
                                    # But let's verify if there is a separate 'Regular' price
                                    
                                    # If we find this, it's often the 'Pro' price because scraping defaults to best offer?
                                    # Or is it just the current price?
                                    # Let's verify against 'for Pros' text to be sure.
                                    # For now, store it as a potential Pro Price candidate
                                    if pro_price is None: 
                                        pro_price = val
                    except:
                        continue
            except Exception as e:
                print(f"Digital Tile scan error: {e}")

            # Strategy 2: Explicit "For Pros" Text (Specific)
            try:
                # Use XPath to find text containing "Pros"
                # Use a broader search
                pro_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Pros')]")
                for el in pro_elements:
                    if el.is_displayed():
                        text = el.text.strip().replace("\n", " ") 
                        # Regex: "$16.62 for Pros" or "for Pros" near price
                        # Relaxed: Price ... for Pros OR Pros ... Price
                        
                        # Type A: "$16.62 for Pros"
                        match = re.search(r'\$?([0-9]+\.[0-9]{2})\s*(?:for)?\s*Pros', text, re.IGNORECASE)
                        if match:
                            val = float(match.group(1))
                            print(f"Found Explicit Pro Price (Type A): {val}")
                            pro_price = val
                            break
                            
                        # Type B: Parent container has both?
                        parent = el.find_element(By.XPATH, "..")
                        p_text = parent.text.replace("\n", " ")
                        match = re.search(r'\$?([0-9]+\.[0-9]{2})\s*(?:for)?\s*Pros', p_text, re.IGNORECASE)
                        if match:
                            val = float(match.group(1))
                            print(f"Found Explicit Pro Price (Type B): {val}")
                            pro_price = val
                            break
            except Exception as e:
                pass

            # Strategy 3: Standard/Main Price (Regular)
            try:
                # Selectors for the main displayed price (crossed out or main)
                # If we have a 'Pro' price, the other price is likely the regular one.
                # .actual-price often shows the 'sale' price, which might be the Pro price.
                # We need to find the HIGHER price if we have a lower Pro price?
                
                price_selectors = [".actual-price", ".price-sales", "span[itemprop='price']", ".prices .price", ".list-price"]
                
                prices_found = []
                for sel in price_selectors:
                    els = driver.find_elements(By.CSS_SELECTOR, sel)
                    for el in els:
                        if el.is_displayed():
                            val = float(re.search(r'\$?([0-9]+\.[0-9]{2})', el.text).group(1))
                            if 0 < val < 200:
                                prices_found.append(val)
                
                if prices_found:
                    # If we have a pro price, regular is likely the max of found prices?
                    # Example: $69.99 (crossed) $17.50 (sale/pro)
                    # If we found $16.62 as pro, $17.50 might be regular sale.
                    # Let's take the MAX as regular price if multiple found?
                    # Or the one that is NOT the pro price?
                    
                    max_p = max(prices_found)
                    min_p = min(prices_found)
                    
                    if pro_price:
                        # If we have a pro price, assume regular is the higher one
                        regular_price = max_p if max_p > pro_price else pro_price
                        # Wait, in WWE example: $17.50 is regular, $16.62 is pro.
                        # If scraper found $17.50, we set regular to $17.50.
                    else:
                        regular_price = max_p # Default to highest (safest for discounts)
                        
                    print(f"Prices found: {prices_found}. Selected Regular: {regular_price}")
            except:
                pass
                
            # Fallback
            if not regular_price:
                html = driver.page_source
                match = re.search(r'"sellingPrice":\s*"?([0-9]+\.[0-9]{2})"?', html)
                if match:
                    regular_price = float(match.group(1))

            # Strategy 4: "5% extra off" Calculation
            if not pro_price and regular_price:
                page_text = driver.find_element(By.TAG_NAME, "body").text
                if "Pros get 5% extra off" in page_text or "Save 5% on PreOwned" in page_text: 
                    # Only apply if we haven't found a text mismatch
                    print("Found 'Pros get 5% extra off' text. Calculating Pro Price.")
                    pro_price = round(regular_price * 0.95, 2)
            
            # Logic Update: If Pro Price is scraped from Digital Tile ($16.62)
            # And Regular Price is scraped from Main ($17.50)
            # We are good.
            
            # If Regular Price is same as Pro Price, but we suspected a discount?
            # Trust the explicit values.
            
            # Final sanity: Pro Price shouldn't be higher than regular
            if pro_price and regular_price and pro_price > regular_price:
                regular_price = pro_price # Swap or equalize? likely logic error, but assume regular is at least pro.
                
            if not pro_price and regular_price:
                # If verified digital, assume regular is the price
                pro_price = regular_price # No discount confirmed
                pass

            # Construct Result
            final_live_price = pro_price if pro_price else regular_price
            
            return {
                "status": "success",
                "url": url,
                "prices": {
                    "regular": regular_price,
                    "pro": pro_price
                },
                "livePrice": final_live_price, # Backward compatibilityish, but we prefer structured
                "verifiedAt": datetime.now().isoformat(),
                "note": "Split Regular/Pro extraction"
            }

 
             
    # Fallback if loop exhausted (handled by return inside loop)
    return {"status": "error", "message": "Verification failed after retries"}



if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print("Starting GameStop Scraper API v4.0 (Digital ONLY - No Physical Products)...")
    print("NOTE: PlayStation digital products are NOT available on GameStop")
    print("Available platforms: Xbox, Nintendo, PC")
    print(f"API will be available at http://localhost:{port}")
    print(f"Documentation at http://localhost:{port}/docs")
    uvicorn.run(app, host="0.0.0.0", port=port)
