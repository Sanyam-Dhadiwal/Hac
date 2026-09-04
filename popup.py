import asyncio
from playwright.async_api import Page
from logger import Logger

CLOSE_SELECTORS = [
    '.maybelater a',
    'a.login_anchor',
    '[aria-label="May be later"]',
    '.cl-btn',
    '.close-modal',
    '.modal-close',
    '.close-popup',
    '.modal span.close',
    '.jd_modal span.close',
    '#loginPop span.close',
    '.modal button.close',
    '.jd_modal button.close',
    '#loginPop button.close',
    '.modal .close_icon',
    '.jd_modal .close_icon',
    '#loginPop .close_icon',
    '.loginPop .close_icon',
    '.modal #close_icon',
    '.jd_modal #close_icon',
    '#loginPop #close_icon',
    '.modal [class*="close_modal"]',
    '.modal [class*="close-modal"]',
    '.jd_modal [class*="close_modal"]',
    '.jd_modal [class*="close-modal"]',
    '#loginPop [class*="close_modal"]',
    '#loginPop [class*="close-modal"]',
    '.modal [class*="close"]',
    '.popup [class*="close"]',
    '.jd_modal [class*="close"]',
    '[class*="modal"] [class*="close"]',
    '[class*="popup"] [class*="close"]',
    '[class*="modal"] .close',
    '[class*="popup"] .close',
    '[class*="modal"] .dnx',
    '[class*="popup"] [class*="dnx"]'
]

class PopupHandler:
    @staticmethod
    def start_modal_watcher(page: Page) -> None:
        Logger.info('PopupHandler: Starting background modal close watcher...')

        async def watcher_loop():
            while not page.is_closed():
                try:
                    for selector in CLOSE_SELECTORS:
                        close_btn = page.locator(selector).first
                        if await close_btn.is_visible():
                            Logger.warning(f'PopupHandler: Detected visible modal close button ("{selector}"). Waiting 1.5s lag...')
                            await page.wait_for_timeout(1500)
                            
                            if await close_btn.is_visible():
                                await close_btn.click(force=True, timeout=2000)
                                Logger.success('PopupHandler: Modal successfully closed.')
                            break
                except Exception as error:
                    # Silent catch in case locator resolves to an element that detaches mid-execution
                    Logger.debug(f'PopupHandler background loop error: {error}')

                # Poll every 1.5 seconds to avoid CPU spin locks
                try:
                    if page.is_closed():
                        break
                    await page.wait_for_timeout(1500)
                except Exception:
                    break
            Logger.info('PopupHandler: Modal watcher terminated (page closed).')

        # Run background watcher coroutine on the current event loop
        asyncio.create_task(watcher_loop())

    @staticmethod
    async def audit_and_diagnose_login_modal(page: Page) -> None:
        modal_selectors = ['#login-modal', 'section#loginPop', '.loginPop', '.jd_modal.loginPop']
        visible_modal_selector = None

        for sel in modal_selectors:
            try:
                modal = page.locator(sel).first
                if await modal.is_visible():
                    visible_modal_selector = sel
                    break
            except Exception:
                pass

        if not visible_modal_selector:
            return

        Logger.warning(f'PopupHandler: Detected login modal via selector "{visible_modal_selector}"')

        # Find potential close buttons inside the visible modal
        close_btn_selectors = [
            '.maybelater a',
            'a.login_anchor',
            '[aria-label="May be later"]',
            'span.jd_modal_close',
            '.jd_modal_close',
            '.close_icon',
            '#close_icon',
            'span.close',
            'button.close',
            'a.close',
            '.close',
            '[class*="close"]'
        ]

        modal_locator = page.locator(visible_modal_selector).first
        clicked = False

        for close_sel in close_btn_selectors:
            try:
                close_btn = modal_locator.locator(close_sel).first
                if await close_btn.is_visible():
                    Logger.info(f'PopupHandler: Found close button inside modal: "{close_sel}". Waiting 1.5s lag...')
                    await page.wait_for_timeout(1500)
                    
                    if await close_btn.is_visible():
                        await close_btn.click(timeout=4000)
                        Logger.success(f'PopupHandler: Clicked close button "{close_sel}" successfully.')
                    clicked = True
                    break
            except Exception as err:
                Logger.warning(f'PopupHandler: Click attempt failed on close button "{close_sel}": {err}')

        # Wait a brief moment to see if it closed
        await page.wait_for_timeout(1000)

        is_still_visible = await modal_locator.is_visible()
        if is_still_visible:
            raise Exception('PopupHandler: Justdial login modal intercepts pointer events and cannot be closed.')

    @classmethod
    async def close_modals_explicitly(cls, page: Page) -> None:
        Logger.info('PopupHandler: Explicitly auditing page for visible overlays/modals...')
        
        # 1. Audit and diagnose login modal first
        await cls.audit_and_diagnose_login_modal(page)

        # 2. Perform fallback checks on other modals
        for selector in CLOSE_SELECTORS:
            try:
                close_btn = page.locator(selector).first
                if await close_btn.is_visible():
                    Logger.warning(f'PopupHandler: Explicitly closing active modal via selector: "{selector}". Waiting 1.5s lag...')
                    await page.wait_for_timeout(1500)
                    
                    if await close_btn.is_visible():
                        await close_btn.click(force=True, timeout=3000)
                        Logger.success('PopupHandler: Modal overlay closed successfully.')
                    break
            except Exception as error:
                Logger.debug(f'PopupHandler: Non-blocking error checking selector "{selector}": {error}')
