"""
Grocery Data Collection Tasks

This module handles grocery-related background tasks including:
- Weekly IGA flyer data scraping
- Data processing and cleaning
- Database storage with cleanup
"""

import asyncio
import logging
import re
from datetime import datetime
from typing import Any, Dict, List, Optional
import aiohttp

from ..celery_app import app
from ...config.database import db_config
from ...database.models.grocery_deals import GroceryDeal
from sqlalchemy import delete, text

# Browser automation for dynamic endpoint discovery
try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

logger = logging.getLogger(__name__)


@app.task(bind=True, max_retries=3, default_retry_delay=300)
def fetch_iga_flyer_data(self) -> Dict[str, Any]:
    """
    Weekly task to fetch IGA digital flyer data.
    
    This task:
    1. Fetches JSON data from IGA digital flyer endpoint
    2. Clears existing data (deals only valid 7 days)
    3. Processes and cleans the data
    4. Stores new deals in database
    5. Provides detailed logging and monitoring
    """
    task_id = self.request.id
    current_time = datetime.utcnow()
    
    # Enhanced logging for Celery beat tracking
    logger.info(f"🛒 GROCERY TASK STARTED: fetch_iga_flyer_data at {current_time}")
    logger.info(f"📋 Task ID: {task_id}")
    logger.info(f"⏰ Current UTC time: {current_time}")
    print(f"🛒 GROCERY TASK STARTED: fetch_iga_flyer_data at {current_time}")
    print(f"📋 Task ID: {task_id}")
    print(f"⏰ Current UTC time: {current_time}")

    try:
        # Use asyncio.run() with proper event loop handling
        import nest_asyncio
        nest_asyncio.apply()
        
        result = asyncio.run(_fetch_and_process_iga_data())
        
        logger.info(f"✅ GROCERY TASK COMPLETED: {result}")
        print(f"✅ GROCERY TASK COMPLETED: {result}")
        
        return {
            "status": "success",
            "task_id": task_id,
            "timestamp": current_time.isoformat(),
            "result": result
        }
        
    except Exception as e:
        error_msg = f"❌ GROCERY TASK FAILED: {str(e)}"
        logger.error(error_msg, exc_info=True)
        print(error_msg)
        
        # Retry logic
        if self.request.retries < self.max_retries:
            retry_delay = self.default_retry_delay * (2 ** self.request.retries)
            logger.info(f"🔄 Retrying task in {retry_delay} seconds (attempt {self.request.retries + 1}/{self.max_retries})")
            raise self.retry(countdown=retry_delay, exc=e)
        
        return {
            "status": "failed",
            "task_id": task_id,
            "timestamp": current_time.isoformat(),
            "error": str(e),
            "retries_exhausted": True
        }


