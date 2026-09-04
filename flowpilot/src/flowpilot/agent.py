import anthropic
from flowpilot.browser import BrowserController
from flowpilot.screenshot import resize_screenshot, encode_screenshot


class Agent:
    def __init__(
        self,
        client: anthropic.Anthropic,
        browser: BrowserController,
        model: str = "claude-opus-5",
    ):
        self._client = client
        self._browser = browser
        self._model = model
        self._scale_factor = 1.0

    async def run(self, goal: str, max_steps: int = 50) -> list[dict]:
        log: list[dict] = []
        messages = [{"role": "user", "content": goal}]
        tools = [{"type": "computer_toolset_20260801"}]

        for step in range(max_steps):
            print(f"\n--- Step {step + 1} ---")

            response = self._client.messages.create(
                model=self._model,
                max_tokens=4096,
                tools=tools,
                messages=messages,
                thinking={"type": "adaptive"},
            )

            if response.stop_reason != "tool_use":
                for block in response.content:
                    if hasattr(block, "text"):
                        print(f"Agent: {block.text}")
                break

            for block in response.content:
                if block.type == "text":
                    print(f"Agent: {block.text}")

            messages.append({"role": "assistant", "content": response.content})

            tool_results = []
            for block in response.content:
                if block.type != "tool_use":
                    continue

                action_name = block.name
                action_input = block.input
                print(f"  Action: {action_name} {action_input}")

                step_entry = {"action": action_name, "input": action_input}

                if action_name == "screenshot":
                    png_bytes = await self._browser.take_screenshot()
                    resized, self._scale_factor = resize_screenshot(png_bytes)
                    encoded = encode_screenshot(resized)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "toolset_name": "computer",
                        "content": [{
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": encoded,
                            },
                        }],
                    })
                    step_entry["result"] = "screenshot_taken"
                else:
                    try:
                        result = await self._browser.execute_action(
                            action_name, action_input, self._scale_factor
                        )
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "toolset_name": "computer",
                            "content": [{"type": "text", "text": result}],
                        })
                        step_entry["result"] = result
                    except Exception as e:
                        error_msg = f"Error: {e}"
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "toolset_name": "computer",
                            "is_error": True,
                            "content": error_msg,
                        })
                        step_entry["result"] = error_msg

                log.append(step_entry)

            messages.append({"role": "user", "content": tool_results})

        return log
