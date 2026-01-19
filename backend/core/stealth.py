# backend/core/stealth.py
import os  # <--- THE MISSING PIECE
from curl_cffi import requests
import random
import logging

logger = logging.getLogger("nexus.stealth")

class StealthEngine:
    def __init__(self):
        self.browser_profiles = ["chrome110", "chrome120", "safari15_5"]
        
        # 1. Load from .env first
        env_proxies = os.getenv("DATACENTER_PROXY_LIST")
        if env_proxies:
            self.datacenter_pool = env_proxies.split(",")
        else:
            # 2. Failsafe (Hardcoded)
            self.datacenter_pool = [
                "http://66622:KUTZdUP5F@192.126.176.227:8800",
                "http://66622:KUTZdUP5F@108.62.70.11:8800"
                # ... rest of your ips
            ]
        
    def _get_config(self, proxy_url=None):
        return {
            "impersonate": random.choice(self.browser_profiles),
            "proxies": {"http": proxy_url, "https": proxy_url} if proxy_url else None,
            "timeout": 30,
            "verify": True
        }

    def get(self, url, tier="datacenter", **kwargs):
        """
        Handles proxy tiering with fallbacks for local development.
        """
        # Logic to pick the right proxy with an empty string fallback
        if tier == "residential":
            proxy_url = os.getenv("RESIDENTIAL_PROXY_URL")
        else:
            proxy_url = random.choice(self.datacenter_pool)
        
        # LOGGING: Vital for debugging your home IP vs Proxy
        if not proxy_url:
            logger.info(f"🌐 No {tier} proxy set. Attempting direct connection via local IP.")
        else:
            logger.info(f"🛡️ Using {tier} proxy: {proxy_url[:15]}...")

        config = self._get_config(proxy_url)
        config.update(kwargs)
        
        try:
            response = requests.get(url, **config)
            return response
        except Exception as e:
            logger.error(f"📡 Connection Failure (Tier: {tier}): {url} | Error: {e}")
            return None
        
    def _get_config(self, proxy_url=None):
        # 1. Sync the Profile and the User-Agent
        # This is the "Golden Rule" of Stealth: TLS Fingerprint must match UA
        profile = random.choice(self.browser_profiles) # e.g., "safari_ios"
        
        headers = {
            "Referer": "https://shopee.ph/",
            "Origin": "https://shopee.ph",
            "Accept": "application/json",
            "Accept-Language": "en-US,en;q=0.9,fil;q=0.8", # Essential for PH Geo-Targeting
            "X-Shopee-Language": "en",
            "X-Requested-With": "XMLHttpRequest",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        }
        
        return {
            "impersonate": profile,
            "proxies": {"http": proxy_url, "https": proxy_url} if proxy_url else None,
            "headers": headers,
            "timeout": 30,
            "verify": True
        }

# 1. Ensure the class is defined above
# 2. CREATE THE INSTANCE HERE
stealth_engine = StealthEngine()