from typing import List
from playwright.async_api import Page, Locator
from logger import Logger
from utils.human_behavior import HumanBehavior

class ListingCollector:
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

    async def collect_and_print(self, page: Page) -> List[Locator]:
        Logger.info('ListingCollector: Analyzing page for business cards...')

        combined_selector = ', '.join(self.card_selectors)
        first_card = page.locator(combined_selector).first
        try:
            await first_card.wait_for(state='visible', timeout=15000)
            Logger.success('ListingCollector: Listing cards are visible.')
        except Exception as err:
            Logger.warning(f"ListingCollector: Timeout waiting for listing cards to become visible: {err}")

        # Analyze DOM hierarchy dynamically to identify card containers and parent chains
        active_selector = await page.evaluate(
            """function(selectors) {
                for (const sel of selectors) {
                    if (document.querySelectorAll(sel).length > 0) {
                        return sel;
                    }
                }
                return '.resultbox_info'; // Fallback
            }""",
            self.card_selectors
        )

        Logger.info(f"ListingCollector: Active selector detected is '{active_selector}'")

        return await page.locator(active_selector).all()
