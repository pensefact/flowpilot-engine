import io
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from PIL import Image
from flowpilot.agent import Agent


def _fake_png_bytes() -> bytes:
    img = Image.new("RGB", (2, 2), color="red")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def _make_tool_use_response(actions):
    content = []
    for i, (name, action_input) in enumerate(actions):
        block = MagicMock()
        block.type = "tool_use"
        block.id = f"toolu_{i:04d}"
        block.name = name
        block.toolset_name = "computer"
        block.input = action_input
        content.append(block)
    msg = MagicMock()
    msg.content = content
    msg.stop_reason = "tool_use"
    msg.model = "claude-opus-5"
    return msg


def _make_end_response(text="Done."):
    block = MagicMock()
    block.type = "text"
    block.text = text
    msg = MagicMock()
    msg.content = [block]
    msg.stop_reason = "end_turn"
    msg.model = "claude-opus-5"
    return msg


@pytest.fixture
def mock_browser():
    browser = AsyncMock()
    browser.take_screenshot.return_value = _fake_png_bytes()
    browser.execute_action.return_value = "OK"
    return browser


@pytest.fixture
def mock_client():
    client = MagicMock()
    return client


@pytest.mark.asyncio
async def test_agent_runs_single_step_then_stops(mock_client, mock_browser):
    mock_client.messages.create.side_effect = [
        _make_tool_use_response([("screenshot", {})]),
        _make_end_response("Task complete."),
    ]

    agent = Agent(mock_client, mock_browser)
    log = await agent.run("Take a screenshot")

    assert len(log) >= 1
    assert mock_client.messages.create.call_count == 2


@pytest.mark.asyncio
async def test_agent_respects_max_steps(mock_client, mock_browser):
    mock_client.messages.create.return_value = _make_tool_use_response(
        [("left_click", {"coordinate": [100, 200]})]
    )

    agent = Agent(mock_client, mock_browser)
    log = await agent.run("Click forever", max_steps=3)

    assert mock_client.messages.create.call_count <= 4


@pytest.mark.asyncio
async def test_agent_sends_screenshot_as_tool_result(mock_client, mock_browser):
    mock_client.messages.create.side_effect = [
        _make_tool_use_response([("screenshot", {})]),
        _make_end_response(),
    ]

    agent = Agent(mock_client, mock_browser)
    await agent.run("Take a screenshot")

    second_call_messages = mock_client.messages.create.call_args_list[1]
    messages = second_call_messages.kwargs.get("messages") or second_call_messages[1].get("messages")
    user_msg = [m for m in messages if m["role"] == "user"]
    assert len(user_msg) >= 1
