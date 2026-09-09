# FlowPilot

Browser automation powered by Claude's computer-use API and Playwright.

The agent takes a natural-language goal, screenshots the browser, sends the image to Claude for the next action, executes it via Playwright, and repeats until the goal is met or the step limit is reached.

## How it works

1. A headless Chrome instance runs inside Docker, exposed via CDP (port 9222) and viewable through noVNC (port 6080).
2. The Python agent connects to Chrome over CDP using Playwright.
3. Each step: take a screenshot, resize it for the vision model, send it to the Anthropic API with `computer_toolset`, and execute the returned action (click, type, scroll, navigate, wait).
4. Coordinates are scaled between the model's resolution and the actual browser viewport.

## Project structure

```
flowpilot/
  src/flowpilot/
    agent.py         # Agent loop (Anthropic messages API + computer_toolset)
    browser.py       # Playwright CDP connection and action execution
    screenshot.py    # Resize, encode, and coordinate scaling
    cli.py           # CLI entry point
  tests/
    test_agent.py
    test_browser.py
    test_screenshot.py
  docker/
    browser/         # Dockerfile for headless Chrome + noVNC
  docker-compose.yml
  pyproject.toml
```

## Setup

```bash
cd flowpilot
docker compose up -d          # starts Chrome + noVNC
pip install -e '.[dev]'       # install Python package
export ANTHROPIC_API_KEY=...
```

## Usage

```bash
flowpilot --cdp-url http://localhost:9222 --goal "Search for 'playwright automation' on Google"
```

Open http://localhost:6080 in your browser to watch the agent work.

Options: `--url` (starting page), `--max-steps` (default 50), `--model` (default claude-opus-5), `--output` (save action log as JSON).

## Tests

```bash
cd flowpilot
pytest
```

## Requirements

- Python 3.12+
- Docker (for the browser container)
- Anthropic API key
