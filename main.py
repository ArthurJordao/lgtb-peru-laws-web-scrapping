#!/usr/bin/env python3
"""
Main entry point for Peru LGBT laws scraping project.

This script allows you to run scrapers for different periods:
- Current (2021+): Uses modern API endpoints
- 2016-2021: Uses 2016-2021 web portal
- 2011-2016: Uses 2011-2016 web portal
- 2006-2011: Uses 2006-2011 web portal (experimental)
"""

import argparse
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from scrapers import PeruLGBTAPIScraper, Peru2016LGBTScraper, Peru2011LGBTScraper


def main():
    """Main function to run selected scrapers"""
    parser = argparse.ArgumentParser(
        description="Scrape LGBT-related laws from Peru's Congress database",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --current              # Scrape current period (2021+)
  python main.py --historical 2016     # Scrape 2016-2021 period
  python main.py --historical 2011     # Scrape 2011-2016 period  
  python main.py --all                 # Scrape all available periods
        """,
    )

    parser.add_argument(
        "--current", action="store_true", help="Scrape current period (2021+) using API"
    )

    parser.add_argument(
        "--historical",
        choices=["2016", "2011", "2006"],
        help="Scrape specific historical period",
    )

    parser.add_argument(
        "--all", action="store_true", help="Scrape all available periods"
    )

    parser.add_argument(
        "--test", action="store_true", help="Run in test mode with limited results"
    )

    args = parser.parse_args()

    if not any([args.current, args.historical, args.all]):
        parser.print_help()
        return

    scrapers_to_run = []

    if args.current or args.all:
        scrapers_to_run.append(("Current Period (2021+)", PeruLGBTAPIScraper))

    if args.historical == "2016" or args.all:
        scrapers_to_run.append(("Historical 2016-2021", Peru2016LGBTScraper))

    if args.historical == "2011" or args.all:
        scrapers_to_run.append(("Historical 2011-2016", Peru2011LGBTScraper))

    if args.historical == "2006":
        print("⚠️  2006-2011 scraper is experimental and may have limited functionality")
        # TODO: Add Peru2006LGBTScraper when ready
        print("2006-2011 scraper not yet available in modular structure")
        return

    # Run selected scrapers
    print(f"🏳️‍🌈 Peru LGBT Laws Scraper")
    print(f"Running {len(scrapers_to_run)} scraper(s)...")
    print()

    for name, scraper_class in scrapers_to_run:
        print(f"🔍 Starting {name}...")
        print("-" * 50)

        try:
            scraper = scraper_class()
            if args.test:
                # Limit search terms for testing
                scraper.search_terms = scraper.search_terms[:5]
                print("🧪 Running in test mode (limited terms)")

            scraper.run()
            print(f"✅ {name} completed successfully")

        except Exception as e:
            print(f"❌ {name} failed: {e}")

        print()

    print("🎉 All scrapers completed!")
    print("📁 Results saved in data/exports/ directory")


if __name__ == "__main__":
    main()
