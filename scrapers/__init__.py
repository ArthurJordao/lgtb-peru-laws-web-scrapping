"""
Peru LGBT Laws Scrapers

A collection of web scrapers for extracting LGBT-related legislation
from Peru's Congress database across different historical periods.
"""

__version__ = "1.0.0"
__author__ = "LGBT Peru Law Research Project"

from .current.api_scraper import PeruLGBTAPIScraper
from .historical.scraper_2016 import Peru2016LGBTScraper
from .historical.scraper_2011 import Peru2011LGBTScraper

__all__ = ["PeruLGBTAPIScraper", "Peru2016LGBTScraper", "Peru2011LGBTScraper"]