async def _fetch_and_process_iga_data() -> Dict[str, Any]:
    """
    Internal async function to fetch and process IGA data.
    
    The IGA flyer uses a dynamic endpoint that changes weekly:
    https://dam.flippenterprise.net/flyerkit/publication/{PUBLICATION_ID}/products
    
    We need to:
    1. Load the main IGA page
    2. Extract the current publication ID from the page
    3. Build the products endpoint URL
    4. Fetch the products data
    """
    # Main IGA digital flyer page (for reference)
    # iga_main_url = "https://www.iga.net/en/flyer/digital_flyer"
    
    async with aiohttp.ClientSession() as session:
        try:
            # Step 1: Discover current publication ID and access token
            logger.info("🔍 Discovering current IGA endpoint...")
            endpoint_info = await _discover_iga_endpoint()
            publication_id = endpoint_info["publication_id"]
            access_token = endpoint_info["access_token"]
            
            logger.info(f"📋 Using publication ID: {publication_id}")
            logger.info(f"🔑 Using access token: {access_token[:10]}...")
            
            # Step 2: Build the products endpoint URL
            products_url = f"https://dam.flippenterprise.net/flyerkit/publication/{publication_id}/products"
            params = {
                "display_type": "all",
                "locale": "en",
                "access_token": access_token
            }
            
            logger.info(f"🛒 Fetching products from: {products_url}")
            
            # Step 4: Fetch the products data
            async with session.get(products_url, params=params, timeout=30) as response:
                if response.status != 200:
                    raise Exception(f"Products API returned status {response.status}")
                
                data = await response.json()
                logger.info(f"📥 Received {len(data)} products from IGA")
                logger.info(f"📊 Data type: {type(data)}")
                
                # Log sample of first product for debugging
                if data and len(data) > 0:
                    logger.info(f"🔍 Sample product structure: {list(data[0].keys())}")
                
        except Exception as e:
            logger.error(f"❌ Failed to fetch IGA data: {e}")
            raise
    
    # Process and store data
    async with db_config.get_session_context() as db_session:
        try:
            # Step 1: Clear existing data (deals only valid 7 days)
            logger.info("🧹 Clearing existing grocery deals data...")
            await db_session.execute(delete(GroceryDeal))
            await db_session.commit()
            logger.info("✅ Existing data cleared")
            
            # Step 2: Process and store new data
            processed_count = 0
            skipped_count = 0
            
            for item in data:
                try:
                    # Extract relevant fields from IGA JSON
                    processed_item = _extract_iga_fields(item)
                    
                    if processed_item:
                        # Create new GroceryDeal record
                        deal = GroceryDeal(
                            id=processed_item["id"],
                            name=processed_item["name"],
                            sku=processed_item["sku"],
                            description=processed_item["description"],
                            valid_from=processed_item["valid_from"],
                            valid_to=processed_item["valid_to"],
                            categories=processed_item["categories"],
                            price_text=processed_item["price_text"],
                            post_price_text=processed_item["post_price_text"],
                            original_price=processed_item["original_price"],
                            brand=processed_item["brand"],
                            web_commission_url=processed_item["web_commission_url"],
                            scraped_at=datetime.utcnow()
                        )
                        
                        db_session.add(deal)
                        processed_count += 1
                        
                    else:
                        skipped_count += 1
                        
                except Exception as e:
                    logger.warning(f"⚠️ Skipped item due to processing error: {e}")
                    skipped_count += 1
                    continue
            
            # Commit all changes
            await db_session.commit()
            
            result = {
                "total_items": len(data),
                "processed_count": processed_count,
                "skipped_count": skipped_count,
                "scrape_timestamp": datetime.utcnow().isoformat()
            }
            
            logger.info(f"✅ Data processing completed: {result}")
            return result
            
        except Exception as e:
            await db_session.rollback()
            logger.error(f"❌ Database operation failed: {e}")
            raise


def _get_iga_endpoint_from_config() -> Dict[str, str]:
    """
    Get IGA endpoint configuration from environment variables.
    
    This is the primary method for getting current publication ID and access token.
    These values need to be updated weekly when new flyers are published.
    
    Environment Variables:
        IGA_PUBLICATION_ID: Current publication ID (e.g., "7502970")
        IGA_ACCESS_TOKEN: Current access token (e.g., "692be3f8ba9e9247dc13d064cb89e7f9")
    
    Returns:
        Dict with 'publication_id' and 'access_token' keys
    """
    import os
    
    publication_id = os.getenv("IGA_PUBLICATION_ID", "7502970")
    access_token = os.getenv("IGA_ACCESS_TOKEN", "692be3f8ba9e9247dc13d064cb89e7f9")
    
    logger.info(f"📋 Using IGA publication ID from config: {publication_id}")
    logger.info(f"🔑 Using IGA access token from config: {access_token[:10]}...")
    
    return {
        "publication_id": publication_id,
        "access_token": access_token
    }


