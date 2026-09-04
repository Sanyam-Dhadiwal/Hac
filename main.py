import sys
import asyncio
import argparse
from config import config
from browser import BrowserManager
from search import SearchService
from services.infinite_scroller import InfiniteScroller
from listing_collector import ListingCollector
from parser import BusinessParser
from csv_exporter import CsvExporter
from logger import Logger

async def run_scraper(category: str, location: str, headed: bool):
    # Resolve headless mode: command-line flag --headed takes precedence over env config
    run_config = config.copy()
    if headed:
        run_config['headless'] = False

    browser_manager = BrowserManager()
    search_service = SearchService()
    infinite_scroller = InfiniteScroller()
    collector = ListingCollector()

    try:
        Logger.info('Launching browser...')
        page = await browser_manager.init(run_config)

        await search_service.execute_search(page, {'category': category, 'location': location}, run_config['baseUrl'])

        Logger.info('Results loaded successfully.')

        # Load all available listings via infinite scrolling before extracting/inspecting
        await infinite_scroller.load_all_listings(page)

        # Locate, filter, count, and print listing cards
        cards = await collector.collect_and_print(page)

        parser = BusinessParser()
        businesses = []
        for i, card in enumerate(cards):
            try:
                # Scroll card into view to trigger lazy loading / hydration of details
                try:
                    await card.scroll_into_view_if_needed()
                except Exception:
                    pass
                await page.wait_for_timeout(50)

                business = await parser.parse(card)
                businesses.append(business)

                if (i + 1) % 10 == 0 or i == len(cards) - 1:
                    Logger.info(f"Parsed {i + 1}/{len(cards)} listings...")
            except Exception as err:
                Logger.warning(f"Error parsing card {i + 1}: {err}")
                if "Target page, context or browser has been closed" in str(err) or "page closed" in str(err).lower():
                    Logger.error("Browser closed/crashed during parsing loop. Saving parsed data so far...")
                    break

        # Export to CSV
        exporter = CsvExporter()
        csv_path = await exporter.export(businesses)
        Logger.success(f"CSV file created at: {csv_path}")

        return businesses

    except Exception as error:
        Logger.error(f"Scraper execution failed: {error}")
        sys.exit(1)
    finally:
        await browser_manager.close()

def main():
    arg_parser = argparse.ArgumentParser(
        prog='justdial-scraper',
        description='CLI to open Justdial and search using Category and Location.'
    )
    arg_parser.add_argument('-c', '--category', required=True, help='Category to search (e.g. "Photographer")')
    arg_parser.add_argument('-l', '--location', required=True, help='Location to search in (e.g. "Pune")')
    arg_parser.add_argument('--headed', action='store_true', help='Run browser in headed mode (visible GUI)')

    args = arg_parser.parse_args()

    category = args.category.strip()
    location = args.location.strip()

    # Input Validation
    if not category:
        Logger.error('Validation Error: Category cannot be empty.')
        sys.exit(1)
    if not location:
        Logger.error('Validation Error: Location cannot be empty.')
        sys.exit(1)

    # Execute Scraper Asynchronously
    asyncio.run(run_scraper(category, location, args.headed))

if __name__ == "__main__":
    main()
