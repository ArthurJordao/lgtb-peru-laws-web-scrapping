"""
Peru LGBT Laws Scrapers

A collection of web scrapers for extracting LGBT-related legislation
from Peru's Congress database across different legislative periods.
"""

__version__ = "1.0.0"
__author__ = "LGBT Peru Law Research Project"

from .periods.scraper_2021 import Peru2021LGBTScraper
from .periods.scraper_2016 import Peru2016LGBTScraper
from .periods.scraper_2011 import Peru2011LGBTScraper

__all__ = ["Peru2021LGBTScraper", "Peru2016LGBTScraper", "Peru2011LGBTScraper"]