async def _discover_iga_endpoint() -> Dict[str, str]:
    """
    Discover the current IGA publication ID and access token automatically.
    
    Strategy:
    1. Try browser automation with stealth techniques (primary method)
    2. Try alternative discovery methods (API patterns, etc.)
    3. Fall back to environment variables if automation fails
    4. Final fallback to hardcoded values
    
    Returns:
        Dict with 'publication_id' and 'access_token' keys
    """
    # Step 1: Try enhanced browser automation with stealth techniques
    if PLAYWRIGHT_AVAILABLE:
        try:
            logger.info("🌐 Attempting stealth browser automation discovery...")
            
            async with async_playwright() as p:
                # Use stealth browser with realistic settings
                browser = await p.chromium.launch(
                    headless=True,
                    args=[
                        '--no-sandbox',
                        '--disable-blink-features=AutomationControlled',
                        '--disable-web-security',
                        '--disable-features=VizDisplayCompositor'
                    ]
                )
                
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
                    viewport={'width': 1920, 'height': 1080},
                    locale='en-CA',
                    timezone_id='America/Toronto'
                )
                
                # Add stealth scripts to avoid detection
                await context.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined,
                    });
                    Object.defineProperty(navigator, 'plugins', {
                        get: () => [1, 2, 3, 4, 5],
                    });
                    Object.defineProperty(navigator, 'languages', {
                        get: () => ['en-CA', 'en-US', 'en'],
                    });
                """)
                
                page = await context.new_page()
                
                # Track network requests
                products_request = None
                all_requests = []
                
                async def handle_request(request):
                    nonlocal products_request, all_requests
                    all_requests.append(request.url)
                    if "flyerkit/publication" in request.url and "/products" in request.url:
                        products_request = request
                        logger.info(f"🎯 Found products request: {request.url}")
                
                page.on("request", handle_request)
                
                # Navigate to IGA flyer page with realistic timing
                logger.info("📄 Loading IGA flyer page with stealth techniques...")
                await page.goto("https://www.iga.net/en/flyer/digital_flyer", 
                              wait_until="networkidle", timeout=45000)
                
                # Wait for page to fully load and make API calls
                await page.wait_for_timeout(8000)
                
                # Try to trigger any lazy-loaded content
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await page.wait_for_timeout(3000)
                
                # Try clicking on any interactive elements that might trigger API calls
                try:
                    # Look for any buttons or links that might load more content
                    buttons = await page.query_selector_all('button, a[href*="flyer"], .flyer-link')
                    for button in buttons[:3]:  # Try first 3 buttons
                        try:
                            await button.click()
                            await page.wait_for_timeout(2000)
                        except:
                            pass
                except:
                    pass
                
                if products_request:
                    url = products_request.url
                    logger.info(f"🔍 Analyzing discovered request URL: {url}")
                    
                    pub_id_match = re.search(r'/publication/(\d+)/', url)
                    token_match = re.search(r'access_token=([^&]+)', url)
                    
                    if pub_id_match and token_match:
                        publication_id = pub_id_match.group(1)
                        access_token = token_match.group(1)
                        logger.info(f"✅ Successfully discovered via browser automation:")
                        logger.info(f"   Publication ID: {publication_id}")
                        logger.info(f"   Access Token: {access_token[:10]}...")
                        await browser.close()
                        return {
                            "publication_id": publication_id,
                            "access_token": access_token
                        }
                else:
                    logger.warning("⚠️ No products API request found")
                    logger.info(f"📊 Total requests made: {len(all_requests)}")
                    # Log some sample requests for debugging
                    sample_requests = all_requests[:5] if len(all_requests) > 5 else all_requests
                    for req in sample_requests:
                        logger.debug(f"📡 Sample request: {req}")
                
                await browser.close()
                
        except Exception as e:
            logger.error(f"❌ Browser automation failed: {e}")
    
    # Step 2: Try alternative discovery methods
    try:
        logger.info("🔍 Trying alternative discovery methods...")
        # Try to find patterns in common API endpoints
        alternative_endpoints = await _try_alternative_endpoints()
        if alternative_endpoints:
            logger.info("✅ Found endpoint via alternative method")
            return alternative_endpoints
    except Exception as e:
        logger.warning(f"⚠️ Alternative discovery failed: {e}")
    
    # Step 3: Fall back to environment variables
    try:
        config_values = _get_iga_endpoint_from_config()
        logger.warning("⚠️ Using IGA endpoint from environment configuration (manual update required)")
        return config_values
    except Exception as e:
        logger.warning(f"⚠️ Failed to get config values: {e}")
    
    # Step 4: Final fallback to hardcoded values
    logger.warning("⚠️ Using fallback publication ID and access token")
    logger.warning("💡 Manual update required: Set IGA_PUBLICATION_ID and IGA_ACCESS_TOKEN environment variables")
    return {
        "publication_id": "7502970",
        "access_token": "692be3f8ba9e9247dc13d064cb89e7f9"
    }


async def _try_alternative_endpoints() -> Optional[Dict[str, str]]:
    """
    Try alternative methods to discover IGA endpoints with access token validation.
    
    Returns:
        Dict with 'publication_id' and 'access_token' keys if successful, None otherwise
    """
    try:
        # Method 1: Try common publication ID patterns with multiple access tokens
        base_id = 7502970
        known_tokens = [
            "692be3f8ba9e9247dc13d064cb89e7f9",  # Current working token
            # Add more tokens here as we discover them
        ]
        
        # Try recent publication IDs with known access tokens
        for offset in range(0, 15):  # Try current + next 14 publication IDs
            test_id = base_id + offset
            
            for token in known_tokens:
                test_url = f"https://dam.flippenterprise.net/flyerkit/publication/{test_id}/products"
                
                async with aiohttp.ClientSession() as session:
                    try:
                        async with session.get(test_url, params={
                            "display_type": "all",
                            "locale": "en",
                            "access_token": token
                        }, timeout=10) as response:
                            if response.status == 200:
                                data = await response.json()
                                if isinstance(data, list) and len(data) > 0:
                                    logger.info(f"✅ Found working combination:")
                                    logger.info(f"   Publication ID: {test_id}")
                                    logger.info(f"   Access Token: {token[:10]}...")
                                    return {
                                        "publication_id": str(test_id),
                                        "access_token": token
                                    }
                    except:
                        continue
        
        # Method 2: Try to discover access tokens from IGA's main site
        discovered_tokens = await _discover_access_tokens()
        if discovered_tokens:
            # Try discovered tokens with recent publication IDs
            for token in discovered_tokens:
                for offset in range(0, 5):
                    test_id = base_id + offset
                    test_url = f"https://dam.flippenterprise.net/flyerkit/publication/{test_id}/products"
                    
                    async with aiohttp.ClientSession() as session:
                        try:
                            async with session.get(test_url, params={
                                "display_type": "all",
                                "locale": "en",
                                "access_token": token
                            }, timeout=10) as response:
                                if response.status == 200:
                                    data = await response.json()
                                    if isinstance(data, list) and len(data) > 0:
                                        logger.info(f"✅ Found working combination with discovered token:")
                                        logger.info(f"   Publication ID: {test_id}")
                                        logger.info(f"   Access Token: {token[:10]}...")
                                        return {
                                            "publication_id": str(test_id),
                                            "access_token": token
                                        }
                        except:
                            continue
        
        # Method 3: Try to find publication ID from IGA's main site
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get("https://www.iga.net/en/flyer/digital_flyer", timeout=30) as response:
                    if response.status == 200:
                        content = await response.text()
                        # Look for publication ID patterns in the HTML/JS
                        id_matches = re.findall(r'publication[_-]?id["\']?\s*[:=]\s*["\']?(\d{7})["\']?', content, re.IGNORECASE)
                        if id_matches:
                            publication_id = id_matches[0]
                            logger.info(f"✅ Found publication ID in HTML: {publication_id}")
                            # Try with known tokens
                            for token in known_tokens:
                                test_url = f"https://dam.flippenterprise.net/flyerkit/publication/{publication_id}/products"
                                try:
                                    async with session.get(test_url, params={
                                        "display_type": "all",
                                        "locale": "en",
                                        "access_token": token
                                    }, timeout=10) as response:
                                        if response.status == 200:
                                            data = await response.json()
                                            if isinstance(data, list) and len(data) > 0:
                                                return {
                                                    "publication_id": publication_id,
                                                    "access_token": token
                                                }
                                except:
                                    continue
            except:
                pass
                
    except Exception as e:
        logger.debug(f"Alternative discovery error: {e}")
    
    return None


async def _discover_access_tokens() -> List[str]:
    """
    Try to discover access tokens from various sources.
    
    Returns:
        List of discovered access tokens
    """
    discovered_tokens = []
    
    try:
        # Method 1: Look for tokens in IGA's main site HTML/JS
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get("https://www.iga.net/en/flyer/digital_flyer", timeout=30) as response:
                    if response.status == 200:
                        content = await response.text()
                        
                        # Look for access token patterns
                        token_patterns = [
                            r'access_token["\']?\s*[:=]\s*["\']?([a-f0-9]{32})["\']?',
                            r'token["\']?\s*[:=]\s*["\']?([a-f0-9]{32})["\']?',
                            r'accessToken["\']?\s*[:=]\s*["\']?([a-f0-9]{32})["\']?',
                        ]
                        
                        for pattern in token_patterns:
                            matches = re.findall(pattern, content, re.IGNORECASE)
                            for match in matches:
                                if match not in discovered_tokens:
                                    discovered_tokens.append(match)
                                    logger.info(f"🔑 Discovered access token: {match[:10]}...")
            except:
                pass
        
        # Method 2: Try common token patterns (if IGA uses predictable tokens)
        # This is speculative - IGA might use patterns like:
        # - Timestamp-based tokens
        # - Sequential tokens
        # - Domain-specific tokens
        
        # Try some common patterns (this is experimental)
        base_token = "692be3f8ba9e9247dc13d064cb89e7f9"
        # Try variations of the current token
        token_variations = [
            base_token,  # Current working token
            # Add more variations as we discover patterns
        ]
        
        for token in token_variations:
            if token not in discovered_tokens:
                discovered_tokens.append(token)
                
    except Exception as e:
        logger.debug(f"Token discovery error: {e}")
    
    return discovered_tokens


def _extract_publication_id(html_content: str) -> Optional[str]:
    """
    Extract the publication ID from IGA HTML page.
    
    The publication ID is used to build the products endpoint URL.
    It's typically found in JavaScript variables or data attributes.
    """
    try:
        # Method 1: Look for publication ID in JavaScript variables
        # Common patterns: publicationId, publication_id, flyerId, etc.
        patterns = [
            r'publicationId["\']?\s*[:=]\s*["\']?(\d+)["\']?',
            r'publication_id["\']?\s*[:=]\s*["\']?(\d+)["\']?',
            r'flyerId["\']?\s*[:=]\s*["\']?(\d+)["\']?',
            r'flyer_id["\']?\s*[:=]\s*["\']?(\d+)["\']?',
            r'publication["\']?\s*[:=]\s*["\']?(\d+)["\']?',
            # Look for the specific URL pattern
            r'flyerkit/publication/(\d+)/products',
            r'/publication/(\d+)/',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            if matches:
                publication_id = matches[0]
                logger.info(f"🔍 Found publication ID using pattern '{pattern}': {publication_id}")
                return publication_id
        
        # Method 2: Look for data attributes
        data_patterns = [
            r'data-publication-id=["\'](\d+)["\']',
            r'data-flyer-id=["\'](\d+)["\']',
            r'data-publication=["\'](\d+)["\']',
        ]
        
        for pattern in data_patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            if matches:
                publication_id = matches[0]
                logger.info(f"🔍 Found publication ID in data attribute: {publication_id}")
                return publication_id
        
        # Method 3: Look for any 7-digit number (typical publication ID length)
        # This is a fallback method
        number_pattern = r'\b(\d{7})\b'
        matches = re.findall(number_pattern, html_content)
        if matches:
            # Take the first 7-digit number found
            publication_id = matches[0]
            logger.info(f"🔍 Found potential publication ID (7-digit number): {publication_id}")
            return publication_id
        
        logger.warning("⚠️ Could not find publication ID in HTML content")
        logger.debug(f"HTML content sample: {html_content[:500]}...")
        return None
        
    except Exception as e:
        logger.error(f"❌ Error extracting publication ID: {e}")
        return None


def _extract_iga_fields(item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Extract and validate relevant fields from IGA JSON item.
    
    Returns None if item is invalid or missing required fields.
    """
    try:
        # Required fields
        required_fields = ["id", "name", "sku", "valid_from", "valid_to", "price_text"]
        
        # Check if all required fields are present
        for field in required_fields:
            if field not in item or item[field] is None:
                logger.warning(f"⚠️ Missing required field '{field}' in item: {item.get('name', 'Unknown')}")
                return None
        
        # Parse dates
        valid_from = datetime.fromisoformat(item["valid_from"].replace("Z", "+00:00"))
        valid_to = datetime.fromisoformat(item["valid_to"].replace("Z", "+00:00"))
        
        # Check if deal is still valid (not expired)
        if valid_to < datetime.utcnow():
            logger.debug(f"⏰ Skipping expired deal: {item['name']} (expired {valid_to})")
            return None
        
        # Extract and clean data
        processed_item = {
            "id": int(item["id"]),
            "name": str(item["name"]).strip(),
            "sku": str(item["sku"]).strip(),
            "description": str(item.get("description", "")).strip(),
            "valid_from": valid_from,
            "valid_to": valid_to,
            "categories": item.get("categories", []),
            "price_text": str(item["price_text"]).strip(),
            "post_price_text": str(item.get("post_price_text", "")).strip(),
            "original_price": float(item["original_price"]) if item.get("original_price") else None,
            "brand": str(item.get("brand", "")).strip(),
            "web_commission_url": str(item.get("web_commission_url", "")).strip()
        }
        
        return processed_item
        
    except Exception as e:
        logger.warning(f"⚠️ Failed to process item: {e}")
        return None


