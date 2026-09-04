import random
import asyncio
from playwright.async_api import Page, Locator

MIN_SHORT_PAUSE = 500     # ms
MAX_SHORT_PAUSE = 1500    # ms

MIN_MEDIUM_PAUSE = 2000   # ms
MAX_MEDIUM_PAUSE = 4000   # ms

MIN_LONG_PAUSE = 5000     # ms
MAX_LONG_PAUSE = 8000     # ms

MIN_KEYPRESS_DELAY = 50   # ms between normal keys
MAX_KEYPRESS_DELAY = 150  # ms between normal keys
WORD_PAUSE_DELAY = 200    # extra ms pause after space characters

MIN_SCROLL_STEP = 50      # pixels per scroll tick
MAX_SCROLL_STEP = 150     # pixels per scroll tick
MIN_SCROLL_DELAY = 50     # ms between scroll ticks
MAX_SCROLL_DELAY = 150    # ms between scroll ticks

MOUSE_MOVE_PROBABILITY = 0.4 # 40% probability of mouse movement

MIN_THINK_PAUSE = 800     # ms for think state
MAX_THINK_PAUSE = 2000    # ms for think state

class HumanBehavior:
    @staticmethod
    async def random_sleep(page: Page, min_ms: int, max_ms: int) -> None:
        ms = random.randint(min_ms, max_ms)
        await page.wait_for_timeout(ms)

    @classmethod
    async def short_pause(cls, page: Page) -> None:
        await cls.random_sleep(page, MIN_SHORT_PAUSE, MAX_SHORT_PAUSE)

    @classmethod
    async def medium_pause(cls, page: Page) -> None:
        await cls.random_sleep(page, MIN_MEDIUM_PAUSE, MAX_MEDIUM_PAUSE)

    @classmethod
    async def long_pause(cls, page: Page) -> None:
        await cls.random_sleep(page, MIN_LONG_PAUSE, MAX_LONG_PAUSE)

    @classmethod
    async def type_like_human(cls, page: Page, locator: Locator, text: str) -> None:
        await locator.focus()
        try:
            await locator.press("Control+A")
        except Exception:
            pass
        try:
            await locator.press("Backspace")
        except Exception:
            pass

        for i, char in enumerate(text):
            await locator.press_sequentially(char)
            delay = random.uniform(MIN_KEYPRESS_DELAY, MAX_KEYPRESS_DELAY)
            if char == ' ' and i > 0 and text[i - 1] != ' ':
                delay += WORD_PAUSE_DELAY
            await page.wait_for_timeout(delay)

    @classmethod
    async def smooth_scroll(cls, page: Page, distance: int = None) -> None:
        if distance is None:
            viewport = page.viewport_size
            distance = viewport['height'] if viewport else 800

        scrolled = 0
        abs_distance = abs(distance)
        direction = 1 if distance >= 0 else -1

        while scrolled < abs_distance:
            step = random.randint(MIN_SCROLL_STEP, MAX_SCROLL_STEP)
            remaining = abs_distance - scrolled
            current_step = min(step, remaining)

            await page.evaluate(f"window.scrollBy(0, {direction * current_step})")
            scrolled += current_step

            delay = random.uniform(MIN_SCROLL_DELAY, MAX_SCROLL_DELAY)
            await page.wait_for_timeout(delay)

    @classmethod
    async def random_mouse_movement(cls, page: Page) -> None:
        if random.random() > MOUSE_MOVE_PROBABILITY:
            return

        viewport = page.viewport_size
        if not viewport:
            return

        min_x = viewport["width"] * 0.2
        max_x = viewport["width"] * 0.8
        min_y = viewport["height"] * 0.2
        max_y = viewport["height"] * 0.8

        target_x = random.randint(int(min_x), int(max_x))
        target_y = random.randint(int(min_y), int(max_y))

        steps = random.randint(10, 20)
        await page.mouse.move(target_x, target_y, steps=steps)

    @classmethod
    async def think(cls, page: Page) -> None:
        await cls.random_sleep(page, MIN_THINK_PAUSE, MAX_THINK_PAUSE)
