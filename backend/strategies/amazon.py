import re
import logging
from .base import BaseScrapeStrategy
from bs4 import BeautifulSoup

logger = logging.getLogger("nexus.strategy")

class AmazonStrategy(BaseScrapeStrategy):
    def get_proxy_tier(self):
        return "datacenter"

    def execute_fetch(self, url, tier="datacenter", mimic_human=True):
        extra_headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": "https://www.google.com/",
            "Device-Memory": "8"
        }

        # Amazon US likes modern Chrome signatures
        response = self.stealth.get(url, impersonate="chrome120", tier=tier, headers=extra_headers)
        
        if response and response.status_code == 200:
            if "captcha" in response.text.lower() or "sorry" in response.url:
                logger.error(f"🛑 Amazon CAPTCHA/Block on {url}")
                return None
            return self.parse(response.text)
        
        logger.error(f"❌ Amazon Fetch Failed: {response.status_code if response else 'No Response'}")
        return None

    def parse(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        try:
            # 1. Product Title
            title_tag = soup.find(id="productTitle")
            title = title_tag.get_text().strip() if title_tag else "Unknown Product"

            # 2. Dynamic Currency Detection
            # Amazon usually puts the symbol in 'a-price-symbol'
            symbol_tag = soup.find("span", class_="a-price-symbol")
            raw_symbol = symbol_tag.get_text().strip() if symbol_tag else "$"
            
            # Map the symbol to ISO Code
            # This handles cases where Amazon detects your PH home IP
            currency_map = {
                "$": "USD",
                "₱": "PHP",
                "PHP": "PHP",
                "£": "GBP",
                "€": "EUR"
            }
            currency_code = currency_map.get(raw_symbol, "USD")

            # 3. Robust Price Extraction
            price_whole = soup.find("span", class_="a-price-whole")
            if price_whole:
                # Remove commas and non-numeric chars
                price_val = re.sub(r'[^\d]', '', price_whole.get_text())
                
                price_fraction = soup.find("span", class_="a-price-fraction")
                fraction = price_fraction.get_text().strip() if price_fraction else "00"
                
                return {
                    "title": title,
                    "price": f"{price_val}.{fraction}",
                    "currency": currency_code,
                    "detected_symbol": raw_symbol,
                    "address": "Amazon Global Store",
                    "source": "amazon_universal_v1"
                }
        except Exception as e:
            logger.warning(f"⚠️ Amazon Parse Error: {e}")
        return None

    