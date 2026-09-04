import asyncio
from playwright.async_api import async_playwright, Page, Browser, BrowserContext
from flowpilot.screenshot import scale_coordinates


class BrowserController:
    def __init__(self):
        self._playwright = None
        self._browser: Browser | None = None
        self._page: Page | None = None

    async def connect(self, cdp_url: str) -> None:
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.connect_over_cdp(cdp_url)
        contexts = self._browser.contexts
        if contexts:
            pages = contexts[0].pages
            self._page = pages[0] if pages else await contexts[0].new_page()
        else:
            ctx = await self._browser.new_context()
            self._page = await ctx.new_page()

    async def take_screenshot(self) -> bytes:
        return await self._page.screenshot(type="png")

    async def navigate(self, url: str) -> None:
        await self._page.goto(url, wait_until="domcontentloaded")

    async def execute_action(self, name: str, action_input: dict, scale_factor: float) -> str:
        if name == "screenshot":
            return "screenshot_taken"

        if name == "wait":
            duration = action_input.get("duration", 1)
            await asyncio.sleep(duration)
            return "OK"

        coord = action_input.get("coordinate")
        if coord:
            coord = scale_coordinates(coord, scale_factor)

        start_coord = action_input.get("start_coordinate")
        if start_coord:
            start_coord = scale_coordinates(start_coord, scale_factor)

        match name:
            case "left_click":
                await self._page.mouse.click(coord[0], coord[1], button="left")
            case "right_click":
                await self._page.mouse.click(coord[0], coord[1], button="right")
            case "middle_click":
                await self._page.mouse.click(coord[0], coord[1], button="middle")
            case "double_click":
                await self._page.mouse.dblclick(coord[0], coord[1])
            case "triple_click":
                await self._page.mouse.click(coord[0], coord[1], click_count=3)
            case "left_click_drag":
                await self._page.mouse.move(start_coord[0], start_coord[1])
                await self._page.mouse.down()
                await self._page.mouse.move(coord[0], coord[1])
                await self._page.mouse.up()
            case "mouse_move":
                await self._page.mouse.move(coord[0], coord[1])
            case "scroll":
                await self._page.mouse.move(coord[0], coord[1])
                direction = action_input.get("scroll_direction", "down")
                amount = action_input.get("scroll_amount", 3)
                delta = amount * 100
                dx, dy = 0, 0
                match direction:
                    case "down":
                        dy = delta
                    case "up":
                        dy = -delta
                    case "right":
                        dx = delta
                    case "left":
                        dx = -delta
                await self._page.mouse.wheel(dx, dy)
            case "type":
                await self._page.keyboard.type(action_input["text"])
            case "key":
                await self._page.keyboard.press(action_input["text"])
            case "cursor_position":
                return "cursor_position: use screenshot to determine"
            case _:
                raise ValueError(f"Unknown action: {name}")

        return "OK"

    async def close(self) -> None:
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()
