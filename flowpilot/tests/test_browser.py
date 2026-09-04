import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from flowpilot.browser import BrowserController


@pytest.fixture
def controller():
    ctrl = BrowserController()
    ctrl._page = AsyncMock()
    ctrl._page.mouse = AsyncMock()
    ctrl._page.keyboard = AsyncMock()
    ctrl._page.screenshot = AsyncMock(return_value=b"\x89PNG\r\n\x1a\n")
    return ctrl


@pytest.mark.asyncio
async def test_take_screenshot(controller):
    result = await controller.take_screenshot()
    assert result == b"\x89PNG\r\n\x1a\n"
    controller._page.screenshot.assert_called_once()


@pytest.mark.asyncio
async def test_execute_left_click(controller):
    result = await controller.execute_action("left_click", {"coordinate": [100, 200]}, 1.0)
    controller._page.mouse.click.assert_called_once_with(100, 200, button="left")
    assert isinstance(result, str)


@pytest.mark.asyncio
async def test_execute_left_click_with_scaling(controller):
    result = await controller.execute_action("left_click", {"coordinate": [50, 100]}, 0.5)
    controller._page.mouse.click.assert_called_once_with(100, 200, button="left")


@pytest.mark.asyncio
async def test_execute_type(controller):
    result = await controller.execute_action("type", {"text": "hello world"}, 1.0)
    controller._page.keyboard.type.assert_called_once_with("hello world")


@pytest.mark.asyncio
async def test_execute_key(controller):
    result = await controller.execute_action("key", {"text": "Return"}, 1.0)
    controller._page.keyboard.press.assert_called_once_with("Return")


@pytest.mark.asyncio
async def test_execute_scroll(controller):
    result = await controller.execute_action(
        "scroll", {"coordinate": [500, 300], "scroll_direction": "down", "scroll_amount": 3}, 1.0
    )
    controller._page.mouse.move.assert_called_once_with(500, 300)


@pytest.mark.asyncio
async def test_execute_screenshot(controller):
    result = await controller.execute_action("screenshot", {}, 1.0)
    assert result == "screenshot_taken"


@pytest.mark.asyncio
async def test_unknown_action_raises(controller):
    with pytest.raises(ValueError, match="Unknown action"):
        await controller.execute_action("teleport", {}, 1.0)
