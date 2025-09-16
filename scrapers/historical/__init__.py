"""
Historical period scrapers for Peru LGBT laws

Covers different historical periods using legacy web interfaces:
- 2016-2021: Uses 2016-2021 portal
- 2011-2016: Uses 2011-2016 portal
- 2006-2011: Uses 2006-2011 portal (Lotus Notes system)
"""

from .scraper_2016 import Peru2016LGBTScraper
from .scraper_2011 import Peru2011LGBTScraper

__all__ = ["Peru2016LGBTScraper", "Peru2011LGBTScraper"]
