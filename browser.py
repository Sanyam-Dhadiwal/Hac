from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from popup import PopupHandler
from logger import Logger

class BrowserManager:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None

    async def init(self, config_dict) -> Page:
        Logger.info(f"Launching browser (headless: {config_dict['headless']})...")

        launch_args = [
            '--disable-blink-features=AutomationControlled'
        ]

        self.playwright = await async_playwright().start()
        
        self.browser = await self.playwright.chromium.launch(
            headless=config_dict['headless'],
            args=launch_args
        )

        Logger.info('Creating browser context...')

        self.context = await self.browser.new_context(
            viewport={'width': 1280, 'height': 800},
            device_scale_factor=1
        )

        # Inject evasion script before any page content loads
        await self.context.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', { get: () => undefined })"
        )

        page = await self.context.new_page()

        # Intercept and block heavy media assets to optimize memory usage
        async def block_resources(route):
            if route.request.resource_type in ["image", "media"]:
                try:
                    await route.abort()
                except Exception:
                    pass
            else:
                try:
                    await route.continue_()
                except Exception:
                    pass

        await page.route("**/*", block_resources)

        # Gracefully handle browser dialog prompts
        async def on_dialog(dialog):
            Logger.warning(f'BrowserManager: Gracefully dismissing browser dialog: "{dialog.message}"')
            try:
                await dialog.dismiss()
            except Exception:
                pass

        page.on('dialog', on_dialog)

        # Enforce global timeout
        page.set_default_timeout(config_dict['timeout'])

        # Start non-blocking background popup closer
        PopupHandler.start_modal_watcher(page)

        Logger.info('Browser context and page initialized successfully.')
        return page

    async def close(self) -> None:
        Logger.info('Cleaning up browser resources...')
        
        if self.context:
            await self.context.close()
            self.context = None
            
        if self.browser:
            await self.browser.close()
            self.browser = None
            
        if self.playwright:
            await self.playwright.stop()
            self.playwright = None
            
        Logger.info('Browser closed successfully.')
