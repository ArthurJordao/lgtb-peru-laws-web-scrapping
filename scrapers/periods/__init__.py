"""
Period-based scrapers for Peru LGBT laws

Each scraper covers a specific legislative period:
- 2021+: Modern API-based scraper for current period
- 2016-2021: Web scraper for 2016-2021 period
- 2011-2016: Web scraper for 2011-2016 period
- 2006-2011: Experimental web scraper for 2006-2011 period
"""

from .scraper_2021 import Peru2021LGBTScraper
from .scraper_2016 import Peru2016LGBTScraper
from .scraper_2011 import Peru2011LGBTScraper

__all__ = ["Peru2021LGBTScraper", "Peru2016LGBTScraper", "Peru2011LGBTScraper"]
