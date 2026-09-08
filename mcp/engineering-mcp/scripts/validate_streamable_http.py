"""Deterministically verify the engineering MCP Streamable HTTP endpoint."""

import argparse
import asyncio

from mcp.client import Client


async def validate(url: str) -> None:
    async with Client(url) as client:
        tools = await client.list_tools()
        tool_names = {tool.name for tool in tools.tools}
        expected = {"app_run", "app_status", "app_test", "app_ui_verify"}
        if tool_names != expected:
            raise RuntimeError(f"Unexpected tools from {url}: {sorted(tool_names)}")

        calls = (
            ("app_status", None),
            ("app_run", {"mode": "start"}),
            ("app_test", None),
            ("app_ui_verify", None),
        )
        for name, arguments in calls:
            result = await client.call_tool(name, arguments)
            if result.is_error:
                raise RuntimeError(f"{name} returned an MCP error: {result.content}")
            print(f"Validated {name} over Streamable HTTP at {url}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://mcp:3001/mcp")
    args = parser.parse_args()
    asyncio.run(validate(args.url))


if __name__ == "__main__":
    main()
