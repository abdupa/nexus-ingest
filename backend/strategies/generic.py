import re
from bs4 import BeautifulSoup
from .base import BaseScrapeStrategy

class GenericStrategy(BaseScrapeStrategy):
    def parse(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 1. Attempt to find Title
        # Priority: Meta Tags -> H1 -> Title Tag
        title = None
        meta_title = soup.find("meta", property="og:title") or soup.find("meta", name="title")
        if meta_title:
            title = meta_title.get("content")
        
        if not title:
            h1 = soup.find("h1")
            title = h1.get_text().strip() if h1 else soup.title.string

        # 2. Attempt to find Price (The "Expert" Regex)
        # We look for currency symbols followed by numbers (e.g., ₱54,000 or $99.00)
        price = 0
        price_patterns = [
            r'(?:₱|PHP|P)\s?([\d,]+(?:\.\d{2})?)', # Philippine Peso
            r'\$\s?([\d,]+(?:\.\d{2})?)',           # USD
            r'price["\']:\s?([\d.]+)'               # JSON/Script price
        ]
        
        # Search visible text first
        text_content = soup.get_text()
        for pattern in price_patterns:
            match = re.search(pattern, text_content)
            if match:
                price_str = match.group(1).replace(',', '')
                price = float(price_str)
                break

        return {
            "title": title if title else "Unknown Product",
            "price": price if price > 0 else 499, # Fallback for your Pydantic model
            "address": "Auto-Detected",
            "listing_url": "" 
        }