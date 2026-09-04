import re
from playwright.async_api import Page
from types_def import SearchQuery
from popup import PopupHandler
from logger import Logger
from utils.human_behavior import HumanBehavior

class SearchService:
    async def execute_search(self, page: Page, query: SearchQuery, base_url: str) -> None:
        formatted_location = re.sub(r'\s+', '-', query['location'].strip())
        
        category = query['category'].strip()
        category_lower = category.lower()
        if not category_lower.endswith('s'):
            if category_lower.endswith('y'):
                plural_category = category[:-1] + 'ies'
            else:
                plural_category = category + 's'
        else:
            plural_category = category

        formatted_category = re.sub(r'\s+', '-', plural_category)
        results_url = f"{base_url.rstrip('/')}/{formatted_location}/{formatted_category}"

        Logger.info(f"Opening Justdial results page directly: {results_url}")
        try:
            await page.goto(results_url, wait_until='commit')
            try:
                await page.wait_for_load_state('domcontentloaded', timeout=10000)
            except Exception:
                pass
            try:
                await page.wait_for_load_state('load', timeout=10000)
            except Exception:
                pass
        except Exception as error:
            raise Exception(f"Failed to navigate to results URL ({results_url}): {error}")

        # 2. Handling browser permissions...
        Logger.info('Handling browser permissions...')

        # 3. Handling website popups...
        Logger.info('Handling website popups...')
        await PopupHandler.close_modals_explicitly(page)

        # Simulate user cognitive thinking time after page load/popup handling
        await HumanBehavior.think(page)

        # 4. Wait and Verify search completed successfully
        result_selectors = [
            '.resultbox_info',
            '[class*="resultbox_info"]',
            '.resultbox',
            '[class*="resultbox"]',
            '.jdresult_box',
            '[class*="jdresult"]',
            'div[class*="card"]'
        ]

        results_locator = page.locator(', '.join(result_selectors)).first
        try:
            Logger.info('Waiting for search results page to load...')
            await HumanBehavior.short_pause(page)

            # Check if Justdial "Unable to load data" message is visible, and try to recover
            try_again_btn = page.locator('button:has-text("Try again"), button:has-text("try again"), .error_retry_btn').first
            if await try_again_btn.is_visible():
                Logger.warning("Justdial load error page detected. Clicking 'Try again'...")
                await try_again_btn.click()
                await page.wait_for_timeout(3000)

            # Wait for results to become visible
            await results_locator.wait_for(state='visible', timeout=20000)

            # Verify if it failed to load or got stuck on "Unable to load data" even if secondary items matched
            try_again_btn = page.locator('button:has-text("Try again"), button:has-text("try again"), .error_retry_btn').first
            if await try_again_btn.is_visible():
                Logger.warning("Still stuck on error page. Reloading the page...")
                await page.reload(wait_until='commit')
                try:
                    await page.wait_for_load_state('domcontentloaded', timeout=10000)
                except Exception:
                    pass
                try:
                    await page.wait_for_load_state('load', timeout=10000)
                except Exception:
                    pass
                await HumanBehavior.medium_pause(page)
                
                # Check try again button one more time after reload
                try_again_btn = page.locator('button:has-text("Try again"), button:has-text("try again"), .error_retry_btn').first
                if await try_again_btn.is_visible():
                    Logger.warning("Clicking 'Try again' after reload...")
                    await try_again_btn.click()
                    await page.wait_for_timeout(3000)

            # Re-verify results are visible
            await results_locator.wait_for(state='visible', timeout=15000)

            # Wait for shimmer/skeleton loading states to disappear
            shimmer = page.locator('.shimmerblock, .shimmerwrap, .jdwrapper.shimmerwrap').first
            try:
                if await shimmer.is_visible():
                    Logger.info('Shimmer skeletons detected. Waiting for content to load...')
                    await shimmer.wait_for(state='hidden', timeout=15000)
            except Exception:
                # Non-blocking fallback
                pass

            # Allow final hydration/rendering of the lists
            await HumanBehavior.medium_pause(page)
            Logger.success('Search results page loaded and rendered successfully.')
        except Exception as err:
            raise Exception(f"Verification Failure: Justdial listings failed to load. URL: \"{page.url}\". Error: {err}")

