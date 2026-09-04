import argparse
import asyncio
import json
import anthropic
from flowpilot.browser import BrowserController
from flowpilot.agent import Agent


async def _run(args: argparse.Namespace) -> None:
    client = anthropic.Anthropic()
    browser = BrowserController()

    try:
        print(f"Connecting to browser at {args.cdp_url}...")
        await browser.connect(args.cdp_url)

        if args.url:
            print(f"Navigating to {args.url}...")
            await browser.navigate(args.url)

        print(f"Starting agent with goal: {args.goal}")
        print(f"Max steps: {args.max_steps}")
        print(f"Watch the browser at http://localhost:6080")
        print("=" * 60)

        agent = Agent(client, browser, model=args.model)
        log = await agent.run(args.goal, max_steps=args.max_steps)

        print("\n" + "=" * 60)
        print(f"Completed. {len(log)} actions taken.")
        if args.output:
            with open(args.output, "w") as f:
                json.dump(log, f, indent=2)
            print(f"Log saved to {args.output}")
    finally:
        await browser.close()


def main():
    parser = argparse.ArgumentParser(description="FlowPilot — AI browser automation")
    parser.add_argument("goal", help="Natural language description of what to do")
    parser.add_argument("--url", help="URL to navigate to before starting")
    parser.add_argument("--cdp-url", default="http://localhost:9222", help="CDP endpoint")
    parser.add_argument("--max-steps", type=int, default=50, help="Maximum agent steps")
    parser.add_argument("--model", default="claude-opus-5", help="Claude model to use")
    parser.add_argument("--output", "-o", help="Path to save the action log as JSON")
    args = parser.parse_args()
    asyncio.run(_run(args))


if __name__ == "__main__":
    main()