@app.task(bind=True, max_retries=2, default_retry_delay=60)
def test_grocery_task_connection(self) -> Dict[str, Any]:
    """
    Test task to verify grocery task system is working.
    """
    task_id = self.request.id
    current_time = datetime.utcnow()
    
    logger.info(f"🧪 GROCERY TEST TASK: test_grocery_task_connection at {current_time}")
    
    try:
        # Test database connection
        async def _test_db():
            async with db_config.get_session_context() as session:
                result = await session.execute(text("SELECT COUNT(*) FROM grocery_deals"))
                count = result.scalar()
                return count
        
        import nest_asyncio
        nest_asyncio.apply()
        
        deal_count = asyncio.run(_test_db())
        
        result = {
            "status": "success",
            "task_id": task_id,
            "timestamp": current_time.isoformat(),
            "database_connection": "ok",
            "grocery_deals_count": deal_count
        }
        
        logger.info(f"✅ GROCERY TEST COMPLETED: {result}")
        return result
        
    except Exception as e:
        error_msg = f"❌ GROCERY TEST FAILED: {str(e)}"
        logger.error(error_msg, exc_info=True)
        
        return {
            "status": "failed",
            "task_id": task_id,
            "timestamp": current_time.isoformat(),
            "error": str(e)
        }


@app.task(bind=True, max_retries=1, default_retry_delay=120)
def cleanup_expired_grocery_deals(self) -> Dict[str, Any]:
    """
    Cleanup task to remove expired grocery deals.
    This is a safety net in case the weekly task fails.
    """
    task_id = self.request.id
    current_time = datetime.utcnow()
    
    logger.info(f"🧹 GROCERY CLEANUP: cleanup_expired_grocery_deals at {current_time}")
    
    try:
        async def _cleanup_expired():
            async with db_config.get_session_context() as session:
                # Delete deals that have expired
                result = await session.execute(
                    delete(GroceryDeal).where(GroceryDeal.valid_to < datetime.utcnow())
                )
                deleted_count = result.rowcount
                await session.commit()
                return deleted_count
        
        import nest_asyncio
        nest_asyncio.apply()
        
        deleted_count = asyncio.run(_cleanup_expired())
        
        result = {
            "status": "success",
            "task_id": task_id,
            "timestamp": current_time.isoformat(),
            "deleted_expired_deals": deleted_count
        }
        
        logger.info(f"✅ GROCERY CLEANUP COMPLETED: {result}")
        return result
        
    except Exception as e:
        error_msg = f"❌ GROCERY CLEANUP FAILED: {str(e)}"
        logger.error(error_msg, exc_info=True)
        
        return {
            "status": "failed",
            "task_id": task_id,
            "timestamp": current_time.isoformat(),
            "error": str(e)
        }
