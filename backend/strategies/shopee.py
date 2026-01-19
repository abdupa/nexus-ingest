import re
import json
import logging
from .base import BaseScrapeStrategy
from bs4 import BeautifulSoup

logger = logging.getLogger("nexus.strategy")

class ShopeeStrategy(BaseScrapeStrategy):
    def get_proxy_tier(self):
        return "residential"

    # Update the signature to accept the new arguments from the Universal Worker
    def execute_fetch(self, url, tier="datacenter", mimic_human=True):
        """
        Phase 2 Strategy: Try Mobile API first with Tiered Proxy escalation.
        """
        # 1. EXTRACT IDs
        id_match = re.search(r'i\.(\d+)\.(\d+)', url)
        
        if id_match:
            shop_id, item_id = id_match.groups()
            api_url = f"https://shopee.ph/api/v4/item/get?itemid={item_id}&shopid={shop_id}"
            
            logger.info(f"🎯 Targeting Mobile API (Tier: {tier}): {api_url}")
            
            # Now we actually use the 'tier' argument here
            response = self.stealth.get(api_url, impersonate="safari_ios", tier=tier)
            
            if response and response.status_code == 200:
                try:
                    data = response.json().get("data")
                    if data and data.get("price"):
                        price = str(int(data["price"]) // 100000)
                        logger.info(f"✅ API SUCCESS: Found Price {price}")
                        return {
                            "title": data.get("name"),
                            "price": price,
                            "currency": "PHP",
                            "address": "Shopee Philippines",
                            "source": f"mobile_api_{tier}"
                        }
                except Exception as e:
                    logger.warning(f"⚠️ API Parse Failed: {e}. Falling back to Web.")

        # 2. FALLBACK to Standard Web Parse
        response = self.stealth.get(url, tier=tier)
        if response and response.status_code == 200:
            return self.parse(response.text)
        
        return None

    # THIS NAME IS MANDATORY TO AVOID THE TYPEERROR
    def parse(self, html_content):
        """
        Hardened Web Extraction Waterfall (Regex -> JSON-LD -> Meta)
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # --- STAGE 0: GREEDY REGEX ---
        price_patterns = [
            r'"price":\s*(\d{9,12})',
            r'item_price":\s*(\d{9,12})',
            r'"price_min":\s*(\d{9,12})'
        ]
        
        found_price = None
        for pattern in price_patterns:
            match = re.search(pattern, html_content)
            if match:
                found_price = str(int(match.group(1)) // 100000)
                break

        name_match = re.search(r'"name":\s*"(.*?)"', html_content)
        
        if found_price and name_match:
            try:
                return {
                    "title": name_match.group(1).encode().decode('unicode_escape'),
                    "price": found_price,
                    "currency": "PHP",
                    "address": "Shopee Philippines"
                }
            except Exception:
                pass 

        # --- STAGE 1: JSON-LD ---
        scripts = soup.find_all('script', type='application/ld+json')
        for script in scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, list): data = data[0]
                if 'offers' in data or data.get('@type') == 'Product':
                    return {
                        "title": data.get("name"),
                        "price": str(data.get("offers", {}).get("price", "0")),
                        "currency": data.get("offers", {}).get("priceCurrency", "PHP"),
                        "address": "Shopee Philippines"
                    }
            except:
                continue 

        # --- STAGE 2: META TAGS ---
        try:
            title_meta = soup.find("meta", property="og:title")
            price_meta = soup.find("meta", property="product:price:amount")
            if title_meta:
                return {
                    "title": title_meta["content"],
                    "price": price_meta["content"] if price_meta else "0",
                    "currency": "PHP",
                    "address": "Shopee Philippines"
                }
        except Exception:
            pass

        return None 