from .shopee import ShopeeStrategy
from .amazon import AmazonStrategy

def get_strategy_for_url(url, stealth):
    url_lower = url.lower()
    
    if "shopee.ph" in url_lower:
        return ShopeeStrategy(stealth)
    
    if "amazon.com" in url_lower:
        return AmazonStrategy(stealth)
    
    raise ValueError(f"No strategy available for: {url}")