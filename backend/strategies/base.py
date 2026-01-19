from abc import ABC, abstractmethod
from bs4 import BeautifulSoup

class BaseScrapeStrategy(ABC):
    def __init__(self, stealth_engine):
        self.stealth = stealth_engine

    @abstractmethod
    def parse(self, html_content):
        """Must return a dict compatible with your Pydantic models"""
        pass

    def get_proxy_tier(self):
        """Default to Datacenter (Tier 1). Override for harder sites."""
        return "datacenter"

    def execute_fetch(self, url):
        """Wraps the stealth fetch with logic for this specific site"""
        return self.stealth.fetch_sync(url)