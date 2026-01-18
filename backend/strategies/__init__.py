from .shopee import ShopeeStrategy
from .generic import GenericStrategy

def get_strategy_for_url(url, stealth):
    if "shopee.ph" in url:
        return ShopeeStrategy(stealth)
    return GenericStrategy(stealth)