import re
from typing import Optional
from playwright.async_api import Locator
from types_def import Business

class BusinessParser:
    parse_count = 0

    async def parse(self, card: Locator) -> Business:
        BusinessParser.parse_count += 1

        name = await self.get_name(card)
        rating = await self.get_rating(card)
        reviews = await self.get_reviews(card)
        address = await self.get_address(card)
        phone = await self.get_phone(card)
        website = await self.get_website(card)
        verified = await self.is_verified(card)

        return {
            "name": name,
            "rating": rating,
            "reviews": reviews,
            "address": address,
            "phone": phone,
            "website": website,
            "verified": verified
        }

    async def get_name(self, card: Locator) -> str:
        selectors = [
            '.resultbox_title_anchor',
            '.resultbox_title',
            '[class*="resultbox_title"]',
            '.store-name',
            '.company-name',
            'h2',
            'h3',
            'h4',
            'a[href*="justdial.com"]'
        ]
        for selector in selectors:
            try:
                el = card.locator(selector).first
                if await el.is_visible():
                    text = (await el.inner_text()).strip()
                    if text:
                        return text
            except Exception:
                pass

        # Fallback: try finding first visible anchor link inside the card
        try:
            first_link = card.locator('a').first
            if await first_link.is_visible():
                text = (await first_link.inner_text()).strip()
                if text:
                    return text
        except Exception:
            pass

        return 'Unknown Business'

    async def get_rating(self, card: Locator) -> Optional[str]:
        selectors = [
            '.resultbox_totalrate',
            '.newratingval',
            '.green-box',
            '.rtg_txt',
            '[data-testid="rating-value"]',
            '.rating-value',
            '.rating'
        ]
        for selector in selectors:
            try:
                el = card.locator(selector).first
                if await el.is_visible():
                    text = (await el.inner_text()).strip()
                    if text:
                        return text
            except Exception:
                pass
        return None

    async def get_reviews(self, card: Locator) -> Optional[str]:
        selectors = [
            '.rating-count',
            '.reviews',
            '.votes',
            '[data-testid="rating-count"]',
            '.lng_vote',
            '.rtg_txt'
        ]
        for selector in selectors:
            try:
                el = card.locator(selector).first
                if await el.is_visible():
                    text = await el.inner_text()
                    cleaned_text = text.replace(',', '')
                    match = re.search(r'\d+', cleaned_text)
                    if match:
                        return match.group(0)
            except Exception:
                pass
        return None

    async def get_address(self, card: Locator) -> Optional[str]:
        selectors = [
            '.resultbox_address',
            '.cont_add',
            '.address-info',
            '[data-testid="address"]',
            '.cont_fl_addr',
            '.address',
            '.store-address'
        ]
        for selector in selectors:
            try:
                el = card.locator(selector).first
                if await el.is_visible():
                    text = (await el.inner_text()).strip()
                    if text:
                        return text
            except Exception:
                pass
        return None

    async def get_phone(self, card: Locator) -> Optional[str]:
        try:
            tel_link = card.locator('a[href^="tel:"]').first
            if await tel_link.is_visible():
                href = await tel_link.get_attribute('href')
                if href:
                    num = href.replace('tel:', '').strip()
                    if num:
                        return num
        except Exception:
            pass

        selectors = [
            '.contact-info',
            '.phone',
            '.mob-no',
            '[data-testid="contact-number"]',
            '.tel-num',
            '.contact-number',
            '.callbutton',
            'a[href*="tel"]'
        ]
        for selector in selectors:
            try:
                el = card.locator(selector).first
                if await el.is_visible():
                    text = (await el.inner_text()).strip()
                    href = await el.get_attribute('href')
                    
                    if text:
                        return text
                    if href and href.startswith('tel:'):
                        num = href.replace('tel:', '').strip()
                        if num:
                            return num
            except Exception:
                pass
        return None

    async def get_website(self, card: Locator) -> Optional[str]:
        selectors = [
            'a.website-link',
            'a[href*="website"]',
            '[data-testid="website-link"]',
            'a:has-text("Website")',
            'a[href^="http"]:not([href*="justdial.com"])'
        ]
        for selector in selectors:
            try:
                el = card.locator(selector).first
                if await el.is_visible():
                    href = await el.get_attribute('href')
                    if href and 'justdial.com' not in href:
                        return href.strip()
            except Exception:
                pass
        return None

    async def is_verified(self, card: Locator) -> bool:
        selectors = [
            '.results_jdverified',
            '.results_jdtrusted',
            '.verified',
            '.trusted',
            '[class*="verified"]',
            '[class*="trusted"]',
            'img[src*="verified"]',
            'img[src*="trusted"]'
        ]
        for selector in selectors:
            try:
                el = card.locator(selector).first
                if await el.is_visible():
                    return True
            except Exception:
                pass
        return False
