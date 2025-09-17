#!/usr/bin/env python3
"""
Main entry point for Peru LGBT laws scraping project.

This script allows you to run scrapers for different periods:
- Current (2021+): Uses modern API endpoints
- 2016-2021: Uses 2016-2021 web portal
- 2011-2016: Uses 2011-2016 web portal
- 2006-2011: Uses 2006-2011 web portal
- 2001-2006: Uses 2001-2006 web portal
- 1995-2001: Uses 1995-2001 web portal
"""

import argparse
from scrapers import (
    Peru2021LGBTScraper,
    Peru2016LGBTScraper,
    Peru2011LGBTScraper,
    Peru2006LGBTScraper,
    Peru2001LGBTScraper,
    Peru2000LGBTScraper,
)


def main():
    """Main function to run selected scrapers"""
    parser = argparse.ArgumentParser(
        description="Scrape LGBT-related laws from Peru's Congress database",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  uv run python main.py --current              # Scrape 2021+ period
  uv run python main.py --period 2016         # Scrape 2016-2021 period
  uv run python main.py --period 2011         # Scrape 2011-2016 period
  uv run python main.py --period 2006         # Scrape 2006-2011 period
  uv run python main.py --period 2001         # Scrape 2001-2006 period
  uv run python main.py --period 2000         # Scrape 2000-2001 period
  uv run python main.py --all                 # Scrape all periods
        """,
    )

    parser.add_argument(
        "--current", action="store_true", help="Scrape 2021+ period using API"
    )

    parser.add_argument(
        "--period",
        choices=["2016", "2011", "2006", "2001", "2000"],
        help="Scrape specific period",
    )

    parser.add_argument("--all", action="store_true", help="Scrape all periods")

    parser.add_argument(
        "--test", action="store_true", help="Run in test mode with limited results"
    )

    args = parser.parse_args()

    if not any([args.current, args.period, args.all]):
        parser.print_help()
        return

    scrapers_to_run = []

    if args.current or args.all:
        scrapers_to_run.append(("Current Period (2021+)", Peru2021LGBTScraper))

    if args.period == "2016" or args.all:
        scrapers_to_run.append(("Historical 2016-2021", Peru2016LGBTScraper))

    if args.period == "2011" or args.all:
        scrapers_to_run.append(("Historical 2011-2016", Peru2011LGBTScraper))

    if args.period == "2006" or args.all:
        scrapers_to_run.append(("Historical 2006-2011", Peru2006LGBTScraper))

    if args.period == "2001" or args.all:
        scrapers_to_run.append(("Historical 2001-2006", Peru2001LGBTScraper))

    if args.period == "2000" or args.all:
        scrapers_to_run.append(("Historical 2000-2001", Peru2000LGBTScraper))

    # Run selected scrapers
    print("🏳️‍🌈 Peru LGBT Laws Scraper")
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
