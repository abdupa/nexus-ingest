from .shopee import ShopeeStrategy
from .amazon import AmazonStrategy

def get_strategy_for_url(url, stealth):
    """
    The Strategy Factory: Automatically routes the URL to the correct profile.
    """
    url_lower = url.lower()
    
    if "shopee.ph" in url_lower:
        return ShopeeStrategy(stealth)
    
    if "amazon.com" in url_lower:
        return AmazonStrategy(stealth)
    
    # Logic for future tenants
    raise ValueError(f"Domain not supported: {url}")