import random
from playwright.async_api import Page
from utils.human_behavior import HumanBehavior
from logger import Logger

MAX_RETRIES = 3
MIN_WAIT_AFTER_SCROLL = 1500  # ms
MAX_WAIT_AFTER_SCROLL = 3000  # ms
MIN_CARDS_INCREASE_EXPECTED = 1
MAX_SCROLL_ITERATIONS = 50

class InfiniteScroller:
    def __init__(self):
        self.card_selectors = [
            '.resultbox_info',
            '[class*="resultbox_info"]',
            '.resultbox',
            '[class*="resultbox"]',
            '.jdresult_box',
            '[class*="jdresult"]',
            'div[class*="card"]'
        ]
        self.active_selector = '.resultbox_info'

    async def _random_wait(self, page: Page, min_val: int, max_val: int) -> None:
        ms = random.randint(min_val, max_val)
        await page.wait_for_timeout(ms)

    async def get_card_count(self, page: Page) -> int:
        for selector in self.card_selectors:
            count = await page.locator(selector).count()
            if count > 0:
                self.active_selector = selector
                return count
        return 0

    async def load_all_listings(self, page: Page) -> int:
        Logger.info('InfiniteScroller: Initializing Infinite Scrolling Engine...')

        combined_selector = ', '.join(self.card_selectors)
        try:
            await page.locator(combined_selector).first.wait_for(state='visible', timeout=15000)
            Logger.success('InfiniteScroller: Detected initial listing card(s).')
        except Exception as err:
            Logger.warning(f"InfiniteScroller: Timeout waiting for first listing card to become visible: {err}")

        current_cards_count = await self.get_card_count(page)
        Logger.info(f"[INFO] Visible cards (using '{self.active_selector}'): {current_cards_count}")

        iterations = 0
        retries = 0

        try:
            while iterations < MAX_SCROLL_ITERATIONS:
                iterations += 1
                Logger.info("[INFO] Scrolling...")

                viewport = page.viewport_size
                base_distance = viewport['height'] if viewport else 800
                scroll_distance = int(base_distance * (0.8 + random.random() * 0.4))

                await HumanBehavior.smooth_scroll(page, scroll_distance)

                await self._random_wait(page, MIN_WAIT_AFTER_SCROLL, MAX_WAIT_AFTER_SCROLL)

                new_cards_count = await self.get_card_count(page)
                increase = new_cards_count - current_cards_count

                if increase >= MIN_CARDS_INCREASE_EXPECTED:
                    Logger.success(f"[SUCCESS] Loaded {increase} new cards ({new_cards_count} total)")
                    current_cards_count = new_cards_count
                    retries = 0
                else:
                    Logger.info("[INFO] No additional cards detected")
                    if retries < MAX_RETRIES:
                        retries += 1
                        Logger.info(f"[INFO] Retry {retries}/{MAX_RETRIES}")

                        await HumanBehavior.smooth_scroll(page, -150)
                        await self._random_wait(page, 500, 1000)
                        await HumanBehavior.smooth_scroll(page, int(scroll_distance * 1.3))
                    else:
                        Logger.success("[SUCCESS] Infinite scrolling complete")
                        break

            if iterations >= MAX_SCROLL_ITERATIONS:
                Logger.warning(f"InfiniteScroller: Reached safety limit of {MAX_SCROLL_ITERATIONS} iterations.")

        except Exception as error:
            Logger.error(f"InfiniteScroller: Error occurred during infinite scroll: {error}")
            if page.is_closed():
                raise Exception("Browser page was closed prematurely.") from error

        final_count = current_cards_count
        try:
            if not page.is_closed():
                final_count = await self.get_card_count(page)
        except Exception:
            pass
        Logger.info(f"Final cards loaded: {final_count}")
        return final_count
